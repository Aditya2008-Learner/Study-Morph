"""
Comprehensive Study Content Repository for B.Tech CSE
Contains notes, formulas, MCQs, examples, flashcards, and practice questions per topic
"""

# ===== YEAR 1 - SEMESTER 1 STUDY CONTENT =====

YEAR1_SEM1_CONTENT = {
    "CS101": {
        "c_fundamentals": {
            "title": "C Fundamentals",
            "summary": "Fundamental syntax, control structures, data types, operator precedence, functions, and recursion in C programming.",
            "key_points": [
                "C is a procedural, statically-typed compiled programming language",
                "Primitive data types include char (1B), int (4B), float (4B), double (8B)",
                "Control flow statements: if-else, switch-case, for, while, and do-while loops",
                "Functions pass arguments by value by default in C",
                "Storage classes define variable lifetime and visibility: auto, register, static, and extern"
            ],
            "formulas": [
                {
                    "name": "Operator Precedence",
                    "latex": "$$() \\rightarrow [] \\rightarrow . \\rightarrow * \\rightarrow + \\rightarrow == \\rightarrow \\&\\& \\rightarrow ||$$",
                    "explanation": "Standard evaluation precedence order of fundamental C operators"
                }
            ],
            "examples": [
                {
                    "question": "What is the output of printf('%d', 5/2); in C?",
                    "answer": "2",
                    "steps": ["Integer division truncates the fractional part towards zero: 5/2 = 2"]
                }
            ],
            "mcqs": [
                {"question": "Which format specifier is used for double data type in printf?", "options": ["%d", "%f", "%lf", "%s"], "correct": 2},
                {"question": "Which storage class preserves variable value between function calls?", "options": ["auto", "register", "static", "extern"], "correct": 2}
            ],
            "practice_questions": [
                "Write a C program to check whether a given integer is a prime number.",
                "Explain the difference between pre-increment and post-increment operators in C."
            ],
            "flashcards": [
                {"front": "What is the difference between call by value and call by reference in C?", "back": "Call by value passes copies of variables; call by reference passes memory addresses using pointers.", "hint": "Passing addresses"},
                {"front": "What are the 4 storage classes in C?", "back": "auto, register, static, and extern", "hint": "Variable lifetime & scope"},
                {"front": "What is the size of standard integer pointer on 64-bit architecture?", "back": "8 bytes (64 bits) regardless of the data type it points to.", "hint": "Address bus width"}
            ],
            "viva_questions": [
                "What happens if a recursive function does not have a base case?",
                "Explain the role of the header file stdio.h in C."
            ],
            "difficulty": "Introductory"
        },
        "pointers": {
            "title": "Pointers and Memory Management",
            "summary": "Pointers store memory addresses and enable dynamic memory allocation (malloc, calloc, realloc, free), array indexing, and pointer arithmetic in C.",
            "key_points": [
                "Pointers store memory addresses of other variables",
                "Dereference operator * accesses the value at the address held by pointer",
                "Address-of operator & retrieves the physical memory address of a variable",
                "malloc() allocates uninitialized heap memory, calloc() initializes to zero",
                "Always call free() on allocated memory blocks to prevent memory leaks"
            ],
            "formulas": [
                {
                    "name": "Pointer Arithmetic",
                    "latex": "$$p + i = \\text{Address}(p) + (i \\times \\text{sizeof}(*p))$$",
                    "explanation": "Pointer offset increments by the byte size of the pointed data type"
                }
            ],
            "examples": [
                {
                    "question": "If int* ptr = (int*)malloc(5 * sizeof(int)); what does ptr hold?",
                    "answer": "The base address of the 20-byte allocated heap block",
                    "steps": ["malloc allocates 5 * 4 = 20 bytes", "Returns void pointer cast to int* pointing to first byte"]
                }
            ],
            "mcqs": [
                {"question": "What does free(ptr) do in C?", "options": ["Deletes ptr variable", "Releases allocated heap memory", "Sets ptr to NULL", "Erases RAM"], "correct": 1},
                {"question": "What is a pointer that has not been initialized called?", "options": ["Null pointer", "Wild pointer", "Dangling pointer", "Void pointer"], "correct": 1}
            ],
            "practice_questions": [
                "Write a C program to swap two numbers using pointer references.",
                "Explain the difference between malloc() and calloc() with syntax examples."
            ],
            "flashcards": [
                {"front": "What is a dangling pointer in C?", "back": "A pointer pointing to a memory location that has already been deallocated/freed.", "hint": "Deallocated memory"},
                {"front": "What is the key difference between malloc() and calloc()?", "back": "malloc() leaves allocated memory uninitialized (garbage); calloc() initializes all bytes to zero.", "hint": "Memory initialization"},
                {"front": "What is array name decay in C?", "back": "An array identifier automatically decays into a pointer to its first element in expressions.", "hint": "Array to pointer conversion"}
            ],
            "viva_questions": [
                "What is a memory leak and how do you prevent it?",
                "What is a void pointer and when is it useful?"
            ],
            "difficulty": "Intermediate"
        },
        "file_handling": {
            "title": "Structures and File Handling",
            "summary": "Structures group heterogeneous data types together. File I/O operations in C use standard file streams (fopen, fread, fwrite, fprintf, fscanf, fclose) for persistent storage.",
            "key_points": [
                "struct groups related variables of different data types under one identifier",
                "Arrow operator -> accesses struct members through pointer to structure",
                "Standard file modes: r (read), w (write/truncate), a (append), and binary b modes",
                "fopen() returns a valid FILE* stream pointer or NULL on failure",
                "fclose() flushes internal write buffers and releases file descriptors"
            ],
            "formulas": [
                {
                    "name": "Structure Memory Size",
                    "latex": "$$\\text{sizeof}(\\text{struct}) \\ge \\sum \\text{sizeof}(\\text{members})$$",
                    "explanation": "Actual struct size is equal to or greater than member sum due to memory alignment padding"
                }
            ],
            "examples": [
                {
                    "question": "How do you open a file for reading in binary mode?",
                    "answer": "FILE *fp = fopen('data.bin', 'rb');",
                    "steps": ["fopen takes filename and mode string 'rb' for read binary"]
                }
            ],
            "mcqs": [
                {"question": "Which function is used to close an open file stream in C?", "options": ["close()", "fclose()", "file_close()", "endfile()"], "correct": 1},
                {"question": "What is the return value of fopen() on failure?", "options": ["-1", "0", "NULL", "EOF"], "correct": 2}
            ],
            "practice_questions": [
                "Write a C program to copy the contents of one text file into another file.",
                "Define a struct Student with roll_no, name, and marks and write functions to read/write."
            ],
            "flashcards": [
                {"front": "What is the difference between struct and union in C?", "back": "In struct, each member gets its own memory; in union, all members share the same memory location (sized to largest member).", "hint": "Shared vs separate memory"},
                {"front": "What does fopen() return when a file cannot be opened?", "back": "NULL pointer", "hint": "Error return value"},
                {"front": "What is structure padding in C?", "back": "Extra bytes inserted between struct members by compiler to satisfy processor memory alignment constraints.", "hint": "Memory alignment"}
            ],
            "viva_questions": [
                "Explain the difference between text mode and binary mode file access in C.",
                "Why is structure padding necessary for CPU performance?"
            ],
            "difficulty": "Intermediate"
        }
    },
    "MA101": {
        "matrices_and_determinants": {
            "title": "Matrices and Determinants",
            "summary": "Matrices are rectangular arrays of numbers used to represent linear transformations and systems of linear equations. Determinants are scalar values computed from square matrices.",
            "key_points": [
                "Matrix addition requires same dimensions",
                "Matrix multiplication is associative but not commutative",
                "Determinant exists only for square matrices",
                "det(AB) = det(A) × det(B)",
                "If det(A) ≠ 0, matrix A is invertible"
            ],
            "formulas": [
                {
                    "name": "Determinant of 2×2 Matrix",
                    "latex": "$$\\det\\begin{bmatrix}a & b \\\\ c & d\\end{bmatrix} = ad - bc$$",
                    "explanation": "Cross-multiply and subtract for 2×2 matrices"
                },
                {
                    "name": "Cramer's Rule",
                    "latex": "$$x_i = \\frac{\\det(A_i)}{\\det(A)}$$",
                    "explanation": "Solve linear systems using determinants when det(A) ≠ 0"
                },
                {
                    "name": "Inverse of 2×2 Matrix",
                    "latex": "$$A^{-1} = \\frac{1}{ad-bc}\\begin{bmatrix}d & -b \\\\ -c & a\\end{bmatrix}$$",
                    "explanation": "Swap diagonal elements, change sign of off-diagonal, divide by determinant"
                }
            ],
            "examples": [
                {
                    "question": "Find determinant of [[3, 2], [1, 4]]",
                    "answer": "det = 3×4 - 2×1 = 12 - 2 = 10",
                    "steps": ["Multiply diagonal elements: 3×4 = 12", "Multiply anti-diagonal: 2×1 = 2", "Subtract: 12 - 2 = 10"]
                },
                {
                    "question": "Solve using Cramer's Rule: 2x + 3y = 8, x - y = 1",
                    "answer": "x = 11/5, y = 6/5",
                    "steps": ["A = [[2,3],[1,-1]], det(A) = -5", "Ax = [[8,3],[1,-1]], det(Ax) = -11", "Ay = [[2,8],[1,1]], det(Ay) = -6", "x = -11/-5 = 11/5, y = -6/-5 = 6/5"]
                }
            ],
            "mcqs": [
                {"question": "For which type of matrices is determinant defined?", "options": ["Rectangular", "Square", "Column", "Row"], "correct": 1},
                {"question": "If det(A) = 0, the matrix A is:", "options": ["Invertible", "Singular", "Non-singular", "Orthogonal"], "correct": 1},
                {"question": "Cramer's Rule can be applied when:", "options": ["det(A) = 0", "det(A) ≠ 0", "A is rectangular", "A has no inverse"], "correct": 1},
                {"question": "The inverse of a matrix exists if and only if:", "options": ["det(A) > 0", "det(A) < 0", "det(A) = 0", "det(A) ≠ 0"], "correct": 3}
            ],
            "practice_questions": [
                "Find determinant of [[5, 3], [2, 7]]",
                "Solve: 3x + 2y = 12, 4x - y = 5 using Cramer's Rule",
                "Find inverse of [[4, 7], [2, 6]]",
                "Explain why det(AB) = det(A)det(B) holds for square matrices"
            ],
            "flashcards": [
                {"front": "What is the condition for a matrix to be invertible?", "back": "Determinant must be non-zero (det(A) ≠ 0)", "hint": "Non-singular matrix"},
                {"front": "State Cramer's Rule formula for solving linear systems", "back": "x_i = det(A_i) / det(A) where A_i replaces column i with constants", "hint": "Using determinants"},
                {"front": "What is det(AB) in terms of det(A) and det(B)?", "back": "det(AB) = det(A) × det(B)", "hint": "Product property"}
            ],
            "viva_questions": [
                "What is the geometric interpretation of determinant?",
                "Explain the relationship between matrix rank and determinant.",
                "Why is Cramer's Rule computationally expensive for large systems?"
            ]
        },
        "eigenvalues_eigenvectors": {
            "title": "Eigenvalues and Eigenvectors",
            "summary": "Eigenvalues and eigenvectors reveal fundamental properties of linear transformations. An eigenvector of a matrix is a vector that changes by only a scalar factor when the linear transformation is applied.",
            "key_points": [
                "Eigenvectors remain in the same direction after transformation",
                "Eigenvalue is the scaling factor for the eigenvector",
                "Sum of eigenvalues = trace of matrix",
                "Product of eigenvalues = determinant of matrix"
            ],
            "formulas": [
                {
                    "name": "Eigenvalue Equation",
                    "latex": "$$A\\mathbf{v} = \\lambda\\mathbf{v}$$",
                    "explanation": "Matrix A transforms eigenvector v by scalar λ"
                },
                {
                    "name": "Characteristic Equation",
                    "latex": "$$\\det(A - \\lambda I) = 0$$",
                    "explanation": "Solve for λ to find eigenvalues"
                },
                {
                    "name": "Cayley-Hamilton Theorem",
                    "latex": "$$p(A) = 0$$",
                    "explanation": "Every square matrix satisfies its own characteristic equation"
                }
            ],
            "examples": [
                {
                    "question": "Find eigenvalues of [[4, 1], [2, 3]]",
                    "answer": "λ = 5, 2",
                    "steps": ["Characteristic equation: det([[4-λ, 1], [2, 3-λ]]) = 0", "(4-λ)(3-λ) - 2 = 0", "λ² - 7λ + 10 = 0", "(λ-5)(λ-2) = 0", "λ = 5, 2"]
                }
            ],
            "mcqs": [
                {"question": "Eigenvectors remain in the same direction after transformation. True/False?", "options": ["True", "False"], "correct": 0},
                {"question": "The product of all eigenvalues equals:", "options": ["Trace of matrix", "Determinant of matrix", "Rank of matrix", "Frobenius norm"], "correct": 1},
                {"question": "Cayley-Hamilton theorem states:", "options": ["A = A⁻¹", "p(A) = 0", "det(A) = 1", "A² = I"], "correct": 1}
            ]
        }
    },
    "PH101": {
        "wave_optics": {
            "title": "Wave Optics",
            "summary": "Wave optics explains optical phenomena using the wave theory of light, including interference, diffraction, and polarization that cannot be explained by ray optics.",
            "key_points": [
                "Interference occurs when coherent waves superpose",
                "Diffraction is bending of light around obstacles",
                "Polarization shows light is a transverse wave",
                "Coherent sources have constant phase difference"
            ],
            "formulas": [
                {
                    "name": "Young's Double Slit",
                    "latex": "$$y = \\frac{\\lambda D}{d}$$",
                    "explanation": "Fringe width where λ=wavelength, D=distance to screen, d=slit separation"
                },
                {
                    "name": "Malus Law",
                    "latex": "$$I = I_0 \\cos^2\\theta$$",
                    "explanation": "Intensity after polarizer at angle θ"
                },
                {
                    "name": "Thin Film Interference",
                    "latex": "$$2nt = m\\lambda \\text{ (constructive)}$$",
                    "explanation": "Condition for bright fringes in thin films"
                }
            ]
        },
        "mechanics": {
            "title": "Mechanics",
            "summary": "Classical Newtonian mechanics covering translational kinematics, Newton's laws, work-energy theorem, rotational dynamics, moment of inertia, and harmonic oscillations.",
            "key_points": [
                "Newton's three laws of motion describe the relationship between forces and kinematics",
                "Work-Energy Theorem states that net work done equals change in kinetic energy: W = ΔK",
                "Moment of inertia represents rotational inertia: I = ∫r² dm",
                "Torque relates to angular acceleration via τ = Iα",
                "Simple Harmonic Motion satisfies d²x/dt² + ω₀²x = 0 with period T = 2π/ω₀"
            ],
            "formulas": [
                {
                    "name": "Work-Energy Theorem",
                    "latex": "$$W = \\int \\vec{F} \\cdot d\\vec{r} = \\Delta K = \\frac{1}{2}mv_f^2 - \\frac{1}{2}mv_i^2$$",
                    "explanation": "Net work done on a particle equals the change in kinetic energy"
                },
                {
                    "name": "Moment of Inertia",
                    "latex": "$$I = \\int r^2\\,dm = \\sum m_i r_i^2$$",
                    "explanation": "Rotational mass equivalent about an axis of rotation"
                },
                {
                    "name": "Damped Harmonic Motion",
                    "latex": "$$\\frac{d^2x}{dt^2} + 2\\gamma \\frac{dx}{dt} + \\omega_0^2 x = 0$$",
                    "explanation": "Equation of motion for oscillator with linear damping γ = b/(2m)"
                }
            ],
            "examples": [
                {
                    "question": "Find the moment of inertia of a solid cylinder of mass 2 kg and radius 0.5 m about its central axis.",
                    "answer": "0.25 kg·m²",
                    "steps": ["I = (1/2) M R²", "I = 0.5 × 2 × (0.5)² = 0.25 kg·m²"]
                }
            ],
            "mcqs": [
                {"question": "What is the moment of inertia of a uniform thin rod of length L and mass M about its center perpendicular to its length?", "options": ["ML²/12", "ML²/3", "ML²/2", "ML²/4"], "correct": 0},
                {"question": "In critical damping, how does the damping coefficient γ relate to natural frequency ω₀?", "options": ["γ < ω₀", "γ = ω₀", "γ > ω₀", "γ = 0"], "correct": 1}
            ],
            "practice_questions": [
                "Derive the work-energy theorem for a particle moving under a conservative variable force.",
                "Calculate the period of oscillation for a physical pendulum of moment of inertia I and distance d to center of mass."
            ],
            "flashcards": [
                {"front": "State the Work-Energy Theorem.", "back": "The net work done by all forces acting on a body equals the change in its kinetic energy: W = ΔK.", "hint": "Kinetic energy change"},
                {"front": "What is the condition for critical damping?", "back": "Damping factor γ = ω₀ (damping coefficient b = 2√(km)), returning system to equilibrium in minimum time without oscillation.", "hint": "No oscillation, fastest decay"},
                {"front": "What is the Parallel Axis Theorem?", "back": "I = I_cm + M d², where I_cm is moment of inertia about center of mass and d is the distance between axes.", "hint": "Shift of rotational axis"}
            ],
            "viva_questions": [
                "What is the physical significance of the radius of gyration?",
                "Why is a flywheel concentrated at its rim?"
            ],
            "difficulty": "Intermediate"
        },
        "waves": {
            "title": "Waves",
            "summary": "Mathematical representation of wave motion, classical 1D wave equation, superposition principle, sound propagation, standing waves, and Doppler shift.",
            "key_points": [
                "General wave equation in 1D: ∂²y/∂x² = (1/v²) ∂²y/∂t²",
                "Phase velocity v = λf = ω/k where k is wave number",
                "Superposition of counter-propagating waves produces standing waves with nodes and antinodes",
                "Doppler effect describes perceived frequency shifts due to relative motion between source and observer"
            ],
            "formulas": [
                {
                    "name": "1D Wave Equation",
                    "latex": "$$\\frac{\\partial^2 y}{\\partial x^2} = \\frac{1}{v^2} \\frac{\\partial^2 y}{\\partial t^2}$$",
                    "explanation": "Governing partial differential equation for linear waves"
                },
                {
                    "name": "Standing Wave Equation",
                    "latex": "$$y(x,t) = 2A \\sin(kx) \\cos(\\omega t)$$",
                    "explanation": "Stationary spatial nodes at x = nλ/2"
                },
                {
                    "name": "Doppler Effect",
                    "latex": "$$f' = f \\left(\\frac{v \\pm v_o}{v \\mp v_s}\\right)$$",
                    "explanation": "Observed frequency with observer speed v_o and source speed v_s"
                }
            ],
            "examples": [
                {
                    "question": "A string of mass density 0.01 kg/m is under tension of 100 N. Calculate wave velocity.",
                    "answer": "100 m/s",
                    "steps": ["v = √(T/μ)", "v = √(100 / 0.01) = √10000 = 100 m/s"]
                }
            ],
            "mcqs": [
                {"question": "What is the distance between two consecutive nodes in a standing wave?", "options": ["λ/4", "λ/2", "λ", "2λ"], "correct": 1},
                {"question": "When a sound source moves towards a stationary observer, the observed frequency is:", "options": ["Higher", "Lower", "Unchanged", "Zero"], "correct": 0}
            ],
            "practice_questions": [
                "Derive the classical 1D wave equation for transverse waves on a stretched string under tension T.",
                "Explain the Doppler effect when both source and observer move towards each other."
            ],
            "flashcards": [
                {"front": "What defines a standing wave node?", "back": "A point along a standing wave where displacement amplitude is permanently zero due to destructive interference.", "hint": "Zero amplitude point"},
                {"front": "How does wave speed depend on string tension and linear density?", "back": "v = √(T/μ), speed increases with higher tension and decreases with heavier strings.", "hint": "Square root ratio"}
            ],
            "viva_questions": [
                "What is the difference between phase velocity and group velocity?",
                "Why can transverse waves not propagate through ideal liquids and gases?"
            ],
            "difficulty": "Intermediate"
        },
        "optics": {
            "title": "Optics",
            "summary": "Wave optics phenomena including Young's double slit interference, thin film interference, Fraunhofer diffraction, diffraction gratings, Brewster's polarization, and laser physics.",
            "key_points": [
                "Interference occurs when coherent waves superpose with fixed phase relationships",
                "Diffraction describes wave bending and intensity redistribution around apertures",
                "Polarization demonstrates the transverse nature of electromagnetic light waves",
                "Brewster's angle satisfies tan(θ_B) = n, producing completely polarized reflected light"
            ],
            "formulas": [
                {
                    "name": "Young's Fringe Width",
                    "latex": "$$\\beta = \\frac{\\lambda D}{d}$$",
                    "explanation": "Fringe separation with slit distance d and screen distance D"
                },
                {
                    "name": "Single Slit Diffraction Minima",
                    "latex": "$$a \\sin\\theta = m\\lambda \\quad (m = \\pm 1, \\pm 2, \\dots)$$",
                    "explanation": "Condition for dark fringes for slit of width a"
                },
                {
                    "name": "Brewster's Law",
                    "latex": "$$\\tan \\theta_B = n$$",
                    "explanation": "Polarizing angle where reflected ray is 100% linearly polarized"
                }
            ],
            "examples": [
                {
                    "question": "In Young's double slit, λ=600nm, D=1m, d=0.5mm. Find fringe width.",
                    "answer": "1.2 mm",
                    "steps": ["β = λD/d", "β = (600×10⁻⁹)(1)/(0.5×10⁻³)", "β = 1.2×10⁻³ m = 1.2 mm"]
                }
            ],
            "mcqs": [
                {"question": "What happens to fringe width in Young's experiment if the apparatus is immersed in water (n=1.33)?", "options": ["Increases", "Decreases by factor of 1.33", "Remains same", "Becomes zero"], "correct": 1},
                {"question": "At Brewster's angle, what is the angle between reflected and refracted rays?", "options": ["0°", "45°", "90°", "180°"], "correct": 2}
            ],
            "practice_questions": [
                "Explain Fraunhofer diffraction at a single slit and derive the expression for central maximum width.",
                "State Brewster's law and show that reflected and refracted rays are mutually perpendicular."
            ],
            "flashcards": [
                {"front": "What is the condition for constructive interference in Young's double slit?", "back": "Path difference must be an integral multiple of wavelength (Δx = nλ).", "hint": "Path difference"},
                {"front": "State Brewster's Law for polarization by reflection", "back": "tan(θ_B) = n where θ_B is the polarizing angle and n is refractive index of medium.", "hint": "Refractive index & angle"},
                {"front": "What is Rayleigh's criterion for resolution?", "back": "Two point sources are just resolved when the central maximum of one diffraction pattern coincides with the first minimum of the other.", "hint": "Diffraction limit"}
            ],
            "viva_questions": [
                "Why are colors seen in thin soap bubbles?",
                "What is the difference between Fresnel and Fraunhofer diffraction?"
            ],
            "difficulty": "Intermediate"
        },
        "thermodynamics": {
            "title": "Thermodynamics",
            "summary": "Laws of thermodynamics, heat engines, Carnot cycle, entropy, Clausius inequality, Helmholtz and Gibbs free energy functions, and thermodynamic potentials.",
            "key_points": [
                "First law establishes conservation of energy: dQ = dU + dW",
                "Second law imposes directionality on natural processes via entropy: dS ≥ 0 for isolated systems",
                "Carnot cycle provides the theoretical maximum efficiency between two thermal reservoirs: η = 1 - T_C/T_H",
                "Entropy change in a reversible process is given by dS = dQ_rev / T"
            ],
            "formulas": [
                {
                    "name": "First Law of Thermodynamics",
                    "latex": "$$dQ = dU + P\\,dV$$",
                    "explanation": "Heat added equals internal energy increase plus boundary work"
                },
                {
                    "name": "Carnot Efficiency",
                    "latex": "$$\\eta = 1 - \\frac{T_C}{T_H}$$",
                    "explanation": "Maximum thermodynamic efficiency operating between T_H and T_C (Kelvin)"
                },
                {
                    "name": "Entropy Change",
                    "latex": "$$\\Delta S = \\int \\frac{dQ_{\\text{rev}}}{T}$$",
                    "explanation": "State function measuring microscopic configuration disorder"
                }
            ],
            "examples": [
                {
                    "question": "A Carnot engine operates between 600 K and 300 K. Calculate its theoretical efficiency.",
                    "answer": "50%",
                    "steps": ["η = 1 - (T_C / T_H)", "η = 1 - (300 / 600) = 0.50 = 50%"]
                }
            ],
            "mcqs": [
                {"question": "Which thermodynamic process occurs at constant entropy?", "options": ["Isothermal", "Isobaric", "Isochoric", "Reversible Adiabatic (Isentropic)"], "correct": 3},
                {"question": "According to the Second Law, the entropy of the universe during an irreversible process:", "options": ["Decreases", "Remains constant", "Increases", "Becomes zero"], "correct": 2}
            ],
            "practice_questions": [
                "Derive the efficiency of a Carnot heat engine operating between hot reservoir T_H and cold reservoir T_C.",
                "Show that entropy remains constant in a reversible adiabatic process and increases in an irreversible process."
            ],
            "flashcards": [
                {"front": "State the Kelvin-Planck statement of the Second Law.", "back": "It is impossible for any device operating on a cycle to receive heat from a single reservoir and produce an equivalent amount of work.", "hint": "100% heat conversion impossibility"},
                {"front": "What is the efficiency of a Carnot engine?", "back": "η = 1 - (T_C / T_H), depending strictly on absolute temperatures of hot and cold reservoirs.", "hint": "Temperature ratio"}
            ],
            "viva_questions": [
                "Can a refrigerator cool a room if left open?",
                "What is the physical meaning of absolute zero in terms of entropy?"
            ],
            "difficulty": "Intermediate"
        },
        "electromagnetism": {
            "title": "Electromagnetism",
            "summary": "Electrostatics, Gauss's law, magnetostatics, Ampere-Maxwell law, Faraday's law of induction, Maxwell's four equations, and electromagnetic wave propagation.",
            "key_points": [
                "Gauss's law relates electric flux to enclosed charge: ∮E·dA = Q_encl / ε₀",
                "Faraday's law shows changing magnetic flux creates an electromotive force: ∮E·dl = -dΦ_B/dt",
                "Displacement current ε₀(∂E/∂t) resolves the continuity contradiction in Ampere's law",
                "Maxwell's equations predict electromagnetic waves propagating at speed c = 1/√(μ₀ε₀)"
            ],
            "formulas": [
                {
                    "name": "Maxwell's Equations (Differential)",
                    "latex": "$$\\nabla \\cdot \\vec{E} = \\frac{\\rho}{\\varepsilon_0}, \\quad \\nabla \\cdot \\vec{B} = 0, \\quad \\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}, \\quad \\nabla \\times \\vec{B} = \\mu_0 \\vec{J} + \\mu_0 \\varepsilon_0 \\frac{\\partial \\vec{E}}{\\partial t}$$",
                    "explanation": "Complete unified equations of classical electrodynamics"
                },
                {
                    "name": "Speed of Light in Vacuum",
                    "latex": "$$c = \\frac{1}{\\sqrt{\\mu_0 \\varepsilon_0}} \\approx 3 \\times 10^8 \\text{ m/s}$$",
                    "explanation": "Propagation velocity derived from Maxwell's curl equations"
                }
            ],
            "examples": [
                {
                    "question": "Find the electric field at distance r from an infinite line of charge with uniform linear density λ.",
                    "answer": "E = λ / (2πε₀r)",
                    "steps": ["Apply Gauss law over cylindrical surface of length L and radius r", "E(2πrL) = λL / ε₀ => E = λ / (2πε₀r)"]
                }
            ],
            "mcqs": [
                {"question": "Which term did Maxwell add to Ampere's law to make it consistent with charge conservation?", "options": ["Inductance", "Displacement current", "Magnetic monopole flux", "Eddy current"], "correct": 1},
                {"question": "In an electromagnetic wave in free space, what is the phase relationship between E and B fields?", "options": ["90° out of phase", "180° out of phase", "In phase", "Variable"], "correct": 2}
            ],
            "practice_questions": [
                "Derive the electromagnetic wave equation in vacuum starting from Maxwell's curl equations.",
                "Explain displacement current and justify why it was necessary to complete Ampere's Law."
            ],
            "flashcards": [
                {"front": "State Gauss's Law in electrostatics.", "back": "The total electric flux out of a closed surface is equal to the net enclosed charge divided by permittivity of free space: ∮E·dA = Q_encl / ε₀.", "hint": "Flux equals enclosed charge"},
                {"front": "What is displacement current?", "back": "A quantity representing the rate of change of electric displacement field: I_D = ε₀ (dΦ_E/dt), producing magnetic fields like conduction current.", "hint": "Changing electric field"}
            ],
            "viva_questions": [
                "Why do magnetic monopoles not exist according to Maxwell's equations?",
                "What is the Poynting vector and what does its magnitude represent?"
            ],
            "difficulty": "Intermediate"
        }
    },
    "CH101": {
        "atomic_structure": {
            "title": "Atomic Structure",
            "summary": "Quantum mechanical model of atom, de Broglie relation, Heisenberg uncertainty principle, Schrödinger wave equation, quantum numbers (n, l, m, s), and orbital configurations.",
            "key_points": [
                "de Broglie dual nature connects matter wavelength with momentum: λ = h/p",
                "Heisenberg uncertainty sets fundamental limits on simultaneous measurement: ΔxΔp ≥ ℏ/2",
                "Four quantum numbers specify energy, angular momentum, magnetic orientation, and electron spin",
                "Aufbau principle, Pauli exclusion principle, and Hund's rule dictate ground state configurations"
            ],
            "formulas": [
                {
                    "name": "de Broglie Wavelength",
                    "latex": "$$\\lambda = \\frac{h}{p} = \\frac{h}{mv}$$",
                    "explanation": "Wavelength associated with any moving matter particle"
                },
                {
                    "name": "Heisenberg Uncertainty Principle",
                    "latex": "$$\\Delta x \\cdot \\Delta p \\ge \\frac{\\hbar}{2} = \\frac{h}{4\\pi}$$",
                    "explanation": "Fundamental quantum uncertainty between position and linear momentum"
                }
            ],
            "examples": [
                {
                    "question": "Calculate the de Broglie wavelength of an electron (m = 9.11×10⁻³¹ kg) moving at 10⁶ m/s.",
                    "answer": "0.727 nm",
                    "steps": ["λ = h / (mv)", "λ = (6.626×10⁻³⁴) / (9.11×10⁻³¹ × 10⁶) = 7.27×10⁻¹⁰ m = 0.727 nm"]
                }
            ],
            "mcqs": [
                {"question": "How many quantum numbers are required to completely define an electron in an orbital?", "options": ["2", "3", "4", "5"], "correct": 2},
                {"question": "What is the maximum number of electrons that can occupy a subshell with l = 2 (d subshell)?", "options": ["2", "6", "10", "14"], "correct": 2}
            ],
            "practice_questions": [
                "Explain the physical significance of the four quantum numbers (n, l, m_l, m_s).",
                "State Pauli's exclusion principle and write the electron configuration of Chromium (Z=24)."
            ],
            "flashcards": [
                {"front": "State Heisenberg's Uncertainty Principle.", "back": "It is fundamentally impossible to simultaneously measure the exact position and momentum of a particle: Δx Δp ≥ ℏ/2.", "hint": "Position-momentum limit"},
                {"front": "What does the principal quantum number (n) determine?", "back": "Main energy level and average orbital distance from the atomic nucleus (n = 1, 2, 3...).", "hint": "Shell level"},
                {"front": "What is Hund's Rule of Maximum Multiplicity?", "back": "Electrons singly occupy degenerate orbitals with parallel spins before doubly occupying any orbital.", "hint": "Single occupation first"}
            ],
            "viva_questions": [
                "Why does Copper have a [Ar] 3d¹⁰ 4s¹ electron configuration instead of [Ar] 3d⁹ 4s²?",
                "What is the physical meaning of the wave function squared (|ψ|²)?"
            ],
            "difficulty": "Intermediate"
        },
        "chemical_bonding": {
            "title": "Chemical Bonding",
            "summary": "Ionic, covalent, coordinate, and metallic bonding, VSEPR theory for molecular geometry, hybridization (sp, sp2, sp3, sp3d), and Molecular Orbital (MO) energy diagrams.",
            "key_points": [
                "VSEPR theory predicts geometric shapes based on valence shell electron pair repulsions",
                "Hybridization mixes atomic orbitals into equivalent hybrid directional orbitals",
                "MO theory forms bonding and antibonding molecular orbitals via LCAO",
                "Bond order = (N_bonding - N_antibonding) / 2 determines bond stability and strength"
            ],
            "formulas": [
                {
                    "name": "Bond Order",
                    "latex": "$$\\text{Bond Order} = \\frac{N_b - N_a}{2}$$",
                    "explanation": "Net covalent bonds between two atoms in Molecular Orbital theory"
                }
            ],
            "examples": [
                {
                    "question": "Calculate the bond order and magnetic property of O₂ molecule.",
                    "answer": "Bond Order = 2, Paramagnetic",
                    "steps": ["O₂ has 16 electrons: 10 bonding, 6 antibonding", "BO = (10 - 6)/2 = 2", "2 unpaired electrons in π* orbitals => Paramagnetic"]
                }
            ],
            "mcqs": [
                {"question": "What is the hybridization and bond angle in methane (CH₄)?", "options": ["sp², 120°", "sp³, 109.5°", "sp, 180°", "dsp², 90°"], "correct": 1},
                {"question": "Which of the following molecules has a bond order of 3?", "options": ["O₂", "N₂", "F₂", "H₂"], "correct": 1}
            ],
            "practice_questions": [
                "Explain Molecular Orbital theory and construct the MO diagram for oxygen (O₂) explaining its paramagnetism.",
                "Compare the geometry and bond angles of CH₄, NH₃, and H₂O using VSEPR theory."
            ],
            "flashcards": [
                {"front": "Why is liquid oxygen paramagnetic?", "back": "According to MO Theory, O₂ contains two unpaired electrons in degenerate π*2p antibonding orbitals.", "hint": "Unpaired electrons in MO"},
                {"front": "What is the bond order formula in MO theory?", "back": "Bond Order = (Number of bonding electrons - Number of antibonding electrons) / 2.", "hint": "(N_b - N_a)/2"}
            ],
            "viva_questions": [
                "Why is the bond angle in H₂O (104.5°) smaller than in CH₄ (109.5°)?",
                "What is the difference between a sigma (σ) and pi (π) bond?"
            ],
            "difficulty": "Intermediate"
        },
        "thermodynamics": {
            "title": "Thermodynamics",
            "summary": "Chemical thermodynamics, enthalpy changes, Hess's law, entropy, Gibbs free energy criterion for reaction spontaneity, and chemical equilibrium constant relations.",
            "key_points": [
                "Enthalpy ΔH represents heat absorbed or released at constant pressure",
                "Hess's law states total enthalpy change is independent of intermediate reaction steps",
                "Gibbs free energy change ΔG = ΔH - TΔS governs reaction spontaneity (ΔG < 0 is spontaneous)",
                "Standard free energy connects directly to equilibrium constant: ΔG° = -RT ln K_eq"
            ],
            "formulas": [
                {
                    "name": "Gibbs-Helmholtz Equation",
                    "latex": "$$\\Delta G = \\Delta H - T\\Delta S$$",
                    "explanation": "Criterion for spontaneity at constant temperature and pressure"
                },
                {
                    "name": "Free Energy and Equilibrium",
                    "latex": "$$\\Delta G^\\circ = -RT \\ln K_{\\text{eq}}$$",
                    "explanation": "Standard Gibbs free energy linked to thermodynamic equilibrium constant"
                }
            ],
            "examples": [
                {
                    "question": "For a reaction with ΔH = -50 kJ/mol and ΔS = -100 J/(mol·K) at 298 K, find ΔG.",
                    "answer": "-20.2 kJ/mol (Spontaneous)",
                    "steps": ["ΔG = ΔH - TΔS", "ΔG = -50000 - 298(-100) = -50000 + 29800 = -20200 J/mol = -20.2 kJ/mol"]
                }
            ],
            "mcqs": [
                {"question": "A reaction is always spontaneous at all temperatures when:", "options": ["ΔH > 0, ΔS > 0", "ΔH < 0, ΔS > 0", "ΔH > 0, ΔS < 0", "ΔH < 0, ΔS < 0"], "correct": 1},
                {"question": "What is the value of ΔG at chemical equilibrium?", "options": ["Positive", "Negative", "Zero", "Infinity"], "correct": 2}
            ],
            "practice_questions": [
                "State Hess's Law of Constant Heat Summation and calculate the enthalpy of formation of methane.",
                "Derive the relationship between standard Gibbs free energy change (ΔG°) and equilibrium constant (K_eq)."
            ],
            "flashcards": [
                {"front": "State Hess's Law of constant heat summation.", "back": "The total enthalpy change in a chemical reaction is identical whether the reaction takes place in one step or multiple steps.", "hint": "Path independence"},
                {"front": "What is the condition for a chemical process to be spontaneous?", "back": "The change in Gibbs Free Energy must be negative (ΔG = ΔH - TΔS < 0) at constant temperature and pressure.", "hint": "ΔG < 0"}
            ],
            "viva_questions": [
                "Can an endothermic reaction ever be spontaneous?",
                "What is the Third Law of Thermodynamics?"
            ],
            "difficulty": "Intermediate"
        },
        "electrochemistry": {
            "title": "Electrochemistry",
            "summary": "Galvanic and electrolytic cells, Nernst equation for cell potential, electrochemical series, corrosion mechanisms, and battery technology (Li-ion, lead-acid, fuel cells).",
            "key_points": [
                "Galvanic cells convert spontaneous chemical energy into electrical work",
                "Nernst equation computes EMF as a function of ion concentrations and temperature",
                "Rusting of iron is an electrochemical cell with anodic Fe oxidation and cathodic O₂ reduction",
                "Lithium-ion batteries operate via reversible intercalation of Li+ ions between graphite and cathode"
            ],
            "formulas": [
                {
                    "name": "Nernst Equation (298 K)",
                    "latex": "$$E = E^\\circ - \\frac{0.0591}{n} \\log_{10} Q$$",
                    "explanation": "Electrochemical cell EMF dependence on reaction quotient Q and n transferred electrons"
                },
                {
                    "name": "Cell Free Energy",
                    "latex": "$$\\Delta G = -nFE$$",
                    "explanation": "Electrical work extracted from cell where F is Faraday constant (96485 C/mol)"
                }
            ],
            "examples": [
                {
                    "question": "Calculate EMF of Daniel cell with [Zn²⁺]=0.01M, [Cu²⁺]=1.0M, E°=1.10V at 298 K.",
                    "answer": "1.159 V",
                    "steps": ["E = 1.10 - (0.0591/2) log10(0.01/1.0)", "E = 1.10 - 0.02955(-2) = 1.10 + 0.0591 = 1.1591 V"]
                }
            ],
            "mcqs": [
                {"question": "In a galvanic cell, which electrode undergoes oxidation?", "options": ["Cathode", "Anode", "Salt bridge", "Electrolyte"], "correct": 1},
                {"question": "Which metal is used for sacrificial cathodic protection of iron pipes?", "options": ["Copper", "Lead", "Zinc or Magnesium", "Silver"], "correct": 2}
            ],
            "practice_questions": [
                "Derive the Nernst equation and calculate the potential of a galvanic concentration cell.",
                "Explain the electrochemical mechanism of rusting of iron and discuss two methods of corrosion prevention."
            ],
            "flashcards": [
                {"front": "State the Nernst Equation for half-cell potential.", "back": "E = E° - (RT/nF) ln([Red]/[Ox]) = E° - (0.0591/n) log10([Red]/[Ox]) at 298 K.", "hint": "Concentration dependence"},
                {"front": "How does galvanization protect steel from corrosion?", "back": "Zinc acts as a sacrificial anode because its standard reduction potential (-0.76V) is more negative than iron (-0.44V).", "hint": "Sacrificial anode"}
            ],
            "viva_questions": [
                "What is the function of the salt bridge in a Daniel cell?",
                "What is the advantage of a fuel cell over conventional combustion engines?"
            ],
            "difficulty": "Intermediate"
        },
        "organic_chemistry": {
            "title": "Organic Chemistry",
            "summary": "Mechanisms of organic reactions (SN1, SN2, E1, E2), synthesis and properties of engineering polymers (Nylon-6,6, Bakelite, Teflon), and principles of Green Chemistry.",
            "key_points": [
                "SN1 proceeds via carbocation intermediate (racemization); SN2 proceeds via concerted backside attack (Walden inversion)",
                "Addition polymers form without byproducts; condensation polymers eliminate small molecules like H₂O",
                "Thermosetting polymers (e.g. Bakelite) form permanent cross-linked networks upon heating",
                "Green chemistry maximizes atom economy and minimizes toxic environmental footprints"
            ],
            "formulas": [
                {
                    "name": "Atom Economy",
                    "latex": "$$\\text{Atom Economy} = \\frac{\\text{Molecular Weight of Desired Product}}{\\text{Total Molecular Weight of All Reactants}} \\times 100\\%$$",
                    "explanation": "Standard metric measuring synthetic efficiency in Green Chemistry"
                }
            ],
            "examples": [
                {
                    "question": "Identify whether 2-bromo-2-methylpropane + NaOH proceeds primarily via SN1 or SN2.",
                    "answer": "SN1 mechanism",
                    "steps": ["Substrate is tertiary (3°) alkyl halide", "Steric hindrance blocks SN2 backside attack", "Stable tertiary carbocation intermediate favors SN1 / E1"]
                }
            ],
            "mcqs": [
                {"question": "Which nucleophilic substitution mechanism exhibits complete stereochemical Walden inversion?", "options": ["SN1", "SN2", "E1", "E2"], "correct": 1},
                {"question": "Bakelite is formed by the condensation polymerization of phenol with:", "options": ["Acetaldehyde", "Formaldehyde", "Acetone", "Benzaldehyde"], "correct": 1}
            ],
            "practice_questions": [
                "Compare SN1 and SN2 reaction mechanisms in terms of kinetics, stereochemistry, and solvent effects.",
                "Explain the synthesis, structure, and engineering applications of Nylon-6,6 and Bakelite."
            ],
            "flashcards": [
                {"front": "What is the key difference between SN1 and SN2 mechanisms?", "back": "SN1 is two-step unimolecular via carbocation (favors 3°); SN2 is single-step bimolecular with Walden inversion (favors 1°).", "hint": "Step count & stereochemistry"},
                {"front": "What monomers form Nylon-6,6?", "back": "Adipic acid (hexanedioic acid) and Hexamethylenediamine (1,6-diaminohexane).", "hint": "6-carbon diacid and diamine"}
            ],
            "viva_questions": [
                "What is the difference between thermoplastic and thermosetting polymers?",
                "Why is 100% atom economy desirable in green chemical synthesis?"
            ],
            "difficulty": "Intermediate"
        }
    },
    "EE101": {
        "dc_circuits": {
            "title": "DC Circuits and Network Theorems",
            "summary": "Analysis of DC electrical circuits using Ohm's Law, Kirchhoff's Laws (KCL/KVL), and network reduction theorems including Thevenin, Norton, Superposition, and Maximum Power Transfer.",
            "key_points": [
                "Ohm's Law states current is proportional to voltage: V = I * R",
                "KCL states total current entering an electrical node equals total current leaving",
                "KVL states the algebraic sum of voltages around any closed loop is zero",
                "Thevenin's theorem replaces a linear network with an equivalent voltage source V_th and series resistance R_th",
                "Maximum power transfer occurs when load resistance matches Thevenin resistance (R_L = R_th)"
            ],
            "formulas": [
                {
                    "name": "Ohm's Law",
                    "latex": "$$V = I \\times R$$",
                    "explanation": "Voltage equals current multiplied by resistance"
                },
                {
                    "name": "Maximum Power Transfer",
                    "latex": "$$P_{\\max} = \\frac{V_{th}^2}{4 R_{th}}$$",
                    "explanation": "Maximum power delivered to load when R_L = R_th"
                }
            ],
            "examples": [
                {
                    "question": "Find Thevenin voltage and resistance for a 12V source with 4 ohm internal resistance.",
                    "answer": "V_th = 12V, R_th = 4 ohms",
                    "steps": ["Open circuit voltage Voc = 12V", "Deactivate source (short circuit): R_th = 4 ohms"]
                }
            ],
            "flashcards": [
                {"front": "State Kirchhoff's Current Law (KCL)", "back": "The algebraic sum of all currents entering and exiting any electrical node is zero (conservation of charge).", "hint": "Node conservation"},
                {"front": "State the condition for Maximum Power Transfer in DC circuits", "back": "Maximum power is transferred to the load when load resistance equals Thevenin source resistance (R_L = R_th).", "hint": "Load vs Thevenin resistance"},
                {"front": "What is Thevenin's Theorem?", "back": "Any linear bilateral DC network can be replaced with an equivalent voltage source (V_th) in series with a resistance (R_th).", "hint": "Equivalent circuit"}
            ],
            "difficulty": "Introductory"
        }
    }
}

