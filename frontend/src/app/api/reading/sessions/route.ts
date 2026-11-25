import { NextRequest, NextResponse } from "next/server";
import { findReadingTestById } from "@/lib/server/contentStore";
import { createSessionRecord, getProgressSummary } from "@/lib/server/sessionStore";

export async function GET() {
  return NextResponse.json(getProgressSummary("reading"));
}

export async function POST(request: NextRequest) {
  const body = (await request.json().catch(() => ({}))) as {
    test_id?: string;
    mode?: "drill" | "section_mock";
    passage_index?: number | null;
    user_id?: string;
  };
  const test = body.test_id ? findReadingTestById(body.test_id) : undefined;
  if (!test) {
    return NextResponse.json(
      { detail: `Reading test '${body.test_id || ""}' not found.` },
      { status: 404 }
    );
  }

  let mode: "drill" | "section_mock" = body.mode || "section_mock";
  let passageFilter: number | null = null;
  let items = test.questions;
  let durationMinutes = test.duration_minutes;

  if (test.is_drill_bank) {
    mode = "drill";
    passageFilter = null;
  } else if (mode === "drill") {
    if (!body.passage_index) {
      return NextResponse.json(
        { detail: "passage_index (1-3) is required for drill mode." },
        { status: 400 }
      );
    }
    passageFilter = body.passage_index;
    items = test.questions.filter((q) => q.passage_index === passageFilter);
    durationMinutes = 20;
  }

  const rec = createSessionRecord({
    user_id: body.user_id || "local-learner",
    test_id: test.id,
    test_title: test.title,
    module: "reading",
    mode,
    passage_index: passageFilter,
    total_questions: items.length,
    duration_minutes: durationMinutes,
  });

  return NextResponse.json({
    session_id: rec.session_id,
    test_id: rec.test_id,
    module: "reading",
    mode: rec.mode,
    passage_index: rec.passage_index,
    duration_minutes: rec.duration_minutes,
    total_questions: rec.total_questions,
    started_at: rec.started_at,
  });
}
