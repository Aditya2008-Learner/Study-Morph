# Core Project Structure
- src/backend/: FastAPI app, database models, APIs, utilities
- src/static/: Frontend assets (HTML templates, CSS, JS)
- src/c_core/: C extension for performance-critical operations
- src/data/: SQLite database (study_assistant.db), PYQ papers
- Key scripts: rebuild_db.py, verify_*.py, check_*.py

# Key Invariants
- Database schema: courses table (id, course_code, name, year, description, credits)
- Topic content stored in topic_content table
- Question bank: question_bank table with course_code/year linkage
- Interactive content: interactive_content table for flashcards
- Study Now links open course.html (not index.html)
- Semester filter dropdown maps to subject dropdown with 28 unique courses
- C-core DLL builds successfully with gcc -O3 -shared and loads in Python
- All API endpoints return HTTP 200 when server is running
- Frontend uses IntersectionObserver for scroll reveal animations
- Design tokens: emerald primary (#059669), charcoal text (#1C1917), warm off-white (#FAFAF9)