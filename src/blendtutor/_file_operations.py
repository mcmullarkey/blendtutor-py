"""Temp file management for lesson code."""

from __future__ import annotations

import os
import tempfile

from blendtutor._validators import BlendtutorError


def create_lesson_code_file(lesson: dict) -> str:
    """Create a temp .py file with the lesson's code template."""
    fd, code_file = tempfile.mkstemp(suffix=".py")

    template = lesson.get("exercise", {}).get("code_template")
    if template:
        content = template
    else:
        content = "# Write your code here\n"

    with os.fdopen(fd, "w") as f:
        f.write(content)

    return code_file


def retrieve_student_code(code_string: str | None, code_file: str) -> str:
    """Get code from a string argument or the temp file.

    If code_string is provided, also saves it to the temp file for persistence.
    """
    if code_string is not None:
        with open(code_file, "w") as f:
            f.write(code_string)
        return code_string

    if not os.path.exists(code_file):
        raise BlendtutorError(
            "Code file not found.\nUse open_editor() to write your code first."
        )

    with open(code_file) as f:
        return f.read()
