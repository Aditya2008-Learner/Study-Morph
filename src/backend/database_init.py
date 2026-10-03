"""
Database initialization and curriculum seeding
This module seeds the database with comprehensive 4-year B.Tech curriculum
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from .curriculum_data import FULL_BTECH_CURRICULUM
from .study_content import ALL_STUDY_CONTENT
from .curriculum_questions import COURSE_QUESTIONS_MAP
from .database import DB_PATH, get_connection, init_db


def seed_curriculum_database():
    """Seed the database with comprehensive 4-year B.Tech curriculum"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Seed curriculum
    for semester, sem_data in FULL_BTECH_CURRICULUM.items():
        for course in sem_data.get("courses", []):
            cursor.execute("""
            INSERT OR REPLACE INTO curriculum (
                code, name, semester, credits, category, course_type,
                modules, outcomes, key_textbooks, assignments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                course["code"],
                course["name"],
                str(semester),
                course.get("credits", 3),
                course.get("category", "Professional Core"),
                course.get("type", "Core"),
                json.dumps(course.get("topics", [])),
                json.dumps(course.get("outcomes", [])),
                json.dumps(course.get("key_textbooks", [])),
                json.dumps(course.get("assignments", []))
            ))
    
    conn.commit()
    print(f"Seeded curriculum: {sum(len(sem_data.get('courses', [])) for sem_data in FULL_BTECH_CURRICULUM.values())} courses")

def seed_topic_content():
    """Seed topic content and interactive content from study_content module"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    for subject_code, topics in ALL_STUDY_CONTENT.items():
        cursor.execute("DELETE FROM topic_content WHERE course_code = ?", (subject_code,))
        cursor.execute("DELETE FROM interactive_content WHERE course_code = ?", (subject_code,))
        for topic_name, content in topics.items():
            topic_id = str(uuid.uuid4())
            t_title = content.get("title", topic_name)
            flashcards = content.get("flashcards", [])
            cursor.execute("""
            INSERT OR REPLACE INTO topic_content (
                id, course_code, topic_name, summary, key_points, formulas,
                examples, mcqs, practice_questions, flashcards, viva_questions, difficulty, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                topic_id,
                subject_code,
                t_title,
                content.get("summary", ""),
                json.dumps(content.get("key_points", [])),
                json.dumps(content.get("formulas", [])),
                json.dumps(content.get("examples", [])),
                json.dumps(content.get("mcqs", [])),
                json.dumps(content.get("practice_questions", [])),
                json.dumps(flashcards),
                json.dumps(content.get("viva_questions", [])),
                content.get("difficulty", "Intermediate"),
                now
            ))

            for fc in flashcards:
                front = fc.get("front", "")
                back = fc.get("back", "")
                cursor.execute("""
                INSERT INTO interactive_content (course_code, topic, content, front_text, back_text)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    subject_code,
                    t_title,
                    back,
                    front,
                    back
                ))
    
    conn.commit()
    count = sum(len(topics) for topics in ALL_STUDY_CONTENT.values())
    print(f"Seeded topic content: {count} topics across {len(ALL_STUDY_CONTENT)} courses")

def seed_pyq_papers():
    """Seed sample PYQ papers for major subjects"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    pyq_samples = [
        {
            "title": "Data Structures End-Semester Examination 2024",
            "college": "Common University",
            "department": "Computer Science",
            "subject": "Data Structures",
            "semester": "2",
            "academic_year": "2024",
            "exam_type": "End-Sem",
            "content_text": """
SECTION A (Short Answer - 5 x 2 = 10 marks)
1. Explain the difference between array and linked list.
2. What is the balance factor in AVL trees?
3. State the time complexity of QuickSort.
4. Define Hashing and explain collision resolution techniques.
5. What is a stack? Give two applications.

SECTION B (Long Answer - 5 x 18 = 90 marks)
1. a) Insert the keys 50, 30, 70, 20, 40, 60, 80 into an AVL tree. Show all rotations required. (9 marks)
   b) Explain the difference between BFS and DFS with examples. (9 marks)

2. a) Solve the recurrence T(n) = 2T(n/2) + n using Master Theorem. (6 marks)
   b) Write the algorithm for 0/1 Knapsack using dynamic programming. (12 marks)

