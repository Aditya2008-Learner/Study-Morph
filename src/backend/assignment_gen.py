import os
import re
import json
import uuid
from typing import List, Dict, Any, Optional

from .ai_engine import AIEngine
from .database import DatabaseRepo

class AssignmentGenerator:
    @staticmethod
    def generate_assignment(
        notebook_id: Optional[str] = None,
        subject: str = "General",
        semester: str = "1",
        difficulty: str = "Intermediate",
        target_exam: str = "University Exam",
        topics: Optional[List[str]] = None,
        num_questions: int = 30
    ) -> Dict[str, Any]:
        context_text = ""
        extracted_topics = topics or []
        
        if notebook_id:
            nb = DatabaseRepo.get_notebook_by_id(notebook_id)
            if nb:
                context_text = nb.get("raw_text", "")
                subject = nb.get("subject") or subject
                semester = nb.get("semester") or semester
                extracted_topics = nb.get("extracted_topics") or extracted_topics

        if AIEngine.is_gemini_available():
            prompt = f"""Generate a comprehensive, university-standard academic assignment for:
Subject: {subject}
Semester: {semester}
Target Exam: {target_exam}
Difficulty: {difficulty}
Topics: {', '.join(extracted_topics) if extracted_topics else 'Core Curriculum'}
Number of Questions: {num_questions}

Study Notes Context:
{context_text[:3000] if context_text else "General university curriculum standards."}

Generate the assignment strictly in the following JSON format:
{{
  "title": "Comprehensive Assignment: {subject}",
  "total_marks": 100,
  "time_limit_mins": 180,
  "questions": [
    {{
      "num": 1,
      "type": "Important / Exam-Style / Viva / Conceptual / Numerical",
      "topic": "Topic Name",
      "bloom_level": "Remember / Understand / Apply / Analyze / Evaluate / Create",
      "marks": 5,
      "text": "Detailed question text with LaTeX if applicable",
      "hints": ["Hint 1", "Hint 2"],
      "model_answer_summary": "Summary of ideal answer and key points"
    }}
  ],
  "rubric": [
    {{"criteria": "Theoretical Accuracy", "weight_pct": 30}},
    {{"criteria": "Problem Solving & Methodology", "weight_pct": 40}},
    {{"criteria": "Mathematical & Asymptotic Rigor", "weight_pct": 20}},
    {{"criteria": "Presentation & Structure", "weight_pct": 10}}
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
                    parsed["semester"] = semester
                    parsed["difficulty"] = difficulty
                    parsed["target_exam"] = target_exam
                    return DatabaseRepo.create_generated_assignment(parsed)
                except Exception as e:
                    print(f"Error parsing Gemini assignment JSON: {e}")

        generated = AssignmentGenerator._generate_curated_assignment(
            notebook_id=notebook_id,
            subject=subject,
            semester=semester,
            difficulty=difficulty,
            target_exam=target_exam,
            topics=extracted_topics,
            num_questions=num_questions
        )
        return DatabaseRepo.create_generated_assignment(generated)

    @staticmethod
    def _generate_curated_assignment(
        notebook_id: Optional[str],
        subject: str,
        semester: str,
        difficulty: str,
        target_exam: str,
        topics: List[str],
        num_questions: int
    ) -> Dict[str, Any]:
        sub_lower = subject.lower()
        
        q_bank = []
        if "data structure" in sub_lower or "algorithm" in sub_lower or "cs" in sub_lower:
            q_bank = [
                {"num": 1, "type": "Important Question", "topic": "Asymptotic Analysis", "bloom_level": "Understand", "marks": 5, "text": "State the Master Theorem for divide-and-conquer recurrences: T(n) = aT(n/b) + f(n). Solve the recurrence T(n) = 4T(n/2) + n^2.", "hints": ["Identify a=4, b=2, f(n)=n^2.", "Compare n^log_b a = n^log_2 4 = n^2 with f(n)."], "model_answer_summary": "Since n^log_b a = n^2 = Theta(f(n)), Case 2 applies: T(n) = Theta(n^2 log n)."},
                {"num": 2, "type": "Exam-Style Question", "topic": "AVL Trees", "bloom_level": "Apply", "marks": 10, "text": "Insert the keys {50, 20, 70, 10, 30, 25} sequentially into an initially empty AVL Tree. Show every tree state and specify each rotation (LL, RR, LR, RL) performed.", "hints": ["Calculate balance factor BF = h_left - h_right after every insertion.", "When inserting 25, node 20 has BF=-1 and node 50 has BF=+2, triggering LR rotation."], "model_answer_summary": "Insertion of 25 causes LR imbalance at node 50. Left rotate child (node 20-30), then Right rotate parent (50)."},
                {"num": 3, "type": "Conceptual Question", "topic": "Sorting Lower Bound", "bloom_level": "Analyze", "marks": 10, "text": "Prove using a Decision Tree model that any comparison-based sorting algorithm requires at least Omega(n log n) comparisons in the worst case.", "hints": ["A decision tree for n elements has n! leaves.", "A binary tree of height h has at most 2^h leaves, so 2^h >= n!."], "model_answer_summary": "h >= log2(n!) = sum_{i=1}^n log2(i) >= (n/2)log2(n/2) = Omega(n log n) by Stirling's approximation."},
                {"num": 4, "type": "Numerical & Coding", "topic": "Dynamic Programming", "bloom_level": "Apply", "marks": 15, "text": "Given item weights W = [2, 3, 4, 5], values V = [3, 4, 5, 6], and knapsack capacity C = 8, construct the 2D dynamic programming table for the 0/1 Knapsack Problem and find the optimal subset of items.", "hints": ["Recurrence: dp[i][w] = max(dp[i-1][w], dp[i-1][w-W[i-1]] + V[i-1]).", "Backtrack from dp[4][8] to retrieve chosen items."], "model_answer_summary": "Maximum achievable value is 10 (taking items 1, 2, and 4 or items 2 and 4 with optimal capacity)."},
                {"num": 5, "type": "Viva Question", "topic": "Graph Algorithms", "bloom_level": "Evaluate", "marks": 10, "text": "Why does Dijkstra's algorithm fail on graphs with negative edge weights? Explain the greedy choice property violation.", "hints": ["Dijkstra marks a vertex finalized once extracted from priority queue.", "A future negative edge can offer a shorter path to an already finalized vertex."], "model_answer_summary": "Dijkstra assumes path distances are monotonically non-decreasing. Negative edges violate this; Bellman-Ford must be used."},
                {"num": 6, "type": "Numerical & Coding", "topic": "Heaps & Priority Queues", "bloom_level": "Create", "marks": 20, "text": "Design a data structure that supports insert(x) in O(log n) and getMedian() in O(1) time over an infinite stream of integers.", "hints": ["Maintain two heaps: Max-Heap for lower half, Min-Heap for upper half.", "Keep heaps balanced in size: difference in count at most 1."], "model_answer_summary": "Pair a Max-Heap (stores smaller half) and Min-Heap (stores larger half). The median is either the top of larger heap or average of both roots."},
                {"num": 7, "type": "Exam-Style Question", "topic": "Graph Traversal", "bloom_level": "Analyze", "marks": 15, "text": "Explain cycle detection in a directed graph using Depth First Search with 3-color vertex marking (White, Gray, Black).", "hints": ["White = unvisited, Gray = visiting (in recursion stack), Black = fully explored.", "A back-edge encountered to a Gray node indicates a directed cycle."], "model_answer_summary": "Cycle exists if and only if a back edge to a Gray vertex is found during DFS traversal. Time complexity O(V + E)."},
                {"num": 8, "type": "Viva Question", "topic": "Hashing", "bloom_level": "Understand", "marks": 15, "text": "Compare Separate Chaining vs Open Addressing (Linear Probing, Quadratic Probing, Double Hashing) for hash collision resolution.", "hints": ["Analyze load factor alpha = n/m.", "Consider cache locality and primary clustering."], "model_answer_summary": "Chaining allows alpha > 1 with linked lists. Open addressing keeps all elements in array, better cache locality, but degrades when alpha > 0.7."}
            ]
        elif "operating" in sub_lower or "os" in sub_lower:
            q_bank = [
                {"num": 1, "type": "Important Question", "topic": "Process Synchronization", "bloom_level": "Understand", "marks": 5, "text": "State the three critical requirements that any valid solution to the Critical Section problem must satisfy.", "hints": ["Mutual Exclusion, Progress, Bounded Waiting."], "model_answer_summary": "1. Mutual Exclusion: only one process in CS. 2. Progress: non-participating processes don't block. 3. Bounded Waiting: limit on entry requests."},
                {"num": 2, "type": "Numerical & Coding", "topic": "CPU Scheduling", "bloom_level": "Apply", "marks": 15, "text": "Given processes P1, P2, P3, P4 with Arrival Times [0, 1, 2, 3] and Burst Times [7, 4, 1, 4], draw Gantt chart and compute Average Turnaround & Waiting Times for Shortest Remaining Time First (SRTF).", "hints": ["Preempt whenever a new process with shorter remaining burst arrives."], "model_answer_summary": "Execution order: P1(0-1), P2(1-2), P3(2-3), P2(3-6), P4(6-10), P1(10-16). Calculate CT, TAT=CT-AT, WT=TAT-BT."},
                {"num": 3, "type": "Conceptual Question", "topic": "Deadlock Avoidance", "bloom_level": "Analyze", "marks": 15, "text": "Explain Banker's Algorithm for deadlock avoidance. How does the safety algorithm guarantee absence of circular wait?", "hints": ["Need matrix = Max - Allocation.", "Find sequence where Need <= Available."], "model_answer_summary": "Checks if there exists at least one safe execution sequence satisfying all pending resource requests."},
                {"num": 4, "type": "Numerical", "topic": "Virtual Memory", "bloom_level": "Apply", "marks": 15, "text": "Calculate the Effective Memory Access Time (EMAT) if TLB access time = 15ns, Main Memory access time = 80ns, and TLB hit ratio = 92%.", "hints": ["EMAT = HitRatio * (TLB + Mem) + (1 - HitRatio) * (TLB + 2 * Mem)."], "model_answer_summary": "EMAT = 0.92 * (15 + 80) + 0.08 * (15 + 160) = 0.92(95) + 0.08(175) = 87.4 + 14 = 101.4ns."},
                {"num": 5, "type": "Viva Question", "topic": "Page Replacement", "bloom_level": "Evaluate", "marks": 10, "text": "What is Belady's Anomaly in page replacement algorithms? Which algorithms are immune to it?", "hints": ["More frames causing more page faults.", "Stack algorithms (LRU, Optimal) never exhibit Belady's Anomaly."], "model_answer_summary": "FIFO can exhibit increased page faults with more frames. Stack-based algorithms (LRU, LFU) are mathematically immune."}
            ]
        else:
            topics_list = topics if topics else [f"{subject} Principles", "Core Formulations", "Analytical Methods", "Case Studies"]
            for idx, t in enumerate(topics_list[:num_questions]):
                q_bank.append({
                    "num": idx + 1,
                    "type": ["Important Question", "Exam-Style Question", "Conceptual Question", "Numerical & Applied", "Viva Question"][idx % 5],
                    "topic": t,
                    "bloom_level": ["Understand", "Apply", "Analyze", "Evaluate", "Create"][idx % 5],
                    "marks": [5, 10, 15, 20][idx % 4],
                    "text": f"Analyze the core principles of {t} in {subject}. Formulate the governing mathematical equations, state boundary assumptions, and demonstrate step-by-step problem resolution.",
                    "hints": [f"Review foundational properties of {t}.", "State governing equations and define all variables."],
                    "model_answer_summary": f"Comprehensive theoretical breakdown of {t} including formulas, architectural diagrams, and error margin analysis."
                })

        selected_qs = q_bank[:num_questions]
        while len(selected_qs) < num_questions:
            idx = len(selected_qs)
            q = dict(q_bank[idx % len(q_bank)])
            q["num"] = idx + 1
            selected_qs.append(q)
        
        selected_qs = selected_qs[:num_questions]
        total_marks = sum(q["marks"] for q in selected_qs)
        
        return {
            "notebook_id": notebook_id,
            "title": f"University Standard Assignment: {subject} (Sem {semester})",
            "subject": subject,
            "semester": str(semester),
            "difficulty": difficulty,
            "target_exam": target_exam,
            "questions": selected_qs,
            "rubric": [
                {"criteria": "Theoretical Correctness & Definitions", "weight_pct": 30},
                {"criteria": "Step-by-Step Problem Solving & Calculations", "weight_pct": 35},
                {"criteria": "Diagrams, LaTeX Formulations & Syntax", "weight_pct": 20},
                {"criteria": "Clarity & Academic Rigor", "weight_pct": 15}
            ],
            "total_marks": total_marks,
            "time_limit_mins": 180
        }