# Backend Audit and Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve backend reliability, cold-start, request responsiveness, search latency, and maintainability without removing any feature, endpoint, response field, table, seed data, or supported workflow.

**Architecture:** Capture route/data/performance baselines first. Make database connections exception-safe, then unify runtime/seed schema initialization while keeping legacy import wrappers. Offload synchronous question generation to the Starlette threadpool and synchronize the in-memory refresh history. Precompute search term-frequency and prefix indexes during the existing atomic rebuild. Finally narrow only optional-provider exception handling and remove provably unused imports; preserve all public behavior.

**Tech Stack:** Python 3.14, FastAPI/Starlette, SQLite WAL, `requests`, Gemini SDK (optional), native C DLL via ctypes, `unittest`, Playwright.

**Spec:** `docs/superpowers/specs/2026-10-02-backend-audit-and-optimization-design.md`

## Global Constraints

- **Do not remove features.** No endpoint, UI capability, data table, seed data, response field, fallback path, or supported workflow may be deleted or silently changed.
- No schema/table drops and no user-row deletion. Tests that alter rows must use a temporary DB and clean up in `finally`.
- Keep the existing route/method inventory identical (23 paths at baseline).
- `DatabaseRepo` remains the runtime data-access layer; `database_init.py` seed functions remain callable.
- Do not add runtime dependencies.
- Preserve current local modifications in `run.py` (PORT 8000 → 8009) and rebuilt `src/c_core/libstudyc.dll`; do not overwrite or stage them in unrelated commits.
- Test runner is `python -m unittest`; do not add pytest.
- Existing search ranking, typo/prefix matching, result deduplication, response fields, and concurrent-index correctness must remain stable.
- Existing question generation contract stays exactly 15 questions, with current web research, Gemini-optional path, local synthesis fallback, and session refresh semantics.
- No secrets, API keys, full prompts, or full user content in logs.

## Review Focus

1. **SQLite operation raises after connect** — connection closes and subsequent DB calls work. Test in Task 2.
2. **Fresh import / older existing DB** — import performs no schema write; startup initializes once without deleting data. Test in Task 3.
3. **Concurrent same-session refreshes** — history/counters remain coherent, bounded to 60, and response shape remains 15 questions. Test in Task 4.
4. **Search rebuild overlaps live searches** — readers see a complete old or new index; identical concurrent queries have identical results. Test in Task 5.
5. **Optional providers timeout, return malformed JSON, or Gemini is unavailable** — local fallback still works; unexpected DB/programming errors remain visible. Test in Task 6.

---

## Files and responsibilities

- `tests/test_end_to_end.py`: route/data/connection/provider/search contract tests.
- `tests/backend_audit_baseline.py`: local, repeatable latency/throughput baseline; stdlib timing only.
- `src/backend/database.py`: canonical SQLite connection factory, schema setup, and repository access.
- `src/backend/database_init.py`: seed entry point, delegating connection/schema setup to `database.py` while retaining seed APIs.
- `src/backend/app.py`: startup/readiness and response-compatible routes.
- `src/backend/question_bank_api.py`: async route boundary for sync question generation.
- `src/backend/web_question_engine.py`: external provider fallback and in-memory session state.
- `src/backend/rag_engine.py`: rebuild-time token/vocabulary caches with atomic index publication.
- `src/backend/ai_engine.py`: optional Gemini logging/fallback behavior.

---

### Task 1: Capture route, response, data, and latency baselines

**Files:**
- Modify: `tests/test_end_to_end.py`
- Create: `tests/backend_audit_baseline.py`

**Interfaces:**
- Produces: route/method inventory and baseline report consumed by later tasks.
- No production-code changes.

- [ ] **Step 1: Write the route inventory test**

Add a test that collects methods and paths from `app.routes`, descending into included routers. Pin this exact set (23 method/path pairs):