3. a) Explain the Kruskal's algorithm for finding MST. (9 marks)
   b) Compare Dijkstra's and Bellman-Ford algorithms. (9 marks)

4. a) What is a binary search tree? Write functions for insertion and deletion. (9 marks)
   b) Explain the concept of hashing. Discuss open addressing and chaining. (9 marks)

5. a) Write the algorithm for topological sort. (6 marks)
   b) Explain the concept of Heaps. Write functions for heapify and heap sort. (12 marks)
            """,
            "parsed_questions": [
                {"num": 1, "text": "Explain the difference between array and linked list.", "marks": 2},
                {"num": 2, "text": "What is the balance factor in AVL trees?", "marks": 2},
                {"num": 3, "text": "State the time complexity of QuickSort.", "marks": 2},
                {"num": 4, "text": "Define Hashing and explain collision resolution techniques.", "marks": 2},
                {"num": 5, "text": "What is a stack? Give two applications.", "marks": 2}
            ]
        },
        {
            "title": "Operating Systems End-Semester Examination 2024",
            "college": "Common University",
            "department": "Computer Science",
            "subject": "Operating Systems",
            "semester": "3",
            "academic_year": "2024",
            "exam_type": "End-Sem",
            "content_text": """
SECTION A
1. State the four necessary conditions for deadlock.
2. Explain the Banker's Algorithm for deadlock avoidance.
3. What is virtual memory? Explain demand paging.
4. Compare FCFS and SJF scheduling algorithms.
5. Explain the concept of thrashing.

SECTION B
1. a) Consider processes with arrival times [0,1,2,3] and burst times [7,4,1,4]. Calculate turnaround time and waiting time for SJF scheduling. (10 marks)
   b) Explain the concept of paging and segmentation. (8 marks)

2. a) Explain the Critical Section problem. What are the requirements for a valid solution? (8 marks)
   b) Write and explain the Reader-Writer problem solution using semaphores. (10 marks)

3. a) Explain the concept of disk scheduling. Compare FCFS, SSTF, and SCAN algorithms. (9 marks)
   b) What is a file system? Explain the different file allocation methods. (9 marks)
            """,
            "parsed_questions": [
                {"num": 1, "text": "State the four necessary conditions for deadlock.", "marks": 5},
                {"num": 2, "text": "Explain the Banker's Algorithm for deadlock avoidance.", "marks": 10},
                {"num": 3, "text": "What is virtual memory? Explain demand paging.", "marks": 8}
            ]
        }
    ]
    
    for paper in pyq_samples:
        cursor.execute("SELECT id FROM pyq_papers WHERE title = ? AND subject = ?", 
                      (paper["title"], paper["subject"]))
        if cursor.fetchone():
            continue
            
        paper_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO pyq_papers (id, title, college, department, subject, semester, academic_year, exam_type, content_text, parsed_questions, downloaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_id,
            paper["title"],
            paper["college"],
            paper.get("department", ""),
            paper["subject"],
            paper["semester"],
            paper["academic_year"],
            paper["exam_type"],
            paper["content_text"],
            json.dumps(paper.get("parsed_questions", [])),
            now
        ))
    
    conn.commit()
    print(f"Seeded {len(pyq_samples)} PYQ papers")

def seed_sample_assignments():
    """Seed sample assignments for major topics"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    sample_assignments = [
        {
            "title": "Data Structures - Binary Trees and BSTs",
            "college": "Common University",
            "subject": "Data Structures",
            "semester": "2",
            "academic_year": "2024",
            "difficulty": "Intermediate",
            "topic_tags": ["Binary Trees", "BST", "Tree Traversals"],
            "content_text": "Assignment on binary trees, BST operations, and tree traversals",
            "questions": [
                {"num": 1, "text": "Write a program to create a BST and perform inorder, preorder, and postorder traversals.", "marks": 10},
                {"num": 2, "text": "Explain the difference between complete and full binary trees.", "marks": 5},
                {"num": 3, "text": "Write functions to find height, number of nodes, and check if tree is balanced.", "marks": 15}
            ]
        },
        {
            "title": "Operating Systems - CPU Scheduling",
            "college": "Common University",
            "subject": "Operating Systems",
            "semester": "3",
            "academic_year": "2024",
            "difficulty": "Intermediate",
            "topic_tags": ["CPU Scheduling", "Process Management"],
            "content_text": "Assignment on CPU scheduling algorithms",
            "questions": [
                {"num": 1, "text": "Consider 4 processes with burst times [8,4,9,5] and arrival times [0,1,2,3]. Calculate completion time, turnaround time, and waiting time for FCFS, SJF, and RR (quantum=2).", "marks": 20},
                {"num": 2, "text": "Explain the advantages and disadvantages of Round Robin scheduling.", "marks": 10}
            ]
        }
    ]
    
    for assignment in sample_assignments:
        assignment_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO assignments (id, title, college, subject, semester, academic_year, topic_tags, difficulty, content_text, questions, status, is_pyq, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            assignment_id,
            assignment["title"],
            assignment["college"],
            assignment["subject"],
            assignment["semester"],
            assignment["academic_year"],
            json.dumps(assignment.get("topic_tags", [])),
            assignment.get("difficulty", "Intermediate"),
            assignment.get("content_text", ""),
            json.dumps(assignment.get("questions", [])),
            "Completed",
            0,
            now,
            now
        ))
    
    conn.commit()
    print(f"Seeded {len(sample_assignments)} sample assignments")

