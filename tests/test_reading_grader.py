"""Unit tests for the deterministic Academic Reading grader."""

from backend.app.scoring.reading import (
    count_ielts_tokens,
    expand_answer_variants,
    grade_reading_item,
    normalize_text,
)


def test_tfng_normalization_and_wrong_label_set() -> None:
    key = {"accepted": ["NOT GIVEN"]}
    assert grade_reading_item("tfng", "ng", key).is_correct
    assert grade_reading_item("tfng", "not  given", key).is_correct
    assert grade_reading_item("tfng", "TRUE", {"accepted": ["TRUE"]}).is_correct
    assert grade_reading_item("tfng", "f", {"accepted": ["FALSE"]}).is_correct

    wrong_set = grade_reading_item("tfng", "YES", {"accepted": ["TRUE"]})
    assert not wrong_set.is_correct
    assert wrong_set.failure_reason == "wrong_label_set"


def test_ynng_normalization_and_wrong_label_set() -> None:
    assert grade_reading_item("ynng", "y", {"accepted": ["YES"]}).is_correct
    assert grade_reading_item("ynng", "no", {"accepted": ["NO"]}).is_correct
    assert grade_reading_item("ynng", "NG", {"accepted": ["NOT GIVEN"]}).is_correct

    wrong_set = grade_reading_item("ynng", "TRUE", {"accepted": ["YES"]})
    assert not wrong_set.is_correct
    assert wrong_set.failure_reason == "wrong_label_set"


def test_uk_us_spelling_and_numeric_equivalence() -> None:
    assert normalize_text("Colourful Urbanisation") == normalize_text("colorful urbanization")
    assert normalize_text("twenty-nine percent") == "twenty-nine %"
    assert normalize_text("29 per cent") == "29%"
    assert normalize_text("three") == "3"

    res = grade_reading_item(
        "summary_completion",
        "colour",
        {"accepted": ["color"], "word_limit": {"max_words": 1, "allow_number": False}},
    )
    assert res.is_correct

    res_num = grade_reading_item(
        "short_answer",
        "3",
        {"accepted": ["three"], "word_limit": {"max_words": 1, "allow_number": True}},
    )
    assert res_num.is_correct


def test_hyphenated_word_counts_as_one_word_and_strict_word_limit() -> None:
    assert count_ielts_tokens("long-term") == (1, 0)
    assert count_ielts_tokens("twenty-nine percent") == (2, 0)
    assert count_ielts_tokens("29%") == (0, 1)

    rule = {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}
    ok_hyphen = grade_reading_item("sentence_completion", "long-term", {"accepted": ["long-term"]}, rule)
    assert ok_hyphen.is_correct

    too_long = grade_reading_item(
        "note_table_flowchart_completion",
        "a millpond",
        {"accepted": ["(a) millpond"]},
        rule,
    )
    assert not too_long.is_correct
    assert too_long.failure_reason == "word_limit_exceeded"
    assert too_long.word_count == 2


def test_optional_parentheticals_and_slash_variants() -> None:
    variants = expand_answer_variants("(the) hippocampus / brain region")
    assert "hippocampus" in variants
    assert "the hippocampus" in variants
    assert "brain region" in variants

    wl = {"max_words": 2, "allow_number": True, "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER"}
    assert grade_reading_item("short_answer", "hippocampus", {"accepted": ["(the) hippocampus"]}, wl).is_correct
    assert grade_reading_item("short_answer", "the hippocampus", {"accepted": ["(the) hippocampus"]}, wl).is_correct


def test_matching_and_mcq_grading() -> None:
    assert grade_reading_item("matching_headings", "IV", {"accepted": ["iv"]}).is_correct
    assert grade_reading_item("mcq_single", "b", {"accepted": ["B"]}).is_correct
    assert grade_reading_item("mcq_multi", ["C", "A"], {"accepted": ["A", "C"]}).is_correct
    blank = grade_reading_item("mcq_single", "", {"accepted": ["A"]})
    assert not blank.is_correct
    assert blank.failure_reason == "blank"
