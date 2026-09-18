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
from src.backend.quiz_engine import QuizEngine
from src.backend.scraper import PYQScraper
from src.c_core.c_bridge import (
    fast_levenshtein,
    fast_fuzzy_similarity,
    fast_bm25_term_score,
    fast_hash_string
)
from src.backend.web_question_engine import WebQuestionEngine
from src.backend.question_bank_api import get_course_questions, refresh_course_questions
from src.backend.app import (
    app,
    search_pyq,
    submit_quiz,
    generate_quiz,
    get_curriculum,
    get_system_status,
    get_topic_content,
    batch_export
)


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


class TestQuizEngine(unittest.TestCase):
    def setUp(self):
        self.quiz = QuizEngine.generate_quiz(
            subject="CS201",
            topic="Asymptotic Analysis",
            num_questions=3
        )
        self.quiz_id = self.quiz["id"]

    def test_quiz_submit_with_list_payload(self):
        answers_list = [
            {"question_id": "q1", "selected_index": 1},
            {"question_id": "q2", "selected_index": 1}
        ]
        result = QuizEngine.grade_attempt(self.quiz_id, answers_list, time_taken=45)
        self.assertIn("score", result)
        self.assertIn("percentage", result)
        self.assertIn("answers", result)

    def test_quiz_submit_with_dict_payload_problem_001(self):
        # Problem 001 fix verification: payload as a dict of {question_id: selected_index}
        answers_dict = {"q1": 1, "q2": 0}
        result = QuizEngine.grade_attempt(self.quiz_id, answers_dict, time_taken=30)
        self.assertIn("score", result)
        self.assertIn("percentage", result)
        self.assertEqual(len(result["answers"]), len(self.quiz["questions"]))

    def test_quiz_submit_with_nested_dict_payload(self):
        answers_nested = {"answers": {"q1": 1, "q2": 1}}
        result = QuizEngine.grade_attempt(self.quiz_id, answers_nested, time_taken=20)
        self.assertIn("score", result)
        self.assertIn("percentage", result)

    def test_quiz_submit_with_empty_or_malformed_answers(self):
        result_empty = QuizEngine.grade_attempt(self.quiz_id, {}, time_taken=10)
        self.assertEqual(result_empty["score"], 0.0)

        result_invalid_list = QuizEngine.grade_attempt(self.quiz_id, ["invalid", None, 123], time_taken=10)
        self.assertEqual(result_invalid_list["score"], 0.0)


class TestPYQSearch(unittest.TestCase):
    def test_search_pyq_with_subject(self):
        results = PYQScraper.search_online_pyq(subject="Data Structures")
        self.assertIsInstance(results, list)

    def test_search_pyq_without_subject_problem_003(self):
        # Problem 003 fix verification: search without query parameters should not crash
        results = PYQScraper.search_online_pyq(subject=None)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)


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
    def test_async_system_status(self):
        res = asyncio.run(get_system_status())
        self.assertEqual(res.get("status"), "online")

    def test_async_pyq_search_no_params(self):
        res = asyncio.run(search_pyq(subject=None))
        self.assertIsInstance(res, list)

    def test_async_quiz_submit_dict_format(self):
        quiz_res = asyncio.run(generate_quiz({
            "subject": "CS201",
            "topic": "Asymptotic Analysis",
            "num_questions": 3
        }))
        quiz_id = quiz_res["id"]
        
        # Test submitting dictionary formatted answers
        submit_payload = {
            "answers": {"q1": 1, "q2": 1},
            "time_taken_seconds": 25
        }
        res = asyncio.run(submit_quiz(quiz_id, submit_payload))
        self.assertIn("score", res)
        self.assertIn("percentage", res)

    def test_async_batch_export_json_and_markdown(self):
        res_json = asyncio.run(batch_export({"format": "json"}))
        self.assertIsNotNone(res_json)
        res_md = asyncio.run(batch_export({"format": "markdown"}))
        self.assertIsNotNone(res_md)

    def test_async_question_bank_web_generator_endpoint(self):
        res = asyncio.run(get_course_questions("CS201", refresh=False))
        self.assertEqual(res.get("total"), 15)
        self.assertEqual(len(res.get("questions", [])), 15)

    def test_async_question_bank_refresh_endpoint(self):
        res = asyncio.run(refresh_course_questions("CS201", {"subject": "Algorithms", "topic": "Asymptotic Analysis"}))
        self.assertEqual(res.get("total"), 15)
        self.assertEqual(len(res.get("questions", [])), 15)


if __name__ == "__main__":
    unittest.main()
