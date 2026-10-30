"""Parse user stories written in a simple, Jira-friendly markdown format (see stories/checkout.md)."""

from __future__ import annotations

import re

from .models import AcceptanceCriterion, UserStory

STORY_RE = re.compile(r"^#\s*Story:\s*(?P<id>[A-Z][A-Z0-9]+-\d+)\s+(?P<title>.+)$", re.M)
AC_RE = re.compile(r"^\s*[-*]\s*(?P<id>AC\d+)\s*[:.)-]\s*(?P<text>.+)$", re.M | re.I)


def parse_stories(markdown: str) -> list[UserStory]:
    matches = list(STORY_RE.finditer(markdown))
    if not matches:
        raise ValueError('No stories found. Start each story with "# Story: KEY-123 Title".')
    stories = []
    for i, m in enumerate(matches):
        body = markdown[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(markdown)]
        narrative_part = body.split("## Acceptance criteria")[0]
        narrative = " ".join(line.strip() for line in narrative_part.strip().splitlines() if line.strip())
        criteria = [AcceptanceCriterion(id=a["id"].upper(), text=a["text"].strip()) for a in AC_RE.finditer(body)]
        if not criteria:
            raise ValueError(f"Story {m['id']} has no acceptance criteria (lines like '- AC1: ...').")
        stories.append(UserStory(id=m["id"], title=m["title"].strip(), narrative=narrative, acceptance_criteria=criteria))
    return stories
