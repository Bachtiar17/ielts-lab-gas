"""Multi-speaker IELTS Listening audio generator using Gemini 3.8 TTS (v1beta Interactions API).

Generates studio-quality multi-speaker WAV files for Parts 1-4 into `data/audio/`
from the seeded original Listening scripts. Supports single-speaker monologues (Parts 2 & 4)
and multi-speaker dialogues (Parts 1 & 3) with per-turn `speech_metadata` annotations.

Usage:
    .venv/bin/python -m pipelines.listening_audio --part 1
    .venv/bin/python -m pipelines.listening_audio --all
"""

from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

from backend.app.seeds.listening_seed import LISTENING_PARTS

DEFAULT_AUDIO_DIR = Path("data/audio")
DEFAULT_TTS_MODEL = "gemini-3.8-flash-lite-tts"


def synthesize_part_audio(
    part: dict[str, Any],
    *,
    output_dir: Path = DEFAULT_AUDIO_DIR,
    model: str = DEFAULT_TTS_MODEL,
    api_key: str | None = None,
) -> Path:
    """Synthesize a single Listening Part's dialogue/monologue into a WAV file."""
    load_dotenv()
    resolved_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required to synthesize Gemini TTS audio. "
            "Without WAV files, the web app automatically uses zero-cost Browser Multi-Voice Speech."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / str(part["audio_filename"])

    speakers = part.get("speakers", [])
    transcript = part.get("transcript", [])

    # Build per-turn content with speech_metadata annotations
    content_items: list[dict[str, Any]] = []
    for turn in transcript:
        meta: dict[str, Any] = {
            "type": "speech_metadata",
            "style": turn.get("style", "clear, natural IELTS exam pace"),
        }
        if len(speakers) > 1:
            meta["speaker"] = turn["speaker"]
        content_items.append(
            {
                "type": "text",
                "text": turn["text"],
                "annotations": [meta],
            }
        )

    # Gemini 3.8 TTS supports up to 2 speakers in speech_config.speakers; map any 3rd speaker cleanly
    if len(speakers) == 1:
        speech_config: Any = [{"voice": speakers[0].get("voice", "Charon")}]
    else:
        primary_speakers = speakers[:2]
        allowed_names = {s["speaker"] for s in primary_speakers}
        fallback_speaker = primary_speakers[0]["speaker"]
        for item in content_items:
            sp = item["annotations"][0].get("speaker")
            if sp not in allowed_names:
                item["annotations"][0]["speaker"] = fallback_speaker
        speech_config = {
            "speakers": [
                {"speaker": s["speaker"], "voice": s.get("voice", "Kore")}
                for s in primary_speakers
            ]
        }

    client = genai.Client(api_key=resolved_key, http_options={"api_version": "v1beta"})
    interaction = client.interactions.create(
        model=model,
        input=[{"type": "user_input", "content": content_items}],
        response_format={"type": "audio"},
        generation_config={"speech_config": speech_config},
        store=False,
    )
    if not interaction.output_audio or not interaction.output_audio.data:
        raise RuntimeError(f"Gemini TTS returned no audio data for Part {part['index']}.")

    out_path.write_bytes(base64.b64decode(interaction.output_audio.data))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize IELTS Listening WAV audio via Gemini 3.8 TTS.")
    parser.add_argument("--part", type=int, choices=[1, 2, 3, 4], default=None)
    parser.add_argument("--all", action="store_true", help="Generate WAV files for all 4 parts.")
    parser.add_argument("--model", default=DEFAULT_TTS_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    args = parser.parse_args()

    targets = (
        LISTENING_PARTS
        if args.all or args.part is None
        else [p for p in LISTENING_PARTS if p["index"] == args.part]
    )
    for part in targets:
        out = synthesize_part_audio(part, output_dir=args.output_dir, model=args.model)
        print(f"Generated Part {part['index']} audio -> {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