# ===== YEAR 1 - SEMESTER 2 STUDY CONTENT =====
YEAR1_SEM2_CONTENT = {
    "MA102": {
        "integral_calculus": {
            "title": "Integral Calculus",
            "summary": "Integral calculus deals with accumulation of quantities and areas under curves. It is the inverse process of differentiation.",
            "key_points": [
                "Definite integrals give net area",
                "Fundamental Theorem links differentiation and integration",
                "Improper integrals have infinite limits or discontinuities",
                "Beta and Gamma functions extend factorial to real numbers"
            ],
            "formulas": [
                {
                    "name": "Fundamental Theorem",
                    "latex": "$$\\int_a^b f(x)\\,dx = F(b) - F(a)$$",
                    "explanation": "If F'(x) = f(x), then definite integral equals F(b) - F(a)"
                },
                {
                    "name": "Integration by Parts",
                    "latex": "$$\\int u\\,dv = uv - \\int v\\,du$$",
                    "explanation": "Product rule for integration"
                },
                {
                    "name": "Beta Function",
                    "latex": "$$B(m,n) = \\int_0^1 x^{m-1}(1-x)^{n-1}\\,dx = \\frac{\\Gamma(m)\\Gamma(n)}{\\Gamma(m+n)}$$",
                    "explanation": "Beta function relates to Gamma function"
                },
                {
                    "name": "Gamma Function",
                    "latex": "$$\\Gamma(n) = \\int_0^\\infty x^{n-1}e^{-x}\\,dx = (n-1)!$$",
                    "explanation": "Generalizes factorial: Γ(n) = (n-1)!"
                }
            ],
            "examples": [
                {
                    "question": "Evaluate ∫x sin(x) dx from 0 to π",
                    "answer": "π",
                    "steps": ["Integration by parts: u=x, dv=sin(x)dx", "du=dx, v=-cos(x)", "-x cos(x)|₀^π + ∫cos(x)dx", "-π(-1) + 0 + sin(x)|₀^π = π"]
                }
            ],
            "mcqs": [
                {"question": "∫₀^∞ e⁻ˣ dx =", "options": ["0", "1", "∞", "π"], "correct": 1},
                {"question": "B(m,n) =", "options": ["Γ(m)Γ(n)", "Γ(m+n)", "Γ(m)Γ(n)/Γ(m+n)", "Γ(m)/Γ(n)"], "correct": 2}
            ]
        },
        "differential_equations": {
            "title": "Differential Equations",
            "summary": "Differential equations relate functions to their derivatives. They model dynamic systems in physics, engineering, and biology.",
            "key_points": [
                "Order = highest derivative, Degree = power of highest derivative",
                "Linear DE: dy/dx + P(x)y = Q(x)",
                "Exact DE: Mdx + Ndy = 0 where ∂M/∂y = ∂N/∂x",
                "Wronskian determines linear independence"
            ],
            "formulas": [
                {
                    "name": "Linear First Order",
                    "latex": "$$\\frac{dy}{dx} + P(x)y = Q(x)$$",
                    "explanation": "Standard form for linear first-order DE"
                },
                {
                    "name": "Integrating Factor",
                    "latex": "$$\\mu(x) = e^{\\int P(x)\\,dx}$$",
                    "explanation": "Multiply to make equation exact"
                },
                {
                    "name": "Wronskian",
                    "latex": "$$W(y_1,y_2) = \\begin{vmatrix}y_1 & y_2 \\\\ y_1' & y_2'\\end{vmatrix}$$",
                    "explanation": "Non-zero Wronskian means linearly independent solutions"
                }
            ],
            "examples": [
                {
                    "question": "Solve dy/dx + 2y = e⁻ˣ",
                    "answer": "y = e⁻ˣ + Ce⁻²ˣ",
                    "steps": ["IF = e^(∫2dx) = e²ˣ", "d/dx(y e²ˣ) = eˣ", "y e²ˣ = eˣ + C", "y = e⁻ˣ + Ce⁻²ˣ"]
                }
            ],
            "mcqs": [
                {"question": "Order of d²y/dx² + 3dy/dx + 2y = 0 is:", "options": ["1", "2", "3", "4"], "correct": 1},
                {"question": "The Wronskian being non-zero implies:", "options": ["Dependent solutions", "Independent solutions", "No solution", "Unique solution"], "correct": 1}
            ]
        }
    },
    "CS102": {
        "arrays_linked_lists": {
            "title": "Arrays and Linked Lists",
            "summary": "Arrays store elements in contiguous memory while linked lists use nodes with pointers. Each has different time complexities for operations.",
            "key_points": [
                "Arrays: O(1) access, O(n) insertion/deletion",
                "Singly Linked List: O(n) access, O(1) insertion at head",
                "Doubly Linked List: bidirectional traversal",
                "Circular Linked List: last points to first"
            ],
            "formulas": [
                {
                    "name": "Array Access",
                    "latex": "$$address = base + (index) \\times size$$",
                    "explanation": "Direct access using base address and index"
                },
                {
                    "name": "Time Complexities",
                    "latex": "Array: Access O(1), Search O(n), Insert O(n), Delete O(n)",
                    "explanation": "Array operation complexities"
                },
                {
                    "name": "Linked List Time",
                    "latex": "LL: Access O(n), Search O(n), Insert O(1), Delete O(1)",
                    "explanation": "Linked list operation complexities"
                }
            ],
            "examples": [
                {
                    "question": "Implement linked list reversal",
                    "answer": "Iterative approach with three pointers",
                    "code": """def reverse(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev"""
                }
            ],
            "mcqs": [
                {"question": "Array access complexity:", "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"], "correct": 0},
                {"question": "Linked list insertion at head:", "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"], "correct": 0},
                {"question": "Memory efficient for dynamic data:", "options": ["Array", "Linked List", "Both same", "None"], "correct": 1}
            ]
        },
        "trees": {
            "title": "Trees",
            "summary": "Trees are hierarchical data structures with a root and child nodes. Binary trees, BSTs, and AVL trees are fundamental tree variants.",
            "key_points": [
                "Binary Tree: each node has at most 2 children",
                "Binary Search Tree: left < root < right",
                "AVL Tree: balance factor |BF| ≤ 1",
                "Height of balanced BST: O(log n)"
            ],
            "formulas": [
                {
                    "name": "Balance Factor",
                    "latex": "$$BF = \\text{height(left)} - \\text{height(right)}$$",
                    "explanation": "For AVL trees, |BF| must be ≤ 1"
                },
                {
                    "name": "AVL Height Bound",
                    "latex": "$$h < 1.4404 \\log_2(n + 2) - 0.328$$",
                    "explanation": "Maximum height of AVL tree with n nodes"
                },
                {
                    "name": "Binary Tree Nodes",
                    "latex": "$$n_{leaves} = n_{degree2} + 1$$",
                    "explanation": "Number of leaves = number of 2-degree nodes + 1"
                }
            ],
            "examples": [
                {
                    "question": "Insert 50, 30, 70, 20, 40 into BST",
                    "answer": "Visual tree structure",
                    "steps": ["50 as root", "30 left of 50", "70 right of 50", "20 left of 30", "40 right of 30"]
                }
            ],
            "mcqs": [
                {"question": "Maximum nodes in binary tree of height h:", "options": ["2ʰ", "2ʰ⁺¹-1", "h²", "h!"], "correct": 1},
                {"question": "AVL tree balance factor range:", "options": ["0 to 1", "-1 to 1", "-2 to 2", "0 to 2"], "correct": 1},
                {"question": "Inorder traversal of BST gives:", "options": ["Reverse order", "Random order", "Sorted order", "Level order"], "correct": 2}
            ]
        }
    }
}

