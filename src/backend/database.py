import os
import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "study_assistant.db")

def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        college TEXT NOT NULL,
        department TEXT DEFAULT '',
        subject TEXT NOT NULL,
        course_code TEXT DEFAULT '',
        semester TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        topic_tags TEXT DEFAULT '[]',
        difficulty TEXT DEFAULT 'Intermediate',
        due_date TEXT DEFAULT '',
        status TEXT DEFAULT 'Pending',
        content_text TEXT DEFAULT '',
        questions TEXT DEFAULT '[]',
        attachments TEXT DEFAULT '[]',
        is_pyq INTEGER DEFAULT 0,
        source_url TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pyq_papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        college TEXT NOT NULL,
        department TEXT DEFAULT '',
        subject TEXT NOT NULL,
        semester TEXT NOT NULL,
        academic_year TEXT NOT NULL,
        exam_type TEXT DEFAULT 'End-Sem',
        file_path TEXT DEFAULT '',
        source_url TEXT DEFAULT '',
        content_text TEXT DEFAULT '',
        parsed_questions TEXT DEFAULT '[]',
        downloaded_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notebooks (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        college TEXT DEFAULT '',
        subject TEXT DEFAULT '',
        semester TEXT DEFAULT '',
        raw_text TEXT DEFAULT '',
        extracted_topics TEXT DEFAULT '[]',
        summary TEXT DEFAULT '',
        formulas TEXT DEFAULT '[]',
        key_points TEXT DEFAULT '[]',
        status TEXT DEFAULT 'Processed',
        uploaded_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_assignments (
        id TEXT PRIMARY KEY,
        notebook_id TEXT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        semester TEXT NOT NULL,
        difficulty TEXT DEFAULT 'Intermediate',
        target_exam TEXT DEFAULT 'University Exam',
        questions TEXT DEFAULT '[]',
        rubric TEXT DEFAULT '[]',
        total_marks INTEGER DEFAULT 100,
        time_limit_mins INTEGER DEFAULT 180,
        created_at TEXT NOT NULL,
        FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE SET NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignment_submissions (
        id TEXT PRIMARY KEY,
        assignment_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        student_answer TEXT NOT NULL,
        marks_awarded REAL DEFAULT 0,
        total_marks REAL DEFAULT 10,
        accuracy_score REAL DEFAULT 0,
        completeness_score REAL DEFAULT 0,
        feedback_text TEXT DEFAULT '',
        rubric_breakdown TEXT DEFAULT '{}',
        missing_points TEXT DEFAULT '[]',
        model_answer TEXT DEFAULT '',
        evaluated_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_notes (
        id TEXT PRIMARY KEY,
        notebook_id TEXT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        summary TEXT DEFAULT '',
        flashcards TEXT DEFAULT '[]',
        formulas TEXT DEFAULT '[]',
        mnemonics TEXT DEFAULT '[]',
        key_takeaways TEXT DEFAULT '[]',
        created_at TEXT NOT NULL,
        FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE SET NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id TEXT PRIMARY KEY,
        notebook_id TEXT,
        assignment_id TEXT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        title TEXT NOT NULL,
        questions TEXT DEFAULT '[]',
        total_questions INTEGER DEFAULT 5,
        created_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id TEXT PRIMARY KEY,
        quiz_id TEXT NOT NULL,
        score REAL NOT NULL,
        max_score REAL NOT NULL,
        percentage REAL NOT NULL,
        time_taken_seconds INTEGER DEFAULT 0,
        answers TEXT DEFAULT '[]',
        weak_topics TEXT DEFAULT '[]',
        mastered_topics TEXT DEFAULT '[]',
        recommendations TEXT DEFAULT '[]',
        completed_at TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        citations TEXT DEFAULT '[]',
        created_at TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS curriculum (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        semester TEXT NOT NULL,
        credits INTEGER DEFAULT 3,
        category TEXT DEFAULT '',
        course_type TEXT DEFAULT 'Core',
        modules TEXT DEFAULT '[]',
        outcomes TEXT DEFAULT '[]',
        key_textbooks TEXT DEFAULT '[]',
        assignments TEXT DEFAULT '[]',
        UNIQUE(code, semester)
    );
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_col_sub ON assignments(college, subject, semester, academic_year);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_is_pyq ON assignments(is_pyq);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pyq_papers_col_sub ON pyq_papers(college, subject, semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notebooks_sub ON notebooks(subject, semester);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id, created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_curriculum_sem ON curriculum(semester);")
    
    # NEW: Topic content table for study material
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_content (
        id TEXT PRIMARY KEY,
        course_code TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        summary TEXT DEFAULT '',
        key_points TEXT DEFAULT '[]',
        formulas TEXT DEFAULT '[]',
        examples TEXT DEFAULT '[]',
        mcqs TEXT DEFAULT '[]',
        practice_questions TEXT DEFAULT '[]',
        flashcards TEXT DEFAULT '[]',
        viva_questions TEXT DEFAULT '[]',
        difficulty TEXT DEFAULT 'Intermediate',
        created_at TEXT NOT NULL
    ); """)
    
    # NEW: Student activity tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_activity (
        id TEXT PRIMARY KEY,
        activity_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        details TEXT DEFAULT '{}',
        duration_seconds INTEGER DEFAULT 0,
        score REAL DEFAULT 0,
        completed_at TEXT NOT NULL
    ); """)
    
    # NEW: Learning progress
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_progress (
        id TEXT PRIMARY KEY,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        status TEXT DEFAULT 'Not Started',
        progress_percentage INTEGER DEFAULT 0,
        notes TEXT DEFAULT '[]',
        quiz_scores TEXT DEFAULT '[]',
        last_accessed TEXT NOT NULL
    ); """)
    
    # NEW: Generated assignments from curriculum topics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topic_assignments (
        id TEXT PRIMARY KEY,
        course_code TEXT NOT NULL,
        topic_name TEXT NOT NULL,
        questions TEXT DEFAULT '[]',
        total_marks INTEGER DEFAULT 50,
        difficulty TEXT DEFAULT 'Intermediate',
        generated_at TEXT NOT NULL
    ); """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic_content ON topic_content(course_code, topic_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_activity ON student_activity(activity_type, subject, topic);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_progress ON learning_progress(subject, topic);")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactive_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT NOT NULL,
        topic TEXT NOT NULL,
        content TEXT,
        front_text TEXT DEFAULT '',
        back_text TEXT DEFAULT ''
    );
    """)
    try:
        cursor.execute("PRAGMA table_info(interactive_content);")
        existing_cols = [row[1] for row in cursor.fetchall()]
        if "front_text" not in existing_cols:
            cursor.execute("ALTER TABLE interactive_content ADD COLUMN front_text TEXT DEFAULT '';")
        if "back_text" not in existing_cols:
            cursor.execute("ALTER TABLE interactive_content ADD COLUMN back_text TEXT DEFAULT '';")
    except Exception:
        pass
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactive_course ON interactive_content(course_code);")

    conn.commit()
    conn.close()

class DatabaseRepo:
    @staticmethod
    def get_assignments(
        college: Optional[str] = None,
        subject: Optional[str] = None,
        semester: Optional[str] = None,
        academic_year: Optional[str] = None,
        status: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_pyq: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM assignments WHERE 1=1"
        params = []
        if college:
            query += " AND LOWER(college) LIKE LOWER(?)"
            params.append(f"%{college}%")
        if subject:
            query += " AND LOWER(subject) LIKE LOWER(?)"
            params.append(f"%{subject}%")
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        if academic_year:
            query += " AND academic_year = ?"
            params.append(academic_year)
        if status:
            query += " AND LOWER(status) = LOWER(?)"
            params.append(status)
        if difficulty:
            query += " AND LOWER(difficulty) = LOWER(?)"
            params.append(difficulty)
        if is_pyq is not None:
            query += " AND is_pyq = ?"
            params.append(is_pyq)
        if search:
            query += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(content_text) LIKE LOWER(?) OR LOWER(topic_tags) LIKE LOWER(?))"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        allowed = {"created_at": "created_at", "due_date": "due_date", "title": "title", "subject": "subject", "difficulty": "difficulty", "academic_year": "academic_year"}
        sort_col = allowed.get(sort_by, "created_at")
        order = "ASC" if sort_order.upper() == "ASC" else "DESC"
        query += f" ORDER BY {sort_col} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["topic_tags"] = json.loads(d["topic_tags"]) if d["topic_tags"] else []
            d["questions"] = json.loads(d["questions"]) if d["questions"] else []
            d["attachments"] = json.loads(d["attachments"]) if d["attachments"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_assignment_by_id(assignment_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: return None
        d = dict(row)
        d["topic_tags"] = json.loads(d["topic_tags"]) if d["topic_tags"] else []
        d["questions"] = json.loads(d["questions"]) if d["questions"] else []
        d["attachments"] = json.loads(d["attachments"]) if d["attachments"] else []
        return d

    @staticmethod
    def create_assignment(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        assignment_id = data.get("id") or str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO assignments (
            id, title, college, department, subject, course_code, semester, academic_year,
            topic_tags, difficulty, due_date, status, content_text, questions, attachments,
            is_pyq, source_url, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assignment_id,
            data.get("title", "Untitled Assignment"),
            data.get("college", "University"),
            data.get("department", ""),
            data.get("subject", "General"),
            data.get("course_code", ""),
            str(data.get("semester", "1")),
            str(data.get("academic_year", datetime.now().year)),
            json.dumps(data.get("topic_tags", [])),
            data.get("difficulty", "Intermediate"),
            data.get("due_date", ""),
            data.get("status", "Pending"),
            data.get("content_text", ""),
            json.dumps(data.get("questions", [])),
            json.dumps(data.get("attachments", [])),
            int(data.get("is_pyq", 0)),
            data.get("source_url", ""),
            data.get("created_at", now),
            now
        ))
        conn.commit()
        conn.close()
        return DatabaseRepo.get_assignment_by_id(assignment_id)

    @staticmethod
    def update_assignment(assignment_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        fields = []
        params = []
        for k, v in updates.items():
            if k in ["topic_tags", "questions", "attachments"]:
                fields.append(f"{k} = ?")
                params.append(json.dumps(v))
            elif k in ["title", "college", "department", "subject", "course_code", "semester", "academic_year", "difficulty", "due_date", "status", "content_text", "is_pyq", "source_url"]:
                fields.append(f"{k} = ?")
                params.append(v)
        if not fields:
            conn.close()
            return DatabaseRepo.get_assignment_by_id(assignment_id)
        fields.append("updated_at = ?")
        params.append(now)
        params.append(assignment_id)
        cursor.execute(f"UPDATE assignments SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        return DatabaseRepo.get_assignment_by_id(assignment_id)

    @staticmethod
    def delete_assignment(assignment_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
        affected = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return affected

    @staticmethod
    def get_pyq_papers(
        college: Optional[str] = None,
        subject: Optional[str] = None,
        semester: Optional[str] = None,
        academic_year: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM pyq_papers WHERE 1=1"
        params = []
        if college:
            query += " AND LOWER(college) LIKE LOWER(?)"
            params.append(f"%{college}%")
        if subject:
            query += " AND LOWER(subject) LIKE LOWER(?)"
            params.append(f"%{subject}%")
        if semester:
            query += " AND semester = ?"
            params.append(semester)
        if academic_year:
            query += " AND academic_year = ?"
            params.append(academic_year)
        if search:
            query += " AND (LOWER(title) LIKE LOWER(?) OR LOWER(content_text) LIKE LOWER(?))"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY downloaded_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["parsed_questions"] = json.loads(d["parsed_questions"]) if d["parsed_questions"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def create_pyq_paper(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        paper_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO pyq_papers (
            id, title, college, department, subject, semester, academic_year,
            exam_type, file_path, source_url, content_text, parsed_questions, downloaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            data.get("title", "Untitled PYQ"),
            data.get("college", "University"),
            data.get("department", ""),
            data.get("subject", "General"),
            str(data.get("semester", "1")),
            str(data.get("academic_year", datetime.now().year)),
            data.get("exam_type", "End-Sem"),
            data.get("file_path", ""),
            data.get("source_url", ""),
            data.get("content_text", ""),
            json.dumps(data.get("parsed_questions", [])),
            data.get("downloaded_at", now)
        ))
        conn.commit()
        conn.close()
        return data

    @staticmethod
    def create_notebook(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        notebook_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO notebooks (
            id, filename, original_name, file_type, file_size, college, subject, semester,
            raw_text, extracted_topics, summary, formulas, key_points, status, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            notebook_id,
            data.get("filename", ""),
            data.get("original_name", "document"),
            data.get("file_type", "unknown"),
            int(data.get("file_size", 0)),
            data.get("college", ""),
            data.get("subject", ""),
            str(data.get("semester", "")),
            data.get("raw_text", ""),
            json.dumps(data.get("extracted_topics", [])),
            data.get("summary", ""),
            json.dumps(data.get("formulas", [])),
            json.dumps(data.get("key_points", [])),
            data.get("status", "Processed"),
            data.get("uploaded_at", now)
        ))
        conn.commit()
        conn.close()
        return DatabaseRepo.get_notebook_by_id(notebook_id)

    @staticmethod
    def get_notebooks() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notebooks ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["extracted_topics"] = json.loads(d["extracted_topics"]) if d["extracted_topics"] else []
            d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
            d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_notebook_by_id(notebook_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notebooks WHERE id = ?", (notebook_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: return None
        d = dict(row)
        d["extracted_topics"] = json.loads(d["extracted_topics"]) if d["extracted_topics"] else []
        d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
        d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
        return d

    @staticmethod
    def get_distinct_metadata() -> Dict[str, List[str]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT college FROM assignments WHERE college IS NOT NULL AND college != '' UNION SELECT DISTINCT college FROM pyq_papers WHERE college != ''")
        colleges = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT subject FROM assignments WHERE subject IS NOT NULL AND subject != '' UNION SELECT DISTINCT subject FROM pyq_papers WHERE subject != '' UNION SELECT DISTINCT subject FROM notebooks WHERE subject != ''")
        subjects = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT semester FROM assignments WHERE semester IS NOT NULL AND semester != '' UNION SELECT DISTINCT semester FROM pyq_papers WHERE semester != '' UNION SELECT DISTINCT semester FROM curriculum WHERE semester IS NOT NULL AND semester != ''")
        semesters = sorted(list(set([str(r[0]) for r in cursor.fetchall()])), key=lambda x: int(x))
        cursor.execute("SELECT DISTINCT academic_year FROM assignments WHERE academic_year IS NOT NULL AND academic_year != '' UNION SELECT DISTINCT academic_year FROM pyq_papers WHERE academic_year != ''")
        years = sorted(list(set([str(r[0]) for r in cursor.fetchall()])), reverse=True)
        conn.close()
        return {"colleges": colleges, "subjects": subjects, "semesters": semesters, "academic_years": years}

    @staticmethod
    def seed_curriculum(courses: List[Dict[str, Any]]):
        conn = get_connection()
        cursor = conn.cursor()
        for c in courses:
            cursor.execute("""
            INSERT OR REPLACE INTO curriculum (
                code, name, semester, credits, category, course_type,
                modules, outcomes, key_textbooks, assignments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["code"], c["name"], str(c.get("semester", c.get("semester_number", 1))),
                int(c.get("credits", 3)), c.get("category", "Professional Core"), c.get("type", "Core"),
                json.dumps(c.get("modules", [])), json.dumps(c.get("outcomes", [])),
                json.dumps(c.get("key_textbooks", [])), json.dumps(c.get("assignments", []))
            ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_curriculum() -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM curriculum ORDER BY semester, code")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["modules"] = json.loads(d["modules"]) if d["modules"] else []
            d["outcomes"] = json.loads(d["outcomes"]) if d["outcomes"] else []
            d["key_textbooks"] = json.loads(d["key_textbooks"]) if d["key_textbooks"] else []
            d["assignments"] = json.loads(d["assignments"]) if d["assignments"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_curriculum_by_semester(semester: int) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM curriculum WHERE semester = ? ORDER BY code", (str(semester),))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["modules"] = json.loads(d["modules"]) if d["modules"] else []
            d["outcomes"] = json.loads(d["outcomes"]) if d["outcomes"] else []
            d["key_textbooks"] = json.loads(d["key_textbooks"]) if d["key_textbooks"] else []
            d["assignments"] = json.loads(d["assignments"]) if d["assignments"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_curriculum_by_code(code: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM curriculum WHERE UPPER(code) = UPPER(?)", (code,))
        row = cursor.fetchone()
        conn.close()
        if not row: return None
        d = dict(row)
        d["modules"] = json.loads(d["modules"]) if d["modules"] else []
        d["outcomes"] = json.loads(d["outcomes"]) if d["outcomes"] else []
        d["key_textbooks"] = json.loads(d["key_textbooks"]) if d["key_textbooks"] else []
        d["assignments"] = json.loads(d["assignments"]) if d["assignments"] else []
        return d

    @staticmethod
    def create_generated_assignment(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        gen_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO generated_assignments (
            id, notebook_id, title, subject, semester, difficulty, target_exam,
            questions, rubric, total_marks, time_limit_mins, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gen_id,
            data.get("notebook_id"),
            data.get("title", "Generated Assignment"),
            data.get("subject", "General"),
            str(data.get("semester", "1")),
            data.get("difficulty", "Intermediate"),
            data.get("target_exam", "University Exam"),
            json.dumps(data.get("questions", [])),
            json.dumps(data.get("rubric", [])),
            int(data.get("total_marks", 100)),
            int(data.get("time_limit_mins", 180)),
            now
        ))
        conn.commit()
        conn.close()
        data["id"] = gen_id
        data["created_at"] = now
        return data

    @staticmethod
    def get_generated_assignments(notebook_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        if notebook_id:
            cursor.execute("SELECT * FROM generated_assignments WHERE notebook_id = ? ORDER BY created_at DESC", (notebook_id,))
        else:
            cursor.execute("SELECT * FROM generated_assignments ORDER BY created_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["questions"] = json.loads(d["questions"]) if d["questions"] else []
            d["rubric"] = json.loads(d["rubric"]) if d["rubric"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_generated_assignment_by_id(gen_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM generated_assignments WHERE id = ?", (gen_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: return None
        d = dict(row)
        d["questions"] = json.loads(d["questions"]) if d["questions"] else []
        d["rubric"] = json.loads(d["rubric"]) if d["rubric"] else []
        return d

    @staticmethod
    def record_submission(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        sub_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO assignment_submissions (
            id, assignment_id, question_id, student_answer, marks_awarded, total_marks,
            accuracy_score, completeness_score, feedback_text, rubric_breakdown,
            missing_points, model_answer, evaluated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sub_id,
            data.get("assignment_id", ""),
            data.get("question_id", ""),
            data.get("student_answer", ""),
            float(data.get("marks_awarded", 0)),
            float(data.get("total_marks", 10)),
            float(data.get("accuracy_score", 0)),
            float(data.get("completeness_score", 0)),
            data.get("feedback_text", ""),
            json.dumps(data.get("rubric_breakdown", {})),
            json.dumps(data.get("missing_points", [])),
            data.get("model_answer", ""),
            now
        ))
        conn.commit()
        conn.close()
        data["id"] = sub_id
        data["evaluated_at"] = now
        return data

    @staticmethod
    def get_submissions_for_assignment(assignment_id: str) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignment_submissions WHERE assignment_id = ? ORDER BY evaluated_at DESC", (assignment_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["rubric_breakdown"] = json.loads(d["rubric_breakdown"]) if d["rubric_breakdown"] else {}
            d["missing_points"] = json.loads(d["missing_points"]) if d["missing_points"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def create_study_note(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        note_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO study_notes (
            id, notebook_id, subject, topic, summary, flashcards,
            formulas, mnemonics, key_takeaways, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            note_id,
            data.get("notebook_id"),
            data.get("subject", "General"),
            data.get("topic", "General Topic"),
            data.get("summary", ""),
            json.dumps(data.get("flashcards", [])),
            json.dumps(data.get("formulas", [])),
            json.dumps(data.get("mnemonics", [])),
            json.dumps(data.get("key_takeaways", [])),
            now
        ))
        conn.commit()
        conn.close()
        data["id"] = note_id
        data["created_at"] = now
        return data

    @staticmethod
    def get_study_notes(notebook_id: Optional[str] = None, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM study_notes WHERE 1=1"
        params = []
        if notebook_id:
            query += " AND notebook_id = ?"
            params.append(notebook_id)
        if subject:
            query += " AND LOWER(subject) LIKE LOWER(?)"
            params.append(f"%{subject}%")
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["flashcards"] = json.loads(d["flashcards"]) if d["flashcards"] else []
            d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
            d["mnemonics"] = json.loads(d["mnemonics"]) if d["mnemonics"] else []
            d["key_takeaways"] = json.loads(d["key_takeaways"]) if d["key_takeaways"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def create_quiz(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        quiz_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO quizzes (
            id, notebook_id, assignment_id, subject, topic, title,
            questions, total_questions, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz_id,
            data.get("notebook_id"),
            data.get("assignment_id"),
            data.get("subject", "General"),
            data.get("topic", "General Topic"),
            data.get("title", "Interactive AI Quiz"),
            json.dumps(data.get("questions", [])),
            int(len(data.get("questions", []))),
            now
        ))
        conn.commit()
        conn.close()
        data["id"] = quiz_id
        data["created_at"] = now
        return data

    @staticmethod
    def get_quizzes(subject: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM quizzes WHERE 1=1"
        params = []
        if subject:
            query += " AND LOWER(subject) LIKE LOWER(?)"
            params.append(f"%{subject}%")
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["questions"] = json.loads(d["questions"]) if d["questions"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_quiz_by_id(quiz_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        row = cursor.fetchone()
        conn.close()
        if not row: return None
        d = dict(row)
        d["questions"] = json.loads(d["questions"]) if d["questions"] else []
        return d

    @staticmethod
    def record_quiz_attempt(data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        att_id = data.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO quiz_attempts (
            id, quiz_id, score, max_score, percentage, time_taken_seconds,
            answers, weak_topics, mastered_topics, recommendations, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            att_id,
            data.get("quiz_id", ""),
            float(data.get("score", 0)),
            float(data.get("max_score", 0)),
            float(data.get("percentage", 0)),
            int(data.get("time_taken_seconds", 0)),
            json.dumps(data.get("answers", [])),
            json.dumps(data.get("weak_topics", [])),
            json.dumps(data.get("mastered_topics", [])),
            json.dumps(data.get("recommendations", [])),
            now
        ))
        conn.commit()
        conn.close()
        data["id"] = att_id
        data["completed_at"] = now
        return data

    @staticmethod
    def get_weakness_radar() -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT weak_topics, mastered_topics, percentage FROM quiz_attempts ORDER BY completed_at DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        topic_stats = {}
        for r in rows:
            weak = json.loads(r["weak_topics"]) if r["weak_topics"] else []
            mastered = json.loads(r["mastered_topics"]) if r["mastered_topics"] else []
            for t in weak:
                if t not in topic_stats: topic_stats[t] = {"weak": 0, "mastered": 0}
                topic_stats[t]["weak"] += 1
            for t in mastered:
                if t not in topic_stats: topic_stats[t] = {"weak": 0, "mastered": 0}
                topic_stats[t]["mastered"] += 1
        topics_summary = []
        for t, stats in topic_stats.items():
            total = stats["weak"] + stats["mastered"]
            mastery = round((stats["mastered"] / total) * 100, 1) if total > 0 else 0
            topics_summary.append({"topic": t, "mastery_percentage": mastery, "is_weak": mastery < 65, "attempts": total})
        topics_summary.sort(key=lambda x: x["mastery_percentage"])
        return {"total_attempts": len(rows), "topic_analytics": topics_summary}

    @staticmethod
    def add_chat_message(session_id: str, role: str, message: str, citations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        citations = citations or []
        cursor.execute("""
        INSERT INTO chat_history (id, session_id, role, message, citations, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, message, json.dumps(citations), now))
        conn.commit()
        conn.close()
        return {"id": msg_id, "session_id": session_id, "role": role, "message": message, "citations": citations, "created_at": now}

    @staticmethod
    def get_chat_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_history WHERE session_id = ? ORDER BY created_at ASC LIMIT ?", (session_id, limit))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["citations"] = json.loads(d["citations"]) if d["citations"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def delete_notebook(notebook_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))
        affected = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return affected

    # ===== NEW: Curriculum & Topic Content Methods =====
    
    @staticmethod
    def get_full_curriculum() -> List[Dict[str, Any]]:
        """Get all curriculum across 8 semesters with full course details"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM curriculum ORDER BY semester, code")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["modules"] = json.loads(d["modules"]) if d["modules"] else []
            d["outcomes"] = json.loads(d["outcomes"]) if d["outcomes"] else []
            d["key_textbooks"] = json.loads(d["key_textbooks"]) if d["key_textbooks"] else []
            d["assignments"] = json.loads(d["assignments"]) if d["assignments"] else []
            result.append(d)
        conn.close()
        return result
    
    @staticmethod
    def get_curriculum_by_year(year: int) -> List[Dict[str, Any]]:
        """Get curriculum for a specific year (1-4)"""
        year_sem_map = {1: [1, 2], 2: [3, 4], 3: [5, 6], 4: [7, 8]}
        semesters = year_sem_map.get(year, [1, 2])
        conn = get_connection()
        cursor = conn.cursor()
        placeholders = ','.join(['?'] * len(semesters))
        cursor.execute(f"SELECT * FROM curriculum WHERE semester IN ({placeholders}) ORDER BY semester, code", semesters)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["modules"] = json.loads(d["modules"]) if d["modules"] else []
            d["outcomes"] = json.loads(d["outcomes"]) if d["outcomes"] else []
            result.append(d)
        conn.close()
        return result
    
    @staticmethod
    def get_topic_content(course_code: str, topic_name: str = None) -> List[Dict[str, Any]]:
        """Get study content for a specific topic or all topics for a course"""
        conn = get_connection()
        cursor = conn.cursor()
        if topic_name:
            cursor.execute("SELECT * FROM topic_content WHERE course_code = ? AND topic_name = ?", 
                          (course_code, topic_name))
        else:
            cursor.execute("SELECT * FROM topic_content WHERE course_code = ?", (course_code,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
            d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
            d["examples"] = json.loads(d["examples"]) if d["examples"] else []
            d["mcqs"] = json.loads(d["mcqs"]) if d["mcqs"] else []
            d["practice_questions"] = json.loads(d["practice_questions"]) if d["practice_questions"] else []
            d["flashcards"] = json.loads(d["flashcards"]) if d["flashcards"] else []
            d["viva_questions"] = json.loads(d["viva_questions"]) if d["viva_questions"] else []
            result.append(d)
        conn.close()
        return result
    
    @staticmethod
    def get_all_topics() -> List[Dict[str, Any]]:
        """Get all topics across all courses"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topic_content ORDER BY course_code, topic_name")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
            d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
            d["mcqs"] = json.loads(d["mcqs"]) if d["mcqs"] else []
            d["flashcards"] = json.loads(d["flashcards"]) if d["flashcards"] else []
            result.append(d)
        conn.close()
        return result
    
    @staticmethod
    def get_topic_by_keyword(keyword: str) -> List[Dict[str, Any]]:
        """Search topics by keyword"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topic_content WHERE topic_name LIKE ? OR summary LIKE ?", 
                      (f'%{keyword}%', f'%{keyword}%'))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["key_points"] = json.loads(d["key_points"]) if d["key_points"] else []
            d["formulas"] = json.loads(d["formulas"]) if d["formulas"] else []
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def get_interactive_content(course_code: str) -> List[Dict[str, Any]]:
        """Get interactive flashcards for a course from interactive_content or fallback to topic_content"""
        conn = get_connection()
        cursor = conn.cursor()
        cards = []
        try:
            cursor.execute("SELECT * FROM interactive_content WHERE course_code = ? ORDER BY topic, id", (course_code,))
            rows = cursor.fetchall()
            for r in rows:
                d = dict(r)
                front = d.get("front_text") or d.get("topic") or ""
                back = d.get("back_text") or d.get("content") or ""
                cards.append({
                    "id": d.get("id"),
                    "course_code": d.get("course_code"),
                    "topic": d.get("topic"),
                    "front_text": front,
                    "back_text": back,
                    "content": back
                })
        except Exception:
            pass

        if not cards:
            try:
                topic_rows = DatabaseRepo.get_topic_content(course_code)
                for tr in topic_rows:
                    tname = tr.get("topic_name", "")
                    fcs = tr.get("flashcards", [])
                    if fcs and isinstance(fcs, list):
                        for fc in fcs:
                            if isinstance(fc, dict):
                                cards.append({
                                    "course_code": course_code,
                                    "topic": tname,
                                    "front_text": fc.get("front", tname),
                                    "back_text": fc.get("back", ""),
                                    "content": fc.get("back", "")
                                })
                    elif tr.get("summary"):
                        cards.append({
                            "course_code": course_code,
                            "topic": tname,
                            "front_text": tname,
                            "back_text": tr.get("summary", ""),
                            "content": tr.get("summary", "")
                        })
            except Exception:
                pass

        if not cards:
            try:
                course = DatabaseRepo.get_curriculum_by_code(course_code)
                if course:
                    cname = course.get("name", course_code)
                    for mod in course.get("modules", []):
                        mtitle = mod.get("name", "Core Module")
                        subtopics = mod.get("subtopics", [])
                        pts = mod.get("important_points", [])
                        summary = f"Key topics: {', '.join(subtopics[:4])}. Points: {'; '.join(pts[:3])}" if pts or subtopics else f"Curriculum module for {cname}"
                        cards.append({
                            "course_code": course_code,
                            "topic": mtitle,
                            "front_text": f"{course_code}: {mtitle}",
                            "back_text": summary,
                            "content": summary
                        })
            except Exception:
                pass

        conn.close()
        return cards
    
    # ===== Activity & Progress Tracking =====
    
    @staticmethod
    def log_student_activity(activity_type: str, subject: str, topic: str, 
                            details: Dict = None, duration: int = 0, score: float = 0) -> Dict[str, Any]:
        """Log student activity for tracking"""
        conn = get_connection()
        cursor = conn.cursor()
        act_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        details = details or {}
        cursor.execute("""
        INSERT INTO student_activity (id, activity_type, subject, topic, details, duration_seconds, score, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (act_id, activity_type, subject, topic, json.dumps(details), duration, score, now))
        conn.commit()
        conn.close()
        return {"id": act_id, "activity_type": activity_type, "subject": subject, "topic": topic}
    
    @staticmethod
    def get_learning_progress() -> List[Dict[str, Any]]:
        """Get overall learning progress across all topics"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_progress ORDER BY last_accessed DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["notes"] = json.loads(d["notes"]) if d["notes"] else []
            d["quiz_scores"] = json.loads(d["quiz_scores"]) if d["quiz_scores"] else []
            result.append(d)
        conn.close()
        return result
    
    @staticmethod
    def update_topic_progress(subject: str, topic: str, status: str = None, 
                              progress_pct: int = None, quiz_score: float = None) -> Dict[str, Any]:
        """Update learning progress for a specific topic"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("SELECT * FROM learning_progress WHERE subject = ? AND topic = ?", (subject, topic))
        existing = cursor.fetchone()
        
        if existing:
            updates = ["last_accessed = ?"]
            params = [now]
            if status:
                updates.append("status = ?")
                params.append(status)
            if progress_pct is not None:
                updates.append("progress_percentage = ?")
                params.append(progress_pct)
            if quiz_score is not None:
                scores = json.loads(existing["quiz_scores"]) if existing["quiz_scores"] else []
                scores.append(quiz_score)
                updates.append("quiz_scores = ?")
                params.append(json.dumps(scores))
            params.extend([subject, topic])
            cursor.execute(f"UPDATE learning_progress SET {', '.join(updates)} WHERE subject = ? AND topic = ?", params)
        else:
            progress_id = str(uuid.uuid4())
            scores = [quiz_score] if quiz_score else []
            cursor.execute("""
            INSERT INTO learning_progress (id, subject, topic, status, progress_percentage, quiz_scores, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (progress_id, subject, topic, status or "In Progress", progress_pct or 0, json.dumps(scores), now))
        
        conn.commit()
        conn.close()
        return {"subject": subject, "topic": topic, "status": status or "Updated"}
    
    @staticmethod
    def get_recommendations() -> Dict[str, Any]:
        """Get smart study recommendations based on activity"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get weak topics from quiz attempts — guard against empty table / division issues
        try:
            cursor.execute("""
                SELECT topic, COUNT(*) as attempts, COALESCE(AVG(percentage), 0) as avg_score
                FROM quiz_attempts 
                GROUP BY topic 
                HAVING COUNT(*) > 0
                ORDER BY avg_score ASC
                LIMIT 5
            """)
            weak_topics_raw = cursor.fetchall()
            weak_topics = [{"topic": r[0], "attempts": r[1], "avg_score": round(r[2], 1) if r[2] else 0} for r in weak_topics_raw]
        except Exception:
            weak_topics = []
        
        # Topics not yet studied
        try:
            cursor.execute("""
                SELECT DISTINCT course_code, topic_name FROM topic_content
                WHERE (course_code, topic_name) NOT IN 
                (SELECT subject, topic FROM learning_progress WHERE status = 'Completed')
                LIMIT 5
            """)
            unstudied_raw = cursor.fetchall()
            unstudied = [{"course_code": r[0], "topic_name": r[1]} for r in unstudied_raw]
        except Exception:
            unstudied = []
        
        # Completed topics for review
        try:
            cursor.execute("""
                SELECT subject, topic FROM learning_progress 
                WHERE status = 'Completed' 
                ORDER BY last_accessed DESC 
                LIMIT 3
            """)
            review_raw = cursor.fetchall()
            review_topics = [{"subject": r[0], "topic": r[1]} for r in review_raw]
        except Exception:
            review_topics = []
        
        conn.close()
        
        return {
            "weak_topics_to_review": weak_topics,
            "next_to_study": unstudied,
            "suggested_review": review_topics
        }

init_db()