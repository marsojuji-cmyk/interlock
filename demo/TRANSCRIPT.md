[01] GRANT — authority comes into existence only here, and it expires.
[02]        lease 8da9a55b030c4424af6f25f633e05157 → docs:write · holder research-agent · ttl 30s
[03] KEEPALIVE — renewal moved the expiry (moved=True). It cannot resurrect a dead lease.
[04] PERMIT — gate passed: e-stop clear, lease live, no gating fault. brief.md written.
[05] EXPIRED — the lapsed lease is denied. The denial is on the record.
[06] FAULT — TOOL_TIMEOUT gates web:read. Faults are resource-scoped: docs:write is unaffected.
[07] PERMIT — docs:write still flows while web:read is gated.
[08] E-STOP — one engagement halts every permit, everywhere.
[09] RELEASE — explicit release only. Permits flow again.
[10] CLAIM — provenance-stamped [inferred]: Demo run: 3 permits granted, 3 denied (expiry, fault, e-stop).
[11] AUDIT — ledger holds 3 permits, 3 denials, 1 claim. Nothing happened off the record.
[12]        denial reasons on record: estop, fault, lease_expired
