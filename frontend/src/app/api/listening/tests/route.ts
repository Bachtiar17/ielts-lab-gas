import { NextResponse } from "next/server";
import { getListeningTests } from "@/lib/server/contentStore";

export async function GET() {
  const summaries = getListeningTests().map((test) => {
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
      parts: test.parts.map((p) => ({
        index: p.index,
        title: p.title,
        context: p.context,
        question_count: counts[p.index] || 0,
        has_audio_file: false,
        has_map: Boolean(p.map_data),
      })),
    };
  });
  return NextResponse.json(summaries);
}
