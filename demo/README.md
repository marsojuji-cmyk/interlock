# The 90-second demonstrator

`scripts/demo_90s.py` runs Interlock end-to-end in one terminal, narrated:

1. **GRANT** — authority comes into existence only here, and it expires.
2. **KEEPALIVE** — renewal moves the expiry; it cannot resurrect a dead lease.
3. **PERMIT** — the gate passes: e-stop clear, lease live, no gating fault.
4. **EXPIRED** — a lapsed lease is denied, and the denial is on the record.
5. **FAULT** — a gating fault refuses permits on its resource only (`web:read`
   gated, `docs:write` unaffected).
6. **E-STOP** — one engagement halts every permit; release is explicit.
7. **CLAIM** — the run is stamped as a provenance-bearing claim.
8. **AUDIT** — the ledger holds every permit and every denial.

The expected output is captured in [TRANSCRIPT.md](TRANSCRIPT.md); the script
exits non-zero if any step behaves unexpectedly, so the transcript doubles as
a smoke test.

Run it:

```bash
python3 scripts/demo_90s.py
```
