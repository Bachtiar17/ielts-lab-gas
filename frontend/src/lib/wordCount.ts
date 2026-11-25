import type { WordLimitSpec } from "@/types/reading";

const NUMBER_TOKEN_RE = /^\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?$/i;

export function countIeltsTokens(rawText: string): { words: number; numbers: number } {
  const cleaned = rawText
    .trim()
    .replace(/[,;:!?"()[\]{}]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  if (!cleaned) return { words: 0, numbers: 0 };

  let words = 0;
  let numbers = 0;
  for (const part of cleaned.split(" ")) {
    const tok = part.replace(/^\.+|\.+$/g, "").trim();
    if (!tok) continue;
    const strippedCurrency = tok.replace(/^[$£€]/, "");
    if (NUMBER_TOKEN_RE.test(strippedCurrency)) {
      numbers += 1;
    } else {
      words += 1;
    }
  }
  return { words, numbers };
}

export function checkClientWordLimit(
  rawText: string,
  rule?: WordLimitSpec
): { ok: boolean; words: number; numbers: number; message: string | null } {
  const { words, numbers } = countIeltsTokens(rawText);
  if (!rule || !rawText.trim()) {
    return { ok: true, words, numbers, message: null };
  }
  if (rule.numbers_only && words > 0) {
    return { ok: false, words, numbers, message: "Numbers only allowed" };
  }
  if (rule.allow_number === false && numbers > 0) {
    return { ok: false, words, numbers, message: "No numbers allowed" };
  }
  if (typeof rule.max_words === "number" && words > rule.max_words) {
    return {
      ok: false,
      words,
      numbers,
      message: `${words}/${rule.max_words} words (over limit)`,
    };
  }
  if (typeof rule.max_numbers === "number" && numbers > rule.max_numbers) {
    return {
      ok: false,
      words,
      numbers,
      message: `${numbers}/${rule.max_numbers} numbers (over limit)`,
    };
  }
  return { ok: true, words, numbers, message: null };
}

export function formatQuestionTypeLabel(qtype: string): string {
  const map: Record<string, string> = {
    tfng: "True / False / Not Given",
    ynng: "Yes / No / Not Given",
    mcq_single: "Multiple Choice",
    mcq_multi: "Multiple Choice (Multi)",
    matching_headings: "Matching Headings",
    matching_information: "Matching Information",
    matching_features: "Matching Features",
    matching_sentence_endings: "Sentence Endings",
    matching: "Matching",
    sentence_completion: "Sentence Completion",
    summary_completion: "Summary Completion",
    note_table_flowchart_completion: "Note Completion",
    form_note_table_completion: "Form / Note Completion",
    diagram_label_completion: "Diagram Labelling",
    map_plan_diagram: "Map / Plan Labelling",
    short_answer: "Short Answer",
  };
  return map[qtype] || qtype.replace(/_/g, " ");
}

export function formatSkillKey(skillKey: string): { moduleLabel: string; typeLabel: string } {
  const [mod, qtype] = skillKey.split(":");
  return {
    moduleLabel: mod === "listening" ? "Listening" : "Reading",
    typeLabel: formatQuestionTypeLabel(qtype || skillKey),
  };
}
