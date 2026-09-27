# Align Code and Deck to the Shipped Product — Design

Date: 2026-09-27
Path: Architectural (restructures service layer, database surface, frontend, and deck)

## Problem

The repository contains two disjoint frontends, and the pitch deck describes neither accurately.

**Two frontends, one shipped.** `src/static/templates/index.html` and `course.html` are served by
`src/backend/app.py` and are the actual product. `src/static/js/app.js` (51KB), `theme.js`,
`styles.css`, and `components.css` are referenced by zero files in the repo — nothing loads them.
They describe a 10-view application (repository, PYQ, notebook OCR, question bank, curriculum,
generator, help, notes, quiz, chat, recommendations) that no user can reach.

**The Study Desk is faked.** `index.html:generateStudyKit()` takes pasted lecture text, slices the
first 50 characters into a "Core Academic Formulation" card, and renders a hardcoded
`f(x) = Σ xᵢwᵢ` and Stokes' theorem equation regardless of input. It makes no network call. Every
input produces the same output. The three preset chips are the same fake: `loadSampleData()` reads
a hardcoded `summaries` array from the in-file `PRESETS` object.

**The retrieval index points at nothing.** `rag_engine.py:RAGIndex` is the app's only search
engine and the only consumer of the native C DLL's BM25 implementation. Its `rebuild_index()`
indexes exactly three sources: notebooks, assignments, and PYQ papers. In the shipped database
those hold **0, 2, and 2 rows** — 84 chunks of near-nothing. Meanwhile the real corpus is
untouched by search:

| Table | Rows | Searchable content |
|---|---|---|
| `question_bank` | **1,740** | 57 subjects × 30 questions, each with difficulty, marks, type, model answer |
| `topic_content` | 57 | summary, key_points, formulas, examples, mcqs, practice, flashcards, viva |
| `interactive_content` | 84 | front_text / back_text flashcards |
| `curriculum` | 29 | course → topic → subtopic structure |
| `notebooks` | 0 | indexed, empty |
| `assignments` | 2 | indexed, near-empty |
| `pyq_papers` | 2 | indexed, near-empty |

**The deck states three false facts.** Slide 5 claims Tailwind CSS and Flask; the app uses
hand-written CSS and FastAPI/uvicorn. Slides 1, 4, and 5 name "OmniRoute" as the AI layer; the app
uses `google-generativeai` (Gemini) with a local heuristic fallback. Slide 4's pipeline diagram
labels a "Flask API Tokenizer." The deck also cites unsourced figures (30% time drain, 400+
pages/week, <20% retention, 98% faster).

## Goal

Make the code, the deck, and the live demo tell one true story. Remove the unreachable
application. Turn the Study Desk into a real prompt box that searches the actual corpus.

## The prompt area

The Study Desk becomes a retrieval interface. A student types raw, unstructured text — "avl tree
rottaions", "how does dijkstra handle negative weights", "memoization vs tabulation" — and the
system matches it against 1,740 questions and 57 topic summaries using BM25, returning matching
questions with their difficulty and marks, the topic summary, and its flashcards. No API key. No
network. Deterministic, so a live demo cannot fail.

Fuzzy matching is mandatory, and the current implementation does not deliver it:

| Query token | Nearest corpus term | Similarity | Verdict |
|---|---|---|---|
| `rottaions` | `rotations` | 0.778 | works |
| `dinamic` | `dynamic` | 0.857 | works |
| `systm` | `system` | 0.833 | works |
| `prog` | `programming` | 0.364 | **fails** |
| `memo` | `memoization` | 0.364 | **fails** |
| `bfs` | `breadth` | 0.143 | **fails** |

`fast_fuzzy_similarity` is length-normalised Levenshtein, so abbreviations are punished. `RAGIndex`
additionally requires `sim > 0.8`, which rejects `rottaions` outright. Casual input — exactly the
"raw things" case — therefore returns nothing. Two fixes are required: a prefix/containment rule
ahead of the similarity threshold, and a lowered cutoff.


## Non-goals

