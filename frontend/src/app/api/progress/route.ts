import { NextRequest, NextResponse } from "next/server";
import { getProgressSummary } from "@/lib/server/sessionStore";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const mod = searchParams.get("module");
  return NextResponse.json(getProgressSummary(mod));
}
