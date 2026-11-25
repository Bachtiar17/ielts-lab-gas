"use client";

/**
 * Browser-side localStorage mirror for completed Reading/Listening sessions & skill accuracy.
 * Ensures each user (e.g. you and your friend on Google AI Studio) has persistent, private
 * progress that survives ephemeral container restarts without needing an external database.
 */

import { rawToListeningBand, rawToReadingBand } from "@/lib/server/bandMath";
import type {
  ProgressSummaryResponse,
  SessionHistoryItem,
  SkillProfileItem,
  SubmitSessionResponse,
} from "@/types/reading";

const SESSIONS_KEY = "ielts_lab_completed_sessions_v1";
const SKILLS_KEY = "ielts_lab_skill_profile_v1";

type LocalSkillsMap = Record<string, { correct: number; attempts: number }>;

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson(key: string, value: unknown): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage quota errors
  }
}

export function saveLocalCompletedSession(result: SubmitSessionResponse): void {
  const existing = readJson<Record<string, SubmitSessionResponse>>(SESSIONS_KEY, {});
  existing[result.session_id] = result;

  // Keep up to 50 most recent sessions in browser storage
  const entries = Object.entries(existing)
    .sort(([, a], [, b]) => (b.completed_at || "").localeCompare(a.completed_at || ""))
    .slice(0, 50);
  writeJson(SESSIONS_KEY, Object.fromEntries(entries));

  const skills = readJson<LocalSkillsMap>(SKILLS_KEY, {});
  const mod = result.module || "reading";
  for (const b of result.by_question_type) {
    const sk = `${mod}:${b.question_type}`;
    const prev = skills[sk] || { correct: 0, attempts: 0 };
    skills[sk] = {
      correct: prev.correct + b.correct,
      attempts: prev.attempts + b.total,
    };
  }
  writeJson(SKILLS_KEY, skills);
}

export function getLocalCompletedSession(sessionId: string): SubmitSessionResponse | null {
  const map = readJson<Record<string, SubmitSessionResponse>>(SESSIONS_KEY, {});
  return map[sessionId] || null;
}

export function getLocalProgressSummary(moduleFilter?: string): ProgressSummaryResponse {
  const sessionsMap = readJson<Record<string, SubmitSessionResponse>>(SESSIONS_KEY, {});
  const skillsMap = readJson<LocalSkillsMap>(SKILLS_KEY, {});

  const recent_sessions: SessionHistoryItem[] = Object.values(sessionsMap)
    .filter((s) => !moduleFilter || (s.module || "reading") === moduleFilter)
    .map((s) => ({
      session_id: s.session_id,
      test_id: s.test_id,
      test_title: s.test_title || s.test_id,
      module: s.module || "reading",
      mode: s.mode,
      passage_index: s.passage_index,
      raw_score: s.raw_score,
      total_questions: s.total_questions,
      overall_band: s.band_score,
      duration_sec: s.duration_sec,
      started_at: s.completed_at,
      completed_at: s.completed_at,
    }))
    .sort((a, b) => (b.completed_at || "").localeCompare(a.completed_at || ""))
    .slice(0, 25);

  const skills: SkillProfileItem[] = Object.entries(skillsMap)
    .filter(([key]) => !moduleFilter || key.startsWith(`${moduleFilter}:`))
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([skill_key, stat]) => {
      const bandFn = skill_key.startsWith("listening:") ? rawToListeningBand : rawToReadingBand;
      return {
        skill_key,
        estimated_band: stat.attempts > 0 ? bandFn(stat.correct, stat.attempts) : 6.0,
        correct_count: stat.correct,
        attempts_count: stat.attempts,
        accuracy_pct:
          stat.attempts > 0 ? Math.round((stat.correct / stat.attempts) * 1000) / 10 : 0,
      };
    });

  return { recent_sessions, skills };
}

export function clearLocalSessions(moduleFilter?: string): void {
  if (!moduleFilter) {
    writeJson(SESSIONS_KEY, {});
    return;
  }
  const map = readJson<Record<string, SubmitSessionResponse>>(SESSIONS_KEY, {});
  for (const [id, s] of Object.entries(map)) {
    if ((s.module || "reading") === moduleFilter) {
      delete map[id];
    }
  }
  writeJson(SESSIONS_KEY, map);
}

export function clearLocalSkills(moduleFilter?: string): void {
  if (!moduleFilter) {
    writeJson(SKILLS_KEY, {});
    return;
  }
  const skills = readJson<LocalSkillsMap>(SKILLS_KEY, {});
  for (const key of Object.keys(skills)) {
    if (key.startsWith(`${moduleFilter}:`)) {
      delete skills[key];
    }
  }
  writeJson(SKILLS_KEY, skills);
}
