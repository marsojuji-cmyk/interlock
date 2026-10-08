"""Regression tests: every ledger record reaches the OS as it is appended."""

import io
import json
import os
import subprocess
import sys
from pathlib import Path

from interlock.ledger import Ledger

SRC = str(Path(__file__).resolve().parents[1] / "src")


def _disk(path):
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def test_record_is_on_disk_before_close(tmp_path):
    path = str(tmp_path / "run.jsonl")
    ledger = Ledger(path)
    ledger.append("permits", {"action": "write"})
    records = [r for r in _disk(path) if r["_type"] == "record"]
    assert [r["action"] for r in records] == ["write"]
    ledger.close()


def test_record_survives_writer_crash(tmp_path):
    """A process that dies without close() still leaves every appended record."""
    path = str(tmp_path / "run.jsonl")
    script = (
        f"import os, sys; sys.path.insert(0, {SRC!r})\n"
        "from interlock.ledger import Ledger\n"
        f"ledger = Ledger({path!r})\n"
        "ledger.append('denials', {'reason': 'estop'})\n"
        "os._exit(1)  # no close(), no interpreter cleanup\n"
    )
    proc = subprocess.run([sys.executable, "-c", script], timeout=30, check=False)
    assert proc.returncode == 1
    records = [r for r in _disk(path) if r["_type"] == "record"]
    assert [r["reason"] for r in records] == ["estop"]


class _CountingBuffer(io.StringIO):
    def __init__(self):
        super().__init__()
        self.flushes = 0

    def flush(self):
        self.flushes += 1
        super().flush()


def test_caller_supplied_handle_is_flushed_per_record():
    buf = _CountingBuffer()
    ledger = Ledger(buf)
    after_open = buf.flushes
    ledger.append("claims", {"a": 1})  # series descriptor + record
    ledger.append("claims", {"a": 2})  # record
    assert buf.flushes - after_open >= 3


def test_close_fsyncs_an_owned_file(tmp_path, monkeypatch):
    calls = []
    real_fsync = os.fsync
    monkeypatch.setattr(os, "fsync", lambda fd: (calls.append(fd), real_fsync(fd)))
    ledger = Ledger(str(tmp_path / "run.jsonl"))
    ledger.append("claims", {"a": 1})
    ledger.close()
    ledger.close()  # idempotent: no second index, no second fsync
    assert len(calls) == 1
