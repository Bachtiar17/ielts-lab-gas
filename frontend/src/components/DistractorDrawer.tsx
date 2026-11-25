"use client";

import React from "react";
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  ExternalLink,
  Loader2,
  MapPin,
  Sparkles,
  X,
  XCircle,
} from "lucide-react";
import { formatQuestionTypeLabel } from "@/lib/wordCount";
import type { DistractorExplanationResponse, QuestionVerdict } from "@/types/reading";

interface DistractorDrawerProps {
  open: boolean;
  loading: boolean;
  verdict: QuestionVerdict | null;
  data: DistractorExplanationResponse | null;
  error: string | null;
  onClose: () => void;
  onLocateEvidence: (verdict: QuestionVerdict) => void;
}

function formatSec(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function DistractorDrawer({
  open,
  loading,
  verdict,
  data,
  error,
  onClose,
  onLocateEvidence,
}: DistractorDrawerProps) {
  if (!open || !verdict) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/35 backdrop-blur-[1px]">
      <div className="flex h-full w-full max-w-lg flex-col bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-slate-900 px-2 py-0.5 text-xs font-bold text-white">
                Q{verdict.question_number}
              </span>
              <span className="text-xs font-semibold text-blue-700">
                {formatQuestionTypeLabel(verdict.question_type)}
              </span>
            </div>
            <h3 className="mt-1 text-base font-bold text-slate-900">
              Distractor Analysis & Strategy Note
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close distractor drawer"
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto px-6 py-5">
          {/* Verdict comparison */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              {verdict.is_correct ? (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
                  <CheckCircle2 className="h-4 w-4" />
                  Correct
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-100 px-3 py-1 text-xs font-bold text-rose-800">
                  <XCircle className="h-4 w-4" />
                  {verdict.failure_reason === "word_limit_exceeded"
                    ? "Word Limit Exceeded"
                    : verdict.failure_reason === "wrong_label_set"
                    ? "Wrong Label Set"
                    : verdict.failure_reason === "blank"
                    ? "Unanswered"
                    : "Incorrect"}
                </span>
              )}

              {(verdict.evidence_span?.paragraph_id || verdict.evidence_span?.transcript_id) && (
                <button
                  type="button"
                  onClick={() => {
                    onLocateEvidence(verdict);
                    onClose();
                  }}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-sky-700"
                >
                  <MapPin className="h-3.5 w-3.5" />
                  {verdict.evidence_span?.paragraph_id
                    ? `Locate Evidence (Para ${verdict.evidence_span.paragraph_id})`
                    : `Locate in Transcript (Part ${verdict.passage_index})`}
                </button>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
                <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                  Your Answer
                </p>
                <p className="mt-1 font-semibold text-slate-900">
                  {verdict.user_answer || "(blank)"}
                </p>
              </div>
              <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
                <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase">
                  Accepted Key
                </p>
                <p className="mt-1 font-semibold text-emerald-700">
                  {verdict.accepted_answers.join(" / ")}
                </p>
              </div>
            </div>
          </div>

          {verdict.evidence_span?.quote && (
            <div className="rounded-xl border border-sky-200 bg-sky-50/70 p-4">
              <p className="text-xs font-bold tracking-wide text-sky-800 uppercase">
                {verdict.evidence_span.paragraph_id
                  ? `Passage Evidence — Paragraph ${verdict.evidence_span.paragraph_id}`
                  : `Audio Transcript Evidence — Part ${verdict.passage_index}`}
              </p>
              <blockquote className="passage-serif mt-2 border-l-2 border-sky-500 pl-3 text-sm italic text-slate-800">
                &ldquo;{verdict.evidence_span.quote}&rdquo;
              </blockquote>
            </div>
          )}

          {loading && (
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 p-4 text-sm text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              Analyzing distractor mechanism…
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {data && !loading && (
            <>
              <div className="space-y-3 rounded-xl border border-indigo-100 bg-indigo-50/40 p-4">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold tracking-wide text-indigo-800 uppercase">
                    <Sparkles className="h-3.5 w-3.5" />
                    Distractor Breakdown
                  </span>
                  <span className="rounded bg-white px-2 py-0.5 font-mono text-[10px] text-slate-500 ring-1 ring-slate-200">
                    {data.explainer_mode}
                  </span>
                </div>
                <p className="text-sm leading-relaxed text-slate-800">
                  <strong className="text-slate-900">Why:</strong> {data.explanation.why_wrong}
                </p>
                <p className="text-sm leading-relaxed text-slate-800">
                  <strong className="text-slate-900">Trap Mechanism:</strong>{" "}
                  {data.explanation.distractor_trap}
                </p>
                <p className="text-sm leading-relaxed text-slate-800">
                  <strong className="text-slate-900">Next Time:</strong>{" "}
                  {data.explanation.how_to_avoid_next_time}
                </p>
              </div>

              {data.strategy_note && (
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="mb-3 flex items-start justify-between gap-2">
                    <div>
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold tracking-wide text-blue-700 uppercase">
                        <BookOpen className="h-3.5 w-3.5" />
                        {data.strategy_note.channel} Strategy Note
                      </span>
                      <h4 className="mt-0.5 text-sm font-bold text-slate-900">
                        {data.strategy_note.title}
                      </h4>
                    </div>
                    <a
                      href={data.strategy_note.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex shrink-0 items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      YouTube
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>

                  <p className="mb-1.5 text-xs font-bold text-slate-700 uppercase">
                    Action Steps
                  </p>
                  <ol className="mb-3 list-decimal space-y-1 pl-4 text-xs leading-relaxed text-slate-700">
                    {data.strategy_note.strategy_steps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>

                  <p className="mb-1.5 text-xs font-bold text-rose-700 uppercase">
                    Band 6.0–6.5 Pitfalls
                  </p>
                  <ul className="mb-3 list-disc space-y-1 pl-4 text-xs leading-relaxed text-slate-700">
                    {data.strategy_note.common_mistakes.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>

                  {data.strategy_note.timestamp_anchors.length > 0 && (
                    <div className="border-t border-slate-100 pt-2.5">
                      <p className="mb-1.5 text-[11px] font-bold text-slate-500 uppercase">
                        Video References
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {data.strategy_note.timestamp_anchors.map((a, idx) => (
                          <a
                            key={idx}
                            href={a.url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-blue-700 hover:bg-blue-50"
                          >
                            {a.time_sec > 0 && (
                              <span className="font-mono text-[10px] text-slate-500">
                                {formatSec(a.time_sec)}
                              </span>
                            )}
                            {a.topic}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
