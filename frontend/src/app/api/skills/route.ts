import { NextRequest, NextResponse } from "next/server";
import { clearSkills } from "@/lib/server/sessionStore";

export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const mod = searchParams.get("module");
  const deleted = clearSkills(mod);
  return NextResponse.json({ deleted_count: deleted, scope: mod || "all_skills" });
}
