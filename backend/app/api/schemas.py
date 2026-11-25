"""Pydantic request/response schemas for Reading, Listening, Sessions, and Settings APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    database_dialect: str
    gemini_configured: bool
    gemini_fast_model: str
    reading_drill_bank_count: int = 0
    listening_test_count: int = 0


class TestGeminiKeyRequest(BaseModel):
    api_key: str = Field(min_length=10)
    model: str = "gemini-3.5-flash-lite"


class TestGeminiKeyResponse(BaseModel):
    ok: bool
    model_used: str
    message: str


class PassageSummary(BaseModel):
    index: int
    title: str
    subtitle: str
    topic: str
    question_count: int
    recommended_minutes: int


class ReadingTestSummary(BaseModel):
    id: str
    title: str
    subtitle: str
    difficulty_label: str
    duration_minutes: int
    total_questions: int
    passages: list[PassageSummary]


class DrillCardItem(BaseModel):
    id: str
    drill_slot: int
    title: str
    subtitle: str
    topic: str
    difficulty_label: str
    question_count: int
    recommended_minutes: int


class RandomDrillsResponse(BaseModel):
    bank_size: int
    drills: list[DrillCardItem]


class PublicQuestionItem(BaseModel):
    """Sanitized question DTO — strictly excludes answer_key and evidence_span."""

    id: str
    passage_index: int
    question_number: int
    question_type: str
    target_band: float
    prompt_payload: dict[str, Any]


class ReadingTestDetail(BaseModel):
    id: str
    title: str
    subtitle: str
    difficulty_label: str
    duration_minutes: int
    is_drill_bank: bool = False
    drill_slot: int | None = None
    passages: list[dict[str, Any]]
    questions: list[PublicQuestionItem]


class ListeningPartSummary(BaseModel):
    index: int
    title: str
    context: str
    question_count: int
    has_audio_file: bool
    has_map: bool


class ListeningTestSummary(BaseModel):
    id: str
    title: str
    subtitle: str
    difficulty_label: str
    duration_minutes: int
    total_questions: int
    parts: list[ListeningPartSummary]


class ListeningTestDetail(BaseModel):
    id: str
    title: str
    subtitle: str
    difficulty_label: str
    duration_minutes: int
    parts: list[dict[str, Any]]
    questions: list[PublicQuestionItem]


class CreateSessionRequest(BaseModel):
    test_id: str
    mode: Literal["drill", "section_mock"] = "section_mock"
    passage_index: int | None = Field(default=None, ge=1, le=4)
    user_id: str = "local-learner"


class CreateSessionResponse(BaseModel):
    session_id: str
    test_id: str
    module: str
    mode: str
    passage_index: int | None
    duration_minutes: int
    total_questions: int
    started_at: datetime


class SubmitSessionRequest(BaseModel):
    answers: dict[str, str | list[str]] = Field(
        default_factory=dict,
        description="Mapping of item_id -> learner response.",
    )
    duration_sec: int = Field(default=0, ge=0)


class QuestionVerdict(BaseModel):
    item_id: str
    passage_index: int
    question_number: int
    question_type: str
    user_answer: str
    normalized_user: str
    accepted_answers: list[str]
    is_correct: bool
    failure_reason: str | None
    diagnostic_detail: str | None
    evidence_span: dict[str, Any]


class QuestionTypeBreakdown(BaseModel):
    question_type: str
    correct: int
    total: int
    accuracy_pct: float


class SubmitSessionResponse(BaseModel):
    session_id: str
    test_id: str
    test_title: str = ""
    module: str = "reading"
    mode: str
    passage_index: int | None
    raw_score: int
    total_questions: int
    band_score: float
    is_prorated_band: bool
    duration_sec: int
    completed_at: datetime
    by_question_type: list[QuestionTypeBreakdown]
    verdicts: list[QuestionVerdict]


class ExplainRequest(BaseModel):
    item_id: str
    user_answer: str = ""
    failure_reason: str | None = None


class SessionHistoryItem(BaseModel):
    session_id: str
    test_id: str
    test_title: str
    module: str
    mode: str
    passage_index: int | None
    raw_score: int | None
    total_questions: int
    overall_band: float | None
    duration_sec: int | None
    started_at: datetime
    completed_at: datetime | None


class SkillProfileItem(BaseModel):
    skill_key: str
    estimated_band: float
    correct_count: int
    attempts_count: int
    accuracy_pct: float


class ProgressSummaryResponse(BaseModel):
    recent_sessions: list[SessionHistoryItem]
    skills: list[SkillProfileItem]


class ResetResponse(BaseModel):
    deleted_count: int
    scope: str
