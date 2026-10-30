import pytest

from req2test.parser import parse_stories


def test_parses_stories_and_criteria(sample_md):
    stories = parse_stories(sample_md)
    assert [s.id for s in stories] == ["SHOP-101", "SHOP-102"]
    assert stories[0].title == "Apply a promo code at checkout"
    assert [ac.id for ac in stories[0].acceptance_criteria] == ["AC1", "AC2", "AC3", "AC4", "AC5"]
    assert stories[0].narrative.startswith("As a shopper")


def test_rejects_text_without_stories():
    with pytest.raises(ValueError, match="No stories found"):
        parse_stories("just some notes")


def test_rejects_story_without_criteria():
    with pytest.raises(ValueError, match="no acceptance criteria"):
        parse_stories("# Story: ABC-1 Something\nAs a user I want things")
