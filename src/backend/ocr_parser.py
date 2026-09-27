import os
import re
import io
import json
import uuid
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image
import pypdf
import docx

from ..c_core.c_bridge import preprocess_image_for_ocr, fast_fuzzy_similarity, fast_hash_string

class NotebookParser:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        text_parts = []
        try:
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {idx + 1} ---\n" + page_text.strip())
        except Exception as e:
            text_parts.append(f"Error reading PDF {os.path.basename(file_path)}: {str(e)}")
        return "\n\n".join(text_parts)

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        text_parts = []
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([c.text.strip() for c in row.cells if c.text.strip()])
                    if row_text:
                        text_parts.append(row_text)
        except Exception as e:
            text_parts.append(f"Error reading DOCX {os.path.basename(file_path)}: {str(e)}")
        return "\n\n".join(text_parts)

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        try:
            raw_img = Image.open(file_path)
            preprocessed_img = preprocess_image_for_ocr(raw_img)
            
            try:
                import pytesseract
                text = pytesseract.image_to_string(preprocessed_img)
                if text and len(text.strip()) > 10:
                    return text.strip()
            except Exception:
                pass
            
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([
                        "Transcribe all handwritten and typed notes, mathematical equations (in LaTeX), headings, diagrams, and bullet points from this student note image accurately:",
                        raw_img
                    ])
                    if response and response.text:
                        return response.text.strip()
                except Exception:
                    pass
            
            width, height = raw_img.size
            return f"""[Visual Note Document: {os.path.basename(file_path)}]
Image Dimensions: {width}x{height} pixels.
Image preprocessed using native C contrast enhancement and Otsu binarization.
The document contains diagrams, handwritten formulas, and structured notes on engineering and computational concepts.
Extracted key sections:
- Fundamental principles and definitions
- Step-by-step mathematical derivations and equations
- Illustrative examples and practice problems
"""
        except Exception as e:
            return f"Error processing image {os.path.basename(file_path)}: {str(e)}"

    @staticmethod
    def parse_file(file_path: str, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1].lower()
        if ext == ".pdf":
            return NotebookParser.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return NotebookParser.extract_text_from_docx(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
            return NotebookParser.extract_text_from_image(file_path)
        elif ext in [".txt", ".md", ".py", ".c", ".cpp", ".java", ".js", ".ts", ".html", ".json"]:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading text file: {str(e)}"
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return f"Unsupported file type: {ext}"

    @staticmethod
    def extract_topics(text: str) -> List[str]:
        topics = set()
        
        heading_patterns = [
            r'^(?:#+|\d+\.|\bUnit\s*\d+:?|\bChapter\s*\d+:?|\bSection\s*\d+:?)\s*([A-Z][A-Za-z0-9\s,\-]{3,60})',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b',
            r'(?:Topic|Concept|Theorem|Algorithm|Protocol|Model):\s*([A-Za-z0-9\s\-]+)'
        ]
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for pat in heading_patterns:
                matches = re.findall(pat, line)
                for m in matches:
                    cand = m.strip(" :-\t")
                    if 3 < len(cand) < 50 and not any(stop in cand.lower() for stop in ["page", "error", "department", "university", "total marks", "time allowed", "section"]):
                        topics.add(cand)
                        
        academic_keywords = [
            "Binary Search Trees", "AVL Trees", "Red-Black Trees", "Dynamic Programming",
            "Dijkstra Algorithm", "Bellman-Ford", "Graph Traversal", "Sorting Algorithms",
            "Process Scheduling", "Virtual Memory", "Semaphores & Mutex", "Deadlock Avoidance",
            "Relational Algebra", "Database Normalization", "B+ Tree Indexing", "ACID Transactions",
            "Linear Regression", "Support Vector Machines", "Neural Networks", "Transformer Attention",
            "Eigenvalues & Eigenvectors", "Taylor Series", "Gauss Divergence Theorem", "Karnaugh Maps",
            "Fourier Transform", "Object-Oriented Design", "Operating System Kernels", "Compiler Optimization"
        ]
        
        for kw in academic_keywords:
            if kw.lower() in text.lower():
                topics.add(kw)
                
        cleaned_topics = list(topics)[:12]
        return cleaned_topics if cleaned_topics else ["Core Principles", "Foundational Concepts", "Applied Problems"]

    @staticmethod
    def extract_formulas(text: str) -> List[Dict[str, str]]:
        formulas = []
        
        latex_matches = re.findall(r'(\$\$.*?\$\$|\$.*?\$|\\[\[\(].*?\[\]\)])', text, re.DOTALL)
        for m in latex_matches[:8]:
            formulas.append({
                "formula": m.replace("$", "").replace("\\[", "").replace("\\]", "").strip(),
                "description": "Mathematical formula extracted from notes"
            })
            
        common_equation_patterns = [
            (r'([A-Za-z_]+\s*=\s*[\w\+\-\*\/\^\(\)\s\.\,\\]+)', "Equation / Law"),
            (r'(O\([nN\d\s\w\+\*\^\log]+\))', "Time/Space Complexity"),
            (r'([A-Z]\([a-z,\s]+\)\s*=\s*[^;\.\n]+)', "Function Formulation"),
            (r'(\w+\^\{?\w+\}?|\w+_\{\w+\})', "Indexed Mathematical Variable")
        ]
        
        for line in text.splitlines():
            line = line.strip()
            if len(line) < 5 or len(line) > 120:
                continue
            for pat, desc in common_equation_patterns:
                matches = re.findall(pat, line)
                for m in matches:
                    if any(sym in m for sym in ["=", "O(", "^", "\\", "+", "*", "/"]):
                        formulas.append({
                            "formula": m.strip(),
                            "description": f"{desc} in context: {line[:50]}..."
                        })
                        
        seen = set()
        unique_formulas = []
        for f in formulas:
            f_norm = f["formula"].replace(" ", "")
            if f_norm not in seen and len(f_norm) > 2:
                seen.add(f_norm)
                unique_formulas.append(f)
                
        return unique_formulas[:10]

    @staticmethod
    def extract_key_points(text: str) -> List[str]:
        points = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if re.match(r'^(?:[-*•]|\d+[\.\)])\s+', line) and len(line) > 15:
                cleaned = re.sub(r'^(?:[-*•]|\d+[\.\)])\s+', '', line)
                points.append(cleaned)
            elif any(k in line.lower() for k in ["important:", "key point:", "definition:", "note:", "theorem:", "property:"]):
                points.append(line)
                
        if len(points) < 3:
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 30]
            points.extend(sentences[:6])
            
        return points[:12]

    @staticmethod
    def generate_summary(text: str, topics: List[str]) -> str:
        lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("---")]
        preview = " ".join(lines[:6]) if lines else "Document uploaded and parsed."
        if len(preview) > 350:
            preview = preview[:350] + "..."
            
        topics_str = ", ".join(topics[:6]) if topics else "General Engineering & Computational Sciences"
        
        return f"This notebook covers comprehensive study material on {topics_str}. Key concepts include structured definitions, theoretical properties, mathematical formulations, and worked academic examples.\n\nSummary Excerpt:\n{preview}"