```python
EXPECTED_ROUTES = frozenset({
    ("GET", "/"), ("GET", "/index.html"),
    ("GET", "/course.html"), ("GET", "/course"),
    ("GET", "/api/system/status"), ("GET", "/api/metadata"),
    ("GET", "/api/curriculum"), ("GET", "/api/curriculum/full"),
    ("GET", "/api/curriculum/year/{year}"), ("GET", "/api/curriculum/{code}"),
    ("GET", "/api/topics"), ("GET", "/api/topics/search"),
    ("GET", "/api/content/{course_code}"),
    ("GET", "/api/content/{course_code}/{topic_name}"),
    ("GET", "/api/interactive/{course_code}"), ("POST", "/api/activity/log"),
    ("GET", "/api/search"),
    ("GET", "/api/questions/topics"),
    ("GET", "/api/questions/course/{course_code}"),
    ("POST", "/api/questions/course/{course_code}/refresh"),
    ("POST", "/api/questions/refresh"),
    ("GET", "/api/questions/topic/{subject}/{topic}"),
    ("GET", "/api/questions/topic-stats/{subject}/{topic}"),
})
```

Build `actual` by iterating `app.routes`, collecting each route's `path`/`methods`, and for each included router collect its child APIRoutes using `getattr(route, "routes", [])`; assert `actual == EXPECTED_ROUTES`. The baseline has **23 unique paths and 23 method/path pairs**; enumerate the literal set above as the contract.

- [ ] **Step 3: Add deterministic local latency benchmark script**

Create `tests/backend_audit_baseline.py` using `argparse`, `statistics`, `time.perf_counter`, and FastAPI `TestClient`. It accepts `--requests` and `--query`; runs warm-up plus samples for `/api/search`, `/api/system/status`, and `/api/questions/course/CS201`. For generation, patch the web research function locally to return deterministic local fixture content (no internet); assert the response contains exactly 15 questions. Print endpoint, request count, p50, p95, and status/schema failures. No timing assertion in CI.

- [ ] **Step 4: Capture baseline**

Add a `.audit/` git-ignore entry in the same commit so benchmark output files are never staged. Run both existing suites and `python tests/backend_audit_baseline.py --requests 30 --query "avl tree rottaions"`, saving raw baseline numbers under `.audit/` (ignored) rather than in production source.

- [ ] **Step 5: Commit**

```bash
git add tests/test_end_to_end.py tests/backend_audit_baseline.py .gitignore
git commit -m "test(backend): capture route and latency baselines"
```

---

### Task 2: Make every repository connection exception-safe

**Files:**
- Modify: `src/backend/database.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Preserve `get_connection() -> sqlite3.Connection` for compatibility.
- Add private context manager `_connection() -> Iterator[sqlite3.Connection]`.
- Preserve all `DatabaseRepo` names, parameters, JSON defaults, return types/keys, SQL filters, and commit behavior.

- [ ] **Step 1: Add temporary-DB failure-injection tests**

Add `TestDatabaseConnectionSafety` with `setUp/tearDown` saving/restoring `database.DB_PATH` and using `tempfile.TemporaryDirectory()`. Initialize the temporary schema, then patch the **module-level `get_connection` factory** with a wrapper that returns a real SQLite connection wrapped by a small proxy exposing `cursor`, `commit`, and `close`; its cursor proxy delegates all methods except that the selected cursor `execute()` raises a sentinel `RuntimeError` after the connection is captured. Assert the exception propagates and the captured real connection rejects future statements with `sqlite3.ProgrammingError`.

Also test normal success and early-return paths: missing `get_assignment_by_id` returns `None`; temp-DB `create_assignment` can be fetched after close.

Do not patch `sqlite3.Cursor.execute` directly: it is an immutable C type in some Python builds and the patch may fail before exercising repository code.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_end_to_end.TestDatabaseConnectionSafety -v`
Expected: injected-exception test fails because current code closes only on normal paths.

- [ ] **Step 3: Add the connection context manager**

