import { NextRequest, NextResponse } from "next/server";
import { findListeningTestById } from "@/lib/server/contentStore";
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
      { detail: `Listening session '${sessionId}' not found.` },
      { status: 404 }
    );
  }

  const test = findListeningTestById(resolvedTestId);
  if (!test) {
    return NextResponse.json({ detail: "Associated Listening test not found." }, { status: 404 });
  }

  const partIndex = session ? session.passage_index : body.passage_index ?? null;
  const mode = session ? session.mode : body.mode || (partIndex ? "drill" : "section_mock");
  const items = partIndex
    ? test.questions.filter((q) => q.passage_index === partIndex)
    : test.questions;

  const result = gradeAndStoreSession({
    sessionId,
    testId: test.id,
    testTitle: test.title,
    moduleName: "listening",
    mode,
    passageIndex: partIndex,
    items,
    answers: body.answers || {},
    durationSec: body.duration_sec || 0,
  });

  return NextResponse.json(result);
}
