"""Unit tests for deterministic IELTS band conversion and rounding rules."""

import pytest

from backend.app.scoring.band_math import (
    compute_overall_band,
    compute_speaking_band,
    compute_writing_band,
    raw_to_listening_band,
    raw_to_reading_band,
    round_to_half,
)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (6.0, 6.0),
        (6.125, 6.0),
        (6.24, 6.0),
        (6.25, 6.5),
        (6.5, 6.5),
        (6.74, 6.5),
        (6.75, 7.0),
        (7.875, 8.0),
        (9.0, 9.0),
    ],
)
def test_round_to_half_official_ielts_rules(score: float, expected: float) -> None:
    assert round_to_half(score) == expected


@pytest.mark.parametrize(
    ("raw", "expected_band"),
    [
        (40, 9.0),
        (39, 9.0),
        (38, 8.5),
        (37, 8.5),
        (35, 8.0),
        (33, 7.5),
        (30, 7.0),
        (27, 6.5),
        (23, 6.0),
        (19, 5.5),
        (15, 5.0),
        (10, 4.0),
        (1, 2.0),
        (0, 1.0),
    ],
)
def test_academic_reading_raw_to_band(raw: int, expected_band: float) -> None:
    assert raw_to_reading_band(raw) == expected_band


def test_listening_curve_differs_from_reading_at_32_and_26() -> None:
    # Listening 32 -> 7.5, Academic Reading 32 -> 7.0
    assert raw_to_listening_band(32) == 7.5
    assert raw_to_reading_band(32) == 7.0
    # Listening 26 -> 6.5, Academic Reading 26 -> 6.0
    assert raw_to_listening_band(26) == 6.5
    assert raw_to_reading_band(26) == 6.0


def test_prorated_single_passage_drill_scaling() -> None:
    # 13/13 -> 9.0; 10/13 (~31/40) -> 7.0; 0/13 -> 1.0
    assert raw_to_reading_band(13, total_questions=13) == 9.0
    assert raw_to_reading_band(10, total_questions=13) == 7.0
    assert raw_to_reading_band(0, total_questions=13) == 1.0


def test_invalid_raw_score_raises() -> None:
    with pytest.raises(ValueError):
        raw_to_reading_band(-1)
    with pytest.raises(ValueError):
        raw_to_reading_band(41)


def test_writing_speaking_and_overall_band_math() -> None:
    # (6.0 + 2*7.0)/3 = 6.666 -> 6.5
    assert compute_writing_band(6.0, 7.0) == 6.5
    # (6.5 + 2*7.5)/3 = 7.166 -> 7.0
    assert compute_writing_band(6.5, 7.5) == 7.0
    # (7.0 + 7.5 + 6.5 + 7.0)/4 = 7.0
    assert compute_speaking_band(7.0, 7.5, 6.5, 7.0) == 7.0
    # (7.5 + 7.0 + 6.5 + 6.0)/4 = 6.75 -> 7.0
    assert compute_overall_band(7.5, 7.0, 6.5, 6.0) == 7.0
