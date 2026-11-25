"use client";

import React from "react";
import type { PublicQuestionItem, QuestionVerdict } from "@/types/reading";

interface QuestionNavigatorProps {
  questions: PublicQuestionItem[];
  answers: Record<string, string>;
  flagged: Record<string, boolean>;
  verdicts: Record<string, QuestionVerdict>;
  activePassageIndex: number;
  onJumpToQuestion: (q: PublicQuestionItem) => void;
}

export function QuestionNavigator({
  questions,
  answers,
  flagged,
  verdicts,
  activePassageIndex,
  onJumpToQuestion,
}: QuestionNavigatorProps) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto border-t border-slate-200 bg-white px-4 py-2.5">
      <span className="mr-2 shrink-0 text-xs font-semibold tracking-wide text-slate-500 uppercase">
        Questions
      </span>
      {questions.map((q) => {
        const verdict = verdicts[q.id];
        const isAnswered = Boolean((answers[q.id] || "").trim());
        const isFlagged = Boolean(flagged[q.id]);
        const inCurrentPassage = q.passage_index === activePassageIndex;

        let style = "border-slate-200 bg-white text-slate-600 hover:border-blue-400";
        if (verdict) {
          style = verdict.is_correct
            ? "border-emerald-500 bg-emerald-600 text-white"
            : "border-rose-500 bg-rose-600 text-white";
        } else if (isAnswered) {
          style = "border-blue-600 bg-blue-600 text-white";
        }

        return (
          <button
            key={q.id}
            type="button"
            onClick={() => onJumpToQuestion(q)}
            title={`Q${q.question_number} (Passage ${q.passage_index})`}
            className={`relative flex h-7 w-7 shrink-0 items-center justify-center rounded-md border text-xs font-bold transition ${style} ${
              inCurrentPassage ? "ring-1 ring-slate-300 ring-offset-1" : "opacity-80"
            }`}
          >
            {q.question_number}
            {isFlagged && !verdict && (
              <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-amber-400 ring-1 ring-white" />
            )}
          </button>
        );
      })}
    </div>
  );
}
