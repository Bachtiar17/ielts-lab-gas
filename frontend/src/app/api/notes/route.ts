import { NextRequest, NextResponse } from "next/server";
import { getAllNotes } from "@/lib/server/contentStore";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const mod = searchParams.get("module");
  const qtype = searchParams.get("question_type");
  return NextResponse.json(getAllNotes(mod, qtype));
}
