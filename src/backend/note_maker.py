import os
import re
import json
import uuid
from typing import List, Dict, Any, Optional

from .ai_engine import AIEngine
from .database import DatabaseRepo

class NoteMaker:
    @staticmethod
    def generate_study_notes(
        notebook_id: Optional[str] = None,
        subject: str = "Computer Science",
        topic: str = "Core Concepts"
    ) -> Dict[str, Any]:
        context_text = ""
        if notebook_id:
            nb = DatabaseRepo.get_notebook_by_id(notebook_id)
            if nb:
                context_text = nb.get("raw_text", "")
                subject = nb.get("subject") or subject
                topic = (nb.get("extracted_topics") or [topic])[0]

        if AIEngine.is_gemini_available():
            prompt = f"""Generate comprehensive, high-yield study revision materials for:
Subject: {subject}
Topic: {topic}

Notes Context:
{context_text[:3000] if context_text else "University curriculum revision guide."}

Output strictly in JSON:
{{
  "summary": "Detailed executive academic summary with headings and Markdown formatting",
  "flashcards": [
    {{
      "id": "1",
      "front": "Question or Concept Prompt",
      "back": "Clear, concise answer with key terms",
      "hint": "Helpful mnemonic or memory trigger",
      "difficulty": "Easy / Medium / Hard",
      "leitner_box": 1
    }}
  ],
  "formulas": [
    {{
      "name": "Formula or Law Name",
      "latex": "$$\\text{Equation}$$",
      "explanation": "What each variable means and when to apply it"
    }}
  ],
  "mnemonics": [
    {{
      "topic": "Specific sub-concept",
      "mnemonic": "ACRONYM / Memory Trick",
      "meaning": "Explanation of the memory aid"
    }}
  ],
  "key_takeaways": [
    "High yield point 1",
    "High yield point 2"
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
                    return DatabaseRepo.create_study_note(parsed)
                except Exception as e:
                    print(f"Error parsing Gemini study note JSON: {e}")

        curated = NoteMaker._generate_curated_notes(notebook_id, subject, topic, context_text)
        return DatabaseRepo.create_study_note(curated)

    @staticmethod
    def _generate_curated_notes(
        notebook_id: Optional[str],
        subject: str,
        topic: str,
        context: str
    ) -> Dict[str, Any]:
        sub_lower = subject.lower()
        
        if "data structure" in sub_lower or "algorithm" in sub_lower:
            return {
                "notebook_id": notebook_id,
                "subject": subject,
                "topic": topic if topic != "Core Concepts" else "Data Structures and Asymptotic Complexity",
                "summary": f"""### Executive Study Summary: {subject}

**Overview and Purpose:**
Data structures and algorithms form the computational backbone for modern software architecture. Key priorities in academic examinations include time/space complexity derivations, balanced search tree invariants, dynamic programming state transitions, and graph traversals.

#### Key Architectural Highlights:
1. **Tree Balancing Invariants:**
   - AVL Trees: Strictly balanced where height h <= 1.44 log2 n. Balance factor in [-1, 0, +1].
   - Red-Black Trees: Relaxed balance where longest path is at most twice shortest path. Root and leaves are black; no two consecutive red nodes.
2. **Dynamic Programming Strategy:**
   - Characterize optimal substructure and overlapping subproblems.
   - Formulate state transition equation DP[i][j] and fill base cases explicitly.
3. **Graph Algorithms:**
   - BFS: Level-order shortest paths in unweighted graphs (O(V + E)).
   - Dijkstra: Single-source shortest path for non-negative edge weights using Min-Heap (O((V+E) log V)).
   - Bellman-Ford: Detects negative cycles (O(V * E)).
