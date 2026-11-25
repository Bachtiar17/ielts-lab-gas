"use client";

import React from "react";
import {
  AlertTriangle,
  BookOpenCheck,
  CheckCircle2,
  Flag,
  MapPin,
  Sparkles,
  XCircle,
} from "lucide-react";
import { checkClientWordLimit, formatQuestionTypeLabel } from "@/lib/wordCount";
import type {
  PublicQuestionItem,
  QuestionGroup,
  QuestionVerdict,
  ReadingPassage,
} from "@/types/reading";

interface QuestionPaneProps {
  passage: ReadingPassage;
  questions: PublicQuestionItem[];
  answers: Record<string, string>;
  flagged: Record<string, boolean>;
  verdicts: Record<string, QuestionVerdict>;
  submitted: boolean;
  activeQuestionId: string | null;
  onAnswerChange: (itemId: string, value: string) => void;
  onToggleFlag: (itemId: string) => void;
  onExplain: (verdict: QuestionVerdict) => void;
  onLocateEvidence: (verdict: QuestionVerdict) => void;
}

function failureLabel(reason: string | null): string | null {
  if (!reason) return null;
  if (reason === "word_limit_exceeded") return "Word limit exceeded";
  if (reason === "wrong_label_set") return "Wrong label set";
  if (reason === "blank") return "Unanswered";
  return "Incorrect";
}

