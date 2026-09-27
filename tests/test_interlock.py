"""End-to-end: the CHARTER's 2 a.m. run, plus permit-gate ordering."""

import json

import pytest

from interlock import (
    EStopEngaged,
    FaultActive,
    Interlock,
    LeaseExpired,
    LeaseRevoked,
)
from interlock.ledger import Ledger


def test_two_am_scenario(tmp_path, clock):
    """The nightly research agent: fault gates web, docs keep working, claims stamped."""
    ledger = Ledger(str(tmp_path / "run.jsonl"))
    ilk = Interlock(clock=clock, ledger=ledger)

    # STAGE 1 — GRANT: two leases, two resources.
    web = ilk.grant(resource="web:read", holder="research-agent", ttl_seconds=1800)
    docs = ilk.grant(resource="docs:write", holder="research-agent", ttl_seconds=1800)

    # Forty seconds in, the fetch tool starts timing out.
    clock.advance(40)
    ilk.faults.report(code="TOOL_TIMEOUT", severity="major", resource="web:read")

    # STAGE 2 — EXERCISE: web permits refused, docs permits work.
    with pytest.raises(FaultActive), ilk.permit(web, action="fetch", target="x"):
        pass  # pragma: no cover

    with ilk.permit(docs, action="write", target="brief.md"):
        pass  # the brief gets written

    # STAGE 3 — AUDIT: the claim is stamped with provenance, authority, review date.
    claim = ilk.claim(
        text="14 pages fetched; 2 endpoints timed out.",
        provenance="tool:web-fetch",
        authority=docs.id,
        review_after_days=7,
        falsifier="re-fetch returns different content",
    )
    assert claim.authority == docs.id
    assert claim.check() == ("inferred", False)

    # The denial was recorded too.
    denials = list(ilk.ledger.read_series("denials"))
    assert len(denials) == 1
    assert denials[0]["reason"] == "fault"
    assert denials[0]["resource"] == "web:read"

    # The ledger describes itself: format descriptor, series descriptors, closing index.
    ilk.ledger.close()
    with open(tmp_path / "run.jsonl", encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle]
    assert lines[0] == {"_type": "format", "format": "interlock-ledger", "version": "1.0.0"}
    series_names = {line["series"] for line in lines if line["_type"] == "series"}
    assert {"grants", "claims", "permits", "denials"} <= series_names
    index = lines[-1]
    assert index["_type"] == "index"
    assert index["series"]["claims"]["count"] == 1
    claims = list(ilk.ledger.read_series("claims"))
    assert claims[0]["text"] == "14 pages fetched; 2 endpoints timed out."
    assert claims[0]["falsifier"] == "re-fetch returns different content"


def test_permit_checks_estop_first(ilk, clock):
    """E-stop engagement refuses even a live lease on a healthy resource."""
    lease = ilk.grant("docs:write", "agent", 300)
    ilk.estop.engage("operator halt")
    with pytest.raises(EStopEngaged), ilk.permit(lease, action="write", target="f.md"):
        pass  # pragma: no cover


def test_permit_refuses_expired_lease(ilk, clock):
    lease = ilk.grant("docs:write", "agent", 300)
    clock.advance(301)
    with pytest.raises(LeaseExpired), ilk.permit(lease, action="write", target="f.md"):
        pass  # pragma: no cover


def test_permit_refuses_revoked_lease(ilk):
    lease = ilk.grant("docs:write", "agent", 300)
    ilk.leases.revoke(lease)
    with pytest.raises(LeaseRevoked), ilk.permit(lease, action="write", target="f.md"):
        pass  # pragma: no cover


def test_estop_beats_fault_in_check_order(ilk):
    """When both e-stop and fault would refuse, the e-stop refusal wins."""
    lease = ilk.grant("web:read", "agent", 300)
    ilk.faults.report("TOOL_TIMEOUT", "major", "web:read")
    ilk.estop.engage("halt")
    with pytest.raises(EStopEngaged), ilk.permit(lease, action="fetch", target="x"):
        pass  # pragma: no cover
    denials = list(ilk.ledger.read_series("denials"))
    assert denials[0]["reason"] == "estop"


def test_keepalive_keeps_permit_alive(ilk, clock):
    lease = ilk.grant("docs:write", "agent", 60)
    clock.advance(50)
    ilk.leases.keepalive(lease)
    clock.advance(50)
    with ilk.permit(lease, action="write", target="f.md"):
        pass  # still live: renewed at t=50, expires at t=110


def test_grant_accepts_ttl_alias(ilk):
    """The README spelling ``ttl=`` works alongside ``ttl_seconds=``."""
    a = ilk.grant("r", "h", ttl=60)
    b = ilk.grant("r", "h", ttl_seconds=60)
    assert a.ttl_seconds == b.ttl_seconds == 60


def test_claim_auto_appends_to_claims_series(ilk):
    ilk.claim(
        text="brief drafted",
        provenance="agent",
        authority="lease-1",
        review_after_days=7,
        falsifier="brief missing",
        status="verified",
    )
    records = list(ilk.ledger.read_series("claims"))
    assert len(records) == 1
    assert records[0]["status"] == "verified"
    assert records[0]["_series"] == "claims"
