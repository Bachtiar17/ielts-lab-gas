"""FastAPI REST endpoints for Reading (M1), Listening (M2), Past Session Reviews, Resets & API Key Settings."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import FileResponse
from google import genai
from sqlalchemy import delete, desc, func, select
from sqlalchemy.orm import Session

from backend.app.api.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    DrillCardItem,
    ExplainRequest,
    HealthResponse,
    ListeningPartSummary,
    ListeningTestDetail,
    ListeningTestSummary,
    PassageSummary,
    ProgressSummaryResponse,
    PublicQuestionItem,
    QuestionTypeBreakdown,
    QuestionVerdict,
    RandomDrillsResponse,
    ReadingTestDetail,
    ReadingTestSummary,
    ResetResponse,
    SessionHistoryItem,
    SkillProfileItem,
    SubmitSessionRequest,
    SubmitSessionResponse,
    TestGeminiKeyRequest,
    TestGeminiKeyResponse,
)
from backend.app.config import get_settings
from backend.app.db.models import (
    KnowledgeConcept,
    ListeningTest,
    QuestionItem,
    ReadingTest,
    TestSession,
    UserAttempt,
    UserSkillProfile,
)
from backend.app.db.session import get_db
from backend.app.scoring.band_math import raw_to_listening_band, raw_to_reading_band
from backend.app.scoring.listening import grade_listening_item
from backend.app.scoring.reading import grade_reading_item
from backend.app.services.explainer import explain_item_distractor

router = APIRouter(prefix="/api")

DBDep = Annotated[Session, Depends(get_db)]


# ==================== HEALTH, TAXONOMY & SETTINGS ====================


@router.get("/health", response_model=HealthResponse)
def health_check(db: DBDep) -> HealthResponse:
    settings = get_settings()
    dialect = db.bind.dialect.name if db.bind is not None else "unknown"
    drill_count = db.execute(
        select(func.count()).select_from(ReadingTest).where(ReadingTest.is_drill_bank.is_(True))
    ).scalar_one()
    listening_count = db.execute(select(func.count()).select_from(ListeningTest)).scalar_one()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        database_dialect=dialect,
        gemini_configured=settings.has_gemini_key,
        gemini_fast_model=settings.gemini_fast_model,
        reading_drill_bank_count=int(drill_count),
        listening_test_count=int(listening_count),
    )


@router.post("/settings/test-gemini", response_model=TestGeminiKeyResponse)
def test_personal_gemini_key(payload: TestGeminiKeyRequest) -> TestGeminiKeyResponse:
    """Validate a user-supplied Gemini API key without saving it to server disk."""
    client = genai.Client(api_key=payload.api_key.strip())
    tried: list[str] = list(dict.fromkeys([payload.model.strip(), "gemini-3.5-flash-lite"]))
    last_error = ""
    for model_name in tried:
        try:
            res = client.interactions.create(
                model=model_name,
                input="Reply with OK only.",
                store=False,
            )
            if res.output_text:
                return TestGeminiKeyResponse(
                    ok=True,
                    model_used=model_name,
                    message=f"Connected successfully using {model_name}.",
                )
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)[:180]
    return TestGeminiKeyResponse(
        ok=False,
        model_used=payload.model,
        message=f"Could not connect: {last_error or 'Unknown error'}",
    )


@router.get("/taxonomy")
def get_taxonomy() -> dict[str, Any]:
    settings = get_settings()
    if not settings.taxonomy_path.exists():
        raise HTTPException(status_code=404, detail="Taxonomy specification file not found.")
    return json.loads(settings.taxonomy_path.read_text(encoding="utf-8"))


@router.get("/notes")
def list_strategy_notes(
    db: DBDep,
    module: str | None = Query(default=None),
    question_type: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    stmt = select(KnowledgeConcept)
    if module:
        stmt = stmt.where(KnowledgeConcept.module == module.lower())
    if question_type:
        stmt = stmt.where(KnowledgeConcept.question_type == question_type.lower())
    stmt = stmt.order_by(KnowledgeConcept.module, KnowledgeConcept.question_type)
    concepts = db.execute(stmt).scalars().all()
    return [
        {
            "id": c.id,
            "module": c.module,
            "question_type": c.question_type,
            "source_type": c.source_type,
            "source_video_id": c.source_video_id,
            "source_url": c.source_url,
            "title": c.title,
            "channel": c.payload_json.get("channel", "IELTS Advantage"),
            "strategy_steps": c.payload_json.get("strategy_steps", []),
            "common_mistakes": c.payload_json.get("common_mistakes", []),
            "band_upgrade_patterns": c.payload_json.get("band_upgrade_patterns", []),
            "timestamp_anchors": c.payload_json.get("timestamp_anchors", []),
            "summary_md": c.summary_md,
        }
        for c in concepts
    ]


# ==================== ACADEMIC READING TESTS & 30-PASSAGE ROTATING DRILLS ====================


@router.get("/reading/tests", response_model=list[ReadingTestSummary])
def list_reading_tests(db: DBDep) -> list[ReadingTestSummary]:
    tests = (
        db.execute(
            select(ReadingTest)
            .where(ReadingTest.is_drill_bank.is_(False))
            .order_by(ReadingTest.created_at)
        )
        .scalars()
        .all()
    )
    summaries: list[ReadingTestSummary] = []
    for test in tests:
        counts: dict[int, int] = defaultdict(int)
        for item in test.items:
            counts[item.passage_index] += 1
        passages = [
            PassageSummary(
                index=int(p["index"]),
                title=str(p["title"]),
                subtitle=str(p.get("subtitle", "")),
                topic=str(p.get("topic", "Academic")),
                question_count=counts[int(p["index"])],
                recommended_minutes=int(p.get("recommended_minutes", 20)),
            )
            for p in test.passages_json
        ]
        summaries.append(
            ReadingTestSummary(
                id=test.id,
                title=test.title,
                subtitle=test.subtitle,
                difficulty_label=test.difficulty_label,
                duration_minutes=test.duration_minutes,
                total_questions=len(test.items),
                passages=passages,
            )
        )
    return summaries


@router.get("/reading/drills/random", response_model=RandomDrillsResponse)
def get_random_reading_drills(
    db: DBDep,
    exclude: str | None = Query(default=None, description="Comma-separated drill IDs to avoid repeating."),
) -> RandomDrillsResponse:
    """Return 3 freshly rotated single-passage drills (1 each from Slots 1, 2, 3) from the 30-passage bank."""
    all_drills = (
        db.execute(select(ReadingTest).where(ReadingTest.is_drill_bank.is_(True)))
        .scalars()
        .all()
    )
    excluded_ids = {s.strip() for s in (exclude or "").split(",") if s.strip()}

    by_slot: dict[int, list[ReadingTest]] = defaultdict(list)
    for d in all_drills:
        by_slot[int(d.drill_slot or 1)].append(d)

    picked: list[DrillCardItem] = []
    for slot in (1, 2, 3):
        pool = by_slot.get(slot, [])
        if not pool:
            continue
        fresh_pool = [d for d in pool if d.id not in excluded_ids]
        choice = random.choice(fresh_pool if fresh_pool else pool)
        p0 = choice.passages_json[0] if choice.passages_json else {}
        picked.append(
            DrillCardItem(
                id=choice.id,
                drill_slot=slot,
                title=choice.title,
                subtitle=choice.subtitle,
                topic=str(p0.get("topic", "Academic")),
                difficulty_label=choice.difficulty_label,
                question_count=len(choice.items),
                recommended_minutes=choice.duration_minutes,
            )
        )

    return RandomDrillsResponse(bank_size=len(all_drills), drills=picked)


@router.get("/reading/tests/{test_id}", response_model=ReadingTestDetail)
def get_reading_test(
    test_id: str,
    db: DBDep,
    passage_index: int | None = Query(default=None, ge=1, le=3),
) -> ReadingTestDetail:
    test = db.get(ReadingTest, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail=f"Reading test '{test_id}' not found.")

    passages = test.passages_json
    items = test.items
    duration = test.duration_minutes

    if passage_index is not None and not test.is_drill_bank:
        passages = [p for p in passages if int(p["index"]) == passage_index]
        items = [q for q in items if q.passage_index == passage_index]
        duration = int(passages[0].get("recommended_minutes", 20)) if passages else 20

    public_questions = [
        PublicQuestionItem(
            id=q.id,
            passage_index=q.passage_index,
            question_number=q.question_number,
            question_type=q.question_type,
            target_band=q.target_band,
            prompt_payload=q.prompt_payload,
        )
        for q in items
    ]
    return ReadingTestDetail(
        id=test.id,
        title=test.title,
        subtitle=test.subtitle,
        difficulty_label=test.difficulty_label,
        duration_minutes=duration,
        is_drill_bank=test.is_drill_bank,
        drill_slot=test.drill_slot,
        passages=passages,
        questions=public_questions,
    )


@router.post("/reading/sessions", response_model=CreateSessionResponse)
def create_reading_session(payload: CreateSessionRequest, db: DBDep) -> CreateSessionResponse:
    test = db.get(ReadingTest, payload.test_id)
    if test is None:
        raise HTTPException(status_code=404, detail=f"Reading test '{payload.test_id}' not found.")

    if test.is_drill_bank:
        mode = "drill"
        passage_filter = None
        items = list(test.items)
        duration_minutes = test.duration_minutes
    elif payload.mode == "drill":
        if payload.passage_index is None:
            raise HTTPException(status_code=400, detail="passage_index (1-3) is required for drill mode.")
        mode = "drill"
        passage_filter = payload.passage_index
        items = [q for q in test.items if q.passage_index == payload.passage_index]
        duration_minutes = 20
    else:
        mode = "section_mock"
        passage_filter = None
        items = list(test.items)
        duration_minutes = test.duration_minutes

    session = TestSession(
        user_id=payload.user_id,
        test_id=test.id,
        mode=mode,
        passage_filter=passage_filter,
        module="reading",
        total_questions=len(items),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return CreateSessionResponse(
        session_id=session.id,
        test_id=session.test_id,
        module="reading",
        mode=session.mode,
        passage_index=session.passage_filter,
        duration_minutes=duration_minutes,
        total_questions=session.total_questions,
        started_at=session.started_at,
    )


def _persist_and_grade_session(
    db: Session,
    session: TestSession,
    items: list[QuestionItem],
    payload: SubmitSessionRequest,
    test_title: str,
) -> SubmitSessionResponse:
    for old_attempt in list(session.attempts):
        db.delete(old_attempt)
    db.flush()

    raw_score = 0
    verdicts: list[QuestionVerdict] = []
    qtype_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    is_listening = session.module == "listening"
    grader = grade_listening_item if is_listening else grade_reading_item
    band_fn = raw_to_listening_band if is_listening else raw_to_reading_band

    for item in items:
        raw_resp = payload.answers.get(item.id, "")
        grade = grader(
            question_type=item.question_type,
            user_response=raw_resp,
            answer_key=item.answer_key,
            word_limit_spec=item.prompt_payload.get("word_limit"),
        )
        if grade.is_correct:
            raw_score += 1
            qtype_stats[item.question_type][0] += 1
        qtype_stats[item.question_type][1] += 1

        user_display = ", ".join(raw_resp) if isinstance(raw_resp, list) else str(raw_resp or "")
        db.add(
            UserAttempt(
                session_id=session.id,
                item_id=item.id,
                user_response={"raw": raw_resp},
                normalized_response=grade.normalized_user,
                is_correct=grade.is_correct,
                failure_reason=grade.failure_reason,
                diagnostic_detail=grade.diagnostic_detail,
            )
        )
        verdicts.append(
            QuestionVerdict(
                item_id=item.id,
                passage_index=item.passage_index,
                question_number=item.question_number,
                question_type=item.question_type,
                user_answer=user_display,
                normalized_user=grade.normalized_user,
                accepted_answers=grade.accepted_display,
                is_correct=grade.is_correct,
                failure_reason=grade.failure_reason,
                diagnostic_detail=grade.diagnostic_detail,
                evidence_span=item.evidence_span,
            )
        )

    total_q = len(items)
    band = band_fn(raw_score, total_questions=total_q)
    now = datetime.now(UTC)
    session.raw_score = raw_score
    session.total_questions = total_q
    session.overall_band = band
    session.duration_sec = payload.duration_sec
    session.completed_at = now

    for qtype, (corr, tot) in qtype_stats.items():
        skill_key = f"{session.module}:{qtype}"
        profile = db.get(UserSkillProfile, (session.user_id, skill_key))
        if profile is None:
            profile = UserSkillProfile(
                user_id=session.user_id,
                skill_key=skill_key,
                correct_count=corr,
                attempts_count=tot,
                estimated_band=band_fn(corr, total_questions=tot),
            )
            db.add(profile)
        else:
            profile.correct_count += corr
            profile.attempts_count += tot
            profile.estimated_band = band_fn(
                profile.correct_count, total_questions=profile.attempts_count
            )

    db.commit()

    breakdown = [
        QuestionTypeBreakdown(
            question_type=qtype,
            correct=corr,
            total=tot,
            accuracy_pct=round((corr / tot) * 100.0, 1) if tot > 0 else 0.0,
        )
        for qtype, (corr, tot) in sorted(qtype_stats.items())
    ]

    return SubmitSessionResponse(
        session_id=session.id,
        test_id=session.test_id,
        test_title=test_title,
        module=session.module,
        mode=session.mode,
        passage_index=session.passage_filter,
        raw_score=raw_score,
        total_questions=total_q,
        band_score=band,
        is_prorated_band=(total_q != 40),
        duration_sec=payload.duration_sec,
        completed_at=now,
        by_question_type=breakdown,
        verdicts=verdicts,
    )


@router.post("/reading/sessions/{session_id}/submit", response_model=SubmitSessionResponse)
def submit_reading_session(
    session_id: str,
    payload: SubmitSessionRequest,
    db: DBDep,
) -> SubmitSessionResponse:
    session = db.get(TestSession, session_id)
    if session is None or session.module != "reading":
        raise HTTPException(status_code=404, detail=f"Reading session '{session_id}' not found.")

    test = db.get(ReadingTest, session.test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Associated Reading test not found.")

    items = (
        [q for q in test.items if q.passage_index == session.passage_filter]
        if session.passage_filter is not None and not test.is_drill_bank
        else list(test.items)
    )
    return _persist_and_grade_session(db, session, items, payload, test.title)


# ==================== LISTENING TESTS, SESSIONS & AUDIO ====================


@router.get("/listening/tests", response_model=list[ListeningTestSummary])
def list_listening_tests(db: DBDep) -> list[ListeningTestSummary]:
    settings = get_settings()
    tests = db.execute(select(ListeningTest).order_by(ListeningTest.created_at)).scalars().all()
    summaries: list[ListeningTestSummary] = []
    for test in tests:
        counts: dict[int, int] = defaultdict(int)
        for item in test.items:
            counts[item.passage_index] += 1
        parts = [
            ListeningPartSummary(
                index=int(p["index"]),
                title=str(p["title"]),
                context=str(p.get("context", "")),
                question_count=counts[int(p["index"])],
                has_audio_file=(settings.audio_dir / str(p.get("audio_filename", ""))).is_file(),
                has_map=bool(p.get("map_data")),
            )
            for p in test.parts_json
        ]
        summaries.append(
            ListeningTestSummary(
                id=test.id,
                title=test.title,
                subtitle=test.subtitle,
                difficulty_label=test.difficulty_label,
                duration_minutes=test.duration_minutes,
                total_questions=len(test.items),
                parts=parts,
            )
        )
    return summaries


@router.get("/listening/tests/{test_id}", response_model=ListeningTestDetail)
def get_listening_test(
    test_id: str,
    db: DBDep,
    part_index: int | None = Query(default=None, ge=1, le=4),
) -> ListeningTestDetail:
    settings = get_settings()
    test = db.get(ListeningTest, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail=f"Listening test '{test_id}' not found.")

    raw_parts = (
        [p for p in test.parts_json if int(p["index"]) == part_index]
        if part_index is not None
        else list(test.parts_json)
    )
    items = (
        [q for q in test.items if q.passage_index == part_index]
        if part_index is not None
        else list(test.items)
    )
    duration = 8 if part_index is not None else test.duration_minutes

    enriched_parts: list[dict[str, Any]] = []
    for part in raw_parts:
        filename = str(part.get("audio_filename", ""))
        has_file = bool(filename and (settings.audio_dir / filename).is_file())
        enriched_parts.append(
            {
                **part,
                "audio_url": f"/api/audio/{filename}" if has_file else None,
            }
        )

    public_questions = [
        PublicQuestionItem(
            id=q.id,
            passage_index=q.passage_index,
            question_number=q.question_number,
            question_type=q.question_type,
            target_band=q.target_band,
            prompt_payload=q.prompt_payload,
        )
        for q in items
    ]
    return ListeningTestDetail(
        id=test.id,
        title=test.title,
        subtitle=test.subtitle,
        difficulty_label=test.difficulty_label,
        duration_minutes=duration,
        parts=enriched_parts,
        questions=public_questions,
    )


@router.post("/listening/sessions", response_model=CreateSessionResponse)
def create_listening_session(payload: CreateSessionRequest, db: DBDep) -> CreateSessionResponse:
    test = db.get(ListeningTest, payload.test_id)
    if test is None:
        raise HTTPException(status_code=404, detail=f"Listening test '{payload.test_id}' not found.")

    if payload.mode == "drill" and payload.passage_index is None:
        raise HTTPException(status_code=400, detail="passage_index (1-4) is required for Listening part drill.")

    if payload.mode == "drill":
        items = [q for q in test.items if q.passage_index == payload.passage_index]
        duration_minutes = 8
        p_filter = payload.passage_index
    else:
        items = list(test.items)
        duration_minutes = test.duration_minutes
        p_filter = None

    session = TestSession(
        user_id=payload.user_id,
        test_id=test.id,
        mode=payload.mode,
        passage_filter=p_filter,
        module="listening",
        total_questions=len(items),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return CreateSessionResponse(
        session_id=session.id,
        test_id=session.test_id,
        module="listening",
        mode=session.mode,
        passage_index=session.passage_filter,
        duration_minutes=duration_minutes,
        total_questions=session.total_questions,
        started_at=session.started_at,
    )


@router.post("/listening/sessions/{session_id}/submit", response_model=SubmitSessionResponse)
def submit_listening_session(
    session_id: str,
    payload: SubmitSessionRequest,
    db: DBDep,
) -> SubmitSessionResponse:
    session = db.get(TestSession, session_id)
    if session is None or session.module != "listening":
        raise HTTPException(status_code=404, detail=f"Listening session '{session_id}' not found.")

    test = db.get(ListeningTest, session.test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Associated Listening test not found.")

    items = (
        [q for q in test.items if q.passage_index == session.passage_filter]
        if session.passage_filter is not None
        else list(test.items)
    )
    return _persist_and_grade_session(db, session, items, payload, test.title)


@router.post("/listening/tests/{test_id}/parts/{part_index}/synthesize")
def synthesize_listening_part(
    test_id: str,
    part_index: int,
    db: DBDep,
    x_gemini_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    """Generate studio WAV audio for a Listening Part on demand using Gemini 3.8 TTS."""
    from pipelines.listening_audio import synthesize_part_audio

    test = db.get(ListeningTest, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Listening test not found.")
    part = next((p for p in test.parts_json if int(p["index"]) == part_index), None)
    if part is None:
        raise HTTPException(status_code=404, detail="Listening part not found.")

    settings = get_settings()
    active_key = (x_gemini_api_key or "").strip() or (settings.gemini_api_key or "").strip()
    if not active_key:
        raise HTTPException(
            status_code=400,
            detail="No Gemini API key available. Add your key via API Settings or use Browser Multi-Voice playback.",
        )
    try:
        out_path = synthesize_part_audio(
            part,
            output_dir=settings.audio_dir,
            model=settings.gemini_tts_model,
            api_key=active_key,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Gemini TTS synthesis failed: {exc}") from exc

    return {
        "audio_url": f"/api/audio/{out_path.name}",
        "bytes": out_path.stat().st_size,
        "model": settings.gemini_tts_model,
    }


@router.get("/audio/{filename}")
def serve_audio_file(filename: str) -> FileResponse:
    """Serve pre-generated Listening WAV audio from data/audio/ safely."""
    safe_name = filename.replace("/", "").replace("\\", "").replace("..", "")
    audio_path = get_settings().audio_dir / safe_name
    if not audio_path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not generated yet.")
    return FileResponse(audio_path, media_type="audio/wav")


# ==================== UNIFIED PROGRESS, PAST SESSION REVIEW & RESETS ====================


def _build_progress(
    db: Session,
    user_id: str,
    limit: int,
    module_filter: str | None = None,
) -> ProgressSummaryResponse:
    stmt = select(TestSession).where(
        TestSession.user_id == user_id,
        TestSession.completed_at.is_not(None),
    )
    if module_filter:
        stmt = stmt.where(TestSession.module == module_filter)
    stmt = stmt.order_by(desc(TestSession.completed_at)).limit(limit)
    sessions = db.execute(stmt).scalars().all()

    title_map: dict[str, str] = {}
    for rt in db.execute(select(ReadingTest)).scalars().all():
        title_map[rt.id] = rt.title
    for lt in db.execute(select(ListeningTest)).scalars().all():
        title_map[lt.id] = lt.title

    history = [
        SessionHistoryItem(
            session_id=s.id,
            test_id=s.test_id,
            test_title=title_map.get(s.test_id, s.test_id),
            module=s.module,
            mode=s.mode,
            passage_index=s.passage_filter,
            raw_score=s.raw_score,
            total_questions=s.total_questions,
            overall_band=s.overall_band,
            duration_sec=s.duration_sec,
            started_at=s.started_at,
            completed_at=s.completed_at,
        )
        for s in sessions
    ]

    skill_stmt = select(UserSkillProfile).where(UserSkillProfile.user_id == user_id)
    if module_filter:
        skill_stmt = skill_stmt.where(UserSkillProfile.skill_key.like(f"{module_filter}:%"))
    skill_rows = db.execute(skill_stmt.order_by(UserSkillProfile.skill_key)).scalars().all()

    skills = [
        SkillProfileItem(
            skill_key=sk.skill_key,
            estimated_band=sk.estimated_band,
            correct_count=sk.correct_count,
            attempts_count=sk.attempts_count,
            accuracy_pct=round((sk.correct_count / sk.attempts_count) * 100.0, 1)
            if sk.attempts_count > 0
            else 0.0,
        )
        for sk in skill_rows
    ]
    return ProgressSummaryResponse(recent_sessions=history, skills=skills)


@router.get("/progress", response_model=ProgressSummaryResponse)
def get_unified_progress(
    db: DBDep,
    user_id: str = Query(default="local-learner"),
    module: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> ProgressSummaryResponse:
    return _build_progress(db, user_id=user_id, limit=limit, module_filter=module)


@router.get("/reading/sessions", response_model=ProgressSummaryResponse)
def get_reading_progress(
    db: DBDep,
    user_id: str = Query(default="local-learner"),
    limit: int = Query(default=15, ge=1, le=50),
) -> ProgressSummaryResponse:
    return _build_progress(db, user_id=user_id, limit=limit, module_filter="reading")


@router.get("/sessions/{session_id}", response_model=SubmitSessionResponse)
def get_completed_session_detail(session_id: str, db: DBDep) -> SubmitSessionResponse:
    """Return full graded result, verdicts, and summary for any past Reading or Listening session."""
    session = db.get(TestSession, session_id)
    if session is None or session.completed_at is None:
        raise HTTPException(status_code=404, detail=f"Completed session '{session_id}' not found.")

    if session.module == "listening":
        ltest = db.get(ListeningTest, session.test_id)
        test_title = ltest.title if ltest else session.test_id
    else:
        rtest = db.get(ReadingTest, session.test_id)
        test_title = rtest.title if rtest else session.test_id

    attempts = (
        db.execute(select(UserAttempt).where(UserAttempt.session_id == session.id))
        .scalars()
        .all()
    )
    item_ids = [a.item_id for a in attempts]
    items_by_id = {
        q.id: q
        for q in db.execute(select(QuestionItem).where(QuestionItem.id.in_(item_ids))).scalars().all()
    }

    verdicts: list[QuestionVerdict] = []
    qtype_stats: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for att in attempts:
        item = items_by_id.get(att.item_id)
        if item is None:
            continue
        raw_val = (att.user_response or {}).get("raw", "")
        user_display = ", ".join(raw_val) if isinstance(raw_val, list) else str(raw_val or "")
        is_ok = bool(att.is_correct)
        if is_ok:
            qtype_stats[item.question_type][0] += 1
        qtype_stats[item.question_type][1] += 1

        verdicts.append(
            QuestionVerdict(
                item_id=item.id,
                passage_index=item.passage_index,
                question_number=item.question_number,
                question_type=item.question_type,
                user_answer=user_display,
                normalized_user=att.normalized_response or "",
                accepted_answers=list(item.answer_key.get("accepted", [])),
                is_correct=is_ok,
                failure_reason=att.failure_reason,
                diagnostic_detail=att.diagnostic_detail,
                evidence_span=item.evidence_span,
            )
        )

    verdicts.sort(key=lambda v: v.question_number)
    breakdown = [
        QuestionTypeBreakdown(
            question_type=qtype,
            correct=corr,
            total=tot,
            accuracy_pct=round((corr / tot) * 100.0, 1) if tot > 0 else 0.0,
        )
        for qtype, (corr, tot) in sorted(qtype_stats.items())
    ]

    return SubmitSessionResponse(
        session_id=session.id,
        test_id=session.test_id,
        test_title=test_title,
        module=session.module,
        mode=session.mode,
        passage_index=session.passage_filter,
        raw_score=int(session.raw_score or 0),
        total_questions=session.total_questions,
        band_score=float(session.overall_band or 1.0),
        is_prorated_band=(session.total_questions != 40),
        duration_sec=int(session.duration_sec or 0),
        completed_at=session.completed_at,
        by_question_type=breakdown,
        verdicts=verdicts,
    )


@router.delete("/sessions", response_model=ResetResponse)
def reset_recent_sessions(
    db: DBDep,
    user_id: str = Query(default="local-learner"),
    module: str | None = Query(default=None),
) -> ResetResponse:
    """Delete persisted practice sessions (and cascaded attempts) for Reset button."""
    stmt = select(TestSession).where(TestSession.user_id == user_id)
    if module:
        stmt = stmt.where(TestSession.module == module)
    rows = db.execute(stmt).scalars().all()
    count = len(rows)
    for row in rows:
        db.delete(row)
    db.commit()
    return ResetResponse(deleted_count=count, scope=module or "all_sessions")


@router.delete("/skills", response_model=ResetResponse)
def reset_skill_profile(
    db: DBDep,
    user_id: str = Query(default="local-learner"),
    module: str | None = Query(default=None),
) -> ResetResponse:
    """Clear UserSkillProfile rows for the Reset Skill Accuracy Profile button."""
    stmt = delete(UserSkillProfile).where(UserSkillProfile.user_id == user_id)
    if module:
        stmt = stmt.where(UserSkillProfile.skill_key.like(f"{module}:%"))
    res = db.execute(stmt)
    db.commit()
    return ResetResponse(deleted_count=int(res.rowcount or 0), scope=module or "all_skills")


# ==================== DISTRACTOR EXPLAINERS (READING & LISTENING) ====================


@router.post("/reading/explain")
@router.post("/listening/explain")
def explain_distractor(
    payload: ExplainRequest,
    db: DBDep,
    x_gemini_api_key: str | None = Header(default=None),
    x_gemini_model: str | None = Header(default=None),
) -> dict[str, Any]:
    item = db.get(QuestionItem, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Question item '{payload.item_id}' not found.")

    return explain_item_distractor(
        db,
        item=item,
        user_answer=payload.user_answer,
        failure_reason=payload.failure_reason,
        api_key_override=x_gemini_api_key,
        model_override=x_gemini_model,
    )
