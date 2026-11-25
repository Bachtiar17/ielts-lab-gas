import { NextRequest, NextResponse } from "next/server";
import { findListeningTestById } from "@/lib/server/contentStore";
import { createSessionRecord } from "@/lib/server/sessionStore";

export async function POST(request: NextRequest) {
  const body = (await request.json().catch(() => ({}))) as {
    test_id?: string;
    mode?: "drill" | "section_mock";
    passage_index?: number | null;
    user_id?: string;
  };
  const test = body.test_id ? findListeningTestById(body.test_id) : undefined;
  if (!test) {
    return NextResponse.json(
      { detail: `Listening test '${body.test_id || ""}' not found.` },
      { status: 404 }
    );
  }

  const mode: "drill" | "section_mock" = body.mode || "section_mock";
  if (mode === "drill" && !body.passage_index) {
    return NextResponse.json(
      { detail: "passage_index (1-4) is required for Listening part drill." },
      { status: 400 }
    );
  }

  const partFilter = mode === "drill" ? body.passage_index ?? null : null;
  const items = partFilter
    ? test.questions.filter((q) => q.passage_index === partFilter)
    : test.questions;
  const durationMinutes = mode === "drill" ? 8 : test.duration_minutes;

  const rec = createSessionRecord({
    user_id: body.user_id || "local-learner",
    test_id: test.id,
    test_title: test.title,
    module: "listening",
    mode,
    passage_index: partFilter,
    total_questions: items.length,
    duration_minutes: durationMinutes,
  });

  return NextResponse.json({
    session_id: rec.session_id,
    test_id: rec.test_id,
    module: "listening",
    mode: rec.mode,
    passage_index: rec.passage_index,
    duration_minutes: rec.duration_minutes,
    total_questions: rec.total_questions,
    started_at: rec.started_at,
  });
}
