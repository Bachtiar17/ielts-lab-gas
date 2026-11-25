# IELTS Academic Domain & Scoring Rules

Reference specification for exam logic, question types, and band calculations across `ielts-lab`.

## 1. Module Taxonomy (IDP IELTS Academic)
- **Reading (60 min, 40 questions, 3 academic passages):**
  - Multiple choice, True/False/Not Given, Yes/No/Not Given, Matching (information, headings, features, sentence endings), Completion (sentence, summary, note, table, flow-chart, diagram label), Short-answer questions.
- **Listening (30 min, 40 questions, 4 Parts — post-2020 format, no Part 1 spoken example):**
  - Part 1: Everyday social conversation; Part 2: Everyday social monologue; Part 3: Academic/training discussion (up to 4 speakers); Part 4: Academic monologue/lecture.
  - Question types: Multiple choice, Matching, Plan/map/diagram labelling, Form/note/table/flow-chart/summary/sentence completion, Short-answer questions.
- **Writing (60 min, 2 formal tasks):**
  - **Task 1** (≥150 words, 1/3 weight): Summarize/describe visual data (line graph, bar chart, pie chart, table, map, process diagram). Requires factual verification against the chart's underlying JSON/image.
  - **Task 2** (≥250 words, 2/3 weight): Academic essay responding to an argument, viewpoint, or problem.
- **Speaking (11–14 min, 3 Parts):**
  - **Part 1** (4–5 min): General introduction & familiar topics.
  - **Part 2** (3–4 min): Cue card + 1 min prep + up to 2 min individual long turn.
  - **Part 3** (4–5 min): Abstract two-way discussion linked to Part 2 topic.

## 2. Deterministic Grading Rules (Reading & Listening)
- Normalize whitespace and case; accept UK/US spelling variants (e.g., `colour`/`color`, `centre`/`center`) and equivalent numerals (`3`/`three`) unless exact wording is required.
- Strictly enforce word/number limits (e.g., `NO MORE THAN TWO WORDS AND/OR A NUMBER`). Hyphenated words count as one word per IELTS rules.
- Map raw score (`0–40`) to Band `1.0–9.0` (0.5 increments) using **separate** Academic Reading and Listening conversion curves.

## 3. Rubric & Band Math (Writing & Speaking)
- **Writing Task 1 Criteria (0–9 each):** Task Achievement (TA), Coherence & Cohesion (CC), Lexical Resource (LR), Grammatical Range & Accuracy (GRA).
- **Writing Task 2 Criteria (0–9 each):** Task Response (TR), Coherence & Cohesion (CC), Lexical Resource (LR), Grammatical Range & Accuracy (GRA).
- **Writing Overall Band (computed in code, never by LLM):**
  - `writing_band = round_to_half((task1_band + 2 * task2_band) / 3)`
- **Speaking Criteria (0–9 each, MUST score from raw audio + transcript):**
  - Fluency & Coherence (FC), Lexical Resource (LR), Grammatical Range & Accuracy (GRA), Pronunciation (P).
  - `speaking_band = round_to_half((FC + LR + GRA + P) / 4)`
- **Overall IELTS Band:** Mean of all 4 module bands rounded to nearest `0.5` (`.25` rounds up to `.5`, `.75` rounds up to next whole band).

## 4. IELTS Advantage Voice-to-Note Schema
Parsed strategy notes stored in `data/notes/` must capture:
- `source_video_id`, `source_url`, `title`
- `module`, `question_type`
- `strategy_steps` (list)
- `common_mistakes` (list)
- `band_upgrade_patterns` (list)
- `timestamp_anchors` (list of `{time_sec, topic, url}`)
