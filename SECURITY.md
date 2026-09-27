# Security Policy

## Scope

Interlock is a safety *substrate*, not a sandbox. It constrains code that
goes through it; it cannot constrain code that bypasses it. Treat it as one
layer in a defense-in-depth posture.

## Reporting

Do not open a public issue for a suspected vulnerability. Describe the
concern, with a reproduction, via the repository's private reporting channel
once the repo is public. You will receive an acknowledgment within 72 hours.

## What we will not promise

- That a lease cannot be bypassed by code outside the substrate.
- That the e-stop halts anything it cannot see.
- That the ledger is tamper-proof (it is tamper-evident by structure, not
  by cryptography — append-only is an operator discipline, not a guarantee).
