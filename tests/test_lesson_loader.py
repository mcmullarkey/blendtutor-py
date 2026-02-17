"""Tests for lesson loader helpers."""

from blendtutor._lesson_loader import (
    collect_validation_results,
    empty_lessons_result,
    read_lesson_descriptions,
)


def test_empty_lessons_result_returns_empty_list():
    result = empty_lessons_result()
    assert result == []


def test_read_lesson_descriptions_reads_description(tmp_path):
    tmp = tmp_path / "lesson.yaml"
    tmp.write_text('description: "A test lesson"')

    descs = read_lesson_descriptions([str(tmp)])
    assert descs == ["A test lesson"]


def test_read_lesson_descriptions_returns_empty_on_missing(tmp_path):
    tmp = tmp_path / "lesson.yaml"
    tmp.write_text("lesson_name: Test")

    descs = read_lesson_descriptions([str(tmp)])
    assert descs == [""]


def test_read_lesson_descriptions_returns_empty_on_parse_error(tmp_path):
    tmp = tmp_path / "lesson.yaml"
    tmp.write_text("invalid: yaml: [broken")

    descs = read_lesson_descriptions([str(tmp)])
    assert descs == [""]


def test_collect_validation_all_ok():
    lesson = {
        "lesson_name": "Test",
        "description": "Desc",
        "textbook_reference": "Ref",
        "exercise": {
            "prompt": "Do something",
            "llm_evaluation_prompt": "Evaluate {student_code}",
            "code_template": "# code",
            "example_usage": "# usage",
            "success_criteria": "- works",
        },
    }
    report = collect_validation_results(lesson)
    statuses = [r["status"] for r in report]
    assert all(s == "OK" for s in statuses)


def test_collect_validation_missing_required():
    lesson = {"description": "Desc"}
    report = collect_validation_results(lesson)
    fails = [r for r in report if r["status"] == "FAIL"]
    fail_fields = [r["field"] for r in fails]
    assert "lesson_name" in fail_fields
    assert "exercise" in fail_fields


def test_collect_validation_missing_recommended():
    lesson = {
        "lesson_name": "Test",
        "exercise": {
            "prompt": "Do something",
            "llm_evaluation_prompt": "Evaluate {student_code}",
        },
    }
    report = collect_validation_results(lesson)
    warns = [r for r in report if r["status"] == "WARN"]
    warn_fields = [r["field"] for r in warns]
    assert "description" in warn_fields
    assert "textbook_reference" in warn_fields


def test_collect_validation_missing_placeholder():
    lesson = {
        "lesson_name": "Test",
        "exercise": {
            "prompt": "Do something",
            "llm_evaluation_prompt": "Evaluate the code",
        },
    }
    report = collect_validation_results(lesson)
    placeholder = [r for r in report if "placeholder" in r["field"]]
    assert len(placeholder) == 1
    assert placeholder[0]["status"] == "WARN"
