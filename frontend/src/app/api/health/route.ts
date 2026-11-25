import { NextResponse } from "next/server";
import { getListeningTests, getReadingDrills } from "@/lib/server/contentStore";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    app_name: "IELTS Lab API (Next.js Node Runtime)",
    database_dialect: "nextjs-node-stateless",
    gemini_configured: Boolean((process.env.GEMINI_API_KEY || "").trim()),
    gemini_fast_model: process.env.GEMINI_FAST_MODEL || "gemini-3.5-flash-lite",
    reading_drill_bank_count: getReadingDrills().length,
    listening_test_count: getListeningTests().length,
  });
}
