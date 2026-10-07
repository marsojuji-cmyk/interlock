"""Regression tests: the gate admits only leases it issued, unaltered and unrevoked.

``LeaseNotIssued`` is looked up at call time so the core regression tests fail
on an assertion (not an ImportError) against code that predates the fix.
"""

import dataclasses

import pytest

import interlock
from interlock import Interlock, InterlockError, Lease, LeaseExpired, LeaseRevoked


def _forged(resource="docs:write"):
    return Lease(
        id="forged",
        resource=resource,
        holder="anyone",
        ttl_seconds=1,
        granted_at=0,
        expires_at=1e18,
        last_keepalive=0,
    )


def _not_issued_error():
    return getattr(interlock, "LeaseNotIssued", None)


def test_permit_rejects_a_forged_lease(ilk):
    ran = []
    with (
        pytest.raises(InterlockError) as info,
        ilk.permit(_forged(), action="write", target="f.md"),
    ):
        ran.append(True)  # pragma: no cover
    assert ran == [], "the action body must never run under a forged lease"
    assert type(info.value).__name__ == "LeaseNotIssued"
    denials = list(ilk.ledger.read_series("denials"))
    assert denials[-1]["reason"] == "lease_not_issued"
    assert list(ilk.ledger.read_series("permits")) == []


def test_permit_rejects_a_lease_from_another_interlock(clock):
    issuer = Interlock(clock=clock)
    gate = Interlock(clock=clock)
    lease = issuer.grant("docs:write", "agent", ttl_seconds=300)
    with pytest.raises(InterlockError) as info, gate.permit(lease, action="write", target="f"):
        pass  # pragma: no cover
    assert type(info.value).__name__ == "LeaseNotIssued"


def test_permit_rejects_a_lease_retargeted_after_issue(ilk):
    lease = ilk.grant("docs:read", "agent", ttl_seconds=300)
    widened = dataclasses.replace(lease, resource="docs:write")  # same id, new resource
    with pytest.raises(InterlockError) as info, ilk.permit(widened, action="write", target="f"):
        pass  # pragma: no cover
    assert type(info.value).__name__ == "LeaseNotIssued"


def test_editing_expires_at_does_not_extend_authority(ilk, clock):
    lease = ilk.grant("docs:write", "agent", ttl_seconds=60)
    lease.expires_at = 1e18
    clock.advance(61)
    with pytest.raises(LeaseExpired), ilk.permit(lease, action="write", target="f"):
        pass  # pragma: no cover


def test_clearing_the_revoked_flag_does_not_restore_authority(ilk):
    lease = ilk.grant("docs:write", "agent", ttl_seconds=300)
    ilk.leases.revoke(lease)
    lease.revoked = False
    with pytest.raises(LeaseRevoked), ilk.permit(lease, action="write", target="f"):
        pass  # pragma: no cover


def test_keepalive_rejects_a_lease_it_never_issued(ilk):
    with pytest.raises(InterlockError) as info:
        ilk.leases.keepalive(_forged())
    assert type(info.value).__name__ == "LeaseNotIssued"


def test_keepalive_still_renews_issued_leases(ilk, clock):
    lease = ilk.grant("docs:write", "agent", ttl_seconds=60)
    clock.advance(50)
    ilk.leases.keepalive(lease)
    clock.advance(50)
    with ilk.permit(lease, action="write", target="f"):
        pass  # renewed at t=50 in the manager's record, live until t=110


def test_is_live_false_for_unissued_lease(ilk):
    assert ilk.leases.is_live(_forged()) is False
    assert ilk.leases.issued(ilk.grant("r", "h", ttl_seconds=5)) is True


def test_lease_not_issued_is_exported_and_derives_from_base():
    err = _not_issued_error()
    assert err is not None and "LeaseNotIssued" in interlock.__all__
    assert issubclass(err, InterlockError)
