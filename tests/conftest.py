"""Shared fixtures for blendtutor tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def tmp_yaml(tmp_path):
    """Create a temporary YAML file and return its path."""

    def _make(content: str) -> str:
        path = tmp_path / "lesson.yaml"
        path.write_text(content)
        return str(path)

    return _make


@pytest.fixture
def valid_lesson_yaml(tmp_path):
    """Create a valid lesson YAML file."""
    content = """\
lesson_name: "Test Lesson"
description: "A test lesson"
textbook_reference: "Test Reference"
exercise:
  type: "function_writing"
  prompt: "Write a test function."
  code_template: |
    def test():
        pass
  example_usage: |
    test()
  success_criteria: |
    - Works correctly
  llm_evaluation_prompt: |
    Evaluate: {student_code}
"""
    path = tmp_path / "test_lesson.yaml"
    path.write_text(content)
    return str(path)
