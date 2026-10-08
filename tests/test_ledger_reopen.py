"""Regression tests: reopening a path-backed ledger must never erase earlier runs."""

import json

import pytest

from interlock.ledger import Ledger


def _file_lines(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def test_reopening_a_path_preserves_earlier_runs(tmp_path):
    path = str(tmp_path / "run.jsonl")
    first = Ledger(path)
    first.append("claims", {"text": "run one"})
    first.close()

    second = Ledger(path)  # a new process opening the same audit log
    second.append("claims", {"text": "run two"})
    second.close()

    texts = [r["text"] for r in _file_lines(path) if r["_type"] == "record"]
    assert texts == ["run one", "run two"]


def test_reopen_starts_a_new_self_describing_segment(tmp_path):
    path = str(tmp_path / "run.jsonl")
    for text in ("run one", "run two"):
        ledger = Ledger(path)
        ledger.append("claims", {"text": text})
        ledger.close()
    lines = _file_lines(path)
    formats = [i for i, line in enumerate(lines) if line["_type"] == "format"]
    indexes = [line for line in lines if line["_type"] == "index"]
    series = [line for line in lines if line["_type"] == "series"]
    assert formats == [0, 4]  # format, series, record, index | format, ...
    assert len(series) == 2  # each segment declares its own schema
    assert [ix["series"]["claims"]["count"] for ix in indexes] == [1, 1]


def test_read_series_spans_segments(tmp_path):
    path = str(tmp_path / "run.jsonl")
    Ledger(path).close()
    first = Ledger(path)
    first.append("claims", {"text": "earlier"})
    first.close()
    second = Ledger(path)
    second.append("claims", {"text": "later"})
    assert [r["text"] for r in second.read_series("claims")] == ["earlier", "later"]
    second.close()


def test_mode_w_truncates_deliberately(tmp_path):
    path = str(tmp_path / "run.jsonl")
    first = Ledger(path)
    first.append("claims", {"text": "discard me"})
    first.close()
    fresh = Ledger(path, mode="w")
    fresh.close()
    assert [line["_type"] for line in _file_lines(path)] == ["format", "index"]


def test_invalid_mode_rejected(tmp_path):
    with pytest.raises(ValueError, match="mode"):
        Ledger(str(tmp_path / "run.jsonl"), mode="r+")