# ===== YEAR 2 - SEMESTER 3 STUDY CONTENT =====
YEAR2_SEM3_CONTENT = {
    "CS201": {
        "asymptotic_analysis": {
            "title": "Asymptotic Analysis",
            "summary": "Asymptotic analysis describes the behavior of algorithms as input size approaches infinity, using Big-O, Big-Theta, and Big-Omega notations.",
            "key_points": [
                "Big-O: Upper bound (worst case)",
                "Big-Ω: Lower bound (best case)",
                "Big-Θ: Tight bound (average case)",
                "Transitivity and reflexivity properties"
            ],
            "formulas": [
                {
                    "name": "Big-O Definition",
                    "latex": "$$f(n) = O(g(n)) \\iff \\exists c, n_0 \\text{ s.t. } 0 \\leq f(n) \\leq cg(n) \\forall n \\geq n_0$$",
                    "explanation": "f(n) grows no faster than g(n)"
                },
                {
                    "name": "Master Theorem",
                    "latex": "$$T(n) = aT\\left(\\frac{n}{b}\\right) + \\Theta(n^k \\log^p n)$$",
                    "explanation": "Cases based on comparison of n^(log_b a) with n^k"
                },
                {
                    "name": "Growth Rate Hierarchy",
                    "latex": "$$1 < \\log n < \\sqrt{n} < n < n\\log n < n^2 < n^3 < 2^n < n!$$",
                    "explanation": "Standard growth rate ordering"
                }
            ],
            "examples": [
                {
                    "question": "Solve T(n) = 2T(n/2) + n using Master Theorem",
                    "answer": "Θ(n log n)",
                    "steps": ["a=2, b=2, f(n)=n", "n^(log_b a) = n^(log_2 2) = n", "f(n) = Θ(n)", "Case 2 applies", "T(n) = Θ(n log n)"]
                }
            ],
            "mcqs": [
                {"question": "T(n) = 3T(n/4) + n has complexity:", "options": ["O(n)", "O(n log n)", "O(n²)", "O(4ⁿ)"], "correct": 0},
                {"question": "Which is NOT a property of Big-O:", "options": ["Reflexive", "Symmetric", "Transitive", "Positive definite"], "correct": 1}
            ]
        },
        "divide_conquer": {
            "title": "Divide and Conquer",
            "summary": "Divide and conquer algorithms break problems into subproblems, solve them recursively, and combine solutions.",
            "key_points": [
                "Three steps: Divide, Conquer, Combine",
                " recurrence relations often solved with Master Theorem",
                "Space complexity from recursion stack depth"
            ],
            "formulas": [
                {
                    "name": "Merge Sort",
                    "latex": "$$T(n) = 2T(n/2) + \\Theta(n)$$",
                    "explanation": "Divide in half, conquer both, merge in O(n)"
                },
                {
                    "name": "Quick Sort Avg",
                    "latex": "$$T(n) = 2T(n/2) + \\Theta(n)$$",
                    "explanation": "Average case with balanced partition"
                }
            ],
            "examples": [
                {
                    "question": "Explain merge sort on [38, 27, 43, 3, 9, 82, 10]",
                    "answer": "Recursive splitting and merging",
                    "steps": ["Split until single elements", "Merge pairs in order", "Final sorted: [3, 9, 10, 27, 38, 43, 82]"]
                }
            ]
        },
        "greedy_algorithms": {
            "title": "Greedy Algorithms",
            "summary": "Greedy algorithms make locally optimal choices at each stage with the hope of finding global optimum.",
            "key_points": [
                "Greedy choice property: local optimum leads to global",
                "Optimal substructure: optimal solution contains optimal subsolutions",
                "Matroid theory characterizes greedy solvable problems"
            ],
            "formulas": [
                {
                    "name": "Kruskal's Complexity",
                    "latex": "$$O(E \\log E)$$",
                    "explanation": "Sort edges + Union-Find operations"
                },
                {
                    "name": "Prim's Complexity",
                    "latex": "$$O((V+E) \\log V)$$",
                    "explanation": "Using binary heap"
                }
            ],
            "examples": [
                {
                    "question": "Activity selection: activities with start=[1,3,0,5,3,5,6,8,8,2,12], finish=[4,5,6,7,9,9,10,11,12,13,14]",
                    "answer": "4 activities: 1,4,8,11",
                    "steps": ["Sort by finish time", "Select first activity", "Select next if start >= last finish"]
                }
            ]
        },
        "dynamic_programming": {
            "title": "Dynamic Programming",
            "summary": "Dynamic programming solves complex problems by breaking them into overlapping subproblems, solving each subproblem once, and storing results.",
            "key_points": [
                "Optimal substructure and overlapping subproblems",
                "Memoization (top-down) vs Tabulation (bottom-up)",
                "State transition equation defines relationship"
            ],
            "formulas": [
                {
                    "name": "0/1 Knapsack",
                    "latex": "$$dp[i][w] = \\max(dp[i-1][w],\\ dp[i-1][w-wt[i]] + val[i])$$",
                    "explanation": "Choose max between excluding or including item i"
                },
                {
                    "name": "LCS",
                    "latex": "$$dp[i][j] = \\begin{cases}dp[i-1][j-1]+1 & \\text{if } X[i]=Y[j] \\\\ \\max(dp[i-1][j], dp[i][j-1]) & \\text{otherwise}\\end{cases}$$",
                    "explanation": "Longest Common Subsequence"
                }
            ],
            "examples": [
                {
                    "question": "0/1 Knapsack: weights=[2,3,4,5], values=[3,4,5,6], capacity=8",
                    "answer": "Maximum value = 10",
                    "steps": ["Build DP table", "Fill using recurrence", "dp[4][8] = 10"]
                }
            ]
        },
        "graph_algorithms": {
            "title": "Graph Algorithms",
            "summary": "Graph algorithms solve problems on vertices and edges including traversal, shortest paths, and minimum spanning trees.",
            "key_points": [
                "BFS: shortest paths in unweighted graphs",
                "DFS: cycle detection, connectivity",
                "Dijkstra: non-negative edge weights",
                "Bellman-Ford: negative edge weights allowed"
            ],
            "formulas": [
                {
                    "name": "Dijkstra",
                    "latex": "$$O((V+E) \\log V)$$",
                    "explanation": "With binary heap priority queue"
                },
                {
                    "name": "Bellman-Ford",
                    "latex": "$$O(VE)$$",
                    "explanation": "Relax all edges V-1 times"
                },
                {
                    "name": "Floyd-Warshall",
                    "latex": "$$O(V^3)$$",
                    "explanation": "All-pairs shortest paths"
                }
            ],
            "examples": [
                {
                    "question": "Run Dijkstra from source A on graph with edges AB=7, AC=9, AD=14, BC=10, CD=11, BD=15",
                    "answer": "Shortest distances: A=0, B=7, C=9, D=20",
                    "steps": ["Initialize distances", "Extract min (A)", "Update neighbors", "Extract B, update C to 17", "Extract C (dist 9), update D to 20", "Extract D (dist 20)"]
                }
            ]
        }
    },
    "CS202": {
        "number_systems": {
            "title": "Number Systems",
            "summary": "Computer arithmetic uses binary, octal, and hexadecimal representations. Two's complement handles signed integers.",
            "key_points": [
                "Binary base 2, Octal base 8, Hexadecimal base 16",
                "Two's complement: invert bits + 1 for negative",
                "Overflow occurs when result exceeds representable range"
            ],
            "formulas": [
                {
                    "name": "2's Complement Range",
                    "latex": "$$-2^{n-1} \\text{ to } 2^{n-1} - 1$$",
                    "explanation": "For n-bit signed integer"
                },
                {
                    "name": "Hex to Binary",
                    "latex": "$$0xF4 = 1111\\ 0100$$",
                    "explanation": "Each hex digit = 4 binary digits"
                }
            ],
            "examples": [
                {
                    "question": "Convert 45 to 8-bit 2's complement",
                    "answer": "00101101",
                    "steps": ["45 in binary: 101101", "Pad to 8 bits: 00101101", "Positive number, done"]
                },
                {
                    "question": "Find -45 in 8-bit 2's complement",
                    "answer": "11010011",
                    "steps": ["45: 00101101", "Invert: 11010010", "Add 1: 11010011"]
                }
            ]
        },
        "pipelining": {
            "title": "Pipelining",
            "summary": "Pipelining overlaps instruction execution to improve throughput by dividing processing into stages.",
            "key_points": [
                "5-stage pipeline: IF, ID, EX, MEM, WB",
                "Hazards: data, control, structural",
                "Forwarding/bypassing solves data hazards"
            ],
            "formulas": [
                {
                    "name": "Pipeline Speedup",
                    "latex": "$$S = \\frac{n}{1 + (n-1) \\times stall\\_ratio}$$",
                    "explanation": "Speedup from pipelining"
                },
                {
                    "name": "Ideal CPI",
                    "latex": "$$CPI = 1$$",
                    "explanation": "One instruction completes per cycle"
                }
            ],
            "examples": [
                {
                    "question": "5-stage pipeline, 100 instructions, 10% branch misprediction (2 stall cycles). Calculate cycles.",
                    "answer": "118 cycles",
                    "steps": ["100 instructions × 1 cycle = 100", "10 branches × 2 stalls = 20", "But first instruction takes 5 cycles", "Total: 5 + 99 + 14 = 118"]
                }
            ]
        }
    },
    "CS203": {
        "process_management": {
            "title": "Process Management",
            "summary": "Processes are programs in execution. The OS manages process creation, termination, and inter-process communication.",
            "key_points": [
                "Process states: New, Ready, Running, Waiting, Terminated",
                "PCB (Process Control Block) stores process info",
                "Context switching saves/loads process state"
            ],
            "formulas": [
                {
                    "name": "Process States",
                    "latex": "New → Ready → Running → (Waiting) → Terminated",
                    "explanation": "Process state transition diagram"
                }
            ],
            "examples": [
                {
                    "question": "Explain fork() system call behavior",
                    "answer": "Creates child process, returns PID to parent, 0 to child",
                    "code": """pid_t pid = fork();
if (pid == 0) {
    // Child process
} else if (pid > 0) {
    // Parent process
} else {
    // Fork failed
}"""
                }
            ]
        },
        "cpu_scheduling": {
            "title": "CPU Scheduling",
            "summary": "CPU scheduling determines which process runs next. Algorithms include FCFS, SJF, Priority, Round Robin, and Multilevel Queue.",
            "key_points": [
                "FCFS: First Come First Served (non-preemptive)",
                "SJF: Shortest Job First (optimal average wait time)",
                "RR: Round Robin (preemptive, time quantum)",
                "Metrics: Turnaround time, Waiting time, Response time"
            ],
            "formulas": [
                {
                    "name": "Turnaround Time",
                    "latex": "$$TAT = Completion\\ Time - Arrival\\ Time$$",
                    "explanation": "Total time from submission to completion"
                },
                {
                    "name": "Waiting Time",
                    "latex": "$$WT = TAT - Burst\\ Time$$",
                    "explanation": "Time spent waiting in ready queue"
                },
                {
                    "name": "Average Waiting Time",
                    "latex": "$$AWT = \\frac{\\sumWT_i}{n}$$",
                    "explanation": "Mean waiting time across all processes"
                }
            ],
            "examples": [
                {
                    "question": "Processes P1(10), P2(29), P3(3) with FCFS. Calculate AWT.",
                    "answer": "19.67",
                    "steps": ["P1: WT=0", "P2: WT=10", "P3: WT=39", "AWT = (0+10+39)/3 = 16.33"]
                },
                {
                    "question": "Same processes with SJF (non-preemptive). Calculate AWT.",
                    "answer": "9.67",
                    "steps": ["P3(3): WT=0", "P1(10): WT=3", "P2(29): WT=13", "AWT = (0+3+13)/3 = 5.33"]
                }
            ]
        },
        "process_synchronization": {
            "title": "Process Synchronization",
            "summary": "Process synchronization ensures coordinated access to shared resources using critical section protocols, semaphores, and monitors.",
            "key_points": [
                "Critical section requires: mutual exclusion, progress, bounded waiting",
                "Semaphore: counter with wait/signal operations",
                "Monitor: high-level synchronization with condition variables"
            ],
            "formulas": [
                {
                    "name": "Critical Section Requirements",
                    "latex": "1. Mutual Exclusion\\n2. Progress\\n3. Bounded Waiting",
                    "explanation": "Three requirements for valid solution"
                }
            ],
            "examples": [
                {
                    "question": "Implement Producer-Consumer with semaphore",
                    "answer": "Use empty, full, mutex semaphores",
                    "code": """semaphore mutex = 1, empty = n, full = 0;

producer() {
    while (true) {
        produce item
        wait(empty)
        wait(mutex)
        put item in buffer
        signal(mutex)
        signal(full)
    }
}

consumer() {
    while (true) {
        wait(full)
        wait(mutex)
        remove item from buffer
        signal(mutex)
        signal(empty)
        consume item
    }
}"""
                }
            ]
        },
        "deadlock": {
            "title": "Deadlock",
            "summary": "Deadlock occurs when processes wait for resources held by each other. Solutions include prevention, avoidance, detection, and recovery.",
            "key_points": [
                "Coffman conditions: mutual exclusion, hold and wait, no preemption, circular wait",
                "Deadlock prevention: break one condition",
                "Banker's algorithm: safe state avoidance",
                "Detection: resource allocation graph"
            ],
            "formulas": [
                {
                    "name": "Banker's Need",
                    "latex": "$$Need = Max - Allocation$$",
                    "explanation": "Resources still needed by process"
                }
            ],
            "examples": [
                {
                    "question": "Check if system is in safe state with Available=[3,3,2], Max and Allocation matrices given",
                    "answer": "Safe sequence: P1, P0, P2",
                    "steps": ["Calculate Need", "Find process with Need ≤ Available", "Release resources, repeat"]
                }
            ]
        }
    },
    "CS204": {
        "er_modeling": {
            "title": "ER Modeling",
            "summary": "Entity-Relationship modeling visualizes database structure using entities, attributes, relationships, and cardinalities.",
            "key_points": [
                "Entities: real-world objects",
                "Attributes: properties of entities",
                "Relationships: associations between entities",
                "Cardinality: 1:1, 1:N, M:N"
            ],
            "formulas": [
                {
                    "name": "Cardinality Notation",
                    "latex": "1:1,\\ 1:N,\\ M:N",
                    "explanation": "Relationship cardinalities"
                }
            ],
            "examples": [
                {
                    "question": "Design ER for university database",
                    "answer": "Entities: Student, Course, Instructor, Department",
                    "steps": ["Identify entities and attributes", "Define relationships with cardinality", "Convert to tables"]
                }
            ]
        },
        "normalization": {
            "title": "Database Normalization",
            "summary": "Normalization organizes data to minimize redundancy. Forms range from 1NF to BCNF, each with stricter requirements.",
            "key_points": [
                "1NF: Atomic values, no repeating groups",
                "2NF: 1NF + no partial dependency",
                "3NF: 2NF + no transitive dependency",
                "BCNF: For every FD X→Y, X is superkey"
            ],
            "formulas": [
                {
                    "name": "Functional Dependency",
                    "latex": "$$X \\rightarrow Y$$",
                    "explanation": "Value of X determines value of Y"
                },
                {
                    "name": "Armstrong's Axioms",
                    "latex": "Reflexivity\\nAugmentation\\nTransitivity",
                    "explanation": "Inference rules for FDs"
                }
            ],
            "examples": [
                {
                    "question": "Decompose R(A,B,C,D) with FDs: A→B, B→C, C→D to 3NF",
                    "answer": "R1(A,B), R2(B,C), R3(C,D)",
                    "steps": ["Find candidate key: A", "Check 2NF: A→B (no partial)", "Check 3NF: B→C (B not superkey, C not prime)", "Decompose"]
                }
            ]
        }
    }
}

