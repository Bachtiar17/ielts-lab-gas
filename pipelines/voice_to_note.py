"""Source #2 Voice/Video-to-Structured-Note Parser (IELTS Advantage).

Fetches timestamped YouTube captions (or reads a local transcript file) and uses
Gemini (`gemini-4-hydrogen` via the official `google-genai` Interactions API) to
synthesize original structured study notes conforming to `StrategyNote`.

Usage:
    .venv/bin/python -m pipelines.voice_to_note \
        --video-url "https://www.youtube.com/watch?v=<VIDEO_ID>" \
        --module reading \
        --question-type tfng
"""

from __future__ import annotations

import argparse
import os
import re
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from google import genai

from pipelines.schemas import StrategyNote, TimestampAnchor

DEFAULT_NOTES_DIR = Path("data/notes")
DEFAULT_MODEL = "gemini-4-hydrogen"


def extract_youtube_video_id(video_url_or_id: str) -> str:
    """Extract a YouTube 11-character video ID from a URL or bare ID string."""
    candidate = video_url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return candidate

    parsed = urlparse(candidate)
    if parsed.hostname in {"youtu.be", "www.youtu.be"}:
        vid = parsed.path.lstrip("/").split("/")[0]
        if vid:
            return vid
    if parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path == "/watch":
            qs = parse_qs(parsed.query)
            if qs.get("v"):
                return qs["v"][0]
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            return parts[1]

    raise ValueError(f"Could not extract YouTube video ID from: {video_url_or_id}")


def build_timestamp_url(video_id: str, time_sec: int) -> str:
    """Return canonical YouTube deep link with seconds offset."""
    safe_sec = max(0, int(time_sec))
    return f"https://www.youtube.com/watch?v={video_id}&t={safe_sec}s"


def format_transcript_segments(segments: Iterable[dict[str, float | str]]) -> str:
    """Format timestamped transcript entries into a compact LLM-readable timeline."""
    lines: list[str] = []
    for seg in segments:
        start = int(float(seg.get("start", 0)))
        text = str(seg.get("text", "")).replace("\n", " ").strip()
        if text:
            lines.append(f"[{start}s] {text}")
    return "\n".join(lines)


def fetch_youtube_transcript(video_id: str, languages: tuple[str, ...] = ("en", "en-GB", "en-US")) -> str:
    """Fetch timestamped English captions using youtube-transcript-api."""
    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    if hasattr(api, "fetch"):
        fetched = api.fetch(video_id, languages=list(languages))
        segments = [{"start": item.start, "text": item.text} for item in fetched]
    else:
        segments = YouTubeTranscriptApi.get_transcript(video_id, languages=list(languages))
    return format_transcript_segments(segments)


def normalize_strategy_note(note: StrategyNote, video_id: str) -> StrategyNote:
    """Ensure canonical YouTube URL and properly formatted timestamp anchor deep links."""
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    fixed_anchors = [
        TimestampAnchor(
            time_sec=anchor.time_sec,
            topic=anchor.topic.strip(),
            url=build_timestamp_url(video_id, anchor.time_sec),
        )
        for anchor in note.timestamp_anchors
    ]
    return note.model_copy(
        update={
            "source_video_id": video_id,
            "source_url": canonical_url,
            "timestamp_anchors": fixed_anchors,
        }
    )


def parse_transcript_to_note(
    transcript_text: str,
    *,
    video_id: str,
    module: str,
    question_type: str,
    title_hint: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> StrategyNote:
    """Parse a spoken transcript into an original structured StrategyNote via Gemini Interactions API."""
    load_dotenv()
    resolved_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_key:
        raise RuntimeError(
            "GEMINI_API_KEY is required to run live Voice-to-Note parsing. "
            "Set GEMINI_API_KEY in .env and re-run."
        )

    resolved_model = model or os.getenv("GEMINI_FAST_MODEL", DEFAULT_MODEL)
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    prompt = f"""You are an expert IELTS Academic curriculum designer.
Synthesize the timestamped video transcript below into ORIGINAL, concise, structured study notes.
Strict copyright & pedagogy rules:
- NEVER copy verbatim transcript paragraphs. Synthesize crisp, original actionable teaching points.
- Preserve attribution to IELTS Advantage and link key concepts to the exact [seconds] timestamps present in the transcript.
- Focus on Band 6.0 -> Band 8.0+ exam execution for IELTS Academic.

Metadata:
- source_video_id: {video_id}
- source_url: {canonical_url}
- module: {module}
- question_type: {question_type}
- title_hint: {title_hint or "Infer a clear title from the lesson"}

Timestamped Transcript:
{transcript_text[:45000]}
"""

    client = genai.Client(api_key=resolved_key)
    interaction = client.interactions.create(
        model=resolved_model,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": StrategyNote.model_json_schema(),
        },
        store=False,
    )
    if not interaction.output_text:
        raise RuntimeError("Gemini returned an empty response while parsing transcript.")

    parsed = StrategyNote.model_validate_json(interaction.output_text)
    return normalize_strategy_note(parsed, video_id=video_id)


def save_strategy_note(note: StrategyNote, output_dir: Path = DEFAULT_NOTES_DIR) -> tuple[Path, Path]:
    """Persist structured note as both JSON and Markdown inside data/notes/."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{note.module}_{note.question_type}_{note.source_video_id}"
    json_path = output_dir / f"{slug}.json"
    md_path = output_dir / f"{slug}.md"

    json_path.write_text(note.model_dump_json(indent=2) + "\n", encoding="utf-8")
    md_path.write_text(note.to_markdown(), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse an IELTS Advantage video into structured notes.")
    parser.add_argument("--video-url", required=True, help="YouTube URL or 11-character video ID.")
    parser.add_argument("--module", required=True, choices=["reading", "listening", "writing", "speaking"])
    parser.add_argument("--question-type", required=True, help="IDP question type ID (e.g. tfng, matching_headings).")
    parser.add_argument("--title", default=None, help="Optional title hint.")
    parser.add_argument("--transcript-file", type=Path, default=None, help="Optional local transcript text file.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_NOTES_DIR)
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    video_id = extract_youtube_video_id(args.video_url)
    if args.transcript_file:
        transcript = args.transcript_file.read_text(encoding="utf-8")
    else:
        transcript = fetch_youtube_transcript(video_id)

    note = parse_transcript_to_note(
        transcript,
        video_id=video_id,
        module=args.module,
        question_type=args.question_type,
        title_hint=args.title,
        model=args.model,
    )
    json_path, md_path = save_strategy_note(note, output_dir=args.output_dir)
    print(f"Saved structured note:\n  JSON: {json_path}\n  MD:   {md_path}")


if __name__ == "__main__":
    main()
