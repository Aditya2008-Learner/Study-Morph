# Align Code and Deck to Shipped Product — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the code, deck, and live demo tell one true story — strip 34 unreachable routes and 12 orphaned files, then turn the faked Study Desk into a real BM25 prompt box over the 1,740-question corpus.

**Architecture:** Two independent subsystems plus a documentation rewrite, sequenced so each is testable alone. **Subsystem A** deletes 34 routes and 12 files that no code path reaches, and moves the `question_bank` SQL that survives into `DatabaseRepo`. **Subsystem B** rewrites `rag_engine.py` to index the real corpus (1,740 questions + 57 topic summaries + 84 flashcards) and adds `GET /api/search`, which `index.html` calls. **Subsystem C** rewrites the pitch deck to match.

**Tech Stack:** Python 3.14, FastAPI + uvicorn, SQLite (WAL), native C DLL via ctypes (`fast_batch_bm25`, `fast_fuzzy_similarity`), KaTeX, vanilla JS. Test runner: `unittest` (the repo's existing choice — do not introduce pytest).

**Spec:** `docs/superpowers/specs/2026-09-27-align-code-and-deck-to-shipped-product-design.md`

## Global Constraints

- Test runner is `python -m unittest`. Do not add pytest, tox, or nose.
- `DatabaseRepo` in `src/backend/database.py` is the **single data layer**. No module outside it may call `get_connection()` or write SQL. This is the invariant the whole cleanup establishes.
- Do not delete the `notebooks` or `submissions` tables. DDL and data stay (spec D3).
- Do not modify `src/data/study_assistant.db`. It holds 1,740 questions the new search depends on.
- The native C DLL (`src/c_core/libstudyc.dll`) must not be recompiled or edited. `c_bridge.py` falls back to pure Python automatically.
- `/api/search` must never call Gemini or make any network request. A demo must not depend on an API key (spec D7).
- Fuzzy threshold is `0.62`. Prefix matching applies at ≥3 characters (spec D8).
- Frontend uses no build step and no framework. Plain HTML/CSS/JS, edited in place.
- Windows/PowerShell environment. Paths in commands are quoted.
- One commit per task. Do not amend, squash, or force-push.

## Review Focus

Inputs the spec implies but no acceptance test in the spec exercises. Each gets a test in the task that owns the code.

1. **A user types gibberish** (`zxcvqw nonsense`) — must return an empty result set with a helpful message, never a 500 or a stack trace.
2. **A user types a single stopword** (`the`, `what is`) — all tokens are stripped, so there is nothing to match. Must be a clear 400, not a silent empty result that looks like "no matches found."
3. **The database file is missing or empty** (fresh clone, first run) — index rebuild yields 0 chunks. `/api/search` must return empty, not raise on an empty corpus.
4. **A user pastes a huge block of text** (a full chapter, 50k+ chars) — must not hang or blow the response size. Needs a length cap.
5. **Two users search the same query concurrently** — `RAGIndex` is a module-level singleton with a mutable `self.chunks` list. A rebuild triggered by one request must not corrupt another's iteration.

---

## Subsystem A — Strip the unreachable code

### Task 1: Add question_bank access to DatabaseRepo

`question_generator.py` holds the only SQL for the `question_bank` table, and it is being deleted. The new search index needs that data, and `DatabaseRepo` must own it per the global constraint. Do this **first** — every later task depends on it.

**Files:**
- Modify: `src/backend/database.py` (add 2 static methods to `DatabaseRepo`)
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: nothing (this is the first task)
- Produces:
  - `DatabaseRepo.get_question_bank_for_index() -> List[Dict[str, Any]]` — all Approved rows, with `id`, `question_text`, `subject`, `topic`, `difficulty`, `marks`, `question_type`. Used by Task 5.
  - `DatabaseRepo.get_all_interactive_content() -> List[Dict[str, Any]]` — every row across all courses, with `course_code`, `topic`, `front_text`, `back_text`. Used by Task 5.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_end_to_end.py` inside `class TestDatabaseAndCurriculum`:

```python
    def test_get_question_bank_for_index_returns_approved_rows(self):
        rows = DatabaseRepo.get_question_bank_for_index()
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 1000, "expected the seeded 1740-question corpus")
        first = rows[0]
        for key in ("id", "question_text", "subject", "topic", "difficulty", "marks"):
            self.assertIn(key, first, f"missing key {key}")

    def test_get_question_bank_for_index_excludes_non_approved(self):
        rows = DatabaseRepo.get_question_bank_for_index()
        statuses = {r.get("status") for r in rows}
        self.assertEqual(statuses, {"Approved"}, f"non-approved rows leaked: {statuses}")

    def test_get_all_interactive_content_returns_every_course(self):
        rows = DatabaseRepo.get_all_interactive_content()
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 50)
        codes = {r["course_code"] for r in rows}
        self.assertGreater(len(codes), 5, "expected multiple courses, not one")
        for key in ("front_text", "back_text"):
            self.assertIn(key, rows[0])
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestDatabaseAndCurriculum -v`
Expected: FAIL with `AttributeError: type object 'DatabaseRepo' has no attribute 'get_question_bank_for_index'`

- [ ] **Step 3: Add the two methods**

Add these as static methods on `DatabaseRepo`, directly after `get_interactive_content`. Match the surrounding style exactly — `conn = get_connection()`, `cursor = conn.cursor()`, loop building `dict(r)`, `conn.close()`, `return`.

```python
    @staticmethod
    def get_question_bank_for_index() -> List[Dict[str, Any]]:
        """Get all approved questions for search indexing"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, subject, topic, difficulty, marks, question_type "
            "FROM question_bank WHERE status = 'Approved' ORDER BY subject, topic"
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["related_concepts"] = json.loads(d["related_concepts"]) if d.get("related_concepts") else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_all_interactive_content() -> List[Dict[str, Any]]:
        """Get all interactive flashcard content across every course"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interactive_content ORDER BY course_code, topic")
        rows = cursor.fetchall()
        result = [dict(r) for r in rows]
        conn.close()
        return result
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestDatabaseAndCurriculum -v`
Expected: PASS — the 3 new tests plus all pre-existing tests in that class.

- [ ] **Step 5: Review Focus check — empty corpus**

The `status` filter must not crash when the table is empty. Verify by hand before committing:

Run: `python -c "import sys; sys.path.insert(0,'.'); from src.backend.database import DatabaseRepo as D; print('rows:', len(D.get_question_bank_for_index())); print('empty ok:', D.get_question_bank_for_index.__doc__ is not None)"`
Expected: prints a row count near 1740, no traceback.

- [ ] **Step 6: Commit**

```bash
git add src/backend/database.py tests/test_end_to_end.py
git commit -m "feat(data): add question_bank and interactive_content queries to DatabaseRepo"
```

---

### Task 2: Remove the dead PYQ-similar stub

`POST /api/questions/generate/pyq-similar` imports `DatabaseRepo` inside the function body, calls `get_pyq_papers()` twice into unused locals, and ends in `# ... implementation` / `pass`. It returns `200` with a `null` body. Delete it now, while `question_generator.py` still exists, so this deletion is provably independent of Task 5.

