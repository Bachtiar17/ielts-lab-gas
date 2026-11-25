import { NextRequest, NextResponse } from "next/server";
import { findReadingTestById } from "@/lib/server/contentStore";
import { gradeAndStoreSession } from "@/lib/server/gradeSession";
import { getSessionRecord } from "@/lib/server/sessionStore";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await context.params;
  const body = (await request.json().catch(() => ({}))) as {
    answers?: Record<string, string | string[]>;
    duration_sec?: number;
    test_id?: string;
    mode?: "drill" | "section_mock";
    passage_index?: number | null;
  };

  const session = getSessionRecord(sessionId);
  const resolvedTestId = session?.test_id || body.test_id;
  if (!resolvedTestId) {
    return NextResponse.json(
      { detail: `Reading session '${sessionId}' not found.` },
      { status: 404 }
    );
  }

  const test = findReadingTestById(resolvedTestId);
  if (!test) {
    return NextResponse.json({ detail: "Associated Reading test not found." }, { status: 404 });
  }

  const passageIndex = session ? session.passage_index : body.passage_index ?? null;
  const mode = session ? session.mode : body.mode || (test.is_drill_bank ? "drill" : "section_mock");
  const items =
    passageIndex !== null && !test.is_drill_bank
      ? test.questions.filter((q) => q.passage_index === passageIndex)
      : test.questions;

  const result = gradeAndStoreSession({
    sessionId,
    testId: test.id,
    testTitle: test.title,
    moduleName: "reading",
    mode,
    passageIndex,
    items,
    answers: body.answers || {},
    durationSec: body.duration_sec || 0,
  });

  return NextResponse.json(result);
}