- No new features beyond making the Study Desk real.
- No change to the 2-page UI's visual design, layout, or copy outside the Study Desk.
- No curriculum content additions. The 6 subjects and their topics stay as they are.
- No database migration or schema rewrite. Tables are left in place per explicit decision.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Rewrite deck to match shipped UI; delete the orphaned application | Judges read code. 28 unreachable endpoints contradicting the pitch is a liability. |
| D2 | Make the prompt area a BM25 retrieval interface over the real corpus | Restores the deck's flagship demo honestly, and is cheaper than building summarization. The data already exists; only the index is misaimed. |
| D3 | Keep `notebooks` and `submissions` tables | Explicit user decision. Avoids FK breakage in `generated_assignments`, `study_notes`, `submissions`. |
| D4 | Delete Socratic hints along with the grader | `get_progressive_hint` lived only in `grader.py`; the whole Help view goes. Nothing in the deck mentions Socratic tutoring. |
| D5 | Strip backend to only the routes the 2-page UI calls, plus the new search route | Aggressive per explicit user decision, and now justified by the query audit: it removes every raw-SQL bypass in the codebase. |
| D6 | Repoint `RAGIndex` at `question_bank` + `topic_content` + `interactive_content` | The index currently reads 84 chunks from empty tables while 1,740 questions go unsearched. |
| D7 | Retrieval only — no Gemini in the prompt path | A live demo must not depend on a network call or an API key. Gemini remains available via `is_gemini_available()` for the status endpoint only. |
| D8 | Add prefix matching and lower the fuzzy threshold | Length-normalised similarity fails abbreviations; `prog` and `memo` currently return nothing. Required for the "raw input" behaviour to hold. |
| D9 | Drop the summarizer salvage | Superseded by D2. `ocr_parser.py`'s text methods go with it. Retrieval is what the user asked for and what the corpus supports. |
| D10 | Delete `question_generator.py` and `question_bank_db.py` | Audit-verified: the 12 raw queries and the second schema source are both unreachable from the shipped UI. See "Query audit" below. |
| D11 | Remove the `init_question_bank` import from `database_init.py` in the same change | Hard dependency: `database_init.py` imports `question_bank_db`, so deleting that module without this edit breaks app startup. |

## Shipped product (ground truth for the deck)

**Landing page (`index.html`)** — three-phase methodology narrative: High-Yield Formulation →
Derivation Flashcards → 15-Question Curated Sets. Interactive Study Desk with preset chips
(Thermodynamics, OS Concurrency, DSA Recurrences), a textarea, and an Extract Study Kit action.
Six subject cards linking to `course.html?course=CODE`.

**Course page (`course.html`)** — semester/course/topic selectors; 15 curated questions with
difficulty filter and solution drawer; a quiz mode with answer selection, navigation, and scoring
that posts each result to `/api/activity/log`; KaTeX equation rendering throughout.

**Subjects:** CS201 Design & Analysis of Algorithms, CS203 Operating Systems, CS401 Artificial
Intelligence & Search, MA101 Engineering Mathematics I, CS402 Machine Learning, CS603 Distributed
Systems.

**Live endpoints the UI actually calls:**

| Endpoint | Purpose |
|---|---|
| `GET /api/questions/course/{code}` | 15-question curated set (+ `/refresh`, `/topic/{s}/{t}`) |
| `GET /api/content/{course_code}` | Study content by course, optional topic |
| `GET /api/interactive/{course_code}` | Concepts, formulas, flashcards |
| `POST /api/activity/log` | Quiz attempt telemetry |

**Supporting endpoints to retain:** `/api/curriculum`, `/api/curriculum/full`,
`/api/curriculum/year/{year}`, `/api/curriculum/{code}`, `/api/topics`, `/api/topics/search`,
`/api/system/status`, `/api/metadata`.

## Query audit

A read-only sweep of SQL placement across `src/backend/`, run to confirm the strip would not
leave data access scattered. Method: per-module counts of SELECT/INSERT/UPDATE/DELETE,
`execute()` calls, and connection constructors, then a reference sweep on every module that
imports a database symbol.

