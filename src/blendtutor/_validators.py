"""Error classes and state validation for blendtutor."""

from __future__ import annotations

from blendtutor._state import _state


class BlendtutorError(Exception):
    """Base exception for blendtutor."""


class NoActiveLessonError(BlendtutorError):
    """Raised when no lesson has been started."""


class LessonCompleteError(BlendtutorError):
    """Raised when the current lesson is already complete."""


def validate_lesson_active(*, allow_completed: bool = False) -> None:
    """Check that a lesson is active and optionally not yet complete.

    Raises:
        NoActiveLessonError: If no lesson has been started.
        LessonCompleteError: If the lesson is complete and allow_completed is False.
    """
    if _state["current_lesson"] is None:
        raise NoActiveLessonError(
            "No active lesson.\nPlease start a lesson first using: start_lesson()"
        )

    if not allow_completed and _state["lesson_complete"]:
        raise LessonCompleteError(
            "This lesson is already complete!\nStart a new lesson with: start_lesson()"
        )
