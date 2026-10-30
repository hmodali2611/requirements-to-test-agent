from pathlib import Path

import pytest


@pytest.fixture
def sample_md() -> str:
    return (Path(__file__).parent.parent / "stories" / "checkout.md").read_text()