| Module | Verdict |
|---|---|
| `database.py` | Correct. 40 SELECT, 11 INSERT, 2 UPDATE, 2 DELETE, 81 `execute()`, all behind 40 `DatabaseRepo` static methods. The single data layer. |
| `app.py` | Clean. No SQL; route layer only. Its `get_connection` import is unused. |
| `curriculum.py`, `curriculum_data.py`, `curriculum_questions.py`, `study_content.py`, `ai_engine.py`, `web_question_engine.py` | Clean. Zero SQL — pure data and logic. `study_content.py` matched an initial `connect` scan only because the English word "connect" appears in its prose. |
| `question_generator.py` | **Violation.** 750 lines, 7 `get_connection()` calls, 12 raw queries against `question_bank` — a table `database.py` owns. Lines 636, 687, and 697 repeat the same fragile tri-state `subject` lookup (`subject = ?` OR a `curriculum` name/code subquery) as three copy-pasted blocks with no shared helper, so a fix must be made in three places or they drift. |
| `question_bank_db.py` | **Violation.** Owns DDL for 5 tables — a second schema source, reachable only via `database_init.py`. |
| `question_bank_api.py` L159 | **Dead stub.** `POST /generate/pyq-similar` imports `DatabaseRepo` inside the function body, calls `get_pyq_papers()` twice into unused locals, and ends in `# ... implementation` / `pass`. It returns `200` with a `null` body — a caller gets success and no data. |

**Reachability of the violations.** The 12 stray queries and both schema sources sit behind
routes the shipped UI never calls. Verified rather than assumed:

- `course.html` calls exactly one question endpoint: `/api/questions/course/{code}`.
- That handler calls `WebQuestionEngine.generate_questions()` directly.
- `web_question_engine.py` contains no SQL and no `QuestionGenerator` reference.
- A live call returned 15 questions, synthesized in memory from web research.

The `question_bank` table is therefore never read by the shipped product. Deleting
`question_generator.py` and `question_bank_db.py` removes every raw-SQL bypass in the codebase
and breaks nothing reachable.

**Ordering constraint.** `database_init.py` imports `init_question_bank` from
`question_bank_db.py`. That import must be removed in the same change that deletes the module,
or the application fails to import at startup (D11).

**Second schema source.** With `question_bank_db.py` gone, `question_bank` and its four sibling
tables are created only by the DDL already present in `database_init.py`. The table and its 1,740
rows are untouched, so the shipped data survives; only the duplicate DDL disappears. Any future
re-generation path must go through `DatabaseRepo`.

## Architecture

### Repointed: `src/backend/rag_engine.py`

`RAGIndex.rebuild_index()` currently reads notebooks, assignments, and PYQ papers. It is replaced
with three sources, all already populated:

1. **`question_bank`** — 1,740 rows. Each becomes a chunk whose text is
   `question_text + model answer`, tagged with subject, topic, difficulty, marks, and
   `question_type`. Search hits carry these as chips in the UI.
2. **`topic_content`** — 57 rows. Each becomes up to 3 chunks: summary, formulas, and the
   flashcard list. `key_points`, `examples`, and `viva_questions` are concatenated into the
   summary chunk.
3. **`interactive_content`** — 84 rows. Each becomes one chunk of `front_text` + `back_text`.

`notebooks`, `assignments`, and `pyq_papers` are dropped as sources per D5. Indexing runs once at
startup via the existing `get_instance()` singleton, and lazily on first search if the corpus
changed. Corpus size is ~1,900 chunks, so a full rebuild is a sub-second operation and needs no
persistence layer.

A new `SearchResult` dataclass replaces the ad-hoc dict, carrying `text`, `source_type`,
`title`, `subject`, `topic`, `difficulty`, `marks`, and `score`.

### Modified: matching behaviour

Two changes make raw input work. Both live in `RAGIndex.search()`, not in the C DLL, so the
native library stays untouched.

1. **Prefix/containment pass before the similarity threshold.** For each query token with no
   direct `doc_frequencies` hit, check the vocabulary for terms where
   `term.startswith(token)` or `token in term`. A prefix match of ≥3 characters counts as a full
   term hit. This makes `prog`→`programming`, `memo`→`memoization`, `bfs`→`breadth` work, and it
   is exact-match fast — the vocabulary is a few thousand terms, and only unmatched tokens trigger
   the scan.
2. **Threshold lowered from 0.8 to 0.62.** Measured values put real typos at 0.778–0.857 and
   unrelated terms far below 0.3, so 0.62 separates them cleanly while admitting `rottaions`.

