import json

from req2test.agent import generate_plan, review
from req2test.llm import MockLLM
from req2test.models import TestType
from req2test.parser import parse_stories


def test_agent_closes_coverage_gaps_in_a_second_round(sample_md):
    promo, wishlist = parse_stories(sample_md)
    plan = generate_plan(promo, MockLLM())
    assert plan.llm_rounds == 2
    assert plan.gaps == []
    types_by_ac = {ac.id: {t.type for t in plan.tests if ac.id in t.covers} for ac in promo.acceptance_criteria}
    assert TestType.negative in types_by_ac["AC2"]  # expired code
    assert TestType.negative in types_by_ac["AC4"]  # only one code
    assert TestType.boundary in types_by_ac["AC5"]  # 20 characters

    wl = generate_plan(wishlist, MockLLM())
    wl_types = {ac.id: {t.type for t in wl.tests if ac.id in t.covers} for ac in wishlist.acceptance_criteria}
    assert TestType.negative in wl_types["AC3"]  # guests
    assert TestType.cross_platform in wl_types["AC4"]  # iOS, Android, web


def test_tests_are_sorted_by_priority_and_numbered(sample_md):
    plan = generate_plan(parse_stories(sample_md)[0], MockLLM())
    priorities = [t.priority.value for t in plan.tests]
    assert priorities == sorted(priorities)
    assert plan.tests[0].id == "SHOP-101-TC01"


class BadModel:
    """Returns one valid test and two invalid ones, then nothing."""

    name = "bad"

    def __init__(self):
        self.calls = 0

    def complete(self, system, user):
        self.calls += 1
        if self.calls > 1:
            return '{"tests": []}'
        return "Here you go:\n" + json.dumps(
            {
                "tests": [
                    {"title": "Valid code applies discount", "type": "functional", "priority": "P1",
                     "steps": ["Apply SAVE20"], "expected": "Total drops 20%", "covers": ["ac1"]},
                    {"title": "Covers a criterion that does not exist", "type": "functional", "priority": "P1",
                     "steps": ["x"], "expected": "xyz", "covers": ["AC9"]},
                    {"title": "Missing steps", "type": "functional", "priority": "P1",
                     "steps": [], "expected": "xyz", "covers": ["AC1"]},
                ]
            }
        )


def test_invalid_model_output_is_rejected_and_remaining_gaps_reported(sample_md):
    story = parse_stories(sample_md)[0]
    model = BadModel()
    plan = generate_plan(story, model, max_rounds=3)
    assert [t.title for t in plan.tests] == ["Valid code applies discount"]
    assert plan.tests[0].covers == ["AC1"]  # normalised to upper case
    assert model.calls == 3  # stopped at max_rounds
    assert "functional AC2" in plan.gaps


def test_review_flags_missing_negative_and_boundary(sample_md):
    story = parse_stories(sample_md)[0]
    gaps = review(story, [])
    assert ("negative", "AC2") in gaps and ("boundary", "AC5") in gaps
