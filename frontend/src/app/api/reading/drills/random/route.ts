import { NextRequest, NextResponse } from "next/server";
import { getReadingDrills } from "@/lib/server/contentStore";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const excludeParam = searchParams.get("exclude") || "";
  const excluded = new Set(
    excludeParam
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
  );

  const allDrills = getReadingDrills();
  const picked = [];

  for (const slot of [1, 2, 3]) {
    const pool = allDrills.filter((d) => d.drill_slot === slot);
    if (pool.length === 0) continue;
    const fresh = pool.filter((d) => !excluded.has(d.id));
    const candidates = fresh.length > 0 ? fresh : pool;
    const choice = candidates[Math.floor(Math.random() * candidates.length)];
    const p0 = choice.passages[0];
    picked.push({
      id: choice.id,
      drill_slot: slot,
      title: choice.title,
      subtitle: choice.subtitle,
      topic: p0?.topic || "Academic",
      difficulty_label: choice.difficulty_label,
      question_count: choice.questions.length,
      recommended_minutes: choice.duration_minutes,
    });
  }

  return NextResponse.json({
    bank_size: allDrills.length,
    drills: picked,
  });
}
