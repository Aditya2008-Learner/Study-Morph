# Backend Audit and Optimization Design

Date: 2026-10-02
Status: Draft for review

## Goal

Audit and optimize the existing Study-Morph backend for correctness, latency, resource safety, and maintainability while preserving every currently supported feature, route, response contract, stored table, and user-facing behaviour.

## Non-negotiable constraint

**Do not remove features.** No endpoint, UI capability, data table, seed data, response field, fallback path, or supported workflow may be deleted or silently changed. An optimization may reorganize implementation only if external behaviour is preserved. Any proposed behaviour change requires a separate explicit user decision.

The work must retain the current restored Study Desk and course pages. Do not redesign the frontend as part of this backend effort.

## Current baseline

- Local branch: `align-code-and-deck`.
- Current committed head when this spec was drafted: `5ca54a9`.
- Existing unrelated working-tree modifications: `run.py` (port 8000 → 8009) and rebuilt `src/c_core/libstudyc.dll`; these must not be overwritten or silently included in unrelated commits.
- Existing verification baseline: `python -m unittest tests.test_end_to_end` (61 tests) and `python -m unittest tests.test_playwright_e2e` (2 tests) passed immediately before this audit request.
- Backend entry: FastAPI in `src/backend/app.py`; SQLite repository in `src/backend/database.py`; seed/migration logic in `src/backend/database_init.py`; local BM25/fuzzy search in `src/backend/rag_engine.py`; live question research/generation in `src/backend/web_question_engine.py`.
- The app currently exposes 23 paths: 4 page paths, 17 API paths including question-bank router routes.

## Audit findings and priority

### P0 — Resource safety and data integrity

#### P0.1 — SQLite connection leaks on exceptions

`DatabaseRepo` has about 44 `get_connection()` sites and most methods call `conn.close()` only on normal return. If SQL execution, JSON decoding, or later result transformation raises, the connection can remain open and retain locks/resources. `get_interactive_content()` additionally suppresses broad exceptions across three fallback stages, which makes a real DB failure indistinguishable from an empty result.

**Acceptance:** every repository operation closes its connection on success and failure. Existing fallbacks still run only for the intended absence/empty conditions; unexpected SQL or decode errors are observable through normal error propagation/logging rather than silently swallowed. CRUD, curriculum, content, search-index build, and status responses remain compatible.

#### P0.2 — Import-time and duplicate schema initialization

`database.py` invokes `init_db()` at module import (end of file), while `app.py` invokes it again on startup. `database_init.py` separately defines another connection/schema initializer used by the seed command. This creates duplicate work, import side effects, and two schema definitions that can drift.

**Acceptance:** normal app imports perform no database writes or schema setup; app startup initializes the schema exactly once; the explicit seed command still creates/upgrades all existing tables and reproduces current seed counts; an existing DB is not reset or destructively migrated. Schema behavior is tested using a temporary DB as well as the ignored local DB.

### P1 — Request latency and search throughput

#### P1.1 — Blocking network/model calls inside async request handlers

The question-bank router declares async handlers that synchronously call `WebQuestionEngine.generate_questions()`. That path performs sequential `requests.get()` calls to Wikipedia and DuckDuckGo, optional Google Custom Search, and synchronous Gemini generation. A slow upstream can occupy the ASGI event-loop thread and delay unrelated requests.

**Acceptance:** synchronous question generation is run without blocking the event loop, using the existing dependencies (e.g. FastAPI/Starlette threadpool helper); preserve endpoint URLs, response schema, exactly-15 result contract, session refresh behaviour, and offline fallback. Configure/retain bounded upstream timeouts. When an upstream is slow/unreachable, unrelated status/content/search requests remain responsive. Do not replace synchronous dependencies or add packages without proving necessity.

#### P1.2 — Per-query repeated work in RAG search

`RAGIndex.search()` recomputes chunk token frequencies with `chunk.tokens.count(token)` for every resolved query term and repeatedly scans the vocabulary for prefix/fuzzy candidates. With 1,881 indexed chunks and ~2,886 vocabulary terms, this work is repeated per request.

**Acceptance:** cache/build token-frequency structures and a prefix lookup during atomic index rebuild, then score searches from cached data. Preserve the current ranking order to floating-point tolerance, typo/prefix resolution, deduplication, result fields, and empty-query behaviour. Benchmark representative queries before/after; no regression in the measured concurrent-query correctness test.

#### P1.3 — Cold index build happens in an async request

`RAGIndex.get_instance()` builds the complete index synchronously on first use. The first `/api/system/status` request calls it directly, and a first `/api/search` request may also build it. This pulls all questions, topics, and flashcards from SQLite and tokenizes them on the event-loop thread, making cold-start latency much worse than steady-state.

**Acceptance:** build/refresh the index during application startup using a threadpool or another non-blocking startup mechanism. Preserve status/search response schemas; readiness must not claim the index is ready until the build completes. A cold-start test verifies that the service becomes ready only after a successful build, and a concurrent lightweight route remains responsive during the build.
### P2 — Maintainability without feature loss

#### P2.1 — Exception handling obscures fallback cause

Several broad `except Exception: pass` blocks exist in database setup/fallback code and the research/generation pipeline. Keep recoverable upstream failures graceful, but distinguish optional-service failure from database/programming errors. Replace silent catches with narrowly scoped exception handling and structured logging (no secrets or raw API keys).

