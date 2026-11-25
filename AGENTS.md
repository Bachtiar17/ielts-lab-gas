# IELTS Lab — Project Standards & Agent Guardrails

These rules are always active for every agent working inside `ielts-lab`.

## 1. Allowed Sources & Copyright Hygiene (Strict)
Only derive exam structure, pedagogy, and calibration parameters from the three approved sources:
1. **IDP IELTS Academic** (`https://ielts.idp.com/about/which-test-do-i-take/academic`): Official exam structure, timing, question-type taxonomy, and public band descriptors.
2. **IELTS Advantage** (`https://www.youtube.com/@Ieltsadvantage`): Teaching frameworks, strategy steps, Band 6→8 mistake patterns, and drill concepts ingested via our Voice/Video-to-Note parser (`pipelines/`). Always synthesize original structured notes with attribution and timestamp links; never re-host videos or copy verbatim scripts as original content.
3. **Google Drive `Cambridge IELTS` folder** (`1Dy70l9yI8mwZfCdweNiUujmu089NGomB`):
   - Use **strictly offline** for difficulty calibration, passage/audio telemetry, distractor pattern analysis, and private Writing scorer validation.
   - Prioritize **Cambridge IELTS 15–19 (Academic only)**; exclude General Training PDFs and non-IELTS files (e.g., CAE).
   - **NEVER** copy, store, commit, or serve verbatim Cambridge passages, questions, answer keys, or MP3 files in the application database, frontend, or Git repository.
   - Keep all temporary downloads exclusively inside `data/private_reference/` (gitignored).

## 2. Architecture & Tech Stack Conventions
- **Frontend (`frontend/`)**: TypeScript + Next.js (App Router) + Tailwind CSS + shadcn/ui (Web-First PWA).
- **Backend & AI Pipelines (`backend/`, `pipelines/`)**: Python + FastAPI, structured JSON outputs via the official `google-genai` SDK.
- **Database**: PostgreSQL + `pgvector` (SQLite acceptable only for fast local unit tests).
- **Media Storage**: Local disk during MVP; S3-compatible / Supabase Storage for deployment.

## 3. Scoring & AI Discipline
- **Deterministic First:** Listening and Academic Reading grading, normalization, word-limit checks, and raw-to-band conversions MUST be implemented in pure deterministic code with unit tests — never delegated to an LLM.
- **Multimodal & Calibrated AI:** Writing (Task 1 chart + essay, Task 2 essay) and Speaking (raw audio + transcript) scoring MUST use structured JSON schemas, explicit `scorer_version` tracking, and offline calibration benchmarks (`MAE ≤ 0.5` bands, `QWK ≥ 0.80`) before shipping prompt changes.
- **Model Routing:**
  - Use **Gemini Flash** for Voice-to-Note parsing, distractor explanations, Study Coach queries, and Live Speaking turn-taking (Gemini Live API).
  - Use **Gemini Pro** for final Writing rubric grading, post-session Speaking audio evaluation, and offline Generator/Critic content creation.

## 4. Engineering Quality & Milestones
- Follow the approved vertical-slice milestone order:
  1. **Milestone 1:** Foundation + Academic Reading MVP
  2. **Milestone 2:** Listening Module
  3. **Milestone 3:** Academic Writing + Calibrated AI Scorer
  4. **Milestone 4:** Live Speaking Examiner + Adaptive Study Coach
- Every deterministic grader, parser schema, and band-conversion utility must include automated unit tests.
- Never commit secrets (`.env`, API keys) or raw copyrighted reference files.
