"""100% deterministic IELTS Listening grading engine.

Extends shared Reading normalization (UK/US spelling, number words, optional parentheticals,
hyphenated single-word counting, strict word/number limits) with Listening-specific rules:
- Date normalization ('14th July', '14 July', 'July 14', 'July 14th' -> '14 july')
- Time normalization ('9.30 am', '9:30am', '09:30' -> '9:30am' / '9:30')
- Currency normalization ('£45', '45 pounds', 'GBP 45' -> '45'; '$20', '20 dollars' -> '20')
- Alphanumeric reference/postcode spacing normalization ('BH14 7QR' == 'BH147QR')
- Map/plan labelling (A-H), matching, MCQ single/multi, form/note/table/summary completion
"""

from __future__ import annotations

import re
from typing import Any

from backend.app.scoring.reading import (
    GradeResult,
    check_word_limit,
    expand_answer_variants,
    normalize_text,
    parse_word_limit,
)

MONTHS: dict[str, str] = {
    "jan": "january",
    "january": "january",
    "feb": "february",
    "february": "february",
    "mar": "march",
    "march": "march",
    "apr": "april",
    "april": "april",
    "may": "may",
    "jun": "june",
    "june": "june",
    "jul": "july",
    "july": "july",
    "aug": "august",
    "august": "august",
    "sep": "september",
    "sept": "september",
    "september": "september",
    "oct": "october",
    "october": "october",
    "nov": "november",
    "november": "november",
    "dec": "december",
    "december": "december",
}

DATE_DM_RE = re.compile(r"^(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-z]+)$", re.IGNORECASE)
DATE_MD_RE = re.compile(r"^([a-z]+)\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?$", re.IGNORECASE)
TIME_RE = re.compile(r"^0?(\d{1,2})[:.](\d{2})\s*(a\.?m\.?|p\.?m\.?)?$", re.IGNORECASE)
CURRENCY_PREFIX_RE = re.compile(r"^[£$€]\s*(\d+(?:[.,]\d+)?)$")
CURRENCY_SUFFIX_RE = re.compile(
    r"^(\d+(?:[.,]\d+)?)\s*(?:pounds?|gbp|dollars?|usd|euros?|eur)$", re.IGNORECASE
)


def normalize_listening_text(text: str, *, allow_number_words: bool = True, is_code: bool = False) -> str:
    """Normalize a Listening response for deterministic comparison."""
    raw = text.strip()
    if not raw:
        return ""

    if is_code:
        # Postcodes / booking codes / phone numbers: ignore spaces and hyphens
        return re.sub(r"[\s-]+", "", raw.lower())

    # Check currency formats (£45 == 45 pounds == 45)
    m_cur_pre = CURRENCY_PREFIX_RE.match(raw)
    if m_cur_pre:
        return m_cur_pre.group(1).replace(",", "")
    m_cur_suf = CURRENCY_SUFFIX_RE.match(raw)
    if m_cur_suf:
        return m_cur_suf.group(1).replace(",", "")

    # Check time formats (9.30 am == 9:30am == 09:30 am)
    m_time = TIME_RE.match(raw)
    if m_time:
        hour = int(m_time.group(1))
        minute = m_time.group(2)
        ampm = (m_time.group(3) or "").replace(".", "").lower()
        return f"{hour}:{minute}{ampm}"

    # Check date formats (14th July == July 14 == 14 July)
    m_dm = DATE_DM_RE.match(raw)
    if m_dm and m_dm.group(2).lower() in MONTHS:
        return f"{int(m_dm.group(1))} {MONTHS[m_dm.group(2).lower()]}"
    m_md = DATE_MD_RE.match(raw)
    if m_md and m_md.group(1).lower() in MONTHS:
        return f"{int(m_md.group(2))} {MONTHS[m_md.group(1).lower()]}"

    return normalize_text(raw, allow_number_words=allow_number_words)


