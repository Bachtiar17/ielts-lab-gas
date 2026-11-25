import { NextRequest, NextResponse } from "next/server";
import { findReadingTestById, toPublicQuestion } from "@/lib/server/contentStore";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ testId: string }> }
) {
  const { testId } = await context.params;
  const test = findReadingTestById(testId);
  if (!test) {
    return NextResponse.json({ detail: `Reading test '${testId}' not found.` }, { status: 404 });
  }

  const { searchParams } = new URL(request.url);
  const passageParam = searchParams.get("passage_index");
  const passageIndex = passageParam ? Number(passageParam) : null;

  let passages = test.passages;
  let questions = test.questions;
  let duration = test.duration_minutes;

  if (passageIndex && !test.is_drill_bank) {
    passages = passages.filter((p) => p.index === passageIndex);
    questions = questions.filter((q) => q.passage_index === passageIndex);
    duration = passages[0]?.recommended_minutes ?? 20;
  }

  return NextResponse.json({
    id: test.id,
    title: test.title,
    subtitle: test.subtitle,
    difficulty_label: test.difficulty_label,
    duration_minutes: duration,
    is_drill_bank: test.is_drill_bank,
    drill_slot: test.drill_slot,
    passages,
    questions: questions.map(toPublicQuestion),
  });
}
