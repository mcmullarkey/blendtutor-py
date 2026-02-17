"""Module-level session state for blendtutor."""

from __future__ import annotations

import os

_state: dict = {
    "current_lesson": None,
    "lesson_complete": False,
    "model": None,
    "code_file": None,
    "source_package": None,
    "lesson_id": None,
    "current_code": None,
}


def initialize_lesson_state(lesson: dict, model: str | None, code_file: str) -> None:
    """Populate state from a loaded lesson."""
    _state["current_lesson"] = lesson
    _state["lesson_complete"] = False
    _state["model"] = model
    _state["code_file"] = code_file
    _state["source_package"] = lesson.get(".source_package")
    _state["lesson_id"] = lesson.get(".lesson_id")


def reset_lesson() -> None:
    """Clear lesson state and delete temp file."""
    code_file = _state.get("code_file")
    if code_file and os.path.exists(code_file):
        os.unlink(code_file)

    _state["current_lesson"] = None
    _state["lesson_complete"] = False
    _state["current_code"] = None
    _state["model"] = None
    _state["code_file"] = None
    _state["source_package"] = None
    _state["lesson_id"] = None

    print("\nLesson state cleared.")
    print("Start a new lesson with: start_lesson()\n")
