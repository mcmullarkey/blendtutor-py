"""YAML loading, validation, and lesson listing."""

from __future__ import annotations

import os

import yaml

from blendtutor._display import (
    console,
    display_lesson_table,
)
from blendtutor._package_discovery import build_lesson_index, resolve_lesson
from blendtutor._validators import BlendtutorError


def read_lesson_yaml(lesson_path: str, lesson_name: str) -> dict:
    """Read and parse a lesson YAML file with error handling."""
    try:
        with open(lesson_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise BlendtutorError(
            f"Error reading lesson file '{lesson_name}.yaml'.\n{e}"
        ) from e


def validate_lesson_structure(lesson: dict, lesson_name: str) -> None:
    """Validate that a lesson contains all required fields."""
    required_fields = ["lesson_name", "exercise"]
    missing = [f for f in required_fields if f not in lesson]
    if missing:
        raise BlendtutorError(
            f"Lesson '{lesson_name}' is missing required fields: {', '.join(missing)}"
        )

    required_exercise_fields = ["prompt", "llm_evaluation_prompt"]
    missing_exercise = [
        f for f in required_exercise_fields if f not in lesson.get("exercise", {})
    ]
    if missing_exercise:
        raise BlendtutorError(
            f"Lesson '{lesson_name}' exercise is missing required fields: "
            f"{', '.join(missing_exercise)}"
        )


def load_lesson(lesson_name: str) -> dict:
    """Load and validate a lesson, attaching discovery metadata."""
    resolved = resolve_lesson(lesson_name)
    lesson = read_lesson_yaml(resolved["path"], resolved["lesson_id"])
    validate_lesson_structure(lesson, resolved["lesson_id"])

    lesson[".source_package"] = resolved["package"]
    lesson[".lesson_id"] = resolved["lesson_id"]
    lesson[".source_path"] = resolved["path"]

    return lesson


def empty_lessons_result() -> list[dict]:
    """Return an empty lessons list."""
    return []


def read_lesson_descriptions(paths: list[str]) -> list[str]:
    """Read lesson descriptions from YAML files.

    Returns empty string for files that can't be read or have no description.
    """
    descriptions = []
    for p in paths:
        try:
            with open(p) as f:
                data = yaml.safe_load(f)
            descriptions.append(data.get("description", "") or "")
        except Exception:
            descriptions.append("")
    return descriptions


def list_lessons(package: str | None = None, *, quiet: bool = False) -> list[dict]:
    """List available lessons across all packages.

    Args:
        package: Filter to a specific package. None shows all.
        quiet: If True, suppress printed output.

    Returns:
        List of dicts with lesson_id, package, and description.
    """
    index = build_lesson_index()
    if package is not None:
        index = [entry for entry in index if entry["package"] == package]

    if not index:
        if not quiet:
            if package is None:
                console.print("No lessons found.")
            else:
                console.print(f"No lessons found in package '{package}'.")
        return empty_lessons_result()

    paths = [entry["path"] for entry in index]
    descriptions = read_lesson_descriptions(paths)

    result = [
        {
            "lesson_id": entry["lesson_id"],
            "package": entry["package"],
            "description": desc,
        }
        for entry, desc in zip(index, descriptions)
    ]

    if not quiet:
        display_lesson_table(result)

    return result


def validate_lesson(path: str) -> list[dict]:
    """Validate a lesson YAML file and print a report.

    Returns a list of dicts with field, status ('OK'/'FAIL'/'WARN'), and message.
    """
    if not os.path.exists(path):
        raise BlendtutorError(f"File not found: {path}")

    try:
        with open(path) as f:
            lesson = yaml.safe_load(f)
    except Exception as e:
        raise BlendtutorError(f"Failed to parse YAML.\n{e}") from e

    report = collect_validation_results(lesson)
    print_validation_report(report, path)
    return report


def collect_validation_results(lesson: dict) -> list[dict]:
    """Run field checks on a parsed lesson and return results."""
    results = []

    # Required top-level fields
    results.extend(check_fields_present(["lesson_name", "exercise"], lesson))

    # Recommended top-level fields
    results.extend(
        check_fields_present(
            ["description", "textbook_reference"],
            lesson,
            fail_status="WARN",
            fail_msg="Recommended field missing",
        )
    )

    # Exercise fields
    if "exercise" in lesson and isinstance(lesson["exercise"], dict):
        ex = lesson["exercise"]
        results.extend(
            check_fields_present(
                ["prompt", "llm_evaluation_prompt"], ex, prefix="exercise."
            )
        )
        results.extend(
            check_fields_present(
                ["code_template", "example_usage", "success_criteria"],
                ex,
                prefix="exercise.",
                fail_status="WARN",
                fail_msg="Recommended field missing",
            )
        )

        # Check {student_code} placeholder
        if "llm_evaluation_prompt" in ex:
            if "{student_code}" in ex["llm_evaluation_prompt"]:
                results.append(
                    {
                        "field": "{student_code} placeholder",
                        "status": "OK",
                        "message": "Found in llm_evaluation_prompt",
                    }
                )
            else:
                results.append(
                    {
                        "field": "{student_code} placeholder",
                        "status": "WARN",
                        "message": (
                            "Not found in llm_evaluation_prompt "
                            "\u2014 student code may not be inserted"
                        ),
                    }
                )

    return results


def check_fields_present(
    fields: list[str],
    container: dict,
    *,
    prefix: str = "",
    fail_status: str = "FAIL",
    fail_msg: str = "Missing required field",
) -> list[dict]:
    """Check whether fields are present in a dict."""
    results = []
    for field in fields:
        full_name = f"{prefix}{field}" if prefix else field
        if field in container:
            results.append({"field": full_name, "status": "OK", "message": "Present"})
        else:
            results.append(
                {"field": full_name, "status": fail_status, "message": fail_msg}
            )
    return results


def print_validation_report(report: list[dict], path: str) -> None:
    """Print a formatted validation report."""
    console.print(f"\nLesson validation: {path}")
    console.print("-" * 60)

    for row in report:
        icon = {"OK": "[OK]  ", "FAIL": "[FAIL]", "WARN": "[WARN]"}[row["status"]]
        console.print(f"{icon} {row['field']} - {row['message']}")

    fails = sum(1 for r in report if r["status"] == "FAIL")
    warns = sum(1 for r in report if r["status"] == "WARN")
    console.print("-" * 60)

    if fails > 0:
        console.print(
            f"{fails} error(s) found. Fix FAIL items before using this lesson."
        )
    elif warns > 0:
        console.print(f"Lesson is valid with {warns} warning(s).")
    else:
        console.print("Lesson is valid.")
    console.print()
