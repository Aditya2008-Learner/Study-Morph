"""
Comprehensive 4-Year B.Tech CSE Curriculum with Full Study Content
This module contains complete course structure, topics, and study material
"""

FULL_BTECH_CURRICULUM = {
    # ===== YEAR 1 - SEMESTER 1 =====
    1: {
        "year": 1,
        "semester": 1,
        "courses": [
            {
                "code": "MA101",
                "name": "Engineering Mathematics I",
                "credits": 4,
                "category": "Basic Sciences",
                "type": "Core",
                "topics": [
                    {
                        "name": "Matrices and Determinants",
                        "subtopics": ["Matrix Operations", "Determinants", "Inverse of Matrix", "Rank of Matrix", "System of Linear Equations"],
                        "important_points": ["Cramer's Rule", "Gaussian Elimination", "Matrix Rank Theorems"],
                        "formulas": ["det(AB) = det(A) × det(B)", "A⁻¹ = adj(A)/det(A)"],
                        "practice_questions": 15
                    },
                    {
                        "name": "Eigenvalues and Eigenvectors",
                        "subtopics": ["Characteristic Equation", "Cayley-Hamilton Theorem", "Diagonalization"],
                        "important_points": ["Eigenvalue Properties", "Similar Matrices", "Spectral Theorem"],
                        "formulas": ["det(A - λI) = 0", "Cayley-Hamilton: p(A) = 0"],
                        "practice_questions": 12
                    },
                    {
                        "name": "Differential Calculus",
                        "subtopics": ["Limits", "Continuity", "Differentiability", "Mean Value Theorems"],
                        "important_points": ["L'Hospital Rule", "Rolle's Theorem", "Lagrange's MVT"],
                        "formulas": ["lim(x→a) f(x)", "f'(x) = lim(h→0) [f(x+h)-f(x)]/h"],
                        "practice_questions": 20
                    }
                ]
            },
            {
                "code": "PH101",
                "name": "Engineering Physics",
                "credits": 3,
                "category": "Basic Sciences",
                "type": "Core",
                "topics": [
                    {
                        "name": "Mechanics",
                        "subtopics": ["Newton's Laws", "Work-Energy Theorem", "Rotational Dynamics", "Moment of Inertia", "Harmonic Motion"],
                        "important_points": ["Conservation of Momentum", "Rotational Equilibrium", "Damped Oscillations"],
                        "formulas": ["W = ΔK", "I = ∫r² dm", "τ = Iα"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Waves",
                        "subtopics": ["Wave Equation", "Superposition", "Sound Waves", "Doppler Effect", "Standing Waves"],
                        "important_points": ["Phase Velocity", "Group Velocity", "Resonance"],
                        "formulas": ["∂²y/∂x² = (1/v²) ∂²y/∂t²", "f' = f(v ± v₀)/(v ∓ v_s)"],
                        "practice_questions": 18
                    },
                    {
                        "name": "Optics",
                        "subtopics": ["Wave Optics", "Interference", "Diffraction", "Polarization", "Lasers"],
                        "important_points": ["Young's Double Slit", "Fraunhofer Diffraction", "Brewster's Law"],
                        "formulas": ["β = λD/d", "a sinθ = mλ", "tan θ_B = n"],
                        "practice_questions": 22
                    },
                    {
                        "name": "Thermodynamics",
                        "subtopics": ["First Law", "Second Law", "Carnot Engine", "Entropy", "Heat Transfer"],
                        "important_points": ["Carnot Efficiency", "Clausius Inequality", "Isentropic Processes"],
                        "formulas": ["dQ = dU + dW", "η = 1 - T_C/T_H", "dS = dQ_rev/T"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Electromagnetism",
                        "subtopics": ["Gauss's Law", "Faraday's Law", "Ampere-Maxwell Law", "Displacement Current", "EM Waves"],
                        "important_points": ["Maxwell's Equations", "Poynting Vector", "Speed of Light in Vacuum"],
                        "formulas": ["∮E·dA = Q/ε₀", "∮E·dl = -dΦ_B/dt", "c = 1/√(μ₀ε₀)"],
                        "practice_questions": 25
                    }
                ]
            },
            {
                "code": "CH101",
                "name": "Engineering Chemistry",
                "credits": 3,
                "category": "Basic Sciences",
                "type": "Core",
                "topics": [
                    {
                        "name": "Atomic Structure",
                        "subtopics": ["Bohr Model", "Quantum Numbers", "Orbitals", "Aufbau Principle", "Periodic Trends"],
                        "important_points": ["Heisenberg Uncertainty", "Pauli Exclusion", "Hund's Rule"],
                        "formulas": ["ΔxΔp ≥ ℏ/2", "λ = h/(mv)", "E_n = -13.6/n² eV"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Chemical Bonding",
                        "subtopics": ["Ionic Bonding", "Covalent Bonding", "VSEPR Theory", "Molecular Orbital Theory", "Hybridization"],
                        "important_points": ["Bond Order", "Paramagnetism of O2", "Steric Numbers"],
                        "formulas": ["Bond Order = (N_b - N_a)/2"],
                        "practice_questions": 22
                    },
                    {
                        "name": "Thermodynamics",
                        "subtopics": ["Enthalpy", "Hess's Law", "Gibbs Free Energy", "Spontaneity", "Chemical Equilibrium"],
                        "important_points": ["Exothermic vs Endothermic", "Free Energy Criterion", "Equilibrium Constant"],
                        "formulas": ["ΔG = ΔH - TΔS", "ΔG° = -RT ln K_eq"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Electrochemistry",
                        "subtopics": ["Galvanic Cells", "Nernst Equation", "EMF", "Corrosion & Rusting", "Batteries & Fuel Cells"],
                        "important_points": ["Standard Electrode Potential", "Cathodic Protection", "Li-ion Intercalation"],
                        "formulas": ["E = E° - (RT/nF) ln Q", "ΔG = -nFE"],
                        "practice_questions": 25
                    },
                    {
                        "name": "Organic Chemistry",
                        "subtopics": ["Reaction Mechanisms", "SN1 vs SN2", "Polymers", "Green Chemistry", "Engineering Materials"],
                        "important_points": ["Walden Inversion", "Nylon-6,6 Synthesis", "Atom Economy"],
                        "formulas": ["Atom Economy = (MW_product / MW_reactants) × 100%"],
                        "practice_questions": 20
                    }
                ]
            },
            {
                "code": "CS101",
                "name": "Programming in C",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "C Fundamentals",
                        "subtopics": ["Data Types", "Operators", "Control Structures", "Functions"],
                        "important_points": ["Type Casting", "Operator Precedence", "Storage Classes"],
                        "formulas": [],
                        "practice_questions": 25,
                        "code_examples": ["Hello World", "Calculator", "Prime Numbers"]
                    },
                    {
                        "name": "Pointers and Arrays",
                        "subtopics": ["Pointer Arithmetic", "Dynamic Memory", "2D Arrays", "Strings"],
                        "important_points": ["malloc/calloc/free", "Pointer to Pointer", "Array Decay"],
                        "formulas": [],
                        "practice_questions": 30,
                        "code_examples": ["String Manipulation", "Matrix Operations", "Linked List Basics"]
                    },
                    {
                        "name": "Structures and File Handling",
                        "subtopics": ["struct", "union", "typedef", "File I/O"],
                        "important_points": ["Structure Padding", "fopen/fread/fwrite", "Binary Files"],
                        "formulas": [],
                        "practice_questions": 20
                    }
                ]
            },
            {
                "code": "EE101",
                "name": "Basic Electrical Engineering",
                "credits": 3,
                "category": "Engineering Sciences",
                "type": "Core",
                "topics": [
                    {
                        "name": "DC Circuits",
                        "subtopics": ["Ohm's Law", "KCL", "KVL", "Network Theorems"],
                        "important_points": ["Thevenin", "Norton", "Superposition", "Maximum Power Transfer"],
                        "formulas": ["V = IR", "P = VI", "Rth = Voc/Isc"],
                        "practice_questions": 25
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 1 - SEMESTER 2 =====
    2: {
        "year": 1,
        "semester": 2,
        "courses": [
            {
                "code": "MA102",
                "name": "Engineering Mathematics II",
                "credits": 4,
                "category": "Basic Sciences",
                "type": "Core",
                "topics": [
                    {
                        "name": "Integral Calculus",
                        "subtopics": ["Definite Integrals", "Improper Integrals", "Beta Gamma Functions"],
                        "important_points": ["Integration by Parts", "Reduction Formulas"],
                        "formulas": ["∫ u dv = uv - ∫ v du", "Γ(n) = (n-1)!"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Differential Equations",
                        "subtopics": ["First Order DE", "Higher Order DE", "Series Solutions"],
                        "important_points": ["Exact Equations", "Integrating Factor", "Wronskian"],
                        "formulas": ["dy/dx + P(x)y = Q(x)", "IF = e^(∫P dx)"],
                        "practice_questions": 25
                    }
                ]
            },
            {
                "code": "CS102",
                "name": "Data Structures",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Arrays and Linked Lists",
                        "subtopics": ["Array Operations", "Singly Linked List", "Doubly Linked List", "Circular Lists"],
                        "important_points": ["Time Complexity", "Space Trade-offs", "Cache Locality"],
                        "formulas": ["Array Access: O(1)", "List Insert: O(n)"],
                        "practice_questions": 30,
                        "code_examples": ["Reverse Linked List", "Merge Two Lists", "Detect Cycle"]
                    },
                    {
                        "name": "Stacks and Queues",
                        "subtopics": ["Stack Implementation", "Queue Implementation", "Circular Queue", "Priority Queue"],
                        "important_points": ["LIFO vs FIFO", "Applications", "Monotonic Stack"],
                        "formulas": ["Push/Pop: O(1)", "Enqueue/Dequeue: O(1)"],
                        "practice_questions": 25,
                        "code_examples": ["Balanced Parentheses", "Infix to Postfix", "Queue using Stacks"]
                    },
                    {
                        "name": "Trees",
                        "subtopics": ["Binary Trees", "BST", "AVL Trees", "Tree Traversals"],
                        "important_points": ["Balance Factor", "Rotations", "Height Balance"],
                        "formulas": ["BF = height(left) - height(right)", "AVL: |BF| ≤ 1"],
                        "practice_questions": 35,
                        "code_examples": ["Inorder Traversal", "BST Insert", "AVL Rotation"]
                    },
                    {
                        "name": "Hashing",
                        "subtopics": ["Hash Functions", "Collision Resolution", "Open Addressing", "Chaining"],
                        "important_points": ["Load Factor", "Rehashing", "Universal Hashing"],
                        "formulas": ["α = n/m", "Expected Time: O(1)"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Graphs",
                        "subtopics": ["Graph Representation", "BFS", "DFS", "Shortest Paths"],
                        "important_points": ["Adjacency Matrix vs List", "Topological Sort", "Cycle Detection"],
                        "formulas": ["BFS/DFS: O(V+E)", "Dijkstra: O((V+E)logV)"],
                        "practice_questions": 40
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 2 - SEMESTER 3 =====
    3: {
        "year": 2,
        "semester": 3,
        "courses": [
            {
                "code": "CS201",
                "name": "Design and Analysis of Algorithms",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Asymptotic Analysis",
                        "subtopics": ["Big-O", "Big-Omega", "Big-Theta", "Master Theorem"],
                        "important_points": ["Growth Rates", "Recurrence Relations", "Amortized Analysis"],
                        "formulas": ["T(n) = aT(n/b) + f(n)", "log n < √n < n < n log n < n² < 2ⁿ"],
                        "practice_questions": 30
                    },
                    {
                        "name": "Divide and Conquer",
                        "subtopics": ["Merge Sort", "Quick Sort", "Binary Search", "Strassen's Matrix"],
                        "important_points": ["Pivot Selection", "Randomization", "Stability"],
                        "formulas": ["Merge Sort: O(n log n)", "Quick Sort Avg: O(n log n)"],
                        "practice_questions": 25
                    },
                    {
                        "name": "Greedy Algorithms",
                        "subtopics": ["Activity Selection", "Huffman Coding", "MST (Prim's, Kruskal's)"],
                        "important_points": ["Greedy Choice Property", "Optimal Substructure", "Matroid"],
                        "formulas": ["Kruskal: O(E log E)", "Prim: O((V+E) log V)"],
                        "practice_questions": 28
                    },
                    {
                        "name": "Dynamic Programming",
                        "subtopics": ["0/1 Knapsack", "LCS", "Matrix Chain", "Edit Distance"],
                        "important_points": ["Overlapping Subproblems", "Memoization vs Tabulation"],
                        "formulas": ["dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt[i]] + val[i])"],
                        "practice_questions": 35
                    },
                    {
                        "name": "Graph Algorithms",
                        "subtopics": ["Dijkstra", "Bellman-Ford", "Floyd-Warshall", "Topological Sort"],
                        "important_points": ["Negative Cycles", "All-Pairs", "DAG Properties"],
                        "formulas": ["Dijkstra: O((V+E)logV)", "Bellman-Ford: O(VE)", "Floyd: O(V³)"],
                        "practice_questions": 32
                    },
                    {
                        "name": "NP-Completeness",
                        "subtopics": ["P vs NP", "NP-Complete Problems", "Reductions"],
                        "important_points": ["SAT", "3-SAT", "Vertex Cover", "TSP"],
                        "formulas": [],
                        "practice_questions": 15
                    }
                ]
            },
            {
                "code": "CS202",
                "name": "Computer Organization and Architecture",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Number Systems",
                        "subtopics": ["Binary", "Octal", "Hexadecimal", "2's Complement"],
                        "important_points": ["Signed Representation", "Overflow Detection"],
                        "formulas": ["Range: -2^(n-1) to 2^(n-1)-1"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Computer Arithmetic",
                        "subtopics": ["Addition", "Subtraction", "Multiplication", "Division"],
                        "important_points": ["Booth's Algorithm", "Restoring Division"],
                        "formulas": [],
                        "practice_questions": 25
                    },
                    {
                        "name": "Instruction Set Architecture",
                        "subtopics": ["RISC vs CISC", "Addressing Modes", "Instruction Formats"],
                        "important_points": ["Register-Register", "Load-Store", "Immediate"],
                        "formulas": [],
                        "practice_questions": 22
                    },
                    {
                        "name": "Pipelining",
                        "subtopics": ["Hazards", "Forwarding", "Branch Prediction"],
                        "important_points": ["Data Hazards", "Control Hazards", "Structural Hazards"],
                        "formulas": ["Speedup = n / (1 + (n-1) * stall_ratio)"],
                        "practice_questions": 28
                    },
                    {
                        "name": "Memory Hierarchy",
                        "subtopics": ["Cache Memory", "Virtual Memory", "TLB"],
                        "important_points": ["Cache Mapping", "Replacement Policies", "Page Tables"],
                        "formulas": ["AMAT = Hit_Time + Miss_Rate × Miss_Penalty"],
                        "practice_questions": 30
                    }
                ]
            },
            {
                "code": "CS203",
                "name": "Operating Systems",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Process Management",
                        "subtopics": ["Process States", "PCB", "Context Switching", "IPC"],
                        "important_points": ["Process vs Thread", "Shared Memory", "Message Passing"],
                        "formulas": [],
                        "practice_questions": 25
                    },
                    {
                        "name": "CPU Scheduling",
                        "subtopics": ["FCFS", "SJF", "Priority", "Round Robin", "MLFQ"],
                        "important_points": ["Turnaround Time", "Waiting Time", "Response Time"],
                        "formulas": ["TAT = CT - AT", "WT = TAT - BT"],
                        "practice_questions": 35
                    },
                    {
                        "name": "Process Synchronization",
                        "subtopics": ["Critical Section", "Semaphores", "Monitors", "Deadlock"],
                        "important_points": ["Mutual Exclusion", "Progress", "Bounded Waiting"],
                        "formulas": [],
                        "practice_questions": 30
                    },
                    {
                        "name": "Deadlock",
                        "subtopics": ["Coffman Conditions", "Deadlock Prevention", "Detection", "Banker's Algorithm"],
                        "important_points": ["Resource Allocation Graph", "Safe State"],
                        "formulas": ["Need = Max - Allocation"],
                        "practice_questions": 28
                    },
                    {
                        "name": "Memory Management",
                        "subtopics": ["Paging", "Segmentation", "Virtual Memory"],
                        "important_points": ["Page Table", "TLB", "Page Replacement"],
                        "formulas": ["Physical Address = Frame_No × Page_Size + Offset"],
                        "practice_questions": 32
                    },
                    {
                        "name": "File Systems",
                        "subtopics": ["File Operations", "Directory Structure", "Disk Scheduling"],
                        "important_points": ["FCFS", "SSTF", "SCAN", "C-SCAN"],
                        "formulas": [],
                        "practice_questions": 20
                    }
                ]
            },
            {
                "code": "CS204",
                "name": "Database Management Systems",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "ER Modeling",
                        "subtopics": ["Entities", "Attributes", "Relationships", "ER Diagrams"],
                        "important_points": ["Cardinality", "Participation", "Weak Entities"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Relational Model",
                        "subtopics": ["Relations", "Keys", "Constraints", "Relational Algebra"],
                        "important_points": ["Super Key", "Candidate Key", "Primary Key", "Foreign Key"],
                        "formulas": ["σ (select)", "π (project)", "⨝ (join)"],
                        "practice_questions": 28
                    },
                    {
                        "name": "SQL",
                        "subtopics": ["DDL", "DML", "Joins", "Aggregates", "Subqueries"],
                        "important_points": ["INNER JOIN", "GROUP BY", "HAVING", "EXISTS"],
                        "formulas": [],
                        "practice_questions": 40
                    },
                    {
                        "name": "Normalization",
                        "subtopics": ["1NF", "2NF", "3NF", "BCNF", "Functional Dependencies"],
                        "important_points": ["Partial Dependency", "Transitive Dependency", "Lossless Join"],
                        "formulas": ["X → Y (FD)", "Armstrong's Axioms"],
                        "practice_questions": 30
                    },
                    {
                        "name": "Transactions",
                        "subtopics": ["ACID Properties", "Concurrency Control", "Locking", "Isolation Levels"],
                        "important_points": ["2PL", "Timestamp Ordering", "Serializability"],
                        "formulas": [],
                        "practice_questions": 25
                    },
                    {
                        "name": "Indexing",
                        "subtopics": ["B-Tree", "B+ Tree", "Hashing"],
                        "important_points": ["Dense vs Sparse", "Primary vs Secondary", "Clustered"],
                        "formulas": ["B+ Tree Order: ceil(n/2)"],
                        "practice_questions": 22
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 2 - SEMESTER 4 =====
    4: {
        "year": 2,
        "semester": 4,
        "courses": [
            {
                "code": "CS301",
                "name": "Computer Networks",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Network Fundamentals",
                        "subtopics": ["OSI Model", "TCP/IP Model", "Network Types"],
                        "important_points": ["7 Layers", "Encapsulation", "Protocol Stack"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Data Link Layer",
                        "subtopics": ["Framing", "Error Detection", "MAC Protocols"],
                        "important_points": ["CRC", "Hamming Code", "CSMA/CD", "CSMA/CA"],
                        "formulas": ["Efficiency = 1 / (1 + 2a)", "a = Propagation Time / Transmission Time"],
                        "practice_questions": 30
                    },
                    {
                        "name": "Network Layer",
                        "subtopics": ["IP Addressing", "Subnetting", "Routing Algorithms"],
                        "important_points": ["Classful vs Classless", "CIDR", "Distance Vector", "Link State"],
                        "formulas": ["Subnet: 2^n hosts", "Routing: Bellman-Ford, Dijkstra"],
                        "practice_questions": 35
                    },
                    {
                        "name": "Transport Layer",
                        "subtopics": ["TCP", "UDP", "Flow Control", "Congestion Control"],
                        "important_points": ["3-Way Handshake", "Sliding Window", "AIMD"],
                        "formulas": ["RTT", "Timeout = EstimatedRTT + 4 × DevRTT"],
                        "practice_questions": 28
                    },
                    {
                        "name": "Application Layer",
                        "subtopics": ["HTTP", "DNS", "SMTP", "FTP"],
                        "important_points": ["Request/Response", "DNS Hierarchy", "Email Protocols"],
                        "formulas": [],
                        "practice_questions": 22
                    }
                ]
            },
            {
                "code": "CS302",
                "name": "Object-Oriented Programming",
                "credits": 3,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "OOP Concepts",
                        "subtopics": ["Classes", "Objects", "Encapsulation", "Abstraction"],
                        "important_points": ["Access Modifiers", "Constructors", "Destructors"],
                        "formulas": [],
                        "practice_questions": 25
                    },
                    {
                        "name": "Inheritance and Polymorphism",
                        "subtopics": ["Inheritance Types", "Method Overriding", "Virtual Functions"],
                        "important_points": ["Is-A Relationship", "Dynamic Binding", "Abstract Classes"],
                        "formulas": [],
                        "practice_questions": 30
                    }
                ]
            },
            {
                "code": "CS303",
                "name": "Theory of Computation",
                "credits": 3,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Automata Theory",
                        "subtopics": ["DFA", "NFA", "Regular Expressions", "NFA to DFA"],
                        "important_points": ["Finite Automata", "State Transitions", "Equivalence"],
                        "formulas": [],
                        "practice_questions": 28
                    },
                    {
                        "name": "Context-Free Grammars",
                        "subtopics": ["CFG", "PDA", "Chomsky Normal Form"],
                        "important_points": ["Parse Trees", "Ambiguity", "CFG to PDA"],
                        "formulas": [],
                        "practice_questions": 25
                    },
                    {
                        "name": "Turing Machines",
                        "subtopics": ["TM Definition", "Variants", "Church-Turing Thesis"],
                        "important_points": ["Decidability", "Halting Problem", "Undecidability"],
                        "formulas": [],
                        "practice_questions": 20
                    }
                ]
            },
            {
                "code": "CS304",
                "name": "Software Engineering",
                "credits": 3,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "SDLC Models",
                        "subtopics": ["Waterfall", "Agile", "Scrum", "Spiral"],
                        "important_points": ["Phases", "Iterative Development", "Sprints"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Requirements Engineering",
                        "subtopics": ["Functional Requirements", "Non-Functional", "SRS"],
                        "important_points": ["Elicitation", "Analysis", "Validation"],
                        "formulas": [],
                        "practice_questions": 18
                    },
                    {
                        "name": "Design",
                        "subtopics": ["UML Diagrams", "Design Patterns", "Architecture"],
                        "important_points": ["Class Diagram", "Sequence Diagram", "MVC"],
                        "formulas": [],
                        "practice_questions": 25
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 3 - SEMESTER 5 =====
    5: {
        "year": 3,
        "semester": 5,
        "courses": [
            {
                "code": "CS401",
                "name": "Artificial Intelligence",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Search Algorithms",
                        "subtopics": ["BFS", "DFS", "A*", "Hill Climbing"],
                        "important_points": ["Heuristic Functions", "Admissibility", "Optimality"],
                        "formulas": ["f(n) = g(n) + h(n)"],
                        "practice_questions": 25
                    },
                    {
                        "name": "Knowledge Representation",
                        "subtopics": ["Propositional Logic", "First-Order Logic", "Inference"],
                        "important_points": ["Resolution", "Forward/Backward Chaining"],
                        "formulas": [],
                        "practice_questions": 22
                    },
                    {
                        "name": "Machine Learning Basics",
                        "subtopics": ["Supervised Learning", "Unsupervised Learning", "Classification"],
                        "important_points": ["Training vs Testing", "Overfitting", "Cross-Validation"],
                        "formulas": [],
                        "practice_questions": 28
                    }
                ]
            },
            {
                "code": "CS402",
                "name": "Machine Learning",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Regression",
                        "subtopics": ["Linear Regression", "Logistic Regression", "Gradient Descent"],
                        "important_points": ["Cost Function", "Learning Rate", "Convergence"],
                        "formulas": ["J(θ) = (1/2m) Σ(h(x) - y)²", "θ = θ - α∇J(θ)"],
                        "practice_questions": 30
                    },
                    {
                        "name": "Classification",
                        "subtopics": ["Decision Trees", "SVM", "Naive Bayes", "KNN"],
                        "important_points": ["Information Gain", "Kernel Trick", "Bayes Theorem"],
                        "formulas": ["Entropy H(S) = -Σ p log p", "SVM: max margin"],
                        "practice_questions": 35
                    },
                    {
                        "name": "Clustering",
                        "subtopics": ["K-Means", "Hierarchical", "DBSCAN"],
                        "important_points": ["Elbow Method", "Silhouette Score", "Dendrograms"],
                        "formulas": ["Euclidean Distance", "Cosine Similarity"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Neural Networks",
                        "subtopics": ["Perceptron", "Backpropagation", "Activation Functions"],
                        "important_points": ["Weights", "Biases", "Loss Functions"],
                        "formulas": ["ReLU: max(0, x)", "Sigmoid: 1/(1+e^-x)"],
                        "practice_questions": 28
                    }
                ]
            },
            {
                "code": "CS403",
                "name": "Web Technologies",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "HTML & CSS",
                        "subtopics": ["HTML5 Tags", "CSS Selectors", "Responsive Design", "Flexbox/Grid"],
                        "important_points": ["Semantic HTML", "Box Model", "Media Queries"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "JavaScript",
                        "subtopics": ["ES6", "DOM Manipulation", "Async/Promises", "Fetch API"],
                        "important_points": ["Arrow Functions", "Closures", "Event Loop"],
                        "formulas": [],
                        "practice_questions": 30
                    },
                    {
                        "name": "Backend Development",
                        "subtopics": ["Node.js", "Express", "REST APIs", "MongoDB"],
                        "important_points": ["Routing", "Middleware", "CRUD Operations"],
                        "formulas": [],
                        "practice_questions": 25
                    }
                ]
            },
            {
                "code": "CS404",
                "name": "Cyber Security",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Cryptography",
                        "subtopics": ["Symmetric Encryption", "Asymmetric Encryption", "Hashing"],
                        "important_points": ["AES", "RSA", "SHA-256", "Digital Signatures"],
                        "formulas": ["C = E(K, P)", "P = D(K, C)"],
                        "practice_questions": 25
                    },
                    {
                        "name": "Network Security",
                        "subtopics": ["Firewalls", "IDS/IPS", "VPN", "SSL/TLS"],
                        "important_points": ["Packet Filtering", "Deep Packet Inspection"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Web Security",
                        "subtopics": ["SQL Injection", "XSS", "CSRF", "OWASP Top 10"],
                        "important_points": ["Input Validation", "Parameterized Queries"],
                        "formulas": [],
                        "practice_questions": 22
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 3 - SEMESTER 6 =====
    6: {
        "year": 3,
        "semester": 6,
        "courses": [
            {
                "code": "CS501",
                "name": "Compiler Design",
                "credits": 4,
                "category": "Professional Core",
                "type": "Core",
                "topics": [
                    {
                        "name": "Lexical Analysis",
                        "subtopics": ["Tokens", "Lexemes", "Regular Expressions", "DFA"],
                        "important_points": ["Lexer", "Token Generation"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Syntax Analysis",
                        "subtopics": ["Parsing", "Top-Down", "Bottom-Up", "LR Parsers"],
                        "important_points": ["Parse Trees", "Shift-Reduce", "SLR, CLR, LALR"],
                        "formulas": [],
                        "practice_questions": 28
                    }
                ]
            },
            {
                "code": "CS502",
                "name": "Cloud Computing",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Cloud Fundamentals",
                        "subtopics": ["IaaS", "PaaS", "SaaS", "Virtualization"],
                        "important_points": ["Hypervisors", "Containers", "Docker"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "AWS/Azure Basics",
                        "subtopics": ["EC2", "S3", "Lambda", "Load Balancing"],
                        "important_points": ["Auto Scaling", "CDN", "Regions/Zones"],
                        "formulas": [],
                        "practice_questions": 25
                    }
                ]
            },
            {
                "code": "CS503",
                "name": "Data Science",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Data Preprocessing",
                        "subtopics": ["Data Cleaning", "Transformation", "Normalization"],
                        "important_points": ["Missing Values", "Outliers", "Feature Scaling"],
                        "formulas": ["MinMax: (x-min)/(max-min)", "Z-score: (x-μ)/σ"],
                        "practice_questions": 20
                    },
                    {
                        "name": "Exploratory Data Analysis",
                        "subtopics": ["Visualization", "Statistical Analysis", "Correlation"],
                        "important_points": ["Pandas", "Matplotlib", "Seaborn"],
                        "formulas": ["Pearson r", "Spearman ρ"],
                        "practice_questions": 25
                    }
                ]
            }
        ]
    },
    
    # ===== YEAR 4 - SEMESTER 7 =====
    7: {
        "year": 4,
        "semester": 7,
        "courses": [
            {
                "code": "CS601",
                "name": "Deep Learning",
                "credits": 4,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Deep Neural Networks",
                        "subtopics": ["MLP", "Backpropagation", "Optimization", "Regularization"],
                        "important_points": ["Dropout", "Batch Normalization", "Adam Optimizer"],
                        "formulas": ["Loss: Cross-Entropy", "Update: Adam"],
                        "practice_questions": 25
                    },
                    {
                        "name": "Convolutional Neural Networks",
                        "subtopics": ["Convolution", "Pooling", "CNN Architectures"],
                        "important_points": ["LeNet", "AlexNet", "ResNet", "Transfer Learning"],
                        "formulas": ["Output Size: (W-F+2P)/S + 1"],
                        "practice_questions": 28
                    },
                    {
                        "name": "Recurrent Neural Networks",
                        "subtopics": ["RNN", "LSTM", "GRU", "Sequence Models"],
                        "important_points": ["Vanishing Gradient", "Bidirectional RNN"],
                        "formulas": [],
                        "practice_questions": 22
                    }
                ]
            },
            {
                "code": "CS602",
                "name": "Big Data Analytics",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Hadoop Ecosystem",
                        "subtopics": ["HDFS", "MapReduce", "YARN", "Hive"],
                        "important_points": ["Distributed Storage", "Fault Tolerance"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Spark",
                        "subtopics": ["RDD", "DataFrames", "Spark SQL"],
                        "important_points": ["In-Memory Processing", "Lazy Evaluation"],
                        "formulas": [],
                        "practice_questions": 18
                    }
                ]
            },
            {
                "code": "CS603",
                "name": "Distributed Systems",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Distributed Computing Fundamentals",
                        "subtopics": ["CAP Theorem", "Consistency Models", "Consensus"],
                        "important_points": ["Paxos", "Raft", "2PC", "3PC"],
                        "formulas": [],
                        "practice_questions": 22
                    }
                ]
            },
            {
                "code": "CS699",
                "name": "Major Project (Phase 1)",
                "credits": 8,
                "category": "Project",
                "type": "Core",
                "topics": []
            }
        ]
    },
    
    # ===== YEAR 4 - SEMESTER 8 =====
    8: {
        "year": 4,
        "semester": 8,
        "courses": [
            {
                "code": "CS701",
                "name": "Natural Language Processing",
                "credits": 3,
                "category": "Professional Elective",
                "type": "Elective",
                "topics": [
                    {
                        "name": "Text Processing",
                        "subtopics": ["Tokenization", "Stemming", "Lemmatization", "POS Tagging"],
                        "important_points": ["NLTK", "spaCy", "Stop Words"],
                        "formulas": [],
                        "practice_questions": 20
                    },
                    {
                        "name": "Word Embeddings",
                        "subtopics": ["Word2Vec", "GloVe", "FastText"],
                        "important_points": ["CBOW", "Skip-Gram", "Cosine Similarity"],
                        "formulas": [],
                        "practice_questions": 18
                    },
                    {
                        "name": "Transformers",
                        "subtopics": ["Attention Mechanism", "BERT", "GPT"],
                        "important_points": ["Self-Attention", "Multi-Head Attention"],
                        "formulas": ["Attention(Q,K,V) = softmax(QKᵀ/√d)V"],
                        "practice_questions": 22
                    }
                ]
            },
            {
                "code": "CS702",
                "name": "Interview Preparation & Placement",
                "credits": 2,
                "category": "Skill Development",
                "type": "Core",
                "topics": [
                    {
                        "name": "Data Structures & Algorithms Interview",
                        "subtopics": ["Array Problems", "String Problems", "Tree Problems", "Graph Problems"],
                        "important_points": ["Two Pointers", "Sliding Window", "Dynamic Programming Patterns"],
                        "formulas": [],
                        "practice_questions": 100
                    },
                    {
                        "name": "System Design",
                        "subtopics": ["Scalability", "Load Balancing", "Caching", "Database Design"],
                        "important_points": ["CAP Theorem", "Microservices", "API Design"],
                        "formulas": [],
                        "practice_questions": 30
                    },
                    {
                        "name": "Behavioral & HR Questions",
                        "subtopics": ["Tell Me About Yourself", "Strengths/Weaknesses", "Leadership"],
                        "important_points": ["STAR Method"],
                        "formulas": [],
                        "practice_questions": 25
                    }
                ]
            },
            {
                "code": "CS799",
                "name": "Major Project (Phase 2)",
                "credits": 10,
                "category": "Project",
                "type": "Core",
                "topics": []
            }
        ]
    }
}

def get_all_semesters():
    """Return list of all semester numbers"""
    return list(FULL_BTECH_CURRICULUM.keys())

def get_semester_courses(semester: int):
    """Get all courses for a given semester"""
    return FULL_BTECH_CURRICULUM.get(semester, {}).get("courses", [])

def get_course_by_code(code: str):
    """Find a course by its code"""
    for sem_data in FULL_BTECH_CURRICULUM.values():
        for course in sem_data.get("courses", []):
            if course["code"] == code:
                return course
    return None

def get_all_topics_for_semester(semester: int):
    """Get all topics across all courses in a semester"""
    topics = []
    courses = get_semester_courses(semester)
    for course in courses:
        for topic in course.get("topics", []):
            topics.append({
                **topic,
                "course_code": course["code"],
                "course_name": course["name"],
                "semester": semester
            })
    return topics

def search_topics(keyword: str):
    """Search topics by keyword"""
    results = []
    for sem_num, sem_data in FULL_BTECH_CURRICULUM.items():
        for course in sem_data.get("courses", []):
            for topic in course.get("topics", []):
                if keyword.lower() in topic["name"].lower():
                    results.append({
                        **topic,
                        "course_code": course["code"],
                        "course_name": course["name"],
                        "semester": sem_num
                    })
    return results
