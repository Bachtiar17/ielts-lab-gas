export interface WordLimitSpec {
  max_words?: number | null;
  allow_number?: boolean;
  max_numbers?: number | null;
  numbers_only?: boolean;
  label?: string;
}

export interface PassageParagraph {
  id: string;
  text: string;
}

export interface QuestionOption {
  id: string;
  text: string;
}

export interface QuestionGroup {
  id: string;
  title: string;
  question_type: string;
  instructions: string;
  word_limit?: WordLimitSpec;
  note_heading?: string;
  options?: QuestionOption[];
  question_numbers: number[];
}

export interface ReadingPassage {
  index: number;
  title: string;
  subtitle: string;
  topic: string;
  recommended_minutes: number;
  paragraphs: PassageParagraph[];
  question_groups: QuestionGroup[];
}

export interface PublicQuestionItem {
  id: string;
  passage_index: number;
  question_number: number;
  question_type: string;
  target_band: number;
  prompt_payload: {
    group_id: string;
    prompt: string;
    options?: QuestionOption[];
    word_limit?: WordLimitSpec;
  };
}

export interface PassageSummary {
  index: number;
  title: string;
  subtitle: string;
  topic: string;
  question_count: number;
  recommended_minutes: number;
}

export interface ReadingTestSummary {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  total_questions: number;
  passages: PassageSummary[];
}

export interface DrillCardItem {
  id: string;
  drill_slot: number;
  title: string;
  subtitle: string;
  topic: string;
  difficulty_label: string;
  question_count: number;
  recommended_minutes: number;
}

export interface RandomDrillsResponse {
  bank_size: number;
  drills: DrillCardItem[];
}

export interface ReadingTestDetail {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  is_drill_bank?: boolean;
  drill_slot?: number | null;
  passages: ReadingPassage[];
  questions: PublicQuestionItem[];
}

export interface TranscriptTurn {
  id: string;
  speaker: string;
  style?: string;
  text: string;
}

export interface MapLandmark {
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  kind: "anchor" | "courtyard" | "water";
}

export interface MapSlot {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface ListeningMapData {
  title: string;
  compass: string;
  landmarks: MapLandmark[];
  slots: MapSlot[];
}

export interface ListeningPart {
  index: number;
  title: string;
  context: string;
  speakers: { speaker: string; voice: string; accent: string; role: string }[];
  audio_filename: string;
  audio_url: string | null;
  map_data?: ListeningMapData;
  transcript: TranscriptTurn[];
  question_groups: QuestionGroup[];
}

export interface ListeningPartSummary {
  index: number;
  title: string;
  context: string;
  question_count: number;
  has_audio_file: boolean;
  has_map: boolean;
}

export interface ListeningTestSummary {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  total_questions: number;
  parts: ListeningPartSummary[];
}

export interface ListeningTestDetail {
  id: string;
  title: string;
  subtitle: string;
  difficulty_label: string;
  duration_minutes: number;
  parts: ListeningPart[];
  questions: PublicQuestionItem[];
}

export interface CreateSessionResponse {
  session_id: string;
  test_id: string;
  module: string;
  mode: "drill" | "section_mock";
  passage_index: number | null;
  duration_minutes: number;
  total_questions: number;
  started_at: string;
}

export interface EvidenceSpan {
  paragraph_id?: string;
  transcript_id?: string;
  quote?: string;
  distractor_note?: string;
}

export interface QuestionVerdict {
  item_id: string;
  passage_index: number;
  question_number: number;
  question_type: string;
  user_answer: string;
  normalized_user: string;
  accepted_answers: string[];
  is_correct: boolean;
  failure_reason: string | null;
  diagnostic_detail: string | null;
  evidence_span: EvidenceSpan;
}

export interface QuestionTypeBreakdown {
  question_type: string;
  correct: number;
  total: number;
  accuracy_pct: number;
}

export interface SubmitSessionResponse {
  session_id: string;
  test_id: string;
  test_title?: string;
  module?: string;
  mode: string;
  passage_index: number | null;
  raw_score: number;
  total_questions: number;
  band_score: number;
  is_prorated_band: boolean;
  duration_sec: number;
  completed_at: string;
  by_question_type: QuestionTypeBreakdown[];
  verdicts: QuestionVerdict[];
}

export interface TimestampAnchor {
  time_sec: number;
  topic: string;
  url: string;
}

export interface StrategyNoteItem {
  id: string;
  module?: string;
  question_type: string;
  source_url: string;
  title: string;
  channel: string;
  strategy_steps: string[];
  common_mistakes: string[];
  band_upgrade_patterns: string[];
  timestamp_anchors: TimestampAnchor[];
}

export interface DistractorExplanationResponse {
  item_id: string;
  module?: string;
  question_number: number;
  question_type: string;
  passage_index: number;
  user_answer: string;
  accepted_answers: string[];
  failure_reason: string | null;
  evidence_span: EvidenceSpan;
  explanation: {
    why_wrong: string;
    evidence_reasoning: string;
    distractor_trap: string;
    how_to_avoid_next_time: string;
  };
  strategy_note: StrategyNoteItem | null;
  explainer_mode: string;
}

export interface SessionHistoryItem {
  session_id: string;
  test_id: string;
  test_title: string;
  module: string;
  mode: string;
  passage_index: number | null;
  raw_score: number | null;
  total_questions: number;
  overall_band: number | null;
  duration_sec: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface SkillProfileItem {
  skill_key: string;
  estimated_band: number;
  correct_count: number;
  attempts_count: number;
  accuracy_pct: number;
}

export interface ProgressSummaryResponse {
  recent_sessions: SessionHistoryItem[];
  skills: SkillProfileItem[];
}

export interface TextHighlight {
  start: number;
  end: number;
  color: "yellow" | "green";
}

export interface TestGeminiKeyResponse {
  ok: boolean;
  model_used: string;
  message: string;
}
