"use client";

import React, { useEffect, useRef, useState } from "react";
import { Eraser, Highlighter } from "lucide-react";
import type { ReadingPassage, TextHighlight } from "@/types/reading";

interface ActiveEvidence {
  passageIndex: number;
  paragraphId: string;
  quote: string;
  questionNumber: number;
}

interface PassagePaneProps {
  passage: ReadingPassage;
  fontSize: "sm" | "base" | "lg";
  highlights: Record<string, TextHighlight[]>;
  onAddHighlight: (paraKey: string, hl: TextHighlight) => void;
  onClearParagraphHighlights: (paraKey: string) => void;
  activeEvidence: ActiveEvidence | null;
}

interface SelectionPopover {
  paraKey: string;
  start: number;
  end: number;
  x: number;
  y: number;
}

function getOffsetWithinElement(container: HTMLElement, targetNode: Node, targetOffset: number): number {
  const range = document.createRange();
  range.selectNodeContents(container);
  range.setEnd(targetNode, targetOffset);
  return range.toString().length;
}

interface Segment {
  text: string;
  userColor?: "yellow" | "green";
  isEvidence?: boolean;
}

function buildRenderedSegments(
  text: string,
  userHighlights: TextHighlight[],
  evidenceQuote?: string
): Segment[] {
  const points = new Set<number>([0, text.length]);
  for (const h of userHighlights) {
    points.add(Math.max(0, Math.min(text.length, h.start)));
    points.add(Math.max(0, Math.min(text.length, h.end)));
  }

  let evStart = -1;
  let evEnd = -1;
  if (evidenceQuote) {
    evStart = text.indexOf(evidenceQuote);
    if (evStart >= 0) {
      evEnd = evStart + evidenceQuote.length;
      points.add(evStart);
      points.add(evEnd);
    }
  }

  const sorted = Array.from(points).sort((a, b) => a - b);
  const segments: Segment[] = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];
    if (end <= start) continue;
    const mid = (start + end) / 2;
    const matchingUser = userHighlights.find((h) => h.start <= mid && mid <= h.end);
    const isEvidence = evStart >= 0 && start >= evStart && end <= evEnd;
    segments.push({
      text: text.slice(start, end),
      userColor: matchingUser?.color,
      isEvidence,
    });
  }
  return segments;
}

