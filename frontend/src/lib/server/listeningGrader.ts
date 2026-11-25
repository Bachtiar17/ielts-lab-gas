/**
 * 100% deterministic IELTS Listening grading engine (TypeScript).
 * 1:1 counterpart of backend/app/scoring/listening.py.
 */

import {
  type AnswerKeySpec,
  type GradeResult,
  type WordLimitRule,
  checkWordLimit,
  expandAnswerVariants,
  normalizeText,
} from "./readingGrader.ts";

const MONTHS: Record<string, string> = {
  jan: "january",
  january: "january",
  feb: "february",
  february: "february",
  mar: "march",
  march: "march",
  apr: "april",
  april: "april",
  may: "may",
  jun: "june",
  june: "june",
  jul: "july",
  july: "july",
  aug: "august",
  august: "august",
  sep: "september",
  sept: "september",
  september: "september",
  oct: "october",
  october: "october",
  nov: "november",
  november: "november",
  dec: "december",
  december: "december",
};

const DATE_DM_RE = /^(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?([a-z]+)$/i;
const DATE_MD_RE = /^([a-z]+)\s+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?$/i;
const TIME_RE = /^0?(\d{1,2})[:.](\d{2})\s*(a\.?m\.?|p\.?m\.?)?$/i;
const CURRENCY_PREFIX_RE = /^[£$€]\s*(\d+(?:[.,]\d+)?)$/;
const CURRENCY_SUFFIX_RE = /^(\d+(?:[.,]\d+)?)\s*(?:pounds?|gbp|dollars?|usd|euros?|eur)$/i;

export function normalizeListeningText(
  text: string,
  allowNumberWords = true,
  isCode = false
): string {
  const raw = text.trim();
  if (!raw) return "";

  if (isCode) {
    return raw.toLowerCase().replace(/[\s-]+/g, "");
  }

  const mCurPre = CURRENCY_PREFIX_RE.exec(raw);
  if (mCurPre) return mCurPre[1].replace(/,/g, "");

  const mCurSuf = CURRENCY_SUFFIX_RE.exec(raw);
  if (mCurSuf) return mCurSuf[1].replace(/,/g, "");

  const mTime = TIME_RE.exec(raw);
  if (mTime) {
    const hour = parseInt(mTime[1], 10);
    const minute = mTime[2];
    const ampm = (mTime[3] || "").replace(/\./g, "").toLowerCase();
    return `${hour}:${minute}${ampm}`;
  }

  const mDm = DATE_DM_RE.exec(raw);
  if (mDm && MONTHS[mDm[2].toLowerCase()]) {
    return `${parseInt(mDm[1], 10)} ${MONTHS[mDm[2].toLowerCase()]}`;
  }
  const mMd = DATE_MD_RE.exec(raw);
  if (mMd && MONTHS[mMd[1].toLowerCase()]) {
    return `${parseInt(mMd[2], 10)} ${MONTHS[mMd[1].toLowerCase()]}`;
  }

  return normalizeText(raw, allowNumberWords);
}

export function gradeListeningItem(
  questionType: string,
  userResponse: string | string[] | null | undefined,
  answerKey: AnswerKeySpec,
  wordLimitSpec?: WordLimitRule | null
): GradeResult {
  const qtype = questionType.trim().toLowerCase();
  const acceptedRaw = answerKey.accepted || [];
  const allowNumberWords = answerKey.allow_number_words !== false;
  const isCode = Boolean(answerKey.is_code);

  if (qtype === "mcq_multi") {
    const userList = Array.isArray(userResponse)
      ? userResponse.map((x) => String(x).trim().toUpperCase()).filter(Boolean)
      : String(userResponse || "")
          .split(",")
          .map((x) => x.trim().toUpperCase())
          .filter(Boolean);
    const expectedSet = new Set(acceptedRaw.map((x) => String(x).trim().toUpperCase()));
    const expectedSorted = Array.from(expectedSet).sort();
    if (userList.length === 0) {
      return {
        is_correct: false,
        normalized_user: "",
        accepted_display: expectedSorted,
        failure_reason: "blank",
        diagnostic_detail: "No answer selected.",
        word_count: 0,
        number_count: 0,
      };
    }
    const userSet = new Set(userList);
    const isOk =
      userSet.size === expectedSet.size && Array.from(userSet).every((v) => expectedSet.has(v));
    return {
      is_correct: isOk,
      normalized_user: Array.from(userSet).sort().join(", "),
      accepted_display: expectedSorted,
      failure_reason: isOk ? null : "incorrect",
      diagnostic_detail: isOk ? null : `Expected ${expectedSorted.join(", ")}.`,
      word_count: 0,
      number_count: 0,
    };
  }

  const rawStr = Array.isArray(userResponse)
    ? userResponse.join(" ").trim()
    : String(userResponse ?? "").trim();

  if (!rawStr) {
    return {
      is_correct: false,
      normalized_user: "",
      accepted_display: acceptedRaw,
      failure_reason: "blank",
      diagnostic_detail: "Question left unanswered.",
      word_count: 0,
      number_count: 0,
    };
  }

  if (["mcq_single", "matching", "map_plan_diagram"].includes(qtype)) {
    const normUser = rawStr.toUpperCase();
    const acceptedNorm = new Set(acceptedRaw.map((a) => a.trim().toUpperCase()));
    const isOk = acceptedNorm.has(normUser);
    return {
      is_correct: isOk,
      normalized_user: normUser,
      accepted_display: acceptedRaw,
      failure_reason: isOk ? null : "incorrect",
      diagnostic_detail: isOk ? null : `Selected '${normUser}'; expected '${acceptedRaw[0]}'.`,
      word_count: 0,
      number_count: 0,
    };
  }

  const rule = wordLimitSpec || answerKey.word_limit || null;
  const wl = checkWordLimit(rawStr, rule);
  const normUser = normalizeListeningText(rawStr, allowNumberWords, isCode);

  if (!wl.ok) {
    return {
      is_correct: false,
      normalized_user: normUser,
      accepted_display: acceptedRaw,
      failure_reason: "word_limit_exceeded",
      diagnostic_detail: wl.message,
      word_count: wl.words,
      number_count: wl.numbers,
    };
  }

  const acceptedVariants = new Set<string>();
  for (const pat of acceptedRaw) {
    for (const v of expandAnswerVariants(pat)) {
      acceptedVariants.add(normalizeListeningText(v, allowNumberWords, isCode));
      const m = CURRENCY_PREFIX_RE.exec(v.trim());
      if (m) acceptedVariants.add(m[1].replace(/,/g, ""));
    }
  }

  const isOk = acceptedVariants.has(normUser);
  return {
    is_correct: isOk,
    normalized_user: normUser,
    accepted_display: acceptedRaw,
    failure_reason: isOk ? null : "incorrect",
    diagnostic_detail: isOk ? null : `Expected one of: ${acceptedRaw.join(", ")}.`,
    word_count: wl.words,
    number_count: wl.numbers,
  };
}
