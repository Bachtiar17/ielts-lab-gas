"use client";

const KEY_STORAGE = "ielts_lab_personal_gemini_key";
const MODEL_STORAGE = "ielts_lab_personal_gemini_model";

export interface PersonalGeminiConfig {
  apiKey: string;
  model: string;
}

export const GEMINI_MODEL_OPTIONS = [
  {
    id: "gemini-3.5-flash-lite",
    label: "Gemini 3.5 Flash-Lite",
    tier: "Free Tier Recommended",
    note: "Fastest & most reliable quota on Free Tier for distractor explanations.",
  },
  {
    id: "gemini-4-hydrogen",
    label: "Gemini 4 Hydrogen",
    tier: "Free / Paid Tier",
    note: "Stronger reasoning & deeper pedagogy explanations (best with Paid Tier).",
  },
  {
    id: "gemini-4-neon",
    label: "Gemini 4 Neon",
    tier: "Paid Tier (Pro)",
    note: "Frontier reasoning for complex rubric & Writing/Speaking feedback.",
  },
];

export function loadPersonalGeminiConfig(): PersonalGeminiConfig {
  if (typeof window === "undefined") {
    return { apiKey: "", model: "gemini-3.5-flash-lite" };
  }
  return {
    apiKey: window.localStorage.getItem(KEY_STORAGE) || "",
    model: window.localStorage.getItem(MODEL_STORAGE) || "gemini-3.5-flash-lite",
  };
}

export function savePersonalGeminiConfig(config: PersonalGeminiConfig): void {
  if (typeof window === "undefined") return;
  const trimmed = config.apiKey.trim();
  if (trimmed) {
    window.localStorage.setItem(KEY_STORAGE, trimmed);
  } else {
    window.localStorage.removeItem(KEY_STORAGE);
  }
  window.localStorage.setItem(MODEL_STORAGE, config.model || "gemini-3.5-flash-lite");
}

export function clearPersonalGeminiConfig(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(KEY_STORAGE);
  window.localStorage.removeItem(MODEL_STORAGE);
}
