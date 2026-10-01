import os
import sys
import json
import re
import unittest
import asyncio

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.backend.database import DatabaseRepo
from src.backend.curriculum_questions import get_course_question_set
from src.c_core.c_bridge import (
    fast_levenshtein,
    fast_fuzzy_similarity,
    fast_bm25_term_score,
    fast_hash_string
)
from src.backend.web_question_engine import WebQuestionEngine


class TestWebQuestionEngine(unittest.TestCase):
    def test_generate_15_questions(self):
        res = WebQuestionEngine.generate_questions("CS201", "Design & Analysis of Algorithms", "Asymptotic Analysis", session_id="test_s1")
        self.assertEqual(res["total"], 15)
        self.assertEqual(len(res["questions"]), 15)
        for q in res["questions"]:
            self.assertIn("question_text", q)
            self.assertIn("difficulty", q)
            self.assertIn("marks", q)
            self.assertIn("id", q)

    def test_refresh_generates_distinct_sets(self):
        sess_id = "test_refresh_sess"
        set_a = WebQuestionEngine.generate_questions("CS101", "Programming in C", "Topic 1: Fundamentals of C", session_id=sess_id, force_refresh=False)
        self.assertEqual(len(set_a["questions"]), 15)

        set_b = WebQuestionEngine.generate_questions("CS101", "Programming in C", "Topic 1: Fundamentals of C", session_id=sess_id, force_refresh=True)
        self.assertEqual(len(set_b["questions"]), 15)

        texts_a = [q["question_text"] for q in set_a["questions"]]
        texts_b = [q["question_text"] for q in set_b["questions"]]
        
        # Verify Set A and Set B are distinct
        overlap = set(texts_a).intersection(set(texts_b))
        self.assertEqual(len(overlap), 0, "Refresh produced duplicate questions across consecutive sets")

    def test_topic_change_generates_specific_questions(self):
        sess_id = "test_topic_sess"
        res_topic1 = WebQuestionEngine.generate_questions("CS101", "Programming in C", "Topic 1: Fundamentals of C", session_id=sess_id)
        res_topic2 = WebQuestionEngine.generate_questions("PH101", "Engineering Physics", "Topic 2: Physical Optics & Lasers", session_id=sess_id)
        
        self.assertEqual(len(res_topic1["questions"]), 15)
        self.assertEqual(len(res_topic2["questions"]), 15)
        self.assertEqual(res_topic1["course_code"], "CS101")
        self.assertEqual(res_topic2["course_code"], "PH101")


class TestCoursePageIntegrity(unittest.TestCase):
    def setUp(self):
        course_path = os.path.join(ROOT_DIR, "src", "static", "templates", "course.html")
        with open(course_path, "r", encoding="utf-8") as f:
            self.course_html = f.read()

    def test_set1_badge_removed(self):
        # Requirement 1: Remove "Set 1" blue icon/badge completely
        self.assertNotIn('id="current-set-badge"', self.course_html)
        self.assertNotIn('>Set 1<', self.course_html)

    def test_switch_set2_changed_to_refresh(self):
        # Requirement 2: Change "Switch Set 2" to "Refresh"
        self.assertNotIn('Switch to Set 2', self.course_html)
        self.assertNotIn('Switch Set 2', self.course_html)
        self.assertIn('<span>Refresh</span>', self.course_html)

    def test_topic_selector_present(self):
        # Course -> Topic selection controls
        self.assertIn('id="topic-select"', self.course_html)


class TestCBridge(unittest.TestCase):
    def test_fast_levenshtein(self):
        self.assertEqual(fast_levenshtein("kitten", "sitting"), 3)
        self.assertEqual(fast_levenshtein("same", "same"), 0)
        self.assertEqual(fast_levenshtein("", "test"), 4)
        self.assertEqual(fast_levenshtein(None, "test"), 4)

    def test_fast_fuzzy_similarity(self):
        self.assertAlmostEqual(fast_fuzzy_similarity("hello", "hello"), 1.0)
        self.assertGreater(fast_fuzzy_similarity("Data Structures", "Data Structure"), 0.9)
        self.assertEqual(fast_fuzzy_similarity(None, None), 1.0)
        self.assertEqual(fast_fuzzy_similarity(None, "DSA"), 0.0)

    def test_fast_bm25_and_hash(self):
        score = fast_bm25_term_score(tf=2, doc_len=100, avg_doc_len=120, doc_count=50, df=5)
        self.assertGreater(score, 0.0)
        h = fast_hash_string("test_string")
        self.assertIsInstance(h, int)


