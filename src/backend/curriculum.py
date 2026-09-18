from typing import List, Dict, Any, Optional

BTECH_CYBER_SECURITY_CURRICULUM: Dict[int, List[Dict[str, Any]]] = {
    1: [
{"code": "MA101", "name": "Engineering Mathematics I", "credits": 4, "category": "Basic Science & Mathematics", "type": "Core",
          "modules": [{"id": "M1", "title": "Linear Algebra", "topics": ["Matrices & Determinants", "Eigenvalues & Eigenvectors", "Cayley-Hamilton Theorem"]},
                      {"id": "M2", "title": "Single Variable Calculus", "topics": ["Limits", "Differentiability", "Integration"]},
                      {"id": "M3", "title": "Multivariable Calculus", "topics": ["Partial Derivatives", "Multiple Integrals", "Vector Calculus"]}],
          "outcomes": ["Apply matrix algebra and calculus to engineering problems."], "key_textbooks": ["Erwin Kreyszig"], "assignments": []},
        {"code": "PH101", "name": "Engineering Physics", "credits": 4, "category": "Basic Science & Mathematics", "type": "Core",
          "modules": [{"id": "M1", "title": "Mechanics & Waves", "topics": ["Mechanics", "Waves"]},
                      {"id": "M2", "title": "Optics & Thermodynamics", "topics": ["Optics", "Thermodynamics"]},
                      {"id": "M3", "title": "Electromagnetism", "topics": ["Electromagnetism"]}],
          "outcomes": ["Apply physical principles and wave mechanics to engineering systems."], "key_textbooks": ["Halliday & Resnick", "Arthur Beiser"], "assignments": []},
        {"code": "CH101", "name": "Engineering Chemistry", "credits": 4, "category": "Basic Science & Mathematics", "type": "Core",
          "modules": [{"id": "M1", "title": "Atomic Structure & Bonding", "topics": ["Atomic Structure", "Chemical Bonding"]},
                      {"id": "M2", "title": "Thermodynamics & Electrochemistry", "topics": ["Thermodynamics", "Electrochemistry"]},
                      {"id": "M3", "title": "Organic Chemistry & Materials", "topics": ["Organic Chemistry"]}],
          "outcomes": ["Apply chemical principles, electrochemistry, and materials science to engineering."], "key_textbooks": ["P.C. Jain & Monica Jain", "Shashi Chawla"], "assignments": []},
        {"code": "CS101", "name": "Introduction to Programming in C", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Fundamentals of C", "topics": ["Data Types", "Control Flow", "Functions"]},
                     {"id": "M2", "title": "Pointers & Arrays", "topics": ["Pointers", "Dynamic Memory", "Strings"]}],
         "outcomes": ["Write correct and efficient C programs."], "key_textbooks": ["Let Us C - Yashavant Kanetkar"], "assignments": []},
    ],
    2: [
        {"code": "MA102", "name": "Engineering Mathematics II", "credits": 4, "category": "Basic Science & Mathematics", "type": "Core",
         "modules": [{"id": "M1", "title": "Complex Analysis", "topics": ["Analytic Functions", "Cauchy-Riemann Equations"]},
                     {"id": "M2", "title": "Laplace & Fourier Transforms", "topics": ["Laplace Transform", "Fourier Series"]}],
         "outcomes": ["Apply transform methods to engineering problems."], "key_textbooks": ["B.S. Grewal"], "assignments": []},
        {"code": "CS102", "name": "Data Structures", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Fundamental Data Structures", "topics": ["Arrays & Linked Lists", "Stacks & Queues"]},
                     {"id": "M2", "title": "Trees", "topics": ["Binary Trees", "AVL Trees", "B-Trees"]},
                     {"id": "M3", "title": "Graph Algorithms", "topics": ["BFS & DFS", "Dijkstra", "Bellman-Ford"]},
                     {"id": "M4", "title": "Hashing & Sorting", "topics": ["Hash Tables", "Sorting Algorithms"]}],
         "outcomes": ["Implement and analyze data structures."], "key_textbooks": ["CLRS"], "assignments": []},
    ],
    3: [
        {"code": "CS201", "name": "Computer Organization & Architecture", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "ISA Design", "topics": ["RISC vs CISC", "Addressing Modes"]},
                     {"id": "M2", "title": "ALU Design", "topics": ["Fast Adders", "Multiplication"]},
                     {"id": "M3", "title": "Pipelining", "topics": ["Pipeline Hazards", "Branch Prediction"]}],
         "outcomes": ["Design and analyze processor architectures."], "key_textbooks": ["Mano"], "assignments": []},
        {"code": "CS202", "name": "Object-Oriented Programming with Java", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "OOP Fundamentals", "topics": ["Classes", "Inheritance", "Polymorphism"]},
                     {"id": "M2", "title": "Multithreading", "topics": ["Thread Lifecycle", "Synchronization"]}],
         "outcomes": ["Design object-oriented solutions in Java."], "key_textbooks": ["Herbert Schildt"], "assignments": []},
        {"code": "CS203", "name": "Operating Systems", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Process Management", "topics": ["Process States", "IPC"]},
                     {"id": "M2", "title": "CPU Scheduling", "topics": ["FCFS", "SJF", "Round Robin"]},
                     {"id": "M3", "title": "Synchronization", "topics": ["Semaphores", "Banker's Algorithm"]},
                     {"id": "M4", "title": "Memory Management", "topics": ["Paging", "Page Replacement"]}],
         "outcomes": ["Analyze and design OS components."], "key_textbooks": ["Silberschatz"], "assignments": []},
        {"code": "CS204", "name": "Database Management Systems", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Relational Model & SQL", "topics": ["ER Model", "SQL", "Joins"]},
                     {"id": "M2", "title": "Normalization", "topics": ["1NF to BCNF", "Functional Dependencies"]},
                     {"id": "M3", "title": "Transactions", "topics": ["ACID", "Concurrency Control"]},
                     {"id": "M4", "title": "Indexing & Optimization", "topics": ["B+ Tree", "Query Optimization"]}],
         "outcomes": ["Design normalized schemas and write SQL."], "key_textbooks": ["Korth"], "assignments": []},
        {"code": "CS205", "name": "Design and Analysis of Algorithms", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Asymptotic Analysis", "topics": ["Big-O", "Master Theorem"]},
                     {"id": "M2", "title": "Greedy Algorithms", "topics": ["Huffman", "Prim's"]},
                     {"id": "M3", "title": "Dynamic Programming", "topics": ["Knapsack", "LCS"]},
                     {"id": "M4", "title": "NP Completeness", "topics": ["P, NP, NP-Hard"]}],
         "outcomes": ["Design and analyze algorithms."], "key_textbooks": ["CLRS"], "assignments": []},
    ],
    4: [
        {"code": "CS301", "name": "Computer Networks", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Data Link Layer", "topics": ["Framing", "Error Detection", "MAC Protocols"]},
                     {"id": "M2", "title": "Network Layer", "topics": ["IP Addressing", "Routing"]},
                     {"id": "M3", "title": "Transport Layer", "topics": ["TCP", "UDP", "Congestion Control"]},
                     {"id": "M4", "title": "Application Layer", "topics": ["HTTP", "DNS", "TLS"]}],
         "outcomes": ["Analyze network protocols."], "key_textbooks": ["Tanenbaum"], "assignments": []},
        {"code": "CS302", "name": "Software Engineering & Project Management", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "SDLC", "topics": ["Waterfall", "Agile", "Scrum"]},
                     {"id": "M2", "title": "Software Design", "topics": ["UML", "Design Patterns"]}],
         "outcomes": ["Apply SDLC models."], "key_textbooks": ["Sommerville"], "assignments": []},
        {"code": "CS303", "name": "Microprocessors & Embedded Systems", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "8086 Microprocessor", "topics": ["Architecture", "Programming"]}],
         "outcomes": ["Program 8086 in assembly."], "key_textbooks": ["Liu"], "assignments": []},
        {"code": "CS304", "name": "Theory of Computation", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Automata", "topics": ["DFA", "NFA"]},
                     {"id": "M2", "title": "Turing Machines", "topics": ["Halting Problem"]}],
         "outcomes": ["Classify languages using Chomsky hierarchy."], "key_textbooks": ["Hopcroft"], "assignments": []},
        {"code": "CY201", "name": "Cyber Security Fundamentals", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "Security Foundations", "topics": ["CIA Triad", "Threats"]},
                     {"id": "M2", "title": "Cryptography Basics", "topics": ["Symmetric", "Asymmetric", "Hashing"]}],
         "outcomes": ["Apply cryptographic techniques."], "key_textbooks": ["Stallings"], "assignments": []},
    ],
    5: [
        {"code": "CS401", "name": "Advanced Algorithms & Optimization", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Network Flow", "topics": ["Ford-Fulkerson"]}],
         "outcomes": ["Solve optimization problems."], "key_textbooks": ["Kleinberg"], "assignments": []},
        {"code": "CS402", "name": "Machine Learning & AI for Cyber Security", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "ML Foundations", "topics": ["Linear Regression", "SVM"]},
                     {"id": "M2", "title": "Deep Learning", "topics": ["CNN", "RNN"]}],
         "outcomes": ["Build ML models for security."], "key_textbooks": ["Bishop"], "assignments": []},
        {"code": "CS403", "name": "Cryptography & Network Security", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Symmetric Cryptography", "topics": ["AES", "Block Cipher Modes"]},
                     {"id": "M2", "title": "Public Key", "topics": ["RSA", "ECC"]}],
         "outcomes": ["Implement cryptographic protocols."], "key_textbooks": ["Stallings"], "assignments": []},
        {"code": "CS404", "name": "Web Application Security", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "OWASP Top 10", "topics": ["XSS", "SQLi", "CSRF"]}],
         "outcomes": ["Identify and exploit web vulnerabilities."], "key_textbooks": ["Stuttard"], "assignments": []},
        {"code": "HS301", "name": "Cyber Law & Digital Forensics", "credits": 3, "category": "Humanities & Social Sciences", "type": "Core",
         "modules": [{"id": "M1", "title": "IT Act 2000", "topics": ["Sections 65-72"]}],
         "outcomes": ["Understand cyber law."], "key_textbooks": ["Cyber Law India"], "assignments": []},
    ],
    6: [
        {"code": "CS501", "name": "Ethical Hacking & Penetration Testing", "credits": 4, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Reconnaissance", "topics": ["Nmap", "OSINT"]},
                     {"id": "M2", "title": "Exploitation", "topics": ["Metasploit", "Buffer Overflow"]}],
         "outcomes": ["Conduct penetration tests."], "key_textbooks": ["Hacking Exposed"], "assignments": []},
        {"code": "CS502", "name": "Cloud Security & Virtualization", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Cloud Fundamentals", "topics": ["IaaS", "PaaS", "SaaS"]}],
         "outcomes": ["Secure cloud architectures."], "key_textbooks": ["AWS Security"], "assignments": []},
        {"code": "CS503", "name": "Malware Analysis & Reverse Engineering", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Static Analysis", "topics": ["IDA Pro", "Ghidra"]}],
         "outcomes": ["Reverse engineer malware."], "key_textbooks": ["Practical Malware Analysis"], "assignments": []},
        {"code": "CS504", "name": "Blockchain & DLT Security", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "Blockchain Fundamentals", "topics": ["Consensus", "Merkle Trees"]}],
         "outcomes": ["Develop smart contracts."], "key_textbooks": ["Antonopoulos"], "assignments": []},
    ],
    7: [
        {"code": "CS601", "name": "Network Forensics & Incident Response", "credits": 3, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Traffic Analysis", "topics": ["Wireshark", "PCAP"]}],
         "outcomes": ["Conduct network forensics."], "key_textbooks": ["Mandia"], "assignments": []},
        {"code": "CS602", "name": "AI-Driven Security Automation", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "SOAR", "topics": ["Automated Playbooks"]}],
         "outcomes": ["Implement AI security automation."], "key_textbooks": ["SOAR Best Practices"], "assignments": []},
        {"code": "CS603", "name": "Secure Software Development Lifecycle", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "SAST/DAST", "topics": ["Static Analysis", "Dynamic Analysis"]}],
         "outcomes": ["Integrate security into SDLC."], "key_textbooks": ["OWASP SAMM"], "assignments": []},
        {"code": "CS699", "name": "Research Project (Phase 1)", "credits": 8, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Research Methodology", "topics": ["Literature Survey"]}],
         "outcomes": ["Conduct original research."], "key_textbooks": [], "assignments": []},
    ],
    8: [
        {"code": "CS701", "name": "Advanced Persistent Threats (APT) & Defense", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "APT Landscape", "topics": ["Kill Chain", "MITRE ATT&CK"]}],
         "outcomes": ["Analyze APT attacks."], "key_textbooks": ["FireEye"], "assignments": []},
        {"code": "CS702", "name": "IoT & Industrial Control Systems Security", "credits": 3, "category": "Professional Elective", "type": "Elective",
         "modules": [{"id": "M1", "title": "IoT Architecture", "topics": ["MQTT", "CoAP"]}],
         "outcomes": ["Secure IoT systems."], "key_textbooks": ["IoT Security"], "assignments": []},
        {"code": "CS798", "name": "Industry Internship", "credits": 10, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Industry Practice", "topics": ["16-Week Placement"]}],
         "outcomes": ["Apply academic knowledge professionally."], "key_textbooks": [], "assignments": []},
        {"code": "CS799", "name": "Research Project (Phase 2) & Thesis", "credits": 8, "category": "Professional Core", "type": "Core",
         "modules": [{"id": "M1", "title": "Thesis & Presentation", "topics": ["Thesis Writing"]}],
         "outcomes": ["Complete original research and publish."], "key_textbooks": [], "assignments": []},
    ],
}

