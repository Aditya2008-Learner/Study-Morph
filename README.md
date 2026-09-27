# 🎓 Assignment Sorter & AI Study Assistant

A full-stack, AI-powered academic platform for managing college assignments, analyzing previous-year papers, OCR-ing notes, generating study materials, grading answers, and RAG-based academic chat.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Start the server
python run.py

# 3. Open in browser
# http://127.0.0.1:8000
```

## 🐞 Debug in VS Code

1. Open the `Assignment Sorter` folder in VS Code.
2. Press `Ctrl + Shift + D` to open the **Run & Debug** panel.
3. Select **🚀 Debug FastAPI Server (Assignment Sorter)**.
4. Press `F5` to start the server with breakpoints enabled.

## 🧪 Run Tests

```bash
python -m unittest tests/test_end_to_end.py
```

---

## ✨ Features

- **B.Tech CSE Cyber Security Curriculum** — 8 semesters, 48+ courses
- **AI Assignment Generator** — Create 30-question exams from notes
- **Live Exam Interface** — Answer questions in text areas with LaTeX
- **AI Grader & Review** — 4-pillar rubric grading with detailed feedback
- **PYQ Paper Hunter** — Discover and import previous year papers
- **Notebook OCR** — Upload PDFs, DOCX, images (with Tesseract + C preprocessing)
- **RAG Academic Chat** — Context-aware AI tutor with citations
- **AI Note Maker** — Generate summaries, flashcards, formulas, mnemonics
- **AI Quiz Engine** — Topic-based MCQ quizzes with weakness radar
- **Native C Acceleration** — BM25 search, fuzzy matching, image preprocessing

---

## 🏗️ Architecture

- **Python (FastAPI)** — Backend, AI, scraping, OCR
- **C (DLL)** — Native utilities (BM25, Levenshtein, Otsu, contrast)
- **HTML/CSS/JS** — Modern responsive UI with KaTeX math rendering
- **SQLite** — Persistent storage with WAL journaling
- **Gemini 1.5 Flash** — Optional LLM API (falls back to local engine)