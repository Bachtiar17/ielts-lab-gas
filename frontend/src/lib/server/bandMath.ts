/**
 * Official IELTS Academic raw-to-band conversion curves and band rounding math.
 * 1:1 deterministic TypeScript counterpart of backend/app/scoring/band_math.py.
 */

export const ACADEMIC_READING_CURVE: ReadonlyArray<[number, number, number]> = [
  [39, 40, 9.0],
  [37, 38, 8.5],
  [35, 36, 8.0],
  [33, 34, 7.5],
  [30, 32, 7.0],
  [27, 29, 6.5],
  [23, 26, 6.0],
  [19, 22, 5.5],
  [15, 18, 5.0],
  [13, 14, 4.5],
  [10, 12, 4.0],
  [8, 9, 3.5],
  [6, 7, 3.0],
  [4, 5, 2.5],
  [1, 3, 2.0],
  [0, 0, 1.0],
];

export const LISTENING_CURVE: ReadonlyArray<[number, number, number]> = [
  [39, 40, 9.0],
  [37, 38, 8.5],
  [35, 36, 8.0],
  [32, 34, 7.5],
  [30, 31, 7.0],
  [26, 29, 6.5],
  [23, 25, 6.0],
  [18, 22, 5.5],
  [16, 17, 5.0],
  [13, 15, 4.5],
  [10, 12, 4.0],
  [8, 9, 3.5],
  [6, 7, 3.0],
  [4, 5, 2.5],
  [1, 3, 2.0],
  [0, 0, 1.0],
];

export function roundToHalf(score: number): number {
  const clamped = Math.max(0.0, Math.min(9.0, score));
  const rounded = Math.floor(clamped * 2.0 + 0.5 + 1e-12) / 2.0;
  return Math.max(0.0, Math.min(9.0, rounded));
}

function lookupCurve(
  rawScore: number,
  curve: ReadonlyArray<[number, number, number]>,
  totalQuestions = 40
): number {
  if (totalQuestions <= 0) {
    throw new Error("totalQuestions must be positive");
  }
  if (rawScore < 0 || rawScore > totalQuestions) {
    throw new Error(`rawScore (${rawScore}) must be within 0..${totalQuestions}`);
  }
  const equivalentRaw =
    totalQuestions === 40
      ? rawScore
      : Math.max(0, Math.min(40, Math.floor((rawScore / totalQuestions) * 40.0 + 0.5 + 1e-12)));

  for (const [low, high, band] of curve) {
    if (equivalentRaw >= low && equivalentRaw <= high) {
      return band;
    }
  }
  return 1.0;
}

export function rawToReadingBand(rawScore: number, totalQuestions = 40): number {
  return lookupCurve(rawScore, ACADEMIC_READING_CURVE, totalQuestions);
}

export function rawToListeningBand(rawScore: number, totalQuestions = 40): number {
  return lookupCurve(rawScore, LISTENING_CURVE, totalQuestions);
}

export function computeWritingBand(task1Band: number, task2Band: number): number {
  return roundToHalf((task1Band + 2.0 * task2Band) / 3.0);
}

export function computeOverallBand(
  listening: number,
  reading: number,
  writing: number,
  speaking: number
): number {
  return roundToHalf((listening + reading + writing + speaking) / 4.0);
}
