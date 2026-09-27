# LEDGER

## The problem

A run log that needs its writer's source code to be understood is not a
record — it is a souvenir. Most agent logs are line-oriented text with
implicit schemas: readable the week they are written, archaeological a
month later. An auditor arriving with no prior knowledge should still be
able to answer: what happened, in what order, under what authority.

## How it works

The ledger is JSONL that describes itself. It opens with a format
descriptor, each series declares its schema on first use, every record
carries its series and capture time, and the file closes with an index.

### STAGE 1 — OPEN

The first line is always the format descriptor:
`{"_type": "format", "format": "interlock-ledger", "version": "1.0.0"}`.
It tells a future reader what grammar the rest of the file speaks, before
a single event is recorded.

### STAGE 2 — APPEND

The first append to a new series writes a series descriptor declaring the
schema — the record's sorted keys. Every record is then stamped with
`_series` and `_ts`, a UTC ISO-8601 capture time. Series are independent:
`grants`, `permits`, `denials`, `claims`, and whatever the operator adds.
`read_series(name)` replays one series in append order.

### STAGE 3 — CLOSE

`close()` appends the index: per series, the record count and the first and
last timestamps. The index makes any moment of the run randomly accessible
without scanning the whole file. Closing is idempotent — a run ends once,
even if `close()` is called twice.

## Safety

The ledger is designed to make the run auditable, not to make the run
safe. It records what the substrate saw; it cannot record what bypassed
the substrate. Operators SHOULD treat the ledger as evidence, not as proof:
a complete ledger shows every permit the gate issued, and says nothing
about actions taken outside the gate. The checkable guarantee is narrower:
the format descriptor is first, every series declares its schema, every
record carries its time, and the index closes the file. The tests cover it.

## A ledger, end to end

At 2:40 the operator opens `run.jsonl`. Line one declares the format, so
no documentation hunt is needed. The series descriptors say what `claims`
and `denials` contain before a single record is read. The index says the
`denials` series has one record between 02:00:40 and 02:00:40 — a single
refusal, already understood. The operator replays `claims`, finds the
brief's stamp with its 7-day review date, and closes the file. Nothing
about the run is a matter of trust. It is a matter of record — and the
record introduced itself.
