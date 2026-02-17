"""blendtutor: AI-powered feedback on interactive coding exercises."""

from blendtutor._educator_tools import (
    create_lesson_package,
    use_blendtutor_evals,
    use_blendtutor_lesson,
)
from blendtutor._evaluation import open_editor, start_lesson, submit_code
from blendtutor._lesson_loader import list_lessons, validate_lesson
from blendtutor._package_discovery import invalidate_lesson_cache
from blendtutor._state import reset_lesson

__all__ = [
    "start_lesson",
    "open_editor",
    "submit_code",
    "reset_lesson",
    "list_lessons",
    "validate_lesson",
    "invalidate_lesson_cache",
    "create_lesson_package",
    "use_blendtutor_lesson",
    "use_blendtutor_evals",
]
