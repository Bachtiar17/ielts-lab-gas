/**
 * On-demand Distractor Explainer & Gemini 3.8 TTS helper for Next.js API routes.
 * Uses the official `@google/genai` >= 3.5.0 Interactions API with graceful offline fallback.
 */

import { GoogleGenAI } from "@google/genai";
import {
  type StoredListeningTest,
  type StoredNote,
  type StoredQuestionItem,
  type StoredReadingTest,
  getAllNotes,
} from "@/lib/server/contentStore";
import type { DistractorExplanationResponse, ListeningPart } from "@/types/reading";

const EXPLANATION_SCHEMA = {
  type: "object",
  properties: {
    why_wrong: {
      type: "string",
      description: "Clear explanation of why the learner's response lost the mark.",
    },
    evidence_reasoning: {
      type: "string",
      description: "How the exact passage/transcript quote proves the correct answer.",
    },
    distractor_trap: {
      type: "string",
      description: "Specific IELTS trap mechanism (e.g. self-correction, qualifier flip).",
    },
    how_to_avoid_next_time: {
      type: "string",
      description: "One concrete actionable step for next attempt.",
    },
  },
  required: ["why_wrong", "evidence_reasoning", "distractor_trap", "how_to_avoid_next_time"],
};

function findStrategyNote(moduleName: "reading" | "listening", qtype: string): StoredNote | null {
  const exact = getAllNotes(moduleName, qtype)[0];
  if (exact) return exact;
  if (moduleName === "reading" && qtype.startsWith("matching_")) {
    return getAllNotes("reading", "matching_features")[0] || null;
  }
  if (moduleName === "reading" && qtype.endsWith("_completion")) {
    return getAllNotes("reading", "summary_completion")[0] || null;
  }
  if (moduleName === "listening") {
    return getAllNotes("listening", "form_note_table_completion")[0] || null;
  }
  return null;
}

function findContextExcerpt(
  moduleName: "reading" | "listening",
  test: StoredReadingTest | StoredListeningTest,
  item: StoredQuestionItem
): { locationLabel: string; excerpt: string } {
  if (moduleName === "listening") {
    const lt = test as StoredListeningTest;
    const part = lt.parts.find((p) => p.index === item.passage_index);
    const tid = item.evidence_span?.transcript_id;
    if (part) {
      const idx = tid ? part.transcript.findIndex((t) => t.id === tid) : -1;
      const slice =
        idx >= 0
          ? part.transcript.slice(Math.max(0, idx - 1), idx + 2)
          : part.transcript.slice(0, 6);
      return {
        locationLabel: `Part ${item.passage_index}`,
        excerpt: slice.map((t) => `${t.speaker}: ${t.text}`).join("\n"),
      };
    }
    return { locationLabel: `Part ${item.passage_index}`, excerpt: "" };
  }

  const rt = test as StoredReadingTest;
  const pid = item.evidence_span?.paragraph_id;
  const passage = rt.passages.find((p) => p.index === item.passage_index);
  if (passage) {
    const para = pid ? passage.paragraphs.find((p) => p.id === pid) : undefined;
    if (para) {
      return { locationLabel: `Paragraph ${pid}`, excerpt: para.text };
    }
    return {
      locationLabel: `Passage ${item.passage_index}`,
      excerpt: passage.paragraphs.map((p) => p.text).join(" ").slice(0, 1500),
    };
  }
  return { locationLabel: `Paragraph ${pid || "?"}`, excerpt: "" };
}