class TestDatabaseAndCurriculum(unittest.TestCase):
    def test_curriculum_retrieval(self):
        curriculum = DatabaseRepo.get_curriculum()
        self.assertIsInstance(curriculum, list)
        self.assertGreater(len(curriculum), 0)

    def test_course_by_code(self):
        course = DatabaseRepo.get_curriculum_by_code("CS201")
        self.assertIsNotNone(course)
        self.assertEqual(course.get("code"), "CS201")

    def test_question_bank_sets(self):
        set1 = get_course_question_set("CS201", set_num=1)
        self.assertIsInstance(set1, list)
        self.assertGreater(len(set1), 0)
        set2 = get_course_question_set("CS201", set_num=2)
        self.assertIsInstance(set2, list)
        self.assertGreater(len(set2), 0)

    def test_assignments_crud(self):
        created = DatabaseRepo.create_assignment({
            "title": "Test Assignment",
            "college": "Test College",
            "department": "CSE",
            "subject": "Testing",
            "semester": "1",
            "academic_year": "2026",
            "difficulty": "Easy",
            "due_date": "2026-12-31",
            "status": "Active",
            "questions": [{"num": 1, "text": "Test question?", "marks": 5}]
        })
        self.assertIn("id", created)
        aid = created["id"]
        
        fetched = DatabaseRepo.get_assignment_by_id(aid)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["title"], "Test Assignment")
        
        updated = DatabaseRepo.update_assignment(aid, {"title": "Updated Test Assignment"})
        self.assertEqual(updated["title"], "Updated Test Assignment")
        
        deleted = DatabaseRepo.delete_assignment(aid)
        self.assertTrue(deleted)
        self.assertIsNone(DatabaseRepo.get_assignment_by_id(aid))

    def test_get_question_bank_for_index_returns_approved_rows(self):
        rows = DatabaseRepo.get_question_bank_for_index()
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 1000, "expected the seeded 1740-question corpus")
        first = rows[0]
        for key in ("id", "question_text", "subject", "topic", "difficulty", "marks"):
            self.assertIn(key, first, f"missing key {key}")

    def test_get_question_bank_for_index_excludes_non_approved(self):
        # Every seeded row is Approved, so the filter cannot be observed by
        # counting alone. Insert a Rejected row, prove it is excluded, then
        # remove it so the test leaves no trace.
        from src.backend.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        marker = "ZZZ-REJECTED-PROBE-QUESTION"
        try:
            cursor.execute(
                "INSERT INTO question_bank (id, question_text, subject, topic, source_type, "
                "difficulty, question_type, marks, status, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("probe-rejected-1", marker, "ZZ999", "Probe", "AI_Generated",
                 "Easy", "Exam", 5, "Rejected", "2026-01-01T00:00:00", "2026-01-01T00:00:00"),
            )
            conn.commit()

            rows = DatabaseRepo.get_question_bank_for_index()
            self.assertNotIn(
                marker, [r["question_text"] for r in rows],
                "a Rejected question leaked into the index results"
            )
        finally:
            cursor.execute("DELETE FROM question_bank WHERE id = ?", ("probe-rejected-1",))
            conn.commit()
            conn.close()

        rows_after = DatabaseRepo.get_question_bank_for_index()
        self.assertGreater(len(rows_after), 1000, "probe cleanup left the corpus damaged")

    def test_get_all_interactive_content_returns_every_course(self):
        rows = DatabaseRepo.get_all_interactive_content()
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 50)
        codes = {r["course_code"] for r in rows}
        self.assertGreater(len(codes), 5, "expected multiple courses, not one")
        for key in ("front_text", "back_text"):
            self.assertIn(key, rows[0])


class _OldFrontendIntegrityPlaceholder(unittest.TestCase):
    pass


