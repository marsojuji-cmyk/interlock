# Contributing

## The contract

Every change ships with four things: the code, a test that fails without
it, a changelog entry, and — for behavioral changes — a docs update. A PR
that cannot state its guarantee and its failure behavior is not ready.

## Workflow

1. Open an issue first for anything beyond a typo. Small is good; small and
   reversible is better.
2. Branch from `main`. Keep branches short-lived.
3. `pip install -e ".[test]"`, then `pytest -q` and `ruff check src tests`
   before pushing. CI runs the same on Python 3.11–3.13.
4. Fill in the PR template completely. "N/A" is an answer only when you say
   why it doesn't apply.

## Releases

Releases are cut by the maintainer with `scripts/release.sh`, which verifies
tests, mirrors the version into `VERSION`, tags `vX.Y.Z`, and updates the
changelog. Never hand-edit `VERSION` — it is written by the script.
