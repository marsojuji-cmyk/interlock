#!/usr/bin/env python3
"""Interlock 90-second demonstrator.

A narrated end-to-end run of the substrate, in one terminal:

  GRANT      authority comes into existence only here, and it expires
  KEEPALIVE  renewal moves the expiry; it cannot resurrect a dead lease
  PERMIT     the gate passes: e-stop clear, lease live, no gating fault
  EXPIRED    a lapsed lease is denied
  FAULT      a gating fault refuses permits on its resource only
  E-STOP     one engagement halts every permit; release is explicit
  CLAIM      the run is stamped as a provenance-bearing claim
  AUDIT      the ledger holds every permit and every denial

Run:  python3 scripts/demo_90s.py
"""

from __future__ import annotations

import sys
import time

sys.path.insert(0, "src")

from interlock import EStopEngaged, FaultActive, Interlock, LeaseExpired  # noqa: E402

_step = 0


def say(text: str) -> None:
    global _step
    _step += 1
    print(f"[{_step:02d}] {text}", flush=True)


def main() -> int:
    ilk = Interlock()

    say("GRANT — authority comes into existence only here, and it expires.")
    lease = ilk.grant(resource="docs:write", holder="research-agent", ttl_seconds=30)
    say(f"       lease {lease.id} → docs:write · holder research-agent · ttl 30s")

    old_expiry = lease.expires_at
    ilk.leases.keepalive(lease)
    moved = lease.expires_at > old_expiry
    say(f"KEEPALIVE — renewal moved the expiry ({moved=}). It cannot resurrect a dead lease.")

    with ilk.permit(lease, action="write", target="brief.md"):
        say("PERMIT — gate passed: e-stop clear, lease live, no gating fault. brief.md written.")

    short = ilk.grant(resource="docs:write", holder="research-agent", ttl_seconds=1)
    time.sleep(1.2)
    try:
        with ilk.permit(short, action="write", target="late.md"):
            pass
        say("EXPIRED — UNEXPECTED: lapsed lease was permitted")
        return 1
    except LeaseExpired:
        say("EXPIRED — the lapsed lease is denied. The denial is on the record.")

    web = ilk.grant(resource="web:read", holder="research-agent", ttl_seconds=300)
    ilk.faults.report(code="TOOL_TIMEOUT", severity="major", resource="web:read")
    try:
        with ilk.permit(web, action="fetch", target="https://example.com/feed"):
            pass
        say("FAULT — UNEXPECTED: gated resource was permitted")
        return 1
    except FaultActive:
        say("FAULT — TOOL_TIMEOUT gates web:read. Faults are resource-scoped: docs:write is unaffected.")
    with ilk.permit(lease, action="write", target="brief-v2.md"):
        say("PERMIT — docs:write still flows while web:read is gated.")

    ilk.estop.engage(reason="operator review requested")
    try:
        with ilk.permit(lease, action="write", target="brief-v3.md"):
            pass
        say("E-STOP — UNEXPECTED: permit passed under e-stop")
        return 1
    except EStopEngaged:
        say("E-STOP — one engagement halts every permit, everywhere.")
    ilk.estop.release()
    with ilk.permit(lease, action="write", target="brief-v3.md"):
        say("RELEASE — explicit release only. Permits flow again.")

    claim = ilk.claim(
        text="Demo run: 3 permits granted, 3 denied (expiry, fault, e-stop).",
        provenance="demo:scripts/demo_90s.py",
        authority=lease.id,
        review_after_days=7,
        falsifier="re-run scripts/demo_90s.py and compare the transcript",
    )
    say(f"CLAIM — provenance-stamped [{claim.status}]: {claim.text}")

    permits = list(ilk.ledger.read_series("permits"))
    denials = list(ilk.ledger.read_series("denials"))
    claims = list(ilk.ledger.read_series("claims"))
    say(
        f"AUDIT — ledger holds {len(permits)} permits, {len(denials)} denials, "
        f"{len(claims)} claim. Nothing happened off the record."
    )
    reasons = sorted({d.get("reason") for d in denials})
    say(f"       denial reasons on record: {', '.join(reasons)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
