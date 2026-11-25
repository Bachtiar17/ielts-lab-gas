# IELTS Lab

An open-source **IELTS Academic** practice workbench built for authentic computer-delivered exam ergonomics, **100% deterministic Reading & Listening grading**, a **30-passage rotating Academic Reading drill bank**, **4-Part Academic Listening** with interactive SVG floorplan labelling, and structured strategy notes attributed to **IELTS Advantage**.

> **Zero API key required for Reading & Listening!** All exam grading, word-limit checks, band math, Browser Multi-Voice Listening playback, and offline evidence explanations work completely free with no API key. Add a free or paid **Gemini API key** anytime via the in-app **Add Personal Gemini API** button for live AI distractor explanations, studio multi-speaker Listening WAV audio, and upcoming Writing/Speaking scoring.

---

## Deploy Free on Google AI Studio (Single-Port Node.js)

This repository is **Google AI Studio ready** out of the box — it runs completely as a single Node.js Next.js app on **port 3000** using built-in `/api/*` route handlers, while keeping `backend/` and `pipelines/` intact for offline Python research/calibration.

1. Import this GitHub repository into **Google AI Studio** (Build / App preview).
2. AI Studio automatically runs `npm install`, `npm run dev`, and `npm run build` from the root `package.json` on **port 3000** — no Python virtual environment or separate port 8000 server needed!
3. *(Optional)* Set `GEMINI_API_KEY` in AI Studio's environment/secrets, **or** let each user enter their own personal Free/Paid Gemini key directly via the in-app **Add Personal Gemini API** button.
4. **Private per-user progress:** Each learner's Recent Sessions, clickable Past Summaries, and Skill Accuracy Profile are stored cleanly in their own browser (`localStorage`), so progress survives container restarts and stays separate between users without needing a paid database.

---

## Easy 1-Click Local Start (No Terminal Experience Needed)

### Prerequisites (one-time install)
1. **[Node.js 20 LTS+](https://nodejs.org/)** *(Required — runs the full app alone via `npm install && npm run dev`!)*
2. **[Python 3.11+](https://www.python.org/downloads/)** *(Optional — only needed for offline calibration pipelines or running the FastAPI backend)*

### Start Locally (Node.js Only — Simplest!)
```bash
npm install
npm run dev
```
Then open **http://localhost:3000**.

### Or Use the 1-Click Launchers (Full Python + Node Stack)
- **macOS / Linux:** Open Terminal in this folder and run:
  ```bash
  ./start.sh
  ```
- **Windows:** Double-click **`start.bat`**

On the first run, the launcher automatically sets up `.venv`, installs dependencies, seeds the local SQLite database (30 Reading drill passages + 40-question Reading mock + 40-question 4-Part Listening mock + 12 IELTS Advantage strategy notes), starts both servers, and opens **http://localhost:3000** in your browser.

---

## Features Included (Milestones 1 & 2)

### Milestone 1 — Academic Reading
- **Full 60-Min Academic Reading Mock** (3 original academic passages, 40 questions, all official IDP question types).
- **30-Passage Rotating Single-Passage Drill Bank** (10 Passage 1, 10 Passage 2, 10 Passage 3 drills) that automatically serves 3 fresh passages on every refresh (plus a **Shuffle 3 New Passages** button).
- **Computer-Delivered Split-Pane UI:** Interactive Yellow/Green passage highlighter, adjustable font size (`A-`/`A`/`A+`), live countdown timer, live IELTS word-limit validator (hyphenated words count as 1 word), and 1–40 navigator.
- **100% Deterministic Grader:** UK/US spelling equivalence, numeric equivalence, optional parentheticals, strict word limits, `wrong_label_set` detection (T/F/NG vs Y/N/NG), and official 0–40 Academic Reading Band curve.

### Milestone 2 — IELTS Listening (Post-2020 4-Part Format)
- **Full 30-Min Listening Mock & Part 1–4 Drills** (40 questions, no Part 1 spoken example):
  - **Part 1:** Coastal Rowing Club enquiry (self-corrections, spelled surname, postcode, rescheduled date).
  - **Part 2:** Maritime Museum orientation with an **Interactive SVG Ground-Floor Map** (`A–G` labelling) + MCQ.
  - **Part 3:** Academic tutorial on Urban Micro-Forests (3 speakers, MCQ + Matching).
  - **Part 4:** Academic lecture on Ancient Amphitheatre Acoustics (`ONE WORD ONLY` lecture notes).
- **Zero-Cost Multi-Voice Playback + Optional Gemini 3.8 Studio TTS:** Plays immediately using Browser Multi-Voice Speech (with Exam 1-Play Lock or Practice Replay mode and speed control) or generates cached WAV audio via `gemini-3.8-flash-lite-tts`.
- **Deterministic Listening Grader:** Separate official Listening 0–40 Band curve + date (`14th July` / `July 14`), time (`9:30 am` / `9.30`), currency (`£45` / `45 pounds`), and postcode normalization.
- **Post-Submission Review:** Highlighted interactive transcript + Distractor Explainer Drawer linked to IELTS Advantage notes.

### Dashboard & Privacy
- **Clickable Past Sessions:** Click any completed Reading or Listening session in **Recent Sessions** to reopen its full graded Band summary, answers, evidence highlights, and Distractor Drawer.
- **Independent Reset Buttons:** Reset **Recent Sessions** or **Skill Accuracy Profile** anytime.
- **Personal Gemini API Key Modal:** Users with a Free or Paid Tier Gemini key can paste it directly in the browser (`localStorage`, sent per-request only — never saved to server disk or Git).

---

## Roadmap

1. **Milestone 1 (Complete):** Foundation + Academic Reading MVP + 30-Passage Drill Bank
2. **Milestone 2 (Complete):** Listening Module (Deterministic Grader + 4-Part Mock + Interactive Map + TTS Pipeline)
3. **Milestone 3 (Next):** Academic Writing (Task 1 charts + Task 2 essays) + Calibrated Multimodal Gemini Pro Scorer (`MAE ≤ 0.5`, `QWK ≥ 0.80`)
4. **Milestone 4:** Live Speaking Examiner (Gemini Live API) + Adaptive Study Coach

---

## Developer Commands

```bash
# Run full automated test suite (45+ unit & API integration tests)
.venv/bin/pytest -v

# Manually run servers in separate terminals
.venv/bin/uvicorn backend.app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Privacy & Copyright Hygiene
- `.env`, local databases (`data/*.db`), generated audio (`data/audio/`), and `data/private_reference/` are permanently excluded via `.gitignore`.
- All seeded passages, listening dialogues, maps, and questions are 100% original academic content calibrated to official IDP IELTS Academic specifications.