function buildOfflineExplanation(
  item: StoredQuestionItem,
  userAnswer: string,
  failureReason: string | null,
  note: StoredNote | null,
  locationLabel: string
) {
  const accepted = (item.answer_key.accepted || []).join(", ");
  const quote = item.evidence_span?.quote || "";
  const curated =
    item.evidence_span?.distractor_note ||
    "Compare the exact phrasing in the evidence against qualifying words or self-corrections.";

  let whyWrong: string;
  let trap: string;

  if (failureReason === "blank") {
    whyWrong = `This question was left blank. The accepted answer is '${accepted}'.`;
    trap = "Unanswered item (time management or missed cue).";
  } else if (failureReason === "word_limit_exceeded") {
    const wl = item.prompt_payload.word_limit?.label || "the stated word limit";
    whyWrong = `Your answer '${userAnswer}' exceeded ${wl}. Under IELTS deterministic rules, exceeding the word limit automatically scores 0. Accepted answer: '${accepted}'.`;
    trap = "Word-limit violation (extra article, modifier, or filler word).";
  } else if (failureReason === "wrong_label_set") {
    whyWrong = `You submitted '${userAnswer}', which belongs to the wrong label set for ${item.question_type}. Use TRUE/FALSE/NOT GIVEN for factual claims and YES/NO/NOT GIVEN for writer's views.`;
    trap = "Label-set confusion (T/F/NG vs Y/N/NG).";
  } else if (!failureReason && userAnswer) {
    whyWrong = `Your answer '${userAnswer}' matches the accepted key ('${accepted}').`;
    trap = curated;
  } else {
    whyWrong = `Your answer '${userAnswer}' does not match the official evidence. The accepted answer is '${accepted}'.`;
    trap = curated;
  }

  return {
    why_wrong: whyWrong,
    evidence_reasoning: quote ? `In ${locationLabel}: "${quote}" — ${curated}` : curated,
    distractor_trap: trap,
    how_to_avoid_next_time:
      note?.strategy_steps?.[0] ||
      "Locate the paraphrased anchor and verify qualifiers or speaker corrections before locking in.",
  };
}

export async function explainDistractorNode(params: {
  moduleName: "reading" | "listening";
  test: StoredReadingTest | StoredListeningTest;
  item: StoredQuestionItem;
  userAnswer: string;
  failureReason: string | null;
  apiKeyOverride?: string | null;
  modelOverride?: string | null;
}): Promise<DistractorExplanationResponse> {
  const { moduleName, test, item, userAnswer, failureReason, apiKeyOverride, modelOverride } =
    params;

  const note = findStrategyNote(moduleName, item.question_type);
  const { locationLabel, excerpt } = findContextExcerpt(moduleName, test, item);

  const activeKey = (apiKeyOverride || "").trim() || (process.env.GEMINI_API_KEY || "").trim();
  const primaryModel =
    (modelOverride || "").trim() || process.env.GEMINI_FAST_MODEL || "gemini-3.5-flash-lite";
  const candidateModels = Array.from(new Set([primaryModel, "gemini-3.5-flash-lite"]));

  let explainerMode = "offline_evidence";
  let explanation = buildOfflineExplanation(item, userAnswer, failureReason, note, locationLabel);

  if (activeKey) {
    const ai = new GoogleGenAI({ apiKey: activeKey });
    const prompt = `You are a concise, precise IELTS Academic ${moduleName} tutor.
Explain why the learner's response lost the mark (or confirm why it succeeded if correct).
Ground your explanation strictly in the evidence excerpt below.

Question #${item.question_number} (${item.question_type}):
Prompt: ${item.prompt_payload.prompt}
Accepted Answer(s): ${JSON.stringify(item.answer_key.accepted)}
Learner Answer: ${userAnswer || "(blank)"}
Deterministic Failure Reason: ${failureReason || "correct_review"}
${locationLabel}: ${excerpt}
Evidence Quote: ${item.evidence_span?.quote || ""}
Distractor Note: ${item.evidence_span?.distractor_note || ""}
Strategy Reference: ${JSON.stringify(note?.strategy_steps || [])}`;

    for (const modelName of candidateModels) {
      try {
        const interaction = await ai.interactions.create({
          model: modelName,
          input: prompt,
          response_format: {
            type: "text",
            mime_type: "application/json",
            schema: EXPLANATION_SCHEMA,
          },
          store: false,
        });
        if (interaction.output_text) {
          const parsed = JSON.parse(interaction.output_text);
          if (parsed?.why_wrong && parsed?.evidence_reasoning) {
            explanation = parsed;
            const keyTag = apiKeyOverride ? "personal-key" : "server-key";
            explainerMode = `gemini:${modelName} (${keyTag})`;
            break;
          }
        }
      } catch {
        continue;
      }
    }
  }

  return {
    item_id: item.id,
    module: moduleName,
    question_number: item.question_number,
    question_type: item.question_type,
    passage_index: item.passage_index,
    user_answer: userAnswer,
    accepted_answers: item.answer_key.accepted,
    failure_reason: failureReason,
    evidence_span: item.evidence_span,
    explanation,
    strategy_note: note,
    explainer_mode: explainerMode,
  };
}

