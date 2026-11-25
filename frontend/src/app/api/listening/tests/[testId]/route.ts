import { NextRequest, NextResponse } from "next/server";
import { findListeningTestById, toPublicQuestion } from "@/lib/server/contentStore";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ testId: string }> }
) {
  const { testId } = await context.params;
  const test = findListeningTestById(testId);
  if (!test) {
    return NextResponse.json({ detail: `Listening test '${testId}' not found.` }, { status: 404 });
  }

  const { searchParams } = new URL(request.url);
  const partParam = searchParams.get("part_index");
  const partIndex = partParam ? Number(partParam) : null;

  const rawParts = partIndex ? test.parts.filter((p) => p.index === partIndex) : test.parts;
  const questions = partIndex
    ? test.questions.filter((q) => q.passage_index === partIndex)
    : test.questions;
  const duration = partIndex ? 8 : test.duration_minutes;

  return NextResponse.json({
    id: test.id,
    title: test.title,
    subtitle: test.subtitle,
    difficulty_label: test.difficulty_label,
    duration_minutes: duration,
    parts: rawParts.map((p) => ({ ...p, audio_url: null })),
    questions: questions.map(toPublicQuestion),
  });
}