The existing C `fast_batch_bm25` remains the scoring kernel, so the native-acceleration claim on
slide 5 stays true and is now actually load-bearing in the shipped product.

### Added: `GET /api/search`

```
GET /api/search?q=<raw text>&limit=<int, default 12>
  -> {"query": str, "total": int, "results": [SearchResult...],
      "topic_context": {subject, topic, summary, formulas, key_points, flashcards} | null}
```

`topic_context` is the highest-scoring `topic_content` row for the query, when one exists. It is
what makes a search feel like a study answer rather than a result list: the student gets both
"here are 12 matching questions" and "here is the topic summary they came from."

No database writes. No Gemini. A cold cache rebuilds the index inline.

### Modified: `src/backend/app.py`

**Add** the search route above. **Delete** 28 routes from `app.py`: all `/api/assignments*` (6),
`/api/pyq/*` (3), `/api/notebooks/*` (3), `/api/generator/*` (3), `/api/help/*` (3),
`/api/notes/*` (2), `/api/quiz/*` (4), `/api/chat/*` (2), `/api/progress` (2),
`/api/recommendations` (1). **Retain** in `app.py`: the 4 page-route decorators (2 handlers —
`/` + `/index.html` on `serve_index`, `/course.html` + `/course` on `serve_course`), the 8
supporting endpoints (`/api/system/status`, `/api/metadata`, `/api/curriculum`,
`/api/curriculum/full`, `/api/curriculum/year/{year}`, `/api/curriculum/{code}`, `/api/topics`,
`/api/topics/search`), and the 4 live data endpoints (`/api/content/{course_code}`,
`/api/content/{course_code}/{topic_name}`, `/api/interactive/{course_code}`,
`/api/activity/log`), plus the new `/api/search` = **18 decorators in `app.py`**, down from 46.

**In `question_bank_api.py`:** retain 6 of 12 — `/topics`, `/course/{course_code}`,
`/course/{course_code}/refresh`, `/refresh`, `/topic/{subject}/{topic}`, and `topic-stats` — and
delete the 6 generation routes. **Total: 24 routes retained, 34 removed, from 58 today.**

**Strip** unused imports: `UploadFile`, `File`, `shutil`, `NotebookParser`, `AssignmentGrader`,
`RAGIndex` (moves behind the search route only), and every engine whose sole consumer was a
deleted route. `RAGIndex` is retained — the search route needs it. `DatabaseRepo` stays for
curriculum/content queries.

`/api/system/status` drops `total_notebooks` and the RAG chunk count; the keys remain, returning
`0` and `0`, to preserve the response shape.

### Deleted files

`src/backend/ocr_parser.py`, `src/backend/grader.py`, `src/backend/assignment_gen.py`,
`src/backend/quiz_engine.py`, `src/backend/note_maker.py`, `src/backend/scraper.py`,
`src/backend/question_generator.py`, `src/backend/question_bank_db.py`, `src/static/js/app.js`,
`src/static/js/theme.js`, `src/static/css/styles.css`, `src/static/css/components.css`.

**`rag_engine.py` is retained and rewritten** — it was previously listed for deletion under the
OCR-grader scope, but it is the natural home for the corpus index. It loses its
`DatabaseRepo` dependency on deleted tables and gains query builders for the three real sources.

**Retained backend modules:** `app.py`, `database.py`, `database_init.py`, `curriculum.py`,
`curriculum_data.py`, `curriculum_questions.py`, `study_content.py`, `ai_engine.py`
(`is_gemini_available()` only), `question_bank_api.py`, `web_question_engine.py`, `rag_engine.py`
(rewritten), `c_core/*`.

**`question_bank_api.py` is retained but trimmed.** It keeps `/topics`, `/course/{code}`,
`/topic/{subject}/{topic}`, and the two refresh routes — the four that back the shipped UI. The
six generation routes (`/generate/similar`, `/generate/topic`, `/generate/pyq-similar`,
`/save-generated`, `/check-similarity`, `/regenerate-rejected`) are removed: all six exist only to
serve `QuestionGenerator`, and `/generate/pyq-similar` is additionally a dead stub returning
`200 null` (see Query audit). Removing them is what makes deleting `question_generator.py` safe
without leaving the dangling import at line 10. The `qgen = QuestionGenerator()` module-level
instantiation is removed with them.