class TestRemovedRoutes(unittest.TestCase):
    """Routes deleted by the cleanup must be gone, not silently returning null."""

    def test_pyq_similar_route_is_removed(self):
        from src.backend.question_bank_api import router
        paths = {r.path for r in router.routes}
        self.assertNotIn("/api/questions/generate/pyq-similar", paths)

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

    def _route_paths(self):
        """Collect route paths, descending into included sub-routers.

        app.routes mixes APIRoute/Mount with _IncludedRouter objects, which have
        no .path of their own, so a naive {r.path for r in app.routes} raises.
        """
        import importlib
        from fastapi.routing import APIRoute
        app = importlib.import_module("src.backend.app").app
        paths = set()
        for r in app.routes:
            p = getattr(r, "path", None)
            if p:
                paths.add(p)
            for sub in getattr(r, "routes", []) or []:
                if isinstance(sub, APIRoute):
                    paths.add(getattr(sub, "path", ""))
        return paths

    def test_route_count_is_reduced(self):
        paths = self._route_paths()
        for gone in ("/api/notebooks/upload", "/api/help/evaluate", "/api/quiz/generate",
                     "/api/chat/message", "/api/assignments", "/api/pyq/search",
                     "/api/generator/create", "/api/notes/generate", "/api/progress",
                     "/api/recommendations"):
            self.assertNotIn(gone, paths, f"route should be gone: {gone}")

    def test_live_routes_are_retained(self):
        paths = self._route_paths()
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


class TestRAGIndex(unittest.TestCase):
    def _fresh(self):
        from src.backend.rag_engine import RAGIndex
        idx = RAGIndex()
        idx.rebuild_index()
        return idx

    def test_index_covers_the_real_corpus(self):
        idx = self._fresh()
        self.assertGreater(len(idx.chunks), 1500,
                           "expected 1740 questions + 57 topics + 84 flashcards")
        kinds = {c.doc_type for c in idx.chunks}
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
        # Every token here is in the tokenizer's stopword list or under the
        # 3-char cutoff, so nothing survives tokenization. (Note: "what" is NOT
        # a safe example for this - it is a real corpus term, so a query
        # containing it legitimately matches.)
        from src.backend.rag_engine import RAGIndex
        self.assertEqual(RAGIndex().search("the of and"), [])
        self.assertEqual(RAGIndex().search("is are was were"), [])

    def test_empty_query_returns_empty(self):
        from src.backend.rag_engine import RAGIndex
        self.assertEqual(RAGIndex().search(""), [])

    def test_topic_context_is_populated(self):
        from src.backend.rag_engine import RAGIndex
        ctx = RAGIndex().get_topic_context("dynamic programming knapsack")
        self.assertIsNotNone(ctx)
        for key in ("summary", "formulas", "key_points"):
            self.assertIn(key, ctx)

    def test_search_results_have_no_duplicate_questions(self):
        """Every question is seeded twice (code + name); search must not show both."""
        from src.backend.rag_engine import RAGIndex
        for q in ("avl tree rottaions", "dijkstra negative weights", "deadlok prevention"):
            results = RAGIndex().search(q, top_k=12)
            texts = [r["text"] for r in results if r["source_type"] == "question"]
            self.assertEqual(len(texts), len(set(texts)),
                             f"duplicate question in results for {q!r}")

    def test_search_results_use_course_codes(self):
        """Subject must be a real curriculum code so links resolve to a course page."""
        from src.backend.rag_engine import RAGIndex
        from src.backend.database import DatabaseRepo
        valid = {c["code"] for c in DatabaseRepo.get_curriculum()}
        for q in ("avl tree rottaions", "dijkstra negative weights"):
            results = RAGIndex().search(q, top_k=12)
            questions = [r for r in results if r["source_type"] == "question"]
            self.assertTrue(questions, f"no question hits for {q!r}")
            for r in questions:
                self.assertIn(r["subject"], valid,
                              f"subject {r['subject']!r} is not a curriculum code")

    def test_search_resolves_topic_to_a_real_unit(self):
        """Placeholder topics like 'Topic 1' must become real unit names.

        Unit names come from the whole study_content catalogue, which is a
        superset of topic_content (e.g. 'DC Circuits' exists as a unit but has
        no topic_content row). So assert against the resolver's own catalogue
        rather than one table.
        """
        from src.backend.rag_engine import RAGIndex
        index = RAGIndex.get_instance()
        known = {name for units in index._units_by_course.values()
                 for name in units.values()}
        known |= {t["topic_name"] for t in index.topic_rows.values()}

        results = index.search("avl tree rottaions", top_k=12)
        questions = [r for r in results if r["source_type"] == "question"]
        self.assertTrue(questions)
        resolved = [r for r in questions if r["topic"] in known]
        self.assertTrue(resolved, "no result resolved to a real syllabus unit")
        # Nothing should be left as a bare positional placeholder when the
        # question clearly names its subject matter.
        self.assertTrue(
            any(r["topic"] not in ("Topic 1", "Topic 2", "Topic 3") for r in questions),
            "every question still carries a positional placeholder topic",
        )
        self.assertIn(index.get_topic_context("avl tree rottaions")["topic"], known)

    def test_topic_resolution_does_not_invent_labels(self):
        """A question naming no unit must keep its placeholder, not borrow one."""
        from src.backend.rag_engine import RAGIndex
        index = RAGIndex.get_instance()
        known = {name for units in index._units_by_course.values()
                 for name in units.values()}
        rows = index._resolve_unit("CH101", {
            "topic": "Topic 1",
            "question_text": "Explain scalability bottlenecks in Spark. Answer: sharding.",
        })
        self.assertTrue(rows in known or rows == "Topic 1",
                        f"unmatched question got an invented unit: {rows!r}")

    def test_search_still_fills_the_requested_limit_after_dedup(self):
        """Dedup must over-fetch, otherwise duplicates consume slots and results shrink."""
        from src.backend.rag_engine import RAGIndex
        results = RAGIndex().search("avl tree rottaions", top_k=8)
        questions = [r for r in results if r["source_type"] == "question"]
        self.assertGreaterEqual(len(questions), 6,
                                f"dedup starved the result list: only {len(questions)} of 8")


