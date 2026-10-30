"""LLM providers. Standard library only (urllib), so the package has one dependency: pydantic."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Protocol


class LLM(Protocol):
    name: str

    def complete(self, system: str, user: str) -> str: ...


def _post(url: str, headers: dict[str, str], body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read())


class AnthropicLLM:
    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        self.api_key, self.model = api_key, model

    def complete(self, system: str, user: str) -> str:
        data = _post(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            {"model": self.model, "max_tokens": 4096, "system": system, "messages": [{"role": "user", "content": user}]},
        )
        return "".join(block.get("text", "") for block in data["content"])


class OpenAILLM:
    name = "openai"

    def __init__(self, api_key: str, model: str):
        self.api_key, self.model = api_key, model

    def complete(self, system: str, user: str) -> str:
        data = _post(
            "https://api.openai.com/v1/chat/completions",
            {"authorization": f"Bearer {self.api_key}"},
            {
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
        )
        return data["choices"][0]["message"]["content"]


class MockLLM:
    """
    Deterministic offline stand-in for a model, used by the demo and CI.

    Like a real model on a first pass, it writes one happy-path test per acceptance
    criterion and misses negative, boundary and cross-platform cases. When the agent
    sends back a GAPS list, it fills them in. That makes the agent's review loop
    visible and testable without an API key.
    """

    name = "mock"

    def complete(self, system: str, user: str) -> str:
        criteria = re.findall(r"^- (AC\d+): (.+)$", user, re.M)
        gaps = re.findall(r"^- GAP (\w+) (AC\d+)$", user, re.M)
        tests = [self._gap_test(kind, ac, dict(criteria)[ac]) for kind, ac in gaps] if gaps else [self._happy(ac, text) for ac, text in criteria]
        return json.dumps({"tests": tests})

    @staticmethod
    def _happy(ac: str, text: str) -> dict:
        return {
            "title": f"Verify: {text}"[:120],
            "type": "functional",
            "priority": "P1" if ac in ("AC1", "AC2") else "P2",
            "preconditions": ["Test user and data from the test data set"],
            "steps": ["Open the feature under test", f"Perform the action described in {ac}", "Observe the result"],
            "expected": text,
            "covers": [ac],
        }

    @staticmethod
    def _gap_test(kind: str, ac: str, text: str) -> dict:
        if kind == "functional":
            return MockLLM._happy(ac, text)
        if kind == "boundary":
            limit = re.search(r"(\d+)", text).group(1)
            return {
                "title": f"Boundary: {ac} at {limit} and {int(limit) + 1}",
                "type": "boundary",
                "priority": "P2",
                "preconditions": [f"Data set up to reach the limit of {limit}"],
                "steps": [f"Enter or add exactly {limit}", "Verify it is accepted", f"Enter or add {int(limit) + 1}", "Verify it is rejected with the documented message"],
                "expected": f"{limit} is accepted and {int(limit) + 1} is rejected",
                "covers": [ac],
            }
        if kind == "cross_platform":
            return {
                "title": f"Cross-platform: {ac} on iOS, Android and web",
                "type": "cross_platform",
                "priority": "P2",
                "preconditions": ["Same account signed in on iOS, Android and web"],
                "steps": ["Make the change on iOS", "Refresh Android and web", "Make a change on web", "Refresh iOS and Android"],
                "expected": "All three platforms show the same state within the sync window",
                "covers": [ac],
            }
        return {
            "title": f"Negative: {ac} with invalid input or state",
            "type": "negative",
            "priority": "P1",
            "preconditions": ["Invalid, expired or unauthorized data from the test data set"],
            "steps": [f"Attempt the action in {ac} with invalid input or state", "Observe the message and resulting state"],
            "expected": f"The system rejects it as specified: {text}",
            "covers": [ac],
        }


def get_llm() -> LLM:
    choice = os.environ.get("LLM_PROVIDER", "mock").lower()
    if choice == "anthropic":
        return AnthropicLLM(os.environ["ANTHROPIC_API_KEY"], os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"))
    if choice == "openai":
        return OpenAILLM(os.environ["OPENAI_API_KEY"], os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    return MockLLM()


def extract_json(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object in model reply: {text[:200]}")
    return json.loads(text[start : end + 1])
