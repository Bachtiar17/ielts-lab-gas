import { NextRequest, NextResponse } from "next/server";
import { clearSessions } from "@/lib/server/sessionStore";

export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const mod = searchParams.get("module");
  const deleted = clearSessions(mod);
  return NextResponse.json({ deleted_count: deleted, scope: mod || "all_sessions" });
}
