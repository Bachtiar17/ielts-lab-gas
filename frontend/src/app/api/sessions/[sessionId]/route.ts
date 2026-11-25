import { NextRequest, NextResponse } from "next/server";
import { getSessionRecord } from "@/lib/server/sessionStore";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await context.params;
  const rec = getSessionRecord(sessionId);
  if (!rec || !rec.completed) {
    return NextResponse.json(
      { detail: `Completed session '${sessionId}' not found.` },
      { status: 404 }
    );
  }
  return NextResponse.json(rec.completed);
}