def grade_listening_item(
    question_type: str,
    user_response: str | list[str] | None,
    answer_key: dict[str, Any],
    word_limit_spec: dict[str, Any] | None = None,
) -> GradeResult:
    """Deterministically grade a single IELTS Listening question item."""
    qtype = question_type.strip().lower()
    accepted_raw: list[str] = list(answer_key.get("accepted", []))
    allow_number_words = bool(answer_key.get("allow_number_words", True))
    is_code = bool(answer_key.get("is_code", False))

    # Multi-select MCQ
    if qtype == "mcq_multi":
        user_list = (
            [str(x).strip().upper() for x in user_response if str(x).strip()]
            if isinstance(user_response, list)
            else [x.strip().upper() for x in str(user_response or "").split(",") if x.strip()]
        )
        expected_set = {str(x).strip().upper() for x in accepted_raw}
        if not user_list:
            return GradeResult(
                is_correct=False,
                normalized_user="",
                accepted_display=sorted(expected_set),
                failure_reason="blank",
                diagnostic_detail="No answer selected.",
            )
        user_set = set(user_list)
        is_ok = user_set == expected_set
        return GradeResult(
            is_correct=is_ok,
            normalized_user=", ".join(sorted(user_set)),
            accepted_display=sorted(expected_set),
            failure_reason=None if is_ok else "incorrect",
            diagnostic_detail=None if is_ok else f"Expected {', '.join(sorted(expected_set))}.",
        )

    raw_str = ""
    if isinstance(user_response, list):
        raw_str = " ".join(str(x) for x in user_response).strip()
    elif user_response is not None:
        raw_str = str(user_response).strip()

    if not raw_str:
        return GradeResult(
            is_correct=False,
            normalized_user="",
            accepted_display=accepted_raw,
            failure_reason="blank",
            diagnostic_detail="Question left unanswered.",
        )

    # Single-letter choice, matching, or map/plan/diagram labelling
    if qtype in {"mcq_single", "matching", "map_plan_diagram"}:
        norm_user = raw_str.strip().upper()
        accepted_norm = {a.strip().upper() for a in accepted_raw}
        is_ok = norm_user in accepted_norm
        return GradeResult(
            is_correct=is_ok,
            normalized_user=norm_user,
            accepted_display=accepted_raw,
            failure_reason=None if is_ok else "incorrect",
            diagnostic_detail=None if is_ok else f"Selected '{norm_user}'; expected '{accepted_raw[0]}'.",
        )

    # Form/note/table/summary/sentence completion & short-answer
    rule = parse_word_limit(word_limit_spec or answer_key.get("word_limit"))
    within_limit, words, numbers, limit_msg = check_word_limit(raw_str, rule)
    norm_user = normalize_listening_text(
        raw_str, allow_number_words=allow_number_words, is_code=is_code
    )

    if not within_limit:
        return GradeResult(
            is_correct=False,
            normalized_user=norm_user,
            accepted_display=accepted_raw,
            failure_reason="word_limit_exceeded",
            diagnostic_detail=limit_msg,
            word_count=words,
            number_count=numbers,
        )

    accepted_variants: set[str] = set()
    for pattern in accepted_raw:
        for variant in expand_answer_variants(pattern):
            accepted_variants.add(
                normalize_listening_text(
                    variant, allow_number_words=allow_number_words, is_code=is_code
                )
            )
            # Also accept bare number if pattern is currency like '£45'
            if CURRENCY_PREFIX_RE.match(variant.strip()):
                accepted_variants.add(CURRENCY_PREFIX_RE.match(variant.strip()).group(1))

    is_ok = norm_user in accepted_variants
    return GradeResult(
        is_correct=is_ok,
        normalized_user=norm_user,
        accepted_display=accepted_raw,
        failure_reason=None if is_ok else "incorrect",
        diagnostic_detail=None if is_ok else f"Expected one of: {', '.join(accepted_raw)}.",
        word_count=words,
        number_count=numbers,
    )
