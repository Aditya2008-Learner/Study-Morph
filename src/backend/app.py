import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
if os.path.exists("C:/Users/dell/.env"):
    load_dotenv("C:/Users/dell/.env")

from .database import DatabaseRepo, init_db
from .ai_engine import AIEngine
from .rag_engine import RAGIndex, RAGChunk
from .question_bank_api import router as question_bank_router
from ..c_core.c_bridge import _lib_loaded

app = FastAPI(
    title="StudyMorph",
    description="Exam-prep instrument: curated syllabus units, question banks, and native BM25 search.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include question bank router
app.include_router(question_bank_router)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Mount static folder for assets like styles/scripts
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def find_html_file(filename: str) -> Optional[str]:
    """Search for an HTML file across all standard project locations."""
    search_paths = [
        os.path.join(STATIC_DIR, "templates", filename),
        os.path.join(STATIC_DIR, filename),
        os.path.join(BASE_DIR, filename),
        os.path.join(os.getcwd(), filename),
        filename,
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    return None

@app.on_event("startup")
async def startup_event():
    init_db()

# --- Page Routes ---

@app.get("/", response_class=FileResponse)
@app.get("/index.html", response_class=FileResponse)
async def serve_index():
    file_path = find_html_file("index.html")
    if file_path:
        return FileResponse(file_path)
    return HTMLResponse(
        content="<h1>index.html not found. Place it in static/templates/ or the root project folder.</h1>", 
        status_code=404
    )

@app.get("/course.html", response_class=FileResponse)
@app.get("/course", response_class=FileResponse)
async def serve_course():
    file_path = find_html_file("course.html")
    if file_path:
        return FileResponse(file_path)
    raise HTTPException(
        status_code=404, 
        detail="course.html not found. Place it in static/templates/ or alongside index.html."
    )

# --- System APIs ---

@app.get("/api/system/status")
async def get_system_status():
    rag = RAGIndex.get_instance()
    meta = DatabaseRepo.get_distinct_metadata()
    assignments = DatabaseRepo.get_assignments(limit=1000)
    notebooks = DatabaseRepo.get_notebooks()
    
    return {
        "status": "online",
        "c_core_accelerated": _lib_loaded,
        "gemini_api_configured": AIEngine.is_gemini_available(),
        "total_assignments": len(assignments),
        "total_notebooks": len(notebooks),
        "indexed_rag_chunks": len(rag.chunks),
        "available_colleges": len(meta["colleges"]),
        "available_subjects": len(meta["subjects"]),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/metadata")
async def get_metadata():
    return DatabaseRepo.get_distinct_metadata()

@app.get("/api/curriculum")
async def get_curriculum(semester: Optional[int] = Query(None)):
    if semester:
        return DatabaseRepo.get_curriculum_by_semester(semester)
    return DatabaseRepo.get_curriculum()

@app.get("/api/curriculum/full")
async def get_full_curriculum():
    """Get complete 4-year B.Tech curriculum"""
    return DatabaseRepo.get_full_curriculum()

@app.get("/api/curriculum/year/{year}")
async def get_curriculum_by_year(year: int):
    """Get curriculum for a specific year (1-4)"""
    if year not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Year must be 1, 2, 3, or 4")
    return DatabaseRepo.get_curriculum_by_year(year)

@app.get("/api/curriculum/{code}")
async def get_course_by_code(code: str):
    course = DatabaseRepo.get_curriculum_by_code(code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# ===== TOPIC CONTENT API =====
@app.get("/api/topics")
async def get_all_topics():
    """Get all topics across all courses"""
    return DatabaseRepo.get_all_topics()

@app.get("/api/topics/search")
async def search_topics(keyword: str = Query(..., description="Search keyword")):
    """Search topics by keyword"""
    return DatabaseRepo.get_topic_by_keyword(keyword)

@app.get("/api/content/{course_code}")
async def get_topic_content(course_code: str, topic: Optional[str] = Query(None)):
    """Get study content for a specific course or topic"""
    return DatabaseRepo.get_topic_content(course_code, topic)

@app.get("/api/content/{course_code}/{topic_name}")
async def get_specific_topic(course_code: str, topic_name: str):
    """Get specific topic content"""
    return DatabaseRepo.get_topic_content(course_code, topic_name)

@app.get("/api/interactive/{course_code}")
async def get_interactive_content(course_code: str):
    """Get interactive flashcards linked to course_code (from interactive_content or topic_content table)"""
    return DatabaseRepo.get_interactive_content(course_code)

# ===== ACTIVITY & PROGRESS API =====
@app.post("/api/activity/log")
async def log_activity(data: Dict[str, Any] = Body(...)):
    """Log student activity"""
    return DatabaseRepo.log_student_activity(
        activity_type=data.get("activity_type", "view"),
        subject=data.get("subject", ""),
        topic=data.get("topic", ""),
        details=data.get("details", {}),
        duration=data.get("duration_seconds", 0),
        score=data.get("score", 0)
    )

# ===== SEARCH API =====
@app.get("/api/search")
async def search_corpus(
    q: str = Query(..., description="Raw study query"),
    limit: int = Query(12, ge=1, le=50, description="Max results")
):
    """Keyword search across the question bank, syllabus units, and flashcards.

    Deliberately offline: BM25 over a locally built index, with typo and
    abbreviation tolerance. No LLM call, so it cannot fail on a missing API key
    or a dropped network mid-demo.
    """
    query = q.strip()
    if not query or not RAGChunk._tokenize(query):
        raise HTTPException(
            status_code=400,
            detail="Type a topic, concept, or question keyword."
        )
    index = RAGIndex.get_instance()
    results = index.search(query, top_k=limit)
    return {
        "query": query,
        "total": len(results),
        "results": results,
        "topic_context": index.get_topic_context(query),
    }

