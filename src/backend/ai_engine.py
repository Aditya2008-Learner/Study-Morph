import os
import re
from typing import List, Dict, Any, Optional

from .rag_engine import RAGIndex

class AIEngine:
    @staticmethod
    def is_gemini_available():
        return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

    @staticmethod
    def _call_gemini_llm(prompt, system_instruction=""):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = model.generate_content(full_prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini API fallback: {e}")
        return None

    @staticmethod
    def chat_rag_response(query, session_id="default"):
        rag = RAGIndex.get_instance()
        relevant_chunks = rag.search(query, top_k=4)
        context_str = "\n\n".join([
            f"Source [{c['doc_type']}: {c['doc_name']} ({c['page_or_sec']})]:\n{c['text']}"
            for c in relevant_chunks
        ])
        citations = [{
            "doc_name": c["doc_name"],
            "doc_type": c["doc_type"],
            "location": c["page_or_sec"],
            "text_snippet": c["text"][:160] + "..." if len(c["text"]) > 160 else c["text"],
            "relevance_score": c["score"]
        } for c in relevant_chunks]

        llm_prompt = f"""You are an expert University Professor and Academic AI Tutor. Answer the student's question clearly, precisely, with mathematical rigor and step-by-step logic.
Use the provided study context if relevant, and cite sources in your answer using [Source: Name, Location].

STUDY CONTEXT:
{context_str if context_str else "No direct document match found in notebook database."}

STUDENT QUESTION:
{query}

Provide a structured, pedagogically clear answer with LaTeX formulas and code blocks where appropriate.
"""
        llm_reply = AIEngine._call_gemini_llm(llm_prompt)
        if llm_reply:
            return {"response": llm_reply, "citations": citations, "model": "Gemini 1.5 Flash (RAG Augmented)"}

        reply = AIEngine._generate_heuristic_academic_answer(query, relevant_chunks)
        return {"response": reply, "citations": citations, "model": "Academic Cognitive Engine (Offline / Local RAG)"}

    @staticmethod
    def _generate_heuristic_academic_answer(query, relevant_chunks):
        q_lower = query.lower()
        
        if relevant_chunks:
            primary = relevant_chunks[0]
            sec_text = primary["text"]
            citation_tag = primary["citation"]
            response = f"""### Academic Explanation and Analysis

Based on your uploaded course materials {citation_tag}:

{sec_text}

---

#### Key Insights and Core Principles:
1. **Theoretical Foundation**: The underlying concept governs how system states and data invariants are maintained.
2. **Algorithmic Complexity and Mechanics**: Operations adhere to standard asymptotic limits, prioritizing optimal space and time tradeoffs.
3. **Exam Application**: In university examinations, always state the standard assumptions, write mathematical formulations using formal notation, and draw block or state transition diagrams.

*Referenced from {primary['doc_name']} ({primary['page_or_sec']}).*
"""
            return response

        if "dijkstra" in q_lower or "shortest path" in q_lower:
            return """### Dijkstra's Single-Source Shortest Path Algorithm

**Core Principle:**
Dijkstra's algorithm finds the shortest path from a starting source node s to all other vertices in a weighted directed or undirected graph with non-negative edge weights.

#### 1. Mathematical Formulation
- Let d[v] be the current shortest distance estimate to vertex v.
- Initialize d[s] = 0 and d[v] = infinity for all v != s.
- Relaxation Step: d[v] = min(d[v], d[u] + w(u, v))

#### 2. Complexity Analysis
- Using Min-Heap or Priority Queue: O((V + E) log V)
- Using Fibonacci Heap: O(E + V log V)
- Space Complexity: O(V) for distance array and priority queue.

#### 3. Why Negative Weights Fail
Dijkstra operates greedily assuming that once a vertex is extracted from the Priority Queue, its shortest distance is finalized. A negative edge later can invalidate this greedy choice. For negative edge weights, use the Bellman-Ford Algorithm with O(V * E) complexity.
"""
        elif "avl" in q_lower or "tree" in q_lower or "red-black" in q_lower:
            return """### AVL Trees vs Red-Black Trees

**Balance Factor in AVL Tree:**
BF(node) = Height(LeftSubtree) - Height(RightSubtree), in {-1, 0, +1}

#### 1. Comparison Matrix:
- AVL Tree: Strictly balanced (height less than 1.44 * log2(n)). Faster lookups. More rotations needed on insert/delete.
- Red-Black Tree: Relaxed balance (height less than 2 * log2(n+1)). Max 2 rotations on insert, 3 on delete. Used in Linux CFS, C++ std::map.

#### 2. Standard Rotations:
1. LL Rotation: Single Right Rotation on unbalanced node.
2. RR Rotation: Single Left Rotation on unbalanced node.
3. LR Rotation: Left rotation on left child followed by Right rotation on parent.
4. RL Rotation: Right rotation on right child followed by Left rotation on parent.
"""
        elif "deadlock" in q_lower or "banker" in q_lower or "semaphore" in q_lower:
            return """### Operating Systems: Deadlock and Synchronization

#### 1. Coffman's 4 Necessary Conditions for Deadlock:
1. Mutual Exclusion: Resources cannot be shared simultaneously.
2. Hold and Wait: A process holds at least one resource and requests additional resources held by others.
3. No Preemption: Resources cannot be forcibly taken from a process.
4. Circular Wait: A closed chain of processes exists where each holds a resource needed by the next.

#### 2. Banker's Algorithm Safety Invariant:
Let Allocation, Max, and Available vectors be defined.
Need[i][j] = Max[i][j] - Allocation[i][j]
A process Pi can execute if Need_i <= Work
Upon completion: Work = Work + Allocation_i
If all processes complete, the system is in a Safe State.
"""
        elif "sql" in q_lower or "normal form" in q_lower or "bcnf" in q_lower or "acid" in q_lower:
            return """### Database Management: ACID and Normalization

#### 1. ACID Properties:
- Atomicity: All operations in a transaction execute or none do.
- Consistency: Transactions preserve database integrity constraints.
- Isolation: Concurrent transactions execute without cross-interference.
- Durability: Committed updates persist across system crashes.

#### 2. Normal Forms Hierarchy:
1. 1NF: Atomic attribute values, no repeating groups.
2. 2NF: 1NF + No partial dependency on candidate key.
3. 3NF: 2NF + No transitive dependency.
4. BCNF: For every functional dependency X -> Y, X must be a Super Key.
"""
        else:
            return f"""### Comprehensive Academic Response

**Question Analyzed:** {query}

#### 1. Key Concept Breakdown
- Definition and Context: In higher academic coursework, understanding foundational definitions is critical for solving multi-part examination questions.
- Underlying Mechanism: Systems and mathematical proofs rely on invariant properties that hold true across all edge cases.

#### 2. Step-by-Step Derivation and Methodology
1. Identify given parameters, initial conditions, and constraints.
2. Apply appropriate standard theorems, formulas, or algorithmic workflows.
3. Validate time and space complexity or boundary stability conditions.

#### 3. Best Practices for Examinations
- Formulate all final answers with units and state assumptions explicitly.
- Include labeled schematics, state diagrams, or asymptotic proofs.
- Verify dimensional consistency and test trivial edge cases.
"""