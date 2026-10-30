from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AcceptanceCriterion(BaseModel):
    id: str
    text: str


class UserStory(BaseModel):
    id: str
    title: str
    narrative: str = ""
    acceptance_criteria: list[AcceptanceCriterion]


class TestType(str, Enum):
    __test__ = False  # not a pytest test class

    functional = "functional"
    negative = "negative"
    boundary = "boundary"
    cross_platform = "cross_platform"
    accessibility = "accessibility"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TestCase(BaseModel):
    __test__ = False  # not a pytest test class

    id: str = ""
    title: str = Field(min_length=5)
    type: TestType
    priority: Priority
    preconditions: list[str] = []
    steps: list[str] = Field(min_length=1)
    expected: str = Field(min_length=3)
    covers: list[str] = Field(min_length=1, description="Acceptance criterion ids this test verifies")

    @field_validator("covers")
    @classmethod
    def upper_ids(cls, v: list[str]) -> list[str]:
        return [c.strip().upper() for c in v]


class StoryTestPlan(BaseModel):
    story: UserStory
    tests: list[TestCase]
    gaps: list[str] = []
    llm_rounds: int = 1
