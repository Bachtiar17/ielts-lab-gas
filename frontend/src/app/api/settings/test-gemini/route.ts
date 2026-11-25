import { NextRequest, NextResponse } from "next/server";
import { testGeminiKeyNode } from "@/lib/server/explainer";

export async function POST(request: NextRequest) {
  const body = (await request.json().catch(() => ({}))) as {
    api_key?: string;
    model?: string;
  };
  if (!body.api_key || body.api_key.trim().length < 10) {
    return NextResponse.json(
      { ok: false, model_used: body.model || "gemini-3.5-flash-lite", message: "API key is too short." },
      { status: 400 }
    );
  }
  const result = await testGeminiKeyNode(body.api_key, body.model || "gemini-3.5-flash-lite");
  return NextResponse.json(result);
}