def get_all_courses() -> List[Dict[str, Any]]:
    courses = []
    for semester, sem_courses in BTECH_CYBER_SECURITY_CURRICULUM.items():
        for c in sem_courses:
            c_copy = dict(c)
            c_copy["semester"] = semester
            courses.append(c_copy)
    return courses

def get_semester_courses(semester: int) -> List[Dict[str, Any]]:
    return BTECH_CYBER_SECURITY_CURRICULUM.get(semester, [])

def get_course_by_code(code: str) -> Optional[Dict[str, Any]]:
    for semester, courses in BTECH_CYBER_SECURITY_CURRICULUM.items():
        for c in courses:
            if c["code"].upper() == code.upper():
                result = dict(c)
                result["semester"] = semester
                return result
    return None

def get_all_semesters() -> List[int]:
    return sorted(BTECH_CYBER_SECURITY_CURRICULUM.keys())

def get_semester_stats() -> Dict[int, int]:
    return {sem: len(courses) for sem, courses in BTECH_CYBER_SECURITY_CURRICULUM.items()}

def get_total_credits() -> int:
    total = 0
    for courses in BTECH_CYBER_SECURITY_CURRICULUM.values():
        for c in courses:
            total += c.get("credits", 0)
    return total

def get_course_categories() -> List[str]:
    categories = set()
    for courses in BTECH_CYBER_SECURITY_CURRICULUM.values():
        for c in courses:
            categories.add(c.get("category", ""))
    return sorted(list(categories))

def get_curriculum_summary() -> Dict[str, Any]:
    all_courses = get_all_courses()
    return {
        "program": "B.Tech Computer Science & Engineering (Cyber Security)",
        "total_semesters": 8,
        "total_courses": len(all_courses),
        "total_credits": get_total_credits(),
        "semesters": get_semester_stats(),
        "categories": get_course_categories(),
    }

BTECH_CYBER_SECURITY_SUMMARY = get_curriculum_summary()