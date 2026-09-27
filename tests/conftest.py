"""Shared fixtures: a deterministic fake clock and a fresh Interlock facade."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from interlock import Interlock


class FakeClock:
    """A manually advanced clock for deterministic lease and claim tests."""

    def __init__(self, start: float = 1_000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def ilk(clock: FakeClock) -> Interlock:
    return Interlock(clock=clock)