export async function testGeminiKeyNode(
  apiKey: string,
  model: string
): Promise<{ ok: boolean; model_used: string; message: string }> {
  const ai = new GoogleGenAI({ apiKey: apiKey.trim() });
  const tried = Array.from(new Set([model.trim(), "gemini-3.5-flash-lite"]));
  let lastErr = "";

  for (const modelName of tried) {
    try {
      const res = await ai.interactions.create({
        model: modelName,
        input: "Reply with OK only.",
        store: false,
      });
      if (res.output_text) {
        return {
          ok: true,
          model_used: modelName,
          message: `Connected successfully using ${modelName}.`,
        };
      }
    } catch (err: unknown) {
      lastErr = err instanceof Error ? err.message.slice(0, 180) : String(err).slice(0, 180);
    }
  }
  return {
    ok: false,
    model_used: model,
    message: `Could not connect: ${lastErr || "Unknown error"}`,
  };
}

export async function synthesizePartWavDataUrl(
  part: Omit<ListeningPart, "audio_url">,
  apiKeyOverride?: string | null
): Promise<{ audio_url: string; bytes: number; model: string }> {
  const activeKey = (apiKeyOverride || "").trim() || (process.env.GEMINI_API_KEY || "").trim();
  if (!activeKey) {
    throw new Error(
      "No Gemini API key available. Add your key via 'Add Personal Gemini API' or use Browser Multi-Voice playback."
    );
  }

  const ttsModel = process.env.GEMINI_TTS_MODEL || "gemini-3.8-flash-lite-tts";
  const speakers = part.speakers || [];
  const primarySpeakers = speakers.slice(0, 2);
  const allowedNames = new Set(primarySpeakers.map((s) => s.speaker));
  const fallbackSpeaker = primarySpeakers[0]?.speaker || "Speaker";

  const content = part.transcript.map((turn) => {
    const meta: Record<string, string> = {
      type: "speech_metadata",
      style: turn.style || "clear, natural IELTS exam pace",
    };
    if (speakers.length > 1) {
      meta.speaker = allowedNames.has(turn.speaker) ? turn.speaker : fallbackSpeaker;
    }
    return {
      type: "text" as const,
      text: turn.text,
      annotations: [meta],
    };
  });

  const speechConfig =
    speakers.length <= 1
      ? [{ voice: speakers[0]?.voice || "Charon" }]
      : {
          speakers: primarySpeakers.map((s) => ({
            speaker: s.speaker,
            voice: s.voice || "Kore",
          })),
        };

  const ai = new GoogleGenAI({ apiKey: activeKey, apiVersion: "v1beta" });
  const interaction = await ai.interactions.create({
    model: ttsModel,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    input: [{ type: "user_input", content }] as any,
    response_format: { type: "audio" },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    generation_config: { speech_config: speechConfig } as any,
    store: false,
  });

  const b64 = interaction.output_audio?.data;
  const mime = interaction.output_audio?.mime_type || "audio/wav";
  if (!b64) {
    throw new Error(`Gemini TTS returned no audio data for Part ${part.index}.`);
  }
  const bytes = Buffer.from(b64, "base64").length;
  return {
    audio_url: `data:${mime};base64,${b64}`,
    bytes,
    model: ttsModel,
  };
}
