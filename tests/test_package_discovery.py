"""Tests for lesson resolution helpers."""

import pytest

from blendtutor._package_discovery import (
    resolve_bare_name,
    resolve_file_path,
    resolve_lesson,
    resolve_qualified_name,
)
from blendtutor._validators import BlendtutorError


def test_resolve_file_path_resolves_existing(tmp_path):
    tmp = tmp_path / "lesson.yaml"
    tmp.write_text("lesson_name: Test")

    result = resolve_file_path(str(tmp))
    assert result["path"] == str(tmp.resolve())
    assert result["package"] is None
    assert isinstance(result["lesson_id"], str)


def test_resolve_file_path_errors_on_missing():
    with pytest.raises(BlendtutorError, match="not found"):
        resolve_file_path("/no/such/file.yaml")


def test_resolve_qualified_name_errors_on_malformed():
    with pytest.raises(BlendtutorError, match="Invalid lesson reference"):
        resolve_qualified_name(":name")
    with pytest.raises(BlendtutorError, match="Invalid lesson reference"):
        resolve_qualified_name("pkg:")


def test_resolve_qualified_name_errors_on_missing_lesson():
    with pytest.raises(BlendtutorError, match="not found in package"):
        resolve_qualified_name("blendtutor:nonexistent_lesson_xyz")


def test_resolve_bare_name_errors_on_unknown():
    with pytest.raises(BlendtutorError, match="not found"):
        resolve_bare_name("no_such_lesson_xyz")


def test_resolve_lesson_dispatches_to_file_path(tmp_path):
    tmp = tmp_path / "lesson.yaml"
    tmp.write_text("lesson_name: Test")

    result = resolve_lesson(str(tmp))
    assert result["path"] == str(tmp.resolve())
    assert result["package"] is None


def test_resolve_lesson_dispatches_to_qualified_name():
    with pytest.raises(BlendtutorError, match="not found in package"):
        resolve_lesson("blendtutor:nonexistent_lesson_xyz")


def test_resolve_lesson_dispatches_to_bare_name():
    with pytest.raises(BlendtutorError, match="not found"):
        resolve_lesson("no_such_lesson_xyz")
