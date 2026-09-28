"""
API Endpoints for Intelligent Question Bank System
Add these routes to app.py
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional

from .web_question_engine import WebQuestionEngine
from .database import DatabaseRepo

router = APIRouter(prefix="/api/questions", tags=["Question Bank"])


def get_topic_question_bank(subject: str, topic: str) -> Dict[str, Any]:
    """Topic stats computed from the question bank"""
    rows = DatabaseRepo.get_question_bank_for_index()
    matching = [r for r in rows if r["subject"] == subject and r["topic"] == topic]
    difficulty: Dict[str, int] = {}
    types: Dict[str, int] = {}
    for r in matching:
        difficulty[r["difficulty"]] = difficulty.get(r["difficulty"], 0) + 1
        types[r["question_type"]] = types.get(r["question_type"], 0) + 1
    target = 20
    return {
        "total": len(matching),
        "difficulty_breakdown": difficulty,
        "type_breakdown": types,
        "target": target,
    }


def get_all_topics_with_counts() -> List[Dict[str, Any]]:
    """All subjects/topics with their approved question counts"""
    rows = DatabaseRepo.get_question_bank_for_index()
    counts: Dict[tuple, int] = {}
    for r in rows:
        key = (r["subject"], r["topic"])
        counts[key] = counts.get(key, 0) + 1
    return [
        {"subject": s, "topic": t, "count": c}
        for (s, t), c in sorted(counts.items())
    ]


@router.get("/topics")
async def get_topics():
    """Get all topics with question counts"""
    return get_all_topics_with_counts()


@router.get("/course/{course_code}")
async def get_course_questions(
    course_code: str,
    subject: Optional[str] = Query(None, description="Subject name"),
    topic: Optional[str] = Query(None, description="Topic name"),
    refresh: bool = Query(False, description="Generate fresh new question set"),
    session_id: Optional[str] = Query(None, description="Session ID for anti-duplication"),
    set_num: Optional[int] = Query(None, alias="set", description="Legacy set number")
):
    """
    Generate exactly 15 web-researched questions for a course and topic.
    Every refresh yields a completely fresh set of 15 questions with duplicate prevention.
    """
    c_code = str(course_code) if (course_code is not None and not hasattr(course_code, 'default')) else "CS201"
    subj = str(subject) if (subject is not None and not hasattr(subject, 'default')) else None
    top = str(topic) if (topic is not None and not hasattr(topic, 'default')) else None
    ref = bool(refresh) if (refresh is not None and not hasattr(refresh, 'default')) else False
    sess = str(session_id) if (session_id is not None and not hasattr(session_id, 'default')) else None
    try:
        return WebQuestionEngine.generate_questions(
            course_code=c_code,
            subject=subj,
            topic=top,
            session_id=sess,
            force_refresh=ref
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@router.post("/course/{course_code}/refresh")
@router.post("/refresh")
async def refresh_course_questions(
    course_code: Optional[str] = None,
    data: Dict[str, Any] = Body({})
):
    """
    Refresh endpoint: Conducts fresh web research and generates 15 new questions.
    """
    code = course_code if (isinstance(course_code, str)) else (data.get("course_code") or data.get("course") or "CS201")
    subject = data.get("subject")
    topic = data.get("topic")
    session_id = data.get("session_id")
    try:
        return WebQuestionEngine.generate_questions(
            course_code=code,
            subject=subject,
            topic=topic,
            session_id=session_id,
            force_refresh=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question refresh failed: {str(e)}")


@router.get("/topic/{subject}/{topic}")
async def get_topic_bank(
    subject: str,
    topic: str,
    refresh: bool = Query(False),
    session_id: Optional[str] = Query(None),
    set_num: Optional[int] = Query(None, alias="set", description="Legacy set number")
):
    """Get fresh 15 web-researched questions for a topic"""
    subj = str(subject) if (subject is not None and not hasattr(subject, 'default')) else "Computer Science"
    top = str(topic) if (topic is not None and not hasattr(topic, 'default')) else "General"
    ref = bool(refresh) if (refresh is not None and not hasattr(refresh, 'default')) else False
    sess = str(session_id) if (session_id is not None and not hasattr(session_id, 'default')) else None
    try:
        return WebQuestionEngine.generate_questions(
            course_code=subj,
            subject=subj,
            topic=top,
            session_id=sess,
            force_refresh=ref
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic question generation failed: {str(e)}")


@router.get("/topic-stats/{subject}/{topic}")
async def get_topic_stats(subject: str, topic: str):
    """Get statistics for a topic"""
    bank = get_topic_question_bank(subject, topic)
    return {
        "subject": subject,
        "topic": topic,
        "total_questions": bank["total"],
        "difficulty_breakdown": bank["difficulty_breakdown"],
        "type_breakdown": bank["type_breakdown"],
        "target": bank["target"],
        "completion_rate": round(bank["total"] / bank["target"] * 100, 1)
    }


