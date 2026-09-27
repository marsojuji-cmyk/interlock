"""Tests for the ledger: format descriptor, series descriptors, records, index."""

import json

import pytest

from interlock.ledger import Ledger


def _lines(ledger):
    return [json.loads(line) for line in ledger._lines()]


def test_first_line_is_format_descriptor():
    ledger = Ledger()
    first = _lines(ledger)[0]
    assert first == {"_type": "format", "format": "interlock-ledger", "version": "1.0.0"}


def test_first_append_writes_series_descriptor_with_sorted_schema():
    ledger = Ledger()
    ledger.append("claims", {"text": "x", "authority": "y"})
    second = _lines(ledger)[1]
    assert second["_type"] == "series"
    assert second["series"] == "claims"
    assert second["schema"] == ["authority", "text"]


def test_series_descriptor_written_once_per_series():
    ledger = Ledger()
    ledger.append("claims", {"a": 1})
    ledger.append("claims", {"a": 2})
    ledger.append("faults", {"b": 1})
    descriptors = [line for line in _lines(ledger) if line["_type"] == "series"]
    assert [(d["series"]) for d in descriptors] == ["claims", "faults"]


def test_records_stamped_with_series_and_utc_ts():
    ledger = Ledger()
    entry = ledger.append("claims", {"text": "hello"})
    assert entry["_series"] == "claims"
    assert entry["_type"] == "record"
    assert entry["_ts"].endswith("+00:00")  # UTC ISO-8601


def test_close_appends_index_with_counts():
    ledger = Ledger()
    ledger.append("claims", {"a": 1})
    ledger.append("claims", {"a": 2})
    ledger.append("faults", {"b": 1})
    ledger.close()
    lines = _lines(ledger)
    index = lines[-1]
    assert index["_type"] == "index"
    assert index["series"]["claims"]["count"] == 2
    assert index["series"]["faults"]["count"] == 1
    info = index["series"]["claims"]
    assert info["first_ts"] <= info["last_ts"]


def test_close_is_idempotent():
    ledger = Ledger()
    ledger.append("claims", {"a": 1})
    ledger.close()
    ledger.close()
    indexes = [line for line in _lines(ledger) if line["_type"] == "index"]
    assert len(indexes) == 1


def test_append_after_close_rejected():
    ledger = Ledger()
    ledger.close()
    with pytest.raises(ValueError, match="closed"):
        ledger.append("claims", {"a": 1})


def test_read_series_yields_only_that_series():
    ledger = Ledger()
    ledger.append("claims", {"text": "one"})
    ledger.append("faults", {"code": "X"})
    ledger.append("claims", {"text": "two"})
    texts = [rec["text"] for rec in ledger.read_series("claims")]
    assert texts == ["one", "two"]
    assert list(ledger.read_series("missing")) == []


def test_path_based_ledger_roundtrip(tmp_path):
    path = str(tmp_path / "run.jsonl")
    ledger = Ledger(path)
    ledger.append("claims", {"text": "file-backed"})
    ledger.close()
    with open(path, encoding="utf-8") as handle:
        lines = [json.loads(line) for line in handle]
    assert lines[0]["_type"] == "format"
    assert lines[-1]["_type"] == "index"
    assert lines[-1]["series"]["claims"]["count"] == 1
