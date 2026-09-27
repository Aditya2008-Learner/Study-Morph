"""
Intelligent Question Generation Pipeline
Uses existing AI engine to generate diverse, non-duplicate questions from existing knowledge base
"""

import os
import json
import re
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .database import DatabaseRepo, get_connection
from .ai_engine import AIEngine
from ..c_core.c_bridge import fast_fuzzy_similarity
from .question_bank_db import init_question_bank


@dataclass
class QuestionMetadata:
    question_text: str
    subject: str
    topic: str
    subtopic: str
    source_type: str
    source_id: str
    source_question_id: Optional[str]
    difficulty: str
    question_type: str
    marks: int
    year: Optional[int]
    college: str
    related_concepts: List[str]
    similarity_score: float
    generation_params: Dict[str, Any]


class QuestionGenerator:
    """Intelligent question generation with strict non-repetition"""
    
    SIMILARITY_THRESHOLD = 0.75  # reject if > 75% similar
    EXACT_MATCH_THRESHOLD = 0.95
    
    def __init__(self):
        # Initialize question bank tables
        try:
            init_question_bank()
        except Exception:
            pass
    
    def _get_existing_questions(self, subject: str, topic: str = None, subtopic: str = None) -> List[Dict]:
        """Get all existing questions for a topic"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM question_bank WHERE subject = ? AND status = 'Approved'"
        params = [subject]
        
        if topic:
            query += " AND topic = ?"
            params.append(topic)
        if subtopic:
            query += " AND subtopic = ?"
            params.append(subtopic)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            d = dict(r)
            d["related_concepts"] = json.loads(d["related_concepts"]) if d["related_concepts"] else []
            d["generation_params"] = json.loads(d["generation_params"]) if d["generation_params"] else {}
            result.append(d)
        return result
    
    def _extract_concepts(self, question_text: str, subject: str, topic: str) -> List[str]:
        """Extract key concepts from a question using AI"""
        if not AIEngine.is_gemini_available():
            return self._extract_concepts_heuristic(question_text, topic)
        
        prompt = f"""Extract the key mathematical/computational concepts from this {subject} question about {topic}:

Question: {question_text}

Return ONLY a JSON array of concept strings. Each concept should be specific and technical.
Example: ["Binary Search Algorithm", "Logarithmic Time Complexity", "Array Indexing", "Divide and Conquer"]

