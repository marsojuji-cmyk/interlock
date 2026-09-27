"""Tests for claims: stamping, records, staleness, and status validation."""

import pytest

from interlock.claims import Claim


def _claim(clock=None, **overrides):
    fields = {
        "text": "14 pages fetched.",
        "provenance": "tool:web-fetch",
        "authority": "lease-abc",
        "review_after_days": 7,
        "falsifier": "re-fetch returns different content",
    }
    fields.update(overrides)
    if clock is not None:
        fields["_clock"] = clock
        fields["created"] = clock()
    return Claim(**fields)


def test_default_status_inferred():
    assert _claim().status == "inferred"


def test_record_carries_all_fields():
    rec = _claim(status="verified").record()
    assert rec == {
        "text": "14 pages fetched.",
        "provenance": "tool:web-fetch",
        "authority": "lease-abc",
        "review_after_days": 7,
        "falsifier": "re-fetch returns different content",
        "status": "verified",
        "created": rec["created"],
    }


def test_invalid_status_rejected():
    with pytest.raises(ValueError, match="status"):
        _claim(status="certain")


def test_not_stale_before_review_date(clock):
    claim = _claim(clock)
    clock.advance(6 * 86400)
    assert claim.is_stale() is False


def test_stale_after_review_date(clock):
    claim = _claim(clock)
    clock.advance(7 * 86400 + 1)
    assert claim.is_stale() is True


def test_check_returns_status_and_staleness(clock):
    claim = _claim(clock, status="guessed")
    assert claim.check() == ("guessed", False)
    clock.advance(8 * 86400)
    assert claim.check() == ("guessed", True)
