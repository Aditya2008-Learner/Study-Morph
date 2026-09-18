==================================================
FINAL IMPLEMENTATION REPORT
==================================================

1. FILES MODIFIED
----------------
Backend:
- src/backend/web_question_engine.py  (NEW — web-researched dynamic question engine with anti-duplication)
- src/backend/question_bank_api.py  (MODIFIED — new /api/questions/course endpoint returns fresh 15 questions; refresh endpoint added)
- src/backend/app.py                 (MINOR — no changes needed; question_bank_api router already included)

Frontend (course.html):
- src/static/templates/course.html  (MODIFIED — removed "Set 1" badge, changed "Switch Set 2" to "Refresh" with refresh icon, added topic dropdown, updated loadQuestionsData/refreshQuestions logic, added session_id for anti-dup)

Tests:
- tests/test_end_to_end.py           (UPDATED — added web engine, refresh flow, frontend integrity tests)
- tests/test_playwright_e2e.py       (NEW — Playwright E2E test verifying 15 questions, no "Set 1", "Refresh" button, 3 distinct sets, different questions on refresh, no console errors)

2. HOW THE NEW REFRESH FLOW WORKS
------------------------------------
- User selects a course (e.g., CS201) and optional topic.
- The frontend calls GET /api/questions/course/{course_code}?topic=...&refresh=true (or false for initial load).
- The backend (WebQuestionEngine) determines the current course/topic, conducts live web/academic research (Wikipedia + DuckDuckGo + optional Google Search API), generates 15 academic questions via AI (Gemini) or algorithmic synthesis, applies anti-duplicate filtering, validates all 15 have required fields, and returns the set.
- For every refresh click: a new web search is performed, new questions are generated (different archetypes/nounces/subtopics/difficulties), previous session questions are used for exclusion, and exactly 15 new questions are produced.

3. WEB/GOOGLE SEARCH MECHANISM
--------------------------------
- Wikipedia Academic Search API (en.wikipedia.org action=query, prop=extracts, list=search) — always used.
- DuckDuckGo Lite (html.duckduckgo.com/lite) — always used.
- Optional Google Custom Search (if GOOGLE_SEARCH_API_KEY + GOOGLE_CSE_ID set) — uses customsearch/v1 endpoint; reads credentials from .env / environment variables.
- No API keys hardcoded in code. No keys exposed to frontend.

4. AI GENERATION MECHANISM
--------------------------
- Uses AIEngine.is_gemini_available() and AIEngine._call_gemini_llm().
- If Gemini is available: Sends a richly structured prompt including live web research context, strict exclusions based on previous session questions, a unique generation nonce (refresh_num + UUID), a strict 15-question JSON output format with difficulty/type/marks/subtopic fields, and asks for exactly 15 items covering the 3-6-4-2 difficulty distribution.
- If Gemini is unavailable or fails: Falls back to _synthesize_academic_questions(), which creates diverse questions from 15 archetypes (Conceptual, Definition, Numerical, Analytical, Algorithmic, Proof, Trade-offs, Security, Optimization, Distributed, System Design, Deep Synthesis, etc.), using the web research text for terminology and varying parameters based on refresh_num (nonce) so each refresh produces genuinely different content.

5. HOW DUPLICATE QUESTIONS ARE PREVENTED
-----------------------------------------
- WebQuestionEngine._SESSION_HISTORY (global dictionary, in-memory) stores generated question texts per session/course/topic.
- Every generation request reads previous session texts.
- Before returning final questions, _deduplicate_and_enforce_15():
  - Removes exact duplicates within the new batch.
  - Checks fuzzy similarity (>0.70) within new batch.
  - Checks fuzzy similarity (>0.75) against previous session questions.
  - If duplicates detected, regenerates unique questions using synthesis.
- The refresh endpoint passes force_refresh=True, which increases refresh_num and varies archetype parameters (nonce, subtopic naming, numerical values) to guarantee variation.

6. HOW EXACTLY 15 QUESTIONS ARE ENFORCED
-----------------------------------------
- The backend validates: len(final_list) == 15 before returning. If fewer, it synthesizes additional unique questions. If more, it trims to 15.
- The final list ensures exactly 15 entries with valid id, question_text, difficulty, marks, subtopic, question_type, subject, topic fields.
- The Playwright E2E test asserts len(q_cards) == 15 for Set A, Set B, Set C, and different topic/course combinations.

7. TESTS PERFORMED
------------------
- Python unit tests (tests/test_end_to_end.py): 28 tests pass (database, quiz engine, scraper, frontend integrity, web engine).
- Playwright E2E test (tests/test_playwright_e2e.py): Verified full flow:
  - "Set 1" badge removed.
  - "Switch Set 2" text removed; "Refresh" visible.
  - Exactly 15 questions load for CS201.
  - 15 different questions after first refresh.
  - 15 different questions after second refresh (set C different from B).
  - Topic dropdown works and generates 15 new questions for new topic.
  - Changing course (CS101) works.
  - Solution drawer opens and contains "Verified Solution".
  - Zero console errors during flow.
- Manual backend import check: No syntax errors; all Python files compile.
- Existing database tables preserved (curriculum, assignments, question_bank, etc.).

8. PROBLEMS / LIMITATIONS
--------------------------
- The Playwright test requires the server to be running in a separate thread; it passes in isolation but needs uvicorn available.
- Web research relies on Wikipedia and DuckDuckGo; if these services are unreachable, the engine synthesizes questions from internal academic templates rather than returning database questions (as required by instruction 10).
- Gemini AI requires a valid GEMINI_API_KEY; without it, synthesis mode produces high-quality but slightly more standardized questions based on archetypes.
- Each refresh takes 2-5 seconds due to live web requests (Wikipedia + DDG) + generation time. The button is debounced/disabled during active requests (isGenerating flag in frontend, disabled attribute).
- Questions contain academic-level content; some generated text uses LaTeX-style formulas ($...$) which are already handled by the existing renderEquations() system in the frontend.

==================================================
IMPLEMENTATION SUMMARY (CONCISE)
==================================================
Modified files:
- src/backend/web_question_engine.py (new dynamic engine)
- src/backend/question_bank_api.py (new endpoint behavior)
- src/static/templates/course.html (UI updates + JavaScript flow)
- tests/test_end_to_end.py + tests/test_playwright_e2e.py

Refresh flow:
1. User selects course/topic.
2. Click Refresh triggers fetch with session_id and refresh=true.
3. Backend conducts Wikipedia/DDG/optional Google research.
4. Engine generates exactly 15 diverse questions (AI or synthesis), excludes previous session duplicates via fuzzy similarity checks.
5. Exactly 15 validated questions returned.

Anti-duplication: Session history + fuzzy similarity + refresh nonce (refresh_num + UUID).
Exactly 15 enforced: Backend trims/pads to 15; asserts verified.
No database questions used: Database tables untouched; all questions come from new research.
No redesign: Only badge removed, text changed, button updated, underlying behavior changed.
