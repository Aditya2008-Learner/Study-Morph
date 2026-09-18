"""
API Endpoints for Intelligent Question Bank System
Add these routes to app.py
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional

from .question_generator import (
    QuestionGenerator,
    get_topic_question_bank,
    get_all_topics_with_counts,
    get_course_question_set
)

router = APIRouter(prefix="/api/questions", tags=["Question Bank"])
qgen = QuestionGenerator()


@router.get("/topics")
async def get_topics():
    """Get all topics with question counts"""
    return get_all_topics_with_counts()


@router.get("/course/{course_code}")
async def get_course_questions(
    course_code: str,
    set_num: int = Query(1, alias="set", description="Question set number (1 or 2)")
):
    """Get all 15 questions for a course for a specific set (Set 1 or Set 2)"""
    return get_course_question_set(course_code, set_num)


@router.get("/topic/{subject}/{topic}")
async def get_topic_bank(
    subject: str,
    topic: str,
    set_num: int = Query(1, alias="set", description="Question set number (1 or 2)")
):
    """Get full question bank for a topic"""
    return get_topic_question_bank(subject, topic, set_num)


@router.post("/generate/similar")
async def generate_similar_questions(
    data: Dict[str, Any] = Body(...)
):
    """Generate similar questions from a source question"""
    source_id = data.get("source_question_id")
    count = data.get("count", 5)
    difficulty = data.get("difficulty")
    question_type = data.get("question_type")
    marks = data.get("marks")
    variation = data.get("variation_level", 0.6)
    
    if not source_id:
        raise HTTPException(status_code=400, detail="source_question_id required")
    
    result = qgen.generate_similar_questions(
        source_question_id=source_id,
        count=count,
        difficulty=difficulty,
        question_type=question_type,
        marks=marks,
        variation_level=variation
    )
    
    return result


@router.post("/generate/topic")
async def generate_topic_questions(
    data: Dict[str, Any] = Body(...)
):
    """Generate full question bank for a topic"""
    subject = data.get("subject")
    topic = data.get("topic")
    target_count = data.get("target_count", 20)
    difficulty_mix = data.get("difficulty_mix")
    type_mix = data.get("type_mix")
    
    if not subject or not topic:
        raise HTTPException(status_code=400, detail="subject and topic required")
    
    result = qgen.generate_topic_questions(
        subject=subject,
        topic=topic,
        target_count=target_count,
        difficulty_mix=difficulty_mix,
        type_mix=type_mix
    )
    
    return result


@router.post("/generate/pyq-similar")
async def generate_from_pyq(
    data: Dict[str, Any] = Body(...)
):
    """Generate similar questions from a PYQ paper"""
    pyq_id = data.get("pyq_id")
    count = data.get("count", 10)
    difficulty = data.get("difficulty")
    question_type = data.get("question_type")
    
    if not pyq_id:
        raise HTTPException(status_code=400, detail="pyq_id required")
    
    # Get PYQ questions
    from .database import DatabaseRepo
    pyq = DatabaseRepo.get_pyq_papers(college="", subject="")
    # Find the specific PYQ
    pyq_data = DatabaseRepo.get_pyq_papers()
    # ... implementation
    pass


@router.post("/save-generated")
async def save_generated_questions(
    data: Dict[str, Any] = Body(...)
):
    """Save approved generated questions to database"""
    questions = data.get("questions", [])
    subject = data.get("subject")
    topic = data.get("topic")
    
    if not questions or not subject or not topic:
        raise HTTPException(status_code=400, detail="questions, subject, topic required")
    
    saved_ids = qgen.save_generated_questions(questions, subject, topic)
    
    return {"success": True, "saved_ids": saved_ids, "count": len(saved_ids)}


@router.post("/check-similarity")
async def check_question_similarity(
    data: Dict[str, Any] = Body(...)
):
    """Check a question against existing database for similarity"""
    question_text = data.get("question_text")
    subject = data.get("subject")
    topic = data.get("topic")
    
    if not question_text or not subject or not topic:
        raise HTTPException(status_code=400, detail="question_text, subject, topic required")
    
    existing = qgen._get_existing_questions(subject, topic)
    max_sim, is_dup = qgen._check_similarity(question_text, existing)
    
    return {
        "max_similarity": round(max_sim, 3),
        "is_duplicate": is_dup,
        "threshold": qgen.SIMILARITY_THRESHOLD,
        "existing_count": len(existing)
    }


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


@router.post("/regenerate-rejected")
async def regenerate_rejected(
    data: Dict[str, Any] = Body(...)
):
    """Regenerate questions that were rejected due to similarity"""
    source_id = data.get("source_question_id")
    rejected_count = data.get("rejected_count", 0)
    
    if not source_id:
        raise HTTPException(status_code=400, detail="source_question_id required")
    
    # Retry generation with higher variation
    result = qgen.generate_similar_questions(
        source_question_id=source_id,
        count=rejected_count,
        variation_level=0.85  # higher variation for retries
    )
    
    return result