"""On-demand distractor explainer service (Reading + Listening).

Uses Gemini via the official `google-genai` Interactions API when an API key is available
(either from the learner's personal `X-Gemini-Api-Key` header or `.env`), automatically
falling back to `gemini-3.5-flash-lite` on transient 503 demand spikes, and seamlessly
falling back to deterministic evidence-span + matched strategy notes when offline.
"""

from __future__ import annotations

from typing import Any

from google import genai
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.db.models import KnowledgeConcept, ListeningTest, QuestionItem, ReadingTest


class LLMExplanationOutput(BaseModel):
    """Structured JSON schema returned by Gemini for distractor explanations."""

    why_wrong: str = Field(description="Clear explanation of why the learner's response lost the mark.")
    evidence_reasoning: str = Field(description="How the exact passage/transcript quote proves the correct answer.")
    distractor_trap: str = Field(description="Specific IELTS trap mechanism (e.g. self-correction, qualifier flip).")
    how_to_avoid_next_time: str = Field(description="One concrete actionable step for next attempt.")


def _find_strategy_note(db: Session, module: str, question_type: str) -> dict[str, Any] | None:
    stmt = select(KnowledgeConcept).where(
        KnowledgeConcept.module == module,
        KnowledgeConcept.question_type == question_type,
    )
    concept = db.execute(stmt).scalars().first()
    if concept is None and module == "reading" and question_type.startswith("matching_"):
        concept = db.execute(
            select(KnowledgeConcept).where(
                KnowledgeConcept.module == "reading",
                KnowledgeConcept.question_type == "matching_features",
            )
        ).scalars().first()
    if concept is None and module == "reading" and question_type.endswith("_completion"):
        concept = db.execute(
            select(KnowledgeConcept).where(
                KnowledgeConcept.module == "reading",
                KnowledgeConcept.question_type == "summary_completion",
            )
        ).scalars().first()
    if concept is None and module == "listening":
        concept = db.execute(
            select(KnowledgeConcept).where(
                KnowledgeConcept.module == "listening",
                KnowledgeConcept.question_type == "form_note_table_completion",
            )
        ).scalars().first()
    if concept is None:
        return None
    return {
        "id": concept.id,
        "title": concept.title,
        "channel": concept.payload_json.get("channel", "IELTS Advantage"),
        "source_url": concept.source_url,
        "question_type": concept.question_type,
        "strategy_steps": concept.payload_json.get("strategy_steps", []),
        "common_mistakes": concept.payload_json.get("common_mistakes", []),
        "band_upgrade_patterns": concept.payload_json.get("band_upgrade_patterns", []),
        "timestamp_anchors": concept.payload_json.get("timestamp_anchors", []),
    }


def _find_context_excerpt(db: Session, item: QuestionItem) -> tuple[str, str]:
    """Return (location_label, context_text) for either a Reading or Listening question item."""
    if item.module == "listening" and item.listening_test_id:
        ltest = db.get(ListeningTest, item.listening_test_id)
        if ltest:
            tid = item.evidence_span.get("transcript_id")
            for part in ltest.parts_json:
                if int(part["index"]) == item.passage_index:
                    turns = part.get("transcript", [])
                    for idx, turn in enumerate(turns):
                        if tid and turn.get("id") == tid:
                            window = turns[max(0, idx - 1) : min(len(turns), idx + 2)]
                            excerpt = "\n".join(f"{t['speaker']}: {t['text']}" for t in window)
                            return f"Part {item.passage_index}", excerpt
                    return f"Part {item.passage_index}", "\n".join(
                        f"{t['speaker']}: {t['text']}" for t in turns[:6]
                    )
        return f"Part {item.passage_index}", ""

    test = db.get(ReadingTest, item.test_id) if item.test_id else None
    paragraph_id = item.evidence_span.get("paragraph_id")
    if test and test.passages_json:
        for passage in test.passages_json:
            if int(passage.get("index", 1)) == item.passage_index:
                for para in passage.get("paragraphs", []):
                    if paragraph_id and para.get("id") == paragraph_id:
                        return f"Paragraph {paragraph_id}", str(para.get("text", ""))
                return f"Passage {item.passage_index}", " ".join(
                    str(p.get("text", "")) for p in passage.get("paragraphs", [])
                )[:1500]
    return f"Paragraph {paragraph_id or '?'}", ""


