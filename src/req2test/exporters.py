"""Write test plans as Gherkin features, a CSV for test management tools, and a traceability matrix."""

from __future__ import annotations

import csv
import io
import re

from .models import StoryTestPlan


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def to_gherkin(plan: StoryTestPlan) -> str:
    s = plan.story
    lines = [f"@{s.id}", f"Feature: {s.title}", ""]
    if s.narrative:
        lines += [f"  {s.narrative}", ""]
    for t in plan.tests:
        tags = " ".join([f"@{t.id}", f"@{t.priority.value}", f"@{t.type.value}", *[f"@{c}" for c in t.covers]])
        lines += [f"  {tags}", f"  Scenario: {t.title}"]
        for i, pre in enumerate(t.preconditions):
            lines.append(f"    {'Given' if i == 0 else 'And'} {pre}")
        for i, step in enumerate(t.steps):
            keyword = "When" if i == 0 else "And"
            if not t.preconditions and i == 0:
                keyword = "Given the user is on the feature under test\n    When"
            lines.append(f"    {keyword} {step}")
        lines += [f"    Then {t.expected}", ""]
    return "\n".join(lines)


def to_csv(plans: list[StoryTestPlan]) -> str:
    """Columns map cleanly to TestRail / Xray / Zephyr CSV import."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["ID", "Story", "Title", "Type", "Priority", "Preconditions", "Steps", "Expected Result", "Covers"])
    for p in plans:
        for t in p.tests:
            w.writerow(
                [
                    t.id,
                    p.story.id,
                    t.title,
                    t.type.value,
                    t.priority.value,
                    "\n".join(t.preconditions),
                    "\n".join(f"{i}. {s}" for i, s in enumerate(t.steps, 1)),
                    t.expected,
                    ", ".join(t.covers),
                ]
            )
    return buf.getvalue()


def to_traceability(plans: list[StoryTestPlan]) -> str:
    out = ["# Traceability matrix", ""]
    for p in plans:
        out += [f"## {p.story.id} {p.story.title}", "", f"LLM rounds: {p.llm_rounds} · Tests: {len(p.tests)}", ""]
        out += ["| Criterion | Tests | Types |", "| --- | --- | --- |"]
        for ac in p.story.acceptance_criteria:
            covering = [t for t in p.tests if ac.id in t.covers]
            ids = ", ".join(t.id for t in covering) or "**NOT COVERED**"
            types = ", ".join(sorted({t.type.value for t in covering})) or "-"
            out.append(f"| {ac.id}: {ac.text} | {ids} | {types} |")
        if p.gaps:
            out += ["", "Open gaps: " + "; ".join(p.gaps)]
        out.append("")
    return "\n".join(out)


def feature_filename(plan: StoryTestPlan) -> str:
    return f"{plan.story.id.lower()}-{_slug(plan.story.title)}.feature"
