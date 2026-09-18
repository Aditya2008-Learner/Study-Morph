# Technology Stack
- Backend: Python 3.14, FastAPI, Uvicorn, SQLite3
- Frontend: HTML5, CSS3 (Tailwind-like utility classes via custom CSS), Vanilla JS (ES6)
- Build: gcc (for C-core DLL), no Node.js/build tools for frontend
- C-core: C99, compiled as shared library (libstudyc.dll) for performance-critical operations
- Database: SQLite3 (study_assistant.db) with PRAGMA foreign_keys=ON
- Other: PowerShell 5.1 for scripts, Git for version control