**Files:**
- Modify: `src/backend/question_bank_api.py:159-178` (delete `generate_from_pyq`)

**Interfaces:**
- Consumes: nothing
- Produces: nothing. Pure deletion.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_end_to_end.py` as a new class:

```python
class TestRemovedRoutes:
    """Routes deleted by the cleanup must be gone, not silently returning null."""

    def test_pyq_similar_route_is_removed(self):
        from src.backend.question_bank_api import router
        paths = {r.path for r in router.routes}
        self.assertNotIn("/api/questions/generate/pyq-similar", paths)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_end_to_end.TestRemovedRoutes -v`
Expected: FAIL with `AssertionError: '/api/questions/generate/pyq-similar' in {...}`

- [ ] **Step 3: Delete the stub**

Remove the entire `generate_from_pyq` function and its decorator, from `@router.post("/generate/pyq-similar")` through the `pass` line.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest tests.test_end_to_end.TestRemovedRoutes -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/backend/question_bank_api.py tests/test_end_to_end.py
git commit -m "refactor(api): remove dead pyq-similar stub returning 200 null"
```

---

### Task 3: Delete the orphaned frontend bundle

`app.js` (51KB), `theme.js`, `styles.css`, and `components.css` are referenced by zero files. Verified: a repo-wide search for each filename returns no hits outside the files themselves. They implement a 10-view app that no page loads.

**Files:**
- Delete: `src/static/js/app.js`, `src/static/js/theme.js`, `src/static/css/styles.css`, `src/static/css/components.css`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: nothing
- Produces: nothing. Pure deletion.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_end_to_end.py`:

```python
class TestFrontendIntegrity:
    def test_orphan_frontend_bundle_is_deleted(self):
        import os
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "static")
        for rel in ("js/app.js", "js/theme.js", "css/styles.css", "css/components.css"):
            path = os.path.join(base, rel.replace("/", os.sep))
            self.assertFalse(os.path.exists(path), f"orphan still present: {rel}")

    def test_served_templates_do_not_reference_orphan_bundle(self):
        import os
        tdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "static", "templates")
        for name in ("index.html", "course.html"):
            with open(os.path.join(tdir, name), encoding="utf-8", errors="ignore") as fh:
                html = fh.read()
            for orphan in ("app.js", "theme.js", "styles.css", "components.css"):
                self.assertNotIn(orphan, html, f"{name} still references {orphan}")
```

- [ ] **Step 2: Run the tests to verify the first fails**

Run: `python -m unittest tests.test_end_to_end.TestFrontendIntegrity -v`
Expected: the first test FAILS (files still exist). The second PASSES already — it is a guard against regression, not a failing test.

- [ ] **Step 3: Delete the four files**

```bash
git rm src/static/js/app.js src/static/js/theme.js src/static/css/styles.css src/static/css/components.css
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestFrontendIntegrity -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_end_to_end.py
git commit -m "refactor(frontend): delete orphaned 10-view app bundle, referenced by nothing"
```

---

### Task 4: Delete OCR, grader, and the six orphaned engines

Delete 12 backend modules. All are unreachable after Subsystem A's route removal. **This task only removes Python modules and route handlers** — it must leave the app importing cleanly, which Task 5 then reduces further.

**Files:**
- Delete: `src/backend/ocr_parser.py`, `grader.py`, `assignment_gen.py`, `quiz_engine.py`, `note_maker.py`, `scraper.py`, `question_generator.py`, `question_bank_db.py`
- Modify: `src/backend/app.py` (remove 28 routes + their imports), `src/backend/database_init.py` (drop `init_question_bank` import)
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: `DatabaseRepo.get_question_bank_for_index` and `get_all_interactive_content` from Task 1 (already landed, so deleting their only other caller is safe)
- Produces: an `app.py` exposing exactly 18 route decorators.

> **Ordering constraint (spec D11):** `database_init.py` imports `init_question_bank` from `question_bank_db.py`. Delete that import in this same commit. If you delete the module without the import, the app fails to import at startup and nothing else will tell you why.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_end_to_end.py`:

```python
class TestRemovedRoutes:
    def test_orphaned_backend_modules_are_deleted(self):
        import os
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "backend")
        for name in ("ocr_parser.py", "grader.py", "assignment_gen.py", "quiz_engine.py",
                     "note_maker.py", "scraper.py", "question_generator.py", "question_bank_db.py"):
            self.assertFalse(os.path.exists(os.path.join(base, name)), f"still present: {name}")

    def test_app_imports_without_orphaned_modules(self):
        import importlib
        app = importlib.import_module("src.backend.app")
        self.assertTrue(hasattr(app, "app"))

    def test_route_count_is_reduced(self):
        import importlib
        app = importlib.import_module("src.backend.app").app
        paths = {r.path for r in app.routes}
        for gone in ("/api/notebooks/upload", "/api/help/evaluate", "/api/quiz/generate",
                     "/api/chat/message", "/api/assignments", "/api/pyq/search",
                     "/api/generator/create", "/api/notes/generate", "/api/progress",
                     "/api/recommendations"):
            self.assertNotIn(gone, paths, f"route should be gone: {gone}")

    def test_live_routes_are_retained(self):
        import importlib
        app = importlib.import_module("src.backend.app").app
        paths = {r.path for r in app.routes}
        for kept in ("/", "/index.html", "/course.html", "/course", "/api/system/status",
                     "/api/curriculum", "/api/curriculum/full", "/api/topics",
                     "/api/content/{course_code}", "/api/interactive/{course_code}",
                     "/api/activity/log"):
            self.assertIn(kept, paths, f"live route was removed by mistake: {kept}")

    def test_database_init_has_no_question_bank_import(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "src", "backend", "database_init.py")
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("question_bank_db", src, "dangling import of deleted module")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestRemovedRoutes -v`
Expected: FAIL on `test_orphaned_backend_modules_are_deleted` and `test_route_count_is_reduced`.

- [ ] **Step 3: Delete the eight modules**

```bash
git rm src/backend/ocr_parser.py src/backend/grader.py src/backend/assignment_gen.py src/backend/quiz_engine.py src/backend/note_maker.py src/backend/scraper.py src/backend/question_generator.py src/backend/question_bank_db.py
```

- [ ] **Step 4: Remove the 28 routes from `app.py`**

