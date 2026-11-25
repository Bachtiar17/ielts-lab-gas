"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookMarked, ExternalLink, GraduationCap } from "lucide-react";
import { fetchStrategyNotes } from "@/lib/api";
import { formatQuestionTypeLabel } from "@/lib/wordCount";
import type { StrategyNoteItem } from "@/types/reading";

export default function StrategyNotesPage() {
  const [notes, setNotes] = useState<StrategyNoteItem[]>([]);
  const [selectedModule, setSelectedModule] = useState<"all" | "reading" | "listening">("all");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStrategyNotes()
      .then(setNotes)
      .finally(() => setLoading(false));
  }, []);

  const moduleFiltered =
    selectedModule === "all" ? notes : notes.filter((n) => n.module === selectedModule);
  const types = Array.from(new Set(moduleFiltered.map((n) => n.question_type)));
  const visible =
    selectedType === "all"
      ? moduleFiltered
      : moduleFiltered.filter((n) => n.question_type === selectedType);

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3.5">
          <div className="flex items-center gap-2.5">
            <Link
              href="/"
              className="inline-flex items-center gap-1 rounded-md border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Workbench
            </Link>
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-blue-700" />
              <span className="font-bold text-slate-900">IELTS Advantage Strategy Notes</span>
            </div>
          </div>

          <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 text-xs font-semibold">
            {(["all", "reading", "listening"] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => {
                  setSelectedModule(m);
                  setSelectedType("all");
                }}
                className={`rounded-md px-2.5 py-1 capitalize transition ${
                  selectedModule === m
                    ? "bg-blue-700 text-white"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-6 py-8">
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setSelectedType("all")}
            className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
              selectedType === "all"
                ? "bg-blue-700 text-white"
                : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
            }`}
          >
            All Question Types ({moduleFiltered.length})
          </button>
          {types.map((qt) => (
            <button
              key={qt}
              type="button"
              onClick={() => setSelectedType(qt)}
              className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                selectedType === qt
                  ? "bg-blue-700 text-white"
                  : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-100"
              }`}
            >
              {formatQuestionTypeLabel(qt)}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-sm text-slate-500">Loading strategy notes…</p>
        ) : (
          <div className="space-y-5">
            {visible.map((note) => (
              <article
                key={note.id}
                className="rounded-xl border border-slate-200 bg-white p-6 shadow-2xs"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase ${
                          note.module === "listening"
                            ? "bg-indigo-100 text-indigo-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {note.module}
                      </span>
                      <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-800">
                        <BookMarked className="h-3.5 w-3.5 text-blue-700" />
                        {formatQuestionTypeLabel(note.question_type)}
                      </span>
                    </div>
                    <h2 className="mt-2 text-lg font-bold text-slate-900">{note.title}</h2>
                  </div>
                  <a
                    href={note.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    {note.channel} on YouTube
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>

                <div className="mt-4 grid gap-5 md:grid-cols-2">
                  <div>
                    <h3 className="mb-2 text-xs font-bold tracking-wide text-slate-700 uppercase">
                      Core Strategy Steps
                    </h3>
                    <ol className="list-decimal space-y-1.5 pl-4 text-sm text-slate-700">
                      {note.strategy_steps.map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ol>
                  </div>
                  <div>
                    <h3 className="mb-2 text-xs font-bold tracking-wide text-rose-700 uppercase">
                      Common Band 6.0–6.5 Mistakes
                    </h3>
                    <ul className="list-disc space-y-1.5 pl-4 text-sm text-slate-700">
                      {note.common_mistakes.map((m, idx) => (
                        <li key={idx}>{m}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-4 rounded-lg bg-emerald-50/70 p-3.5">
                  <h3 className="mb-1.5 text-xs font-bold tracking-wide text-emerald-800 uppercase">
                    Band 6 → Band 8 Upgrade Patterns
                  </h3>
                  <ul className="list-disc space-y-1 pl-4 text-xs text-slate-800">
                    {note.band_upgrade_patterns.map((p, idx) => (
                      <li key={idx}>{p}</li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