**`database_init.py` is retained and modified** — the `init_question_bank` import is dropped
along with the `question_bank_db.py` deletion (D11). The `question_bank` DDL already present in
this module remains the sole schema source; no data is touched.

**Dependency note.** `Pillow` and `numpy` are imported by `ocr_parser.py` and `c_bridge.py`.
`preprocess_image_for_ocr` in `c_bridge.py` is a no-op grayscale stub used only by the deleted OCR
path, so its import is made lazy. `numpy`, `pypdf`, and `python-docx` become unused and are
dropped from `requirements.txt`. `Pillow` is retained for the lazy path.

**Route count after the change:** 18 in `app.py` + 6 in `question_bank_api.py` = **24 retained**,
down from 58 today.

### Modified: `src/static/templates/index.html`

Replace the body of `generateStudyKit()`:

1. Read and trim the textarea (or selected preset). Empty → inline error, no `alert()`.
2. `GET /api/search?q=<text>`.
3. Render three regions, reusing the existing card vocabulary:
   - **Matching questions** — question text, with difficulty and marks chips.
   - **Topic context** — the matched `topic_content` summary, formulas via `renderEquations()`,
     and key points.
   - **Flashcards** — from the matched `interactive_content` / `topic_content` flashcards, with
     the existing `flipCard()` interaction.
4. Empty result → an honest "no matches — try a topic like AVL, Dijkstra, or deadlocks" state.
5. Button shows a loading state and is disabled during the request.

`renderEquations()` already handles KaTeX, so stored LaTeX renders without new work.

**Note on the preset chips.** The three chips (Thermodynamics, OS Concurrency, DSA Recurrences)
call `loadSampleData(key, el)`, which injects a hardcoded `summaries` array from the in-file
`PRESETS` object — the same fake, for the same reason. `loadSampleData()` keeps only `text` and
`name`; the hardcoded `summaries` and `flashcards` arrays are deleted, and a chip click populates
the textarea and stops. Output comes only from the real search. This is what makes the acceptance
test meaningful: a preset and a typed query both flow through the identical real path.

### Modified: `requirements.txt`

Remove `pypdf`, `python-docx`, `numpy`. Keep `Pillow` (lazy-imported in `c_bridge.py`).

### Deleted: `tests/test_end_to_end.py` sections

The existing suite has 28 test methods across 8 classes. Four of those classes test modules this
design deletes: `TestQuizEngine`, `TestPYQSearch`, plus route tests inside `TestFastAPIRoutes` and
`TestDatabaseAndCurriculum` that hit `/api/quiz/*` and `/api/pyq/*`. `TestFrontendIntegrity` and
`TestCoursePageIntegrity` assert on `index.html` and `course.html` string content, including the
Study Desk markup.

The suite is rewritten to cover the retained surface: curriculum, content, interactive, questions,
activity log, and the new search endpoint. `TestFrontendIntegrity` is extended to assert that
`index.html` contains no hardcoded `PRESETS.summaries` and that `generateStudyKit` performs a
`fetch` — a regression guard against the fake returning. The Playwright E2E test is kept and
extended with a Study Desk case asserting that two different inputs produce two different kits.

### Rewritten: `studymorph-pitch-deck.html`

8 slides, same clay palette and JetBrains Mono so the visual identity is preserved. Content
rewritten to the ground truth above.

| Slide | Change |
|---|---|
| 1 Title & Vision | "OmniRoute AI Engine" → "BM25 retrieval over 1,740 verified questions" |
| 2 Problem | Replace 30% / 400+ / <20% figures with descriptive claims about exam prep |
| 3 Solution | Study Desk becomes the real prompt box; remove the "<2.5s via Multi-Model Processing Layer" claim |
| 4 Workflow | "Flask API Tokenizer" → FastAPI service layer; reflect the real BM25 pipeline |
| 5 Tech Stack | Tailwind → hand-written CSS; Flask → FastAPI + uvicorn; add the native C DLL as load-bearing |
| 6 Market Impact | Replace "98% Faster" with the 1,740 questions, 57 units, and 15-questions-per-set facts |
| 7 Roadmap | Phase 2 (PDF upload) is now impossible — it was OCR. Replace with unit expansion |
| 8 Conclusion | Unchanged structurally |

