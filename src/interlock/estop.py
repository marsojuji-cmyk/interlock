"""The one halt: a global emergency stop.

A single e-stop engagement suspends all permits, everywhere, immediately.
Resuming requires explicit, deliberate release — never an automatic timeout.
"""

from interlock._errors import EStopEngaged


class EStop:
    """A latching global halt. Engagement is sticky; release is deliberate."""

    def __init__(self) -> None:
        self._engaged = False
        self._reason = ""

    def engage(self, reason: str) -> None:
        """Engage the e-stop. All permits are refused until :meth:`release`."""
        self._engaged = True
        self._reason = reason

    def release(self) -> None:
        """Release the e-stop. An operator decision, never a timeout."""
        self._engaged = False
        self._reason = ""

    @property
    def is_engaged(self) -> bool:
        """Whether the e-stop is currently engaged."""
        return self._engaged

    @property
    def reason(self) -> str:
        """The reason given at the last engagement, or ``""`` when clear."""
        return self._reason

    def assert_clear(self) -> None:
        """Raise :exc:`EStopEngaged` unless the e-stop is clear."""
        if self._engaged:
            raise EStopEngaged(f"e-stop engaged: {self._reason}")