def seed_question_bank():
    """Seed comprehensive 15 questions per subject (Set 1 & Set 2) into question_bank"""
    # The separate schema module was removed in this cleanup; the question_bank
    # table is created by init_db() in this module, so no extra DDL call is needed.
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Ensure set_num column exists
    try:
        cursor.execute("PRAGMA table_info(question_bank);")
        cols = [r[1] for r in cursor.fetchall()]
        if "set_num" not in cols:
            cursor.execute("ALTER TABLE question_bank ADD COLUMN set_num INTEGER DEFAULT 1;")
    except Exception:
        pass

    # Clear previous question bank entries to avoid duplicates
    cursor.execute("DELETE FROM question_bank;")

    # Lookup map from code to course name and year
    course_info = {}
    for sem, sdata in FULL_BTECH_CURRICULUM.items():
        for course in sdata.get("courses", []):
            course_info[course["code"]] = {
                "name": course["name"],
                "year": sdata.get("year", 1),
                "semester": sem
            }

    total_inserted = 0
    for code, sets in COURSE_QUESTIONS_MAP.items():
        info = course_info.get(code, {"name": code, "year": 1, "semester": 1})
        cname = info["name"]
        cyear = info["year"]

        for set_key, set_num in [("set_1", 1), ("set_2", 2)]:
            q_list = sets.get(set_key, [])
            for idx, q in enumerate(q_list):
                q_text = q["text"]
                topic_label = f"Topic {idx + 1}"
                subtopic = q.get("topic", "")
                diff = q.get("difficulty", "Medium")
                marks = q.get("marks", 5)

                # Insert by subject code
                qid_code = str(uuid.uuid4())
                cursor.execute("""
                INSERT INTO question_bank (
                    id, question_text, subject, topic, subtopic, source_type,
                    difficulty, question_type, marks, year, set_num, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    qid_code, q_text, code, topic_label, subtopic, "AI_Generated",
                    diff, "Exam", marks, cyear, set_num, "Approved", now, now
                ))

                # Insert by subject name
                qid_name = str(uuid.uuid4())
                cursor.execute("""
                INSERT INTO question_bank (
                    id, question_text, subject, topic, subtopic, source_type,
                    difficulty, question_type, marks, year, set_num, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    qid_name, q_text, cname, topic_label, subtopic, "AI_Generated",
                    diff, "Exam", marks, cyear, set_num, "Approved", now, now
                ))
                total_inserted += 2

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM question_bank")
    print(f"Seeded question bank: {cursor.fetchone()[0]} total questions across all 29 courses (Sets 1 & 2)")

def seed_all():
    """Seed all curriculum data"""
    print("Initializing database...")
    init_db()
    
    print("Seeding curriculum...")
    seed_curriculum_database()
    
    print("Seeding topic content...")
    seed_topic_content()
    
    print("Seeding question bank...")
    seed_question_bank()

    print("Seeding PYQ papers...")
    seed_pyq_papers()
    
    print("Seeding sample assignments...")
    seed_sample_assignments()
    
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_all()