""",
                "flashcards": [
                    {"id": "1", "front": "What is the balance factor condition for an AVL Tree?", "back": "BF(node) = Height(LeftSubtree) - Height(RightSubtree), and BF must be in {-1, 0, +1}.", "hint": "Left minus Right height", "difficulty": "Easy", "leitner_box": 1},
                    {"id": "2", "front": "When does Dijkstra's Algorithm fail?", "back": "When the graph contains negative edge weights, because Dijkstra makes a greedy choice that cannot be revised.", "hint": "Negative edges violate greedy monotonicity", "difficulty": "Medium", "leitner_box": 1},
                    {"id": "3", "front": "State the worst-case time complexity of QuickSort and how to avoid it.", "back": "Worst case is O(n^2) when pivot is always extreme. Avoided by Randomized Pivot or Median-of-Three pivot selection.", "hint": "Partition imbalance", "difficulty": "Medium", "leitner_box": 1},
                    {"id": "4", "front": "What are the two key properties required to apply Dynamic Programming?", "back": "1. Optimal Substructure (optimal solution contains optimal sub-solutions). 2. Overlapping Subproblems.", "hint": "Substructure + Overlapping", "difficulty": "Hard", "leitner_box": 1},
                    {"id": "5", "front": "What is the lower bound for comparison-based sorting in the worst case?", "back": "Omega(n log n), proven via binary decision tree height with n! leaves.", "hint": "Decision tree leaves log(n!)", "difficulty": "Hard", "leitner_box": 1}
                ],
                "formulas": [
                    {"name": "Master Theorem Recurrence", "latex": "$$T(n) = a T\\left(\\frac{n}{b}\\right) + \\Theta(n^k \\log^p n)$$", "explanation": "Determines asymptotic time complexity for divide-and-conquer recurrences with branching factor a and subproblem division b."},
                    {"name": "AVL Tree Height Bound", "latex": "$$h < 1.4404 \\log_2(n + 2) - 0.328$$", "explanation": "Guarantees that search, insertion, and deletion in AVL trees remain strictly logarithmic in the worst case."},
                    {"name": "0/1 Knapsack DP State Transition", "latex": "$$dp[i][w] = \\max(dp[i-1][w], \\, dp[i-1][w - w_i] + v_i)$$", "explanation": "Chooses maximum value between excluding item i or including item i with weight deduction."}
                ],
                "mnemonics": [
                    {"topic": "Sorting Algorithm Complexities", "mnemonic": "Q-M-H (Quick, Merge, Heap)", "meaning": "Remember that Merge and Heap are ALWAYS O(N log N) in all cases; Quick is O(N log N) average but O(N^2) worst."},
                    {"topic": "Graph Algorithms", "mnemonic": "D-B-F (Dijkstra, Bellman-Ford, Floyd-Warshall)", "meaning": "D = Non-negative edges (Greedy), B = Negative edges allowed (DP/Relaxation), F = All-pairs shortest paths."}
                ],
                "key_takeaways": [
                    "Always write recurrence relations explicitly before deriving asymptotic complexity.",
                    "In AVL rotations: LL -> Right Rotate, RR -> Left Rotate, LR -> Left-Right double rotate, RL -> Right-Left double rotate.",
                    "Use Hash Tables for O(1) expected lookup, but balanced BSTs (AVL / Red-Black) when in-order traversal and guaranteed O(log n) worst case are needed.",
                    "Priority Queues implemented via Binary Heaps take O(N) to build (heapify) and O(log N) to push/pop."
                ]
            }
        else:
            return {
                "notebook_id": notebook_id,
                "subject": subject,
                "topic": topic,
                "summary": f"""### High-Yield Study Summary: {subject} - {topic}

**Core Academic Overview:**
This revision sheet synthesizes foundational definitions, mathematical formulations, key derivations, and high-frequency examination questions for **{topic}**.

#### Essential Pillars:
1. **Fundamental Laws and Principles:** Invariants that govern problem spaces and boundary constraints.
2. **Mathematical Formulations:** Explicit relationships between dependent and independent variables.
3. **Examination Strategy:** Step-by-step methodology for tackling numerical problems and conceptual proofs.
""",
                "flashcards": [
                    {"id": "1", "front": f"What is the fundamental definition of {topic} in {subject}?", "back": f"The core theoretical framework establishing governing relationships and operational invariants in {subject}.", "hint": "Foundational principle", "difficulty": "Easy", "leitner_box": 1},
                    {"id": "2", "front": f"State the primary boundary conditions when analyzing {topic}.", "back": "Initial states, conservation laws, domain limits, and convergence constraints.", "hint": "Limits and edge conditions", "difficulty": "Medium", "leitner_box": 1},
                    {"id": "3", "front": f"How do you evaluate efficiency or performance in {topic}?", "back": "By measuring resource utilization, asymptotic bounds, signal-to-noise ratio, or throughput metrics.", "hint": "Quantitative performance metric", "difficulty": "Hard", "leitner_box": 1}
                ],
                "formulas": [
                    {"name": f"Governing Relationship for {topic}", "latex": "$$\\mathcal{F}(x, t) = \\sum_{i=1}^n \\alpha_i \\phi_i(x) e^{-\\lambda_i t}$$", "explanation": "Generalized linear superposition of basis states and temporal decay parameters."}
                ],
                "mnemonics": [
                    {"topic": topic, "mnemonic": "I-D-E-A (Identify, Define, Execute, Analyze)", "meaning": "Standard 4-step framework for solving any university exam problem."}
                ],
                "key_takeaways": [
                    f"Always state standard assumptions clearly at the beginning of {topic} proofs.",
                    "Verify unit consistency and check edge cases (zero/infinity).",
                    "Draw labeled architectural or circuit diagrams for full visual marks."
                ]
            }