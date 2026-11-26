"""Gedeelde fixtures voor alle tests."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def verwacht() -> dict:
    return json.loads((ROOT / "tests" / "verwacht.json").read_text(encoding="utf-8"))
