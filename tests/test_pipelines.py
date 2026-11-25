"""Unit tests for offline pipelines (Voice-to-Note schema + Cambridge telemetry hygiene)."""

from pathlib import Path

from pipelines.cambridge_telemetry import (
    aggregate_telemetry,
    classify_reference_pdf,
    compute_text_metrics,
    extract_reading_passages_from_text,
)
from pipelines.schemas import StrategyNote, TimestampAnchor
from pipelines.voice_to_note import (
    build_timestamp_url,
    extract_youtube_video_id,
    normalize_strategy_note,
    save_strategy_note,
)


def test_extract_youtube_video_id_formats() -> None:
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_strategy_note_normalization_and_serialization(tmp_path: Path) -> None:
    note = StrategyNote(
        source_video_id="abcDEF12345",
        source_url="https://youtu.be/abcDEF12345",
        title="True False Not Given Framework",
        module="reading",
        question_type="TFNG",
        strategy_steps=["Read the full claim.", "Verify against passage evidence."],
        common_mistakes=["Confusing FALSE with NOT GIVEN."],
        band_upgrade_patterns=["Paraphrase the claim into a yes/no question."],
        timestamp_anchors=[
            TimestampAnchor(time_sec=135, topic="Qualifier trap", url="https://example.com")
        ],
    )
    normalized = normalize_strategy_note(note, "abcDEF12345")
    assert normalized.question_type == "tfng"
    assert normalized.source_url == "https://www.youtube.com/watch?v=abcDEF12345"
    assert normalized.timestamp_anchors[0].url == build_timestamp_url("abcDEF12345", 135)

    json_path, md_path = save_strategy_note(normalized, output_dir=tmp_path)
    assert json_path.exists()
    assert md_path.exists()
    assert "[02:15]" in md_path.read_text(encoding="utf-8")


def test_cambridge_pdf_filter_strictly_books_15_to_19_academic() -> None:
    assert classify_reference_pdf(Path("Cambridge IELTS 19 Academic.pdf")) == (True, 19, "included")
    assert classify_reference_pdf(Path("Cambridge_IELTS_15_Academic.pdf")) == (True, 15, "included")

    ok_gt, _, reason_gt = classify_reference_pdf(Path("Cambridge IELTS 18 General Training.pdf"))
    assert not ok_gt and "excluded_keyword" in reason_gt

    ok_cae, _, reason_cae = classify_reference_pdf(Path("Cambridge CAE Practice Tests.pdf"))
    assert not ok_cae and "excluded_keyword" in reason_cae

    ok_old, _, reason_old = classify_reference_pdf(Path("Cambridge IELTS 12 Academic.pdf"))
    assert not ok_old and "book_out_of_range" in reason_old


def test_telemetry_extraction_contains_zero_verbatim_text() -> None:
    sentinel_sentence = "SUPER_SECRET_SENTINEL_PASSAGE_PHRASE_XYZ987"
    synthetic_passage = " ".join(
        [f"{sentinel_sentence} coastal engineering tidal reservoir hydrology." for _ in range(70)]
    )
    synthetic_pdf_text = (
        f"READING PASSAGE 1\nYou should spend about 20 minutes on Questions 1-13.\n"
        f"{synthetic_passage}\n"
        f"Questions 1-6\nDo the following statements agree? TRUE FALSE NOT GIVEN\n"
        f"Questions 7-13\nComplete the notes below. Choose ONE WORD ONLY from the passage.\n"
    )

    metrics = compute_text_metrics(synthetic_passage)
    assert metrics["word_count"] >= 350

    passages = extract_reading_passages_from_text(synthetic_pdf_text, book_number=19)
    assert len(passages) == 1
    assert passages[0].passage_number == 1
    assert "tfng" in passages[0].detected_question_types
    assert "ONE WORD ONLY" in passages[0].detected_word_limits

    report = aggregate_telemetry(passages, files_scanned=1, files_excluded=["CAE.pdf (excluded_keyword:cae)"])
    serialized = report.model_dump_json()
    # Copyright hygiene guarantee: zero verbatim source phrases appear in calibration output
    assert sentinel_sentence not in serialized
    assert "coastal engineering" not in serialized