def _build_offline_explanation(
    item: QuestionItem,
    user_answer: str,
    failure_reason: str | None,
    strategy_note: dict[str, Any] | None,
    location_label: str,
) -> LLMExplanationOutput:
    accepted = ", ".join(item.answer_key.get("accepted", []))
    evidence_quote = item.evidence_span.get("quote", "")
    curated_note = item.evidence_span.get(
        "distractor_note",
        "Compare the exact phrasing in the evidence against qualifying words or self-corrections.",
    )

    if failure_reason == "blank":
        why_wrong = f"This question was left blank. The accepted answer is '{accepted}'."
        trap = "Unanswered item (time management or missed cue)."
    elif failure_reason == "word_limit_exceeded":
        wl = (item.prompt_payload.get("word_limit") or {}).get("label", "the stated word limit")
        why_wrong = (
            f"Your answer '{user_answer}' exceeded {wl}. Under IELTS deterministic rules, "
            f"exceeding the word limit automatically scores 0 even if the keyword is present. "
            f"The accepted answer is '{accepted}'."
        )
        trap = "Word-limit violation (extra article, modifier, or filler word)."
    elif failure_reason == "wrong_label_set":
        why_wrong = (
            f"You submitted '{user_answer}', which belongs to the wrong label set for `{item.question_type}`. "
            f"Use TRUE/FALSE/NOT GIVEN for factual claims and YES/NO/NOT GIVEN for writer's views."
        )
        trap = "Label-set confusion (T/F/NG vs Y/N/NG)."
    elif failure_reason is None and user_answer:
        why_wrong = f"Your answer '{user_answer}' matches the accepted key ('{accepted}')."
        trap = curated_note
    else:
        why_wrong = (
            f"Your answer '{user_answer}' does not match the official evidence. "
            f"The accepted answer is '{accepted}'."
        )
        trap = curated_note

    evidence_reasoning = (
        f"In {location_label}: \"{evidence_quote}\" — {curated_note}"
        if evidence_quote
        else curated_note
    )
    next_step = (
        strategy_note["strategy_steps"][0]
        if strategy_note and strategy_note.get("strategy_steps")
        else "Locate the paraphrased anchor and verify qualifiers or speaker corrections before locking in."
    )

    return LLMExplanationOutput(
        why_wrong=why_wrong,
        evidence_reasoning=evidence_reasoning,
        distractor_trap=trap,
        how_to_avoid_next_time=next_step,
    )


def explain_item_distractor(
    db: Session,
    *,
    item: QuestionItem,
    user_answer: str,
    failure_reason: str | None = None,
    api_key_override: str | None = None,
    model_override: str | None = None,
) -> dict[str, Any]:
    """Return a structured distractor explanation + linked IELTS Advantage strategy note."""
    settings = get_settings()
    strategy_note = _find_strategy_note(db, module=item.module, question_type=item.question_type)
    location_label, context_excerpt = _find_context_excerpt(db, item)

    active_key = (api_key_override or "").strip() or (settings.gemini_api_key or "").strip()
    primary_model = (model_override or "").strip() or settings.gemini_fast_model
    candidate_models = list(dict.fromkeys([primary_model, "gemini-3.5-flash-lite"]))

    source_mode = "offline_evidence"
    explanation: LLMExplanationOutput | None = None

    if active_key:
        prompt = f"""You are a concise, precise IELTS Academic {item.module.title()} tutor.
Explain why the learner's response lost the mark (or confirm why it succeeded if correct).
Ground your explanation strictly in the evidence excerpt below.

Question #{item.question_number} ({item.question_type}):
Prompt: {item.prompt_payload.get('prompt', '')}
Accepted Answer(s): {item.answer_key.get('accepted', [])}
Learner Answer: {user_answer or '(blank)'}
Deterministic Failure Reason: {failure_reason or 'correct_review'}
{location_label}: {context_excerpt}
Evidence Quote: {item.evidence_span.get('quote', '')}
Distractor Note: {item.evidence_span.get('distractor_note', '')}
Strategy Reference: {strategy_note.get('strategy_steps', []) if strategy_note else []}
"""
        client = genai.Client(api_key=active_key)
        for model_name in candidate_models:
            try:
                interaction = client.interactions.create(
                    model=model_name,
                    input=prompt,
                    response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": LLMExplanationOutput.model_json_schema(),
                    },
                    store=False,
                )
                if interaction.output_text:
                    explanation = LLMExplanationOutput.model_validate_json(interaction.output_text)
                    key_tag = "personal-key" if api_key_override else "server-key"
                    source_mode = f"gemini:{model_name} ({key_tag})"
                    break
            except Exception:  # noqa: BLE001
                continue

    if explanation is None:
        explanation = _build_offline_explanation(
            item, user_answer, failure_reason, strategy_note, location_label
        )

    return {
        "item_id": item.id,
        "module": item.module,
        "question_number": item.question_number,
        "question_type": item.question_type,
        "passage_index": item.passage_index,
        "user_answer": user_answer,
        "accepted_answers": item.answer_key.get("accepted", []),
        "failure_reason": failure_reason,
        "evidence_span": item.evidence_span,
        "explanation": explanation.model_dump(),
        "strategy_note": strategy_note,
        "explainer_mode": source_mode,
    }


# Backward-compatible alias
explain_reading_distractor = explain_item_distractor
