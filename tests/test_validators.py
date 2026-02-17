"""Tests for validation helpers."""

import pytest

from blendtutor._state import _state
from blendtutor._validators import (
    LessonCompleteError,
    NoActiveLessonError,
    validate_lesson_active,
)


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    original = _state.copy()
    yield
    _state.update(original)


def test_validate_lesson_active_no_lesson():
    _state["current_lesson"] = None
    with pytest.raises(NoActiveLessonError, match="No active lesson"):
        validate_lesson_active()


def test_validate_lesson_active_completed_lesson():
    _state["current_lesson"] = {"lesson_name": "Test"}
    _state["lesson_complete"] = True
    with pytest.raises(LessonCompleteError, match="already complete"):
        validate_lesson_active()


def test_validate_lesson_active_completed_allowed():
    _state["current_lesson"] = {"lesson_name": "Test"}
    _state["lesson_complete"] = True
    # Should not raise
    validate_lesson_active(allow_completed=True)


def test_validate_lesson_active_success():
    _state["current_lesson"] = {"lesson_name": "Test"}
    _state["lesson_complete"] = False
    # Should not raise
    validate_lesson_active()
