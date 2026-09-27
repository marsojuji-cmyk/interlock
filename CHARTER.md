# INTERLOCK: LEASED AUTHORITY FOR AGENT SYSTEMS

## The problem

AI agents act with ambient, unexpiring authority. A coding agent holds your
filesystem, your credentials, and your network access for the entire session —
granted once, never renewed, never revoked short of killing the process. When
something goes wrong, there is no e-stop: only a Ctrl-C and a hope. When a
tool fails, the failure is a string in a transcript, not a fault on a bus that
gates further action. When the agent reports what it did, the report carries
no provenance, no authority record, and no expiry date.

Mobile robots solved this a decade ago. Boston Dynamics' Spot admits intent
through a narrow gate — command plus lease plus clock — and treats safety as
structure: leases with keepalives, a global e-stop, a fault taxonomy, and
refusal states. Interlock transfers that architecture to software agents.

## Design principles

1. **Authority MUST be leased, never ambient.** Every capability an agent
   exercises is held under a time-bounded lease for a named resource. The
   lease is renewed by keepalive; without renewal it expires. Unexercised
   authority decays.
2. **There MUST be one halt.** A single e-stop engagement suspends all
   permits, everywhere, immediately. Resuming requires explicit, deliberate
   release — never an automatic timeout.
3. **Faults MUST gate action.** Tool failures, timeouts, and contradictions
   are reported as faults on a shared bus with severity. An active fault of
   sufficient severity refuses new permits on the affected resource.
4. **Every claim MUST carry its provenance.** Anything the system asserts —
   to the user, to a log, to another agent — is stamped with what produced
   it, under what authority, when it was valid, and what would prove it wrong.
5. **Every handoff MUST be an interface record.** Boundaries state their
   guarantees, constraints, ownership, and failure behavior. Truth lives at
   boundaries.
6. **The run log MUST describe itself.** The ledger opens with its format
   descriptor, each series declares its schema, each record carries its
   capture time, and the file closes with an index. A reader with no prior
   knowledge can still audit the run.

## How it works

### STAGE 1 — GRANT

The operator (human or supervising agent) grants a lease: a named holder, a
named resource, a time-to-live. The grant is the only moment authority comes
into existence. A lease that is never exercised simply expires; nothing about
an unexercised grant persists.

### STAGE 2 — EXERCISE

To act, the agent presents the lease and requests a permit for a specific
action on a specific target. The interlock checks, in order: is the e-stop
clear? Is the lease live (held, unexpired, keepalive-fresh)? Is there an
active fault gating this resource? Only if all three pass is the permit
issued — and the permit covers exactly the requested action, nothing more.

### STAGE 3 — AUDIT

Every permit, denial, fault, and claim is appended to the ledger. Claims
stamped during the run carry review dates; a claim read after its review
date is reported as stale, not as fact. The ledger's closing index makes any
moment of the run randomly accessible to an auditor.

## Safety

Interlock is designed to reduce the risk of an agent acting beyond its
authority. It is not designed to eliminate that risk. A lease system cannot
constrain code that bypasses it; an e-stop cannot halt what it cannot see.
Operators SHOULD treat Interlock as one layer in a defense-in-depth posture,
not as a guarantee. The framework's own guarantee is narrower and checkable:
*within* the substrate, no action executes without a live lease, a clear
e-stop, and no gating fault. That property is covered by tests, and the tests
are part of the release.

## A run, end to end

It is 2 a.m. and the nightly research agent wakes to refresh the competitive
landscape brief. It holds a lease for `web:read` (TTL 30 minutes, keepalive
every 5) and a lease for `docs:write` scoped to one directory. Forty seconds
in, the fetch tool starts timing out; the agent reports a `TOOL_TIMEOUT`
fault, severity major, on `web:read`. The interlock refuses further web
permits — the agent cannot burn the night hammering a dead endpoint. It
keeps its docs lease, writes up what it gathered, and stamps the brief:
*provenance: 14 fetched pages; authority: lease docs:write; review date:
7 days; falsifier: any cited page returning different content on re-fetch.*
At 2:40 the operator reviews the ledger, sees the fault, the refusals, and
the stamped claims, and releases the e-stop that was never needed. Nothing
about the run is a matter of trust. It is a matter of record.

## What this demonstrates

Interlock is a transfer result: the safety architecture of a 35 kg quadruped,
re-expressed as a zero-dependency Python substrate for agent systems. It
demonstrates systems design (leases, fault buses, capability scoping),
technical writing (concept documentation in the Boston Dynamics register),
and release discipline (VERSION-file releases, changelogs, CI, docs-as-code).
The full provenance of the transfer — sources read, depth of reading, and
what was not verified — is recorded in the project's intake ledger.
