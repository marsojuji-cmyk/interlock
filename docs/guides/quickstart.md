# Quickstart: your first lease in five minutes

This is the fastest path from zero to a live lease, a refused permit, and
an auditable ledger.

## 1. Create the interlock

```python
from interlock import Interlock

ilk = Interlock()
```

You now hold four components: `.leases` (the lease manager), `.estop`
(the one halt), `.faults` (the fault bus), and `.ledger` (the run log).

## 2. Grant a lease

```python
lease = ilk.grant(resource="docs:write", holder="demo-agent", ttl_seconds=300)
```

Authority now exists, and it expires in 300 seconds. Nothing else in the
system can act on `docs:write` without this lease.

## 3. Exercise it through the gate

```python
with ilk.permit(lease, action="write", target="notes.md"):
    Path("notes.md").write_text("hello")
```

The gate checks, in order: e-stop clear, lease live, no gating fault on
`docs:write`. If any check fails, the context manager raises instead of
yielding — `EStopEngaged`, `LeaseExpired`/`LeaseRevoked`, or `FaultActive`.

## 4. Watch a fault refuse

```python
ilk.faults.report(code="DISK_FULL", severity="major", resource="docs:write")

with ilk.permit(lease, action="write", target="notes.md"):
    ...  # raises FaultActive — the refusal is appended to the ledger
```

Clear the fault to resume: `ilk.faults.clear(fault.id)`.

## 5. Halt everything, then release

```python
ilk.estop.engage("taking a look")
# every permit now raises EStopEngaged, on every resource
ilk.estop.release()  # deliberate, never automatic
```

## 6. Stamp a claim and read the ledger

```python
claim = ilk.claim(
    text="notes.md written",
    provenance="demo",
    authority=lease.id,
    review_after_days=7,
    falsifier="notes.md missing or different",
)
print(claim.check())  # ('inferred', False)

for record in ilk.ledger.read_series("claims"):
    print(record["text"], record["_ts"])

ilk.ledger.close()
```

## Next steps

- `docs/concepts/leases.md` — why authority must decay.
- `docs/concepts/estop-and-faults.md` — the one halt and the gating bus.
- `docs/concepts/claims.md` — provenance, review dates, falsifiers.
- `docs/concepts/ledger.md` — the self-describing run log.
- `CHARTER.md` — the full design rationale and safety caveats.
