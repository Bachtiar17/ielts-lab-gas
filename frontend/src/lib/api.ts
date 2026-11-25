import { loadPersonalGeminiConfig } from "@/lib/geminiSettings";
import {
  clearLocalSessions,
  clearLocalSkills,
  getLocalCompletedSession,
  getLocalProgressSummary,
  saveLocalCompletedSession,
} from "@/lib/localHistory";
import type {
  CreateSessionResponse,
  DistractorExplanationResponse,
  ListeningTestDetail,
  ListeningTestSummary,
  ProgressSummaryResponse,
  RandomDrillsResponse,
  ReadingTestDetail,
  ReadingTestSummary,
  StrategyNoteItem,
  SubmitSessionResponse,
  TestGeminiKeyResponse,
} from "@/types/reading";

// Default to same-origin ("") so Next.js built-in /api/* routes work on a single port (3000)
// in Google AI Studio, Cloud Run, or local `npm run dev`. Set NEXT_PUBLIC_API_URL=http://localhost:8000
// only if you explicitly want to target the Python FastAPI server locally.
function resolveApiBase(): string {
  const envBase = (process.env.NEXT_PUBLIC_API_URL || "").trim().replace(/\/$/, "");
  if (!envBase) return "";
  // Safety guard: never allow a stale localhost:8000 env var to break remote previews (e.g. Google AI Studio).
  if (
    typeof window !== "undefined" &&
    /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(envBase) &&
    !["localhost", "127.0.0.1"].includes(window.location.hostname)
  ) {
    return "";
  }
  return envBase;
}

export const API_BASE = resolveApiBase();

