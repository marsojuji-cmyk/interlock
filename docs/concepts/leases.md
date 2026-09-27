# LEASES

## The problem

An agent's authority is usually ambient: granted once at session start, held
until the process dies. Nothing about the grant says how long it lasts, what
it covers, or who may take it back. When the agent stops needing a capability,
the capability does not stop being available. Unexercised authority persists —
and persisting authority is how a compromised or confused agent does damage
at 3 a.m. with permissions granted at noon.

## How it works

A lease is the only form authority takes: a named holder, a named resource,
and a time-to-live. The grant is the single moment authority comes into
existence. Everything after that is renewal or decay.

### STAGE 1 — GRANT

The operator grants a lease for a named resource (`web:read`, `docs:write`)
to a named holder with a TTL. The lease carries a unique id, the grant time,
and the expiry time. Nothing is implied: the lease covers exactly the named
resource, for exactly the TTL.

### STAGE 2 — RENEW

A live agent renews its leases with keepalives. Each keepalive moves
`expires_at` forward by the original TTL and records `last_keepalive`. A
keepalive on an expired or revoked lease raises — renewal cannot resurrect
the dead. Operators SHOULD set TTLs short enough that a silent agent loses
authority quickly, and keepalive intervals well inside the TTL.

### STAGE 3 — EXPIRE

Without renewal, the lease expires. Expiry is not an event anyone must
remember to fire; it is the default. A lease that is never exercised simply
decays, and nothing about an unexercised grant persists. Revocation is the
deliberate counterpart: immediate, permanent, and checked before expiry in
every gate.

## Safety

Leases are designed to reduce the risk of authority outliving its need. They
are not designed to eliminate it. A lease system cannot constrain code that
bypasses it, and a TTL cannot help if the TTL is a year. Operators SHOULD
treat short TTLs and frequent keepalives as the normal posture, not as
paranoia. The checkable guarantee is narrower: *within* the substrate, no
permit issues against an expired or revoked lease, and the tests cover it.

## A lease, end to end

The nightly research agent wakes at 2 a.m. holding `web:read` with a
30-minute TTL and a keepalive every 5 minutes. At 2:12 the fetch loop hangs
and the agent stops renewing — it is busy, then it is stuck, then it is
dead. At 2:30 the lease expires on its own. Nobody revoked anything; nobody
had to notice. When the operator reviews the ledger at 2:40, the story is
complete without anyone having written it down: granted at 2:00, renewed
until 2:10, expired at 2:30. The authority lasted exactly as long as the
agent was alive to defend it.