# ===== YEAR 2 - SEMESTER 4 STUDY CONTENT =====
YEAR2_SEM4_CONTENT = {
    "CS301": {
        "network_fundamentals": {
            "title": "Network Fundamentals",
            "summary": "Computer networks connect devices for communication. The OSI and TCP/IP models standardize network layers.",
            "key_points": [
                "OSI: 7 layers (Physical to Application)",
                "TCP/IP: 4 layers (Link to Application)",
                "Encapsulation adds headers at each layer",
                "Protocols: IP, TCP, UDP, HTTP, DNS"
            ],
            "formulas": [
                {
                    "name": "Encapsulation",
                    "latex": "Data → Segment → Packet → Frame → Bits",
                    "explanation": "Layer-by-layer header addition"
                }
            ],
            "examples": [
                {
                    "question": "Trace HTTP request through OSI layers",
                    "answer": "Application → Presentation → Session → Transport → Network → Data Link → Physical",
                    "steps": ["HTTP request created", "TLS encryption (Presentation)", "Session management", "TCP segment", "IP packet", "MAC frame", "Binary signal"]
                }
            ]
        },
        "data_link_layer": {
            "title": "Data Link Layer",
            "summary": "The data link layer provides reliable node-to-node delivery using framing, error detection, and MAC protocols.",
            "key_points": [
                "Framing: delimiting message boundaries",
                "Error detection: CRC for bit-level errors",
                "MAC protocols: CSMA/CD, CSMA/CA"
            ],
            "formulas": [
                {
                    "name": "CRC",
                    "latex": "$$Remainder = Data \\mod Generator$$",
                    "explanation": "Cyclic Redundancy Check for error detection"
                },
                {
                    "name": "CSMA/CD Efficiency",
                    "latex": "$$\\eta = \\frac{1}{1 + 6.4 \\times (T_p/T_t)}$$",
                    "explanation": "Efficiency for Ethernet with collision detection"
                },
                {
                    "name": "Propagation Factor",
                    "latex": "$$a = \\frac{T_p}{T_t}$$",
                    "explanation": "Ratio of propagation time to transmission time"
                }
            ],
            "examples": [
                {
                    "question": "Data=101101, Generator=1011. Find CRC remainder.",
                    "answer": "010",
                    "steps": ["Append 3 zeros: 101101000", "Divide by 1011 using XOR", "Remainder = 010"]
                }
            ]
        }
    },
    "CS302": {
        "oop_concepts": {
            "title": "OOP Concepts",
            "summary": "Object-Oriented Programming uses objects, classes, inheritance, polymorphism, and encapsulation.",
            "key_points": [
                "Encapsulation: bundling data and methods",
                "Inheritance: code reuse",
                "Polymorphism: same interface, different implementations",
                "Abstraction: hiding implementation details"
            ],
            "formulas": [
                {
                    "name": "Java Class Template",
                    "latex": "$$public\\ class\\ ClassName\\ \\{\\\\\\ private\\ fields\\\\\\ public\\ methods\\ \\}$$",
                    "explanation": "Basic class structure"
                }
            ],
            "examples": [
                {
                    "question": "Implement inheritance in Java",
                    "answer": "Use extends keyword",
                    "code": """class Animal {
    void eat() { System.out.println("eating"); }
}
class Dog extends Animal {
    void bark() { System.out.println("barking"); }
}
class TestInheritance {
    public static void main(String args[]) {
        Dog d = new Dog();
        d.eat(); // inherited
        d.bark(); // own
    }
}"""
                }
            ],
            "flashcards": [
                {"front": "What is the difference between Method Overloading and Method Overriding?", "back": "Overloading occurs at compile-time with same method name but different parameters; Overriding occurs at runtime when a subclass redefines a superclass method.", "hint": "Compile-time vs Runtime polymorphism"},
                {"front": "What is Encapsulation in OOP?", "back": "Bundling data (attributes) and methods that operate on that data into a single unit (class), restricting direct access to internal state.", "hint": "Data hiding"}
            ]
        }
    },
    "CS303": {
        "automata_and_grammars": {
            "title": "Automata and Formal Languages",
            "summary": "Theoretical foundations of computation covering Finite Automata (DFA/NFA), Regular Expressions, Context-Free Grammars (CFG), Pushdown Automata (PDA), and Turing Machines.",
            "key_points": [
                "DFA and NFA recognize exactly the class of Regular Languages",
                "Pumping Lemma is used to prove languages are non-regular",
                "CFGs generate context-free languages recognized by Pushdown Automata",
                "Turing Machines model general algorithms and define decidability",
                "Halting Problem is undecidable by Turing Machines"
            ],
            "formulas": [
                {
                    "name": "Pumping Lemma for Regular Languages",
                    "latex": "$$w = xyz, \\quad |y| \\ge 1, \\quad |xy| \\le p, \\quad xy^i z \\in L$$",
                    "explanation": "Condition that any sufficiently long regular string must satisfy"
                }
            ],
            "flashcards": [
                {"front": "What is the key difference between DFA and NFA?", "back": "DFA has exactly one deterministic transition per state-symbol pair; NFA allows zero, one, or multiple transitions including epsilon transitions.", "hint": "Determinism"},
                {"front": "What type of language is recognized by a Pushdown Automaton (PDA)?", "back": "Context-Free Languages (CFLs), using an internal stack for memory.", "hint": "Stack memory"},
                {"front": "What does the Halting Problem prove?", "back": "No general algorithm can decide whether an arbitrary computer program with given input will eventually halt or run forever.", "hint": "Undecidability"}
            ],
            "difficulty": "Advanced"
        }
    },
    "CS304": {
        "sdlc_and_architecture": {
            "title": "Software Engineering and Design Patterns",
            "summary": "Systematic software development methodologies including Agile/Scrum, requirements engineering, architectural styles, SOLID design principles, and design patterns.",
            "key_points": [
                "Agile emphasizes iterative delivery and responding to change",
                "SOLID principles ensure maintainable, extensible object-oriented code",
                "Design patterns provide reusable templates for common architectural problems",
                "Unit testing and continuous integration improve software quality"
            ],
            "formulas": [
                {
                    "name": "Cyclomatic Complexity",
                    "latex": "$$V(G) = E - N + 2P$$",
                    "explanation": "Measure of software complexity from control flow graph"
                }
            ],
            "flashcards": [
                {"front": "What does the Single Responsibility Principle (SRP) in SOLID state?", "back": "A module, class, or function should have one, and only one, reason to change.", "hint": "One reason to change"},
                {"front": "What is the difference between Verification and Validation?", "back": "Verification asks 'Are we building the product right?' (spec compliance); Validation asks 'Are we building the right product?' (user needs).", "hint": "Right product vs building right"},
                {"front": "What is the Singleton design pattern?", "back": "A creational pattern that ensures a class has only one instance and provides a global access point to it.", "hint": "Single instance"}
            ],
            "difficulty": "Intermediate"
        }
    }
}

