#!/usr/bin/env python
"""Local, repeatable latency and throughput probe for the StudyMorph backend.

Standard library only, no production imports beyond the app itself, and no
public-internet dependency: question generation is exercised against a
deterministic local research fixture so the numbers measure our code rather
than someone else's uptime.

Usage:
    python tests/backend_audit_baseline.py --requests 30 --query "avl tree rottaions"

Prints p50/p95 in milliseconds plus a schema check per endpoint. There are
no assertions here on purpose - this is a measurement tool, not a test.
"""

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SEARCH_KEYS = {"query", "total", "results", "topic_context"}
STATUS_KEYS = {
    "status", "c_core_accelerated", "gemini_api_configured", "total_assignments",
    "total_notebooks", "indexed_rag_chunks", "available_colleges",
    "available_subjects", "timestamp",
}
QUESTION_KEYS = {
    "course_code", "subject", "topic", "total", "questions",
    "research_query", "research_sources", "source", "refresh_count",
}


def _pct(values, percentile):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(int(len(ordered) * percentile) - 1, len(ordered) - 1)
    return ordered[max(index, 0)]


def _sample(client, method, path, params, expected_keys, failures):
    response = client.request(method, path, params=params)
    if response.status_code != 200:
        failures.append(f"{method} {path} -> HTTP {response.status_code}")
        return None
    body = response.json()
    missing = expected_keys - set(body)
    if missing:
        failures.append(f"{path} -> missing keys {sorted(missing)}")
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--query", default="avl tree rottaions")
    parser.add_argument("--warmup", type=int, default=3)
    args = parser.parse_args()

    from fastapi.testclient import TestClient
    from src.backend.app import app
    from src.backend.web_question_engine import WebQuestionEngine

    # Deterministic offline research fixture: keeps this probe off the internet
    # while still running the real generation and synthesis code paths.
    def fake_research(subject, topic, course_code="", refresh_count=0):
        return {
            "subject": subject,
            "topic": topic,
            "course_code": course_code,
            "query": f"offline fixture: {subject} {topic}",
            "titles": ["Offline Fixture"],
            "snippets": ["deterministic local research text for benchmarking"],
            "research_text": "local fixture research body",
            "sources": [],
            "refresh_count": refresh_count,
        }

    original_research = WebQuestionEngine.search_web_for_topic
    WebQuestionEngine.search_web_for_topic = staticmethod(fake_research)

    failures = []
    timings = {}
    try:
        client = TestClient(app)
        endpoints = [
            ("GET", "/api/search", {"q": args.query}, SEARCH_KEYS),
            ("GET", "/api/system/status", None, STATUS_KEYS),
            ("GET", "/api/questions/course/CS201", {"refresh": "false"}, QUESTION_KEYS),
        ]

        with client:
            for method, path, params, keys in endpoints:
                # Generating questions mutates in-memory session history, so each
                # sample uses a distinct session. Otherwise later samples hit the
                # anti-duplication path and measure less work than the first call.
                label = f"{method} {path}"

                def _params(n):
                    if "questions/course" not in path:
                        return params
                    base = dict(params or {})
                    base["session_id"] = f"bench-{n}-{time.time_ns()}"
                    return base

                for n in range(args.warmup):
                    _sample(client, method, path, _params(f"warm{n}"), keys, failures)

                samples = []
                for n in range(args.requests):
                    start = time.perf_counter()
                    _sample(client, method, path, _params(f"run{n}"), keys, failures)
                    samples.append((time.perf_counter() - start) * 1000.0)
                timings[label] = samples

            # Question-generation contract: exactly 15 questions, every time.
            body = _sample(client, "GET", "/api/questions/course/CS201",
                           {"refresh": "false", "session_id": f"bench-final-{time.time_ns()}"},
                           QUESTION_KEYS, failures)
            if body is not None:
                count = len(body.get("questions", []))
                if count != 15:
                    failures.append(f"question generation returned {count}, expected 15")
    finally:
        WebQuestionEngine.search_web_for_topic = original_research

    print(f"samples per endpoint : {args.requests} (after {args.warmup} warmup)")
    print(f"query                 : {args.query!r}")
    print()
    for label, samples in timings.items():
        mean = statistics.fmean(samples)
        print(f"{label}")
        print(f"    p50  {statistics.median(samples):8.2f} ms")
        print(f"    p95  {_pct(samples, 0.95):8.2f} ms")
        print(f"    mean {mean:8.2f} ms")
        print(f"    min  {min(samples):8.2f} ms")
    print()
    if failures:
        print("SCHEMA/CONTRACT FAILURES:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("all endpoint schema checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())