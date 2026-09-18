import os
import sys
import platform
import ctypes
from PIL import Image

_lib = None
_lib_loaded = False

def _init_c_library():
    global _lib, _lib_loaded
    if _lib_loaded:
        return _lib
    current_dir = os.path.dirname(os.path.abspath(__file__))
    is_windows = platform.system() == "Windows"
    lib_name = "libstudyc.dll" if is_windows else "libstudyc.so"
    lib_path = os.path.join(current_dir, lib_name)
    if not os.path.exists(lib_path):
        try:
            from .build import build_c_library
            build_c_library()
        except Exception:
            pass
    if os.path.exists(lib_path):
        try:
            _lib = ctypes.CDLL(lib_path)
            _lib.c_levenshtein.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            _lib.c_levenshtein.restype = ctypes.c_int
            _lib.c_fuzzy_similarity.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            _lib.c_fuzzy_similarity.restype = ctypes.c_double
            _lib.c_bm25_term_score.argtypes = [
                ctypes.c_int, ctypes.c_int, ctypes.c_double,
                ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double
            ]
            _lib.c_bm25_term_score.restype = ctypes.c_double
            _lib.c_batch_bm25_scores.argtypes = [
                ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                ctypes.c_int, ctypes.c_double, ctypes.c_int, ctypes.c_int,
                ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double)
            ]
            _lib.c_batch_bm25_scores.restype = None
            _lib.c_fnv1a_hash.argtypes = [ctypes.c_char_p]
            _lib.c_fnv1a_hash.restype = ctypes.c_ulonglong
            _lib.c_rgb_to_grayscale.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
                ctypes.c_int, ctypes.c_int
            ]
            _lib.c_rgb_to_grayscale.restype = None
            _lib.c_otsu_threshold.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int
            ]
            _lib.c_otsu_threshold.restype = ctypes.c_int
            _lib.c_enhance_contrast.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int
            ]
            _lib.c_enhance_contrast.restype = None
            _lib_loaded = True
            return _lib
        except Exception as e:
            print(f"C library load warning: {e}", file=sys.stderr)
            _lib_loaded = False
            return None
    return None

_init_c_library()

def fast_levenshtein(s1, s2):
    s1 = str(s1) if s1 is not None else ""
    s2 = str(s2) if s2 is not None else ""
    lib = _init_c_library()
    if lib:
        return lib.c_levenshtein(s1.encode('utf-8', errors='ignore'), s2.encode('utf-8', errors='ignore'))
    s1, s2 = s1.lower(), s2.lower()
    if len(s1) < len(s2):
        return fast_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        cur = [i + 1]
        for j, c2 in enumerate(s2):
            cur.append(min(cur[j] + 1, prev[j + 1] + 1, prev[j] + (c1 != c2)))
        prev = cur
    return prev[-1]

def fast_fuzzy_similarity(s1, s2):
    s1 = str(s1) if s1 is not None else ""
    s2 = str(s2) if s2 is not None else ""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    lib = _init_c_library()
    if lib:
        return float(lib.c_fuzzy_similarity(s1.encode('utf-8', errors='ignore'), s2.encode('utf-8', errors='ignore')))
    dist = fast_levenshtein(s1, s2)
    return 1.0 - (dist / max(len(s1), len(s2)))

def fast_bm25_term_score(tf, doc_len, avg_doc_len, doc_count, df, k1=1.5, b=0.75):
    lib = _init_c_library()
    if lib:
        return float(lib.c_bm25_term_score(tf, doc_len, avg_doc_len, doc_count, df, k1, b))
    if tf <= 0 or df <= 0 or doc_count <= 0 or avg_doc_len <= 0:
        return 0.0
    import math
    idf = math.log(1.0 + (doc_count - df + 0.5) / (df + 0.5))
    if idf < 0: idf = 0.0
    len_norm = 1.0 - b + b * (doc_len / avg_doc_len)
    tf_norm = (tf * (k1 + 1.0)) / (tf + k1 * len_norm)
    return idf * tf_norm

def fast_batch_bm25(tfs, doc_lens, avg_doc_len, total_docs, df, k1=1.5, b=0.75):
    n = len(tfs)
    if n == 0:
        return []
    lib = _init_c_library()
    if lib:
        try:
            tfs_arr = (ctypes.c_int * n)(*tfs)
            lens_arr = (ctypes.c_int * n)(*doc_lens)
            out = (ctypes.c_double * n)()
            lib.c_batch_bm25_scores(tfs_arr, lens_arr, n, avg_doc_len, total_docs, df, k1, b, out)
            return [float(x) for x in out]
        except Exception:
            pass
    return [fast_bm25_term_score(tfs[i], doc_lens[i], avg_doc_len, total_docs, df, k1, b) for i in range(n)]

def fast_hash_string(s):
    lib = _init_c_library()
    if lib:
        return int(lib.c_fnv1a_hash(s.encode('utf-8', errors='ignore')))
    h = 14695981039346656037
    for b in s.lower().encode('utf-8', errors='ignore'):
        h ^= b
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h

def preprocess_image_for_ocr(image):
    if image.mode != "L":
        return image.convert("L")
    return image