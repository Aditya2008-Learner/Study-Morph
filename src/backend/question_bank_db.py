"""
Question Bank Database Schema
Extends existing database with intelligent question bank tables
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Add to existing database.py

QUESTION_BANK_TABLES = """
-- Main questions table - stores ALL questions (PYQ, Assignment, Generated, Notebook)
CREATE TABLE IF NOT EXISTS question_bank (
    id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    subtopic TEXT DEFAULT '',
    source_type TEXT NOT NULL,  -- 'PYQ' | 'Assignment' | 'Notebook' | 'AI_Generated'
    source_id TEXT,              -- original assignment/pyq/notebook ID
    source_question_id TEXT,     -- parent question ID if generated
    difficulty TEXT DEFAULT 'Medium',  -- 'Easy' | 'Medium' | 'Hard' | 'Advanced'
    question_type TEXT DEFAULT 'Exam',  -- 'Conceptual' | 'Short' | 'Long' | 'Numerical' | 'Application' | 'Scenario' | 'Comparison' | 'Analytical' | 'Viva' | 'Exam'
    marks INTEGER DEFAULT 5,
    year INTEGER,
    college TEXT,
    set_num INTEGER DEFAULT 1,
    related_concepts TEXT DEFAULT '[]',  -- JSON array
    similarity_score REAL DEFAULT 0.0,   -- against parent if generated
    generation_params TEXT DEFAULT '{}', -- JSON: difficulty, type, marks, variation_level
    status TEXT DEFAULT 'Approved',      -- 'Pending' | 'Approved' | 'Rejected' | 'Review'
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Topic tracking - target 15-20 questions per topic
CREATE TABLE IF NOT EXISTS topic_question_tracker (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    subtopic TEXT DEFAULT '',
    target_count INTEGER DEFAULT 20,
    current_count INTEGER DEFAULT 0,
    easy_count INTEGER DEFAULT 0,
    medium_count INTEGER DEFAULT 0,
    hard_count INTEGER DEFAULT 0,
    advanced_count INTEGER DEFAULT 0,
    last_generated_at TEXT,
    generation_attempts INTEGER DEFAULT 0,
    UNIQUE(subject, topic, subtopic)
);

-- Semantic similarity index using C-core fast_fuzzy_similarity
CREATE TABLE IF NOT EXISTS question_similarity_index (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    signature TEXT NOT NULL,  -- semantic fingerprint
    embedding_json TEXT,      -- optional vector embedding
    created_at TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES question_bank(id) ON DELETE CASCADE
);

-- Generation requests log
CREATE TABLE IF NOT EXISTS generation_log (
    id TEXT PRIMARY KEY,
    request_type TEXT NOT NULL,  -- 'Similar' | 'Topic_Batch' | 'PYQ_Similar'
    source_question_id TEXT,
    subject TEXT,
    topic TEXT,
    requested_count INTEGER,
    generated_count INTEGER,
    accepted_count INTEGER,
    rejected_count INTEGER,
    params TEXT DEFAULT '{}',  -- JSON
    status TEXT DEFAULT 'Completed',  -- 'Pending' | 'Completed' | 'Failed'
    created_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_qb_subject_topic ON question_bank(subject, topic, subtopic);
CREATE INDEX IF NOT EXISTS idx_qb_subject_set ON question_bank(subject, set_num);
CREATE INDEX IF NOT EXISTS idx_qb_source_type ON question_bank(source_type);
CREATE INDEX IF NOT EXISTS idx_qb_difficulty ON question_bank(difficulty);
CREATE INDEX IF NOT EXISTS idx_qb_status ON question_bank(status);
CREATE INDEX IF NOT EXISTS idx_qb_source_id ON question_bank(source_id);
CREATE INDEX IF NOT EXISTS idx_qb_parent ON question_bank(source_question_id);
CREATE INDEX IF NOT EXISTS idx_tracker_subject_topic ON topic_question_tracker(subject, topic);
CREATE INDEX IF NOT EXISTS idx_sim_index_sig ON question_similarity_index(signature);
CREATE INDEX IF NOT EXISTS idx_gen_log_type ON generation_log(request_type);
"""


def get_question_bank_schema():
    """Return the question bank schema SQL"""
    return QUESTION_BANK_TABLES


def init_question_bank(db_path: str = None):
    """Initialize question bank tables in existing database"""
    if db_path is None:
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "study_assistant.db")
    
    conn = sqlite3.connect(db_path, timeout=20.0)
    conn.row_factory = sqlite3.Row

    # Run table creation (without indexes that depend on columns that might be missing in old schema)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_bank (
        id TEXT PRIMARY KEY,
        question_text TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        subtopic TEXT DEFAULT '',
        source_type TEXT NOT NULL,
        source_id TEXT,
        source_question_id TEXT,
        difficulty TEXT DEFAULT 'Medium',
        question_type TEXT DEFAULT 'Exam',
        marks INTEGER DEFAULT 5,
        year INTEGER,
        college TEXT,
        set_num INTEGER DEFAULT 1,
        related_concepts TEXT DEFAULT '[]',
        similarity_score REAL DEFAULT 0.0,
        generation_params TEXT DEFAULT '{}',
        status TEXT DEFAULT 'Approved',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Migration: add set_num if table previously existed without it
    try:
        cursor.execute("PRAGMA table_info(question_bank);")
        cols = [r[1] for r in cursor.fetchall()]
        if "set_num" not in cols:
            cursor.execute("ALTER TABLE question_bank ADD COLUMN set_num INTEGER DEFAULT 1;")
    except Exception:
        pass

    conn.executescript(QUESTION_BANK_TABLES)
    conn.commit()
    conn.close()
    print("Question bank tables initialized")


if __name__ == "__main__":
    init_question_bank()