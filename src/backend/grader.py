import os
import re
import json
from typing import List, Dict, Any, Optional

from .ai_engine import AIEngine
from .database import DatabaseRepo
from ..c_core.c_bridge import fast_fuzzy_similarity

class AssignmentGrader:
    @staticmethod
    def get_progressive_hint(question_text: str, current_level: int = 1, context: str = "") -> Dict[str, Any]:
        if AIEngine.is_gemini_available():
            prompt = f"""You are a Socratic Academic Tutor. The student is working on this assignment question:
"{question_text}"

The student requested Hint Level {current_level} (Level 1 = conceptual starting nudge, Level 2 = key formula/strategy, Level 3 = full step-by-step walkthrough).
Provide an encouraging, academically precise hint without giving away the raw final answer if level < 3.
Use LaTeX for math.
"""
            llm_res = AIEngine._call_gemini_llm(prompt)
            if llm_res:
                return {"level": current_level, "hint_text": llm_res, "model": "Gemini Socratic Tutor"}

        q_lower = question_text.lower()
        if current_level == 1:
            hint = f"**Level 1 (Starting Direction):** Identify the primary variables, boundary conditions, and what theorem or standard method applies. Think about what invariant or fundamental property stays constant."
            if "master theorem" in q_lower:
                hint = "**Level 1 (Starting Direction):** Put the recurrence into standard form T(n) = aT(n/b) + f(n). Calculate the watershed exponent log_b a and compare n^log_b a with f(n)."
            elif "avl" in q_lower:
                hint = "**Level 1 (Starting Direction):** Remember balance factor BF = height(left) - height(right). Check if any node has |BF| > 1 after each insertion."
            elif "knapsack" in q_lower:
                hint = "**Level 1 (Starting Direction):** For each item i and capacity w, decide whether including item i yields higher value than excluding it: dp[i][w] = max(dp[i-1][w], dp[i-1][w-W[i]] + V[i])."
            elif "dijkstra" in q_lower:
                hint = "**Level 1 (Starting Direction):** Consider how Dijkstra makes greedy local choices by popping the minimum distance unvisited vertex. What happens if a subsequent edge has negative weight?"
        elif current_level == 2:
            hint = f"**Level 2 (Methodology and Formula):** Set up the formal governing equations. Substitute the given values into the formula and verify dimensional consistency."
            if "master theorem" in q_lower:
                hint = "**Level 2 (Methodology and Formula):** If f(n) = Theta(n^log_b a), then T(n) = Theta(n^log_b a log n) (Case 2). If f(n) grows polynomially faster or slower, use Case 3 or Case 1 respectively."
            elif "avl" in q_lower:
                hint = "**Level 2 (Methodology and Formula):** Identify the rotation type: Left-Left requires Right rotation; Right-Right requires Left rotation; Left-Right requires Left child rotate then Right parent rotate."
            elif "knapsack" in q_lower:
                hint = "**Level 2 (Methodology and Formula):** Initialize a table of size (N+1) x (C+1) with zeros. Fill row by row from i=1..N and w=0..C."
        else:
            hint = f"""**Level 3 (Step-by-Step Solution Outline):**
1. State given parameters and definitions.
2. Execute each computational step sequentially.
3. Verify against edge conditions and state the final result with formal academic justification."""
            if "master theorem" in q_lower:
                hint = """**Level 3 (Complete Walkthrough):**
For T(n) = 4T(n/2) + n^2:
1. a = 4, b = 2, f(n) = n^2.
2. Compute n^log_b a = n^log_2 4 = n^2.
3. Since f(n) = n^2 = Theta(n^log_b a), we apply Case 2 of the Master Theorem.
4. Final Complexity: T(n) = Theta(n^2 log n)."""

        return {"level": current_level, "hint_text": hint, "model": "Academic Socratic Engine"}

    @staticmethod
    def evaluate_answer(
        question_text: str,
        student_answer: str,
        total_marks: float = 10.0,
        model_answer_summary: str = ""
    ) -> Dict[str, Any]:
        if not student_answer or len(student_answer.strip()) < 5:
            return {
                "marks_awarded": 0.0,
                "total_marks": total_marks,
                "accuracy_score": 0.0,
                "completeness_score": 0.0,
                "feedback_text": "Answer is too brief or blank. Please provide your complete reasoning, formulas, and steps.",
                "rubric_breakdown": {
                    "Theory & Definitions (30%)": "0 / 3.0",
                    "Methodology & Steps (35%)": "0 / 3.5",
                    "Accuracy & Rigor (20%)": "0 / 2.0",
                    "Clarity & Presentation (15%)": "0 / 1.5"
                },
                "missing_points": ["Initial definitions", "Step-by-step calculation", "Final concluded result"],
                "model_answer": model_answer_summary or "Please refer to the course textbook or lecture notes for the complete derivation."
            }

        if AIEngine.is_gemini_available():
            prompt = f"""You are a rigorous university professor grading a student's answer.
QUESTION ({total_marks} Marks):
{question_text}

STUDENT ANSWER:
{student_answer}

MODEL ANSWER REFERENCE:
{model_answer_summary if model_answer_summary else "Standard university curriculum solution."}

Evaluate the student answer and output strictly in JSON format:
{{
  "marks_awarded": float (between 0 and {total_marks}),
  "accuracy_score": float (0 to 100),
  "completeness_score": float (0 to 100),
  "feedback_text": "Constructive academic feedback highlighting what was done well and specific errors",
  "missing_points": ["List of missing steps or concepts"],
  "rubric_breakdown": {{
    "Theory & Definitions (30%)": "score / max",
    "Methodology & Steps (35%)": "score / max",
    "Accuracy & Rigor (20%)": "score / max",
    "Clarity & Presentation (15%)": "score / max"
  }},
  "model_answer": "Comprehensive ideal model solution with LaTeX"
}}
"""
            llm_res = AIEngine._call_gemini_llm(prompt)
            if llm_res:
                try:
                    cleaned_json = re.sub(r'```(?:json)?\s*', '', llm_res).replace('```', '').strip()
                    return json.loads(cleaned_json)
                except Exception as e:
                    print(f"Error parsing Gemini evaluation: {e}")

        answer_len = len(student_answer.split())
        has_formulas = bool(re.search(r'[\$\\=+\-*/^O\(\)]', student_answer))
        has_keywords = any(w in student_answer.lower() for w in ["because", "therefore", "since", "step", "formula", "algorithm", "case", "table", "complexity", "theorem"])
        
        sim = fast_fuzzy_similarity(student_answer, model_answer_summary) if model_answer_summary else 0.5
        
        base_pct = min(1.0, (answer_len / 40.0) * 0.4 + (0.3 if has_formulas else 0.1) + (0.3 if has_keywords else 0.1) + (sim * 0.2))
        accuracy = round(min(98.0, base_pct * 95.0), 1)
        completeness = round(min(95.0, (answer_len / 50.0) * 100.0), 1)
        marks_awarded = round((accuracy / 100.0) * total_marks, 1)

        t_score = round(0.30 * marks_awarded, 1)
        m_score = round(0.35 * marks_awarded, 1)
        a_score = round(0.20 * marks_awarded, 1)
        c_score = round(0.15 * marks_awarded, 1)

        missing = []
        if not has_formulas:
            missing.append("Formal mathematical formulation / LaTeX equation")
        if answer_len < 30:
            missing.append("Detailed intermediate steps and reasoning")
        if not has_keywords:
            missing.append("Explicit justification of boundary conditions or complexity analysis")

        feedback = f"Good attempt! Your response demonstrates understanding of the main concepts. "
        if missing:
            feedback += f"To achieve full marks in an exam, ensure you include: {', '.join(missing)}."
        else:
            feedback += "Excellent structured derivation with clear logic and accurate execution."

        return {
            "marks_awarded": marks_awarded,
            "total_marks": total_marks,
            "accuracy_score": accuracy,
            "completeness_score": completeness,
            "feedback_text": feedback,
            "missing_points": missing if missing else ["None - well rounded answer!"],
            "rubric_breakdown": {
                "Theory & Definitions (30%)": f"{t_score} / {round(0.30 * total_marks, 1)}",
                "Methodology & Steps (35%)": f"{m_score} / {round(0.35 * total_marks, 1)}",
                "Accuracy & Rigor (20%)": f"{a_score} / {round(0.20 * total_marks, 1)}",
                "Clarity & Presentation (15%)": f"{c_score} / {round(0.15 * total_marks, 1)}"
            },
            "model_answer": model_answer_summary or "State the foundational theorem, substitute initial conditions into the recurrence or matrix, compute step-by-step transitions, and state asymptotic bound."
        }