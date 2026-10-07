# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/). The single source of truth for
the current version is `interlock.__version__` (mirrored into `VERSION` by
`scripts/release.sh`).

## [Unreleased]
### Fixed
- `Ledger(path)` no longer erases an existing audit log. A path opens in append mode by
  default, so reopening a ledger keeps every earlier run and starts a new self-describing
  segment. `Ledger(path, mode="w")` truncates deliberately; any other mode raises
  `ValueError`. Regression tests: `tests/test_ledger_reopen.py`.
- The ledger flushes every line as it writes it. A record now survives the writing process
  crashing before `close()`; before, records sat in the process buffer and died with it.
  `close()` fsyncs a file the ledger opened itself. Regression tests:
  `tests/test_ledger_durability.py`.

## [0.1.0] — 2026-09-27
### Added
- `interlock.leases`: time-bounded authority grants with keepalive renewal and expiry.
- `interlock.estop`: global halt — one engagement suspends all permits; release is explicit.
- `interlock.faults`: fault bus with severity; gating faults refuse permits on affected resources.
- `interlock.claims`: provenance-stamped assertions (provenance, authority, review date, falsifier).
- `interlock.interfaces`: handoff records stating guarantees, constraints, ownership, failure behavior.
- `interlock.ledger`: self-describing run ledger (format descriptor, per-series schemas, closing index).
- Concept documentation in `docs/concepts/`, quickstart in `docs/guides/`.
- CI (Python 3.11–3.13, pytest, ruff), issue/PR templates, release script.
