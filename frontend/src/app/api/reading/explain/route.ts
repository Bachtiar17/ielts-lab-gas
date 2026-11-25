import { NextRequest, NextResponse } from "next/server";
import { findQuestionItemById } from "@/lib/server/contentStore";
import { explainDistractorNode } from "@/lib/server/explainer";

export async function POST(request: NextRequest) {
  const body = (await request.json().catch(() => ({}))) as {
    item_id?: string;
    user_answer?: string;
    failure_reason?: string | null;
  };
  const found = body.item_id ? findQuestionItemById(body.item_id) : null;
  if (!found) {
    return NextResponse.json(
      { detail: `Question item '${body.item_id || ""}' not found.` },
      { status: 404 }
    );
  }

  const result = await explainDistractorNode({
    moduleName: found.module,
    test: found.test,
    item: found.item,
    userAnswer: body.user_answer || "",
    failureReason: body.failure_reason ?? null,
    apiKeyOverride: request.headers.get("x-gemini-api-key"),
    modelOverride: request.headers.get("x-gemini-model"),
  });

  return NextResponse.json(result);
}