Concepts:"""
        
        try:
            result = AIEngine._call_gemini_llm(prompt)
            if result:
                cleaned = re.sub(r'```(?:json)?\s*', '', result).replace('```', '').strip()
                return json.loads(cleaned)
        except Exception:
            pass
        
        return self._extract_concepts_heuristic(question_text, topic)
    
    def _extract_concepts_heuristic(self, question_text: str, topic: str) -> List[str]:
        """Fallback concept extraction using keywords"""
        concepts = [topic]
        q_lower = question_text.lower()
        
        # Add domain-specific concepts based on keywords
        concept_map = {
            "binary search": ["Binary Search Algorithm", "Logarithmic Time Complexity", "Divide and Conquer", "Array Indexing"],
            "dynamic programming": ["Dynamic Programming", "Memoization", "Optimal Substructure", "State Transition"],
            "avl tree": ["AVL Tree", "Balance Factor", "Tree Rotation", "Self-Balancing BST"],
            "dijkstra": ["Dijkstra Algorithm", "Shortest Path", "Priority Queue", "Graph Traversal"],
            "knapsack": ["0/1 Knapsack", "Dynamic Programming", "Optimization", "Memoization"],
            "deadlock": ["Deadlock", "Coffman Conditions", "Resource Allocation", "Banker's Algorithm"],
            "normalization": ["Database Normalization", "Functional Dependencies", "BCNF", "Lossless Decomposition"],
            "complexity": ["Time Complexity", "Space Complexity", "Big-O Notation", "Asymptotic Analysis"],
        }
        
        for key, vals in concept_map.items():
            if key in q_lower:
                concepts.extend(vals)
        
        return list(set(concepts))  # deduplicate
    
    def _analyze_question_pattern(self, questions: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in existing questions to guide generation"""
        if not questions:
            return {}
        
        patterns = {
            "avg_marks": sum(q.get("marks", 5) for q in questions) / len(questions),
            "difficulty_dist": {},
            "type_dist": {},
            "concept_freq": {},
            "numerical_ratio": 0,
            "conceptual_ratio": 0,
        }
        
        for q in questions:
            diff = q.get("difficulty", "Medium")
            qtype = q.get("question_type", "Exam")
            patterns["difficulty_dist"][diff] = patterns["difficulty_dist"].get(diff, 0) + 1
            patterns["type_dist"][qtype] = patterns["type_dist"].get(qtype, 0) + 1
            
            # Count numerical vs conceptual
            text = q.get("question_text", "").lower()
            if any(kw in text for kw in ["calculate", "compute", "determine", "find", "solve", "number", "value", "percentage", "probability"]):
                patterns["numerical_ratio"] += 1
            else:
                patterns["conceptual_ratio"] += 1
            
            for concept in q.get("related_concepts", []):
                patterns["concept_freq"][concept] = patterns["concept_freq"].get(concept, 0) + 1
        
        patterns["numerical_ratio"] /= len(questions)
        patterns["conceptual_ratio"] /= len(questions)
        
        return patterns
    
    def _build_generation_prompt(self, 
                                 source_question: Dict,
                                 target_difficulty: str,
                                 target_type: str,
                                 target_marks: int,
                                 variation_level: float,
                                 existing_questions: List[Dict],
                                 concepts: List[str]) -> str:
        """Build the AI prompt for generating a new question variation"""
        
        # Summarize existing questions to avoid duplicates
        existing_summary = ""
        if existing_questions:
            existing_texts = [q["question_text"][:200] for q in existing_questions[:10]]
            existing_summary = "EXISTING QUESTIONS (DO NOT DUPLICATE):\n" + "\n".join(f"- {t}" for t in existing_texts) + "\n\n"
        
        # Difficulty guidance
        diff_guidance = {
            "Easy": "Test basic understanding and recall. Use simple numbers and straightforward application.",
            "Medium": "Require multi-step reasoning. Combine concepts. Use realistic problem sizes.",
            "Hard": "Require deep synthesis. Combine multiple concepts. Edge cases. Optimization.",
            "Advanced": "Research-level or novel synthesis. Proofs. Complex system design. Novel constraints."
        }
        
        type_guidance = {
            "Conceptual": "Focus on understanding and explanation. No calculations.",
            "Short": "Brief answer. One or two sentences. Definition or key property.",
            "Long": "Detailed explanation with derivation. Multiple paragraphs.",
            "Numerical": "Must be mathematically solvable. Provide all needed values. Include units.",
            "Application": "Real-world scenario. Map concept to practical problem.",
            "Scenario": "Hypothetical situation. What-if analysis. Trade-offs.",
            "Comparison": "Compare two approaches/concepts. Highlight trade-offs.",
            "Analytical": "Deep analysis. Why does this work? Mathematical proof or reasoning.",
            "Viva": "Oral exam style. Follow-up questions likely. Concise answer.",
            "Exam": "Standard university exam format. Clear marks allocation."
        }
        
        variation_desc = {
            0.2: "Minor variation - change numbers/names only",
            0.4: "Moderate variation - change scenario and some constraints",
            0.6: "Significant variation - different context, same core concept",
            0.8: "Major variation - novel application of same concept",
            1.0: "Complete reimagining - same learning objective, entirely new scenario"
        }
        
        prompt = f"""You are an expert university professor creating NEW exam questions.

SOURCE QUESTION:
{source_question.get('question_text', '')}

SOURCE METADATA:
- Subject: {source_question.get('subject', '')}
- Topic: {source_question.get('topic', '')}
- Difficulty: {source_question.get('difficulty', 'Medium')}
- Type: {source_question.get('question_type', 'Exam')}
- Marks: {source_question.get('marks', 5)}
- Concepts: {', '.join(concepts)}

TARGET SPECIFICATION:
- Difficulty: {target_difficulty} - {diff_guidance.get(target_difficulty, '')}
- Type: {target_type} - {type_guidance.get(target_type, '')}
- Marks: {target_marks}
- Variation Level: {variation_level} - {variation_desc.get(variation_level, '')}

{existing_summary}

CONSTRAINTS:
1. Preserve the SAME learning objective and core concept
2. Create a GENUINELY DIFFERENT question - not a word rewrite
3. For numerical: ensure solvable, provide all needed values
3. For theory: stay within {source_question.get('topic', '')} scope
4. Vary: numbers, context, scenario, constraints, wording, data, examples
5. Do NOT just change a few words - change the framing entirely
5. Output must be a valid, academically sound question

OUTPUT FORMAT (JSON only):
{{
  "question_text": "Full question text with LaTeX if needed",
  "concepts_used": ["concept1", "concept2"],
  "solvable": true,
  "expected_approach": "Brief description of solution approach"
}}
"""
        return prompt
    
    def _generate_single_question(self, 
                                   source_question: Dict,
                                   target_difficulty: str,
                                   target_type: str,
                                   target_marks: int,
                                   variation_level: float,
                                   existing_questions: List[Dict]) -> Optional[Dict]:
        """Generate a single question variation"""
        
        concepts = self._extract_concepts(
            source_question.get("question_text", ""),
            source_question.get("subject", ""),
            source_question.get("topic", "")
        )
        
        if AIEngine.is_gemini_available():
            prompt = self._build_generation_prompt(
                source_question, target_difficulty, target_type, target_marks,
                variation_level, existing_questions, concepts
            )
            
            result = AIEngine._call_gemini_llm(prompt)
            if result:
                try:
                    cleaned = re.sub(r'```(?:json)?\s*', '', result).replace('```', '').strip()
                    parsed = json.loads(cleaned)
                    
                    if parsed.get("solvable", True) and parsed.get("question_text"):
                        return {
                            "question_text": parsed["question_text"],
                            "related_concepts": parsed.get("concepts_used", concepts),
                            "similarity_score": 0.0,  # will be computed
                            "generation_params": {
                                "difficulty": target_difficulty,
                                "type": target_type,
                                "marks": target_marks,
                                "variation_level": variation_level,
                                "source_question_id": source_question["id"]
                            }
                        }
                except Exception as e:
                    print(f"AI generation parse error: {e}")
        
        # Fallback: template-based generation
        return self._generate_template_question(source_question, target_difficulty, target_type, target_marks, concepts)
    
    def _generate_template_question(self, 
                                     source_question: Dict,
                                     target_difficulty: str,
                                     target_type: str,
                                     target_marks: int,
                                     concepts: List[str]) -> Dict:
        """Template-based fallback generation"""
        
        topic = source_question.get("topic", "")
        base_text = source_question.get("question_text", "")
        
        # Simple template variations
        templates = {
            ("Numerical", "Easy"): f"Calculate the time complexity of {topic} for an input size of n=1000.",
            ("Numerical", "Medium"): f"Given a {topic} scenario with constraints X, Y, Z, determine the optimal solution and its complexity.",
            ("Conceptual", "Easy"): f"Explain the key invariant maintained by {topic} during its operation.",
            ("Conceptual", "Medium"): f"Why does {topic} guarantee correctness? Provide the formal reasoning.",
            ("Application", "Medium"): f"Design a system that uses {topic} to solve a real-world problem in domain D.",
            ("Comparison", "Medium"): f"Compare {topic} with alternative approach A. When would you choose each?",
        }
        
        key = (target_type, target_difficulty)
        new_text = templates.get(key, f"Analyze {topic} in the context of {target_type.lower()} problems at {target_difficulty.lower()} level.")
        
        return {
            "question_text": new_text,
            "related_concepts": concepts,
            "similarity_score": 0.3,
            "generation_params": {
                "difficulty": target_difficulty,
                "type": target_type,
                "marks": target_marks,
                "variation_level": 0.5,
                "source_question_id": source_question["id"]
            }
        }
    
    def _check_similarity(self, new_question: str, existing_questions: List[Dict]) -> Tuple[float, bool]:
        """Check exact and semantic similarity against existing questions"""
        max_similarity = 0.0
        is_duplicate = False
        
        for eq in existing_questions:
            # Exact text similarity
            exact_sim = fast_fuzzy_similarity(new_question.lower(), eq["question_text"].lower())
            if exact_sim > max_similarity:
                max_similarity = exact_sim
            
            if exact_sim > self.EXACT_MATCH_THRESHOLD:
                is_duplicate = True
                break
        
        return max_similarity, is_duplicate
    
    def generate_similar_questions(self,
                                   source_question_id: str,
                                   count: int = 5,
                                   difficulty: str = None,
                                   question_type: str = None,
                                   marks: int = None,
                                   variation_level: float = 0.6) -> Dict[str, Any]:
        """Generate similar questions from a source question"""
        
        # Get source question
        source = None
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM question_bank WHERE id = ?", (source_question_id,))
        row = cursor.fetchone()
        
        if not row:
            # Check in assignments
            source_q = DatabaseRepo.get_assignment_by_id(source_question_id)
            if source_q and source_q.get("questions"):
                # Find specific question
                pass
        
        if row:
            source = dict(row)
            source["related_concepts"] = json.loads(source["related_concepts"]) if source["related_concepts"] else []
            source["generation_params"] = json.loads(source["generation_params"]) if source["generation_params"] else {}
        conn.close()
        
        if not source:
            # Fallback: search assignments
            assignments = DatabaseRepo.get_assignments(limit=100)
            for a in assignments:
                for q in a.get("questions", []):
                    if q.get("num") == source_question_id or f"{a['id']}_q{q['num']}" == source_question_id:
                        source = {
                            "id": f"{a['id']}_q{q['num']}",
                            "question_text": q.get("text", ""),
                            "subject": a.get("subject", ""),
                            "topic": q.get("topic", ""),
                            "difficulty": a.get("difficulty", "Medium"),
                            "question_type": q.get("type", "Exam"),
                            "marks": q.get("marks", 5)
                        }
                        break
        
        if not source:
            return {"success": False, "error": "Source question not found"}
        
        # Get existing questions for this topic
        existing = self._get_existing_questions(source.get("subject", ""), source.get("topic", ""))
        
        # Generate questions
        generated = []
        rejected = 0
        
        difficulties = ["Easy", "Medium", "Hard", "Advanced"]
        types = ["Conceptual", "Short", "Long", "Numerical", "Application", "Scenario", "Comparison", "Analytical", "Viva", "Exam"]
        
        for i in range(count * 3):  # try up to 3x to account for rejections
            if len(generated) >= count:
                break
            
            target_diff = difficulty or difficulties[i % len(difficulties)]
            target_type = question_type or types[i % len(types)]
            target_m = marks or source.get("marks", 5)
            
            result = self._generate_single_question(
                source, target_diff, target_type, target_m, variation_level, existing
            )
            
            if not result:
                rejected += 1
                continue
            
            # Check similarity
            sim_score, is_dup = self._check_similarity(result["question_text"], existing)
            
            if is_dup or sim_score > self.SIMILARITY_THRESHOLD:
                rejected += 1
                continue
            
            result["similarity_score"] = round(sim_score, 3)
            generated.append(result)
            
            # Add to existing for next iteration
            existing.append({"question_text": result["question_text"]})
        
        return {
            "success": True,
            "generated": generated,
            "rejected": rejected,
            "source_question_id": source_question_id
        }
    
    def generate_topic_questions(self,
                                  subject: str,
                                  topic: str,
                                  target_count: int = 20,
                                  difficulty_mix: Dict[str, int] = None,
                                  type_mix: Dict[str, int] = None) -> Dict[str, Any]:
        """Generate a full question bank for a topic"""
        
        # Get existing questions
        existing = self._get_existing_questions(subject, topic)
        current_count = len(existing)
        
        if current_count >= target_count:
            return {
                "success": True,
                "generated": [],
                "message": f"Topic already has {current_count} questions (target: {target_count})",
                "current_count": current_count
            }
        
        needed = target_count - current_count
        
        # Default difficulty/type mix
        if difficulty_mix is None:
            difficulty_mix = {"Easy": 5, "Medium": 8, "Hard": 5, "Advanced": 2}
        if type_mix is None:
            type_mix = {
                "Conceptual": 3, "Short": 2, "Long": 2, "Numerical": 4,
                "Application": 3, "Scenario": 2, "Comparison": 2, "Analytical": 2
            }
        
        # Analyze patterns from existing
        patterns = self._analyze_question_pattern(existing)
        
        # Select source questions from assignments/PYQs
        source_questions = self._get_source_questions_for_topic(subject, topic)
        
        generated = []
        rejected = 0
        
        # Build generation plan
        plan = []
        for diff, diff_count in difficulty_mix.items():
            for qtype, type_count in type_mix.items():
                plan.extend([(diff, qtype)] * min(diff_count, type_count))
        
        plan = plan[:needed]
        
        for i, (target_diff, target_type) in enumerate(plan):
            if len(generated) >= needed:
                break
            
            # Select source question
            source = source_questions[i % len(source_questions)] if source_questions else existing[i % len(existing)] if existing else None
            
            if not source:
                continue
            
            result = self._generate_single_question(
                source, target_diff, target_type, 
                source.get("marks", 5), 0.6, existing
            )
            
            if not result:
                rejected += 1
                continue
            
            sim_score, is_dup = self._check_similarity(result["question_text"], existing)
            
            if is_dup or sim_score > self.SIMILARITY_THRESHOLD:
                rejected += 1
                continue
            
            result["similarity_score"] = round(sim_score, 3)
            generated.append(result)
            existing.append({"question_text": result["question_text"]})
        
        return {
            "success": True,
            "generated": generated,
            "rejected": rejected,
            "needed": needed,
            "current_count": current_count
        }
    
    def _get_source_questions_for_topic(self, subject: str, topic: str) -> List[Dict]:
        """Get source questions from assignments and PYQs"""
        sources = []
        
        # From assignments
        assignments = DatabaseRepo.get_assignments(limit=200)
        for a in assignments:
            if a.get("subject") == subject:
                for q in a.get("questions", []):
                    if q.get("topic", "").lower() == topic.lower():
                        sources.append({
                            "id": f"assign_{a['id']}_q{q['num']}",
                            "question_text": q.get("text", ""),
                            "subject": subject,
                            "topic": topic,
                            "difficulty": a.get("difficulty", "Medium"),
                            "question_type": q.get("type", "Exam"),
                            "marks": q.get("marks", 5)
                        })
        
        # From PYQs
        pyqs = DatabaseRepo.get_pyq_papers()
        for p in pyqs:
            if p.get("subject") == subject:
                for q in p.get("parsed_questions", []):
                    if topic.lower() in q.get("text", "").lower():
                        sources.append({
                            "id": f"pyq_{p['id']}",
                            "question_text": q.get("text", ""),
                            "subject": subject,
                            "topic": topic,
                            "difficulty": "Medium",
                            "question_type": "Exam",
                            "marks": 10
                        })
        
        return sources
    
    def save_generated_questions(self, questions: List[Dict], subject: str, topic: str) -> List[str]:
        """Save generated questions to database"""
        conn = get_connection()
        cursor = conn.cursor()
        saved_ids = []
        
        for q in questions:
            q_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO question_bank (
                    id, question_text, subject, topic, subtopic, source_type,
                    source_id, source_question_id, difficulty, question_type,
                    marks, year, college, related_concepts, similarity_score,
                    generation_params, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q_id,
                q["question_text"],
                subject,
                topic,
                "",
                "AI_Generated",
                q.get("generation_params", {}).get("source_question_id", ""),
                q.get("generation_params", {}).get("source_question_id", ""),
                q.get("generation_params", {}).get("difficulty", "Medium"),
                q.get("generation_params", {}).get("type", "Exam"),
                q.get("generation_params", {}).get("marks", 5),
                None,
                "",
                json.dumps(q.get("related_concepts", [])),
                q.get("similarity_score", 0.0),
                json.dumps(q.get("generation_params", {})),
                "Approved",
                now,
                now
            ))
            
            saved_ids.append(q_id)
        
        # Update topic tracker
        cursor.execute("""
            INSERT OR REPLACE INTO topic_question_tracker 
            (id, subject, topic, target_count, current_count, last_generated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"{subject}_{topic}", subject, topic, 20,
            len(saved_ids) + self._get_topic_count(subject, topic),
            datetime.now(timezone.utc).isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return saved_ids
    
    def _get_topic_count(self, subject: str, topic: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM question_bank WHERE subject = ? AND topic = ? AND status = 'Approved'", 
                      (subject, topic))
        count = cursor.fetchone()[0]
        conn.close()
        return count

def get_course_question_set(course_code: str, set_num: int = 1) -> Dict[str, Any]:
    """Get all 15 questions for a course for a specific set (Set 1 or Set 2)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM question_bank 
        WHERE (subject = ? OR subject = (SELECT name FROM curriculum WHERE code = ? COLLATE NOCASE) OR subject = (SELECT code FROM curriculum WHERE name = ? COLLATE NOCASE)) 
          AND set_num = ? AND status = 'Approved'
        ORDER BY CAST(REPLACE(topic, 'Topic ', '') AS INTEGER), id
    """, (course_code, course_code, course_code, set_num))
    
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    seen = set()
    for r in rows:
        d = dict(r)
        q_text = d.get("question_text", "")
        if q_text not in seen:
            seen.add(q_text)
            d["related_concepts"] = json.loads(d["related_concepts"]) if d["related_concepts"] else []
            d["generation_params"] = json.loads(d["generation_params"]) if d["generation_params"] else {}
            questions.append(d)

    # Fallback to curriculum_questions module if DB has no entries
    if not questions:
        from .curriculum_questions import get_course_question_set as get_qs_from_module
        raw_qs = get_qs_from_module(course_code, set_num)
        for idx, q in enumerate(raw_qs):
            questions.append({
                "id": f"{course_code}-set{set_num}-{idx+1}",
                "question_text": q["text"],
                "subject": course_code,
                "topic": f"Topic {idx+1}",
                "subtopic": q.get("topic", ""),
                "difficulty": q.get("difficulty", "Medium"),
                "marks": q.get("marks", 5),
                "set_num": set_num,
                "status": "Approved"
            })
    
    return {
        "course_code": course_code,
        "set_num": set_num,
        "total": len(questions),
        "questions": questions
    }


def get_topic_question_bank(subject: str, topic: str, set_num: int = 1) -> Dict[str, Any]:
    """Get full question bank for a topic with stats"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM question_bank 
        WHERE (subject = ? OR subject = (SELECT name FROM curriculum WHERE code = ? COLLATE NOCASE) OR subject = (SELECT code FROM curriculum WHERE name = ? COLLATE NOCASE)) 
          AND topic = ? AND set_num = ? AND status = 'Approved'
        ORDER BY difficulty, question_type
    """, (subject, subject, subject, topic, set_num))
    
    rows = cursor.fetchall()
    if not rows:
        # Fallback query without set_num constraint
        cursor.execute("""
            SELECT * FROM question_bank 
            WHERE (subject = ? OR subject = (SELECT name FROM curriculum WHERE code = ? COLLATE NOCASE) OR subject = (SELECT code FROM curriculum WHERE name = ? COLLATE NOCASE)) 
              AND topic = ? AND status = 'Approved'
            ORDER BY difficulty, question_type
        """, (subject, subject, subject, topic))
        rows = cursor.fetchall()

    conn.close()
    
    questions = []
    stats = {"Easy": 0, "Medium": 0, "Hard": 0, "Advanced": 0}
    type_stats = {}
    seen = set()
    
    for r in rows:
        d = dict(r)
        q_text = d.get("question_text", "")
        if q_text not in seen:
            seen.add(q_text)
            d["related_concepts"] = json.loads(d["related_concepts"]) if d["related_concepts"] else []
            d["generation_params"] = json.loads(d["generation_params"]) if d["generation_params"] else {}
            questions.append(d)
            stats[d.get("difficulty", "Medium")] = stats.get(d.get("difficulty", "Medium"), 0) + 1
            type_stats[d.get("question_type", "Exam")] = type_stats.get(d.get("question_type", "Exam"), 0) + 1
    
    return {
        "subject": subject,
        "topic": topic,
        "set_num": set_num,
        "total": len(questions),
        "questions": questions,
        "difficulty_breakdown": stats,
        "type_breakdown": type_stats,
        "target": 20
    }


def get_all_topics_with_counts() -> List[Dict]:
    """Get all topics with their current question counts"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT subject, topic, COUNT(*) as count
        FROM question_bank 
        WHERE status = 'Approved'
        GROUP BY subject, topic
        ORDER BY subject, topic
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{"subject": r[0], "topic": r[1], "count": r[2]} for r in rows]