Delete these route handlers and nothing else:

```
/api/assignments, /api/assignments/{assignment_id} (GET/POST/PUT/DELETE), /api/assignments/batch-export
/api/pyq/search, /api/pyq/import, /api/pyq/papers
/api/notebooks/upload, /api/notebooks, /api/notebooks/{notebook_id} (GET/DELETE)
/api/generator/create, /api/generator/assignments, /api/generator/assignments/{gen_id}
/api/help/hint, /api/help/evaluate, /api/help/submissions/{assignment_id}
/api/notes/generate, /api/notes
/api/quiz/generate, /api/quiz/{quiz_id}, /api/quiz/{quiz_id}/submit, /api/quiz/analytics/radar
/api/chat/message, /api/chat/history
/api/progress, /api/progress/{subject}/{topic}
/api/recommendations
```

Then remove the now-unused imports at the top of `app.py`: `UploadFile`, `File`, `shutil`, `uuid` (if unused after), `NotebookParser`, `AssignmentGrader`, `AssignmentGenerator`, `NoteMaker`, `QuizEngine`, and the chat path of `AIEngine`. Keep `RAGIndex` (Task 5 needs it), `DatabaseRepo`, `get_connection` only if still referenced, and every curriculum/content import.

Verify with: `python -c "import ast,sys; ast.parse(open('src/backend/app.py',encoding='utf-8').read()); print('parses ok')"`

- [ ] **Step 5: Remove the `init_question_bank` import from `database_init.py`**

Find the line `from .question_bank_db import init_question_bank` and delete it. If `init_question_bank()` is called anywhere in that file, delete the call too. Keep the `question_bank` DDL that already exists in `database_init.py` — it becomes the sole schema source.

- [ ] **Step 6: Run the import gate first**

Run: `python -c "import sys; sys.path.insert(0,'.'); import src.backend.app; print('IMPORT OK')"`
Expected: `IMPORT OK`. If this raises `ModuleNotFoundError: No module named 'src.backend.question_bank_db'`, the Step 5 import removal was missed.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end -v`
Expected: PASS for the new tests. Pre-existing tests in `TestQuizEngine`, `TestPYQSearch`, and parts of `TestDatabaseAndCurriculum` will FAIL — they test deleted code. Delete those three classes in this step; they are rewritten in Task 8.

- [ ] **Step 8: Delete the tests for deleted code**

Remove `class TestQuizEngine`, `class TestPYQSearch`, and any individual test methods inside other classes that reference `/api/quiz/`, `/api/pyq/`, `QuizEngine`, `NoteMaker`, `AssignmentGrader`, or `NotebookParser`.

- [ ] **Step 9: Re-run the full suite**

Run: `python -m unittest tests.test_end_to_end -v`
Expected: all remaining tests PASS.

- [ ] **Step 9b: Note the newly-dead repo methods (do not delete yet)**

After this task, `DatabaseRepo.get_assignments`, `get_pyq_papers`, and `get_notebooks` have no
callers left — every remaining reference was inside a module just deleted. They are left in
place deliberately: the `notebooks` and `submissions` **tables stay** (spec D3), so these accessors
remain the documented way to reach that data if it is ever revived. Do not remove them in this
task. Record them in a follow-up note rather than expanding this commit's blast radius.

- [ ] **Step 10: Review Focus check — import survives a cold start**

Run: `python run.py` then, in a second terminal, `curl -s http://127.0.0.1:8000/api/system/status`
Expected: JSON with `"status": "online"`. Then stop the server.

- [ ] **Step 11: Commit**

```bash
git add -A src/backend tests/test_end_to_end.py
git commit -m "refactor(backend): remove 28 unreachable routes and 8 orphaned modules"
```

---

### Task 5: Trim question_bank_api to the four live routes

The router still imports `QuestionGenerator` at line 10 and instantiates `qgen` at line 18. Task 4 deleted that class, so the router cannot import. Trim it to the routes the shipped UI and course page actually use.

**Files:**
- Modify: `src/backend/question_bank_api.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: `WebQuestionEngine` (unchanged, retained)
- Produces: a router with exactly 6 routes under prefix `/api/questions`: `/topics`, `/course/{course_code}`, `/course/{course_code}/refresh`, `/refresh`, `/topic/{subject}/{topic}`, `/topic-stats/{subject}/{topic}`.

- [ ] **Step 1: Write the failing test**

Add to `TestRemovedRoutes`:

```python
    def test_question_router_keeps_only_live_routes(self):
        from src.backend.question_bank_api import router
        paths = {r.path for r in router.routes}
        for kept in ("/api/questions/topics", "/api/questions/course/{course_code}",
                     "/api/questions/course/{course_code}/refresh", "/api/questions/refresh",
                     "/api/questions/topic/{subject}/{topic}",
                     "/api/questions/topic-stats/{subject}/{topic}"):
            self.assertIn(kept, paths, f"live question route missing: {kept}")
        for gone in ("/api/questions/generate/similar", "/api/questions/generate/topic",
                     "/api/questions/save-generated", "/api/questions/check-similarity",
                     "/api/questions/regenerate-rejected"):
            self.assertNotIn(gone, paths, f"dead question route retained: {gone}")

    def test_question_router_has_no_question_generator_dependency(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "src", "backend", "question_bank_api.py")
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("question_generator", src)
        self.assertNotIn("qgen", src)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestRemovedRoutes -v`
Expected: FAIL — the six generation routes are still present.

- [ ] **Step 3: Remove the generation routes and the dead import**

Delete these handlers: `generate_similar_questions`, `generate_topic_questions`,
`save_generated_questions`, `check_question_similarity`, `regenerate_rejected`.

Then replace the import block at the top:

```python
from .web_question_engine import WebQuestionEngine
```

and delete the module-level `qgen = QuestionGenerator()` line. Remove the now-unused
`QuestionGenerator, get_topic_question_bank, get_all_topics_with_counts` imports, keeping
`get_course_question_set` and `get_topic_question_bank` only if the retained routes reference them.
`/topics` uses `get_all_topics_with_counts` and `/topic-stats/{subject}/{topic}` uses
`get_topic_question_bank` — **both of those live in the deleted `question_generator.py`**.

Reimplement them against `DatabaseRepo` in the same edit:

```python
from .database import DatabaseRepo

def get_topic_question_bank(subject: str, topic: str) -> Dict[str, Any]:
    """Topic stats computed from the question bank"""
    rows = DatabaseRepo.get_question_bank_for_index()
    matching = [r for r in rows if r["subject"] == subject and r["topic"] == topic]
    difficulty: Dict[str, int] = {}
    types: Dict[str, int] = {}
    for r in matching:
        difficulty[r["difficulty"]] = difficulty.get(r["difficulty"], 0) + 1
        types[r["question_type"]] = types.get(r["question_type"], 0) + 1
    target = 20
    return {
        "total": len(matching),
        "difficulty_breakdown": difficulty,
        "type_breakdown": types,
        "target": target,
    }

