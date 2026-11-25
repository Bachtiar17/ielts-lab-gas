"""Export verified IELTS Lab content & taxonomy into a single JSON bundle for the Node.js / AI Studio runtime.

Keeps Python seeds (`backend/app/seeds/`) and `data/` as the single source of truth so
the Next.js API routes serve the exact same 40-question Reading mock, 30-passage Reading
drill bank, 40-question 4-Part Listening mock, IDP taxonomy, and IELTS Advantage notes.

Usage:
    .venv/bin/python -m pipelines.export_web_bundle
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.seeds.listening_seed import LISTENING_PARTS, LISTENING_QUESTIONS, LISTENING_TEST_ID
from backend.app.seeds.reading_bank_p1 import P1_DRILLS
from backend.app.seeds.reading_bank_p2 import P2_DRILLS
from backend.app.seeds.reading_bank_p3 import P3_DRILLS
from backend.app.seeds.reading_seed import PASSAGES, QUESTIONS, READING_TEST_ID
from pipelines.schemas import StrategyNote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "frontend" / "src" / "data" / "content_bundle.json"


def build_bundle() -> dict[str, Any]:
    taxonomy_path = PROJECT_ROOT / "data" / "spec" / "idp_academic_taxonomy.json"
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))

    notes_dir = PROJECT_ROOT / "data" / "notes"
    notes: list[dict[str, Any]] = []
    for json_file in sorted(notes_dir.glob("*.json")):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            note = StrategyNote.model_validate(entry)
            notes.append(
                {
                    "id": note.source_video_id,
                    "source_type": "ielts_advantage",
                    "summary_md": note.to_markdown(),
                    **note.model_dump(),
                }
            )

    reading_mocks = [
        {
            "id": READING_TEST_ID,
            "title": "IELTS Academic Reading Practice Test 01",
            "subtitle": (
                "Original 3-passage calibrated mock covering T/F/NG, Note Completion, Matching Headings, "
                "Matching Features, Summary Completion, MCQ, Y/N/NG, Matching Sentence Endings, and Short Answer."
            ),
            "difficulty_label": "Band 6.0–8.5",
            "duration_minutes": 60,
            "is_drill_bank": False,
            "drill_slot": None,
            "passages": PASSAGES,
            "questions": QUESTIONS,
        }
    ]

    reading_drills = [
        {
            "id": d["id"],
            "title": d["title"],
            "subtitle": d["subtitle"],
            "difficulty_label": d["difficulty_label"],
            "duration_minutes": d["duration_minutes"],
            "is_drill_bank": True,
            "drill_slot": d["drill_slot"],
            "passages": d["passages"],
            "questions": d["questions"],
        }
        for d in (P1_DRILLS + P2_DRILLS + P3_DRILLS)
    ]

    listening_tests = [
        {
            "id": LISTENING_TEST_ID,
            "title": "IELTS Academic Listening Practice Test 01",
            "subtitle": (
                "Official post-2020 4-Part format (40 questions, 30 min): Rowing Club Enquiry, "
                "Maritime Museum Floorplan Map, Urban Micro-Forests Tutorial, and Ancient Amphitheatre Acoustics."
            ),
            "difficulty_label": "Band 6.0–8.5",
            "duration_minutes": 30,
            "parts": LISTENING_PARTS,
            "questions": LISTENING_QUESTIONS,
        }
    ]

    return {
        "taxonomy": taxonomy,
        "notes": notes,
        "reading_mocks": reading_mocks,
        "reading_drills": reading_drills,
        "listening_tests": listening_tests,
    }


def main() -> None:
    bundle = build_bundle()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Exported web content bundle -> {OUTPUT_PATH} "
        f"(mocks={len(bundle['reading_mocks'])}, drills={len(bundle['reading_drills'])}, "
        f"listening={len(bundle['listening_tests'])}, notes={len(bundle['notes'])})"
    )


if __name__ == "__main__":
    main()
