"""Tests for leases: grants, keepalive renewal, revocation, liveness."""

import pytest

from interlock import InterlockError, LeaseExpired, LeaseRevoked
from interlock.leases import LeaseManager


def test_grant_sets_fields(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "research-agent", 300)
    assert lease.resource == "web:read"
    assert lease.holder == "research-agent"
    assert lease.ttl_seconds == 300
    assert len(lease.id) == 32  # uuid4 hex
    assert lease.granted_at == clock()
    assert lease.expires_at == clock() + 300
    assert lease.last_keepalive == lease.granted_at
    assert lease.revoked is False


def test_grant_ids_unique(clock):
    mgr = LeaseManager(clock)
    assert mgr.grant("a", "h", 60).id != mgr.grant("a", "h", 60).id


def test_keepalive_renews_expiry(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "agent", 300)
    clock.advance(100)
    mgr.keepalive(lease)
    assert lease.last_keepalive == clock()
    assert lease.expires_at == clock() + 300


def test_keepalive_expired_raises(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "agent", 300)
    clock.advance(301)
    with pytest.raises(LeaseExpired):
        mgr.keepalive(lease)


def test_keepalive_revoked_raises(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "agent", 300)
    mgr.revoke(lease)
    with pytest.raises(LeaseRevoked):
        mgr.keepalive(lease)


def test_is_live(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "agent", 300)
    assert mgr.is_live(lease) is True
    clock.advance(301)
    assert mgr.is_live(lease) is False


def test_revoke_kills_liveness(clock):
    mgr = LeaseManager(clock)
    lease = mgr.grant("web:read", "agent", 300)
    mgr.revoke(lease)
    assert lease.revoked is True
    assert mgr.is_live(lease) is False


def test_lease_errors_derive_from_base():
    assert issubclass(LeaseExpired, InterlockError)
    assert issubclass(LeaseRevoked, InterlockError)