# ===== YEAR 3 - SEMESTER 5 STUDY CONTENT =====
YEAR3_SEM5_CONTENT = {
    "CS401": {
        "search_algorithms": {
            "title": "Search Algorithms",
            "summary": "Search algorithms explore state spaces to find solutions. uninformed (BFS, DFS) and informed (A*, Hill Climbing) approaches.",
            "key_points": [
                "BFS: Complete, optimal for uniform cost",
                "DFS: Not optimal, uses less memory",
                "A*: Complete, optimal with admissible heuristic",
                "Hill Climbing: Local optimum problem"
            ],
            "formulas": [
                {
                    "name": "A* Heuristic",
                    "latex": "$$f(n) = g(n) + h(n)$$",
                    "explanation": "g(n)=cost so far, h(n)=estimated to goal"
                },
                {
                    "name": "Admissible Heuristic",
                    "latex": "$$h(n) \\leq h^*(n)$$",
                    "explanation": "Never overestimates true cost"
                }
            ],
            "examples": [
                {
                    "question": "A* search on graph with h(n) = straight-line distance",
                    "answer": "Expands nodes with lowest f(n)=g(n)+h(n)",
                    "steps": ["Start at initial state", "Generate successors", "Calculate f(n) for each", "Expand node with minimum f(n)"]
                }
            ]
        },
        "machine_learning_basics": {
            "title": "Machine Learning Basics",
            "summary": "Machine learning enables computers to learn from data without explicit programming. Types include supervised, unsupervised, and reinforcement learning.",
            "key_points": [
                "Supervised: labeled data (classification, regression)",
                "Unsupervised: unlabeled data (clustering, dimensionality reduction)",
                "Reinforcement: learning from interactions",
                "Training set, test set, validation set split"
            ],
            "formulas": [
                {
                    "name": "Accuracy",
                    "latex": "$$Accuracy = \\frac{TP + TN}{TP + TN + FP + FN}$$",
                    "explanation": "Classification accuracy"
                },
                {
                    "name": "Precision",
                    "latex": "$$Precision = \\frac{TP}{TP + FP}$$",
                    "explanation": "Relevance of positive predictions"
                },
                {
                    "name": "Recall",
                    "latex": "$$Recall = \\frac{TP}{TP + FN}$$",
                    "explanation": "Fraction of positives retrieved"
                }
            ],
            "examples": [
                {
                    "question": "Calculate precision and recall for classifier",
                    "answer": "Given confusion matrix values",
                    "steps": ["TP=50, FP=10, FN=5, TN=100", "Precision = 50/(50+10) = 0.833", "Recall = 50/(50+5) = 0.909"]
                }
            ]
        }
    },
    "CS402": {
        "regression": {
            "title": "Regression",
            "summary": "Regression predicts continuous values. Linear regression models linear relationships, logistic regression handles classification.",
            "key_points": [
                "Linear regression: y = mx + c",
                "Gradient descent: iterative optimization",
                "Cost function: MSE for linear regression"
            ],
            "formulas": [
                {
                    "name": "Linear Regression",
                    "latex": "$$y = \\beta_0 + \\beta_1 x$$",
                    "explanation": "Simple linear regression"
                },
                {
                    "name": "Cost Function (MSE)",
                    "latex": "$$J(\\theta) = \\frac{1}{2m} \\sum_{i=1}^m (h_\\theta(x^{(i)}) - y^{(i)})^2$$",
                    "explanation": "Mean Squared Error"
                },
                {
                    "name": "Gradient Descent Update",
                    "latex": "$$\\theta_j := \\theta_j - \\alpha \\frac{\\partial J}{\\partial \\theta_j}$$",
                    "explanation": "Update rule for optimization"
                }
            ],
            "examples": [
                {
                    "question": "Gradient descent for y = 2x + 1 with noisy data",
                    "answer": "Iteratively update θ to minimize cost",
                    "steps": ["Initialize θ randomly", "Compute gradient", "Update θ = θ - α × gradient", "Repeat until convergence"]
                }
            ]
        },
        "classification": {
            "title": "Classification",
            "summary": "Classification predicts discrete labels. Decision trees, SVM, Naive Bayes, and KNN are popular algorithms.",
            "key_points": [
                "Decision trees: split on features",
                "SVM: find optimal hyperplane",
                "Naive Bayes: probabilistic with feature independence",
                "KNN: lazy learning based on neighbors"
            ],
            "formulas": [
                {
                    "name": "Information Gain",
                    "latex": "$$IG(S, A) = H(S) - \\sum_{v \\in Values(A)} \\frac{|S_v|}{|S|} H(S_v)$$",
                    "explanation": "Decision tree splitting criterion"
                },
                {
                    "name": "Bayes Theorem",
                    "latex": "$$P(y|x) = \\frac{P(x|y)P(y)}{P(x)}$$",
                    "explanation": "Naive Bayes classification"
                }
            ],
            "examples": [
                {
                    "question": "Decision tree for weather data",
                    "answer": "Split on outlook, then temperature, humidity, wind",
                    "steps": ["Calculate entropy of dataset", "Calculate information gain for each feature", "Split on highest gain feature", "Repeat recursively"]
                }
            ],
            "flashcards": [
                {"front": "What is the difference between Generative and Discriminative models in ML?", "back": "Generative models learn joint probability P(X, Y) to model distribution; Discriminative models learn conditional probability P(Y|X) to find decision boundaries.", "hint": "Joint vs Conditional probability"},
                {"front": "What is the purpose of the Kernel Trick in Support Vector Machines (SVM)?", "back": "Maps non-linearly separable data into higher-dimensional feature space where it becomes linearly separable without explicitly computing coordinates.", "hint": "High-dimensional mapping"}
            ]
        }
    },
    "CS403": {
        "web_architecture": {
            "title": "Web Technologies and Full-Stack Development",
            "summary": "Modern web architecture encompassing semantic HTML5, CSS responsive layouts (Flexbox/Grid), asynchronous JavaScript (Promises/Async-Await), and RESTful API backend design.",
            "key_points": [
                "DOM represents structured HTML documents as an accessible node tree",
                "Event loop processes asynchronous callbacks via microtask and macrotask queues",
                "REST APIs use standard HTTP verbs (GET, POST, PUT, DELETE) and status codes",
                "CORS controls cross-origin HTTP requests between browser and backend"
            ],
            "formulas": [
                {
                    "name": "HTTP Status Code Ranges",
                    "latex": "2xx: Success, \\quad 3xx: Redirection, \\quad 4xx: Client Error, \\quad 5xx: Server Error",
                    "explanation": "Standard HTTP response classifications"
                }
            ],
            "flashcards": [
                {"front": "Explain the JavaScript Event Loop mechanism", "back": "Monitors Call Stack and Task Queues; executes synchronous code first, then microtasks (Promises), then macrotasks (setTimeout/I/O).", "hint": "Async execution"},
                {"front": "What is the difference between PUT and PATCH in REST APIs?", "back": "PUT completely replaces the target resource; PATCH applies partial modifications to the resource.", "hint": "Full vs partial update"},
                {"front": "What is CORS (Cross-Origin Resource Sharing)?", "back": "A browser security mechanism that uses HTTP headers to restrict resource requests from domains outside the originating origin.", "hint": "Browser security policy"}
            ],
            "difficulty": "Intermediate"
        }
    },
    "CS404": {
        "cryptography_and_security": {
            "title": "Cyber Security and Cryptography",
            "summary": "Core information security principles covering the CIA triad, symmetric/asymmetric cryptography, hash functions, network security, and web vulnerability mitigation (OWASP Top 10).",
            "key_points": [
                "CIA Triad: Confidentiality, Integrity, and Availability",
                "Symmetric encryption uses single shared key (AES); Asymmetric uses public-private keypairs (RSA)",
                "Cryptographic hashes (SHA-256) are deterministic, one-way, and collision-resistant",
                "SQL Injection and XSS are prevented by parameterized queries and contextual output encoding"
            ],
            "formulas": [
                {
                    "name": "RSA Key Generation",
                    "latex": "$$n = p \\times q, \\quad \\phi(n) = (p-1)(q-1), \\quad e \\cdot d \\equiv 1 \\pmod{\\phi(n)}$$",
                    "explanation": "Mathematical foundation of RSA public key cryptosystem"
                }
            ],
            "flashcards": [
                {"front": "What is the difference between Symmetric and Asymmetric Encryption?", "back": "Symmetric encryption uses one shared secret key for both encryption and decryption; Asymmetric uses a public key to encrypt and private key to decrypt.", "hint": "Shared vs key pair"},
                {"front": "What is a Man-in-the-Middle (MITM) attack?", "back": "An attack where the adversary secretly intercepts and alters communications between two parties who believe they are communicating directly.", "hint": "Interception"},
                {"front": "How do Parameterized Queries prevent SQL Injection?", "back": "They treat user input strictly as literal data parameters, preventing input from altering the SQL command syntax.", "hint": "Data vs code separation"}
            ],
            "difficulty": "Intermediate"
        }
    }
}

