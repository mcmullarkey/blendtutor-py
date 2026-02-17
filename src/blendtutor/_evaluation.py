"""Student workflow: start_lesson, open_editor, submit_code, reset_lesson."""

from __future__ import annotations

import os
import platform
import subprocess

from blendtutor._display import (
    console,
    display_feedback,
    display_lesson_content,
    display_lesson_header,
    display_retry_instructions,
    display_usage_instructions,
)
from blendtutor._file_operations import create_lesson_code_file, retrieve_student_code
from blendtutor._fireworks import evaluate_with_llm
from blendtutor._lesson_loader import list_lessons, load_lesson
from blendtutor._state import _state, initialize_lesson_state
from blendtutor._validators import validate_lesson_active


def start_lesson(
    lesson_name: str = "add_two_numbers", model: str | None = None
) -> None:
    """Load a lesson and begin an interactive learning session."""
    lesson = load_lesson(lesson_name)
    code_file = create_lesson_code_file(lesson)
    initialize_lesson_state(lesson, model, code_file)

    display_lesson_header(lesson)
    display_lesson_content(lesson)
    display_usage_instructions()


def open_editor() -> None:
    """Open the lesson's code file in the system editor."""
    validate_lesson_active(allow_completed=False)

    console.print("\nOpening editor...")
    console.print("Write your code, save the file, and close the editor.")
    console.print("Then call submit_code() to evaluate.\n")

    editor = _get_editor()
    subprocess.run([editor, _state["code_file"]])


def submit_code(code_string: str | None = None) -> None:
    """Submit code for AI evaluation and display feedback."""
    validate_lesson_active(allow_completed=False)

    code_string = retrieve_student_code(code_string, _state["code_file"])
    _state["current_code"] = code_string

    lesson = _state["current_lesson"]
    result = _evaluate_student_submission(code_string, lesson, _state["model"])

    display_feedback(result["feedback"])

    if _check_feedback_correct(result):
        _handle_lesson_completion(lesson)
    else:
        display_retry_instructions()


def _evaluate_student_submission(
    code_string: str, lesson: dict, model: str | None
) -> dict:
    """Print status and call evaluate_with_llm."""
    console.print("\nEvaluating your code with AI...\n")

    return evaluate_with_llm(
        student_code=code_string,
        exercise_prompt=lesson["exercise"]["llm_evaluation_prompt"],
        model=model,
    )


def _check_feedback_correct(result: dict) -> bool:
    """Return whether the result indicates a correct answer."""
    return bool(result.get("is_correct"))


def _format_next_lessons(current_id: str | None) -> list[str]:
    """List other available lessons as start_lesson() suggestions."""
    available = list_lessons(quiet=True)
    other = [les for les in available if les["lesson_id"] != current_id]
    if not other:
        return []

    suggestions = []
    for les in other:
        ref = les["lesson_id"]
        if les["package"] != "blendtutor":
            ref = f"{les['package']}:{ref}"
        suggestions.append(f'  start_lesson("{ref}")')
    return suggestions


def _handle_lesson_completion(lesson: dict) -> None:
    """Mark lesson as complete and show next suggestions."""
    console.print("Congratulations! Lesson complete!\n")
    _state["lesson_complete"] = True

    suggestions = _format_next_lessons(lesson.get(".lesson_id"))
    if suggestions:
        console.print("Try another lesson:")
        for s in suggestions:
            console.print(s)
        console.print()


def _get_editor() -> str:
    """Resolve editor from env vars with platform fallbacks."""
    for var in ("VISUAL", "EDITOR"):
        editor = os.environ.get(var)
        if editor:
            return editor

    if platform.system() == "Darwin":
        return "open"
    if platform.system() == "Windows":
        return "notepad"
    return "vi"
