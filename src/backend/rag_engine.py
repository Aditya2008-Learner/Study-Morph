import os
import re
from typing import List, Dict, Any, Optional

from ..c_core.c_bridge import fast_batch_bm25, fast_fuzzy_similarity, fast_levenshtein
from .database import DatabaseRepo


class RAGChunk:
    def __init__(self, chunk_id, doc_id, doc_name, doc_type, text, page_or_sec="",
                 subject="", topic="", difficulty="", marks=0):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.doc_type = doc_type
        self.text = text
        self.page_or_sec = page_or_sec
        self.subject = subject
        self.topic = topic
        self.difficulty = difficulty
        self.marks = marks
        self.tokens = self._tokenize(text)
        self.length = len(self.tokens)

    @staticmethod
    def _tokenize(text):
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of", "it", "this", "that", "these", "those", "from"}
        return [t for t in cleaned.split() if len(t) > 2 and t not in stopwords]


def _flatten(value: Any) -> str:
    """Render a JSON-ish field (list, dict, or scalar) as searchable text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_flatten(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten(v) for v in value)
    return str(value)


def _topic_blob(topic_row: Dict[str, Any]) -> str:
    """Flatten a topic_content row into indexable text."""
    parts = [topic_row.get("summary", "") or ""]
    for field in ("key_points", "formulas", "examples", "viva_questions"):
        parts.append(_flatten(topic_row.get(field)))
    return " ".join(p for p in parts if p)


class RAGIndex:
    # Measured against the real vocabulary, not guessed. Real single-token typos
    # score 0.83-0.88 (systm->system 0.83, dinamic->dynamic 0.86,
    # deadlok->deadlock 0.88), while unrelated collisions sit far lower
    # (sorting->working 0.71, nonsense->consensus 0.67, xyzzy->xyz 0.60).
    # 0.80 separates them with margin on both sides.
    FUZZY_THRESHOLD = 0.80

    _instance = None

    def __init__(self):
        self.chunks = []
        self.doc_frequencies = {}
        self.avg_doc_len = 0.0
        self.topic_rows = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.rebuild_index()
        return cls._instance

    def rebuild_index(self):
        self.chunks = []
        self.doc_frequencies = {}
        self.topic_rows = {}

        for q in DatabaseRepo.get_question_bank_for_index():
            self._add_chunks(
                q["id"], q["question_text"][:80], "question", q["question_text"],
                q.get("topic", ""), subject=q.get("subject", ""), topic=q.get("topic", ""),
                difficulty=q.get("difficulty", ""), marks=q.get("marks", 0),
            )

        for t in DatabaseRepo.get_all_topics():
            self._add_chunks(
                t["id"], f"{t['course_code']} — {t['topic_name']}", "topic", _topic_blob(t),
                t["topic_name"], subject=t["course_code"], topic=t["topic_name"],
            )
            self.topic_rows[t["id"]] = t

        for f in DatabaseRepo.get_all_interactive_content():
            blob = f"{f.get('front_text', '')} {f.get('back_text', '')}"
            self._add_chunks(
                f["id"], f"{f.get('front_text', '')[:80]}", "flashcard", blob,
                f.get("topic", ""), subject=f.get("course_code", ""), topic=f.get("topic", ""),
            )

        total_tokens = sum(c.length for c in self.chunks)
        self.avg_doc_len = (total_tokens / len(self.chunks)) if self.chunks else 50.0

        for c in self.chunks:
            for t in set(c.tokens):
                self.doc_frequencies[t] = self.doc_frequencies.get(t, 0) + 1

    def _add_chunks(self, doc_id, doc_name, doc_type, text, page_or_sec,
                    subject="", topic="", difficulty="", marks=0):
        if not text or len(text.strip()) < 10:
            return
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [text.strip()]
        for i, p in enumerate(paragraphs):
            chunk = RAGChunk(f"{doc_id}_{i}", doc_id, doc_name, doc_type, p, page_or_sec,
                             subject=subject, topic=topic, difficulty=difficulty, marks=marks)
            self.chunks.append(chunk)

    def _prefix_match(self, token: str) -> Optional[str]:
        """Resolve an abbreviation to a corpus term (prog -> programming).

        A bare startswith() is too greedy: it maps unrelated tokens onto whatever
        corpus term happens to share their first letters (`the` -> `them`,
        `nonsense` -> `non...`). The length-normalized fuzzy score cannot arbitrate
        here either, because a short abbreviation of a long word is inherently
        low-scoring (prog vs programming is only 0.36).

        So prefix matching stands on its own evidence: the token must be a
        substantial share of the term it claims, and the term must be long enough
        that the shared letters are not coincidence. `prog`/`program` (0.57) and
        `memo`/`memoization` (0.36) both pass the length test; `the`/`them` (0.75)
        is rejected by requiring the longer side to be a real word-length term.
        """
        if len(token) < 3:
            return None
        best = None
        for term in self.doc_frequencies:
            if not term.startswith(token) or len(term) < 5:
                continue
            if (len(token) / len(term)) < 0.3:
                continue
            if best is None or len(term) < len(best):
                best = term
        return best

    def _resolve_token(self, token: str) -> Optional[str]:
        """Map a raw query token onto a corpus term: direct, prefix, then fuzzy.

        The fuzzy pass also enforces an edit-distance ceiling. Length-normalized
        similarity alone lets short tokens snap onto unrelated same-length words
        with a single letter change (`calls` -> `cells`, which is what hijacked
        a "system calls" query toward Electrochemistry). Requiring at most one
        edit for a short token keeps genuine typos (`systm` -> `system`) while
        rejecting that class of collision.
        """
        if token in self.doc_frequencies:
            return token
        prefix = self._prefix_match(token)
        if prefix:
            return prefix
        best_match, best_sim = None, 0.0
        for known_term in self.doc_frequencies:
            distance = fast_levenshtein(token, known_term)
            sim = fast_fuzzy_similarity(token, known_term)
            if sim < self.FUZZY_THRESHOLD:
                continue
            if len(token) <= 5:
                # A single edit on a short token is a coin flip: `systm`->`system`
                # is a typo we want, `calls`->`cells` is a collision we don't.
                # Distinguish them by edit *shape` - a typo of a real term usually
                # leaves the token's own prefix intact, while a substitution
                # collision tends to change an interior letter. Prefer the longer
                # term only when the token's first 3 characters still align.
                if distance == 1 and token[:3] != known_term[:3]:
                    continue
                if distance > 1:
                    continue
            elif distance > 2:
                continue
            if sim > best_sim:
                best_sim, best_match = sim, known_term
        return best_match

    def search(self, query, top_k=12):
        if not self.chunks:
            self.rebuild_index()
        query_tokens = RAGChunk._tokenize(query)[:64]
        if not query_tokens:
            return []
        total_docs = len(self.chunks)
        scores = [0.0] * total_docs

        for token in query_tokens:
            resolved = self._resolve_token(token)
            if not resolved:
                continue
            df = self.doc_frequencies.get(resolved, 0)
            if df == 0:
                continue
            tfs = [chunk.tokens.count(resolved) for chunk in self.chunks]
            doc_lens = [chunk.length for chunk in self.chunks]
            term_scores = fast_batch_bm25(tfs, doc_lens, self.avg_doc_len, total_docs, df)
            for i in range(total_docs):
                scores[i] += term_scores[i]

        ranked = sorted(range(total_docs), key=lambda i: scores[i], reverse=True)
        results = []
        for idx in ranked[:top_k]:
            if scores[idx] > 0.05:
                c = self.chunks[idx]
                results.append({
                    "chunk_id": c.chunk_id,
                    "doc_id": c.doc_id,
                    "doc_name": c.doc_name,
                    "source_type": c.doc_type,
                    "text": c.text,
                    "subject": c.subject,
                    "topic": c.topic,
                    "difficulty": c.difficulty,
                    "marks": c.marks,
                    "score": round(scores[idx], 4),
                    "citation": f"[{c.doc_type}: {c.doc_name}]",
                })
        return results

    def get_topic_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Best-matching topic_content row for a query, with its study material."""
        for r in self.search(query, top_k=25):
            if r["source_type"] != "topic":
                continue
            row = self.topic_rows.get(r["doc_id"])
            if row:
                return {
                    "subject": row.get("course_code", ""),
                    "topic": row.get("topic_name", ""),
                    "summary": row.get("summary", ""),
                    "formulas": row.get("formulas", []),
                    "key_points": row.get("key_points", []),
                    "flashcards": row.get("flashcards", []),
                }
        return None
