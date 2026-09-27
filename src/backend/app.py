import os
import sys
import shutil
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
if os.path.exists("C:/Users/dell/.env"):
    load_dotenv("C:/Users/dell/.env")

from .database import DatabaseRepo, init_db, get_connection
from .scraper import PYQScraper
from .ocr_parser import NotebookParser
from .ai_engine import AIEngine
from .rag_engine import RAGIndex
from .assignment_gen import AssignmentGenerator
from .grader import AssignmentGrader
from .note_maker import NoteMaker
from .quiz_engine import QuizEngine
from .question_bank_api import router as question_bank_router
from ..c_core.c_bridge import _lib_loaded

app = FastAPI(
    title="Assignment Sorter & AI Study Assistant",
    description="Intelligent academic platform for managing, generating, grading assignments, and studying with AI.",
    version="2.0.0"
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

@app.get("/api/assignments")
async def list_assignments(
    college: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    is_pyq: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("DESC"),
    limit: int = Query(100),
    offset: int = Query(0)
):
    return DatabaseRepo.get_assignments(
        college=college,
        subject=subject,
        semester=semester,
        academic_year=academic_year,
        status=status,
        difficulty=difficulty,
        is_pyq=is_pyq,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

@app.get("/api/assignments/{assignment_id}")
async def get_assignment(assignment_id: str):
    assignment = DatabaseRepo.get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@app.post("/api/assignments")
async def create_assignment(data: Dict[str, Any] = Body(...)):
    res = DatabaseRepo.create_assignment(data)
    RAGIndex.get_instance().rebuild_index()
    return res

@app.put("/api/assignments/{assignment_id}")
async def update_assignment(assignment_id: str, updates: Dict[str, Any] = Body(...)):
    res = DatabaseRepo.update_assignment(assignment_id, updates)
    if not res:
        raise HTTPException(status_code=404, detail="Assignment not found")
    RAGIndex.get_instance().rebuild_index()
    return res

@app.delete("/api/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str):
    success = DatabaseRepo.delete_assignment(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    RAGIndex.get_instance().rebuild_index()
    return {"message": "Assignment deleted successfully"}

@app.post("/api/assignments/batch-export")
async def batch_export(data: Dict[str, Any] = Body(...)):
    ids = data.get("assignment_ids", [])
    export_format = data.get("format", "json")
    
    assignments = []
    for aid in ids:
        a = DatabaseRepo.get_assignment_by_id(aid)
        if a:
            assignments.append(a)
            
    if not assignments:
        assignments = DatabaseRepo.get_assignments(limit=50)

    if export_format == "json":
        return JSONResponse(content=assignments)
    elif export_format == "markdown":
        md_text = "# Academic Assignment Repository Export\n\n"
        for a in assignments:
            md_text += f"## {a['title']}\n"
            md_text += f"- **College:** {a['college']} | **Subject:** {a['subject']} | **Sem:** {a['semester']} | **Year:** {a['academic_year']}\n"
            md_text += f"- **Difficulty:** {a['difficulty']} | **Status:** {a['status']}\n\n"
            md_text += f"### Questions:\n"
            for q in a.get("questions", []):
                md_text += f"{q.get('num', '-')}. ({q.get('marks', 5)} Marks) {q.get('text', '')}\n"
            md_text += "\n---\n\n"
        return Response(content=md_text, media_type="text/markdown")
    else:
        csv_lines = ["ID,Title,College,Subject,Semester,AcademicYear,Status,Difficulty"]
        for a in assignments:
            title_escaped = a['title'].replace('"', '""')
            csv_lines.append(f'"{a["id"]}","{title_escaped}","{a["college"]}","{a["subject"]}","{a["semester"]}","{a["academic_year"]}","{a["status"]}","{a["difficulty"]}"')
        return Response(content="\n".join(csv_lines), media_type="text/csv")

@app.get("/api/pyq/search")
async def search_pyq(
    subject: Optional[str] = Query(None, description="Subject or course name"),
    college: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    year: Optional[str] = Query(None)
):
    s = subject if isinstance(subject, str) else None
    c = college if isinstance(college, str) else None
    sem = semester if isinstance(semester, str) else None
    y = year if isinstance(year, str) else None
    return PYQScraper.search_online_pyq(
        subject=s,
        college=c,
        semester=sem,
        year=y
    )

@app.post("/api/pyq/import")
async def import_pyq(paper_data: Dict[str, Any] = Body(...)):
    assignment = PYQScraper.import_pyq_to_repository(paper_data)
    RAGIndex.get_instance().rebuild_index()
    return assignment

@app.get("/api/pyq/papers")
async def list_pyq_papers(
    college: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    semester: Optional[str] = Query(None)
):
    return DatabaseRepo.get_pyq_papers(college=college, subject=subject, semester=semester)

@app.post("/api/notebooks/upload")
async def upload_notebook(
    file: UploadFile = File(...),
    college: str = Form("University"),
    subject: str = Form("General"),
    semester: str = Form("1")
):
    file_id = str(uuid.uuid4())
    original_name = file.filename or "uploaded_document"
    ext = os.path.splitext(original_name)[1].lower()
    saved_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOADS_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    
    extracted_text = NotebookParser.parse_file(file_path, original_name)
    topics = NotebookParser.extract_topics(extracted_text)
    formulas = NotebookParser.extract_formulas(extracted_text)
    key_points = NotebookParser.extract_key_points(extracted_text)
    summary = NotebookParser.generate_summary(extracted_text, topics)
    
    notebook_record = DatabaseRepo.create_notebook({
        "id": file_id,
        "filename": saved_filename,
        "original_name": original_name,
        "file_type": ext.replace(".", "").upper(),
        "file_size": file_size,
        "college": college,
        "subject": subject,
        "semester": semester,
        "raw_text": extracted_text,
        "extracted_topics": topics,
        "summary": summary,
        "formulas": formulas,
        "key_points": key_points,
        "status": "Analyzed & Ready"
    })
    
    RAGIndex.get_instance().rebuild_index()
    return notebook_record

@app.get("/api/notebooks")
async def list_notebooks():
    return DatabaseRepo.get_notebooks()

@app.get("/api/notebooks/{notebook_id}")
async def get_notebook(notebook_id: str):
    nb = DatabaseRepo.get_notebook_by_id(notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb

@app.delete("/api/notebooks/{notebook_id}")
async def delete_notebook(notebook_id: str):
    nb = DatabaseRepo.get_notebook_by_id(notebook_id)
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    file_path = os.path.join(UPLOADS_DIR, nb["filename"])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
            
    DatabaseRepo.delete_notebook(notebook_id)
    RAGIndex.get_instance().rebuild_index()
    return {"message": "Notebook deleted successfully"}

@app.post("/api/generator/create")
async def generate_assignment(data: Dict[str, Any] = Body(...)):
    return AssignmentGenerator.generate_assignment(
        notebook_id=data.get("notebook_id"),
        subject=data.get("subject", "General"),
        semester=str(data.get("semester", "1")),
        difficulty=data.get("difficulty", "Intermediate"),
        target_exam=data.get("target_exam", "University Exam"),
        topics=data.get("topics", []),
        num_questions=int(data.get("num_questions", 30))
    )

@app.get("/api/generator/assignments")
async def list_generated_assignments(notebook_id: Optional[str] = Query(None)):
    return DatabaseRepo.get_generated_assignments(notebook_id=notebook_id)

@app.get("/api/generator/assignments/{gen_id}")
async def get_generated_assignment(gen_id: str):
    item = DatabaseRepo.get_generated_assignment_by_id(gen_id)
    if not item:
        raise HTTPException(status_code=404, detail="Generated assignment not found")
    return item

@app.post("/api/help/hint")
async def get_hint(data: Dict[str, Any] = Body(...)):
    question_text = data.get("question_text", "")
    level = int(data.get("level", 1))
    context = data.get("context", "")
    return AssignmentGrader.get_progressive_hint(question_text, level, context)

@app.post("/api/help/evaluate")
async def evaluate_submission(data: Dict[str, Any] = Body(...)):
    assignment_id = data.get("assignment_id", "")
    question_id = str(data.get("question_id", "q1"))
    question_text = data.get("question_text", "")
    student_answer = data.get("student_answer", "")
    total_marks = float(data.get("total_marks", 10.0))
    model_answer_summary = data.get("model_answer_summary", "")
    
    evaluation = AssignmentGrader.evaluate_answer(
        question_text=question_text,
        student_answer=student_answer,
        total_marks=total_marks,
        model_answer_summary=model_answer_summary
    )
    
    if assignment_id:
        DatabaseRepo.record_submission({
            "assignment_id": assignment_id,
            "question_id": question_id,
            "student_answer": student_answer,
            "marks_awarded": evaluation.get("marks_awarded", 0),
            "total_marks": total_marks,
            "accuracy_score": evaluation.get("accuracy_score", 0),
            "completeness_score": evaluation.get("completeness_score", 0),
            "feedback_text": evaluation.get("feedback_text", ""),
            "rubric_breakdown": evaluation.get("rubric_breakdown", {}),
            "missing_points": evaluation.get("missing_points", []),
            "model_answer": evaluation.get("model_answer", "")
        })
        
    return evaluation

@app.get("/api/help/submissions/{assignment_id}")
async def get_submissions(assignment_id: str):
    return DatabaseRepo.get_submissions_for_assignment(assignment_id)

@app.post("/api/notes/generate")
async def generate_notes(data: Dict[str, Any] = Body(...)):
    return NoteMaker.generate_study_notes(
        notebook_id=data.get("notebook_id"),
        subject=data.get("subject", "Computer Science"),
        topic=data.get("topic", "Core Concepts")
    )

@app.get("/api/notes")
async def list_notes(notebook_id: Optional[str] = Query(None), subject: Optional[str] = Query(None)):
    return DatabaseRepo.get_study_notes(notebook_id=notebook_id, subject=subject)

@app.post("/api/quiz/generate")
async def generate_quiz(data: Dict[str, Any] = Body(...)):
    return QuizEngine.generate_quiz(
        notebook_id=data.get("notebook_id"),
        subject=data.get("subject", "Computer Science"),
        topic=data.get("topic", "General"),
        num_questions=int(data.get("num_questions", 5))
    )

@app.get("/api/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    q = DatabaseRepo.get_quiz_by_id(quiz_id)
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return q

@app.post("/api/quiz/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, data: Dict[str, Any] = Body(...)):
    answers = data.get("answers", [])
    try:
        time_taken = int(data.get("time_taken_seconds", 60))
    except (ValueError, TypeError):
        time_taken = 60
    try:
        return QuizEngine.grade_attempt(quiz_id, answers, time_taken)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/quiz/analytics/radar")
async def get_quiz_radar():
    return DatabaseRepo.get_weakness_radar()

@app.post("/api/chat/message")
async def chat_message(data: Dict[str, Any] = Body(...)):
    query = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session")
    
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    DatabaseRepo.add_chat_message(session_id, "user", query)
    ai_res = AIEngine.chat_rag_response(query, session_id=session_id)
    DatabaseRepo.add_chat_message(session_id, "assistant", ai_res["response"], ai_res["citations"])
    
    return ai_res

@app.get("/api/chat/history")
async def get_chat_history(session_id: str = Query("default_session")):
    return DatabaseRepo.get_chat_history(session_id)

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

@app.get("/api/progress")
async def get_learning_progress():
    """Get learning progress across all topics"""
    return DatabaseRepo.get_learning_progress()

@app.put("/api/progress/{subject}/{topic}")
async def update_progress(subject: str, topic: str, data: Dict[str, Any] = Body(...)):
    """Update progress for a specific topic"""
    return DatabaseRepo.update_topic_progress(
        subject=subject,
        topic=topic,
        status=data.get("status"),
        progress_pct=data.get("progress_percentage"),
        quiz_score=data.get("quiz_score")
    )

@app.get("/api/recommendations")
async def get_recommendations():
    """Get smart study recommendations"""
    return DatabaseRepo.get_recommendations()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run("src.backend.app:app", host=host, port=port, reload=True)