# ===== YEAR 3 - SEMESTER 6 STUDY CONTENT =====
YEAR3_SEM6_CONTENT = {
    "CS501": {
        "syntax_analysis": {
            "title": "Syntax Analysis",
            "summary": "Syntax analysis (parsing) checks if source code follows language grammar. Top-down and bottom-up are two parsing approaches.",
            "key_points": [
                "Top-down: predictive, recursive descent",
                "Bottom-up: shift-reduce, LR parsers",
                "LL(1) and LR(1) are common parser types",
                "Ambiguity causes parsing problems"
            ],
            "formulas": [
                {
                    "name": "LL(1) Grammar",
                    "latex": "$$Predictive\\ parsing\\ with\\ 1\\ token\\ lookahead$$",
                    "explanation": "Left-to-right, Leftmost derivation, 1 token"
                }
            ],
            "examples": [
                {
                    "question": "Parse 'id + id * id' using operator precedence",
                    "answer": "id + (id * id)",
                    "steps": ["id has highest precedence", "* has higher than +", "Parse as id + (id * id)"]
                }
            ],
            "flashcards": [
                {"front": "What is the difference between Top-Down and Bottom-Up Parsing?", "back": "Top-down parsing starts from root non-terminal and attempts to construct parse tree downwards; Bottom-up starts from input tokens and reduces them towards start symbol.", "hint": "Direction of parse tree construction"},
                {"front": "What is an Ambiguous Grammar?", "back": "A context-free grammar that can produce two or more distinct leftmost (or rightmost) derivations or parse trees for the same input string.", "hint": "Multiple parse trees"}
            ]
        }
    },
    "CS502": {
        "cloud_architecture": {
            "title": "Cloud Computing and Virtualization",
            "summary": "Cloud infrastructure models (IaaS, PaaS, SaaS), hypervisor virtualization, containerization (Docker, Kubernetes), auto-scaling, and distributed cloud storage.",
            "key_points": [
                "IaaS provides raw infrastructure; PaaS provides runtime platform; SaaS provides end-user applications",
                "Type 1 hypervisors run on bare metal; Type 2 run on host OS",
                "Containers share the host kernel, offering lightweight virtualization compared to VMs",
                "Elasticity allows compute capacity to scale dynamically based on real-time traffic demand"
            ],
            "formulas": [
                {
                    "name": "Cloud Availability Formula",
                    "latex": "$$\\text{Availability} = \\frac{\\text{MTBF}}{\\text{MTBF} + \\text{MTTR}} \\times 100\\%$$",
                    "explanation": "MTBF=Mean Time Between Failures, MTTR=Mean Time To Repair"
                }
            ],
            "flashcards": [
                {"front": "Compare IaaS, PaaS, and SaaS cloud delivery models", "back": "IaaS provides raw compute/storage (AWS EC2); PaaS provides runtime platform (Heroku/AppEngine); SaaS provides finished web applications (Google Docs).", "hint": "Management levels"},
                {"front": "What is the primary difference between a Container and a Virtual Machine?", "back": "VMs virtualize hardware and run complete guest OSes; Containers share the host OS kernel and package only the application and dependencies.", "hint": "Kernel sharing"},
                {"front": "What is horizontal scaling vs vertical scaling in cloud systems?", "back": "Horizontal scaling adds more machine instances; Vertical scaling upgrades existing machine capacity (CPU/RAM).", "hint": "Scale out vs scale up"}
            ],
            "difficulty": "Intermediate"
        }
    },
    "CS503": {
        "data_analytics": {
            "title": "Data Science and Statistical Modeling",
            "summary": "Data analytics lifecycle including data wrangling, missing value imputation, feature engineering, exploratory data analysis (EDA), and predictive statistical inference.",
            "key_points": [
                "Data wrangling cleans, structures, and enriches raw datasets",
                "EDA uncovers patterns, anomalies, and distributions using statistical visualizations",
                "Standardization (z-score) and Normalization scale numerical features for machine learning models",
                "Correlation does not imply causation"
            ],
            "formulas": [
                {
                    "name": "Z-Score Standardization",
                    "latex": "$$z = \\frac{x - \\mu}{\\sigma}$$",
                    "explanation": "Transforms feature distribution to mean 0 and standard deviation 1"
                }
            ],
            "flashcards": [
                {"front": "What is the difference between Standard Normalization (Z-score) and Min-Max Scaling?", "back": "Z-score scales data to mean=0, std=1; Min-Max scales data to a fixed bounded range [0, 1].", "hint": "Scaling range & distribution"},
                {"front": "What is the purpose of Exploratory Data Analysis (EDA)?", "back": "To summarize main characteristics of datasets, detect outliers, uncover underlying patterns, and formulate hypotheses before modeling.", "hint": "Data discovery"},
                {"front": "Explain the difference between Overfitting and Underfitting", "back": "Overfitting captures noise and performs well only on training data (high variance); Underfitting fails to capture trends (high bias).", "hint": "Bias vs Variance"}
            ],
            "difficulty": "Intermediate"
        }
    }
}

