/**
 * 100% deterministic IELTS Academic Reading grading engine (TypeScript).
 * 1:1 counterpart of backend/app/scoring/reading.py.
 */

export interface WordLimitRule {
  max_words?: number | null;
  allow_number?: boolean;
  max_numbers?: number | null;
  numbers_only?: boolean;
  label?: string;
}

export interface AnswerKeySpec {
  accepted: string[];
  allow_number_words?: boolean;
  is_code?: boolean;
  word_limit?: WordLimitRule;
}

export interface GradeResult {
  is_correct: boolean;
  normalized_user: string;
  accepted_display: string[];
  failure_reason: "blank" | "word_limit_exceeded" | "wrong_label_set" | "incorrect" | null;
  diagnostic_detail: string | null;
  word_count: number;
  number_count: number;
}

const UK_US_EQUIVALENTS: Record<string, string> = {
  colour: "color",
  colours: "colors",
  coloured: "colored",
  colourful: "colorful",
  centre: "center",
  centres: "centers",
  centred: "centered",
  metre: "meter",
  metres: "meters",
  kilometre: "kilometer",
  kilometres: "kilometers",
  litre: "liter",
  litres: "liters",
  fibre: "fiber",
  fibres: "fibers",
  theatre: "theater",
  theatres: "theaters",
  labour: "labor",
  neighbour: "neighbor",
  neighbours: "neighbors",
  neighbourhood: "neighborhood",
  behaviour: "behavior",
  behaviours: "behaviors",
  behavioural: "behavioral",
  favour: "favor",
  favourable: "favorable",
  flavour: "flavor",
  harbour: "harbor",
  humour: "humor",
  odour: "odor",
  rumour: "rumor",
  vapour: "vapor",
  organisation: "organization",
  organisations: "organizations",
  organise: "organize",
  organised: "organized",
  organising: "organizing",
  analyse: "analyze",
  analysed: "analyzed",
  analysing: "analyzing",
  realise: "realize",
  realised: "realized",
  recognise: "recognize",
  recognised: "recognized",
  emphasise: "emphasize",
  emphasised: "emphasized",
  minimise: "minimize",
  minimised: "minimized",
  maximise: "maximize",
  maximised: "maximized",
  optimise: "optimize",
  optimised: "optimized",
  utilise: "utilize",
  utilised: "utilized",
  specialise: "specialize",
  specialised: "specialized",
  urbanisation: "urbanization",
  industrialisation: "industrialization",
  standardise: "standardize",
  standardised: "standardized",
  programme: "program",
  programmes: "programs",
  catalogue: "catalog",
  catalogues: "catalogs",
  dialogue: "dialog",
  defence: "defense",
  offence: "offense",
  licence: "license",
  practise: "practice",
  travelling: "traveling",
  travelled: "traveled",
  traveller: "traveler",
  modelling: "modeling",
  modelled: "modeled",
  labelling: "labeling",
  labelled: "labeled",
  cancelling: "canceling",
  cancelled: "canceled",
  grey: "gray",
  artefact: "artifact",
  artefacts: "artifacts",
  aluminium: "aluminum",
  archaeology: "archeology",
  archaeological: "archeological",
  mediaeval: "medieval",
  sceptical: "skeptical",
  scepticism: "skepticism",
  manoeuvre: "maneuver",
  ageing: "aging",
  storey: "story",
  storeys: "stories",
  tyre: "tire",
  tyres: "tires",
  plough: "plow",
  mould: "mold",
  smoulder: "smolder",
  fulfil: "fulfill",
  fulfilment: "fulfillment",
  enrol: "enroll",
  enrolment: "enrollment",
  skilful: "skillful",
  wilful: "willful",
};

const NUMBER_WORDS: Record<string, string> = {
  zero: "0",
  one: "1",
  two: "2",
  three: "3",
  four: "4",
  five: "5",
  six: "6",
  seven: "7",
  eight: "8",
  nine: "9",
  ten: "10",
  eleven: "11",
  twelve: "12",
  thirteen: "13",
  fourteen: "14",
  fifteen: "15",
  sixteen: "16",
  seventeen: "17",
  eighteen: "18",
  nineteen: "19",
  twenty: "20",
  thirty: "30",
  forty: "40",
  fifty: "50",
  sixty: "60",
  seventy: "70",
  eighty: "80",
  ninety: "90",
  first: "1st",
  second: "2nd",
  third: "3rd",
  fourth: "4th",
  fifth: "5th",
  sixth: "6th",
  seventh: "7th",
  eighth: "8th",
  ninth: "9th",
  tenth: "10th",
};

