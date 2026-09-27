# E-STOP AND FAULTS

## The problem

When an agent's tool starts failing, the failure is usually a string in a
transcript. Nothing in the system changes state. The agent retries, the tool
fails again, and the night burns on a dead endpoint — or worse, the agent
routes around the failure into actions nobody scoped. There is no halt, and
there is no memory of the failure that other decisions can consult.

## How it works

Interlock treats halting and failure as structure, not policy. One global
e-stop suspends everything. One shared fault bus records every failure with
a severity, and severe faults gate their resource.

### STAGE 1 — ENGAGE

The e-stop is engaged with a reason — by the operator, or by a supervising
agent that has decided the run is no longer safe. Engagement is latching:
every permit check starts by asserting the e-stop is clear, and an engaged
e-stop refuses before leases or faults are even consulted.

### STAGE 2 — REPORT

Failures are reported to the fault bus as faults: a code (`TOOL_TIMEOUT`),
a severity (`minor`, `major`, `critical`), a resource, and a detail string.
Severity is the whole policy: `minor` faults are informational, while an
uncleared `major` or `critical` fault *gates* its resource — new permits on
that resource are refused with `FaultActive` until the fault is cleared.
Clearing is recorded, never erased.

### STAGE 3 — RELEASE

Resuming after an e-stop requires explicit, deliberate release — never an
automatic timeout. A timeout would convert the halt into a pause, and a
pause is not a decision. The release SHOULD follow a review of the ledger:
what engaged the stop, what faulted, what was refused.

## Safety

The e-stop is designed to give the operator one handle that always works.
It is not designed to halt what it cannot see: code that bypasses the
substrate keeps running, and a fault bus only gates resources that report
to it. Operators SHOULD treat the e-stop as one layer in a defense-in-depth
posture. The checkable guarantee is narrower: *within* the substrate, an
engaged e-stop refuses every permit, and a gating fault refuses every
permit on its resource. The tests cover both.

## A halt and a fault, end to end

At 2:00:40 the fetch tool times out for the third time and the agent reports
`TOOL_TIMEOUT`, severity major, on `web:read`. The next web permit is
refused — not debated, not retried with backoff, refused. The agent still
holds `docs:write`, so it writes up what it gathered instead of hammering
the dead endpoint all night. The e-stop sits untouched the whole run; at
2:40 the operator reviews the ledger, sees the fault and the single refusal,
and never needs to reach for the halt. The halt was there. That was enough.
