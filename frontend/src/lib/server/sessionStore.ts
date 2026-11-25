/**
 * Lightweight server-side session & skill store for Node.js / Google AI Studio.
 * Uses globalThis + /tmp JSON cache for active container life, while the browser
 * also mirrors completed sessions & skills into localStorage so progress survives
 * ephemeral container restarts and keeps each user's history private!
 */

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { rawToListeningBand, rawToReadingBand } from "@/lib/server/bandMath";
import type {
  ProgressSummaryResponse,
  SessionHistoryItem,
  SkillProfileItem,
  SubmitSessionResponse,
} from "@/types/reading";

export interface ActiveSessionRecord {
  session_id: string;
  user_id: string;
  test_id: string;
  test_title: string;
  module: "reading" | "listening";
  mode: "drill" | "section_mock";
  passage_index: number | null;
  total_questions: number;
  duration_minutes: number;
  started_at: string;
  completed?: SubmitSessionResponse;
}

interface StoreState {
  sessions: Record<string, ActiveSessionRecord>;
  skills: Record<string, { correct: number; attempts: number }>;
}

const CACHE_FILE = path.join(os.tmpdir(), "ielts_lab_node_state.json");

const globalStore = globalThis as unknown as { __ieltsLabStore?: StoreState };

function loadState(): StoreState {
  if (globalStore.__ieltsLabStore) return globalStore.__ieltsLabStore;
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const parsed = JSON.parse(fs.readFileSync(CACHE_FILE, "utf-8")) as StoreState;
      if (parsed && parsed.sessions && parsed.skills) {
        globalStore.__ieltsLabStore = parsed;
        return parsed;
      }
    }
  } catch {
    // Ignore corrupted temp cache
  }
  globalStore.__ieltsLabStore = { sessions: {}, skills: {} };
  return globalStore.__ieltsLabStore;
}

function saveState(state: StoreState): void {
  globalStore.__ieltsLabStore = state;
  try {
    fs.writeFileSync(CACHE_FILE, JSON.stringify(state), "utf-8");
  } catch {
    // Ephemeral / read-only FS fallback: in-memory state still works
  }
}

export function createSessionRecord(params: {
  user_id: string;
  test_id: string;
  test_title: string;
  module: "reading" | "listening";
  mode: "drill" | "section_mock";
  passage_index: number | null;
  total_questions: number;
  duration_minutes: number;
}): ActiveSessionRecord {
  const state = loadState();
  const record: ActiveSessionRecord = {
    session_id: crypto.randomUUID(),
    ...params,
    started_at: new Date().toISOString(),
  };
  state.sessions[record.session_id] = record;
  saveState(state);
  return record;
}

export function getSessionRecord(sessionId: string): ActiveSessionRecord | undefined {
  return loadState().sessions[sessionId];
}

export function saveCompletedSession(
  sessionId: string,
  result: SubmitSessionResponse
): void {
  const state = loadState();
  const existing = state.sessions[sessionId];
  if (existing) {
    existing.completed = result;
  } else {
    state.sessions[sessionId] = {
      session_id: sessionId,
      user_id: "local-learner",
      test_id: result.test_id,
      test_title: result.test_title || result.test_id,
      module: result.module === "listening" ? "listening" : "reading",
      mode: result.mode === "drill" ? "drill" : "section_mock",
      passage_index: result.passage_index,
      total_questions: result.total_questions,
      duration_minutes: result.module === "listening" ? 30 : 60,
      started_at: result.completed_at,
      completed: result,
    };
  }

  for (const b of result.by_question_type) {
    const key = `${result.module || "reading"}:${b.question_type}`;
    const prev = state.skills[key] || { correct: 0, attempts: 0 };
    state.skills[key] = {
      correct: prev.correct + b.correct,
      attempts: prev.attempts + b.total,
    };
  }

  saveState(state);
}

export function getProgressSummary(moduleFilter?: string | null): ProgressSummaryResponse {
  const state = loadState();
  const completed: SessionHistoryItem[] = Object.values(state.sessions)
    .filter((s) => Boolean(s.completed) && (!moduleFilter || s.module === moduleFilter))
    .map((s) => ({
      session_id: s.session_id,
      test_id: s.test_id,
      test_title: s.test_title,
      module: s.module,
      mode: s.mode,
      passage_index: s.passage_index,
      raw_score: s.completed!.raw_score,
      total_questions: s.completed!.total_questions,
      overall_band: s.completed!.band_score,
      duration_sec: s.completed!.duration_sec,
      started_at: s.started_at,
      completed_at: s.completed!.completed_at,
    }))
    .sort((a, b) => (b.completed_at || "").localeCompare(a.completed_at || ""))
    .slice(0, 25);

  const skills: SkillProfileItem[] = Object.entries(state.skills)
    .filter(([key]) => !moduleFilter || key.startsWith(`${moduleFilter}:`))
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([skill_key, stat]) => {
      const bandFn = skill_key.startsWith("listening:") ? rawToListeningBand : rawToReadingBand;
      return {
        skill_key,
        estimated_band:
          stat.attempts > 0 ? bandFn(stat.correct, stat.attempts) : 6.0,
        correct_count: stat.correct,
        attempts_count: stat.attempts,
        accuracy_pct:
          stat.attempts > 0 ? Math.round((stat.correct / stat.attempts) * 1000) / 10 : 0,
      };
    });

  return { recent_sessions: completed, skills };
}

export function clearSessions(moduleFilter?: string | null): number {
  const state = loadState();
  let deleted = 0;
  for (const [id, rec] of Object.entries(state.sessions)) {
    if (!moduleFilter || rec.module === moduleFilter) {
      delete state.sessions[id];
      deleted += 1;
    }
  }
  saveState(state);
  return deleted;
}

export function clearSkills(moduleFilter?: string | null): number {
  const state = loadState();
  let deleted = 0;
  for (const key of Object.keys(state.skills)) {
    if (!moduleFilter || key.startsWith(`${moduleFilter}:`)) {
      delete state.skills[key];
      deleted += 1;
    }
  }
  saveState(state);
  return deleted;
}
