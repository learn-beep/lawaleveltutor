# lawaleveltutor.com

Static Astro site for OCR A Level Law (H418) and AS Level Law (H018), deployed on Netlify. Built 24 November 2026 from the Sociology site (alevelsociologytutor.com) with the `subject-revision-site` skill.

## Run locally
    npm install
    npm run dev        # http://localhost:4321
    npm run build      # writes dist/ (150 pages)

## Deploy
Push to `main` of the linked GitHub repository; Netlify builds with `npm run build` and publishes `dist/`.
Set `CROPS=off` in Netlify's environment to replace every OCR crop with a link to OCR's site.

## Data
- `scripts/export.py --bank "<Question Bank folder>" --topics topics.json --config site.config.json [--images [--only <bundle>]]`
  reads the OCR Law question bank export (`Dropbox\Teaching\Law\OCR\Question Bank\data\index.js`, `data\img\*.js`) and writes `src/data/questions.json`, `papers.json`, `topics.json`, `spec.json`, `weighting.json`, and with `--images` the WebP crops under `public/img/<bundle>/` (664 crops, 102 MB).
  `--only` rewrites the data files with a single paper: always follow it with the full run.
- This export is the Law version. It differs from the generic one: the question label comes from the bank's `L` field ("7* (also Q10*)"); the bank's notes list (`mc`) is split into the section line, the AO marks line and the remaining notes; each record carries `number`, `section`, `sectionLetter`, `part`, `title` (the question sentence without the scenario) and `dupOf`.
- Question types are the bank's `fmt`, renamed: Describe or explain, Evaluation, Scenario, Essay.
- `dupOf`: Papers 3 and 4 print the same two nature of law essays in Section A. The Paper 4 copies point at the Paper 3 question and are left out of topic pages, practice, counts and the analysis; the Paper 4 past-paper page still shows them (`everyQuestion` against `allQuestions` in `src/lib/data.ts`).
- `topics.json` (repo root) maps each of the 44 specification sections (1.1 to 7.7) to one site topic, in seven groups (`GROUPS` in `src/lib/data.ts` sets badges, motifs and "where examined"). Three sections (4.1, 6.1, 7.1, the "rules and theory" outlines) have no question yet; their pages say so.
- `src/data/exams.json` is the June 2027 timetable (H418/01 20 May pm, /02 27 May am, /03 and /04 10 June pm; H018/01 14 May pm, /02 21 May am), taken from several sites that transcribe OCR's final timetable, not from OCR's PDF.
- `src/data/boundaries.json` is A level out of 240 for 2022 to 2026 as compiled by tutor2u. OCR sets a boundary for each option (01+02+03 and 01+02+04) and they differ by a mark or two in some years: **check against OCR's boundary PDFs**. No AS boundaries yet.

## Pages specific to Law
- `/mock/` builds OCR-shaped papers: A-level Papers 1 and 2 (Section A one 8 and one 12; Section B one whole Part from one paper), Papers 3 and 4 (one nature of law essay; one Part), AS Papers 1 and 2 (eight 8-mark questions; Section B from one paper). 90 seconds a mark at A level; AS is 64 marks in 90 minutes.
- `/essays/` lists every essay; `/questions/type/scenarios/` every problem question. Self-marking uses four OCR levels (`LEVELS` in `src/scripts/player.js`: 8, 12 and 20 marks).
- Question-type pages: describe-explain, evaluation, scenarios, essays.
- Flashcards are key-term decks (`src/data/decks/*.json`, picked up by `src/lib/decks.ts`). Six decks, 49 cards, all `"checked": false`.
- `src/data/tutors.json` holds Sue (fee £100 per hour; no photo, biography facts or reviews yet).
- `[hidden] { display: none !important; }` is in the stylesheet (the Sociology template lacked it).

## Content that needs the tutor's check before or soon after launch
- The six key-term decks in `src/data/decks/`.
- The level summary on `/essays/` and the question-type introductions in `src/pages/questions/type/[type].astro`.
- The topic tags (made by the site; only the June 2024 Paper 1 pilot was reviewed).
- Sue's profile: two generic paragraphs until her background, photo and any reviews are supplied.

## Known gaps
- June 2023 AS Paper 2 has no examiners' report (OCR's link serves the Paper 1 report).
- June 2026 papers: add when OCR releases them.

## Cambridge International 9084 section (`/cambridge/`, added 25 Nov 2026)
- `npm run build` runs `node scripts/build.mjs` (the method used on the Economics and Sociology sites): the OCR site is built at the root as before, then a copy of `src/` is built with the Cambridge data and moved under `dist/cambridge/` with its internal links prefixed. Shared pages (tutors, about, privacy, terms, report, thank-you, 404) come from the OCR build only. One sitemap covers both.
- Board files are in `boards/cambridge/`:
  - `data/`, written by `python3 boards/cambridge/export_cie.py --bank "<Law\CIE\Question Bank>" [--images]` (lossless WebP crops to `public/img/cie/<paper>/`).
  - `exams.json` (June 2027, Cambridge final timetable, zone 3), `boundaries.json` (every A Level and AS option from Cambridge's threshold documents, June 2023 to November 2025; A Level out of 300 after weighting, Paper 2 × 1.25), `site.config.json`.
  - `replace.json` from `python3 boards/cambridge/make_replace.py` (not applied to overrides), and `overrides/src/` (home, topic and type pages, past papers, essays, mock, practice, syllabus checklist, thresholds, dates, analysis, what came up, `lib/data.ts`, `scripts/player.js`, 12 decks).
- 39 topics from the 53 syllabus sub-sections (small contract and tort sub-sections merged; `TOPIC_LIST` in the export script), in seven groups.
- Question types: Short answer, Explain or describe (10), Source-based application (Paper 2, 10), Scenario (25), Essay (10, 15, 25).
- Storage keys `malt-cie-…`; header strings are split so the replacements leave the OCR | Cambridge switch alone.
- For a tutor to check: the 12 Cambridge decks (`checked: false`; five adapted from the OCR decks, seven new), the level summaries on `/cambridge/essays/` and the question-type notes.
