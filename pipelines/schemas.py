"""Strict Pydantic schemas for offline pipelines (Source #2 notes & Source #3 telemetry)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TimestampAnchor(BaseModel):
    """Clickable timestamp reference back to a specific teaching moment."""

    time_sec: int = Field(ge=0, description="Timestamp offset in seconds from video start.")
    topic: str = Field(min_length=2, description="Short topic label for this segment.")
    url: str = Field(description="Deep link URL pointing to the video at time_sec.")


class StrategyNote(BaseModel):
    """Structured IELTS Advantage study note schema (per .agents/rules/ielts-rubrics.md)."""

    source_video_id: str = Field(min_length=1, description="YouTube video ID or curated note ID.")
    source_url: str = Field(description="Canonical source URL with attribution.")
    title: str = Field(min_length=3, description="Concise title of the strategy note.")
    channel: str = Field(default="IELTS Advantage", description="Attributed pedagogy source.")
    module: Literal["reading", "listening", "writing", "speaking"]
    question_type: str = Field(min_length=2, description="IDP taxonomy question_type ID.")
    strategy_steps: list[str] = Field(min_length=1, description="Numbered actionable framework steps.")
    common_mistakes: list[str] = Field(min_length=1, description="Pitfalls keeping learners at Band 6.0-6.5.")
    band_upgrade_patterns: list[str] = Field(
        min_length=1, description="Concrete Band 6 -> Band 8 habits and paraphrasing techniques."
    )
    timestamp_anchors: list[TimestampAnchor] = Field(
        default_factory=list, description="Deep links back to exact moments in the source video."
    )

    @field_validator("question_type")
    @classmethod
    def normalize_question_type(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    def to_markdown(self) -> str:
        """Render clean, searchable Markdown synthesis (never raw transcript)."""
        lines = [
            f"# {self.title}",
            "",
            f"- **Source:** {self.channel} ([Watch original video]({self.source_url}))",
            f"- **Module:** `{self.module}` | **Question Type:** `{self.question_type}`",
            "",
            "## Core Strategy Steps",
        ]
        for idx, step in enumerate(self.strategy_steps, start=1):
            lines.append(f"{idx}. {step}")

        lines.extend(["", "## Common Mistakes (Band 6.0–6.5 Traps)"])
        for mistake in self.common_mistakes:
            lines.append(f"- {mistake}")

        lines.extend(["", "## Band 6 → Band 8 Upgrade Patterns"])
        for pattern in self.band_upgrade_patterns:
            lines.append(f"- {pattern}")

        if self.timestamp_anchors:
            lines.extend(["", "## Video Timestamp Anchors"])
            for anchor in self.timestamp_anchors:
                mins, secs = divmod(anchor.time_sec, 60)
                lines.append(f"- [{mins:02d}:{secs:02d}] [{anchor.topic}]({anchor.url})")

        return "\n".join(lines) + "\n"


class PassageTelemetry(BaseModel):
    """Non-copyrighted structural telemetry for a single academic reading passage."""

    book_number: int = Field(ge=15, le=19)
    test_number: int = Field(ge=1, le=4)
    passage_number: int = Field(ge=1, le=3)
    word_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    mean_words_per_sentence: float = Field(ge=0.0)
    long_word_ratio: float = Field(ge=0.0, le=1.0, description="Share of words with >= 7 letters.")
    type_token_ratio: float = Field(ge=0.0, le=1.0, description="Lexical diversity ratio.")
    detected_question_types: list[str] = Field(default_factory=list)
    detected_word_limits: list[str] = Field(default_factory=list)


class AggregatePassageStats(BaseModel):
    """Summary statistics aggregated across all inspected passages for a given slot (P1, P2, P3)."""

    passage_number: int = Field(ge=1, le=3)
    sample_count: int = Field(ge=0)
    word_count_min: int = 0
    word_count_median: float = 0.0
    word_count_mean: float = 0.0
    word_count_max: int = 0
    mean_words_per_sentence: float = 0.0
    mean_long_word_ratio: float = 0.0
    mean_type_token_ratio: float = 0.0
    question_type_counts: dict[str, int] = Field(default_factory=dict)
    word_limit_counts: dict[str, int] = Field(default_factory=dict)


class ReadingTelemetryReport(BaseModel):
    """Sanitized Cambridge Books 15-19 Academic structural telemetry output."""

    generated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    source_scope: str = "Cambridge IELTS 15-19 Academic (offline calibration only)"
    files_scanned: int = 0
    files_excluded: list[str] = Field(default_factory=list)
    passages_analyzed: int = 0
    by_passage_slot: list[AggregatePassageStats] = Field(default_factory=list)
    per_passage_metrics: list[PassageTelemetry] = Field(default_factory=list)