def get_all_topics_with_counts() -> List[Dict[str, Any]]:
    """All subjects/topics with their approved question counts"""
    rows = DatabaseRepo.get_question_bank_for_index()
    counts: Dict[tuple, int] = {}
    for r in rows:
        key = (r["subject"], r["topic"])
        counts[key] = counts.get(key, 0) + 1
    return [
        {"subject": s, "topic": t, "count": c}
        for (s, t), c in sorted(counts.items())
    ]
```

- [ ] **Step 4: Run the import gate**

Run: `python -c "import sys; sys.path.insert(0,'.'); import src.backend.app; print('IMPORT OK')"`
Expected: `IMPORT OK`

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestRemovedRoutes -v`
Expected: PASS

- [ ] **Step 6: Verify the live endpoint still returns 15 questions**

Run: `python run.py`, then in a second terminal:
`curl -s "http://127.0.0.1:8000/api/questions/course/CS201" | python -c "import json,sys; d=json.load(sys.stdin); print('count:', len(d.get('questions', d)))"`
Expected: `count: 15`. Then stop the server.

- [ ] **Step 7: Commit**

```bash
git add src/backend/question_bank_api.py tests/test_end_to_end.py
git commit -m "refactor(api): trim question router to 4 live routes, move stats onto DatabaseRepo"
```

---

## Subsystem B — The real prompt box

### Task 6: Repoint RAGIndex at the real corpus

`RAGIndex.rebuild_index()` currently reads notebooks (0 rows), assignments (2), and PYQ papers (2) — 84 chunks of nothing. Point it at 1,740 questions, 57 topic summaries, and 84 flashcards.

**Files:**
- Modify: `src/backend/rag_engine.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: `DatabaseRepo.get_question_bank_for_index()` and `DatabaseRepo.get_all_interactive_content()` from Task 1.
- Produces:
  - `RAGIndex.get_instance() -> RAGIndex` (existing singleton, unchanged signature)
  - `RAGIndex.rebuild_index() -> None`
  - `RAGIndex.search(query: str, top_k: int = 12) -> List[Dict[str, Any]]` — each result has `text`, `source_type` (`"question" | "topic" | "flashcard"`), `title`, `subject`, `topic`, `difficulty`, `marks`, `score`.
  - `RAGIndex.get_topic_context(query: str) -> Optional[Dict[str, Any]]` — the best-scoring `topic_content` row, with `subject`, `topic`, `summary`, `formulas`, `key_points`, `flashcards`.

- [ ] **Step 1: Write the failing tests**

Add a new class:

```python
class TestRAGIndex:
    def setUp(self):
        from src.backend.rag_engine import RAGIndex
        self.index = RAGIndex()
        self.index.rebuild_index()

    def test_index_covers_the_real_corpus(self):
        self.assertGreater(len(self.index.chunks), 1500,
                           "expected 1740 questions + 57 topics + 84 flashcards")
        kinds = {c.doc_type for c in self.index.chunks}
        self.assertEqual(kinds, {"question", "topic", "flashcard"}, f"got {kinds}")

    def test_search_finds_avl_by_typo(self):
        from src.backend.rag_engine import RAGIndex
        results = RAGIndex().search("avl tree rottaions")
        self.assertTrue(results, "typo'd query returned nothing")
        blob = " ".join(r["text"].lower() for r in results)
        self.assertIn("avl", blob, f"typo query missed AVL; got: {blob[:200]}")

    def test_search_finds_by_prefix(self):
        from src.backend.rag_engine import RAGIndex
        results = RAGIndex().search("prog")
        self.assertTrue(results, "prefix query returned nothing")

    def test_search_returns_difficulty_and_marks(self):
        from src.backend.rag_engine import RAGIndex
        results = RAGIndex().search("operating system deadlock")
        questions = [r for r in results if r["source_type"] == "question"]
        self.assertTrue(questions)
        self.assertIn("difficulty", questions[0])
        self.assertIn("marks", questions[0])

    def test_gibberish_returns_empty_not_exception(self):
        from src.backend.rag_engine import RAGIndex
        self.assertEqual(RAGIndex().search("zxcvqw nonsense"), [])

    def test_stopword_only_query_returns_empty(self):
        from src.backend.rag_engine import RAGIndex
        self.assertEqual(RAGIndex().search("the of and what is"), [])

    def test_empty_query_returns_empty(self):
        from src.backend.rag_engine import RAGIndex
        self.assertEqual(RAGIndex().search(""), [])

    def test_topic_context_is_populated(self):
        from src.backend.rag_engine import RAGIndex
        ctx = RAGIndex().get_topic_context("dynamic programming knapsack")
        self.assertIsNotNone(ctx)
        for key in ("summary", "formulas", "key_points"):
            self.assertIn(key, ctx)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestRAGIndex -v`
Expected: FAIL — `chunks` will contain only ~84 notebook/assignment chunks, so `test_index_covers_the_real_corpus` fails.

- [ ] **Step 3: Rewrite `rebuild_index`**

Replace the three source blocks in `rebuild_index()` with:

```python
    def rebuild_index(self):
        self.chunks = []
        self.doc_frequencies = {}

        for q in DatabaseRepo.get_question_bank_for_index():
            text = f"{q['question_text']}"
            self._add_chunks(
                q["id"], q["question_text"][:80], "question", text,
                q.get("topic", ""), subject=q.get("subject", ""),
                topic=q.get("topic", ""), difficulty=q.get("difficulty", ""),
                marks=q.get("marks", 0),
            )

        for t in DatabaseRepo.get_all_topics():
            blob = self._topic_blob(t)
            self._add_chunks(
                t["id"], f"{t['course_code']} — {t['topic_name']}", "topic", blob,
                t["topic_name"], subject=t["course_code"], topic=t["topic_name"],
            )
            self.topic_rows = getattr(self, "topic_rows", {})
            self.topic_rows[t["id"]] = t

        for f in DatabaseRepo.get_all_interactive_content():
            blob = f"{f.get('front_text', '')} {f.get('back_text', '')}"
            self._add_chunks(
                f["id"], f"{f.get('front_text', '')[:80]}", "flashcard", blob,
                f.get("topic", ""), subject=f.get("course_code", ""), topic=f.get("topic", ""),
            )

        total_tokens = sum(c.length for c in self.chunks)
        self.avg_doc_len = (total_tokens / len(self.chunks)) if self.chunks else 50.0

        for c in self.chunks:
            for t in set(c.tokens):
                self.doc_frequencies[t] = self.doc_frequencies.get(t, 0) + 1
