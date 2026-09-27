"""Provenance-stamped assertions.

Anything the system asserts — to the user, to a log, to another agent — is
stamped with what produced it, under what authority, when it was valid, and
what would prove it wrong. A claim read after its review date is reported as
stale, not as fact.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field

STATUSES = ("verified", "inferred", "guessed")


@dataclass
class Claim:
    """A stamped assertion with provenance, authority, review date, and falsifier."""

    text: str
    provenance: str
    authority: str
    review_after_days: float
    falsifier: str
    status: str = "inferred"
    created: float = field(default_factory=time.time)
    _clock: Callable[[], float] | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"status must be one of {STATUSES}, got {self.status!r}")

    def _now(self) -> float:
        return self._clock() if self._clock is not None else time.time()

    def record(self) -> dict:
        """The claim as a plain dict, suitable for appending to the ledger."""
        return {
            "text": self.text,
            "provenance": self.provenance,
            "authority": self.authority,
            "review_after_days": self.review_after_days,
            "falsifier": self.falsifier,
            "status": self.status,
            "created": self.created,
        }

    def is_stale(self) -> bool:
        """True when now is past ``created`` plus ``review_after_days``."""
        return self._now() > self.created + self.review_after_days * 86400

    def check(self) -> tuple[str, bool]:
        """Return ``(status, stale)`` — what is known, and whether it is still fresh."""
        return (self.status, self.is_stale())
