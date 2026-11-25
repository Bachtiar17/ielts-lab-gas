import { NextResponse } from "next/server";
import { getTaxonomy } from "@/lib/server/contentStore";

export async function GET() {
  return NextResponse.json(getTaxonomy());
}
