import { NextRequest, NextResponse } from "next/server";
import { findListeningTestById } from "@/lib/server/contentStore";
import { synthesizePartWavDataUrl } from "@/lib/server/explainer";

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ testId: string; partIndex: string }> }
) {
  const { testId, partIndex } = await context.params;
  const test = findListeningTestById(testId);
  if (!test) {
    return NextResponse.json({ detail: "Listening test not found." }, { status: 404 });
  }
  const part = test.parts.find((p) => p.index === Number(partIndex));
  if (!part) {
    return NextResponse.json({ detail: "Listening part not found." }, { status: 404 });
  }

  try {
    const res = await synthesizePartWavDataUrl(part, request.headers.get("x-gemini-api-key"));
    return NextResponse.json(res);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Gemini TTS synthesis failed.";
    return NextResponse.json({ detail: msg }, { status: msg.includes("No Gemini API key") ? 400 : 502 });
  }
}