const TFNG_ALIASES: Record<string, string> = {
  t: "TRUE",
  true: "TRUE",
  f: "FALSE",
  false: "FALSE",
  ng: "NOT GIVEN",
  "not given": "NOT GIVEN",
  notgiven: "NOT GIVEN",
  "not-given": "NOT GIVEN",
};

const YNNG_ALIASES: Record<string, string> = {
  y: "YES",
  yes: "YES",
  n: "NO",
  no: "NO",
  ng: "NOT GIVEN",
  "not given": "NOT GIVEN",
  notgiven: "NOT GIVEN",
  "not-given": "NOT GIVEN",
};

const NUMBER_TOKEN_RE = /^\d+(?:[.,]\d+)*(?:%|st|nd|rd|th)?$/i;

export function countIeltsTokens(rawText: string): [number, number] {
  const cleaned = rawText
    .trim()
    .replace(/[,;:!?"()[\]{}]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!cleaned) return [0, 0];

  let words = 0;
  let numbers = 0;
  for (const rawTok of cleaned.split(" ")) {
    const tok = rawTok.replace(/^\.+|\.+$/g, "").trim();
    if (!tok) continue;
    const strippedCurrency = tok.replace(/^[$£€]/, "");
    if (NUMBER_TOKEN_RE.test(strippedCurrency)) {
      numbers += 1;
    } else {
      words += 1;
    }
  }
  return [words, numbers];
}

export function checkWordLimit(
  rawText: string,
  rule?: WordLimitRule | null
): { ok: boolean; words: number; numbers: number; message: string | null } {
  const [words, numbers] = countIeltsTokens(rawText);
  if (!rule) return { ok: true, words, numbers, message: null };

  if (rule.numbers_only && words > 0) {
    return {
      ok: false,
      words,
      numbers,
      message: `Expected a number only, but received ${words} word(s).`,
    };
  }
  if (rule.allow_number === false && numbers > 0) {
    return {
      ok: false,
      words,
      numbers,
      message: `Numbers are not allowed (${rule.label || "WORDS ONLY"}).`,
    };
  }
  if (typeof rule.max_words === "number" && words > rule.max_words) {
    return {
      ok: false,
      words,
      numbers,
      message: `Exceeded word limit: wrote ${words} word(s), maximum allowed is ${rule.max_words} (${rule.label || ""}).`,
    };
  }
  if (typeof rule.max_numbers === "number" && numbers > rule.max_numbers) {
    return {
      ok: false,
      words,
      numbers,
      message: `Exceeded number limit: wrote ${numbers} number(s), maximum allowed is ${rule.max_numbers}.`,
    };
  }
  return { ok: true, words, numbers, message: null };
}

export function normalizeText(text: string, allowNumberWords = true): string {
  let s = text
    .trim()
    .toLowerCase()
    .replace(/[’‘]/g, "'")
    .replace(/[–—]/g, "-")
    .replace(/\bper\s+cent\b/g, "%")
    .replace(/\bpercent\b/g, "%")
    .replace(/(\d)\s+%/g, "$1%")
    .replace(/[^\w\s'%.-]/g, " ")
    .replace(/(?<!\d)\.(?!\d)/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  if (!s) return "";

  const out: string[] = [];
  for (let tok of s.split(" ")) {
    if (!tok) continue;
    if (tok.includes("-")) {
      tok = tok
        .split("-")
        .map((p) => UK_US_EQUIVALENTS[p] ?? p)
        .join("-");
    } else {
      tok = UK_US_EQUIVALENTS[tok] ?? tok;
    }
    if (allowNumberWords && NUMBER_WORDS[tok]) {
      tok = NUMBER_WORDS[tok];
    }
    out.push(tok);
  }
  s = out.join(" ");
  return s;
}

export function expandAnswerVariants(pattern: string): string[] {
  const branches = pattern
    .split("/")
    .map((b) => b.trim())
    .filter(Boolean);
  const expanded: string[] = [];
  const parenRe = /\(([^()]+)\)/g;

  for (const branch of branches) {
    const matches = Array.from(branch.matchAll(parenRe));
    if (matches.length === 0) {
      expanded.push(branch);
      continue;
    }
    const combos = 1 << matches.length;
    for (let mask = 0; mask < combos; mask++) {
      let out = "";
      let cursor = 0;
      matches.forEach((m, idx) => {
        const start = m.index ?? 0;
        out += branch.slice(cursor, start);
        if ((mask & (1 << idx)) !== 0) {
          out += m[1];
        }
        cursor = start + m[0].length;
      });
      out += branch.slice(cursor);
      const candidate = out.replace(/\s+/g, " ").trim();
      if (candidate) expanded.push(candidate);
    }
  }
  return Array.from(new Set(expanded));
}

export function gradeReadingItem(
  questionType: string,
  userResponse: string | string[] | null | undefined,
  answerKey: AnswerKeySpec,
  wordLimitSpec?: WordLimitRule | null
): GradeResult {
  const qtype = questionType.trim().toLowerCase();
  const acceptedRaw = answerKey.accepted || [];
  const allowNumberWords = answerKey.allow_number_words !== false;

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

  if (qtype === "tfng") {
    const keyLower = rawStr.toLowerCase().replace(/\s+/g, " ").trim();
    const expected =
      TFNG_ALIASES[(acceptedRaw[0] || "").trim().toLowerCase()] ||
      (acceptedRaw[0] || "").trim().toUpperCase();
    if (["y", "yes", "n", "no"].includes(keyLower)) {
      return {
        is_correct: false,
        normalized_user: rawStr.toUpperCase(),
        accepted_display: [expected],
        failure_reason: "wrong_label_set",
        diagnostic_detail: "Used YES/NO on a TRUE/FALSE/NOT GIVEN question.",
        word_count: 0,
        number_count: 0,
      };
    }
    const mapped = TFNG_ALIASES[keyLower] || rawStr.toUpperCase();
    const isOk = mapped === expected;
    return {
      is_correct: isOk,
      normalized_user: mapped,
      accepted_display: [expected],
      failure_reason: isOk ? null : "incorrect",
      diagnostic_detail: isOk ? null : `Selected ${mapped}; correct answer is ${expected}.`,
      word_count: 0,
      number_count: 0,
    };
  }

  if (qtype === "ynng") {
    const keyLower = rawStr.toLowerCase().replace(/\s+/g, " ").trim();
    const expected =
      YNNG_ALIASES[(acceptedRaw[0] || "").trim().toLowerCase()] ||
      (acceptedRaw[0] || "").trim().toUpperCase();
    if (["t", "true", "f", "false"].includes(keyLower)) {
      return {
        is_correct: false,
        normalized_user: rawStr.toUpperCase(),
        accepted_display: [expected],
        failure_reason: "wrong_label_set",
        diagnostic_detail: "Used TRUE/FALSE on a YES/NO/NOT GIVEN question.",
        word_count: 0,
        number_count: 0,
      };
    }
    const mapped = YNNG_ALIASES[keyLower] || rawStr.toUpperCase();
    const isOk = mapped === expected;
    return {
      is_correct: isOk,
      normalized_user: mapped,
      accepted_display: [expected],
      failure_reason: isOk ? null : "incorrect",
      diagnostic_detail: isOk ? null : `Selected ${mapped}; correct answer is ${expected}.`,
      word_count: 0,
      number_count: 0,
    };
  }

  if (
    [
      "mcq_single",
      "matching_headings",
      "matching_information",
      "matching_features",
      "matching_sentence_endings",
    ].includes(qtype)
  ) {
    const normUser = rawStr.toLowerCase();
    const acceptedNorm = new Set(acceptedRaw.map((a) => a.trim().toLowerCase()));
    const isOk = acceptedNorm.has(normUser);
    const displayUser = qtype === "matching_headings" ? normUser : normUser.toUpperCase();
    return {
      is_correct: isOk,
      normalized_user: displayUser,
      accepted_display: acceptedRaw,
      failure_reason: isOk ? null : "incorrect",
      diagnostic_detail: isOk ? null : `Selected '${displayUser}'; expected '${acceptedRaw[0]}'.`,
      word_count: 0,
      number_count: 0,
    };
  }

  const rule = wordLimitSpec || answerKey.word_limit || null;
  const wl = checkWordLimit(rawStr, rule);
  const normUser = normalizeText(rawStr, allowNumberWords);
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
      acceptedVariants.add(normalizeText(v, allowNumberWords));
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