# ===== YEAR 4 - SEMESTER 7 STUDY CONTENT =====
YEAR4_SEM7_CONTENT = {
    "CS601": {
        "deep_neural_networks": {
            "title": "Deep Neural Networks",
            "summary": "Deep neural networks have multiple hidden layers, enabling learning of complex representations for tasks like image recognition and NLP.",
            "key_points": [
                "Depth enables hierarchical feature learning",
                "Backpropagation computes gradients",
                "Dropout and batch normalization prevent overfitting",
                "Adam optimizer combines momentum and adaptive learning"
            ],
            "formulas": [
                {
                    "name": "ReLU Activation",
                    "latex": "$$ReLU(x) = \\max(0, x)$$",
                    "explanation": "Rectified Linear Unit"
                },
                {
                    "name": "Dropout",
                    "latex": "$$output = \\begin{cases}0 & \\text{with probability p} \\\\ \\frac{input}{1-p} & \\text{otherwise}\\end{cases}$$",
                    "explanation": "Randomly sets inputs to zero during training"
                },
                {
                    "name": "Batch Normalization",
                    "latex": "$$\\hat{x} = \\frac{x - \\mu_B}{\\sqrt{\\sigma_B^2 + \\epsilon}}$$",
                    "explanation": "Normalizes layer inputs"
                }
            ],
            "examples": [
                {
                    "question": "MLP for binary classification",
                    "answer": "Input → Hidden layers → Sigmoid output",
                    "code": """model = Sequential([
    Dense(64, activation='relu', input_shape=(784,)),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid')
])"""
                }
            ],
            "flashcards": [
                {"front": "Why is the ReLU activation preferred over Sigmoid in deep neural networks?", "back": "ReLU avoids vanishing gradients for positive inputs and has much faster computation (constant derivative 1 for x > 0).", "hint": "Vanishing gradient"},
                {"front": "What does Dropout do during neural network training?", "back": "Randomly deactivates a fraction p of neurons during each forward pass to prevent co-adaptation and overfitting.", "hint": "Regularization"}
            ]
        },
        "convolutional_neural_networks": {
            "title": "Convolutional Neural Networks",
            "summary": "CNNs use convolution layers to automatically extract features from images, making them ideal for computer vision tasks.",
            "key_points": [
                "Convolution: filter slides over input",
                "Pooling: downsample feature maps",
                "Transfer learning: reuse pre-trained models",
                "Data augmentation: increase training data"
            ],
            "formulas": [
                {
                    "name": "Convolution Output Size",
                    "latex": "$$Output = \\frac{W - F + 2P}{S} + 1$$",
                    "explanation": "W=input size, F=filter size, P=padding, S=stride"
                },
                {
                    "name": "Max Pooling",
                    "latex": "$$Output_{i,j} = \\max_{(x,y) \\in window} Input_{i+x, j+y}$$",
                    "explanation": "Selects maximum in each window"
                }
            ],
            "examples": [
                {
                    "question": "LeNet architecture for MNIST",
                    "answer": "2 conv + 2 pooling + 2 fully connected",
                    "code": """model = Sequential([
    Conv2D(6, (5,5), activation='relu', input_shape=(28,28,1)),
    MaxPooling2D((2,2)),
    Conv2D(16, (5,5), activation='relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(120, activation='relu'),
    Dense(84, activation='relu'),
    Dense(10, activation='softmax')
])"""
                }
            ],
            "flashcards": [
                {"front": "What is parameter sharing in Convolutional Neural Networks?", "back": "The same filter weights are applied across all spatial positions of the input image, drastically reducing parameter count.", "hint": "Weight sharing"},
                {"front": "What is the purpose of Max Pooling in CNNs?", "back": "Reduces spatial dimensions (downsampling), lowers computational complexity, and provides translation invariance.", "hint": "Downsampling"}
            ]
        },
        "recurrent_neural_networks": {
            "title": "Recurrent Neural Networks",
            "summary": "RNNs process sequences by maintaining hidden state that captures information from previous timesteps.",
            "key_points": [
                "Hidden state carries information across timesteps",
                "Vanishing gradient problem in deep RNNs",
                "LSTM and GRU use gating mechanisms",
                "Bidirectional RNNs process in both directions"
            ],
            "formulas": [
                {
                    "name": "RNN Hidden State",
                    "latex": "$$h_t = \\tanh(W_{hh}h_{t-1} + W_{xh}x_t + b_h)$$",
                    "explanation": "Standard RNN recurrence"
                },
                {
                    "name": "LSTM Gate",
                    "latex": "$$f_t = \\sigma(W_f [h_{t-1}, x_t])$$",
                    "explanation": "Forget gate in LSTM"
                }
            ],
            "examples": [
                {
                    "question": "LSTM for text generation",
                    "answer": "Character-level RNN",
                    "code": """model = Sequential([
    LSTM(128, input_shape=(seq_len, vocab_size)),
    Dense(vocab_size, activation='softmax')
])"""
                }
            ],
            "flashcards": [
                {"front": "How does an LSTM cell solve the vanishing gradient problem?", "back": "Through a constant error carousel (cell state conveyor) regulated by forget, input, and output gates.", "hint": "Gated memory cell"}
            ]
        }
    },
    "CS602": {
        "hadoop_ecosystem": {
            "title": "Hadoop Ecosystem",
            "summary": "Hadoop is a distributed computing framework for processing big data across clusters of computers.",
            "key_points": [
                "HDFS: distributed file system",
                "MapReduce: distributed processing model",
                "YARN: resource management",
                "Ecosystem tools: Hive, Pig, HBase, Spark"
            ],
            "formulas": [
                {
                    "name": "HDFS Block Size",
                    "latex": "$$Default = 128\\ MB\\ (Hadoop\\ 2.x)$$",
                    "explanation": "Default block size for HDFS"
                }
            ],
            "examples": [
                {
                    "question": "HDFS write process",
                    "answer": "Client → NameNode → DataNodes",
                    "steps": ["Client requests write", "NameNode checks permissions and namespace", "Client splits file into blocks", "Blocks replicated to DataNodes"]
                }
            ],
            "flashcards": [
                {"front": "What are the roles of NameNode and DataNode in HDFS?", "back": "NameNode manages file system namespace and metadata; DataNodes store and retrieve actual data blocks.", "hint": "Master vs Worker"},
                {"front": "What is the key advantage of Apache Spark over Hadoop MapReduce?", "back": "In-memory RDD processing (up to 100x faster for iterative algorithms) instead of writing intermediate results to disk.", "hint": "In-memory processing"}
            ]
        }
    },
    "CS603": {
        "distributed_consensus": {
            "title": "Distributed Systems and Consensus",
            "summary": "Architecture of distributed systems covering RPCs, logical clocks (Lamport/Vector), distributed consensus algorithms (Paxos/Raft), and the CAP theorem trade-offs.",
            "key_points": [
                "Distributed systems lack a global shared clock and shared memory",
                "Lamport clocks establish partial causal ordering of distributed events",
                "Consensus algorithms (Raft/Paxos) achieve fault-tolerant agreement among distributed nodes",
                "CAP Theorem: Under network partition, a system can provide either Consistency or Availability, but not both"
            ],
            "formulas": [
                {
                    "name": "CAP Theorem",
                    "latex": "$$\\text{Consistency} + \\text{Availability} + \\text{Partition Tolerance} \\le 2$$",
                    "explanation": "Trade-off in distributed storage design"
                }
            ],
            "flashcards": [
                {"front": "State the CAP Theorem for distributed systems", "back": "A distributed data store can simultaneously guarantee at most two out of three: Consistency, Availability, and Partition Tolerance.", "hint": "Three-way trade-off"},
                {"front": "What is the Raft Consensus Algorithm designed for?", "back": "Achieving distributed state machine replication and leader election across a cluster in an understandable, fault-tolerant manner.", "hint": "Leader election & log replication"},
                {"front": "What are Lamport Logical Clocks?", "back": "A monotonically increasing counter mechanism used to determine the partial causal order of events in distributed systems.", "hint": "Happens-before relation"}
            ],
            "difficulty": "Advanced"
        }
    },
    "CS699": {
        "project_formulation": {
            "title": "Major Project Planning and Problem Formulation",
            "summary": "Engineering methodology for capstone projects: literature review, problem formulation, feasibility study, system requirements, architectural diagrams, and milestone planning.",
            "key_points": [
                "Clear problem statements specify the domain, bottleneck, and measurable objectives",
                "Comprehensive literature survey establishes current state-of-the-art benchmarks",
                "System architecture diagrams define component interfaces and data pipelines",
                "Gantt charts and agile sprint backlogs ensure milestone tracking"
            ],
            "formulas": [
                {
                    "name": "Critical Path Method (CPM)",
                    "latex": "$$\\text{Total Float} = LS - ES = LF - EF$$",
                    "explanation": "Slack time calculation for project scheduling"
                }
            ],
            "flashcards": [
                {"front": "What are the core components of an Engineering Problem Statement?", "back": "Context/Domain, Identified Gap/Deficiency, Proposed Solution Concept, and Measurable Success Criteria.", "hint": "Gap & Objectives"},
                {"front": "What is the goal of a Technical Feasibility Study?", "back": "To evaluate whether the proposed project can be implemented with available hardware, software, datasets, and time constraints.", "hint": "Practical viability"},
                {"front": "What is the difference between Functional and Non-Functional Requirements?", "back": "Functional requirements define specific system behaviors/features; Non-functional requirements define quality attributes (latency, throughput, security).", "hint": "Behavior vs Performance"}
            ],
            "difficulty": "Intermediate"
        }
    }
}

