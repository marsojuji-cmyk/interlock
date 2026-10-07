"""Exception hierarchy for the Interlock substrate.

Every failure mode in the substrate is a named exception, so callers can
distinguish a refused permit from a programming error. All derive from
:exc:`InterlockError`.
"""


class InterlockError(Exception):
    """Base class for all Interlock errors."""


class LeaseExpired(InterlockError):
    """A lease was exercised after its expiry without a keepalive renewal."""


class LeaseNotIssued(InterlockError):
    """A lease was presented that this lease manager never issued, or was altered after issue."""


class LeaseRevoked(InterlockError):
    """A lease was exercised after being revoked by its granter."""


class EStopEngaged(InterlockError):
    """Action was attempted while the global e-stop was engaged."""


class FaultActive(InterlockError):
    """A permit was refused because a gating fault is active on the resource."""