```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
```

Migrate each `DatabaseRepo` method to `with _connection() as conn:` in logical groups. Preserve each existing `commit()` and never change SQL/result logic in this task. Avoid re-indenting or rewriting unrelated data methods.

- [ ] **Step 4: Run focused tests after each method group**

Run the connection-safety tests after each converted group and inspect failures before proceeding.

- [ ] **Step 5: Run full unit suite**

Run: `python -m unittest tests.test_end_to_end`
Expected: all current tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/backend/database.py tests/test_end_to_end.py
git commit -m "fix(db): close repository connections on every exit path"
```

---

### Task 3: Unify database initialization, keep seeding compatible

**Files:**
- Modify: `src/backend/database.py`, `src/backend/database_init.py`, `src/backend/app.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Importing `src.backend.database` performs no schema creation or DB write.
- App startup completes schema initialization before serving requests.
- Keep `database_init.get_connection`, `database_init.init_db`, `seed_all`, and each seed function callable for existing scripts.
- Existing tables and seed counts remain intact; migrations stay additive.

- [ ] **Step 1: Write fresh-import and startup tests using a subprocess/temp DB**

Test that importing `src.backend.database` with `DB_PATH` pointed into a fresh temp directory does not create the DB. Calling `init_db()` then creates the expected existing tables. Test app startup initializes once and `/api/system/status` works afterward.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_end_to_end.TestDatabaseInitialization -v`
Expected: import-side-effect test fails because `database.py` ends in a module-level `init_db()` call.

- [ ] **Step 3: Remove import-time initialization**

Remove only the terminal `init_db()` invocation in `database.py`; retain the function. Keep FastAPI startup as runtime initialization owner.

- [ ] **Step 4: Delegate duplicate helper definitions from the seeder module**

In `database_init.py`, import `DB_PATH`, `get_connection`, and `init_db` from `.database` (or provide thin backward-compatible wrappers if callers depend on module globals). Remove the duplicated schema initializer only after temp-DB parity tests verify the canonical `database.init_db()` creates every table/index needed by every existing seed function. Do not delete seed functions or change their table contents.

- [ ] **Step 5: Existing DB migration safety test**

Copy the ignored current DB to a temp DB; record table names/counts; invoke canonical `init_db()` twice; assert every existing table remains and every row count is unchanged. Do not run `seed_all()` against the real local DB.

- [ ] **Step 6: Verify the seeder output contract**

Run seed functions only on a disposable temp DB and assert the same baseline counts for curriculum, topic content, interactive content, and question bank.

- [ ] **Step 7: Full verification and commit**

Run import gate, focused initialization tests, full unit suite, and E2E suite. Then commit:

```bash
git add src/backend/database.py src/backend/database_init.py src/backend/app.py tests/test_end_to_end.py
git commit -m "refactor(db): centralize schema initialization without import side effects"
```

---

### Task 4: Keep blocking question generation off the event loop

**Files:**
- Modify: `src/backend/question_bank_api.py`, `src/backend/web_question_engine.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- All existing question routes, parameters, and JSON schemas remain unchanged.
- `WebQuestionEngine.generate_questions(...)` remains synchronous for direct callers.
- Async API handlers call it via `starlette.concurrency.run_in_threadpool`.

- [ ] **Step 1: Write event-loop responsiveness test**

Patch `WebQuestionEngine.search_web_for_topic` with a `threading.Event` wait (bounded at 0.5s) and patch synthesis to return 15 deterministic question objects. Start question generation and `/api/system/status` concurrently using `httpx.AsyncClient`/ASGI transport or a real local uvicorn test server. Assert status completes while research is still blocked; release the event and assert generation returns exactly 15 valid questions with the established response keys.

- [ ] **Step 2: Write session concurrency test**

