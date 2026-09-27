# Interlock

**Leased authority, a global e-stop, a fault bus, and provenance — for AI agent systems.**

Agents act with ambient, unexpiring authority: filesystem, credentials, and
network granted once for the whole session, revoked only by killing the
process. Mobile robots solved this a decade ago — Boston Dynamics' Spot
admits intent through a narrow gate of *command plus lease plus clock*, with
keepalives, a global e-stop, and a fault taxonomy as structure, not policy.
Interlock transfers that architecture to software agents as a
zero-dependency Python substrate.

```python
from interlock import Interlock

ilk = Interlock()

# STAGE 1 — GRANT: authority comes into existence only here, and it expires.
lease = ilk.grant(resource="docs:write", holder="research-agent", ttl=1800)

# STAGE 2 — EXERCISE: every action passes the gate —
# e-stop clear? lease live and keepalive-fresh? no gating fault?
with ilk.permit(lease, action="write", target="brief.md"):
    ...  # raises LeaseExpired, EStopEngaged, or FaultActive otherwise

# A fault refuses further permits on the affected resource.
ilk.faults.report(code="TOOL_TIMEOUT", severity="major", resource="web:read")

# STAGE 3 — AUDIT: claims carry provenance, authority, review date, falsifier.
claim = ilk.claim(
    text="14 pages fetched; 2 endpoints timed out.",
    provenance="tool:web-fetch",
    authority=lease.id,
    review_after_days=7,
    falsifier="re-fetch returns different content",
)  # auto-appended to the ledger's "claims" series
```

## Why this exists

The 2026 agent stack has an authority problem, not a capability problem.
Interlock is one layer of a defense-in-depth posture: *within* the
substrate, no action executes without a live lease, a clear e-stop, and no
gating fault. That property is tested, and the tests ship with the release.

## Layout

- `src/interlock/` — the substrate: `leases`, `estop`, `faults`, `claims`,
  `interfaces`, `ledger`. Zero runtime dependencies.
- `docs/concepts/` — concept documentation in the Boston Dynamics register.
- `docs/guides/quickstart.md` — the fastest path to a first lease.
- `CHARTER.md` — the full design rationale, including the safety caveats.
- `INTAKE_LEDGER.md` — every source behind the transfer, with reading depth
  and an explicit unverified list.

## Status

v0.1.0 — core substrate with tests. See `CHANGELOG.md`.

## License

MIT — see `LICENSE`.