class TestSearchEndpoint(unittest.TestCase):
    def _client(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        return TestClient(app)

    def test_search_endpoint_returns_results(self):
        r = self._client().get("/api/search", params={"q": "avl tree rottaions"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["query"], "avl tree rottaions")
        self.assertGreater(data["total"], 0)
        self.assertIn("results", data)
        self.assertIn("topic_context", data)

    def test_search_endpoint_rejects_empty_query(self):
        r = self._client().get("/api/search", params={"q": "   "})
        self.assertEqual(r.status_code, 400)

    def test_search_endpoint_rejects_stopword_only_query(self):
        r = self._client().get("/api/search", params={"q": "the of and"})
        self.assertEqual(r.status_code, 400)

    def test_search_endpoint_gibberish_is_200_with_empty_results(self):
        r = self._client().get("/api/search", params={"q": "zxcvqw nonsense"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["total"], 0)

    def test_search_endpoint_caps_limit(self):
        # FastAPI validates limit=ge=1,le=50 itself, so an over-max request is a
        # 422 rather than a silently clamped 200. That is the intended contract:
        # reject a bad limit instead of quietly returning a different size.
        r = self._client().get("/api/search", params={"q": "algorithm", "limit": 9999})
        self.assertEqual(r.status_code, 422)

    def test_search_endpoint_respects_limit(self):
        r = self._client().get("/api/search", params={"q": "algorithm", "limit": 3})
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(r.json()["results"]), 3)


class _OldFrontendIntegrityPlaceholder(unittest.TestCase):
    pass


class TestStatusShape(unittest.TestCase):
    def test_status_keeps_all_keys(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        data = TestClient(app).get("/api/system/status").json()
        for key in ("status", "c_core_accelerated", "gemini_api_configured",
                    "total_assignments", "total_notebooks", "indexed_rag_chunks",
                    "available_colleges", "available_subjects", "timestamp"):
            self.assertIn(key, data, f"status key removed: {key}")
        self.assertEqual(data["status"], "online")

    def test_dropped_dependencies_are_not_imported(self):
        """pypdf, python-docx and numpy went away with the OCR upload path."""
        import ast
        import pathlib
        banned = ("pypdf", "docx", "numpy")
        for f in (pathlib.Path(ROOT_DIR) / "src").rglob("*.py"):
            tree = ast.parse(f.read_text(encoding="utf-8", errors="ignore"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        self.assertNotIn(a.name.split(".")[0], banned,
                                         f"{f.name} imports {a.name}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], banned,
                                     f"{f.name} imports from {node.module}")

    def test_requirements_drop_ocr_only_packages(self):
        with open(os.path.join(ROOT_DIR, "requirements.txt"), encoding="utf-8") as fh:
            text = fh.read()
        for gone in ("pypdf", "python-docx", "numpy"):
            self.assertNotIn(gone, text, f"requirements.txt still lists {gone}")
        self.assertIn("fastapi", text)
        # Pillow stays: c_bridge still imports it for the image helpers.
        self.assertIn("Pillow", text)


class TestFrontendIntegrity(unittest.TestCase):
    def setUp(self):
        template_path = os.path.join(ROOT_DIR, "src", "static", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()

    def test_generate_study_kit_calls_the_search_api(self):
        i = self.index_html.index("function generateStudyKit")
        body = self.index_html[i:i + 3000]
        self.assertIn("/api/search", body, "generateStudyKit still does not call the backend")
        self.assertNotIn("alert(", body, "must not use alert(); render an inline error")

    def test_presets_no_longer_carry_hardcoded_output(self):
        i = self.index_html.index("const PRESETS")
        j = self.index_html.index("function loadSampleData")
        presets = self.index_html[i:j]
        self.assertNotIn("summaries", presets, "PRESETS still hardcodes summaries")
        self.assertNotIn("flashcards", presets, "PRESETS still hardcodes flashcards")
        self.assertIn("text", presets, "PRESETS must keep its real lecture text")

    def test_flashcard_deck_contract_is_preserved(self):
        """The single-card 3D deck is existing behaviour; it must not be replaced."""
        for token in ("currentDeck", "function updateDeckView", "function flipCard",
                      "flashcardModel", "fcQuestion", "fcAnswer"):
            self.assertIn(token, self.index_html, f"flashcard deck contract broken: {token}")
        self.assertNotIn("flashcardContainer", self.index_html,
                         "do not replace the single-card deck with a card list")

    def test_study_desk_has_an_error_element(self):
        self.assertIn('id="studyKitError"', self.index_html,
                      "no inline error element for failed searches")

    def test_navbar_anchors_exist_problem_002(self):
        # Problem 002 fix verification: navbar links must point to existing section IDs
        nav_matches = re.findall(r'<ul class="nav-links">([\s\S]*?)</ul>', self.index_html)
        self.assertTrue(len(nav_matches) > 0)
        links = re.findall(r'href="#([^"]+)"', nav_matches[0])
        self.assertTrue(len(links) >= 3)
        for anchor_id in links:
            id_pattern = rf'id="{anchor_id}"'
            self.assertRegex(
                self.index_html,
                id_pattern,
                f"Navbar link #{anchor_id} does not correspond to an element with id='{anchor_id}'"
            )

    def test_no_dead_links_in_navbar(self):
        self.assertNotIn('href="#workflow"', self.index_html)
        self.assertNotIn('href="#roadmap"', self.index_html)

    def test_load_sample_data_robustness_problem_005(self):
        # Problem 005 fix verification: loadSampleData must not rely on implicit global event
        self.assertIn("function loadSampleData(key, el)", self.index_html)
        self.assertNotIn("if (event && event.target", self.index_html)
class TestFastAPIRoutes(unittest.TestCase):
    def _client(self):
        from fastapi.testclient import TestClient
        from src.backend.app import app
        return TestClient(app)

    def test_system_status_endpoint(self):
        res = self._client().get("/api/system/status")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("status"), "online")

    def test_index_page_is_served(self):
        res = self._client().get("/")
        self.assertEqual(res.status_code, 200)

    def test_course_page_is_served(self):
        res = self._client().get("/course.html")
        self.assertEqual(res.status_code, 200)

    def test_curriculum_endpoints(self):
        c = self._client()
        self.assertEqual(c.get("/api/curriculum").status_code, 200)
        self.assertEqual(c.get("/api/curriculum/full").status_code, 200)
        self.assertEqual(c.get("/api/curriculum/CS201").status_code, 200)

    def test_content_and_interactive_endpoints(self):
        c = self._client()
        self.assertEqual(c.get("/api/content/CS201").status_code, 200)
        self.assertEqual(c.get("/api/interactive/CS201").status_code, 200)

    def test_question_bank_course_endpoint_returns_15(self):
        res = self._client().get("/api/questions/course/CS201")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body.get("total"), 15)
        self.assertEqual(len(body.get("questions", [])), 15)


if __name__ == "__main__":
    unittest.main()
