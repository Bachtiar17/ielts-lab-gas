"""100% deterministic Academic Reading grading engine.

Handles:
- Normalization (whitespace, casing, punctuation)
- UK/US spelling equivalence (bidirectional canonicalization)
- Written number <-> numeral equivalence (e.g. 'three' <-> '3', 'percent' <-> '%')
- Optional parentheticals and slash alternatives in answer keys
- Strict IELTS word/number-limit enforcement (hyphenated words count as ONE word)
- Diagnostic failure reasons ('blank', 'word_limit_exceeded', 'wrong_label_set', 'incorrect')
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from typing import Any

# Bidirectional UK <-> US canonical spelling map (both map to a canonical lowercase token).
UK_US_EQUIVALENTS: dict[str, str] = {
    "colour": "color",
    "colours": "colors",
    "coloured": "colored",
    "colourful": "colorful",
    "centre": "center",
    "centres": "centers",
    "centred": "centered",
    "metre": "meter",
    "metres": "meters",
    "kilometre": "kilometer",
    "kilometres": "kilometers",
    "litre": "liter",
    "litres": "liters",
    "fibre": "fiber",
    "fibres": "fibers",
    "theatre": "theater",
    "theatres": "theaters",
    "labour": "labor",
    "neighbour": "neighbor",
    "neighbours": "neighbors",
    "neighbourhood": "neighborhood",
    "behaviour": "behavior",
    "behaviours": "behaviors",
    "behavioural": "behavioral",
    "favour": "favor",
    "favourable": "favorable",
    "flavour": "flavor",
    "harbour": "harbor",
    "humour": "humor",
    "odour": "odor",
    "rumour": "rumor",
    "vapour": "vapor",
    "organisation": "organization",
    "organisations": "organizations",
    "organise": "organize",
    "organised": "organized",
    "organising": "organizing",
    "analyse": "analyze",
    "analysed": "analyzed",
    "analysing": "analyzing",
    "realise": "realize",
    "realised": "realized",
    "recognise": "recognize",
    "recognised": "recognized",
    "emphasise": "emphasize",
    "emphasised": "emphasized",
    "minimise": "minimize",
    "minimised": "minimized",
    "maximise": "maximize",
    "maximised": "maximized",
    "optimise": "optimize",
    "optimised": "optimized",
    "utilise": "utilize",
    "utilised": "utilized",
    "specialise": "specialize",
    "specialised": "specialized",
    "urbanisation": "urbanization",
    "industrialisation": "industrialization",
    "standardise": "standardize",
    "standardised": "standardized",
    "programme": "program",
    "programmes": "programs",
    "catalogue": "catalog",
    "catalogues": "catalogs",
    "dialogue": "dialog",
    "defence": "defense",
    "offence": "offense",
    "licence": "license",
    "practise": "practice",
    "travelling": "traveling",
    "travelled": "traveled",
    "traveller": "traveler",
    "modelling": "modeling",
    "modelled": "modeled",
    "labelling": "labeling",
    "labelled": "labeled",
    "cancelling": "canceling",
    "cancelled": "canceled",
    "grey": "gray",
    "artefact": "artifact",
    "artefacts": "artifacts",
    "aluminium": "aluminum",
    "archaeology": "archeology",
    "archaeological": "archeological",
    "mediaeval": "medieval",
    "sceptical": "skeptical",
    "scepticism": "skepticism",
    "manoeuvre": "maneuver",
    "ageing": "aging",
    "storey": "story",
    "storeys": "stories",
    "tyre": "tire",
    "tyres": "tires",
    "plough": "plow",
    "mould": "mold",
    "smoulder": "smolder",
    "fulfil": "fulfill",
    "fulfilment": "fulfillment",
    "enrol": "enroll",
    "enrolment": "enrollment",
    "skilful": "skillful",
    "wilful": "willful",
}

NUMBER_WORDS: dict[str, str] = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "first": "1st",
    "second": "2nd",
    "third": "3rd",
    "fourth": "4th",
    "fifth": "5th",
    "sixth": "6th",
    "seventh": "7th",
    "eighth": "8th",
    "ninth": "9th",
    "tenth": "10th",
}

TFNG_ALIASES: dict[str, str] = {
    "t": "TRUE",
    "true": "TRUE",
    "f": "FALSE",
    "false": "FALSE",
    "ng": "NOT GIVEN",
    "not given": "NOT GIVEN",
    "notgiven": "NOT GIVEN",
    "not-given": "NOT GIVEN",
}

YNNG_ALIASES: dict[str, str] = {
    "y": "YES",
    "yes": "YES",
    "n": "NO",
    "no": "NO",
    "ng": "NOT GIVEN",
    "not given": "NOT GIVEN",
    "notgiven": "NOT GIVEN",
    "not-given": "NOT GIVEN",
}

NUMBER_TOKEN_RE = re.compile(r"^\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?$", re.IGNORECASE)


@dataclass(frozen=True)
class WordLimitRule:
    """Structured IELTS word & number constraint for completion / short-answer items."""

    max_words: int | None = None
    allow_number: bool = True
    max_numbers: int | None = None
    numbers_only: bool = False
    label: str = ""


@dataclass
class GradeResult:
    """Deterministic grading verdict for a single question item."""

    is_correct: bool
    normalized_user: str
    accepted_display: list[str] = field(default_factory=list)
    failure_reason: str | None = None  # blank | word_limit_exceeded | wrong_label_set | incorrect
    diagnostic_detail: str | None = None
    word_count: int = 0
    number_count: int = 0


def parse_word_limit(spec: dict[str, Any] | None) -> WordLimitRule | None:
    """Build a WordLimitRule from answer_key/prompt metadata if present."""
    if not spec:
        return None
    if not any(k in spec for k in ("max_words", "allow_number", "max_numbers", "numbers_only", "label")):
        return None
    return WordLimitRule(
        max_words=spec.get("max_words"),
        allow_number=spec.get("allow_number", True),
        max_numbers=spec.get("max_numbers"),
        numbers_only=spec.get("numbers_only", False),
        label=str(spec.get("label", "")),
    )


def count_ielts_tokens(raw_text: str) -> tuple[int, int]:
    """Count (word_count, number_count) following official IELTS rules.

    - Hyphenated compounds like 'long-term' or 'well-known' count as ONE word.
    - Pure numeric tokens like '1850', '4.5', '25%' count as numbers (not words when allow_number=True).
    """
    cleaned = raw_text.strip()
    if not cleaned:
        return 0, 0
    # Replace punctuation except internal hyphens, apostrophes, decimals, percent, currency
    cleaned = re.sub(r"[,;:!?\"()\[\]{}]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return 0, 0

    word_count = 0
    number_count = 0
    for token in cleaned.split(" "):
        tok = token.strip(".").strip()
        if not tok:
            continue
        stripped_currency = tok.lstrip("$£€")
        if NUMBER_TOKEN_RE.match(stripped_currency):
            number_count += 1
        else:
            word_count += 1
    return word_count, number_count


def check_word_limit(raw_text: str, rule: WordLimitRule | None) -> tuple[bool, int, int, str | None]:
    """Validate raw user input against an IELTS word/number limit rule."""
    words, numbers = count_ielts_tokens(raw_text)
    if rule is None:
        return True, words, numbers, None

    if rule.numbers_only and words > 0:
        return False, words, numbers, f"Expected a number only, but received {words} word(s)."

    if not rule.allow_number and numbers > 0:
        return False, words, numbers, f"Numbers are not allowed ({rule.label or 'WORDS ONLY'})."

    if rule.max_words is not None and words > rule.max_words:
        return (
            False,
            words,
            numbers,
            f"Exceeded word limit: wrote {words} word(s), maximum allowed is {rule.max_words} ({rule.label}).",
        )

    if rule.max_numbers is not None and numbers > rule.max_numbers:
        return (
            False,
            words,
            numbers,
            f"Exceeded number limit: wrote {numbers} number(s), maximum allowed is {rule.max_numbers}.",
        )

    return True, words, numbers, None


def normalize_text(text: str, *, allow_number_words: bool = True) -> str:
    """Normalize text for deterministic IELTS Reading/Listening comparison."""
    s = text.strip().lower()
    # Normalize unicode dashes and quotes
    s = s.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    # Standardize 'per cent' / 'percent' -> '%'
    s = re.sub(r"\bper\s+cent\b", "%", s)
    s = re.sub(r"\bpercent\b", "%", s)
    s = re.sub(r"(\d)\s+%", r"\1%", s)
    # Strip trailing/leading punctuation (keep internal hyphens, apostrophes, decimals, %)
    s = re.sub(r"[^\w\s'%.-]", " ", s)
    s = re.sub(r"(?<!\d)\.(?!\d)", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    canonical_tokens: list[str] = []
    for tok in s.split(" "):
        if not tok:
            continue
        # Canonicalize hyphenated segments individually as well
        if "-" in tok:
            parts = [UK_US_EQUIVALENTS.get(p, p) for p in tok.split("-")]
            tok = "-".join(parts)
        else:
            tok = UK_US_EQUIVALENTS.get(tok, tok)
        if allow_number_words and tok in NUMBER_WORDS:
            tok = NUMBER_WORDS[tok]
        canonical_tokens.append(tok)

    return " ".join(canonical_tokens)


def expand_answer_variants(pattern: str) -> list[str]:
    """Expand optional parentheticals '(the) bridge' and slash alternatives 'a/b'."""
    # Split slash alternatives first unless inside parentheses
    raw_branches = [b.strip() for b in pattern.split("/") if b.strip()]
    expanded: list[str] = []

    paren_re = re.compile(r"\(([^()]+)\)")
    for branch in raw_branches:
        matches = list(paren_re.finditer(branch))
        if not matches:
            expanded.append(branch)
            continue
        # Generate include/exclude combinations for each parenthetical group
        for mask in itertools.product((False, True), repeat=len(matches)):
            parts: list[str] = []
            cursor = 0
            for match, keep in zip(matches, mask):
                parts.append(branch[cursor : match.start()])
                if keep:
                    parts.append(match.group(1))
                cursor = match.end()
            parts.append(branch[cursor:])
            candidate = re.sub(r"\s+", " ", "".join(parts)).strip()
            if candidate:
                expanded.append(candidate)

    # Deduplicate preserving order
    return list(dict.fromkeys(expanded))


def grade_reading_item(
    question_type: str,
    user_response: str | list[str] | None,
    answer_key: dict[str, Any],
    word_limit_spec: dict[str, Any] | None = None,
) -> GradeResult:
    """Deterministically grade a single IELTS Academic Reading question item."""
    qtype = question_type.strip().lower()
    accepted_raw: list[str] = list(answer_key.get("accepted", []))
    allow_number_words = bool(answer_key.get("allow_number_words", True))

    # Handle multi-select MCQ
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

    # Single string response handling
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

    # 1. TRUE / FALSE / NOT GIVEN
    if qtype == "tfng":
        key_lower = re.sub(r"\s+", " ", raw_str.lower()).strip()
        expected = TFNG_ALIASES.get(accepted_raw[0].strip().lower(), accepted_raw[0].strip().upper())
        if key_lower in {"y", "yes", "n", "no"}:
            return GradeResult(
                is_correct=False,
                normalized_user=raw_str.upper(),
                accepted_display=[expected],
                failure_reason="wrong_label_set",
                diagnostic_detail="Used YES/NO on a TRUE/FALSE/NOT GIVEN question.",
            )
        mapped = TFNG_ALIASES.get(key_lower, raw_str.upper())
        is_ok = mapped == expected
        return GradeResult(
            is_correct=is_ok,
            normalized_user=mapped,
            accepted_display=[expected],
            failure_reason=None if is_ok else "incorrect",
            diagnostic_detail=None if is_ok else f"Selected {mapped}; correct answer is {expected}.",
        )

    # 2. YES / NO / NOT GIVEN
    if qtype == "ynng":
        key_lower = re.sub(r"\s+", " ", raw_str.lower()).strip()
        expected = YNNG_ALIASES.get(accepted_raw[0].strip().lower(), accepted_raw[0].strip().upper())
        if key_lower in {"t", "true", "f", "false"}:
            return GradeResult(
                is_correct=False,
                normalized_user=raw_str.upper(),
                accepted_display=[expected],
                failure_reason="wrong_label_set",
                diagnostic_detail="Used TRUE/FALSE on a YES/NO/NOT GIVEN question.",
            )
        mapped = YNNG_ALIASES.get(key_lower, raw_str.upper())
        is_ok = mapped == expected
        return GradeResult(
            is_correct=is_ok,
            normalized_user=mapped,
            accepted_display=[expected],
            failure_reason=None if is_ok else "incorrect",
            diagnostic_detail=None if is_ok else f"Selected {mapped}; correct answer is {expected}.",
        )

    # 3. Single-letter MCQ & Matching (case-insensitive exact option ID, e.g. A, B, iv, vii)
    if qtype in {
        "mcq_single",
        "matching_headings",
        "matching_information",
        "matching_features",
        "matching_sentence_endings",
    }:
        norm_user = raw_str.strip().lower()
        accepted_norm = {a.strip().lower() for a in accepted_raw}
        is_ok = norm_user in accepted_norm
        # Preserve Roman numeral lowercase style for headings, uppercase for letter choices
        display_user = norm_user if qtype == "matching_headings" else norm_user.upper()
        return GradeResult(
            is_correct=is_ok,
            normalized_user=display_user,
            accepted_display=accepted_raw,
            failure_reason=None if is_ok else "incorrect",
            diagnostic_detail=None if is_ok else f"Selected '{display_user}'; expected '{accepted_raw[0]}'.",
        )

    # 4. Completion & Short-Answer questions (strict IELTS word-limit + UK/US & number normalization)
    rule = parse_word_limit(word_limit_spec or answer_key.get("word_limit"))
    within_limit, words, numbers, limit_msg = check_word_limit(raw_str, rule)
    norm_user = normalize_text(raw_str, allow_number_words=allow_number_words)

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
            accepted_variants.add(normalize_text(variant, allow_number_words=allow_number_words))

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
