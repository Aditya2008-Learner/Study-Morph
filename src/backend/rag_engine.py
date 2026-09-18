import os
import re
from typing import List, Dict, Any, Optional

from ..c_core.c_bridge import fast_batch_bm25, fast_fuzzy_similarity
from .database import DatabaseRepo

class RAGChunk:
    def __init__(self, chunk_id, doc_id, doc_name, doc_type, text, page_or_sec=""):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.doc_type = doc_type
        self.text = text
        self.page_or_sec = page_or_sec
        self.tokens = self._tokenize(text)
        self.length = len(self.tokens)

    @staticmethod
    def _tokenize(text):
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at", "to", "for", "with", "by", "of", "it", "this", "that", "these", "those", "from"}
        return [t for t in cleaned.split() if len(t) > 2 and t not in stopwords]

class RAGIndex:
    _instance = None

    def __init__(self):
        self.chunks = []
        self.doc_frequencies = {}
        self.avg_doc_len = 0.0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.rebuild_index()
        return cls._instance

    def rebuild_index(self):
        self.chunks = []
        self.doc_frequencies = {}

        notebooks = DatabaseRepo.get_notebooks()
        for nb in notebooks:
            text = nb.get("raw_text", "")
            pages = text.split("--- Page ")
            if len(pages) > 1:
                for p in pages[1:]:
                    lines = p.split("\n", 1)
                    page_num = lines[0].replace("---", "").strip()
                    page_content = lines[1] if len(lines) > 1 else ""
                    self._add_chunks(nb["id"], nb["original_name"], "Notebook", page_content, f"Page {page_num}")
            else:
                self._add_chunks(nb["id"], nb["original_name"], "Notebook", text, "Section 1")

        assignments = DatabaseRepo.get_assignments(limit=200)
        for a in assignments:
            content = f"{a['title']}\n{a.get('content_text', '')}"
            for q in a.get("questions", []):
                content += f"\nQuestion {q.get('num', '')}: {q.get('text', '')}"
            self._add_chunks(a["id"], a["title"], "Assignment", content, a.get("subject", "Coursework"))

        pyqs = DatabaseRepo.get_pyq_papers()
        for p in pyqs:
            self._add_chunks(p["id"], p["title"], "Previous Year Paper", p.get("content_text", ""), p.get("subject", "Exam"))

        total_tokens = sum(c.length for c in self.chunks)
        self.avg_doc_len = (total_tokens / len(self.chunks)) if self.chunks else 50.0

        for c in self.chunks:
            seen = set(c.tokens)
            for t in seen:
                self.doc_frequencies[t] = self.doc_frequencies.get(t, 0) + 1

    def _add_chunks(self, doc_id, doc_name, doc_type, text, page_or_sec):
        if not text or len(text.strip()) < 10:
            return
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [text.strip()]
        for i, p in enumerate(paragraphs):
            chunk = RAGChunk(f"{doc_id}_{i}", doc_id, doc_name, doc_type, p, page_or_sec)
            self.chunks.append(chunk)

    def search(self, query, top_k=5):
        if not self.chunks:
            self.rebuild_index()
        query_tokens = RAGChunk._tokenize(query)
        if not query_tokens:
            return []
        total_docs = len(self.chunks)
        if total_docs == 0:
            return []
        scores = [0.0] * total_docs
        for token in query_tokens:
            df = self.doc_frequencies.get(token, 0)
            if df == 0:
                best_match = None
                best_sim = 0.0
                for known_term in self.doc_frequencies:
                    sim = fast_fuzzy_similarity(token, known_term)
                    if sim > 0.8 and sim > best_sim:
                        best_sim = sim
                        best_match = known_term
                if best_match:
                    token = best_match
                    df = self.doc_frequencies.get(token, 0)
                else:
                    continue
            tfs = [chunk.tokens.count(token) for chunk in self.chunks]
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
                    "doc_type": c.doc_type,
                    "page_or_sec": c.page_or_sec,
                    "text": c.text,
                    "score": round(scores[idx], 4),
                    "citation": f"[{c.doc_type}: {c.doc_name}, {c.page_or_sec}]"
                })
        return results