Use a barrier to concurrently record more than 60 uniquely tagged questions for one session key. Assert history remains capped to the last 60 without lost list integrity; a different session/topic key remains isolated. Do not hold the lock during network/model work.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_end_to_end.TestQuestionGenerationConcurrency -v`.
Expected: responsiveness test fails because sync network generation currently executes directly inside `async def` route handlers.

- [ ] **Step 4: Offload at API boundary**

Wrap only calls to `WebQuestionEngine.generate_questions` in retained async handlers with `await run_in_threadpool(...)`. Keep engine function sync and preserve every argument and return object.

- [ ] **Step 5: Synchronize session state**

Add a module `threading.RLock` around brief history/counter reads/writes. Copy the previous-history snapshot and reserve/increment the refresh counter under lock; release before web and LLM calls. Keep key construction and the 60-record cap unchanged.

- [ ] **Step 6: Verify exactly-15 fallback and API contract**

Run focused concurrency tests, full unit suite, E2E suite, and route inventory. Confirm provider timeout still falls back to local synthesis and returns exactly 15.

- [ ] **Step 7: Commit**

```bash
git add src/backend/question_bank_api.py src/backend/web_question_engine.py tests/test_end_to_end.py
git commit -m "fix(api): offload generation and synchronize refresh history"
```

---

### Task 5: Cache search term frequencies and prefix candidates

**Files:**
- Modify: `src/backend/rag_engine.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Preserve `RAGIndex.search(query, top_k=12)` and `get_topic_context(query)` signatures.
- Preserve response field names, ordering, thresholds, course-code normalization, deduplication, unit resolution, and thread-safe atomic rebuild.

- [ ] **Step 1: Add reference-equivalence test**

For a fixed deterministic corpus fixture, calculate the current reference term-frequency vector using `chunk.tokens.count(token)` and compare ordered chunk IDs and score values against the optimized cache path for:
`avl tree rottaions`, `dijkstra negative weights`, `deadlok`, `memoization`, `prog`, and gibberish. Scores must match within `1e-9`; query results must remain the same after deduplication.

- [ ] **Step 2: Add rebuild invalidation test**

Patch repository row providers to yield corpus A, build, then corpus B and rebuild. Assert cached term frequencies/vocabulary/prefix mappings contain B and no unique token from A; query results for B match the reference implementation.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_end_to_end.TestSearchCacheEquivalence -v`.
Expected: cache-presence/invalidation test fails before the cache exists.

- [ ] **Step 4: Build per-chunk term counters and lookup maps locally**

During the existing atomic `rebuild_index()` local-build phase, build `Counter`/dict token frequencies per chunk, document frequencies, and a prefix map keyed by prefixes of length ≥3. Assign all index components together while holding the existing reentrant lock. Do not mutate published state during build.

- [ ] **Step 5: Use caches in search**

Replace per-query `chunk.tokens.count(token)` with cached count lookup. Replace vocabulary prefix scan with the prefix map. Keep the edit-distance/fuzzy fallback unchanged. Avoid retaining duplicate copies of large token arrays if benchmarked memory rises excessively; store only the per-chunk data needed for scoring.

- [ ] **Step 6: Validate identical behavior and performance**

Run reference-equivalence test, full unit suite, and E2E suite. Re-run Task 1 baseline with same query/sample count; record p50/p95 and memory delta. If ranking/score differs beyond tolerance or memory/latency worsens materially, revise or revert the cache design.

- [ ] **Step 7: Commit**

```bash
git add src/backend/rag_engine.py tests/test_end_to_end.py
git commit -m "perf(search): cache token counts and prefix candidates during index build"
```

---

### Task 6: Make external-provider fallback explicit and safe

**Files:**
- Modify: `src/backend/web_question_engine.py`, `src/backend/ai_engine.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- Keep Wikipedia, DuckDuckGo, optional Google Custom Search, optional Gemini, and local synthesis fallback.
- Preserve every route and response field; generation remains exactly 15.
- Logs contain provider and exception class only; no API keys, full prompt, raw response, or user query.