export function QuestionPane({
  passage,
  questions,
  answers,
  flagged,
  verdicts,
  submitted,
  activeQuestionId,
  onAnswerChange,
  onToggleFlag,
  onExplain,
  onLocateEvidence,
}: QuestionPaneProps) {
  const questionsByNumber = new Map(questions.map((q) => [q.question_number, q]));

  const renderInput = (q: PublicQuestionItem, group: QuestionGroup) => {
    const val = answers[q.id] || "";
    const disabled = submitted;

    if (q.question_type === "tfng" || q.question_type === "ynng") {
      const choices =
        q.question_type === "tfng" ? ["TRUE", "FALSE", "NOT GIVEN"] : ["YES", "NO", "NOT GIVEN"];
      return (
        <div className="mt-2.5 flex flex-wrap gap-2">
          {choices.map((choice) => {
            const active = val === choice;
            return (
              <button
                key={choice}
                type="button"
                disabled={disabled}
                onClick={() => onAnswerChange(q.id, choice)}
                className={`rounded-lg border px-3.5 py-1.5 text-xs font-semibold tracking-wide transition ${
                  active
                    ? "border-blue-600 bg-blue-600 text-white shadow-xs"
                    : "border-slate-200 bg-white text-slate-700 hover:border-blue-300 hover:bg-blue-50/50"
                } disabled:cursor-default disabled:opacity-85`}
              >
                {choice}
              </button>
            );
          })}
        </div>
      );
    }

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
                    ? "border-blue-600 bg-blue-50/60 text-slate-900"
                    : "border-slate-200 bg-white text-slate-700 hover:border-slate-300"
                } ${disabled ? "cursor-default" : ""}`}
              >
                <input
                  type="radio"
                  name={q.id}
                  value={opt.id}
                  checked={active}
                  disabled={disabled}
                  onChange={() => onAnswerChange(q.id, opt.id)}
                  className="mt-1 accent-blue-600"
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

    if (
      q.question_type === "matching_headings" ||
      q.question_type === "matching_features" ||
      q.question_type === "matching_sentence_endings" ||
      q.question_type === "matching_information"
    ) {
      const options = group.options || q.prompt_payload.options || [];
      return (
        <div className="mt-2.5">
          <select
            aria-label={`Answer for question ${q.question_number}`}
            value={val}
            disabled={disabled}
            onChange={(e) => onAnswerChange(q.id, e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none disabled:bg-slate-100"
          >
            <option value="">Select an option…</option>
            {options.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.id} — {opt.text}
              </option>
            ))}
          </select>
        </div>
      );
    }

    // Completion & short-answer text input with live IELTS word-count check
    const wlRule = q.prompt_payload.word_limit || group.word_limit;
    const wlStatus = checkClientWordLimit(val, wlRule);
    return (
      <div className="mt-2.5">
        <div className="flex items-center gap-2">
          <input
            type="text"
            aria-label={`Answer for question ${q.question_number}`}
            value={val}
            disabled={disabled}
            placeholder="Type your exact answer from the passage…"
            onChange={(e) => onAnswerChange(q.id, e.target.value)}
            className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:bg-slate-100 ${
              !wlStatus.ok
                ? "border-red-500 bg-red-50/40 focus:border-red-600"
                : "border-slate-300 bg-white focus:border-blue-600"
            }`}
          />
        </div>
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
              "Hyphenated words (e.g. long-term) count as 1 word."
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
    <div className="h-full overflow-y-auto bg-slate-50 px-5 py-6 lg:px-7">
      <div className="space-y-6 pb-16">
        {passage.question_groups.map((group) => {
          const groupQuestions = group.question_numbers
            .map((num) => questionsByNumber.get(num))
            .filter((item): item is PublicQuestionItem => Boolean(item));

          return (
            <section
              key={group.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs"
            >
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h2 className="text-base font-bold text-slate-900">{group.title}</h2>
                  <p className="text-xs font-medium text-blue-700">
                    {formatQuestionTypeLabel(group.question_type)}
                  </p>
                </div>
                {group.word_limit?.label && (
                  <span className="rounded-md border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-bold tracking-wide text-amber-900">
                    {group.word_limit.label}
                  </span>
                )}
              </div>

              <p className="mb-4 text-sm leading-relaxed text-slate-600">{group.instructions}</p>

              {group.note_heading && (
                <div className="mb-4 rounded-lg bg-slate-100 px-3.5 py-2 text-xs font-bold tracking-wide text-slate-800 uppercase">
                  {group.note_heading}
                </div>
              )}

              {group.options && group.options.length > 0 && (
                <div className="mb-4 rounded-lg border border-slate-200 bg-slate-50/80 p-3.5">
                  <p className="mb-2 text-xs font-bold tracking-wide text-slate-500 uppercase">
                    Options Reference Box
                  </p>
                  <ul className="space-y-1.5 text-sm text-slate-700">
                    {group.options.map((opt) => (
                      <li key={opt.id} className="flex gap-2">
                        <span className="w-6 shrink-0 font-bold text-slate-900">{opt.id}</span>
                        <span>{opt.text}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="space-y-4">
                {groupQuestions.map((q) => {
                  const verdict = verdicts[q.id];
                  const isFlagged = Boolean(flagged[q.id]);
                  const isActive = activeQuestionId === q.id;
                  const failBadge = verdict ? failureLabel(verdict.failure_reason) : null;

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
                          ? "border-blue-400 bg-blue-50/25 ring-1 ring-blue-200"
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

                        {!submitted && (
                          <button
                            type="button"
                            onClick={() => onToggleFlag(q.id)}
                            title={isFlagged ? "Remove flag" : "Flag for review"}
                            className={`shrink-0 rounded-md p-1.5 transition ${
                              isFlagged
                                ? "bg-amber-100 text-amber-700"
                                : "text-slate-400 hover:bg-slate-100 hover:text-slate-600"
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
                                  {failBadge}
                                </span>
                                <span className="rounded bg-white px-2 py-0.5 font-medium text-slate-700 ring-1 ring-slate-200">
                                  Accepted: <strong>{verdict.accepted_answers.join(" / ")}</strong>
                                </span>
                              </>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            {verdict.evidence_span?.paragraph_id && (
                              <button
                                type="button"
                                onClick={() => onLocateEvidence(verdict)}
                                className="inline-flex items-center gap-1 rounded-md border border-sky-200 bg-sky-50 px-2.5 py-1 font-semibold text-sky-700 hover:bg-sky-100"
                              >
                                <MapPin className="h-3.5 w-3.5" />
                                Para {verdict.evidence_span.paragraph_id}
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={() => onExplain(verdict)}
                              className="inline-flex items-center gap-1 rounded-md border border-indigo-200 bg-indigo-50 px-2.5 py-1 font-semibold text-indigo-700 hover:bg-indigo-100"
                            >
                              {verdict.is_correct ? (
                                <BookOpenCheck className="h-3.5 w-3.5" />
                              ) : (
                                <Sparkles className="h-3.5 w-3.5" />
                              )}
                              {verdict.is_correct ? "Review Evidence" : "Explain Distractor"}
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
  );
}
