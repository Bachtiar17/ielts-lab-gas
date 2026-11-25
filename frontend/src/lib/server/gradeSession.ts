/**
 * Shared deterministic session grading helper for Reading & Listening Next.js API routes.
 */

import { rawToListeningBand, rawToReadingBand } from "@/lib/server/bandMath";
import type { StoredQuestionItem } from "@/lib/server/contentStore";
import { gradeListeningItem } from "@/lib/server/listeningGrader";
import { gradeReadingItem } from "@/lib/server/readingGrader";
import { saveCompletedSession } from "@/lib/server/sessionStore";
import type {
  QuestionTypeBreakdown,
  QuestionVerdict,
  SubmitSessionResponse,
} from "@/types/reading";

export function gradeAndStoreSession(params: {
  sessionId: string;
  testId: string;
  testTitle: string;
  moduleName: "reading" | "listening";
  mode: "drill" | "section_mock";
  passageIndex: number | null;
  items: StoredQuestionItem[];
  answers: Record<string, string | string[]>;
  durationSec: number;
}): SubmitSessionResponse {
  const {
    sessionId,
    testId,
    testTitle,
    moduleName,
    mode,
    passageIndex,
    items,
    answers,
    durationSec,
  } = params;

  const isListening = moduleName === "listening";
  const grader = isListening ? gradeListeningItem : gradeReadingItem;
  const bandFn = isListening ? rawToListeningBand : rawToReadingBand;

  let rawScore = 0;
  const verdicts: QuestionVerdict[] = [];
  const qtypeStats: Record<string, [number, number]> = {};

  for (const item of items) {
    const rawResp = answers[item.id] ?? "";
    const grade = grader(
      item.question_type,
      rawResp,
      item.answer_key,
      item.prompt_payload.word_limit ?? null
    );
    if (!qtypeStats[item.question_type]) {
      qtypeStats[item.question_type] = [0, 0];
    }
    if (grade.is_correct) {
      rawScore += 1;
      qtypeStats[item.question_type][0] += 1;
    }
    qtypeStats[item.question_type][1] += 1;

    const userDisplay = Array.isArray(rawResp) ? rawResp.join(", ") : String(rawResp || "");
    verdicts.push({
      item_id: item.id,
      passage_index: item.passage_index,
      question_number: item.question_number,
      question_type: item.question_type,
      user_answer: userDisplay,
      normalized_user: grade.normalized_user,
      accepted_answers: grade.accepted_display,
      is_correct: grade.is_correct,
      failure_reason: grade.failure_reason,
      diagnostic_detail: grade.diagnostic_detail,
      evidence_span: item.evidence_span,
    });
  }

  const totalQ = items.length;
  const bandScore = bandFn(rawScore, totalQ);
  const completedAt = new Date().toISOString();

  const byQuestionType: QuestionTypeBreakdown[] = Object.entries(qtypeStats)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([question_type, [correct, total]]) => ({
      question_type,
      correct,
      total,
      accuracy_pct: total > 0 ? Math.round((correct / total) * 1000) / 10 : 0,
    }));

  const response: SubmitSessionResponse = {
    session_id: sessionId,
    test_id: testId,
    test_title: testTitle,
    module: moduleName,
    mode,
    passage_index: passageIndex,
    raw_score: rawScore,
    total_questions: totalQ,
    band_score: bandScore,
    is_prorated_band: totalQ !== 40,
    duration_sec: durationSec,
    completed_at: completedAt,
    by_question_type: byQuestionType,
    verdicts,
  };

  saveCompletedSession(sessionId, response);
  return response;
}
