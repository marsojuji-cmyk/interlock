"""Tests for the fault bus: reporting, clearing, and gating."""

import pytest

from interlock import FaultActive, InterlockError
from interlock.faults import FaultBus


def test_report_returns_structured_fault():
    bus = FaultBus()
    fault = bus.report(code="TOOL_TIMEOUT", severity="major", resource="web:read")
    assert fault.id == 1
    assert fault.code == "TOOL_TIMEOUT"
    assert fault.severity == "major"
    assert fault.resource == "web:read"
    assert fault.detail == ""
    assert fault.cleared is False


def test_report_with_detail():
    bus = FaultBus()
    fault = bus.report("E_CONN", "critical", "db:write", detail="connection refused")
    assert fault.detail == "connection refused"


def test_ids_increment():
    bus = FaultBus()
    assert bus.report("A", "minor", "r").id == 1
    assert bus.report("B", "minor", "r").id == 2


def test_invalid_severity_rejected():
    bus = FaultBus()
    with pytest.raises(ValueError, match="severity"):
        bus.report("X", "catastrophic", "r")


def test_clear_marks_fault():
    bus = FaultBus()
    fault = bus.report("TOOL_TIMEOUT", "major", "web:read")
    cleared = bus.clear(fault.id)
    assert cleared.cleared is True
    assert bus.active() == []


def test_clear_unknown_id_raises():
    bus = FaultBus()
    with pytest.raises(KeyError):
        bus.clear(999)


def test_active_filters_by_resource():
    bus = FaultBus()
    bus.report("A", "minor", "web:read")
    bus.report("B", "minor", "docs:write")
    assert {f.resource for f in bus.active()} == {"web:read", "docs:write"}
    assert [f.code for f in bus.active("web:read")] == ["A"]


def test_gating_major_and_critical():
    bus = FaultBus()
    assert bus.gating("web:read") is False
    bus.report("TOOL_TIMEOUT", "major", "web:read")
    assert bus.gating("web:read") is True
    assert bus.gating("docs:write") is False  # other resources unaffected


def test_minor_does_not_gate():
    bus = FaultBus()
    bus.report("SLOW", "minor", "web:read")
    assert bus.gating("web:read") is False


def test_cleared_fault_no_longer_gates():
    bus = FaultBus()
    fault = bus.report("TOOL_TIMEOUT", "critical", "web:read")
    bus.clear(fault.id)
    assert bus.gating("web:read") is False


def test_fault_error_derives_from_base():
    assert issubclass(FaultActive, InterlockError)
