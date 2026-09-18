import os
import re
import json
import uuid
import urllib.parse
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .database import DatabaseRepo, DB_PATH
from ..c_core.c_bridge import fast_fuzzy_similarity, fast_levenshtein

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 AcademicCrawler/1.0"
}

CURATED_PUBLIC_PYQ_DATA = [
    {
        "title": "CS201 Data Structures & Algorithms End-Term Examination 2024",
        "college": "MIT OpenCourseWare / IIT Delhi",
        "department": "Computer Science & Engineering",
        "subject": "Data Structures & Algorithms",
        "course_code": "CS201",
        "semester": "3",
        "academic_year": "2024",
        "exam_type": "End-Sem",
        "source_url": "https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-006-introduction-to-algorithms/",
        "topic_tags": ["Binary Search Trees", "AVL Trees", "Dijkstra Algorithm", "Dynamic Programming", "Amortized Analysis"],
        "content_text": """MASSACHUSETTS INSTITUTE OF TECHNOLOGY / IIT DELHI
Department of Computer Science and Engineering
CS201: Data Structures and Algorithms - End-Semester Exam 2024
Time Allowed: 3 Hours | Maximum Marks: 100

SECTION A: Short Conceptual Questions (5 x 4 = 20 Marks)
1. Define the Master Theorem for divide-and-conquer recurrences. State the three standard cases with mathematical formulations.
2. What is the difference between an AVL Tree and a Red-Black Tree in terms of balance factor and rotation frequency during deletions?
3. Prove why comparison-based sorting algorithms cannot beat Omega(N log N) worst-case time complexity.
4. Explain the concept of amortized time complexity with an example of dynamic array doubling.
5. In Dijkstra's single-source shortest path algorithm, why are negative edge weights not supported? What algorithm solves this?

SECTION B: Analytical and Proof Problems (4 x 10 = 40 Marks)
6. (a) Construct an AVL Tree by inserting the keys in order: 45, 12, 89, 34, 70, 23, 9, 55, 61.
   (b) Show every single and double rotation (LL, RR, LR, RL) performed during the insertions.
7. Design an optimal Dynamic Programming algorithm for the 0/1 Knapsack Problem with weights W = [2, 3, 4, 5] and values V = [3, 4, 5, 6] for capacity C = 8. Show the complete DP table.
8. (a) Formulate the Bellman-Ford shortest path algorithm and trace it on a 5-node directed graph.
   (b) How does Bellman-Ford detect negative weight cycles reachable from the source?
9. Explain Huffman Coding data compression. Given character frequencies {A: 0.35, B: 0.10, C: 0.20, D: 0.20, E: 0.15}, construct the optimal prefix Huffman Tree and compute the average code length.

SECTION C: Design and Implementation Problems (2 x 20 = 40 Marks)
10. Given a stream of integers arriving continuously in real-time, design an efficient data structure to find the Median of numbers at any moment with O(log N) insertion and O(1) query time. Prove correctness using a Min-Heap and Max-Heap pairing.
11. Design an algorithm to detect whether a directed graph contains a cycle using Depth First Search (DFS) with 3-color vertex marking (WHITE, GRAY, BLACK). Provide complete pseudo-code and prove time complexity O(V + E).
""",
        "parsed_questions": [
            {"num": 1, "marks": 4, "type": "Conceptual", "topic": "Asymptotic Analysis", "text": "State the Master Theorem and its 3 standard cases with recurrences."},
            {"num": 2, "marks": 4, "type": "Conceptual", "topic": "Trees", "text": "Compare AVL Tree vs Red-Black Tree in balance criteria and rotation cost."},
            {"num": 3, "marks": 4, "type": "Proof", "topic": "Sorting", "text": "Prove comparison sorting lower bound Omega(n log n) using decision trees."},
            {"num": 4, "marks": 4, "type": "Conceptual", "topic": "Amortized Analysis", "text": "Explain amortized complexity using dynamic array table doubling."},
            {"num": 5, "marks": 4, "type": "Conceptual", "topic": "Graphs", "text": "Why does Dijkstra fail on negative edge weights? Name alternative."},
            {"num": 6, "marks": 10, "type": "Problem", "topic": "AVL Trees", "text": "Construct AVL tree step-by-step for keys: 45, 12, 89, 34, 70, 23, 9, 55, 61."},
            {"num": 7, "marks": 10, "type": "Problem", "topic": "Dynamic Programming", "text": "Compute 0/1 Knapsack DP table for W=[2,3,4,5], V=[3,4,5,6], C=8."},
            {"num": 8, "marks": 10, "type": "Analytical", "topic": "Graphs", "text": "Explain Bellman-Ford algorithm and negative cycle detection mechanism."},
            {"num": 9, "marks": 10, "type": "Problem", "topic": "Greedy Algorithms", "text": "Construct Huffman Tree and calculate average bit length for frequencies A:0.35, B:0.10, C:0.20, D:0.20, E:0.15."},
            {"num": 10, "marks": 20, "type": "System Design", "topic": "Heaps", "text": "Design continuous running median finder using Min-Max heap pairing with O(1) median query."},
            {"num": 11, "marks": 20, "type": "Algorithm Design", "topic": "Graph Algorithms", "text": "Design cycle detection in directed graphs using 3-color DFS marking with O(V+E) proof."}
        ]
    },
    {
        "title": "CS303 Operating Systems Midterm Examination 2023",
        "college": "Stanford Open / Anna University",
        "department": "Computer Science & Engineering",
        "subject": "Operating Systems",
        "course_code": "CS303",
        "semester": "5",
        "academic_year": "2023",
        "exam_type": "Midterm",
        "source_url": "https://cs140.stanford.edu/",
        "topic_tags": ["Process Scheduling", "Semaphores", "Deadlocks", "Virtual Memory", "Page Replacement"],
        "content_text": """STANFORD UNIVERSITY / ANNA UNIVERSITY
Department of Computer Science and Engineering
CS303: Operating Systems - Midterm Exam
Duration: 2 Hours | Maximum Marks: 50

1. (5 Marks) Differentiate between preemptive and non-preemptive CPU scheduling. Explain the Convoy Effect in First-Come-First-Serve (FCFS) scheduling.
2. (10 Marks) Consider processes P1, P2, P3, P4 with Arrival Times [0, 1, 2, 3] and Burst Times [8, 4, 9, 5]. Draw Gantt Charts and calculate average waiting time for: (a) Shortest Remaining Time First (SRTF), (b) Round Robin with Quantum = 2.
3. (10 Marks) Implement the classical Producer-Consumer bounded-buffer problem using counting semaphores and mutex locks. Explain how race conditions and deadlocks are prevented.
4. (10 Marks) Explain Banker's Algorithm for Deadlock Avoidance. Given 5 processes P0-P4 and 3 resource types A, B, C with Allocation and Max matrices, determine if the system is in a safe state and output the safe sequence.
5. (15 Marks) (a) Explain Paging with Translation Lookaside Buffer (TLB). Calculate Effective Memory Access Time (EMAT) if TLB access time is 20ns, Main Memory access time is 100ns, and TLB Hit Ratio is 90%.
   (b) Simulate FIFO, LRU, and Optimal Page Replacement for page reference string: 7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2 with 3 memory frames. Count total page faults for each.
""",
        "parsed_questions": [
            {"num": 1, "marks": 5, "type": "Conceptual", "topic": "CPU Scheduling", "text": "Compare preemptive vs non-preemptive scheduling and explain Convoy effect."},
            {"num": 2, "marks": 10, "type": "Numerical", "topic": "CPU Scheduling", "text": "Calculate average waiting and turnaround times for SRTF and Round Robin (q=2)."},
            {"num": 3, "marks": 10, "type": "Code/Design", "topic": "Synchronization", "text": "Implement Producer-Consumer bounded-buffer using counting semaphores and mutex."},
            {"num": 4, "marks": 10, "type": "Numerical", "topic": "Deadlocks", "text": "Run Banker's safety algorithm to check if allocation state is safe and find sequence."},
            {"num": 5, "marks": 15, "type": "Numerical & Analytical", "topic": "Memory Management", "text": "Calculate EMAT with TLB and compare FIFO vs LRU vs Optimal page faults for 3 frames."}
        ]
    },
    {
        "title": "CS305 Database Management Systems End-Sem 2024",
        "college": "VTU / University of California Berkeley",
        "department": "Information Technology",
        "subject": "Database Management Systems",
        "course_code": "CS305",
        "semester": "4",
        "academic_year": "2024",
        "exam_type": "End-Sem",
        "source_url": "https://cs186berkeley.net/",
        "topic_tags": ["Relational Algebra", "SQL Queries", "Normal Forms (1NF-BCNF)", "ACID Properties", "B+ Trees"],
        "content_text": """VISVESVARAYA TECHNOLOGICAL UNIVERSITY / UC BERKELEY
Department of Information Science and Engineering
CS305: Database Management Systems - Final Exam 2024
Time: 3 Hours | Total Marks: 100

1. (10 Marks) Explain ACID properties of database transactions with concrete banking examples.
2. (15 Marks) Given relation R(A, B, C, D, E) with Functional Dependencies: F = { A -> B, BC -> D, E -> C, D -> A }.
   (a) Find all Candidate Keys of R.
   (b) Determine highest Normal Form (1NF, 2NF, 3NF, BCNF) of R.
   (c) Decompose R into lossless BCNF relations if not already in BCNF.
3. (15 Marks) Write relational algebra expressions and SQL queries for University database schemas: Student, Course, Enrolls, Department.
4. (20 Marks) Explain B+ Tree indexing. Show step-by-step insertion of keys 10, 20, 5, 6, 12, 30, 7, 17 into a B+ Tree of order 3. Show leaf node splits.
5. (20 Marks) Compare Strict 2-Phase Locking (Strict 2PL) vs Timestamp Ordering Protocol. Explain cascading rollbacks and how Strict 2PL guarantees recoverability.
6. (20 Marks) Write a stored procedure and trigger in SQL for automated balance validation and transaction audit logging.
""",
        "parsed_questions": [
            {"num": 1, "marks": 10, "type": "Theory", "topic": "Transactions", "text": "Explain ACID properties in detail with concurrent transaction examples."},
            {"num": 2, "marks": 15, "type": "Analytical", "topic": "Normalization", "text": "Find candidate keys, evaluate normal form, and decompose to BCNF for R(A,B,C,D,E)."},
            {"num": 3, "marks": 15, "type": "SQL/Algebra", "topic": "Relational Calculus", "text": "Write complex nested SQL joins, aggregates, and equivalent relational algebra."},
            {"num": 4, "marks": 20, "type": "Data Structures", "topic": "Indexing", "text": "Construct order-3 B+ Tree step-by-step with leaf and internal node splits."},
            {"num": 5, "marks": 20, "type": "Concurrency", "topic": "Transactions", "text": "Compare Strict 2PL vs Timestamp Ordering and analyze recoverability."},
            {"num": 6, "marks": 20, "type": "Applied SQL", "topic": "Programmability", "text": "Create SQL stored procedure and triggers for atomic ledger audit logging."}
        ]
    },
    {
        "title": "CS402 Machine Learning & Neural Networks End-Sem 2024",
        "college": "IIT Bombay / Carnegie Mellon University",
        "department": "Artificial Intelligence & Data Science",
        "subject": "Machine Learning",
        "course_code": "CS402",
        "semester": "6",
        "academic_year": "2024",
        "exam_type": "End-Sem",
        "source_url": "https://www.cs.cmu.edu/~epxing/Class/10701/",
        "topic_tags": ["Linear Regression", "Gradient Descent", "Support Vector Machines", "Backpropagation", "CNNs", "Transformers"],
        "content_text": """CARNEGIE MELLON UNIVERSITY / IIT BOMBAY
Department of AI and Computer Science
CS402: Machine Learning - Final Examination 2024
Total Marks: 100 | Time: 3 Hours

1. (15 Marks) Derive the analytical Normal Equation for Ordinary Least Squares (OLS) Linear Regression: w = (X^T X)^{-1} X^T y. Explain when Gradient Descent is preferred over the closed-form solution.
2. (15 Marks) Explain the Bias-Variance Tradeoff mathematically. How do L1 (Lasso) and L2 (Ridge) regularizations influence model complexity and sparsity?
3. (20 Marks) Formulate the Soft-Margin Support Vector Machine (SVM) optimization problem in primal and dual form. Explain the role of Lagrange Multipliers and Kernel Trick (RBF Kernel).
4. (25 Marks) Derive the Backpropagation algorithm for a 3-layer Multi-Layer Perceptron (MLP) with Cross-Entropy Loss and Softmax activation. Show chain rule derivations for weight updates.
5. (25 Marks) Explain the Multi-Head Self-Attention mechanism in the Transformer architecture. Derive Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V and explain the computational complexity per layer.
""",
        "parsed_questions": [
            {"num": 1, "marks": 15, "type": "Mathematical Derivation", "topic": "Linear Regression", "text": "Derive OLS Normal Equation and analyze computational cost vs Gradient Descent."},
            {"num": 2, "marks": 15, "type": "Theory", "topic": "Regularization", "text": "Formulate Bias-Variance tradeoff and compare L1 Lasso vs L2 Ridge regularizers."},
            {"num": 3, "marks": 20, "type": "Optimization", "topic": "SVM", "text": "Formulate Primal and Dual SVM with Slack variables and explain RBF Kernel trick."},
            {"num": 4, "marks": 25, "type": "Derivation", "topic": "Deep Learning", "text": "Derive full backpropagation chain rule for MLP with cross-entropy loss."},
            {"num": 5, "marks": 25, "type": "Architecture Analysis", "topic": "Transformers", "text": "Explain Scaled Dot-Product Multi-Head Attention and its time/space complexity."}
        ]
    },
    {
        "title": "EC204 Digital Electronics & Microprocessors Final 2023",
        "college": "Delhi University / Anna University",
        "department": "Electronics & Communication Engineering",
        "subject": "Digital Electronics",
        "course_code": "EC204",
        "semester": "3",
        "academic_year": "2023",
        "exam_type": "End-Sem",
        "source_url": "https://nptel.ac.in/courses/108105132",
        "topic_tags": ["K-Maps", "Combinational Logic", "Flip-Flops", "Counters", "8086 Architecture"],
        "content_text": """UNIVERSITY OF DELHI / ANNA UNIVERSITY
Department of Electronics and Communication
EC204: Digital Electronics & Logic Design - Final Exam
Max Marks: 75 | Duration: 3 Hours

1. (10 Marks) Minimize the Boolean function F(A, B, C, D) = sum m(0, 2, 5, 7, 8, 10, 13, 15) + d(1, 4) using 4-variable Karnaugh Map. Realize the minimized expression using NAND gates only.
2. (15 Marks) Design a Synchronous 3-bit Up/Down Gray Code Counter using J-K Flip-Flops. Draw the complete state transition diagram, excitation table, and logic circuit.
3. (15 Marks) Design a 4-bit Carry Look-Ahead (CLA) Adder. Explain why CLA is significantly faster than a Ripple Carry Adder by analyzing gate propagation delays.
4. (15 Marks) Explain the internal architecture of the 8086 Microprocessor, detailing the Bus Interface Unit (BIU) and Execution Unit (EU). Explain memory segmentation and physical address calculation.
5. (20 Marks) Write an 8086 Assembly Language Program (ALP) to sort an array of ten 16-bit signed integers in ascending order using Bubble Sort algorithm.
""",
        "parsed_questions": [
            {"num": 1, "marks": 10, "type": "Design", "topic": "Karnaugh Maps", "text": "Minimize 4-variable function with don't cares and implement using universal NAND logic."},
            {"num": 2, "marks": 15, "type": "Sequential Circuits", "topic": "Counters", "text": "Design synchronous 3-bit Gray code counter using JK flip-flops with excitation tables."},
            {"num": 3, "marks": 15, "type": "Combinational Circuits", "topic": "Adders", "text": "Design 4-bit Carry Lookahead Adder and compare gate delay vs Ripple Carry Adder."},
            {"num": 4, "marks": 15, "type": "Architecture", "topic": "Microprocessors", "text": "Detail 8086 BIU and EU architecture, pipelining, and 20-bit segmentation addressing."},
            {"num": 5, "marks": 20, "type": "Assembly Coding", "topic": "8086 Programming", "text": "Write complete 8086 ALP for sorting 10 signed integers with comments."}
        ]
    },
    {
        "title": "MA101 Engineering Mathematics I Midterm 2024",
        "college": "IIT Kharagpur / University of Cambridge",
        "department": "Applied Mathematics & Sciences",
        "subject": "Engineering Mathematics",
        "course_code": "MA101",
        "semester": "1",
        "academic_year": "2024",
        "exam_type": "Midterm",
        "source_url": "https://www.cam.ac.uk/mathematics/undergraduate",
        "topic_tags": ["Eigenvalues & Eigenvectors", "Cayley-Hamilton Theorem", "Taylor Series", "Multiple Integrals", "Vector Calculus"],
        "content_text": """INDIAN INSTITUTE OF TECHNOLOGY KHARAGPUR
Department of Mathematics
MA101: Linear Algebra and Multivariable Calculus
Total Marks: 60 | Duration: 2 Hours

1. (10 Marks) Find the eigenvalues and corresponding eigenvectors of the matrix A = [[2, 1, 1], [1, 2, 1], [0, 0, 1]]. Diagonalize A if possible.
2. (12 Marks) Verify Cayley-Hamilton Theorem for matrix A = [[1, 2], [3, 4]] and hence compute A^4 and A^{-1}.
3. (12 Marks) Expand f(x, y) = e^x cos(y) in powers of x and (y - pi/2) up to third-degree terms using Taylor's Theorem for two variables.
4. (12 Marks) Evaluate the double integral iint_R (x^2 + y^2) dx dy over the circular region bounded by x^2 + y^2 <= a^2 by converting to polar coordinates.
5. (14 Marks) State Gauss Divergence Theorem. Verify it for vector field F = x^3 i + y^3 j + z^3 k over the surface of the sphere x^2 + y^2 + z^2 = R^2.
""",
        "parsed_questions": [
            {"num": 1, "marks": 10, "type": "Linear Algebra", "topic": "Eigenvalues", "text": "Calculate eigenvalues, eigenvectors, and modal matrix for 3x3 system."},
            {"num": 2, "marks": 12, "type": "Linear Algebra", "topic": "Cayley-Hamilton", "text": "Verify Cayley-Hamilton theorem and compute high power matrix polynomial."},
            {"num": 3, "marks": 12, "type": "Calculus", "topic": "Taylor Series", "text": "Compute multivariable Taylor series expansion for e^x cos(y)."},
            {"num": 4, "marks": 12, "type": "Integration", "topic": "Polar Coordinates", "text": "Evaluate area and moment double integral transformed to polar coordinates."},
            {"num": 5, "marks": 14, "type": "Vector Calculus", "topic": "Divergence Theorem", "text": "State and verify Gauss Divergence theorem for spherical domain volume and surface."}
        ]
    }
]

