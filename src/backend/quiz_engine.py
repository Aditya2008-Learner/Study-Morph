import os
import re
import json
import uuid
from typing import List, Dict, Any, Optional

from .ai_engine import AIEngine
from .database import DatabaseRepo

class QuizEngine:
    @staticmethod
    def generate_quiz(
        notebook_id: Optional[str] = None,
        subject: str = "Computer Science",
        topic: str = "General",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        context_text = ""
        if notebook_id:
            nb = DatabaseRepo.get_notebook_by_id(notebook_id)
            if nb:
                context_text = nb.get("raw_text", "")
                subject = nb.get("subject") or subject
                topic = (nb.get("extracted_topics") or [topic])[0]

        if AIEngine.is_gemini_available():
            prompt = f"""Generate a high-yield interactive university exam quiz for:
Subject: {subject}
Topic: {topic}
Number of Questions: {num_questions}

Study Notes Context:
{context_text[:3000] if context_text else "University exam level questions."}

Output strictly in JSON format:
{{
  "title": "Interactive Exam Quiz: {subject} ({topic})",
  "subject": "{subject}",
  "topic": "{topic}",
  "questions": [
    {{
      "id": "q1",
      "type": "MCQ",
      "topic": "{topic}",
      "question": "Clear question text with LaTeX if applicable",
      "options": [
        "Option A text",
        "Option B text",
        "Option C text",
        "Option D text"
      ],
      "correct_index": 0,
      "explanation": "Detailed explanation of why the correct option is right and why the distractors are wrong.",
      "bloom_level": "Understand / Apply / Analyze"
    }}
  ]
}}
"""
            llm_res = AIEngine._call_gemini_llm(prompt)
            if llm_res:
                try:
                    cleaned_json = re.sub(r'```(?:json)?\s*', '', llm_res).replace('```', '').strip()
                    parsed = json.loads(cleaned_json)
                    parsed["notebook_id"] = notebook_id
                    parsed["subject"] = subject
                    parsed["topic"] = topic
                    return DatabaseRepo.create_quiz(parsed)
                except Exception as e:
                    print(f"Error parsing Gemini quiz JSON: {e}")

        curated = QuizEngine._generate_curated_quiz(notebook_id, subject, topic, num_questions)
        return DatabaseRepo.create_quiz(curated)

    @staticmethod
    def _generate_curated_quiz(
        notebook_id: Optional[str],
        subject: str,
        topic: str,
        num_questions: int
    ) -> Dict[str, Any]:
        sub_lower = subject.lower()
        
        all_qs = [
            {"id": "q1", "type": "MCQ", "topic": "Balanced Trees", "question": "In an AVL tree, what is the maximum permissible difference between the heights of the left and right subtrees of any node?", "options": ["0", "1", "2", "log(n)"], "correct_index": 1, "explanation": "By definition, the balance factor BF = height(left) - height(right) in an AVL tree must be within {-1, 0, +1}, meaning a maximum difference of 1.", "bloom_level": "Remember"},
            {"id": "q2", "type": "MCQ", "topic": "Graph Algorithms", "question": "What is the time complexity of Dijkstra's algorithm implemented with a Binary Min-Heap for a graph with V vertices and E edges?", "options": ["O(V^2)", "O((V + E) log V)", "O(V * E)", "O(E log E)"], "correct_index": 1, "explanation": "Each vertex extraction takes O(log V) (total V log V), and each edge relaxation can decrease key in O(log V) (total E log V), yielding O((V+E) log V).", "bloom_level": "Understand"},
            {"id": "q3", "type": "MCQ", "topic": "Operating Systems", "question": "Which of the following conditions is NOT one of Coffman's four necessary conditions for deadlock to occur?", "options": ["Mutual Exclusion", "Hold and Wait", "Preemption Allowed", "Circular Wait"], "correct_index": 2, "explanation": "The condition is 'No Preemption' (resources cannot be forcibly reclaimed). If preemption is allowed, deadlock cannot occur.", "bloom_level": "Understand"},
            {"id": "q4", "type": "MCQ", "topic": "Dynamic Programming", "question": "What is the space complexity of the standard space-optimized 1D array approach for the 0/1 Knapsack problem with capacity W?", "options": ["O(N * W)", "O(W)", "O(N)", "O(log W)"], "correct_index": 1, "explanation": "By iterating the capacity array backwards from W down to item weight w_i, we only require a single 1D array of size W+1, reducing space from O(N * W) to O(W).", "bloom_level": "Apply"},
            {"id": "q5", "type": "MCQ", "topic": "Database Normalization", "question": "A relation R is in Boyce-Codd Normal Form (BCNF) if and only if for every non-trivial functional dependency X -> Y:", "options": ["Y is a prime attribute", "X is a Super Key of R", "X contains at least one prime attribute", "R has no composite primary keys"], "correct_index": 1, "explanation": "BCNF eliminates all redundancy based on functional dependencies by strictly mandating that the determinant X must be a superkey for every non-trivial FD.", "bloom_level": "Analyze"}
        ]

        selected = all_qs[:num_questions]
        return {
            "notebook_id": notebook_id,
            "subject": subject,
            "topic": topic,
            "title": f"Comprehensive Academic Quiz: {subject}",
            "questions": selected,
            "total_questions": len(selected)
        }

    @staticmethod
    def grade_attempt(quiz_id: str, submitted_answers: Any, time_taken: int = 60) -> Dict[str, Any]:
        quiz = DatabaseRepo.get_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")

        if isinstance(submitted_answers, dict):
            if "answers" in submitted_answers and isinstance(submitted_answers["answers"], (list, dict)):
                submitted_answers = submitted_answers["answers"]

        if isinstance(submitted_answers, dict):
            submitted_answers = [{"question_id": k, "selected_index": v} for k, v in submitted_answers.items()]
        elif not isinstance(submitted_answers, list):
            submitted_answers = []

        normalized_answers = []
        for a in submitted_answers:
            if isinstance(a, dict):
                normalized_answers.append(a)
            elif isinstance(a, (list, tuple)) and len(a) >= 2:
                normalized_answers.append({"question_id": a[0], "selected_index": a[1]})
        submitted_answers = normalized_answers

        questions = quiz.get("questions", [])
        total_q = len(questions)
        score = 0.0

        weak_topics = set()
        mastered_topics = set()
        detailed_answers = []

        for q in questions:
            qid = q.get("id")
            correct_idx = q.get("correct_index", 0)
            topic = q.get("topic", "General")
            
            sub = next((a for a in submitted_answers if isinstance(a, dict) and str(a.get("question_id")) == str(qid)), None)
            user_choice = sub.get("selected_index") if (sub and isinstance(sub, dict)) else None
            
            try:
                is_correct = (user_choice is not None) and (int(user_choice) == int(correct_idx))
            except (ValueError, TypeError):
                is_correct = False

            if is_correct:
                score += 1.0
                mastered_topics.add(topic)
            else:
                weak_topics.add(topic)

            detailed_answers.append({
                "question_id": qid,
                "question": q.get("question"),
                "options": q.get("options", []),
                "selected_index": user_choice,
                "correct_index": correct_idx,
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
                "topic": topic
            })

        percentage = round((score / total_q) * 100, 1) if total_q > 0 else 0.0
        
        recommendations = []
        for t in weak_topics:
            recommendations.append(f"Review core definitions and practice 3 derivations on '{t}'. Check corresponding flashcards in Note Maker.")

        attempt_record = DatabaseRepo.record_quiz_attempt({
            "quiz_id": quiz_id,
            "score": score,
            "max_score": float(total_q),
            "percentage": percentage,
            "time_taken_seconds": time_taken,
            "answers": detailed_answers,
            "weak_topics": list(weak_topics),
            "mastered_topics": list(mastered_topics),
            "recommendations": recommendations
        })

        return attempt_record