import { NextResponse } from "next/server";
import { getReadingMocks } from "@/lib/server/contentStore";

export async function GET() {
  const summaries = getReadingMocks().map((test) => {
    const counts: Record<number, number> = {};
    for (const q of test.questions) {
      counts[q.passage_index] = (counts[q.passage_index] || 0) + 1;
    }
    return {
      id: test.id,
      title: test.title,
      subtitle: test.subtitle,
      difficulty_label: test.difficulty_label,
      duration_minutes: test.duration_minutes,
      total_questions: test.questions.length,
      passages: test.passages.map((p) => ({
        index: p.index,
        title: p.title,
        subtitle: p.subtitle,
        topic: p.topic,
        question_count: counts[p.index] || 0,
        recommended_minutes: p.recommended_minutes,
      })),
    };
  });
  return NextResponse.json(summaries);
}
