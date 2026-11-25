"""Core SQLAlchemy ORM models matching the IELTS Lab blueprint ER diagram."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class KnowledgeConcept(Base):
    """Structured pedagogy & strategy notes (IDP spec, IELTS Advantage notes, calibration)."""

    __tablename__ = "knowledge_concepts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    module: Mapped[str] = mapped_column(String(32), index=True)
    question_type: Mapped[str] = mapped_column(String(64), index=True)
    source_type: Mapped[str] = mapped_column(String(32), default="ielts_advantage")
    source_video_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_url: Mapped[str] = mapped_column(String(512))
    title: Mapped[str] = mapped_column(String(256))
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    summary_md: Mapped[str] = mapped_column(Text)
    embedding_json: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ReadingTest(Base):
    """Container for Academic Reading mock tests and single-passage drills."""

    __tablename__ = "reading_tests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    subtitle: Mapped[str] = mapped_column(String(512), default="")
    difficulty_label: Mapped[str] = mapped_column(String(64), default="Band 6.0–8.5")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_drill_bank: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    drill_slot: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)  # 1, 2, or 3
    passages_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    items: Mapped[list[QuestionItem]] = relationship(
        back_populates="reading_test",
        cascade="all, delete-orphan",
        order_by="QuestionItem.question_number",
    )


class ListeningTest(Base):
    """Container for post-2020 4-part IELTS Listening mock tests (40 questions, 30 min)."""

    __tablename__ = "listening_tests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    subtitle: Mapped[str] = mapped_column(String(512), default="")
    difficulty_label: Mapped[str] = mapped_column(String(64), default="Band 6.0–8.5")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    parts_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    items: Mapped[list[QuestionItem]] = relationship(
        back_populates="listening_test",
        cascade="all, delete-orphan",
        order_by="QuestionItem.question_number",
    )


class QuestionItem(Base):
    """Individual exam question across Reading, Listening, Writing, or Speaking."""

    __tablename__ = "question_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    test_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("reading_tests.id", ondelete="CASCADE"), nullable=True, index=True
    )
    listening_test_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("listening_tests.id", ondelete="CASCADE"), nullable=True, index=True
    )
    passage_index: Mapped[int] = mapped_column(Integer, default=1, index=True)
    question_number: Mapped[int] = mapped_column(Integer, index=True)
    module: Mapped[str] = mapped_column(String(32), default="reading", index=True)
    question_type: Mapped[str] = mapped_column(String(64), index=True)
    target_band: Mapped[float] = mapped_column(Float, default=7.0)
    prompt_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    answer_key: Mapped[dict[str, Any]] = mapped_column(JSON)
    evidence_span: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    media_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=True)

    reading_test: Mapped[ReadingTest | None] = relationship(back_populates="items")
    listening_test: Mapped[ListeningTest | None] = relationship(back_populates="items")


class TestSession(Base):
    """A single practice drill or mock test session (Reading or Listening)."""

    __tablename__ = "test_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(64), default="local-learner", index=True)
    test_id: Mapped[str] = mapped_column(String(64), index=True)
    mode: Mapped[str] = mapped_column(String(32), default="section_mock")  # drill | section_mock | full_mock
    passage_filter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    module: Mapped[str] = mapped_column(String(32), default="reading", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=40)
    overall_band: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)

    attempts: Mapped[list[UserAttempt]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class UserAttempt(Base):
    """Per-question learner response and deterministic verdict."""

    __tablename__ = "user_attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("test_sessions.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("question_items.id", ondelete="CASCADE"), index=True
    )
    user_response: Mapped[dict[str, Any]] = mapped_column(JSON)
    normalized_response: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    diagnostic_detail: Mapped[str | None] = mapped_column(String(512), nullable=True)
    time_spent_sec: Mapped[int] = mapped_column(Integer, default=0)

    session: Mapped[TestSession] = relationship(back_populates="attempts")


class RubricEvaluation(Base):
    """Multimodal AI rubric evaluations for Writing & Speaking (Milestones 3-4)."""

    __tablename__ = "rubric_evaluations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    attempt_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_attempts.id", ondelete="CASCADE"), unique=True
    )
    criteria_scores: Mapped[dict[str, float]] = mapped_column(JSON)
    band_score: Mapped[float] = mapped_column(Float)
    inline_annotations: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    error_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    scorer_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class UserSkillProfile(Base):
    """Per-skill accuracy & estimated band tracker for adaptive coaching."""

    __tablename__ = "user_skill_profile"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True, default="local-learner")
    skill_key: Mapped[str] = mapped_column(String(128), primary_key=True)  # e.g. reading:tfng, listening:map_plan_diagram
    estimated_band: Mapped[float] = mapped_column(Float, default=6.0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
