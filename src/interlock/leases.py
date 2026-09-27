"""Time-bounded authority grants with keepalive renewal.

A lease is the only form authority takes in Interlock: a named holder, a
named resource, and a time-to-live. The grant is the single moment authority
comes into existence; without keepalive renewal the lease expires, and an
unexercised grant simply decays. The clock is injectable so tests can drive
time deterministically.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from interlock._errors import LeaseExpired, LeaseRevoked


@dataclass
class Lease:
    """A grant of authority over a named resource, valid until ``expires_at``."""

    id: str
    resource: str
    holder: str
    ttl_seconds: float
    granted_at: float
    expires_at: float
    last_keepalive: float
    revoked: bool = False


class LeaseManager:
    """Issues, renews, revokes, and checks leases against an injectable clock."""

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock if clock is not None else time.monotonic

    def now(self) -> float:
        """Current time according to the manager's clock."""
        return self._clock()

    def grant(self, resource: str, holder: str, ttl_seconds: float) -> Lease:
        """Create a new lease. This is the only moment authority comes into existence."""
        now = self.now()
        return Lease(
            id=uuid4().hex,
            resource=resource,
            holder=holder,
            ttl_seconds=ttl_seconds,
            granted_at=now,
            expires_at=now + ttl_seconds,
            last_keepalive=now,
        )

    def keepalive(self, lease: Lease) -> Lease:
        """Renew a lease: ``expires_at`` becomes now plus the original TTL.

        Raises :exc:`LeaseRevoked` if the lease was revoked and
        :exc:`LeaseExpired` if the renewal arrives after expiry. A renewal
        cannot resurrect a dead lease.
        """
        if lease.revoked:
            raise LeaseRevoked(f"lease {lease.id} for {lease.resource} was revoked")
        now = self.now()
        if now > lease.expires_at:
            raise LeaseExpired(
                f"lease {lease.id} for {lease.resource} expired at {lease.expires_at}"
            )
        lease.last_keepalive = now
        lease.expires_at = now + lease.ttl_seconds
        return lease

    def revoke(self, lease: Lease) -> None:
        """Revoke a lease immediately. Revocation is permanent."""
        lease.revoked = True

    def is_live(self, lease: Lease) -> bool:
        """True when the lease is held, unrevoked, and not yet expired."""
        return not lease.revoked and self.now() <= lease.expires_at