- [ ] **Step 1: Add provider failure matrix tests**

For each provider boundary, test timeout, non-200, malformed JSON, and empty response. Assert the final endpoint returns the established response keys and exactly 15 synthesized/LLM questions. Add a DB failure case and assert DB exceptions propagate rather than masquerading as empty results.

- [ ] **Step 2: Add secret/content redaction log test**

Inject an exception containing sentinel strings `FAKE_API_KEY_123` and `PRIVATE_QUERY_SENTINEL`; capture logs and assert neither sentinel is present.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_end_to_end.TestProviderFallbacks -v`.
Expected: current broad silent exception branches produce no structured warning and the redaction/visibility tests fail.

- [ ] **Step 4: Narrow optional-service exception handling**

Catch `requests.RequestException` for HTTP providers, JSON decode/value errors for malformed payloads, and documented Gemini SDK exceptions at the Gemini boundary. Log only provider name and exception class. Preserve current fallback order and researched/unresearched response behavior.

- [ ] **Step 5: Run focused tests, unit suite, E2E suite**

Expected: each unavailable optional provider falls back, exact-15 output remains, DB/programming errors remain visible, and logs contain no sentinel secrets/content.

- [ ] **Step 6: Commit**

```bash
git add src/backend/web_question_engine.py src/backend/ai_engine.py tests/test_end_to_end.py
git commit -m "fix(ai): make optional provider fallbacks observable and safe"
```

---

### Task 7: Consolidate repeated repository JSON decoding

**Files:**
- Modify: `src/backend/database.py`
- Test: `tests/test_end_to_end.py`

**Interfaces:**
- No `DatabaseRepo` method removed/renamed; preserve all returned keys, `None`/empty defaults, and database schema.

- [ ] **Step 1: Capture current decoded return shapes**

Add table-driven tests for topic and curriculum repository methods with valid JSON, NULL, and empty-string fields. Assert exact keys/types/defaults as presently returned.

- [ ] **Step 2: Add a private pure row-decoding helper**

Implement `_decode_json_fields(row, fields)` returning a new dict; decode truthy values with `json.loads`, map empty/NULL to `[]`. Do not use this helper for fields that currently have a different default or are intentionally omitted.

- [ ] **Step 3: Refactor identical groups**

Refactor topic-content decoders first (`get_all_topics`, `get_topic_content`, `get_topic_by_keyword` only where field sets match), run focused tests, then curriculum decoders. Do not modify SQL, ordering, filters, or transaction boundaries.

- [ ] **Step 4: Verify output compatibility and full suites**

Serialize fixed fixture outputs to JSON before and after and assert exact equality. Run both full suites.

- [ ] **Step 5: Commit**

```bash
git add src/backend/database.py tests/test_end_to_end.py
git commit -m "refactor(db): share equivalent JSON row decoding"
```

---

### Task 8: Final preservation and performance verification

**Files:** no production changes unless a regression is found.

- [ ] **Step 1: Exact route/method comparison** — route inventory equals Task 1 baseline exactly.
- [ ] **Step 2: Data preservation** — on a temp DB copy, compare schema, table names, counts, curriculum codes, question bank, topics, interactive content; zero rows lost and zero tables dropped.
- [ ] **Step 3: Full tests** — `python -m unittest tests.test_end_to_end` and `python -m unittest tests.test_playwright_e2e` both pass.
- [ ] **Step 4: Performance comparison** — rerun exact Task 1 benchmark inputs; report p50/p95 for status/search/question-generation, concurrent throughput, index-build time, and memory delta. Investigate regressions >5%; do not claim improvements without measurements.
- [ ] **Step 5: User changes protected** — inspect `git diff -- run.py src/c_core/libstudyc.dll`; do not stage either. Stage only files in the current task.
- [ ] **Step 6: Final status** — verify no secrets, local DB, or temporary audit scripts are staged; report findings and remaining limitations.
