import assert from "node:assert/strict";
import test from "node:test";
import {
  computeOverallBand,
  computeWritingBand,
  rawToListeningBand,
  rawToReadingBand,
  roundToHalf,
} from "../bandMath.ts";
import { gradeListeningItem, normalizeListeningText } from "../listeningGrader.ts";
import { countIeltsTokens, gradeReadingItem, normalizeText } from "../readingGrader.ts";

test("official IELTS half-band rounding and separate Reading vs Listening curves", () => {
  assert.equal(roundToHalf(6.24), 6.0);
  assert.equal(roundToHalf(6.25), 6.5);
  assert.equal(roundToHalf(6.75), 7.0);
  assert.equal(rawToReadingBand(32), 7.0);
  assert.equal(rawToListeningBand(32), 7.5);
  assert.equal(rawToReadingBand(26), 6.0);
  assert.equal(rawToListeningBand(26), 6.5);
  assert.equal(rawToReadingBand(10, 13), 7.0);
  assert.equal(computeWritingBand(6.0, 7.0), 6.5);
  assert.equal(computeOverallBand(7.5, 7.0, 6.5, 6.0), 7.0);
});

test("deterministic Reading grader: UK/US, word limits, hyphenated words, label sets", () => {
  assert.equal(normalizeText("Colourful Urbanisation"), normalizeText("colorful urbanization"));
  assert.deepEqual(countIeltsTokens("long-term"), [1, 0]);
  assert.deepEqual(countIeltsTokens("29%"), [0, 1]);

  const wrongSet = gradeReadingItem("tfng", "YES", { accepted: ["TRUE"] });
  assert.equal(wrongSet.is_correct, false);
  assert.equal(wrongSet.failure_reason, "wrong_label_set");

  const wl = { max_words: 1, allow_number: false, label: "ONE WORD ONLY" };
  const tooLong = gradeReadingItem("note_table_flowchart_completion", "the millpond", { accepted: ["millpond"] }, wl);
  assert.equal(tooLong.is_correct, false);
  assert.equal(tooLong.failure_reason, "word_limit_exceeded");

  assert.equal(
    gradeReadingItem("short_answer", "the hippocampus", { accepted: ["(the) hippocampus"] }, { max_words: 2, allow_number: true }).is_correct,
    true
  );
});

test("deterministic Listening grader: dates, times, currency, postcodes, map labels", () => {
  assert.equal(normalizeListeningText("14th July"), "14 july");
  assert.equal(normalizeListeningText("July 14"), "14 july");
  assert.equal(normalizeListeningText("9.30 am"), "9:30am");
  assert.equal(normalizeListeningText("£45"), "45");
  assert.equal(normalizeListeningText("45 pounds"), "45");
  assert.equal(normalizeListeningText("BH14 7QR", true, true), "bh147qr");

  assert.equal(
    gradeListeningItem("form_note_table_completion", "bh147qr", { accepted: ["BH14 7QR"], is_code: true }).is_correct,
    true
  );
  assert.equal(gradeListeningItem("map_plan_diagram", "f", { accepted: ["F"] }).is_correct, true);
});