**Acceptance:** a simulated web timeout still falls back and returns the established output shape; a malformed DB/schema/JSON failure is not converted into a successful empty result; logs identify the failing optional source without credentials or full user content.

#### P2.2 — Duplicate connection/schema helper definitions and inconsistent repository method patterns

`database.py` and `database_init.py` each define a `get_connection()` with similar PRAGMAs; many repository methods repeat JSON field decoding and close patterns. Consolidation may be appropriate, but moving seed/schema code is high blast radius.

**Acceptance:** one canonical connection factory is used by runtime repository and seeding code, while the public import path used by `run.py`/seed scripts remains compatible. JSON decode defaults and returned shapes remain byte-for-byte equivalent where practical. No schema/table is removed.

#### P2.3 — Unused imports and dead code

Remove only imports/functions confirmed by a full repository reference search to be unused. Do not remove modules, routes, DB methods, or compatibility wrappers merely because their current UI caller is absent. The requirement is maintainability, not product-scope reduction.

**Acceptance:** static reference/import sweep shows no unresolved import; route inventory before and after is identical; existing tests pass; explicitly retained compatibility APIs remain importable.

## Design approach

### Stage 1 — Baseline capture

- Record route paths/methods and current response shapes for `/api/system/status`, `/api/metadata`, curriculum/content/interactive endpoints, `/api/search`, and all `/api/questions/*` routes.
- Record DB table names/counts and seed counts using a temporary DB copy; never run reset/seeding against the user's live DB during an audit.
- Capture baseline latency distributions (at least p50/p95) for `/api/search` with representative queries, `/api/system/status`, and question generation with mocked local HTTP responses. Record concurrency correctness and response schemas.

### Stage 2 — Correctness/resource safety first

- Make DB connection cleanup exception-safe with a small helper/context manager and migrate repository methods in tested groups.
- Refactor initialization to one startup initialization path and one canonical connection factory, preserving seed/migration entry points.
- Narrow exception handling. Preserve graceful fallback on external-service failures.
- Move the first `RAGIndex` build out of request handlers into the startup/readiness path, awaited without blocking the event loop.

### Stage 3 — Performance

- Offload synchronous question-generation work from async handlers; preserve request/response behaviour.
- Build an immutable or atomically swapped search index containing precomputed term-frequency data and prefix candidates. Keep existing atomic rebuild/thread-safety guarantees.
- Benchmark on the same corpus and representative queries. Only accept optimizations that improve measured latency or reduce repeated allocations while preserving ranking/output contracts.

### Stage 4 — Maintainability

- Consolidate duplicated repository transformations only where tests prove exact shape preservation.
- Audit unused imports and unreachable private code; remove only items proven unreferenced by a complete repository sweep and tests. Do not remove modules, routes, DB methods, compatibility wrappers, or any code with observable/support value merely because its current UI caller is absent.

## Testing and acceptance gates

1. Full existing unit suite passes: `python -m unittest tests.test_end_to_end`.
2. Full existing E2E suite passes: `python -m unittest tests.test_playwright_e2e`.
3. Route/method inventory before vs after is identical.
4. DB schema/table names and seeded counts are unchanged; no table drops or row deletion.
5. Every public JSON response retains its existing keys and meanings.
6. Query-result ranking for a fixed corpus/query set is unchanged except for verified duplicate elimination already present at baseline.
7. Search concurrency probe returns identical results/counts for repeated concurrent identical queries.
8. Simulated network timeout tests confirm the question endpoint returns its existing fallback response and unrelated endpoints remain responsive.
9. Connection tests inject a failing SQL/result-decoding operation and confirm the connection is closed.
10. Performance report compares before/after p50/p95 latency, throughput under concurrent search, and peak temporary allocation where measurable. No performance claim without recorded measurements.
11. No new runtime dependencies without a documented, separately approved justification.
12. Verify no secrets or local-only files are staged. Preserve the user's existing `run.py` port change and generated DLL unless the user separately asks otherwise.
13. Cold-start index build test verifies readiness waits for the index and that unrelated requests are not blocked during construction.

## Scope boundaries

In scope: Python backend runtime, repository/data access, DB initialization/connection lifecycle, search internals, question-generation request execution, backend tests and benchmarks.

Out of scope: landing-page redesign/copy; deleting or restoring user-facing features; changing frontend routes/flows; changing corpus contents; changing external service providers; schema redesign; deleting legacy DB tables; modifying GitHub remotes or pushing without a separate explicit request.

## Risks

- Moving DB initialization can expose hidden import-order assumptions. Mitigation: import-gate tests, fresh-temp-DB startup test, existing-DB test, and seed count comparison.
- Threadpool execution changes concurrency characteristics of session history. Mitigation: protect shared history/counter updates with a lock and add concurrent refresh tests; do not change session key semantics.
- Precomputed term frequencies consume memory. Mitigation: measure memory on the 1,881-chunk corpus and compare with request-time allocation; maintain an atomic index swap.
- Narrowing swallowed exceptions may reveal existing latent failures. Mitigation: add explicit fallback tests and log stack traces server-side without leaking user material.

## Explicit non-goals

This audit does not authorize removing any feature, API route, response field, database table, stored data, seed content, or supported input. Do not interpret "trim code" as permission to delete functionality.