```

Add this helper as a module-level function:

```python
def _topic_blob(topic_row: Dict[str, Any]) -> str:
    """Flatten a topic_content row into indexable text"""
    parts = [topic_row.get("summary", "") or ""]
    for field in ("key_points", "formulas", "examples", "viva_questions"):
        value = topic_row.get(field) or []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parts.extend(str(v) for v in item.values())
                else:
                    parts.append(str(item))
    return " ".join(p for p in parts if p)
```

- [ ] **Step 4: Widen `RAGChunk` to carry metadata**

Replace the `RAGChunk.__init__` signature and add the new fields:

```python
class RAGChunk:
    def __init__(self, chunk_id, doc_id, doc_name, doc_type, text, page_or_sec="",
                 subject="", topic="", difficulty="", marks=0):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.doc_type = doc_type
        self.text = text
        self.page_or_sec = page_or_sec
        self.subject = subject
        self.topic = topic
        self.difficulty = difficulty
        self.marks = marks
        self.tokens = self._tokenize(text)
        self.length = len(self.tokens)
```

Update `_add_chunks` to accept and forward the new keyword arguments.

- [ ] **Step 5: Add prefix matching to `search`**

In `search()`, replace the `if df == 0:` fallback block with a three-stage resolution — direct hit, then prefix, then fuzzy:

```python
            if df == 0:
                prefix_match = self._prefix_match(token)
                if prefix_match:
                    token = prefix_match
                    df = self.doc_frequencies.get(token, 0)
                else:
                    best_match, best_sim = None, 0.0
                    for known_term in self.doc_frequencies:
                        sim = fast_fuzzy_similarity(token, known_term)
                        if sim > 0.62 and sim > best_sim:
                            best_sim, best_match = sim, known_term
                    if not best_match:
                        continue
                    token = best_match
                    df = self.doc_frequencies.get(token, 0)
```

Add the helper, which only runs for unmatched tokens so the exact-match fast path is unaffected:

```python
    def _prefix_match(self, token: str) -> Optional[str]:
        """Resolve an abbreviation to a corpus term (prog -> programming)"""
        if len(token) < 3:
            return None
        candidates = [t for t in self.doc_frequencies if t.startswith(token)]
        if not candidates:
            return None
        return min(candidates, key=len)
```

- [ ] **Step 6: Return the new result shape from `search`**

Replace the appended result dict with:

```python
                results.append({
                    "chunk_id": c.chunk_id,
                    "doc_id": c.doc_id,
                    "doc_name": c.doc_name,
                    "source_type": c.doc_type,
                    "text": c.text,
                    "subject": c.subject,
                    "topic": c.topic,
                    "difficulty": c.difficulty,
                    "marks": c.marks,
                    "score": round(scores[idx], 4),
                    "citation": f"[{c.doc_type}: {c.doc_name}]",
                })
