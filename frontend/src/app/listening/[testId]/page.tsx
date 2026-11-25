"use client";

import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeft,
  BookOpenCheck,
  CheckCircle2,
  Clock,
  Flag,
  Headphones,
  History,
  Loader2,
  Lock,
  MapPin,
  Pause,
  Play,
  RotateCcw,
  Send,
  Sparkles,
  Square,
  Volume2,
  XCircle,
} from "lucide-react";
import { DistractorDrawer } from "@/components/DistractorDrawer";
import { ListeningMapDiagram } from "@/components/ListeningMapDiagram";
import { QuestionNavigator } from "@/components/QuestionNavigator";
import {
  API_BASE,
  createListeningSession,
  explainListeningDistractor,
  fetchCompletedSession,
  fetchListeningTestDetail,
  submitListeningSession,
  synthesizeListeningPartAudio,
} from "@/lib/api";
import { checkClientWordLimit, formatQuestionTypeLabel } from "@/lib/wordCount";
import type {
  DistractorExplanationResponse,
  ListeningTestDetail,
  PublicQuestionItem,
  QuestionGroup,
  QuestionVerdict,
  SubmitSessionResponse,
} from "@/types/reading";

function formatTimer(totalSec: number): string {
  const safe = Math.max(0, totalSec);
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function ListeningExamWorkspace() {
  const params = useParams<{ testId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const testId = params.testId;
  const partParam = searchParams.get("part");
  const reviewSessionId = searchParams.get("session");
  const drillPartIndex = partParam ? Number(partParam) : null;
  const isPartDrill = drillPartIndex !== null && [1, 2, 3, 4].includes(drillPartIndex);

  const [testDetail, setTestDetail] = useState<ListeningTestDetail | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(reviewSessionId);
  const [activePartIndex, setActivePartIndex] = useState<number>(drillPartIndex || 1);
  const [activeQuestionId, setActiveQuestionId] = useState<string | null>(null);

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [flagged, setFlagged] = useState<Record<string, boolean>>({});
  const [scratchNotes, setScratchNotes] = useState<string>("");

  const [remainingSec, setRemainingSec] = useState<number>(isPartDrill ? 8 * 60 : 30 * 60);
  const startTimeRef = useRef<number>(Date.now());

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SubmitSessionResponse | null>(null);

  // Audio playback state (Studio WAV or zero-cost Browser Multi-Voice Speech)
  const [examLockMode, setExamLockMode] = useState<boolean>(false);
  const [playedParts, setPlayedParts] = useState<Record<number, boolean>>({});
  const [playbackRate, setPlaybackRate] = useState<number>(1.0);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [activeTurnIdx, setActiveTurnIdx] = useState<number>(-1);
  const [synthesizing, setSynthesizing] = useState<boolean>(false);
  const [synthMessage, setSynthMessage] = useState<string | null>(null);
  const speakingCancelRef = useRef<boolean>(false);
  const audioElRef = useRef<HTMLAudioElement | null>(null);

  // Post-submission evidence locator & Distractor drawer
  const [highlightedTranscriptId, setHighlightedTranscriptId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerVerdict, setDrawerVerdict] = useState<QuestionVerdict | null>(null);
  const [drawerData, setDrawerData] = useState<DistractorExplanationResponse | null>(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [drawerError, setDrawerError] = useState<string | null>(null);

  const stopSpeech = useCallback(() => {
    speakingCancelRef.current = true;
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (audioElRef.current) {
      audioElRef.current.pause();
    }
    setIsSpeaking(false);
    setActiveTurnIdx(-1);
  }, []);

  useEffect(() => {
    return () => {
      stopSpeech();
    };
  }, [stopSpeech]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setResult(null);
    setAnswers({});

    if (reviewSessionId) {
      Promise.all([
        fetchListeningTestDetail(testId, isPartDrill ? drillPartIndex : null),
        fetchCompletedSession(reviewSessionId),
      ])
        .then(([detail, pastResult]) => {
          if (!active) return;
          setTestDetail(detail);
          setSessionId(pastResult.session_id);
          setResult(pastResult);
          setActivePartIndex(detail.parts[0]?.index ?? 1);
          const restored: Record<string, string> = {};
          for (const v of pastResult.verdicts) {
            restored[v.item_id] = v.user_answer;
          }
          setAnswers(restored);
        })
        .catch((err: unknown) => {
          if (!active) return;
          setError(err instanceof Error ? err.message : "Unable to load past Listening review.");
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    } else {
      Promise.all([
        fetchListeningTestDetail(testId, isPartDrill ? drillPartIndex : null),
        createListeningSession({
          test_id: testId,
          mode: isPartDrill ? "drill" : "section_mock",
          passage_index: isPartDrill ? drillPartIndex : null,
        }),
      ])
        .then(([detail, session]) => {
          if (!active) return;
          setTestDetail(detail);
          setSessionId(session.session_id);
          setActivePartIndex(detail.parts[0]?.index ?? 1);
          setRemainingSec(session.duration_minutes * 60);
          startTimeRef.current = Date.now();
        })
        .catch((err: unknown) => {
          if (!active) return;
          setError(err instanceof Error ? err.message : "Unable to start Listening session.");
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }

    return () => {
      active = false;
    };
  }, [testId, isPartDrill, drillPartIndex, reviewSessionId]);

  useEffect(() => {
    if (loading || result) return;
    const id = window.setInterval(() => {
      setRemainingSec((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => window.clearInterval(id);
  }, [loading, result]);

  const currentPart = useMemo(
    () => testDetail?.parts.find((p) => p.index === activePartIndex) ?? testDetail?.parts[0],
    [testDetail, activePartIndex]
  );

  const currentPartQuestions = useMemo(
    () => testDetail?.questions.filter((q) => q.passage_index === currentPart?.index) ?? [],
    [testDetail, currentPart]
  );

  const verdictMap = useMemo(() => {
    const map: Record<string, QuestionVerdict> = {};
    if (result) {
      for (const v of result.verdicts) {
        map[v.item_id] = v;
      }
    }
    return map;
  }, [result]);

  const answeredCount = useMemo(
    () => (testDetail?.questions ?? []).filter((q) => Boolean((answers[q.id] || "").trim())).length,
    [testDetail, answers]
  );

  const assignedMapLabels = useMemo(() => {
    const map: Record<string, string> = {};
    if (!currentPart?.map_data) return map;
    for (const q of currentPartQuestions) {
      if (q.question_type === "map_plan_diagram") {
        const chosen = (answers[q.id] || "").trim().toUpperCase();
        if (chosen) {
          map[chosen] = `Q${q.question_number}`;
        }
      }
    }
    return map;
  }, [currentPart, currentPartQuestions, answers]);

  const handlePlayBrowserSpeech = () => {
    if (!currentPart) return;
    if (examLockMode && playedParts[currentPart.index] && !result) return;
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setSynthMessage("Browser speech synthesis is unavailable in this browser.");
      return;
    }

    stopSpeech();
    speakingCancelRef.current = false;
    setIsSpeaking(true);
    setPlayedParts((prev) => ({ ...prev, [currentPart.index]: true }));

    const voices = window.speechSynthesis.getVoices().filter((v) => v.lang.startsWith("en"));
    const speakerNames = currentPart.speakers.map((s) => s.speaker);

    const speakTurn = (idx: number) => {
      if (speakingCancelRef.current || idx >= currentPart.transcript.length) {
        setIsSpeaking(false);
        setActiveTurnIdx(-1);
        return;
      }
      const turn = currentPart.transcript[idx];
      setActiveTurnIdx(idx);
      const utter = new SpeechSynthesisUtterance(turn.text);
      utter.rate = playbackRate;
      const spIdx = Math.max(0, speakerNames.indexOf(turn.speaker));
      if (voices.length > 0) {
        utter.voice = voices[spIdx % voices.length];
      }
      utter.pitch = spIdx % 2 === 0 ? 1.0 : 0.92;
      utter.onend = () => {
        if (!speakingCancelRef.current) {
          window.setTimeout(() => speakTurn(idx + 1), 220);
        }
      };
      utter.onerror = () => {
        setIsSpeaking(false);
        setActiveTurnIdx(-1);
      };
      window.speechSynthesis.speak(utter);
    };

    speakTurn(0);
  };

  const handleSynthesizeStudioAudio = async () => {
    if (!currentPart || synthesizing) return;
    setSynthesizing(true);
    setSynthMessage(null);
    try {
      const res = await synthesizeListeningPartAudio(testId, currentPart.index);
      setTestDetail((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          parts: prev.parts.map((p) =>
            p.index === currentPart.index ? { ...p, audio_url: res.audio_url } : p
          ),
        };
      });
      setSynthMessage(`Studio WAV ready (${Math.round(res.bytes / 1024)} KB via ${res.model}).`);
    } catch (err: unknown) {
      setSynthMessage(
        err instanceof Error ? err.message : "Could not synthesize audio; Browser Multi-Voice still works!"
      );
    } finally {
      setSynthesizing(false);
    }
  };

  const handleJumpToQuestion = (q: PublicQuestionItem) => {
    if (q.passage_index !== activePartIndex) {
      stopSpeech();
      setActivePartIndex(q.passage_index);
    }
    setActiveQuestionId(q.id);
    window.setTimeout(() => {
      document.getElementById(`question-card-${q.question_number}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 60);
  };

  const handleSubmit = async () => {
    if (!sessionId || submitting || result) return;
    stopSpeech();
    setSubmitting(true);
    setError(null);
    try {
      const elapsedSec = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 1000));
      const res = await submitListeningSession(sessionId, answers, elapsedSec, {
        test_id: testId,
        mode: isPartDrill ? "drill" : "section_mock",
        passage_index: isPartDrill ? drillPartIndex : null,
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit Listening answers.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleLocateEvidence = (verdict: QuestionVerdict) => {
    const tid = verdict.evidence_span?.transcript_id;
    if (!tid) return;
    setActivePartIndex(verdict.passage_index);
    setHighlightedTranscriptId(tid);
    window.setTimeout(() => {
      document.getElementById(`transcript-turn-${tid}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 80);
  };

  const handleExplain = async (verdict: QuestionVerdict) => {
    setDrawerVerdict(verdict);
    setDrawerOpen(true);
    setDrawerLoading(true);
    setDrawerError(null);
    setDrawerData(null);
    try {
      const data = await explainListeningDistractor({
        item_id: verdict.item_id,
        user_answer: verdict.user_answer,
        failure_reason: verdict.failure_reason,
      });
      setDrawerData(data);
    } catch (err: unknown) {
      setDrawerError(err instanceof Error ? err.message : "Could not load explanation.");
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleRetake = () => {
    const cleanUrl = isPartDrill ? `/listening/${testId}?part=${drillPartIndex}` : `/listening/${testId}`;
    if (reviewSessionId) {
      router.push(cleanUrl);
    } else {
      window.location.href = cleanUrl;
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600">
        <Loader2 className="mr-2 h-5 w-5 animate-spin text-indigo-600" />
        Loading IELTS Listening workspace…
      </div>
    );
  }

  if (error || !testDetail || !currentPart) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-6 text-center">
        <p className="max-w-md rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
          {error || "Listening test not found."}
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const questionsByNum = new Map(currentPartQuestions.map((q) => [q.question_number, q]));
  const partLocked = examLockMode && Boolean(playedParts[currentPart.index]) && !result;

  const renderInput = (q: PublicQuestionItem, group: QuestionGroup) => {
    const val = answers[q.id] || "";
    const disabled = Boolean(result);

    if (q.question_type === "mcq_single") {
      const options = q.prompt_payload.options || [];
      return (
        <div className="mt-2.5 space-y-2">
          {options.map((opt) => {
            const active = val === opt.id;
            return (
              <label
                key={opt.id}
                className={`flex cursor-pointer items-start gap-2.5 rounded-lg border p-2.5 text-sm transition ${
                  active
                    ? "border-indigo-600 bg-indigo-50/60 text-slate-900"
                    : "border-slate-200 bg-white text-slate-700 hover:border-slate-300"
                }`}
              >
                <input
                  type="radio"
                  name={q.id}
                  value={opt.id}
                  checked={active}
                  disabled={disabled}
                  onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt.id }))}
                  className="mt-1 accent-indigo-600"
                />
                <span>
                  <strong className="mr-1.5 text-slate-900">{opt.id}.</strong>
                  {opt.text}
                </span>
              </label>
            );
          })}
        </div>
      );
    }

    if (q.question_type === "map_plan_diagram" || q.question_type === "matching") {
      const options = group.options || [];
      return (
        <div className="mt-2.5">
          <select
            aria-label={`Answer for question ${q.question_number}`}
            value={val}
            disabled={disabled}
            onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-indigo-600 focus:outline-none disabled:bg-slate-100"
          >
            <option value="">Select letter…</option>
            {options.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.id} — {opt.text}
              </option>
            ))}
          </select>
        </div>
      );
    }

    const wlRule = q.prompt_payload.word_limit || group.word_limit;
    const wlStatus = checkClientWordLimit(val, wlRule);
    return (
      <div className="mt-2.5">
        <input
          type="text"
          aria-label={`Answer for question ${q.question_number}`}
          value={val}
          disabled={disabled}
          placeholder="Type what you hear…"
          onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
          className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:bg-slate-100 ${
            !wlStatus.ok
              ? "border-red-500 bg-red-50/40 focus:border-red-600"
              : "border-slate-300 bg-white focus:border-indigo-600"
          }`}
        />
        <div className="mt-1 flex items-center justify-between text-xs">
          <span className={wlStatus.ok ? "text-slate-500" : "font-semibold text-red-600"}>
            {!wlStatus.ok ? (
              <span className="inline-flex items-center gap-1">
                <AlertTriangle className="h-3.5 w-3.5" />
                {wlStatus.message}
              </span>
            ) : val.trim() ? (
              `Count: ${wlStatus.words} word${wlStatus.words === 1 ? "" : "s"}${
                wlStatus.numbers > 0 ? `, ${wlStatus.numbers} number` : ""
              }`
            ) : (
              "Watch for speaker self-corrections & exact plurals."
            )}
          </span>
          {wlRule?.label && (
            <span className="font-mono text-[11px] font-semibold text-amber-700">
              {wlRule.label}
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-100">
      {/* Top Toolbar */}
      <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-slate-900 px-4 py-2.5 text-white">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            onClick={stopSpeech}
            className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2.5 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Exit
          </Link>
          <div className="hidden sm:block">
            <p className="flex items-center gap-1.5 text-xs font-bold tracking-wide text-white">
              <Headphones className="h-3.5 w-3.5 text-indigo-400" />
              {testDetail.title}
            </p>
            <p className="text-[11px] text-slate-400">
              {reviewSessionId
                ? "Past Listening Session Summary"
                : isPartDrill
                ? `Part ${drillPartIndex} Drill`
                : "Post-2020 4-Part Mock (No Part 1 Spoken Example)"}
            </p>
          </div>
        </div>

        {/* Part Switcher */}
        {testDetail.parts.length > 1 && (
          <div className="flex items-center gap-1 rounded-lg bg-slate-800 p-1">
            {testDetail.parts.map((p) => (
              <button
                key={p.index}
                type="button"
                onClick={() => {
                  stopSpeech();
                  setActivePartIndex(p.index);
                }}
                className={`rounded-md px-3 py-1 text-xs font-semibold transition ${
                  p.index === currentPart.index
                    ? "bg-indigo-600 text-white"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                Part {p.index}
              </button>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2.5">
          {!reviewSessionId && !result && (
            <button
              type="button"
              onClick={() => setExamLockMode((v) => !v)}
              className={`hidden items-center gap-1 rounded-md border px-2.5 py-1 text-xs font-semibold sm:inline-flex ${
                examLockMode
                  ? "border-amber-400 bg-amber-500/20 text-amber-200"
                  : "border-slate-700 bg-slate-800 text-slate-300 hover:text-white"
              }`}
              title="Real IELTS plays each recording once only"
            >
              <Lock className="h-3 w-3" />
              {examLockMode ? "Exam Mode (1 Play)" : "Practice Mode (Replay OK)"}
            </button>
          )}

          {!reviewSessionId ? (
            <div className="flex items-center gap-1.5 rounded-lg bg-slate-800 px-3 py-1.5 font-mono text-sm font-bold text-amber-300">
              <Clock className="h-4 w-4" />
              {formatTimer(remainingSec)}
            </div>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-lg bg-slate-800 px-3 py-1.5 text-xs font-semibold text-sky-300">
              <History className="h-3.5 w-3.5" />
              Saved Summary
            </span>
          )}

          <span className="hidden text-xs font-medium text-slate-300 md:inline">
            {answeredCount}/{testDetail.questions.length} answered
          </span>

          {!result ? (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-emerald-500 disabled:opacity-60"
            >
              {submitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
              Submit Test
            </button>
          ) : (
            <button
              type="button"
              onClick={handleRetake}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-indigo-500"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Retake
            </button>
          )}
        </div>
      </header>

      {/* Synced Audio Controller Bar */}
      <div className="shrink-0 border-b border-slate-200 bg-white px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            {currentPart.audio_url ? (
              <audio
                ref={audioElRef}
                controls
                src={
                  currentPart.audio_url.startsWith("data:") ||
                  currentPart.audio_url.startsWith("http")
                    ? currentPart.audio_url
                    : `${API_BASE}${currentPart.audio_url}`
                }
                className="h-9 max-w-md"
              />
            ) : (
              <div className="flex items-center gap-2">
                {!isSpeaking ? (
                  <button
                    type="button"
                    disabled={partLocked}
                    onClick={handlePlayBrowserSpeech}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-700 px-3.5 py-2 text-xs font-bold text-white shadow-xs hover:bg-indigo-800 disabled:bg-slate-400"
                  >
                    <Play className="h-3.5 w-3.5" />
                    {partLocked ? "Audio Locked (Exam Mode)" : `Play Part ${currentPart.index} Audio`}
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={stopSpeech}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-rose-600 px-3.5 py-2 text-xs font-bold text-white hover:bg-rose-700"
                  >
                    <Square className="h-3.5 w-3.5" />
                    Stop Audio
                  </button>
                )}

                <div className="flex items-center rounded-md border border-slate-200 bg-slate-50 text-xs">
                  {[0.85, 1.0, 1.15].map((rate) => (
                    <button
                      key={rate}
                      type="button"
                      onClick={() => setPlaybackRate(rate)}
                      className={`px-2 py-1 font-semibold ${
                        playbackRate === rate
                          ? "bg-indigo-600 text-white"
                          : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="text-xs text-slate-600">
              {isSpeaking && activeTurnIdx >= 0 ? (
                <span className="inline-flex items-center gap-1.5 font-semibold text-indigo-700">
                  <Volume2 className="h-4 w-4 animate-pulse" />
                  Speaking: {currentPart.transcript[activeTurnIdx]?.speaker} (Line{" "}
                  {activeTurnIdx + 1}/{currentPart.transcript.length})
                </span>
              ) : (
                <span>
                  <strong>{currentPart.title}</strong> · Multi-Voice Playback Ready
                </span>
              )}
            </div>
          </div>

          {!currentPart.audio_url && (
            <button
              type="button"
              disabled={synthesizing}
              onClick={handleSynthesizeStudioAudio}
              className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-800 hover:bg-indigo-100 disabled:opacity-60"
            >
              {synthesizing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Sparkles className="h-3.5 w-3.5" />
              )}
              {synthesizing ? "Synthesizing Studio WAV…" : "Generate Studio WAV (Gemini TTS)"}
            </button>
          )}
        </div>
        {synthMessage && <p className="mt-1.5 text-xs text-indigo-700">{synthMessage}</p>}
      </div>

      {/* Post-Submission Score Banner */}
      {result && (
        <div className="shrink-0 border-b border-emerald-200 bg-emerald-50 px-5 py-3">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-6 w-6 text-emerald-700" />
              <div>
                <p className="text-xs font-bold tracking-wide text-emerald-800 uppercase">
                  Deterministic Listening Score Report
                </p>
                <p className="text-sm font-semibold text-slate-900">
                  Raw Score: <strong>{result.raw_score} / {result.total_questions}</strong> ·
                  Listening Band:{" "}
                  <span className="rounded bg-emerald-700 px-2 py-0.5 text-white">
                    {result.band_score.toFixed(1)}
                  </span>
                  {result.is_prorated_band && (
                    <span className="ml-2 text-xs font-normal text-slate-600">
                      (prorated on official Listening 0–40 curve)
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {result.by_question_type.map((b) => (
                <span
                  key={b.question_type}
                  className="rounded-full border border-emerald-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-700"
                >
                  {formatQuestionTypeLabel(b.question_type)}:{" "}
                  <strong>
                    {b.correct}/{b.total}
                  </strong>
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Split-Pane Body: Left (Map / Context / Post-Submit Transcript), Right (Questions) */}
      <div className="grid min-h-0 flex-1 grid-cols-1 divide-y divide-slate-200 lg:grid-cols-2 lg:divide-x lg:divide-y-0">
        {/* Left Pane */}
        <div className="h-full space-y-5 overflow-y-auto bg-white px-6 py-6">
          <div className="border-b border-slate-200 pb-4">
            <span className="rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-bold tracking-wide text-indigo-800 uppercase">
              Listening Part {currentPart.index}
            </span>
            <h1 className="mt-2 text-xl font-bold text-slate-900">{currentPart.title}</h1>
            <p className="mt-1 text-sm text-slate-600">{currentPart.context}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {currentPart.speakers.map((sp) => (
                <span
                  key={sp.speaker}
                  className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700"
                >
                  <strong>{sp.speaker}</strong> · {sp.role} ({sp.accent})
                </span>
              ))}
            </div>
          </div>

          {currentPart.map_data && (
            <ListeningMapDiagram
              mapData={currentPart.map_data}
              assignedLabels={assignedMapLabels}
            />
          )}

          {!result ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="mb-2 flex items-center justify-between">
                <h3 className="text-xs font-bold tracking-wide text-slate-700 uppercase">
                  Scratchpad Notes (Transcript Locked Until Submission)
                </h3>
                <Pause className="h-3.5 w-3.5 text-slate-400" />
              </div>
              <textarea
                rows={7}
                value={scratchNotes}
                onChange={(e) => setScratchNotes(e.target.value)}
                placeholder="Jot down dates, prices, spelled postcodes, or self-corrections while listening…"
                className="w-full rounded-lg border border-slate-200 bg-white p-3 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          ) : (
            <div className="space-y-3 pb-10">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold tracking-wide text-slate-900 uppercase">
                  Verified Audio Transcript (Part {currentPart.index})
                </h2>
                <span className="text-xs text-slate-500">
                  Click &ldquo;Locate Evidence&rdquo; on any question to jump here
                </span>
              </div>
              {currentPart.transcript.map((turn) => {
                const isTarget = highlightedTranscriptId === turn.id;
                return (
                  <div
                    key={turn.id}
                    id={`transcript-turn-${turn.id}`}
                    className={`rounded-xl border p-3.5 text-sm leading-relaxed transition ${
                      isTarget
                        ? "evidence-flash border-sky-400 bg-sky-50 text-slate-950"
                        : "border-slate-200 bg-slate-50/70 text-slate-800"
                    }`}
                  >
                    <span className="mr-2 inline-block rounded bg-slate-900 px-2 py-0.5 text-[11px] font-bold text-white">
                      {turn.speaker}
                    </span>
                    {turn.text}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Pane: Questions */}
        <div className="h-full overflow-y-auto bg-slate-50 px-5 py-6 lg:px-7">
          <div className="space-y-6 pb-16">
            {currentPart.question_groups.map((group) => {
              const groupQs = group.question_numbers
                .map((num) => questionsByNum.get(num))
                .filter((item): item is PublicQuestionItem => Boolean(item));

              return (
                <section
                  key={group.id}
                  className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs"
                >
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                    <div>
                      <h2 className="text-base font-bold text-slate-900">{group.title}</h2>
                      <p className="text-xs font-medium text-indigo-700">
                        {formatQuestionTypeLabel(group.question_type)}
                      </p>
                    </div>
                    {group.word_limit?.label && (
                      <span className="rounded-md border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-bold text-amber-900">
                        {group.word_limit.label}
                      </span>
                    )}
                  </div>

                  <p className="mb-4 text-sm text-slate-600">{group.instructions}</p>

                  {group.note_heading && (
                    <div className="mb-4 rounded-lg bg-slate-100 px-3.5 py-2 text-xs font-bold tracking-wide text-slate-800 uppercase">
                      {group.note_heading}
                    </div>
                  )}

                  {group.options && group.options.length > 0 && group.question_type === "matching" && (
                    <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50 p-3.5">
                      <p className="mb-2 text-xs font-bold text-slate-500 uppercase">
                        Options Box
                      </p>
                      <ul className="space-y-1 text-sm text-slate-700">
                        {group.options.map((opt) => (
                          <li key={opt.id} className="flex gap-2">
                            <strong className="w-5 text-slate-900">{opt.id}</strong>
                            <span>{opt.text}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="space-y-4">
                    {groupQs.map((q) => {
                      const verdict = verdictMap[q.id];
                      const isFlagged = Boolean(flagged[q.id]);
                      const isActive = activeQuestionId === q.id;
                      return (
                        <div
                          key={q.id}
                          id={`question-card-${q.question_number}`}
                          className={`rounded-xl border p-4 transition ${
                            verdict
                              ? verdict.is_correct
                                ? "border-emerald-200 bg-emerald-50/40"
                                : "border-rose-200 bg-rose-50/40"
                              : isActive
                              ? "border-indigo-400 bg-indigo-50/25 ring-1 ring-indigo-200"
                              : "border-slate-200 bg-white"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-2.5">
                              <span
                                className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                                  verdict
                                    ? verdict.is_correct
                                      ? "bg-emerald-600 text-white"
                                      : "bg-rose-600 text-white"
                                    : "bg-slate-900 text-white"
                                }`}
                              >
                                {q.question_number}
                              </span>
                              <p className="text-sm font-medium leading-relaxed text-slate-900">
                                {q.prompt_payload.prompt}
                              </p>
                            </div>
                            {!result && (
                              <button
                                type="button"
                                onClick={() => setFlagged((prev) => ({ ...prev, [q.id]: !prev[q.id] }))}
                                className={`shrink-0 rounded-md p-1.5 ${
                                  isFlagged ? "bg-amber-100 text-amber-700" : "text-slate-400 hover:bg-slate-100"
                                }`}
                              >
                                <Flag className="h-3.5 w-3.5" />
                              </button>
                            )}
                          </div>

                          {renderInput(q, group)}

                          {verdict && (
                            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-slate-200/80 pt-3 text-xs">
                              <div className="flex flex-wrap items-center gap-2">
                                {verdict.is_correct ? (
                                  <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
                                    <CheckCircle2 className="h-4 w-4" />
                                    Correct
                                  </span>
                                ) : (
                                  <>
                                    <span className="inline-flex items-center gap-1 font-semibold text-rose-700">
                                      <XCircle className="h-4 w-4" />
                                      {verdict.failure_reason === "word_limit_exceeded"
                                        ? "Word limit exceeded"
                                        : verdict.failure_reason === "blank"
                                        ? "Unanswered"
                                        : "Incorrect"}
                                    </span>
                                    <span className="rounded bg-white px-2 py-0.5 font-medium text-slate-700 ring-1 ring-slate-200">
                                      Accepted: <strong>{verdict.accepted_answers.join(" / ")}</strong>
                                    </span>
                                  </>
                                )}
                              </div>

                              <div className="flex items-center gap-2">
                                {verdict.evidence_span?.transcript_id && (
                                  <button
                                    type="button"
                                    onClick={() => handleLocateEvidence(verdict)}
                                    className="inline-flex items-center gap-1 rounded-md border border-sky-200 bg-sky-50 px-2.5 py-1 font-semibold text-sky-700 hover:bg-sky-100"
                                  >
                                    <MapPin className="h-3.5 w-3.5" />
                                    Transcript
                                  </button>
                                )}
                                <button
                                  type="button"
                                  onClick={() => handleExplain(verdict)}
                                  className="inline-flex items-center gap-1 rounded-md border border-indigo-200 bg-indigo-50 px-2.5 py-1 font-semibold text-indigo-700 hover:bg-indigo-100"
                                >
                                  {verdict.is_correct ? (
                                    <BookOpenCheck className="h-3.5 w-3.5" />
                                  ) : (
                                    <Sparkles className="h-3.5 w-3.5" />
                                  )}
                                  {verdict.is_correct ? "Review" : "Explain Distractor"}
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>
        </div>
      </div>

      <QuestionNavigator
        questions={testDetail.questions}
        answers={answers}
        flagged={flagged}
        verdicts={verdictMap}
        activePassageIndex={currentPart.index}
        onJumpToQuestion={handleJumpToQuestion}
      />

      <DistractorDrawer
        open={drawerOpen}
        loading={drawerLoading}
        verdict={drawerVerdict}
        data={drawerData}
        error={drawerError}
        onClose={() => setDrawerOpen(false)}
        onLocateEvidence={handleLocateEvidence}
      />
    </div>
  );
}

export default function ListeningExamPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600">
          <Loader2 className="mr-2 h-5 w-5 animate-spin text-indigo-600" />
          Loading IELTS Listening workspace…
        </div>
      }
    >
      <ListeningExamWorkspace />
    </Suspense>
  );
}
