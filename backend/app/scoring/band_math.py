"""Official IELTS Academic raw-to-band conversion curves and band rounding math.

Pure deterministic code — never delegated to an LLM.
"""

from __future__ import annotations

import math

# Separate official IDP/Cambridge IELTS Academic Reading raw (0-40) -> Band (1.0-9.0) curve.
ACADEMIC_READING_CURVE: tuple[tuple[int, int, float], ...] = (
    (39, 40, 9.0),
    (37, 38, 8.5),
    (35, 36, 8.0),
    (33, 34, 7.5),
    (30, 32, 7.0),
    (27, 29, 6.5),
    (23, 26, 6.0),
    (19, 22, 5.5),
    (15, 18, 5.0),
    (13, 14, 4.5),
    (10, 12, 4.0),
    (8, 9, 3.5),
    (6, 7, 3.0),
    (4, 5, 2.5),
    (1, 3, 2.0),
    (0, 0, 1.0),
)

# Separate official IELTS Listening raw (0-40) -> Band (1.0-9.0) curve (ready for Milestone 2).
LISTENING_CURVE: tuple[tuple[int, int, float], ...] = (
    (39, 40, 9.0),
    (37, 38, 8.5),
    (35, 36, 8.0),
    (32, 34, 7.5),
    (30, 31, 7.0),
    (26, 29, 6.5),
    (23, 25, 6.0),
    (18, 22, 5.5),
    (16, 17, 5.0),
    (13, 15, 4.5),
    (10, 12, 4.0),
    (8, 9, 3.5),
    (6, 7, 3.0),
    (4, 5, 2.5),
    (1, 3, 2.0),
    (0, 0, 1.0),
)


def round_to_half(score: float) -> float:
    """Official IELTS half-band rounding: .25 rounds up to .5, .75 rounds up to next whole band."""
    clamped = max(0.0, min(9.0, score))
    # Multiply by 2 and use half-up rounding (avoiding Python's banker's rounding).
    scaled = clamped * 2.0
    rounded_half = math.floor(scaled + 0.5 + 1e-12) / 2.0
    return max(0.0, min(9.0, rounded_half))


def _lookup_curve(
    raw_score: int,
    curve: tuple[tuple[int, int, float], ...],
    total_questions: int = 40,
) -> float:
    if total_questions <= 0:
        raise ValueError("total_questions must be positive")
    if raw_score < 0 or raw_score > total_questions:
        raise ValueError(f"raw_score ({raw_score}) must be within 0..{total_questions}")

    if total_questions == 40:
        equivalent_raw = raw_score
    else:
        # Proportionally scale single-passage drills (e.g. 13-14 questions) onto the 40-point curve.
        equivalent_raw = int(math.floor((raw_score / total_questions) * 40.0 + 0.5 + 1e-12))
        equivalent_raw = max(0, min(40, equivalent_raw))

    for low, high, band in curve:
        if low <= equivalent_raw <= high:
            return band
    return 1.0


def raw_to_reading_band(raw_score: int, total_questions: int = 40) -> float:
    """Map Academic Reading raw score to official IELTS Band (1.0-9.0)."""
    return _lookup_curve(raw_score, ACADEMIC_READING_CURVE, total_questions=total_questions)


def raw_to_listening_band(raw_score: int, total_questions: int = 40) -> float:
    """Map Listening raw score to official IELTS Band (1.0-9.0)."""
    return _lookup_curve(raw_score, LISTENING_CURVE, total_questions=total_questions)


def compute_writing_band(task1_band: float, task2_band: float) -> float:
    """Official IELTS Writing formula: (Task 1 + 2 * Task 2) / 3, rounded to nearest 0.5."""
    return round_to_half((task1_band + 2.0 * task2_band) / 3.0)


def compute_speaking_band(fc: float, lr: float, gra: float, pronunciation: float) -> float:
    """Official IELTS Speaking formula: mean of 4 criteria rounded to nearest 0.5."""
    return round_to_half((fc + lr + gra + pronunciation) / 4.0)


def compute_overall_band(
    listening: float, reading: float, writing: float, speaking: float
) -> float:
    """Official overall IELTS band: mean of 4 modules rounded to nearest 0.5."""
    return round_to_half((listening + reading + writing + speaking) / 4.0)
