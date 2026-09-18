import os
import sys
import time
import socket
import unittest
import threading
import uvicorn
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.backend.app import app


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class TestPlaywrightCourseE2E(unittest.TestCase):
    server_thread = None
    server = None
    port = None

    @classmethod
    def setUpClass(cls):
        cls.port = get_free_port()
        config = uvicorn.Config(app, host="127.0.0.1", port=cls.port, log_level="error")
        cls.server = uvicorn.Server(config)
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()
        time.sleep(1.5)

    @classmethod
    def tearDownClass(cls):
        if cls.server:
            cls.server.should_exit = True

    def test_full_course_question_refresh_flow(self):
        console_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # Listen for console errors
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            base_url = f"http://127.0.0.1:{self.port}"
            page.goto(f"{base_url}/course.html?course=CS201", wait_until="networkidle")

            # 1. Confirm "Set 1" blue icon/badge is gone
            set1_badge = page.query_selector("#current-set-badge")
            self.assertIsNone(set1_badge, "Badge #current-set-badge should be completely removed")
            
            body_text = page.inner_text("body")
            self.assertNotIn("Set 1", page.inner_text(".qb-header-bar"))
            self.assertNotIn("Switch to Set 2", body_text)
            self.assertNotIn("Switch Set 2", body_text)

            # 2. Confirm the button says "Refresh"
            refresh_btn = page.wait_for_selector("#btn-toggle-set", timeout=5000)
            self.assertIsNotNone(refresh_btn)
            self.assertEqual(refresh_btn.inner_text().strip(), "Refresh")

            # 3. Wait for initial 15 questions to load
            page.wait_for_selector(".question-card", timeout=10000)
            q_cards_a = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_a), 15, f"Expected 15 questions in Set A, got {len(q_cards_a)}")

            set_a_texts = [card.query_selector(".question-text").inner_text().strip() for card in q_cards_a]
            # Ensure no duplicates within Set A
            self.assertEqual(len(set(set_a_texts)), 15, "Set A contains duplicate questions")

            # 4. Click Refresh button
            refresh_btn.click()

            # Wait for questions container to finish updating
            page.wait_for_selector("#btn-toggle-set:not([disabled])", timeout=10000)
            page.wait_for_timeout(500)

            q_cards_b = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_b), 15, f"Expected 15 questions in Set B, got {len(q_cards_b)}")

            set_b_texts = [card.query_selector(".question-text").inner_text().strip() for card in q_cards_b]
            self.assertEqual(len(set(set_b_texts)), 15, "Set B contains duplicate questions")

            # 5. Compare Set A and Set B (must be genuinely different)
            overlap_ab = set(set_a_texts).intersection(set(set_b_texts))
            self.assertEqual(len(overlap_ab), 0, f"Overlap detected between Set A and Set B: {overlap_ab}")

            # 6. Click Refresh again for Set C
            refresh_btn.click()
            page.wait_for_selector("#btn-toggle-set:not([disabled])", timeout=10000)
            page.wait_for_timeout(500)

            q_cards_c = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_c), 15, f"Expected 15 questions in Set C, got {len(q_cards_c)}")

            set_c_texts = [card.query_selector(".question-text").inner_text().strip() for card in q_cards_c]
            self.assertEqual(len(set(set_c_texts)), 15, "Set C contains duplicate questions")

            overlap_bc = set(set_b_texts).intersection(set(set_c_texts))
            self.assertEqual(len(overlap_bc), 0, f"Overlap detected between Set B and Set C: {overlap_bc}")

            # 7. Change Topic via dropdown
            topic_select = page.wait_for_selector("#topic-select", timeout=5000)
            self.assertIsNotNone(topic_select)
            
            # Select Topic 2
            page.select_option("#topic-select", index=1)
            page.wait_for_selector("#btn-toggle-set:not([disabled])", timeout=10000)
            page.wait_for_timeout(500)

            q_cards_topic = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_topic), 15)

            # 8. Change Course to CS101 (Programming in C)
            page.select_option("#course-select", value="CS101")
            page.wait_for_selector("#btn-toggle-set:not([disabled])", timeout=10000)
            page.wait_for_timeout(500)

            q_cards_c101 = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_c101), 15)

            # Verify topic selector updated with C topics
            topic_options = page.eval_on_selector_all("#topic-select option", "opts => opts.map(o => o.value)")
            self.assertTrue(any("Fundamentals of C" in opt or "Pointers" in opt for opt in topic_options))

            # Select Pointers topic
            page.select_option("#topic-select", index=2)
            page.wait_for_selector("#btn-toggle-set:not([disabled])", timeout=10000)
            page.wait_for_timeout(500)

            q_cards_pointers = page.query_selector_all(".question-card")
            self.assertEqual(len(q_cards_pointers), 15)

            # 9. Test Solution Drawer expansion
            first_card = q_cards_pointers[0]
            sol_btn = first_card.query_selector("button")
            self.assertIsNotNone(sol_btn)
            sol_btn.click()
            page.wait_for_timeout(200)

            drawer = first_card.query_selector(".solution-drawer")
            self.assertIn("open", drawer.get_attribute("class"))
            self.assertIn("verified solution", drawer.inner_text().lower())

            # 10. Verify 0 console errors
            self.assertEqual(len(console_errors), 0, f"Console errors observed: {console_errors}")

            browser.close()


if __name__ == "__main__":
    unittest.main()
