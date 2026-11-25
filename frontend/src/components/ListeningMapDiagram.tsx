"use client";

import React from "react";
import { Compass } from "lucide-react";
import type { ListeningMapData } from "@/types/reading";

interface ListeningMapDiagramProps {
  mapData: ListeningMapData;
  assignedLabels: Record<string, string>; // zone letter ('A'-'G') -> label e.g. 'Q11'
}

export function ListeningMapDiagram({ mapData, assignedLabels }: ListeningMapDiagramProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-bold text-slate-900">{mapData.title}</h3>
          <p className="text-xs text-slate-500">
            Orient yourself from the Main Entrance & Ticket Foyer before pressing Play
          </p>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-bold text-slate-700">
          <Compass className="h-3.5 w-3.5 text-blue-600" />
          N ↑
        </span>
      </div>

      <svg
        viewBox="0 0 680 385"
        className="h-auto w-full rounded-lg border border-slate-200 bg-slate-50"
        role="img"
        aria-label={mapData.title}
      >
        {/* Outer museum boundary */}
        <rect x="24" y="48" width="632" height="320" rx="10" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />

        {/* Landmarks */}
        {mapData.landmarks.map((lm, idx) => {
          const fill =
            lm.kind === "water"
              ? "#e0f2fe"
              : lm.kind === "courtyard"
              ? "#ecfdf5"
              : "#f1f5f9";
          const stroke =
            lm.kind === "water"
              ? "#38bdf8"
              : lm.kind === "courtyard"
              ? "#34d399"
              : "#94a3b8";
          const textFill =
            lm.kind === "water"
              ? "#0369a1"
              : lm.kind === "courtyard"
              ? "#047857"
              : "#334155";
          return (
            <g key={idx}>
              <rect
                x={lm.x}
                y={lm.y}
                width={lm.w}
                height={lm.h}
                rx="6"
                fill={fill}
                stroke={stroke}
                strokeWidth="1.5"
                strokeDasharray={lm.kind === "courtyard" ? "5 3" : undefined}
              />
              <text
                x={lm.x + lm.w / 2}
                y={lm.y + lm.h / 2 + 4}
                textAnchor="middle"
                fontSize="11"
                fontWeight="700"
                fill={textFill}
              >
                {lm.label}
              </text>
            </g>
          );
        })}

        {/* Labelable Zones A-G */}
        {mapData.slots.map((slot) => {
          const assigned = assignedLabels[slot.id];
          return (
            <g key={slot.id}>
              <rect
                x={slot.x}
                y={slot.y}
                width={slot.w}
                height={slot.h}
                rx="8"
                fill={assigned ? "#eff6ff" : "#fffbeb"}
                stroke={assigned ? "#2563eb" : "#f59e0b"}
                strokeWidth="2"
              />
              <text
                x={slot.x + slot.w / 2}
                y={slot.y + (assigned ? slot.h / 2 - 4 : slot.h / 2 + 6)}
                textAnchor="middle"
                fontSize="18"
                fontWeight="800"
                fill={assigned ? "#1d4ed8" : "#92400e"}
              >
                {slot.id}
              </text>
              {assigned && (
                <text
                  x={slot.x + slot.w / 2}
                  y={slot.y + slot.h / 2 + 16}
                  textAnchor="middle"
                  fontSize="10.5"
                  fontWeight="600"
                  fill="#1e40af"
                >
                  {assigned}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