export function PassagePane({
  passage,
  fontSize,
  highlights,
  onAddHighlight,
  onClearParagraphHighlights,
  activeEvidence,
}: PassagePaneProps) {
  const [popover, setPopover] = useState<SelectionPopover | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!activeEvidence || activeEvidence.passageIndex !== passage.index) return;
    const el = document.getElementById(`passage-${passage.index}-para-${activeEvidence.paragraphId}`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeEvidence, passage.index]);

  const handleMouseUp = (paraId: string, e: React.MouseEvent<HTMLParagraphElement>) => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || sel.rangeCount === 0) {
      setPopover(null);
      return;
    }
    const targetEl = e.currentTarget;
    const range = sel.getRangeAt(0);
    if (!targetEl.contains(range.startContainer) || !targetEl.contains(range.endContainer)) {
      setPopover(null);
      return;
    }

    const start = getOffsetWithinElement(targetEl, range.startContainer, range.startOffset);
    const end = getOffsetWithinElement(targetEl, range.endContainer, range.endOffset);
    if (end - start < 2) {
      setPopover(null);
      return;
    }

    const rect = range.getBoundingClientRect();
    const containerRect = containerRef.current?.getBoundingClientRect();
    const x = containerRect ? rect.left - containerRect.left + rect.width / 2 : rect.left;
    const y = containerRect
      ? rect.top - containerRect.top + (containerRef.current?.scrollTop || 0) - 44
      : rect.top - 44;

    setPopover({
      paraKey: `${passage.index}:${paraId}`,
      start,
      end,
      x: Math.max(80, x),
      y: Math.max(8, y),
    });
  };

  const applyHighlight = (color: "yellow" | "green") => {
    if (!popover) return;
    onAddHighlight(popover.paraKey, { start: popover.start, end: popover.end, color });
    window.getSelection()?.removeAllRanges();
    setPopover(null);
  };

  const fontClass =
    fontSize === "sm"
      ? "text-[15px] leading-7"
      : fontSize === "lg"
      ? "text-[19px] leading-9"
      : "text-[16.5px] leading-8";

  const totalHighlightsInPassage = passage.paragraphs.reduce(
    (acc, p) => acc + (highlights[`${passage.index}:${p.id}`]?.length || 0),
    0
  );

  return (
    <div
      ref={containerRef}
      className="relative h-full overflow-y-auto bg-white px-7 py-6 lg:px-10"
      onClick={() => {
        const sel = window.getSelection();
        if (!sel || sel.isCollapsed) setPopover(null);
      }}
    >
      {popover && (
        <div
          style={{ left: popover.x, top: popover.y }}
          className="absolute z-30 flex -translate-x-1/2 items-center gap-1 rounded-full border border-slate-200 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white shadow-lg"
          onMouseDown={(e) => e.preventDefault()}
        >
          <Highlighter className="mr-1 h-3.5 w-3.5 text-amber-300" />
          <button
            type="button"
            onClick={() => applyHighlight("yellow")}
            className="rounded-full bg-amber-300 px-2 py-0.5 text-slate-900 hover:bg-amber-200"
          >
            Yellow
          </button>
          <button
            type="button"
            onClick={() => applyHighlight("green")}
            className="rounded-full bg-emerald-300 px-2 py-0.5 text-slate-900 hover:bg-emerald-200"
          >
            Green
          </button>
        </div>
      )}

      <div className="mb-6 border-b border-slate-200 pb-4">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold tracking-wide text-blue-700 uppercase">
              Reading Passage {passage.index}
            </span>
            <span className="text-xs font-medium text-slate-500">{passage.topic}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-flex items-center gap-1">
              <Highlighter className="h-3.5 w-3.5 text-amber-500" />
              Select text to highlight
            </span>
            {totalHighlightsInPassage > 0 && (
              <button
                type="button"
                onClick={() =>
                  passage.paragraphs.forEach((p) =>
                    onClearParagraphHighlights(`${passage.index}:${p.id}`)
                  )
                }
                className="inline-flex items-center gap-1 rounded border border-slate-200 px-2 py-0.5 text-slate-600 hover:bg-slate-100"
              >
                <Eraser className="h-3 w-3" />
                Clear ({totalHighlightsInPassage})
              </button>
            )}
          </div>
        </div>
        <h1 className="passage-serif text-2xl font-bold tracking-tight text-slate-900 lg:text-3xl">
          {passage.title}
        </h1>
        {passage.subtitle && (
          <p className="mt-1.5 text-sm text-slate-600 italic">{passage.subtitle}</p>
        )}
      </div>

      <article className="space-y-5 pb-12">
        {passage.paragraphs.map((para) => {
          const paraKey = `${passage.index}:${para.id}`;
          const paraHighlights = highlights[paraKey] || [];
          const isEvidenceTarget =
            activeEvidence &&
            activeEvidence.passageIndex === passage.index &&
            activeEvidence.paragraphId === para.id;

          const segments = buildRenderedSegments(
            para.text,
            paraHighlights,
            isEvidenceTarget ? activeEvidence.quote : undefined
          );

          return (
            <div
              key={para.id}
              id={`passage-${passage.index}-para-${para.id}`}
              className={`group flex gap-3.5 rounded-lg p-2.5 transition-colors ${
                isEvidenceTarget ? "bg-sky-50/70 ring-1 ring-sky-300" : ""
              }`}
            >
              <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50 text-xs font-bold text-slate-700">
                {para.id}
              </div>
              <div className="flex-1">
                {isEvidenceTarget && (
                  <div className="mb-1.5 inline-flex items-center gap-1.5 rounded-full bg-sky-600 px-2.5 py-0.5 text-[11px] font-semibold text-white">
                    Evidence for Question {activeEvidence.questionNumber}
                  </div>
                )}
                <p
                  onMouseUp={(e) => handleMouseUp(para.id, e)}
                  className={`passage-serif text-slate-800 selection:bg-blue-100 ${fontClass}`}
                >
                  {segments.map((seg, idx) => {
                    if (seg.isEvidence) {
                      return (
                        <mark
                          key={idx}
                          className="evidence-flash rounded bg-sky-200 px-1 py-0.5 text-slate-950"
                        >
                          {seg.text}
                        </mark>
                      );
                    }
                    if (seg.userColor === "yellow") {
                      return (
                        <mark key={idx} className="rounded bg-amber-200/85 px-0.5 text-slate-900">
                          {seg.text}
                        </mark>
                      );
                    }
                    if (seg.userColor === "green") {
                      return (
                        <mark key={idx} className="rounded bg-emerald-200/80 px-0.5 text-slate-900">
                          {seg.text}
                        </mark>
                      );
                    }
                    return <React.Fragment key={idx}>{seg.text}</React.Fragment>;
                  })}
                </p>
              </div>
            </div>
          );
        })}
      </article>
    </div>
  );
}
