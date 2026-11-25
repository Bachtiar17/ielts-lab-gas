"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Award,
  BookMarked,
  BookOpen,
  Clock,
  ExternalLink,
  GraduationCap,
  Headphones,
  KeyRound,
  Layers,
  MapPin,
  RefreshCw,
  RotateCcw,
  Target,
  Volume2,
} from "lucide-react";
import { ApiKeyModal } from "@/components/ApiKeyModal";
import {
  fetchListeningTests,
  fetchRandomReadingDrills,
  fetchReadingTests,
  fetchStrategyNotes,
  fetchUnifiedProgress,
  resetRecentSessions,
  resetSkillProfile,
} from "@/lib/api";
import { loadPersonalGeminiConfig } from "@/lib/geminiSettings";
import { formatQuestionTypeLabel, formatSkillKey } from "@/lib/wordCount";
import type {
  DrillCardItem,
  ListeningTestSummary,
  ProgressSummaryResponse,
  ReadingTestSummary,
  StrategyNoteItem,
} from "@/types/reading";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<"reading" | "listening">("reading");
  const [readingTests, setReadingTests] = useState<ReadingTestSummary[]>([]);
  const [listeningTests, setListeningTests] = useState<ListeningTestSummary[]>([]);
  const [drills, setDrills] = useState<DrillCardItem[]>([]);
  const [bankSize, setBankSize] = useState<number>(30);
  const [shuffling, setShuffling] = useState(false);

  const [progress, setProgress] = useState<ProgressSummaryResponse | null>(null);
  const [notes, setNotes] = useState<StrategyNoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reset confirmation states
  const [confirmResetSessions, setConfirmResetSessions] = useState(false);
  const [confirmResetSkills, setConfirmResetSkills] = useState(false);
  const [resetting, setResetting] = useState(false);

  // Personal Gemini API Key modal state
  const [apiModalOpen, setApiModalOpen] = useState(false);
  const [hasPersonalKey, setHasPersonalKey] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [rt, lt, dr, prog, stNotes] = await Promise.all([
        fetchReadingTests(),
        fetchListeningTests(),
        fetchRandomReadingDrills(),
        fetchUnifiedProgress(),
        fetchStrategyNotes(),
      ]);
      setReadingTests(rt);
      setListeningTests(lt);
      setDrills(dr.drills);
      setBankSize(dr.bank_size);
      setProgress(prog);
      setNotes(stNotes);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to connect to IELTS Lab API.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const cfg = loadPersonalGeminiConfig();
    setHasPersonalKey(Boolean(cfg.apiKey));
    void loadAll();
  }, [loadAll]);

  const handleShuffleDrills = async () => {
    setShuffling(true);
    try {
      const currentIds = drills.map((d) => d.id);
      const res = await fetchRandomReadingDrills(currentIds);
      setDrills(res.drills);
      setBankSize(res.bank_size);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to refresh drills.");
    } finally {
      setShuffling(false);
    }
  };

  const handleResetSessions = async () => {
    setResetting(true);
    try {
      await resetRecentSessions();
      const updated = await fetchUnifiedProgress();
      setProgress(updated);
    } finally {
      setResetting(false);
      setConfirmResetSessions(false);
    }
  };

  const handleResetSkills = async () => {
    setResetting(true);
    try {
      await resetSkillProfile();
      const updated = await fetchUnifiedProgress();
      setProgress(updated);
    } finally {
      setResetting(false);
      setConfirmResetSkills(false);
    }
  };

  const primaryReading = readingTests[0];
  const primaryListening = listeningTests[0];
  const filteredNotes = notes.filter((n) => n.module === activeTab);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Navbar */}
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-3.5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-700 text-white shadow-xs">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-slate-900">IELTS Lab</span>
              <span className="ml-2 rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700">
                Reading + Listening
              </span>
            </div>
          </div>

          <nav className="flex items-center gap-3 text-sm font-medium">
            <Link href="/" className="text-blue-700">
              Workbench
            </Link>
            <Link href="/notes" className="text-slate-600 hover:text-slate-900">
              Strategy Notes ({notes.length})
            </Link>
            <button
              type="button"
              onClick={() => setApiModalOpen(true)}
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition ${
                hasPersonalKey
                  ? "border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                  : "border-indigo-200 bg-indigo-50 text-indigo-800 hover:bg-indigo-100"
              }`}
            >
              <KeyRound className="h-3.5 w-3.5" />
              {hasPersonalKey ? "Personal Gemini Key Active" : "Add Personal Gemini API"}
            </button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        {/* Module Switcher */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="inline-flex rounded-xl border border-slate-200 bg-white p-1 shadow-2xs">
            <button
              type="button"
              onClick={() => setActiveTab("reading")}
              className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                activeTab === "reading"
                  ? "bg-blue-700 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <BookOpen className="h-4 w-4" />
              Academic Reading
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("listening")}
              className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                activeTab === "listening"
                  ? "bg-blue-700 text-white shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Headphones className="h-4 w-4" />
              Listening
              <span className="rounded-full bg-emerald-100 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800">
                NEW
              </span>
            </button>
          </div>

          <p className="text-xs text-slate-500">
            100% deterministic Band 1.0–9.0 grading · Separate Reading & Listening curves
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">
            <strong>Connection error:</strong> {error}. Please refresh or verify the app server is running.
          </div>
        )}

        {loading ? (
          <div className="grid gap-4 md:grid-cols-3">
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                className="h-44 animate-pulse rounded-xl border border-slate-200 bg-white p-5"
              />
            ))}
          </div>
        ) : activeTab === "reading" ? (
          <>
            {/* Reading Hero */}
            <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-2xs">
              <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
                <div className="max-w-2xl">
                  <p className="text-xs font-bold tracking-wider text-blue-700 uppercase">
                    Computer-Delivered IELTS Academic Reading
                  </p>
                  <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                    Academic Reading Practice & Deterministic Band Scoring
                  </h1>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">
                    Split-pane exam simulator with interactive text highlighting, live word-limit
                    checks, official 0–40 raw-to-band scoring, and evidence-backed distractor
                    breakdowns linked to IELTS Advantage strategy notes.
                  </p>
                </div>

                {primaryReading && (
                  <Link
                    href={`/reading/${primaryReading.id}`}
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800"
                  >
                    Start Full 60-Min Mock
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            </section>

            {/* Rotating 30-Passage Single-Passage Drills */}
            <section className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Targeted Single-Passage Drills
                  </h2>
                  <p className="text-xs text-slate-500">
                    Rotates automatically on every refresh from a{" "}
                    <strong className="text-slate-700">{bankSize}-passage original bank</strong>{" "}
                    (Passage 1, 2 & 3 difficulty tiers)
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleShuffleDrills}
                  disabled={shuffling}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-2xs transition hover:border-blue-400 hover:text-blue-700 disabled:opacity-60"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${shuffling ? "animate-spin" : ""}`} />
                  Shuffle 3 New Passages
                </button>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                {drills.map((d) => (
                  <div
                    key={d.id}
                    className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-2xs transition hover:border-blue-300"
                  >
                    <div>
                      <div className="mb-2 flex items-center justify-between">
                        <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-700">
                          Passage {d.drill_slot} Drill
                        </span>
                        <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                          <Clock className="h-3.5 w-3.5" />
                          {d.recommended_minutes} min · {d.question_count} Qs
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-slate-900">{d.title}</h3>
                      <p className="mt-1 text-xs leading-relaxed text-slate-600">{d.subtitle}</p>
                      <p className="mt-2 text-[11px] font-semibold text-blue-700">{d.topic}</p>
                    </div>

                    <Link
                      href={`/reading/${d.id}`}
                      className="mt-4 inline-flex items-center justify-center gap-1.5 rounded-lg border border-blue-200 bg-blue-50/70 px-3.5 py-2 text-xs font-semibold text-blue-800 transition hover:bg-blue-100"
                    >
                      Launch Passage {d.drill_slot} Drill
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                ))}
              </div>
            </section>
          </>
        ) : (
          <>
            {/* Listening Hero */}
            <section className="rounded-2xl border border-slate-200 bg-white p-7 shadow-2xs">
              <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
                <div className="max-w-2xl">
                  <p className="text-xs font-bold tracking-wider text-indigo-700 uppercase">
                    Milestone 2 · Post-2020 IELTS Listening (Parts 1–4)
                  </p>
                  <h1 className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                    Synced Listening Practice, Interactive Maps & Self-Correction Drills
                  </h1>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600">
                    Practice all 4 official Listening parts with Exam Mode (single play) or Practice
                    Mode, interactive SVG floorplan labelling, deterministic date/time/postcode
                    grading, and post-submission highlighted transcript review.
                  </p>
                </div>

                {primaryListening && (
                  <Link
                    href={`/listening/${primaryListening.id}`}
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-indigo-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-800"
                  >
                    <Headphones className="h-4 w-4" />
                    Start Full 30-Min Mock
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            </section>

            {/* 4 Listening Part Drills */}
            {primaryListening && (
              <section className="space-y-4">
                <div>
                  <h2 className="text-lg font-bold text-slate-900">
                    Focused Listening Part Drills (Parts 1–4)
                  </h2>
                  <p className="text-xs text-slate-500">
                    {primaryListening.title} · Plays with studio Gemini TTS audio or zero-cost
                    Browser Multi-Voice Speech out of the box
                  </p>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  {primaryListening.parts.map((part) => (
                    <div
                      key={part.index}
                      className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-2xs transition hover:border-indigo-300"
                    >
                      <div>
                        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                          <span className="rounded-md bg-indigo-50 px-2.5 py-0.5 text-xs font-bold text-indigo-800">
                            Part {part.index} · {part.question_count} Questions
                          </span>
                          <div className="flex items-center gap-1.5 text-[11px] font-semibold">
                            {part.has_map && (
                              <span className="inline-flex items-center gap-1 rounded bg-sky-50 px-2 py-0.5 text-sky-700">
                                <MapPin className="h-3 w-3" />
                                Interactive Map
                              </span>
                            )}
                            <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-slate-600">
                              <Volume2 className="h-3 w-3" />
                              {part.has_audio_file ? "Studio WAV Ready" : "Multi-Voice Audio"}
                            </span>
                          </div>
                        </div>
                        <h3 className="text-base font-bold text-slate-900">{part.title}</h3>
                        <p className="mt-1 text-xs leading-relaxed text-slate-600">
                          {part.context}
                        </p>
                      </div>

                      <Link
                        href={`/listening/${primaryListening.id}?part=${part.index}`}
                        className="mt-4 inline-flex items-center justify-center gap-1.5 rounded-lg border border-indigo-200 bg-indigo-50/70 px-3.5 py-2 text-xs font-semibold text-indigo-800 transition hover:bg-indigo-100"
                      >
                        Launch Part {part.index} Drill
                        <ArrowRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {/* Unified Recent Sessions & Skill Accuracy Profile (Clickable + Resettable) */}
        <div className="grid gap-6 lg:grid-cols-5">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs lg:col-span-3">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-blue-700" />
                <div>
                  <h2 className="text-base font-bold text-slate-900">Recent Sessions</h2>
                  <p className="text-[11px] text-slate-500">
                    Click any completed drill or mock to inspect its full result & summary
                  </p>
                </div>
              </div>

              {progress && progress.recent_sessions.length > 0 && (
                <div className="flex items-center gap-1.5">
                  {!confirmResetSessions ? (
                    <button
                      type="button"
                      onClick={() => setConfirmResetSessions(true)}
                      className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
                    >
                      <RotateCcw className="h-3 w-3" />
                      Reset
                    </button>
                  ) : (
                    <>
                      <button
                        type="button"
                        disabled={resetting}
                        onClick={handleResetSessions}
                        className="rounded-md bg-rose-600 px-2.5 py-1 text-xs font-bold text-white hover:bg-rose-700"
                      >
                        Confirm Reset
                      </button>
                      <button
                        type="button"
                        onClick={() => setConfirmResetSessions(false)}
                        className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-600"
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {!progress || progress.recent_sessions.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
                Complete a Reading or Listening drill to record your Band score history and unlock
                one-click past result reviews.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 text-xs text-slate-500 uppercase">
                      <th className="pb-2">Drill / Test</th>
                      <th className="pb-2">Score</th>
                      <th className="pb-2">Band</th>
                      <th className="pb-2 text-right">Review</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {progress.recent_sessions.map((s) => {
                      const reviewHref =
                        s.module === "listening"
                          ? `/listening/${s.test_id}?session=${s.session_id}${
                              s.passage_index ? `&part=${s.passage_index}` : ""
                            }`
                          : `/reading/${s.test_id}?session=${s.session_id}${
                              s.passage_index ? `&passage=${s.passage_index}` : ""
                            }`;

                      return (
                        <tr
                          key={s.session_id}
                          className="group transition hover:bg-blue-50/40"
                        >
                          <td className="py-2.5 pr-2">
                            <Link href={reviewHref} className="block">
                              <div className="flex items-center gap-1.5">
                                <span
                                  className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                                    s.module === "listening"
                                      ? "bg-indigo-100 text-indigo-800"
                                      : "bg-blue-100 text-blue-800"
                                  }`}
                                >
                                  {s.module}
                                </span>
                                <span className="font-semibold text-slate-900 group-hover:text-blue-700">
                                  {s.test_title}
                                </span>
                              </div>
                              <p className="mt-0.5 text-[11px] text-slate-500">
                                {s.mode === "drill"
                                  ? s.passage_index
                                    ? `${s.module === "listening" ? "Part" : "Passage"} ${s.passage_index} Drill`
                                    : "Single-Passage Drill"
                                  : "Full Mock"}{" "}
                                ·{" "}
                                {s.completed_at
                                  ? new Date(s.completed_at).toLocaleString([], {
                                      month: "short",
                                      day: "numeric",
                                      hour: "2-digit",
                                      minute: "2-digit",
                                    })
                                  : "—"}
                              </p>
                            </Link>
                          </td>
                          <td className="py-2.5 text-xs font-semibold text-slate-700">
                            {s.raw_score} / {s.total_questions}
                          </td>
                          <td className="py-2.5">
                            <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-bold text-emerald-800">
                              Band {s.overall_band?.toFixed(1)}
                            </span>
                          </td>
                          <td className="py-2.5 text-right">
                            <Link
                              href={reviewHref}
                              className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-blue-700 hover:border-blue-300 hover:bg-blue-50"
                            >
                              Summary
                              <ArrowRight className="h-3 w-3" />
                            </Link>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs lg:col-span-2">
            <div className="mb-4 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-indigo-600" />
                <div>
                  <h2 className="text-base font-bold text-slate-900">Skill Accuracy Profile</h2>
                  <p className="text-[11px] text-slate-500">Cumulative accuracy by question type</p>
                </div>
              </div>

              {progress && progress.skills.length > 0 && (
                <div className="flex items-center gap-1.5">
                  {!confirmResetSkills ? (
                    <button
                      type="button"
                      onClick={() => setConfirmResetSkills(true)}
                      className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
                    >
                      <RotateCcw className="h-3 w-3" />
                      Reset
                    </button>
                  ) : (
                    <>
                      <button
                        type="button"
                        disabled={resetting}
                        onClick={handleResetSkills}
                        className="rounded-md bg-rose-600 px-2.5 py-1 text-xs font-bold text-white hover:bg-rose-700"
                      >
                        Confirm
                      </button>
                      <button
                        type="button"
                        onClick={() => setConfirmResetSkills(false)}
                        className="rounded-md border border-slate-200 px-2 py-1 text-xs text-slate-600"
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {!progress || progress.skills.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
                Accuracy by question type (T/F/NG, Matching Headings, Map Labelling, Completion)
                will appear here after your first submission.
              </div>
            ) : (
              <div className="space-y-3.5">
                {progress.skills.map((sk) => {
                  const { moduleLabel, typeLabel } = formatSkillKey(sk.skill_key);
                  return (
                    <div key={sk.skill_key}>
                      <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                        <span className="font-semibold text-slate-800">
                          <span
                            className={`mr-1.5 rounded px-1 py-0.5 text-[10px] font-bold ${
                              moduleLabel === "Listening"
                                ? "bg-indigo-100 text-indigo-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {moduleLabel}
                          </span>
                          {typeLabel}
                        </span>
                        <span className="shrink-0 font-medium text-slate-600">
                          {sk.correct_count}/{sk.attempts_count} ({sk.accuracy_pct}%) · B
                          {sk.estimated_band.toFixed(1)}
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                        <div
                          className={`h-full rounded-full ${
                            moduleLabel === "Listening" ? "bg-indigo-600" : "bg-blue-600"
                          }`}
                          style={{ width: `${Math.min(100, sk.accuracy_pct)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </div>

        {/* Strategy Notes Preview */}
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookMarked className="h-5 w-5 text-emerald-700" />
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  Structured Strategy Notes (IELTS Advantage ·{" "}
                  {activeTab === "reading" ? "Reading" : "Listening"})
                </h2>
                <p className="text-xs text-slate-500">
                  Synthesized frameworks indexed for the post-submission Distractor Explainer
                </p>
              </div>
            </div>
            <Link
              href="/notes"
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:underline"
            >
              Browse All Notes ({notes.length})
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            {filteredNotes.slice(0, 3).map((note) => (
              <div
                key={note.id}
                className="rounded-lg border border-slate-200 bg-slate-50/70 p-4"
              >
                <span className="rounded bg-white px-2 py-0.5 text-[11px] font-semibold text-blue-700 ring-1 ring-slate-200">
                  {formatQuestionTypeLabel(note.question_type)}
                </span>
                <h3 className="mt-2 text-sm font-bold text-slate-900">{note.title}</h3>
                <p className="mt-1 line-clamp-2 text-xs text-slate-600">
                  {note.strategy_steps[0]}
                </p>
                <a
                  href={note.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-blue-700"
                >
                  <BookOpen className="h-3.5 w-3.5" />
                  Source Lesson
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* Roadmap Bar */}
        <section className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-100/70 px-5 py-3.5 text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-slate-500" />
            <span>
              <strong>Roadmap:</strong> Milestone 1 (Reading · 30-Passage Bank) ✅ · Milestone 2
              (Listening · 4-Part + Map) ✅ · Milestone 3 (Writing AI Rubric) · Milestone 4 (Live
              Speaking)
            </span>
          </div>
        </section>
      </main>

      <ApiKeyModal
        open={apiModalOpen}
        onClose={() => setApiModalOpen(false)}
        onSaved={(hasKey) => setHasPersonalKey(hasKey)}
      />
    </div>
  );
}
