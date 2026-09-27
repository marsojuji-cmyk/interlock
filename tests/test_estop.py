"""Tests for the e-stop: engagement, release, and the clear assertion."""

import pytest

from interlock import EStopEngaged, InterlockError
from interlock.estop import EStop


def test_starts_clear():
    estop = EStop()
    assert estop.is_engaged is False
    estop.assert_clear()  # must not raise


def test_engage_latches():
    estop = EStop()
    estop.engage("operator halt")
    assert estop.is_engaged is True
    assert estop.reason == "operator halt"


def test_assert_clear_raises_when_engaged():
    estop = EStop()
    estop.engage("smoke in the server room")
    with pytest.raises(EStopEngaged, match="smoke in the server room"):
        estop.assert_clear()


def test_release_requires_deliberate_action():
    estop = EStop()
    estop.engage("halt")
    estop.release()
    assert estop.is_engaged is False
    assert estop.reason == ""
    estop.assert_clear()


def test_estop_error_derives_from_base():
    assert issubclass(EStopEngaged, InterlockError)