function personalGeminiHeaders(): Record<string, string> {
  const cfg = loadPersonalGeminiConfig();
  const headers: Record<string, string> = {};
  if (cfg.apiKey) {
    headers["X-Gemini-Api-Key"] = cfg.apiKey;
  }
  if (cfg.model) {
    headers["X-Gemini-Model"] = cfg.model;
  }
  return headers;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const base = resolveApiBase();
  const res = await fetch(`${base}${path}`, {
    ...init,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return (await res.json()) as T;
}

// ==================== READING ====================

export function fetchReadingTests(): Promise<ReadingTestSummary[]> {
  return apiFetch<ReadingTestSummary[]>("/api/reading/tests");
}

export function fetchRandomReadingDrills(excludeIds: string[] = []): Promise<RandomDrillsResponse> {
  const qs = excludeIds.length > 0 ? `?exclude=${encodeURIComponent(excludeIds.join(","))}` : "";
  return apiFetch<RandomDrillsResponse>(`/api/reading/drills/random${qs}`);
}

export function fetchReadingTestDetail(
  testId: string,
  passageIndex?: number | null
): Promise<ReadingTestDetail> {
  const qs = passageIndex ? `?passage_index=${passageIndex}` : "";
  return apiFetch<ReadingTestDetail>(`/api/reading/tests/${testId}${qs}`);
}

export function createReadingSession(payload: {
  test_id: string;
  mode: "drill" | "section_mock";
  passage_index?: number | null;
}): Promise<CreateSessionResponse> {
  return apiFetch<CreateSessionResponse>("/api/reading/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function submitReadingSession(
  sessionId: string,
  answers: Record<string, string>,
  durationSec: number,
  meta?: { test_id: string; mode: "drill" | "section_mock"; passage_index?: number | null }
): Promise<SubmitSessionResponse> {
  const res = await apiFetch<SubmitSessionResponse>(`/api/reading/sessions/${sessionId}/submit`, {
    method: "POST",
    body: JSON.stringify({
      answers,
      duration_sec: durationSec,
      ...(meta || {}),
    }),
  });
  saveLocalCompletedSession(res);
  return res;
}

export function explainReadingDistractor(payload: {
  item_id: string;
  user_answer: string;
  failure_reason?: string | null;
}): Promise<DistractorExplanationResponse> {
  return apiFetch<DistractorExplanationResponse>("/api/reading/explain", {
    method: "POST",
    headers: personalGeminiHeaders(),
    body: JSON.stringify(payload),
  });
}

// ==================== LISTENING ====================

export function fetchListeningTests(): Promise<ListeningTestSummary[]> {
  return apiFetch<ListeningTestSummary[]>("/api/listening/tests");
}

export function fetchListeningTestDetail(
  testId: string,
  partIndex?: number | null
): Promise<ListeningTestDetail> {
  const qs = partIndex ? `?part_index=${partIndex}` : "";
  return apiFetch<ListeningTestDetail>(`/api/listening/tests/${testId}${qs}`);
}

export function createListeningSession(payload: {
  test_id: string;
  mode: "drill" | "section_mock";
  passage_index?: number | null;
}): Promise<CreateSessionResponse> {
  return apiFetch<CreateSessionResponse>("/api/listening/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function submitListeningSession(
  sessionId: string,
  answers: Record<string, string>,
  durationSec: number,
  meta?: { test_id: string; mode: "drill" | "section_mock"; passage_index?: number | null }
): Promise<SubmitSessionResponse> {
  const res = await apiFetch<SubmitSessionResponse>(`/api/listening/sessions/${sessionId}/submit`, {
    method: "POST",
    body: JSON.stringify({
      answers,
      duration_sec: durationSec,
      ...(meta || {}),
    }),
  });
  saveLocalCompletedSession(res);
  return res;
}

export function explainListeningDistractor(payload: {
  item_id: string;
  user_answer: string;
  failure_reason?: string | null;
}): Promise<DistractorExplanationResponse> {
  return apiFetch<DistractorExplanationResponse>("/api/listening/explain", {
    method: "POST",
    headers: personalGeminiHeaders(),
    body: JSON.stringify(payload),
  });
}

export function synthesizeListeningPartAudio(
  testId: string,
  partIndex: number
): Promise<{ audio_url: string; bytes: number; model: string }> {
  return apiFetch(`/api/listening/tests/${testId}/parts/${partIndex}/synthesize`, {
    method: "POST",
    headers: personalGeminiHeaders(),
  });
}

// ==================== UNIFIED PROGRESS, PAST SESSIONS, RESETS & SETTINGS ====================

export async function fetchUnifiedProgress(moduleName?: string): Promise<ProgressSummaryResponse> {
  const local = getLocalProgressSummary(moduleName);
  const base = resolveApiBase();
  // In same-origin Node.js / AI Studio mode, prefer per-browser localStorage so each user
  // keeps private, container-restart-proof progress; merge any server-side sessions if pointing to FastAPI.
  if (!base) {
    return local;
  }
  try {
    const qs = moduleName ? `?module=${encodeURIComponent(moduleName)}` : "";
    const remote = await apiFetch<ProgressSummaryResponse>(`/api/progress${qs}`);
    if (remote.recent_sessions.length > 0 || remote.skills.length > 0) {
      return remote;
    }
    return local;
  } catch {
    return local;
  }
}

export async function fetchCompletedSession(sessionId: string): Promise<SubmitSessionResponse> {
  const local = getLocalCompletedSession(sessionId);
  if (local) return local;
  return apiFetch<SubmitSessionResponse>(`/api/sessions/${sessionId}`);
}

export async function resetRecentSessions(
  moduleName?: string
): Promise<{ deleted_count: number; scope: string }> {
  clearLocalSessions(moduleName);
  const qs = moduleName ? `?module=${encodeURIComponent(moduleName)}` : "";
  try {
    return await apiFetch(`/api/sessions${qs}`, { method: "DELETE" });
  } catch {
    return { deleted_count: 0, scope: moduleName || "local_sessions" };
  }
}

export async function resetSkillProfile(
  moduleName?: string
): Promise<{ deleted_count: number; scope: string }> {
  clearLocalSkills(moduleName);
  const qs = moduleName ? `?module=${encodeURIComponent(moduleName)}` : "";
  try {
    return await apiFetch(`/api/skills${qs}`, { method: "DELETE" });
  } catch {
    return { deleted_count: 0, scope: moduleName || "local_skills" };
  }
}

export function fetchStrategyNotes(moduleName?: string): Promise<StrategyNoteItem[]> {
  const qs = moduleName ? `?module=${encodeURIComponent(moduleName)}` : "";
  return apiFetch<StrategyNoteItem[]>(`/api/notes${qs}`);
}

export function testPersonalGeminiKey(apiKey: string, model: string): Promise<TestGeminiKeyResponse> {
  return apiFetch<TestGeminiKeyResponse>("/api/settings/test-gemini", {
    method: "POST",
    body: JSON.stringify({ api_key: apiKey, model }),
  });
}
