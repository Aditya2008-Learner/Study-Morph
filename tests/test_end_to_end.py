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


class TestFrontendIntegrity(unittest.TestCase):
    def setUp(self):
        template_path = os.path.join(ROOT_DIR, "src", "static", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            self.index_html = f.read()

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
