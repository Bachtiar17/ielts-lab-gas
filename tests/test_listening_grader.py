"""Unit tests for the 100% deterministic IELTS Listening grader."""

from backend.app.scoring.listening import grade_listening_item, normalize_listening_text


def test_date_time_currency_and_postcode_normalization() -> None:
    assert normalize_listening_text("14th July") == "14 july"
    assert normalize_listening_text("July 14") == "14 july"
    assert normalize_listening_text("the 14th of July") == "14 july"

    assert normalize_listening_text("9.30 am") == "9:30am"
    assert normalize_listening_text("09:30am") == "9:30am"
    assert normalize_listening_text("9:30 a.m.") == "9:30am"

    assert normalize_listening_text("£45") == "45"
    assert normalize_listening_text("45 pounds") == "45"
    assert normalize_listening_text("$20") == "20"

    assert normalize_listening_text("BH14 7QR", is_code=True) == "bh147qr"
    assert normalize_listening_text("bh147qr", is_code=True) == "bh147qr"


def test_listening_form_completion_and_word_limits() -> None:
    wl = {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"}
    assert grade_listening_item(
        "form_note_table_completion", "45 pounds", {"accepted": ["£45", "45"]}, {"max_words": 2, "allow_number": True}
    ).is_correct
    assert grade_listening_item(
        "form_note_table_completion", "45", {"accepted": ["£45"]}, wl
    ).is_correct
    assert grade_listening_item(
        "form_note_table_completion", "July 14th", {"accepted": ["14 July"]}, wl
    ).is_correct
    assert grade_listening_item(
        "form_note_table_completion", "bh147qr", {"accepted": ["BH14 7QR"], "is_code": True}, {"max_words": 2, "allow_number": True}
    ).is_correct

    over = grade_listening_item(
        "form_note_table_completion", "old bakery", {"accepted": ["bakery"]}, wl
    )
    assert not over.is_correct
    assert over.failure_reason == "word_limit_exceeded"


def test_listening_map_matching_and_mcq() -> None:
    assert grade_listening_item("map_plan_diagram", "f", {"accepted": ["F"]}).is_correct
    assert not grade_listening_item("map_plan_diagram", "G", {"accepted": ["F"]}).is_correct
    assert grade_listening_item("matching", "e", {"accepted": ["E"]}).is_correct
    assert grade_listening_item("mcq_single", "B", {"accepted": ["B"]}).is_correct
    assert grade_listening_item("mcq_multi", ["C", "A"], {"accepted": ["A", "C"]}).is_correct
    blank = grade_listening_item("map_plan_diagram", "", {"accepted": ["A"]})
    assert blank.failure_reason == "blank"