# ===== YEAR 4 - SEMESTER 8 STUDY CONTENT =====
YEAR4_SEM8_CONTENT = {
    "CS701": {
        "nlp_transformers": {
            "title": "Natural Language Processing and Transformers",
            "summary": "Computational linguistics and modern deep learning for NLP: tokenization, word embeddings (Word2Vec, GloVe), self-attention, Transformers, and Large Language Models (LLMs).",
            "key_points": [
                "Tokenization converts text into discrete integer token sequences",
                "Word embeddings represent semantic similarity in continuous vector spaces",
                "Self-attention computes dynamic contextual representations across token positions",
                "Transformers enable parallelized sequence modeling using multi-head attention and positional encodings"
            ],
            "formulas": [
                {
                    "name": "Scaled Dot-Product Attention",
                    "latex": "$$\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$$",
                    "explanation": "Core self-attention equation in Transformers"
                }
            ],
            "flashcards": [
                {"front": "How does Self-Attention work in the Transformer architecture?", "back": "Computes attention weights between Query (Q), Key (K), and Value (V) matrices using softmax((Q * K^T) / sqrt(d_k)) * V.", "hint": "Q, K, V calculation"},
                {"front": "What is Byte-Pair Encoding (BPE) in NLP?", "back": "A subword tokenization algorithm that iteratively merges the most frequent pairs of characters or character sequences.", "hint": "Subword tokenization"},
                {"front": "What is the difference between BERT (encoder-only) and GPT (decoder-only)?", "back": "BERT is bidirectional for understanding tasks (classification/NER); GPT is autoregressive (causal masking) for text generation.", "hint": "Bidirectional vs Autoregressive"}
            ],
            "difficulty": "Advanced"
        }
    },
    "CS702": {
        "technical_interview_prep": {
            "title": "Technical Interview & System Design Preparation",
            "summary": "High-yield engineering interview strategies: core DSA patterns (Two Pointers, Sliding Window, DP, Graphs), scalable system design principles, and technical behavioral frameworks.",
            "key_points": [
                "Recognizing DSA algorithmic patterns enables rapid optimal problem-solving",
                "System design requires defining functional/non-functional requirements, estimating throughput/storage, and designing microservices",
                "Database scaling strategies include sharding, indexing, read replicas, and caching (Redis)",
                "STAR method (Situation, Task, Action, Result) structures behavioral interview answers"
            ],
            "formulas": [
                {
                    "name": "Throughput QPS Estimate",
                    "latex": "$$\\text{QPS} = \\frac{\\text{Daily Active Users} \\times \\text{Requests/User}}{86400}$$",
                    "explanation": "Estimates backend server capacity requirements"
                }
            ],
            "flashcards": [
                {"front": "When is the Sliding Window pattern optimal in DSA?", "back": "When solving array or string problems involving continuous subarrays/substrings meeting specific constraint criteria.", "hint": "Continuous subarray"},
                {"front": "What is the purpose of a Distributed Cache (e.g. Redis)?", "back": "Stores frequently accessed data in RAM to drastically reduce database load and achieve sub-millisecond read latencies.", "hint": "In-memory speed"},
                {"front": "What does the STAR framework stand for in engineering interviews?", "back": "Situation (context), Task (goal), Action (steps taken), Result (measurable outcome).", "hint": "Behavioral structure"}
            ],
            "difficulty": "Intermediate"
        }
    },
    "CS799": {
        "project_execution_defense": {
            "title": "Major Project Execution, Benchmarking, and Defense",
            "summary": "Engineering execution phase: module integration, end-to-end testing, empirical performance benchmarking, ablation studies, thesis preparation, and viva defense.",
            "key_points": [
                "End-to-end testing validates complete user flows and interface contracts",
                "Empirical benchmarking compares runtime, accuracy, and resource utilization against baseline methods",
                "Ablation studies demonstrate the individual contribution of each system component",
                "Defense presentations highlight methodology, novelty, empirical results, and future research directions"
            ],
            "formulas": [
                {
                    "name": "Speedup Ratio",
                    "latex": "$$\\text{Speedup} = \\frac{T_{\\text{baseline}}}{T_{\\text{optimized}}}$$",
                    "explanation": "Quantifies empirical performance enhancement"
                }
            ],
            "flashcards": [
                {"front": "What is an Ablation Study in engineering research?", "back": "An experimental procedure where system components or features are systematically removed to quantify their individual impact on overall performance.", "hint": "Component validation"},
                {"front": "What is Empirical Performance Benchmarking?", "back": "Conducting controlled experiments using standardized test metrics and datasets to compare the proposed system with existing baseline solutions.", "hint": "Standardized evaluation"},
                {"front": "What are the essential sections of an Engineering Thesis Defense?", "back": "Problem Motivation, Prior Art Limitations, Proposed Architecture, Experimental Methodology, Empirical Results, and Conclusion.", "hint": "Defense structure"}
            ],
            "difficulty": "Advanced"
        }
    }
}

# ===== UNION OF ALL CONTENT =====
# Add Year 4 Semester 7 content if available
_year4_sem7 = YEAR4_SEM7_CONTENT if 'YEAR4_SEM7_CONTENT' in globals() else {}

ALL_STUDY_CONTENT = {
    **YEAR1_SEM1_CONTENT,
    **YEAR1_SEM2_CONTENT,
    **YEAR2_SEM3_CONTENT,
    **YEAR2_SEM4_CONTENT,
    **YEAR3_SEM5_CONTENT,
    **YEAR3_SEM6_CONTENT,
    **YEAR4_SEM7_CONTENT,
    **YEAR4_SEM8_CONTENT,
}

def get_subject_content(subject_code: str):
    """Get all study content for a subject"""
    return ALL_STUDY_CONTENT.get(subject_code, {})

def get_topic_content(subject_code: str, topic_name: str):
    """Get specific topic content"""
    subject = get_subject_content(subject_code)
    return subject.get(topic_name.lower().replace(" ", "_"), {})

def get_all_subjects():
    """Get list of all subject codes"""
    return list(ALL_STUDY_CONTENT.keys())
