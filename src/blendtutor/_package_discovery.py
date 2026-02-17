"""Cross-package lesson discovery via entry points."""

from __future__ import annotations

import importlib.metadata
import importlib.resources
import os
from pathlib import Path

from blendtutor._validators import BlendtutorError

_discovery_cache: list[dict] | None = None


def find_lesson_packages() -> list[str]:
    """Find installed packages that register blendtutor lessons via entry points."""
    eps = importlib.metadata.entry_points(group="blendtutor.lessons")
    return [ep.name for ep in eps]


def _get_lessons_dir(package_name: str) -> Path | None:
    """Get the lessons directory for a package using importlib.resources."""
    try:
        pkg_files = importlib.resources.files(package_name)
        lessons_dir = pkg_files / "lessons"
        # Convert to a real path if it's a traversable
        if hasattr(lessons_dir, "_path"):
            real_path = Path(lessons_dir._path)
        else:
            real_path = Path(str(lessons_dir))

        if real_path.is_dir():
            return real_path
    except (ModuleNotFoundError, TypeError, FileNotFoundError):
        pass
    return None


def build_lesson_index() -> list[dict]:
    """Build and return a cached list of all discoverable lessons."""
    global _discovery_cache
    if _discovery_cache is not None:
        return _discovery_cache

    packages = find_lesson_packages()
    rows: list[dict] = []

    for pkg in packages:
        lessons_dir = _get_lessons_dir(pkg)
        if lessons_dir is None:
            continue

        for yaml_file in sorted(lessons_dir.glob("*.yaml")):
            lesson_id = yaml_file.stem
            rows.append(
                {"lesson_id": lesson_id, "package": pkg, "path": str(yaml_file)}
            )

    _discovery_cache = rows
    return _discovery_cache


def resolve_file_path(lesson_ref: str) -> dict:
    """Resolve a file path lesson reference (contains '/' or ends in '.yaml')."""
    if not os.path.exists(lesson_ref):
        raise BlendtutorError(f"Lesson file not found: {lesson_ref}")

    return {
        "path": os.path.abspath(lesson_ref),
        "package": None,
        "lesson_id": Path(lesson_ref).stem,
    }


def resolve_qualified_name(lesson_ref: str) -> dict:
    """Resolve a 'pkg:name' lesson reference."""
    parts = lesson_ref.split(":", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise BlendtutorError(
            f"Invalid lesson reference: '{lesson_ref}'\n"
            "Use 'package:lesson_name' format."
        )

    pkg, name = parts
    lessons_dir = _get_lessons_dir(pkg)
    if lessons_dir is None:
        raise BlendtutorError(
            f"Lesson '{name}' not found in package '{pkg}'.\n"
            f'Use list_lessons(package="{pkg}") to see available lessons.'
        )

    lesson_path = lessons_dir / f"{name}.yaml"
    if not lesson_path.exists():
        raise BlendtutorError(
            f"Lesson '{name}' not found in package '{pkg}'.\n"
            f'Use list_lessons(package="{pkg}") to see available lessons.'
        )

    return {"path": str(lesson_path), "package": pkg, "lesson_id": name}


def resolve_bare_name(lesson_ref: str) -> dict:
    """Resolve a bare lesson name by searching all packages."""
    index = build_lesson_index()
    matches = [entry for entry in index if entry["lesson_id"] == lesson_ref]

    if not matches:
        raise BlendtutorError(
            f"Lesson '{lesson_ref}' not found.\n"
            "Use list_lessons() to see available lessons."
        )

    if len(matches) > 1:
        pkgs = [m["package"] for m in matches]
        qualified = [f"{p}:{lesson_ref}" for p in pkgs]
        raise BlendtutorError(
            f"Lesson '{lesson_ref}' found in multiple packages:\n"
            + "\n".join(f"  * {q}" for q in qualified)
            + f'\nUse a qualified name, e.g.: start_lesson("{qualified[0]}")'
        )

    return matches[0]


def resolve_lesson(lesson_ref: str) -> dict:
    """Resolve a lesson reference to a path.

    Accepts three forms:
      - File path: contains '/' or ends in '.yaml'
      - Qualified: 'pkg:name' (single colon)
      - Bare name: searches all packages
    """
    if "/" in lesson_ref or lesson_ref.endswith(".yaml"):
        return resolve_file_path(lesson_ref)

    if ":" in lesson_ref:
        return resolve_qualified_name(lesson_ref)

    return resolve_bare_name(lesson_ref)


def invalidate_lesson_cache() -> None:
    """Clear the lesson discovery cache."""
    global _discovery_cache
    _discovery_cache = None
