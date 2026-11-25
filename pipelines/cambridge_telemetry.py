"""Source #3 Offline Calibration Telemetry Pipeline (Cambridge IELTS Books 15-19 Academic).

Strictly offline analysis of PDFs placed in gitignored `data/private_reference/`.
- Filters exclusively to Cambridge IELTS Books 15-19 (Academic only).
- Explicitly excludes General Training PDFs, Books 1-14, and stray non-IELTS files (e.g. CAE).
- Outputs ONLY sanitized, non-copyrighted structural telemetry (word counts, sentence length,
  lexical diversity, question-type distributions, and word-limit frequencies) to
  `data/calibration/reading_telemetry.json`.
- NEVER copies, logs, or writes verbatim passages, questions, or answer keys.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from statistics import mean, median

from pipelines.schemas import (
    AggregatePassageStats,
    PassageTelemetry,
    ReadingTelemetryReport,
)

DEFAULT_REFERENCE_DIR = Path("data/private_reference")
DEFAULT_OUTPUT_PATH = Path("data/calibration/reading_telemetry.json")

EXCLUDED_KEYWORDS = (
    "general",
    "gt",
    "cae",
    "cpe",
    "fce",
    "toefl",
    "trainer",
)

QUESTION_TYPE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("tfng", re.compile(r"\bTRUE\b.*\bFALSE\b.*\bNOT\s+GIVEN\b", re.IGNORECASE | re.DOTALL)),
    ("ynng", re.compile(r"\bYES\b.*\bNO\b.*\bNOT\s+GIVEN\b", re.IGNORECASE | re.DOTALL)),
    ("matching_headings", re.compile(r"list\s+of\s+headings|correct\s+heading", re.IGNORECASE)),
    ("matching_information", re.compile(r"which\s+paragraph\s+contains\s+the\s+following", re.IGNORECASE)),
    ("matching_features", re.compile(r"list\s+of\s+(?:researchers|people|theories|findings|names)", re.IGNORECASE)),
    ("matching_sentence_endings", re.compile(r"complete\s+each\s+sentence\s+with\s+the\s+correct\s+ending", re.IGNORECASE)),
    ("summary_completion", re.compile(r"complete\s+the\s+summary", re.IGNORECASE)),
    ("note_table_flowchart_completion", re.compile(r"complete\s+the\s+(?:notes|table|flow-?chart)", re.IGNORECASE)),
    ("sentence_completion", re.compile(r"complete\s+the\s+sentences\s+below", re.IGNORECASE)),
    ("diagram_label_completion", re.compile(r"label\s+the\s+diagram", re.IGNORECASE)),
    ("mcq_single", re.compile(r"choose\s+the\s+correct\s+letter,\s*A,\s*B,\s*C\s+or\s+D", re.IGNORECASE)),
    ("mcq_multi", re.compile(r"choose\s+TWO\s+letters|choose\s+THREE\s+letters", re.IGNORECASE)),
    ("short_answer", re.compile(r"answer\s+the\s+questions\s+below", re.IGNORECASE)),
]

WORD_LIMIT_PATTERN = re.compile(
    r"\b(?:ONE\s+WORD\s+ONLY|ONE\s+WORD\s+AND/OR\s+A\s+NUMBER|"
    r"NO\s+MORE\s+THAN\s+(?:ONE|TWO|THREE)\s+WORDS?(?:\s+AND/OR\s+A\s+NUMBER)?)\b",
    re.IGNORECASE,
)


def classify_reference_pdf(pdf_path: Path) -> tuple[bool, int | None, str]:
    """Decide whether a PDF belongs to Cambridge IELTS Books 15-19 Academic.

    Returns:
        (is_included, book_number, reason)
    """
    name = pdf_path.name
    lower = name.lower()

    if pdf_path.suffix.lower() != ".pdf":
        return False, None, "non_pdf"

    for bad in EXCLUDED_KEYWORDS:
        if re.search(rf"(?<![a-z]){re.escape(bad)}(?![a-z])", lower):
            return False, None, f"excluded_keyword:{bad}"

    if "ielts" not in lower and "cambridge" not in lower:
        return False, None, "not_cambridge_ielts"

    match = re.search(r"(?:ielts|cambridge)\D{0,10}(\d{1,2})(?!\d)", lower)
    if not match:
        return False, None, "missing_book_number"

    book_num = int(match.group(1))
    if not (15 <= book_num <= 19):
        return False, book_num, f"book_out_of_range:{book_num}"

    return True, book_num, "included"


def compute_text_metrics(passage_text: str) -> dict[str, float | int]:
    """Compute strictly aggregate, non-reconstructible linguistic metrics for a passage."""
    tokens = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)*", passage_text)
    word_count = len(tokens)
    sentences = [s.strip() for s in re.split(r"[.!?]+", passage_text) if len(s.strip().split()) >= 3]
    sentence_count = max(1, len(sentences)) if word_count > 0 else 0

    if word_count == 0:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "mean_words_per_sentence": 0.0,
            "long_word_ratio": 0.0,
            "type_token_ratio": 0.0,
        }

    lower_tokens = [t.lower() for t in tokens]
    long_words = sum(1 for t in lower_tokens if len(t) >= 7)
    unique_words = len(set(lower_tokens))

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "mean_words_per_sentence": round(word_count / sentence_count, 2),
        "long_word_ratio": round(long_words / word_count, 4),
        "type_token_ratio": round(unique_words / word_count, 4),
    }


def detect_question_types_and_limits(section_text: str) -> tuple[list[str], list[str]]:
    """Detect IDP question types and word-limit directives from a reading section."""
    q_types = [qid for qid, pat in QUESTION_TYPE_PATTERNS if pat.search(section_text)]
    limits = sorted({re.sub(r"\s+", " ", m.group(0).upper()) for m in WORD_LIMIT_PATTERN.finditer(section_text)})
    return q_types, limits


def extract_reading_passages_from_text(full_text: str, book_number: int) -> list[PassageTelemetry]:
    """Parse Test 1-4 / Reading Passage 1-3 boundaries from extracted PDF text and return metrics only."""
    passage_header = re.compile(r"READING\s+PASSAGE\s+([123])\b", re.IGNORECASE)
    matches = list(passage_header.finditer(full_text))
    if not matches:
        return []

    results: list[PassageTelemetry] = []
    test_counter = 0

    for idx, m in enumerate(matches):
        p_num = int(m.group(1))
        if p_num == 1:
            test_counter += 1
        if test_counter == 0 or test_counter > 4:
            continue

        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else min(len(full_text), start + 14000)
        chunk = full_text[start:end]

        # Strip rubric header line ("You should spend about 20 minutes on Questions X-Y...") BEFORE splitting questions.
        chunk = re.sub(
            r"You should spend about 20 minutes on Questions.*?(?:\n|$)",
            "\n",
            chunk,
            flags=re.IGNORECASE,
        )

        # Split passage prose from question instructions where "Questions X-Y" begins.
        q_split = re.search(r"\bQuestions?\s+\d+\s*[–-]\s*\d+\b", chunk, re.IGNORECASE)
        if q_split:
            passage_body = chunk[: q_split.start()]
            questions_body = chunk[q_split.start() :]
        else:
            passage_body = chunk[:6000]
            questions_body = ""

        metrics = compute_text_metrics(passage_body)
        if metrics["word_count"] < 250:
            continue

        q_types, limits = detect_question_types_and_limits(questions_body)
        results.append(
            PassageTelemetry(
                book_number=book_number,
                test_number=test_counter,
                passage_number=p_num,
                word_count=int(metrics["word_count"]),
                sentence_count=int(metrics["sentence_count"]),
                mean_words_per_sentence=float(metrics["mean_words_per_sentence"]),
                long_word_ratio=float(metrics["long_word_ratio"]),
                type_token_ratio=float(metrics["type_token_ratio"]),
                detected_question_types=q_types,
                detected_word_limits=limits,
            )
        )

    return results


def aggregate_telemetry(
    per_passage: list[PassageTelemetry],
    *,
    files_scanned: int,
    files_excluded: list[str],
) -> ReadingTelemetryReport:
    """Aggregate per-passage metrics by Passage slot (1, 2, 3) into a calibration report."""
    by_slot: list[AggregatePassageStats] = []
    for slot in (1, 2, 3):
        items = [p for p in per_passage if p.passage_number == slot]
        if not items:
            by_slot.append(AggregatePassageStats(passage_number=slot, sample_count=0))
            continue

        wc = [p.word_count for p in items]
        q_counter: Counter[str] = Counter()
        l_counter: Counter[str] = Counter()
        for p in items:
            q_counter.update(p.detected_question_types)
            l_counter.update(p.detected_word_limits)

        by_slot.append(
            AggregatePassageStats(
                passage_number=slot,
                sample_count=len(items),
                word_count_min=min(wc),
                word_count_median=round(float(median(wc)), 1),
                word_count_mean=round(float(mean(wc)), 1),
                word_count_max=max(wc),
                mean_words_per_sentence=round(float(mean(p.mean_words_per_sentence for p in items)), 2),
                mean_long_word_ratio=round(float(mean(p.long_word_ratio for p in items)), 4),
                mean_type_token_ratio=round(float(mean(p.type_token_ratio for p in items)), 4),
                question_type_counts=dict(q_counter.most_common()),
                word_limit_counts=dict(l_counter.most_common()),
            )
        )

    return ReadingTelemetryReport(
        files_scanned=files_scanned,
        files_excluded=sorted(files_excluded),
        passages_analyzed=len(per_passage),
        by_passage_slot=by_slot,
        per_passage_metrics=per_passage,
    )


def scan_reference_directory(reference_dir: Path = DEFAULT_REFERENCE_DIR) -> ReadingTelemetryReport:
    """Scan local gitignored Cambridge PDFs in memory and return non-copyrighted telemetry."""
    import pymupdf

    if not reference_dir.exists():
        return aggregate_telemetry([], files_scanned=0, files_excluded=[])

    included_files: list[tuple[Path, int]] = []
    excluded_files: list[str] = []

    for path in sorted(reference_dir.rglob("*")):
        if path.is_dir() or path.name.startswith("."):
            continue
        ok, book_num, reason = classify_reference_pdf(path)
        if ok and book_num is not None:
            included_files.append((path, book_num))
        else:
            excluded_files.append(f"{path.name} ({reason})")

    all_metrics: list[PassageTelemetry] = []
    for pdf_path, book_num in included_files:
        with pymupdf.open(pdf_path) as doc:
            full_text = "\n".join(page.get_text("text") for page in doc)
        all_metrics.extend(extract_reading_passages_from_text(full_text, book_number=book_num))

    return aggregate_telemetry(
        all_metrics,
        files_scanned=len(included_files),
        files_excluded=excluded_files,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute offline Reading structural telemetry from Cambridge IELTS 15-19 Academic PDFs."
    )
    parser.add_argument("--reference-dir", type=Path, default=DEFAULT_REFERENCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    report = scan_reference_directory(args.reference_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(
        f"Telemetry written to {args.output} "
        f"(scanned={report.files_scanned}, passages={report.passages_analyzed}, excluded={len(report.files_excluded)})"
    )


if __name__ == "__main__":
    main()