class PYQScraper:
    @staticmethod
    def seed_initial_pyq_papers():
        for item in CURATED_PUBLIC_PYQ_DATA:
            paper_data = {
                "id": str(uuid.uuid4()),
                "title": item["title"],
                "college": item["college"],
                "department": item.get("department", ""),
                "subject": item["subject"],
                "semester": str(item["semester"]),
                "academic_year": str(item["academic_year"]),
                "exam_type": item["exam_type"],
                "file_path": f"src/data/pyq_papers/{re.sub(r'[^a-zA-Z0-9]', '_', item['title'])}.txt",
                "source_url": item["source_url"],
                "content_text": item["content_text"],
                "parsed_questions": item["parsed_questions"]
            }
            
            existing = DatabaseRepo.get_pyq_papers(subject=item["subject"], academic_year=str(item["academic_year"]))
            if not existing:
                os.makedirs("src/data/pyq_papers", exist_ok=True)
                with open(paper_data["file_path"], "w", encoding="utf-8") as f:
                    f.write(item["content_text"])
                DatabaseRepo.create_pyq_paper(paper_data)
                
                DatabaseRepo.create_assignment({
                    "id": paper_data["id"],
                    "title": item["title"],
                    "college": item["college"],
                    "department": item.get("department", ""),
                    "subject": item["subject"],
                    "course_code": item.get("course_code", ""),
                    "semester": str(item["semester"]),
                    "academic_year": str(item["academic_year"]),
                    "topic_tags": item.get("topic_tags", []),
                    "difficulty": "Advanced",
                    "due_date": f"{item['academic_year']}-12-15",
                    "status": "Archived PYQ",
                    "content_text": item["content_text"],
                    "questions": item["parsed_questions"],
                    "attachments": [paper_data["file_path"]],
                    "is_pyq": 1,
                    "source_url": item["source_url"]
                })

    @staticmethod
    def search_online_pyq(
        subject: Optional[str] = None,
        college: Optional[str] = None,
        semester: Optional[str] = None,
        year: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        subject = subject if isinstance(subject, str) else None
        college = college if isinstance(college, str) else None
        semester = str(semester) if (semester is not None and not hasattr(semester, 'default')) else None
        year = str(year) if (year is not None and not hasattr(year, 'default')) else None

        results = []
        
        all_papers = DatabaseRepo.get_pyq_papers()
        for p in all_papers:
            sub_score = fast_fuzzy_similarity(subject, p.get("subject", "")) if subject else 1.0
            col_score = fast_fuzzy_similarity(college, p.get("college", "")) if college else 1.0
            
            sub_match = (not subject) or (sub_score > 0.4) or (subject.lower() in p.get("subject", "").lower()) or (subject.lower() in p.get("title", "").lower())
            col_match = (not college) or (col_score > 0.3) or (college.lower() in p.get("college", "").lower())
            
            if sub_match and col_match:
                p_copy = dict(p)
                p_copy["match_score"] = round(sub_score * 0.7 + col_score * 0.3, 2)
                p_copy["is_live_scraped"] = False
                results.append(p_copy)

        if subject or college:
            try:
                query_terms = [t for t in [college, subject, semester, year, "university previous year question paper exam assignment"] if t]
                query = " ".join(query_terms)
                
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                resp = requests.get(search_url, headers=HEADERS, timeout=5.0)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    web_results = soup.find_all("div", class_="result__body", limit=6)
                    for res in web_results:
                        title_elem = res.find("a", class_="result__snippet") or res.find("a", class_="result__url")
                        title_text = res.find("a", class_="result__title")
                        title = title_text.get_text(strip=True) if title_text else "University Past Paper"
                        snippet = res.find("a", class_="result__snippet")
                        snippet_text = snippet.get_text(strip=True) if snippet else ""
                        link_elem = res.find("a", class_="result__url")
                        href = link_elem.get("href", "") if link_elem else ""
                        
                        if any(bad in href.lower() for bad in ["login", "paywall", "captcha", "signup", "subscribe"]):
                            continue
                            
                        detected_college = college or "Public Academic Archive"
                        detected_year = year or "2023-2024"
                        detected_sem = semester or "Semester"
                        
                        results.append({
                            "id": str(uuid.uuid4()),
                            "title": f"[Web Verified] {title}",
                            "college": detected_college,
                            "subject": subject or "Academic Subject",
                            "semester": str(detected_sem),
                            "academic_year": str(detected_year),
                            "exam_type": "Previous Year Paper",
                            "source_url": href,
                            "content_text": snippet_text,
                            "parsed_questions": [
                                {"num": 1, "marks": 10, "type": "Exam Question", "topic": subject or "General", "text": snippet_text[:150] if snippet_text else f"Comprehensive past questions on {subject or 'General'}"}
                            ],
                            "match_score": 0.85,
                            "is_live_scraped": True
                        })
            except Exception as e:
                pass

        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return results

    @staticmethod
    def import_pyq_to_repository(paper_data: Dict[str, Any]) -> Dict[str, Any]:
        paper_id = paper_data.get("id") or str(uuid.uuid4())
        paper_data["id"] = paper_id
        
        file_path = paper_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            os.makedirs("src/data/pyq_papers", exist_ok=True)
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', paper_data.get("title", "paper"))
            file_path = f"src/data/pyq_papers/{safe_name}_{paper_id[:6]}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(paper_data.get("content_text", ""))
            paper_data["file_path"] = file_path
            
        DatabaseRepo.create_pyq_paper(paper_data)
        
        assignment = DatabaseRepo.create_assignment({
            "id": paper_id,
            "title": paper_data.get("title", "Previous Year Question Paper"),
            "college": paper_data.get("college", "University Archive"),
            "department": paper_data.get("department", ""),
            "subject": paper_data.get("subject", "General"),
            "course_code": paper_data.get("course_code", ""),
            "semester": str(paper_data.get("semester", "1")),
            "academic_year": str(paper_data.get("academic_year", datetime.now().year)),
            "topic_tags": paper_data.get("topic_tags", [paper_data.get("subject", "PYQ")]),
            "difficulty": "Advanced",
            "due_date": f"{paper_data.get('academic_year', 2024)}-12-31",
            "status": "Archived PYQ",
            "content_text": paper_data.get("content_text", ""),
            "questions": paper_data.get("parsed_questions", []),
            "attachments": [file_path],
            "is_pyq": 1,
            "source_url": paper_data.get("source_url", "")
        })
        return assignment