"use client";

import React, { Suspense, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  History,
  Loader2,
  Pause,
  Play,
  RotateCcw,
  Send,
} from "lucide-react";
import { DistractorDrawer } from "@/components/DistractorDrawer";
import { PassagePane } from "@/components/PassagePane";
import { QuestionNavigator } from "@/components/QuestionNavigator";
import { QuestionPane } from "@/components/QuestionPane";
import {
  createReadingSession,
  explainReadingDistractor,
  fetchCompletedSession,
  fetchReadingTestDetail,
  submitReadingSession,
} from "@/lib/api";
import { formatQuestionTypeLabel } from "@/lib/wordCount";
import type {
  DistractorExplanationResponse,
  PublicQuestionItem,
  QuestionVerdict,
  ReadingTestDetail,
  SubmitSessionResponse,
  TextHighlight,
} from "@/types/reading";

function formatTimer(totalSec: number): string {
  const safe = Math.max(0, totalSec);
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function ReadingExamWorkspace() {
  const params = useParams<{ testId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const testId = params.testId;
  const passageParam = searchParams.get("passage");
  const reviewSessionId = searchParams.get("session");
  const drillPassageIndex = passageParam ? Number(passageParam) : null;
  const isLegacyPassageDrill = drillPassageIndex !== null && [1, 2, 3].includes(drillPassageIndex);

  const [testDetail, setTestDetail] = useState<ReadingTestDetail | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(reviewSessionId);
  const [activePassageIndex, setActivePassageIndex] = useState<number>(drillPassageIndex || 1);
  const [activeQuestionId, setActiveQuestionId] = useState<string | null>(null);
  const [fontSize, setFontSize] = useState<"sm" | "base" | "lg">("base");

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [flagged, setFlagged] = useState<Record<string, boolean>>({});
  const [highlights, setHighlights] = useState<Record<string, TextHighlight[]>>({});

  const [remainingSec, setRemainingSec] = useState<number>(20 * 60);
  const [paused, setPaused] = useState(false);
  const startTimeRef = useRef<number>(Date.now());

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SubmitSessionResponse | null>(null);

  const [activeEvidence, setActiveEvidence] = useState<{
    passageIndex: number;
    paragraphId: string;
    quote: string;
    questionNumber: number;
  } | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerVerdict, setDrawerVerdict] = useState<QuestionVerdict | null>(null);
  const [drawerData, setDrawerData] = useState<DistractorExplanationResponse | null>(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [drawerError, setDrawerError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    setResult(null);
    setAnswers({});

    if (reviewSessionId) {
      // Load past completed session summary & verdicts directly into Review Mode
      Promise.all([
        fetchReadingTestDetail(testId, isLegacyPassageDrill ? drillPassageIndex : null),
        fetchCompletedSession(reviewSessionId),
      ])
        .then(([detail, pastResult]) => {
          if (!active) return;
          setTestDetail(detail);
          setSessionId(pastResult.session_id);
          setResult(pastResult);
          setActivePassageIndex(detail.passages[0]?.index ?? 1);
          const restoredAnswers: Record<string, string> = {};
          for (const v of pastResult.verdicts) {
            restoredAnswers[v.item_id] = v.user_answer;
          }
          setAnswers(restoredAnswers);
        })
        .catch((err: unknown) => {
          if (!active) return;
          setError(err instanceof Error ? err.message : "Unable to load past session review.");
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    } else {
      Promise.all([
        fetchReadingTestDetail(testId, isLegacyPassageDrill ? drillPassageIndex : null),
        createReadingSession({
          test_id: testId,
          mode: isLegacyPassageDrill ? "drill" : "section_mock",
          passage_index: isLegacyPassageDrill ? drillPassageIndex : null,
        }),
      ])
        .then(([detail, session]) => {
          if (!active) return;
          setTestDetail(detail);
          setSessionId(session.session_id);
          setActivePassageIndex(detail.passages[0]?.index ?? 1);
          setRemainingSec(session.duration_minutes * 60);
          startTimeRef.current = Date.now();
        })
        .catch((err: unknown) => {
          if (!active) return;
          setError(err instanceof Error ? err.message : "Unable to start reading session.");
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }

    return () => {
      active = false;
    };
  }, [testId, isLegacyPassageDrill, drillPassageIndex, reviewSessionId]);

  useEffect(() => {
    if (loading || paused || result) return;
    const id = window.setInterval(() => {
      setRemainingSec((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => window.clearInterval(id);
  }, [loading, paused, result]);

  const verdictMap = useMemo(() => {
    const map: Record<string, QuestionVerdict> = {};
    if (result) {
      for (const v of result.verdicts) {
        map[v.item_id] = v;
      }
    }
    return map;
  }, [result]);

  const currentPassage = useMemo(
    () => testDetail?.passages.find((p) => p.index === activePassageIndex) ?? testDetail?.passages[0],
    [testDetail, activePassageIndex]
  );

  const currentPassageQuestions = useMemo(
    () => testDetail?.questions.filter((q) => q.passage_index === currentPassage?.index) ?? [],
    [testDetail, currentPassage]
  );

  const answeredCount = useMemo(
    () => (testDetail?.questions ?? []).filter((q) => Boolean((answers[q.id] || "").trim())).length,
    [testDetail, answers]
  );

  const isDrillMode = Boolean(isLegacyPassageDrill || testDetail?.is_drill_bank);

  const handleAddHighlight = (paraKey: string, hl: TextHighlight) => {
    setHighlights((prev) => {
      const existing = prev[paraKey] || [];
      const nonOverlapping = existing.filter((item) => item.end <= hl.start || item.start >= hl.end);
      return {
        ...prev,
        [paraKey]: [...nonOverlapping, hl].sort((a, b) => a.start - b.start),
      };
    });
  };

  const handleClearParagraphHighlights = (paraKey: string) => {
    setHighlights((prev) => ({ ...prev, [paraKey]: [] }));
  };

  const handleJumpToQuestion = (q: PublicQuestionItem) => {
    setActivePassageIndex(q.passage_index);
    setActiveQuestionId(q.id);
    window.setTimeout(() => {
      const el = document.getElementById(`question-card-${q.question_number}`);
      el?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 60);
  };

  const handleSubmit = async () => {
    if (!sessionId || submitting || result) return;
    setSubmitting(true);
    setError(null);
    try {
      const elapsedSec = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 1000));
      const res = await submitReadingSession(sessionId, answers, elapsedSec, {
        test_id: testId,
        mode: isDrillMode ? "drill" : "section_mock",
        passage_index: isLegacyPassageDrill ? drillPassageIndex : null,
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit answers.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleLocateEvidence = (verdict: QuestionVerdict) => {
    if (!verdict.evidence_span?.paragraph_id || !verdict.evidence_span?.quote) return;
    setActivePassageIndex(verdict.passage_index);
    setActiveEvidence({
      passageIndex: verdict.passage_index,
      paragraphId: verdict.evidence_span.paragraph_id,
      quote: verdict.evidence_span.quote,
      questionNumber: verdict.question_number,
    });
  };

  const handleExplain = async (verdict: QuestionVerdict) => {
    setDrawerVerdict(verdict);
    setDrawerOpen(true);
    setDrawerLoading(true);
    setDrawerError(null);
    setDrawerData(null);

    try {
      const data = await explainReadingDistractor({
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
    const cleanUrl = isLegacyPassageDrill
      ? `/reading/${testId}?passage=${drillPassageIndex}`
      : `/reading/${testId}`;
    if (reviewSessionId) {
      router.push(cleanUrl);
    } else {
      window.location.href = cleanUrl;
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600">
        <Loader2 className="mr-2 h-5 w-5 animate-spin text-blue-600" />
        Loading Academic Reading workspace…
      </div>
    );
  }

  if (error || !testDetail || !currentPassage) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-6 text-center">
        <p className="max-w-md rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
          {error || "Test not found."}
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

  const totalQ = testDetail.questions.length;
  const lowTime = remainingSec <= 300 && !result;

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-slate-100">
      {/* Top Exam Toolbar */}
      <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-slate-900 px-4 py-2.5 text-white">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2.5 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Exit
          </Link>
          <div className="hidden sm:block">
            <p className="text-xs font-bold tracking-wide text-white">{testDetail.title}</p>
            <p className="text-[11px] text-slate-400">
              {reviewSessionId
                ? "Past Session Result & Summary"
                : isDrillMode
                ? testDetail.drill_slot
                  ? `Passage ${testDetail.drill_slot} Drill`
                  : `Passage ${drillPassageIndex} Drill`
                : "Full 3-Passage Mock"}
            </p>
          </div>
        </div>

        {/* Passage Switcher Tabs */}
        {testDetail.passages.length > 1 && (
          <div className="flex items-center gap-1 rounded-lg bg-slate-800 p-1">
            {testDetail.passages.map((p) => {
              const active = p.index === currentPassage.index;
              return (
                <button
                  key={p.index}
                  type="button"
                  onClick={() => setActivePassageIndex(p.index)}
                  className={`rounded-md px-3 py-1 text-xs font-semibold transition ${
                    active ? "bg-blue-600 text-white" : "text-slate-300 hover:text-white"
                  }`}
                >
                  Passage {p.index}
                </button>
              );
            })}
          </div>
        )}

        {/* Timer + Font Size + Submit */}
        <div className="flex items-center gap-2.5">
          <div className="hidden items-center rounded-md border border-slate-700 bg-slate-800 text-xs sm:flex">
            {(["sm", "base", "lg"] as const).map((sz, idx) => (
              <button
                key={sz}
                type="button"
                onClick={() => setFontSize(sz)}
                className={`px-2 py-1 font-semibold ${
                  fontSize === sz ? "bg-slate-700 text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                {idx === 0 ? "A-" : idx === 1 ? "A" : "A+"}
              </button>
            ))}
          </div>

          {!reviewSessionId ? (
            <div
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-mono text-sm font-bold ${
                lowTime ? "bg-rose-600 text-white" : "bg-slate-800 text-amber-300"
              }`}
            >
              <Clock className="h-4 w-4" />
              {formatTimer(remainingSec)}
              {isDrillMode && !result && (
                <button
                  type="button"
                  onClick={() => setPaused((p) => !p)}
                  title={paused ? "Resume timer" : "Pause timer"}
                  className="ml-1 rounded p-0.5 text-slate-300 hover:bg-slate-700 hover:text-white"
                >
                  {paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                </button>
              )}
            </div>
          ) : (
            <span className="inline-flex items-center gap-1.5 rounded-lg bg-slate-800 px-3 py-1.5 text-xs font-semibold text-sky-300">
              <History className="h-3.5 w-3.5" />
              Saved Summary
            </span>
          )}

          <span className="hidden text-xs font-medium text-slate-300 md:inline">
            {answeredCount}/{totalQ} answered
          </span>

          {!result ? (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={submitting}
              className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-xs transition hover:bg-emerald-500 disabled:opacity-60"
            >
              {submitting ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Send className="h-3.5 w-3.5" />
              )}
              Submit Test
            </button>
          ) : (
            <button
              type="button"
              onClick={handleRetake}
              className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-blue-500"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Retake Drill
            </button>
          )}
        </div>
      </header>

      {/* Post-Submission / Past-Session Band Score Banner */}
      {result && (
        <div className="shrink-0 border-b border-emerald-200 bg-emerald-50 px-5 py-3">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-6 w-6 text-emerald-700" />
              <div>
                <p className="text-xs font-bold tracking-wide text-emerald-800 uppercase">
                  {reviewSessionId ? "Past Session Deterministic Score Report" : "Deterministic Score Report"}
                </p>
                <p className="text-sm font-semibold text-slate-900">
                  Raw Score: <strong>{result.raw_score} / {result.total_questions}</strong> ·
                  Academic Reading Band:{" "}
                  <span className="rounded bg-emerald-700 px-2 py-0.5 text-white">
                    {result.band_score.toFixed(1)}
                  </span>
                  {result.is_prorated_band && (
                    <span className="ml-2 text-xs font-normal text-slate-600">
                      (prorated from {result.total_questions}-question drill)
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

      {/* Main Split-Pane Workspace */}
      <div className="grid min-h-0 flex-1 grid-cols-1 divide-y divide-slate-200 lg:grid-cols-2 lg:divide-x lg:divide-y-0">
        <div className="min-h-0 overflow-hidden">
          <PassagePane
            passage={currentPassage}
            fontSize={fontSize}
            highlights={highlights}
            onAddHighlight={handleAddHighlight}
            onClearParagraphHighlights={handleClearParagraphHighlights}
            activeEvidence={activeEvidence}
          />
        </div>
        <div className="min-h-0 overflow-hidden">
          <QuestionPane
            passage={currentPassage}
            questions={currentPassageQuestions}
            answers={answers}
            flagged={flagged}
            verdicts={verdictMap}
            submitted={Boolean(result)}
            activeQuestionId={activeQuestionId}
            onAnswerChange={(id, val) => setAnswers((prev) => ({ ...prev, [id]: val }))}
            onToggleFlag={(id) => setFlagged((prev) => ({ ...prev, [id]: !prev[id] }))}
            onExplain={handleExplain}
            onLocateEvidence={handleLocateEvidence}
          />
        </div>
      </div>

      <QuestionNavigator
        questions={testDetail.questions}
        answers={answers}
        flagged={flagged}
        verdicts={verdictMap}
        activePassageIndex={currentPassage.index}
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

export default function ReadingExamPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-slate-50 text-slate-600">
          <Loader2 className="mr-2 h-5 w-5 animate-spin text-blue-600" />
          Loading Academic Reading workspace…
        </div>
      }
    >
      <ReadingExamWorkspace />
    </Suspense>
  );
}
