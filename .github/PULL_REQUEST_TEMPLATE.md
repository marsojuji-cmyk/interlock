## What changed
<!-- One sentence: what does this change? -->

## Why
<!-- The reason, with evidence: a failing test, a measured behavior, a cited source. -->

## Guarantee
<!-- What this change promises, stated checkably. What does it NOT promise? -->

## Failure behavior
<!-- How does this fail, and how would an operator notice? -->

## How it was verified
<!-- The exact commands you ran and the counts they printed, for example:
     `pytest -q` -> N passed -->

## Evidence commit hashes
<!-- The commit behind every number in this PR, its README or its docs. -->

## Checklist
- [ ] CI green
- [ ] `pytest -q` passes
- [ ] `ruff check src tests` passes
- [ ] Every claim traces to a command, a count and a commit
- [ ] No secrets, tokens or private paths in the diff