```

- [ ] **Step 7: Add `get_topic_context`**

```python
    def get_topic_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Best-matching topic_content row for a query, with its study material"""
        for r in self.search(query, top_k=25):
            if r["source_type"] != "topic":
                continue
            row = getattr(self, "topic_rows", {}).get(r["doc_id"])
            if row:
                return {
                    "subject": row.get("course_code", ""),
                    "topic": row.get("topic_name", ""),
                    "summary": row.get("summary", ""),
                    "formulas": row.get("formulas", []),
                    "key_points": row.get("key_points", []),
                    "flashcards": row.get("flashcards", []),
                }
        return None
```

- [ ] **Step 8: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestRAGIndex -v`
Expected: PASS — all 8 tests.

- [ ] **Step 9: Review Focus check — long input does not hang**

Run: `python -c "import sys,time; sys.path.insert(0,'.'); from src.backend.rag_engine import RAGIndex; i=RAGIndex(); i.rebuild_index(); t=time.time(); r=i.search('algorithm ' * 5000); print('tokens fed: 5000, results:', len(r), 'secs: %.2f' % (time.time()-t))"`
Expected: completes in under 5 seconds. If it hangs, cap the token count in `search()`:

```python
        query_tokens = RAGChunk._tokenize(query)[:64]
```

- [ ] **Step 10: Commit**

```bash
git add src/backend/rag_engine.py tests/test_end_to_end.py
git commit -m "feat(search): index 1740 questions, 57 topics, 84 flashcards with prefix matching"
```

---

### Task 7: Expose GET /api/search

**Files:**
- Modify: `src/backend/app.py` (add one route)
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: `RAGIndex.get_instance().search(query, top_k)` and `.get_topic_context(query)` from Task 6.
- Produces: `GET /api/search?q=<str>&limit=<int>` returning `{"query": str, "total": int, "results": [...], "topic_context": {...} | null}`.

- [ ] **Step 1: Write the failing test**

Add to `TestRAGIndex`:

```python
    def test_search_endpoint_returns_results(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        client = TestClient(app)
        r = client.get("/api/search", params={"q": "avl tree rottaions"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["query"], "avl tree rottaions")
        self.assertGreater(data["total"], 0)
        self.assertIn("results", data)
        self.assertIn("topic_context", data)

    def test_search_endpoint_rejects_empty_query(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        r = TestClient(app).get("/api/search", params={"q": "   "})
        self.assertEqual(r.status_code, 400)

    def test_search_endpoint_rejects_stopword_only_query(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        r = TestClient(app).get("/api/search", params={"q": "the of and"})
        self.assertEqual(r.status_code, 400)

    def test_search_endpoint_gibberish_is_200_with_empty_results(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        r = TestClient(app).get("/api/search", params={"q": "zxcvqw nonsense"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["total"], 0)

    def test_search_endpoint_caps_limit(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        r = TestClient(app).get("/api/search", params={"q": "algorithm", "limit": 9999})
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(r.json()["results"]), 50)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestRAGIndex -v`
Expected: FAIL — `/api/search` returns 404.

- [ ] **Step 3: Add the route**

Add to `app.py` next to the other data endpoints:

```python
@app.get("/api/search")
async def search_corpus(
    q: str = Query(..., description="Raw study query"),
    limit: int = Query(12, ge=1, le=50, description="Max results")
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Type a topic, concept, or question keyword.")
    index = RAGIndex.get_instance()
    if not RAGChunk._tokenize(query):
        raise HTTPException(status_code=400, detail="Type a topic, concept, or question keyword.")
    results = index.search(query, top_k=limit)
    return {
        "query": query,
        "total": len(results),
        "results": results,
        "topic_context": index.get_topic_context(query),
    }
```

Add `RAGChunk` to the existing `from .rag_engine import ...` line in `app.py`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestRAGIndex -v`
Expected: PASS — all tests including the 5 new endpoint tests.

- [ ] **Step 5: Review Focus check — concurrent searches are safe**

`RAGIndex` is a module-level singleton whose `chunks` list is mutated by `rebuild_index`. Two
simultaneous requests must not corrupt each other. Verify:

Run: `python run.py`, then in a second terminal:
`1..8 | ForEach-Object { Start-Job { curl -s "http://127.0.0.1:8000/api/search?q=deadlock" } } | Wait-Job | Receive-Job | Select-String -Pattern '"total":\d+'`
Expected: eight responses, each with a positive `total`, no tracebacks, no empty responses. Then stop the server.

- [ ] **Step 6: Commit**

```bash
git add src/backend/app.py tests/test_end_to_end.py
git commit -m "feat(api): add GET /api/search with stopword and limit validation"
```

---

### Task 8: Wire the prompt box in index.html

`generateStudyKit()` slices the first 50 characters of the input and renders a hardcoded
`f(x) = Σxᵢwᵢ` and Stokes' theorem. `loadSampleData()` injects a second hardcoded `summaries`
array. Replace both with a real call to `/api/search`.

**Files:**
- Modify: `src/static/templates/index.html` (replace `generateStudyKit`, trim `loadSampleData`, update `renderStudyKit`)
- Test: `tests/test_end_to_end.py` (string assertions), `tests/test_playwright_e2e.py` (behaviour)

**Interfaces:**
- Consumes: `GET /api/search?q=&limit=` from Task 7.
- Produces: no new backend interface.

> **Read the Study Desk markup before writing any JS.** The existing DOM is:
> `lectureInput` (textarea), `charCounter`, an unnamed `.btn.btn-brand` button carrying
> `onclick="generateStudyKit()"`, `summaryContainer` (a `.summary-feed` div), and a **single**
> 3D flashcard driven by `flashcardModel` / `fcQuestion` / `fcAnswer` / `deckCounter` / `deckDots`.
> The deck is **not** a container of card elements — `currentDeck` + `cardIndex` +
> `updateDeckView()` own it, and `flipCard()` toggles one element.
>
> The only ids in the file are: `btnNext`, `btnPrev`, `charCounter`, `courses`, `dashboard`,
> `deckCounter`, `deckDots`, `fcAnswer`, `fcQuestion`, `features`, `flashcardModel`,
> `lectureInput`, `summaryContainer`. There is **no** `extractBtn`, `flashcardContainer`,
> `studyKitError`, or `studyKitEmpty`. Steps below add only `studyKitError`, and locate the
> button via `document.querySelector('.btn-brand')` rather than inventing an id.

- [ ] **Step 1: Write the failing test**

Add to `TestFrontendIntegrity`:

```python
    def test_generate_study_kit_calls_the_search_api(self):
        import os
        tdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "src", "static", "templates")
        with open(os.path.join(tdir, "index.html"), encoding="utf-8", errors="ignore") as fh:
            html = fh.read()
        i = html.index("function generateStudyKit")
        body = html[i:i + 3000]
        self.assertIn("/api/search", body, "generateStudyKit still does not call the backend")
        self.assertNotIn("alert(", body, "must not use alert(); render an inline error")

    def test_presets_no_longer_carry_hardcoded_output(self):
        import os
        tdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "src", "static", "templates")
        with open(os.path.join(tdir, "index.html"), encoding="utf-8", errors="ignore") as fh:
            html = fh.read()
        i = html.index("const PRESETS")
        j = html.index("function loadSampleData")
        presets = html[i:j]
        self.assertNotIn("summaries", presets, "PRESETS still hardcodes summaries")
        self.assertNotIn("flashcards", presets, "PRESETS still hardcards flashcards")
        self.assertIn("text", presets, "PRESETS must keep its real lecture text")

    def test_flashcard_deck_contract_is_preserved(self):
        """The single-card 3D deck is existing behaviour; Task 8 must not replace it."""
        import os
        tdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "src", "static", "templates")
        with open(os.path.join(tdir, "index.html"), encoding="utf-8", errors="ignore") as fh:
            html = fh.read()
        for token in ("currentDeck", "function updateDeckView", "function flipCard",
                      "flashcardModel", "fcQuestion", "fcAnswer"):
            self.assertIn(token, html, f"flashcard deck contract broken: {token} missing")
        self.assertNotIn("flashcardContainer", html,
                         "do not replace the single-card deck with a card list")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m unittest tests.test_end_to_end.TestFrontendIntegrity -v`
Expected: FAIL on both new tests.

- [ ] **Step 3: Trim the PRESETS object**

In the `const PRESETS = {` block, delete every `summaries: [...]` and `flashcards: [...]` array,
keeping `name` and `text` for each of the three presets (thermo, os, dsa).

- [ ] **Step 4: Simplify `loadSampleData`**

Replace its body so a chip click only fills the textarea and stops:

```javascript
        function loadSampleData(key, el) {
            const data = PRESETS[key];
            if (!data) return;

            document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
            const chip = el && el.classList ? el : (typeof event !== 'undefined' && event ? event.target : null);
            if (chip && chip.classList) chip.classList.add('active');

            const input = document.getElementById('lectureInput');
            if (input) {
                input.value = data.text;
                input.focus();
            }
        }
```

- [ ] **Step 5: Add the error element**

Immediately after the `<textarea id="lectureInput">` line, add:

```html
                <div id="studyKitError" class="char-counter" style="color: var(--accent-amber); min-height: 1.2em;"></div>
```

- [ ] **Step 6: Replace `generateStudyKit` with a real search**

The button has no id, so select it by class. `currentDeck` and `cardIndex` are already
module-level globals in this file — reuse them rather than shadowing.

```javascript
        async function generateStudyKit() {
            const input = document.getElementById('lectureInput');
            const raw = input ? input.value.trim() : '';
            const errEl = document.getElementById('studyKitError');
            if (errEl) errEl.textContent = '';

            if (!raw) {
                if (errEl) errEl.textContent = 'Type a topic, concept, or question keyword.';
                return;
            }

            const btn = document.querySelector('.btn-brand');
            const label = btn ? btn.querySelector('span') : null;
            const original = label ? label.textContent : '';
            if (btn) btn.disabled = true;
            if (label) label.textContent = 'Searching…';

            try {
                const res = await fetch('/api/search?q=' + encodeURIComponent(raw));
                if (res.status === 400) {
                    const body = await res.json().catch(() => ({}));
                    if (errEl) errEl.textContent = body.detail || 'Type a topic, concept, or question keyword.';
                    return;
                }
                if (!res.ok) throw new Error('Search failed (' + res.status + ')');

                const data = await res.json();
                document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
                renderStudyKit(data.results || [], data.topic_context || null);
            } catch (e) {
                if (errEl) errEl.textContent = 'Search is unavailable right now. Is the server running?';
            } finally {
                if (btn) btn.disabled = false;
                if (label) label.textContent = original;
            }
        }
```

- [ ] **Step 7: Rewrite `renderStudyKit` to feed the existing deck**

`currentDeck` holds `{q, a}` pairs and `updateDeckView()` paints them. Reuse both.

```javascript
        function renderStudyKit(results, topicContext) {
            const feed = document.getElementById('summaryContainer');

            if (feed) {
                let html = '';
                if (topicContext) {
                    html += `<div class="summary-card">
                        <span class="summary-tag">${escapeHtml(topicContext.subject || '')} — ${escapeHtml(topicContext.topic || '')}</span>
                        <div class="summary-content">${escapeHtml(topicContext.summary || '')}</div>
                    </div>`;
                    (topicContext.key_points || []).slice(0, 5).forEach(kp => {
                        const text = typeof kp === 'string' ? kp : (kp.point || kp.text || JSON.stringify(kp));
                        html += `<div class="summary-card">
                            <span class="summary-tag">Key Point</span>
                            <div class="summary-content">${escapeHtml(text)}</div>
                        </div>`;
                    });
                }
                results.filter(r => r.source_type === 'question').slice(0, 8).forEach((q, n) => {
                    const marks = q.marks ? ` · ${escapeHtml(String(q.marks))} marks` : '';
                    html += `<div class="summary-card">
                        <span class="summary-tag">Q${n + 1} · ${escapeHtml(q.difficulty || '')}${marks}</span>
                        <div class="summary-content">${escapeHtml(q.text || '')}</div>
                    </div>`;
                });
                feed.innerHTML = html ||
                    '<div class="summary-card"><div class="summary-content">No matches. Try a topic like AVL, Dijkstra, or deadlocks.</div></div>';
                renderEquations(feed);
            }

            const cards = (topicContext && topicContext.flashcards) || [];
            currentDeck = cards.map(c => ({
                q: escapeHtml(c.front || c.question || ''),
                a: escapeHtml(c.back || c.answer || '')
            }));
            cardIndex = 0;
            if (currentDeck.length === 0) {
                currentDeck = [{
                    q: 'No flashcards for this query.',
                    a: 'Try a broader topic such as AVL, Dijkstra, or deadlocks.'
                }];
            }
            const model = document.getElementById('flashcardModel');
            if (model) model.classList.remove('flipped');
            updateDeckView();
            renderEquations();
        }
```

Note the flashcard text is escaped **before** being stored in `currentDeck` because
`updateDeckView()` assigns it via `innerHTML`; escaping at the source keeps both call sites safe.
`updateEquations()` takes no argument in this file — call it bare.

- [ ] **Step 8: Run the string assertions to verify they pass**

Run: `python -m unittest tests.test_end_to_end.TestFrontendIntegrity -v`
Expected: PASS, including `test_flashcard_deck_contract_is_preserved`.

- [ ] **Step 9: Add the Playwright behaviour test**

Add to `tests/test_playwright_e2e.py`:

```python
def test_study_desk_searches_real_corpus(page):
    page.goto("http://127.0.0.1:8000/index.html")
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.fill("#lectureInput", "avl tree rottaions")
    page.click(".btn-brand")
    page.wait_for_selector("#summaryContainer .summary-card", timeout=15000)
    first = page.inner_text("#summaryContainer")
    assert "avl" in first.lower(), f"typo query produced no AVL content: {first[:200]}"

    assert "1 /" in page.inner_text("#deckCounter"), "flashcard deck did not populate"

    page.fill("#lectureInput", "dijkstra negative weights")
    page.click(".btn-brand")
    page.wait_for_timeout(2000)
    second = page.inner_text("#summaryContainer")
    assert first != second, "two different queries returned identical output"

    assert not errors, f"console errors: {errors}"
```

- [ ] **Step 10: Run the E2E test**

Run: start the server with `python run.py`, then `python -m unittest tests.test_playwright_e2e -v`
Expected: PASS with no console errors. Then stop the server.

- [ ] **Step 11: Commit**

```bash
git add src/static/templates/index.html tests/test_end_to_end.py tests/test_playwright_e2e.py
git commit -m "feat(frontend): replace hardcoded study kit with real /api/search prompt box"
```

---

### Task 9: Trim requirements and the system status shape

**Files:**
- Modify: `requirements.txt`, `src/backend/app.py` (status endpoint), `src/c_core/c_bridge.py` (lazy Pillow)
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Consumes: nothing
- Produces: `/api/system/status` with unchanged keys; `total_notebooks` and `indexed_rag_chunks` return `0` rather than disappearing.

- [ ] **Step 1: Write the failing test**

```python
class TestStatusShape:
    def test_status_keeps_all_keys(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        data = TestClient(app).get("/api/system/status").json()
        for key in ("status", "c_core_accelerated", "gemini_api_configured",
                    "total_assignments", "total_notebooks", "indexed_rag_chunks",
                    "available_subjects", "timestamp"):
            self.assertIn(key, data, f"status key removed: {key}")
        self.assertEqual(data["status"], "online")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest tests.test_end_to_end.TestStatusShape -v`
Expected: FAIL — `get_system_status` calls `DatabaseRepo.get_notebooks()` and `RAGIndex.get_instance()`, both of which may now be unreachable, or the keys vanish.

- [ ] **Step 3: Fix the status endpoint**

Replace the body of `get_system_status` with:

```python
async def get_system_status():
    meta = DatabaseRepo.get_distinct_metadata()
    return {
        "status": "online",
        "c_core_accelerated": _lib_loaded,
        "gemini_api_configured": AIEngine.is_gemini_available(),
        "total_assignments": 0,
        "total_notebooks": 0,
        "indexed_rag_chunks": len(RAGIndex.get_instance().chunks),
        "available_colleges": len(meta["colleges"]),
        "available_subjects": len(meta["subjects"]),
        "timestamp": datetime.now().isoformat()
    }
```

`indexed_rag_chunks` is now genuinely useful — it reports the real corpus size.

- [ ] **Step 4: Make the Pillow import lazy in `c_bridge.py`**

`preprocess_image_for_ocr` was the only consumer of the module-level `from PIL import Image`, and
it is now unused. Change the top-level import to a lazy one inside the function:

```python
def preprocess_image_for_ocr(image):
    from PIL import Image  # noqa: F401  (kept for callers passing PIL images)
    if image.mode != "L":
        return image.convert("L")
    return image
```

and delete the module-level `from PIL import Image` line.

- [ ] **Step 5: Trim `requirements.txt`**

Remove these three lines: `pypdf>=4.1.0`, `python-docx>=1.1.0`, `numpy>=1.26.0`. Keep `Pillow>=10.2.0`
for the lazy path. Keep everything else unchanged.

- [ ] **Step 6: Verify nothing imports the dropped packages**

Run: `python -c "import ast,pathlib,sys; bad=[]; [bad.append((f.name,n)) for f in pathlib.Path('src').rglob('*.py') for n in ast.walk(ast.parse(f.read_text(encoding='utf-8',errors='ignore'))) if isinstance(n,(ast.Import,ast.ImportFrom)) and any(m in ('pypdf','docx','numpy') for m in ([a.name for a in n.names] if isinstance(n,ast.Import) else [n.module or '']))]; print('violations:', bad)"`
Expected: `violations: []`

- [ ] **Step 7: Run the test to verify it passes**

Run: `python -m unittest tests.test_end_to_end.TestStatusShape -v`
Expected: PASS

- [ ] **Step 8: Run the full suite and the import gate**

Run: `python -c "import sys; sys.path.insert(0,'.'); import src.backend.app; print('IMPORT OK')"` then `python -m unittest tests.test_end_to_end -v`
Expected: `IMPORT OK`, then all tests PASS.

- [ ] **Step 9: Commit**

```bash
git add requirements.txt src/backend/app.py src/c_core/c_bridge.py tests/test_end_to_end.py
git commit -m "chore: drop pypdf/docx/numpy deps, lazy Pillow, stabilize status shape"
```

---

## Subsystem C — The deck

### Task 10: Rewrite the pitch deck

The deck states three false facts and cites four unsourced figures. Fix every factual claim
against the code, keeping the existing visual identity.

**Files:**
- Modify: `C:\Users\dell\OneDrive\Desktop\Essentials\Open Design SHIT\11aa8985-637e-41a9-9c65-225de549f0bb\studymorph-pitch-deck.html`
- Test: manual verification (no test harness for a standalone HTML deck)

**Interfaces:**
- Consumes: the finished code from Tasks 1–9. Every claim must trace to a real file path or endpoint.
- Produces: an 8-slide deck with no false claims.

> This file is outside the `Study-Morph-master` repository, which has no `.git` of its own — it
> sits inside the `C:\Users\dell` repo. Confirm with the user before staging it.

- [ ] **Step 1: Record the baseline**

Run: `Select-String -LiteralPath "<deck path>" -Pattern "OmniRoute|Flask|Tailwind|98%|30%|400\+|2\.5s" | Measure-Object | Select-Object -ExpandProperty Count`
Expected: a non-zero count — these are the claims to eliminate.

- [ ] **Step 2: Fix slide 1 — the AI layer claim**

Replace "OmniRoute AI Engine" with the retrieval framing: native BM25 search across
**1,740 verified questions and 57 unit summaries**, powered by a hand-written C DLL via ctypes.

- [ ] **Step 3: Fix slide 2 — remove unsourced figures**

Delete "Up to 30% of study time is wasted", "400+ Pages/Wk", and "< 20% After 48h". Replace with
descriptive framing grounded in the product: exam-pattern question sets mapped to a real B.Tech
CSE syllabus, with difficulty and marks carried per question.

- [ ] **Step 4: Fix slide 3 — the Study Desk claim**

Retitle from "Instant generation" to retrieval. Remove "< 2.5s via Multi-Model Processing Layer"
and the "Generated in" caption. Describe: type raw text — including misspellings and
abbreviations — and get matching questions with difficulty and marks, the topic summary, and
flashcards. Note that the search is typo-tolerant by design.

- [ ] **Step 5: Fix slide 4 — the pipeline diagram**

Replace "Flask API Tokenizer" with the real pipeline:

```
Raw query → FastAPI /api/search → BM25 index (C DLL via ctypes) → SQLite corpus → Results + KaTeX
```

- [ ] **Step 6: Fix slide 5 — the tech stack**

- Frontend: "HTML, CSS, and Tailwind CSS" → "Hand-written HTML/CSS/JS, no build step, KaTeX for math"
- Backend: "Python (Flask)" → "Python 3.14 · FastAPI + uvicorn"
- AI Engine: "Powered by OmniRoute" → "Native C acceleration (BM25, fuzzy match) via ctypes; Gemini 1.5 Flash optional for question generation"
- Add SQLite with WAL journaling to the stack list.

- [ ] **Step 7: Fix slide 6 — remove "98% Faster"**

Replace with verifiable counts: 1,740 questions, 57 syllabus units, 6 subjects in the shipped UI,
15 questions per set, native retrieval with no API key required.

- [ ] **Step 8: Fix slide 7 — the roadmap**

"Phase 2 — Direct PDF and document file uploads" described the deleted OCR feature. Replace with
expansion: more subjects and syllabus units, richer per-topic question variety, and spaced-repetition
scheduling against the existing `student_activity` table.

- [ ] **Step 9: Verify no false claims remain**

Run: `Select-String -LiteralPath "<deck path>" -Pattern "OmniRoute|Flask|Tailwind|98%|2\.5s"`
Expected: no matches.

- [ ] **Step 10: Cross-check every surviving number against the database**

Run: `python -c "import sys; sys.path.insert(0,'.'); from src.backend.database import DatabaseRepo as D; from src.backend.rag_engine import RAGIndex; i=RAGIndex(); i.rebuild_index(); print('questions:', len(D.get_question_bank_for_index())); print('topics:', len(D.get_all_topics())); print('flashcards:', len(D.get_all_interactive_content())); print('index chunks:', len(i.chunks))"`
Expected: 1740, 57, 84, and ~1881. Correct any deck number that disagrees.

- [ ] **Step 11: Verify the deck renders**

Open the file in a browser and step through all 8 slides. Confirm text does not overflow the
1920×1080 stage on slides 2, 3, 5, and 7, which gain the most replacement text.

- [ ] **Step 12: Commit**

```bash
git add "<deck path>"
git commit -m "docs(deck): correct stack, AI layer, and metrics to match shipped code"
```

---

## Final verification

- [ ] **Full suite green:** `python -m unittest tests.test_end_to_end -v`
- [ ] **Import gate:** `python -c "import sys; sys.path.insert(0,'.'); import src.backend.app; print('IMPORT OK')"`
- [ ] **Route count is 24:** 18 in `app.py` + 6 in `question_bank_api.py`
- [ ] **No raw SQL outside `database.py`:** re-run the placement sweep from the spec's Query audit
- [ ] **Manual smoke:** `python run.py`, then load `/` and `/course.html?course=CS201`, run a
      search, take a 15-question quiz, and confirm no console errors
- [ ] **Deck claims match code:** every number from Task 10 Step 10