Slides 1, 3, and 5 change most, because the pitch moves from "AI summarises your notes" to
"BM25 search across the whole syllabus, typo-tolerant." That is a stronger claim than the fake
one, because it is true and measurable: 1,740 questions and 57 unit summaries, ranked natively.

Slide 7 needs particular care: "Direct PDF and document file uploads" describes the OCR feature
being deleted. It becomes expansion to more subjects and units.

## Data flow

```
Student types raw text (or picks a preset chip)
  → index.html GET /api/search?q=<raw text>
    → RAGIndex.search(query)
      → tokenize + stopword strip
      → for each token: direct df hit
                       → else prefix/containment match (≥3 chars)
                       → else fuzzy match (C, threshold 0.62)
      → fast_batch_bm25 scoring (native C)
      → rank, threshold 0.05, take top N
    → topic_context = best-scoring topic_content row
  ← JSON {results, topic_context}
  → render: question cards + topic summary + flashcards (KaTeX)
```

No database write. No Gemini. No network. The response is derived entirely from the 1,740-row
question bank and 57 topic summaries already in SQLite.

## Error handling

| Condition | Behaviour |
|---|---|
| Empty/whitespace query | 400 with a clear message; UI shows an inline error |
| Query with only stopwords | 400, "type a topic, concept, or question keyword" |
| No matches above threshold | 200 with empty `results`; UI shows the honest empty state naming example topics |
| Corpus empty (fresh DB) | Index rebuild yields 0 chunks; `/api/search` returns empty rather than raising |
| Native DLL absent | `c_bridge` already falls back to pure Python; unchanged |
| Gemini unreachable | Irrelevant — the search path never calls Gemini |

## Testing

0. **Import gate, run first.** `python -c "import src.backend.app"` must succeed after the strip.
   This is the specific check that catches D11's ordering constraint — a surviving
   `init_question_bank` import fails here and nowhere else.
1. `python -m unittest tests/test_end_to_end.py` — rewritten suite, must pass.
2. Manual: `python run.py`, then exercise the 4 live endpoints plus `/api/search`.
3. **Acceptance test for D2 — the prompt box must respond to raw input:**
   - `avl tree rottaions` → returns AVL questions (typo tolerated)
   - `prog` → returns programming questions (prefix match)
   - `memoization vs tabulation` → returns DP questions with a topic summary
   - `dijkstra negative weights` → returns graph questions
   - `zxcvqw nonsense` → honest empty state, no crash
4. **Acceptance test for the fake being gone:** two different queries return two visibly different
   result sets, and the response differs from the previously hardcoded output.
5. Playwright: load both pages, run a search, assert no console errors, assert two queries →
   two different result sets.
6. `TestFrontendIntegrity` extended to assert `index.html` contains no hardcoded `PRESETS.summaries`
   and that `generateStudyKit` performs a `fetch` — a regression guard against the fake returning.

## Risks

| Risk | Mitigation |
|---|---|
| Deleting 28 routes breaks something unforeseen | Full-repo import + reference sweep before each deletion group; run the suite after each group |
| `database_init.py` still imports `question_bank_db` after deletion | Startup fails loudly, not silently. Covered by acceptance test 0 and by D11 being a single change |
| `question_bank_api.py` retains a dangling `QuestionGenerator` import | The six generation routes and the `qgen` instantiation are removed in the same edit (D10) |
| `c_bridge.py` lazy Pillow import breaks a caller | `preprocess_image_for_ocr` has one caller, in the deleted OCR path. Verify by import test |
| Raw input returns nothing for common abbreviations | Prefix/containment pass plus a 0.62 threshold, verified by acceptance tests 3a–3e against the live corpus |
| Deck claims drift from code again | Every deck fact traced to a file path or endpoint in this spec |
| A future contributor re-adds raw SQL beside `DatabaseRepo` | The audit is recorded in this spec as the reference; `DatabaseRepo` is the documented single data layer |

## Out of scope

Deleting the `notebooks` and `submissions` tables (D3), adding curriculum content, redesigning the
UI, adding user accounts, and the `brag-output/` video assets.
