/**
 * Read-only loader over the exported verified IELTS Lab content bundle.
 */

import bundleJson from "@/data/content_bundle.json";
import type { AnswerKeySpec } from "@/lib/server/readingGrader";
import type {
  EvidenceSpan,
  ListeningPart,
  PublicQuestionItem,
  ReadingPassage,
  StrategyNoteItem,
} from "@/types/reading";

export interface StoredQuestionItem extends PublicQuestionItem {
  answer_key: AnswerKeySpec;
  evidence_span: EvidenceSpan;
}

export interface StoredReadingTest {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  is_drill_bank: boolean;
  drill_slot: number | null;
  passages: ReadingPassage[];
  questions: StoredQuestionItem[];
}

export interface StoredListeningTest {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  parts: Omit<ListeningPart, "audio_url">[];
  questions: StoredQuestionItem[];
}

export interface StoredNote extends StrategyNoteItem {
  module: string;
  source_type: string;
  source_video_id: string;
  summary_md: string;
}

interface ContentBundle {
  taxonomy: Record<string, unknown>;
  notes: StoredNote[];
  reading_mocks: StoredReadingTest[];
  reading_drills: StoredReadingTest[];
  listening_tests: StoredListeningTest[];
}

const bundle = bundleJson as unknown as ContentBundle;

export function getTaxonomy(): Record<string, unknown> {
  return bundle.taxonomy;
}

export function getAllNotes(moduleName?: string | null, questionType?: string | null): StoredNote[] {
  return bundle.notes.filter((n) => {
    if (moduleName && n.module.toLowerCase() !== moduleName.toLowerCase()) return false;
    if (questionType && n.question_type.toLowerCase() !== questionType.toLowerCase()) return false;
    return true;
  });
}

export function getReadingMocks(): StoredReadingTest[] {
  return bundle.reading_mocks;
}

export function getReadingDrills(): StoredReadingTest[] {
  return bundle.reading_drills;
}

export function findReadingTestById(testId: string): StoredReadingTest | undefined {
  return (
    bundle.reading_mocks.find((t) => t.id === testId) ||
    bundle.reading_drills.find((t) => t.id === testId)
  );
}

export function getListeningTests(): StoredListeningTest[] {
  return bundle.listening_tests;
}

export function findListeningTestById(testId: string): StoredListeningTest | undefined {
  return bundle.listening_tests.find((t) => t.id === testId);
}

export function findQuestionItemById(itemId: string): {
  module: "reading" | "listening";
  test: StoredReadingTest | StoredListeningTest;
  item: StoredQuestionItem;
} | null {
  for (const t of [...bundle.reading_mocks, ...bundle.reading_drills]) {
    const found = t.questions.find((q) => q.id === itemId);
    if (found) return { module: "reading", test: t, item: found };
  }
  for (const lt of bundle.listening_tests) {
    const found = lt.questions.find((q) => q.id === itemId);
    if (found) return { module: "listening", test: lt, item: found };
  }
  return null;
}

export function toPublicQuestion(q: StoredQuestionItem): PublicQuestionItem {
  return {
    id: q.id,
    passage_index: q.passage_index,
    question_number: q.question_number,
    question_type: q.question_type,
    target_band: q.target_band,
    prompt_payload: q.prompt_payload,
  };
}
