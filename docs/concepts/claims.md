# CLAIMS

## The problem

When an agent reports what it did, the report usually carries no provenance,
no authority record, and no expiry date. "14 pages fetched" — fetched by
what, under whose authority, and for how long is that statement true? A
claim without provenance is a rumor with formatting. A claim without a
review date is a fact that forgot it could be wrong.

## How it works

Every assertion the system makes is stamped with five things: the text,
what produced it (provenance), under what authority it was produced, when
it must be reviewed, and what would prove it wrong (the falsifier). The
status records how the claim was established: `verified`, `inferred` (the
default), or `guessed`.

### STAGE 1 — STAMP

The agent stamps the claim at the moment of assertion, naming the lease id
as its authority. The stamp is cheap and mandatory: `claim()` both builds
the `Claim` and appends its record to the ledger's `claims` series, so no
claim exists unstamped.

### STAGE 2 — REVIEW

A claim carries `review_after_days`. Before that date it is reported with
its status; after it, `is_stale()` returns true and `check()` reports the
claim as stale — not as fact. Staleness is not an accusation. It is the
system remembering, on the reader's behalf, that evidence ages.

### STAGE 3 — FALSIFY

The falsifier states what would prove the claim wrong, concretely enough to
check: "re-fetch returns different content," not "if I'm mistaken." A
claim whose falsifier cannot be evaluated SHOULD be restated until it can
be, or downgraded to `guessed`.

## Safety

Claims are designed to make the record auditable, not to make assertions
true. A stamped falsehood is still a falsehood — but it is a falsehood
with an author, a date, and a way to check. Operators SHOULD treat
`verified` as a strong word: it means something checked the claim against
the world, not merely that the agent is confident. The checkable guarantee
is narrower: *within* the substrate, every claim carries its five stamps,
and stale claims are reported as stale. The tests cover it.

## A claim, end to end

At 2:35 the agent finishes the brief and stamps it: *provenance: 14 fetched
pages; authority: lease docs:write; review date: 7 days; falsifier: any
cited page returning different content on re-fetch.* At 2:40 the operator
reads the claim fresh and acts on it. Nine days later a second agent reads
the same ledger line and sees `stale` — the brief may still be right, but
the system no longer asserts it. The claim did not decay because someone
doubted it. It decayed because that is what claims do, and the substrate
was honest about it.
