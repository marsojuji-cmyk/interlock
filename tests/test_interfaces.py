"""Tests for interface records: declaration, validation, and the registry."""

import pytest

from interlock.interfaces import REGISTRY, declare


def _fields(name="test.iface", **overrides):
    fields = {
        "name": name,
        "guarantees": "permits only with a live lease",
        "constraints": "no network access",
        "owner": "operator",
        "failure_behavior": "refuse and log",
    }
    fields.update(overrides)
    return fields


def test_declare_registers_record():
    record = declare(**_fields(name="iface.alpha"))
    assert REGISTRY["iface.alpha"] is record
    assert record.validate() is record


def test_validate_rejects_empty_fields():
    for field in ("name", "guarantees", "constraints", "owner", "failure_behavior"):
        fields = _fields(name=f"iface.bad.{field}")
        fields[field] = ""
        with pytest.raises(ValueError, match=field):
            declare(**fields)


def test_redeclare_overwrites_same_name():
    first = declare(**_fields(name="iface.overwrite"))
    second = declare(**_fields(name="iface.overwrite", owner="supervisor"))
    assert REGISTRY["iface.overwrite"] is second
    assert second is not first
