"""
The agent loop:

    story ─▶ draft tests (LLM) ─▶ validate (pydantic) ─▶ review coverage (rules) ─┐
                 ▲                                                                 │
                 └──────────────── GAPS fed back, up to max_rounds ◀──────────────┘

Review is deterministic code, not another prompt, so "is every criterion covered?"
has a reliable answer and the loop always terminates.
"""

from __future__ import annotations

import re

from pydantic import ValidationError

from .llm import LLM, extract_json, get_llm
from .models import StoryTestPlan, TestCase, TestType, UserStory

SYSTEM = """You are a senior SDET writing test cases from a user story.
Reply with ONLY JSON: {"tests": [{"title", "type", "priority", "preconditions", "steps", "expected", "covers"}]}
- type: functional | negative | boundary | cross_platform | accessibility
- priority: P1 (core flow or data loss), P2 (important), P3 (minor)
- covers: the acceptance criterion ids the test verifies, e.g. ["AC2"]
- Steps are concrete user actions. Expected results are observable and specific.
- Cover every acceptance criterion. Add negative tests for invalid input, expired or unauthorized states,
  boundary tests for every numeric limit, and cross-platform tests when iOS, Android and web are mentioned."""

NEGATIVE_HINTS = re.compile(r"\b(expired|invalid|error|guests?|not|only one|cannot|unauthori[sz]ed|full)\b", re.I)
LIMIT_HINTS = re.compile(r"\b(at most|maximum|max|up to|no more than|limit)\b.*\d|\d+\s*(characters|items|attempts)", re.I)
PLATFORM_HINTS = re.compile(r"\b(ios|android|web|website)\b.*\b(ios|android|web|website)\b", re.I)


def review(story: UserStory, tests: list[TestCase]) -> list[tuple[str, str]]:
    """Return (gap_kind, ac_id) pairs the current tests miss."""
    gaps: list[tuple[str, str]] = []
    for ac in story.acceptance_criteria:
        covering = [t for t in tests if ac.id in t.covers]
        types = {t.type for t in covering}
        if not covering:
            gaps.append(("functional", ac.id))
        if NEGATIVE_HINTS.search(ac.text) and TestType.negative not in types:
            gaps.append(("negative", ac.id))
        if LIMIT_HINTS.search(ac.text) and TestType.boundary not in types:
            gaps.append(("boundary", ac.id))
        if PLATFORM_HINTS.search(ac.text) and TestType.cross_platform not in types:
            gaps.append(("cross_platform", ac.id))
    return gaps


def _story_prompt(story: UserStory) -> str:
    acs = "\n".join(f"- {ac.id}: {ac.text}" for ac in story.acceptance_criteria)
    return f"STORY {story.id}: {story.title}\n{story.narrative}\nACCEPTANCE CRITERIA:\n{acs}"


def _parse_tests(reply: str, valid_ids: set[str]) -> tuple[list[TestCase], list[str]]:
    tests, problems = [], []
    for i, raw in enumerate(extract_json(reply).get("tests", [])):
        try:
            tc = TestCase.model_validate(raw)
        except ValidationError as e:
            problems.append(f"test {i + 1} rejected: {e.errors()[0]['msg']}")
            continue
        unknown = [c for c in tc.covers if c not in valid_ids]
        if unknown:
            problems.append(f"test {i + 1} rejected: covers unknown criteria {unknown}")
            continue
        tests.append(tc)
    return tests, problems


def _dedupe(tests: list[TestCase]) -> list[TestCase]:
    seen, out = set(), []
    for t in tests:
        key = (t.type, tuple(sorted(t.covers)), t.title.lower())
        if key not in seen:
            seen.add(key)
            out.append(t)
    return out


def generate_plan(story: UserStory, llm: LLM | None = None, max_rounds: int = 3) -> StoryTestPlan:
    llm = llm or get_llm()
    valid_ids = {ac.id for ac in story.acceptance_criteria}
    prompt = _story_prompt(story)
    tests, _ = _parse_tests(llm.complete(SYSTEM, prompt), valid_ids)
    rounds = 1

    gaps = review(story, tests)
    while gaps and rounds < max_rounds:
        gap_lines = "\n".join(f"- GAP {kind} {ac}" for kind, ac in gaps)
        follow_up = f"{prompt}\n\nYou already wrote {len(tests)} tests. Add tests ONLY for these gaps:\n{gap_lines}"
        new_tests, _ = _parse_tests(llm.complete(SYSTEM, follow_up), valid_ids)
        tests = _dedupe(tests + new_tests)
        rounds += 1
        gaps = review(story, tests)

    order = {"P1": 0, "P2": 1, "P3": 2}
    tests.sort(key=lambda t: (order[t.priority.value], t.covers[0]))
    for i, t in enumerate(tests, 1):
        t.id = f"{story.id}-TC{i:02d}"
    return StoryTestPlan(story=story, tests=tests, gaps=[f"{k} {a}" for k, a in gaps], llm_rounds=rounds)
