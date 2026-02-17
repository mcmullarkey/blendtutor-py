"""Console formatting with rich for blendtutor."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def display_lesson_header(lesson: dict) -> None:
    """Display lesson title, package, and reference."""
    lines = [f"Lesson: {lesson['lesson_name']}"]

    source_pkg = lesson.get(".source_package")
    if source_pkg and source_pkg != "blendtutor":
        lines.append(f"Package: {source_pkg}")

    if lesson.get("textbook_reference"):
        lines.append(f"Reference: {lesson['textbook_reference']}")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title="Blendtutor: Interactive Coding Lessons",
            width=60,
        )
    )
    console.print()


def display_lesson_content(lesson: dict) -> None:
    """Display lesson description, exercise prompt, and example usage."""
    if lesson.get("description"):
        console.print(lesson["description"])
        console.print()

    console.print("[bold]EXERCISE:[/bold]")
    console.print(lesson["exercise"]["prompt"])

    if lesson["exercise"].get("example_usage"):
        console.print("[bold]EXAMPLE USAGE:[/bold]")
        console.print(lesson["exercise"]["example_usage"])


def display_usage_instructions() -> None:
    """Display numbered workflow steps."""
    console.print("-" * 60)
    console.print("To write your code:")
    console.print("  1. open_editor()   # Opens editor with template")
    console.print("  2. Write your code and save")
    console.print("  3. submit_code()   # Evaluates your code")
    console.print("-" * 60)
    console.print()


def display_feedback(feedback: str) -> None:
    """Display feedback in a panel."""
    console.print(Panel(feedback, title="FEEDBACK", width=60))
    console.print()


def display_retry_instructions() -> None:
    """Display retry steps after incorrect submission."""
    console.print("Try again!")
    console.print("  1. open_editor()  # Edit your code")
    console.print("  2. submit_code()  # Resubmit")
    console.print()


def truncate_description(desc: str, max_len: int = 45) -> str:
    """Truncate a description for table display."""
    if not desc:
        return ""
    if len(desc) > max_len:
        desc = desc[: max_len - 3] + "..."
    return f"  - {desc}"


def display_lesson_table(lessons: list[dict]) -> None:
    """Display lessons grouped by package in a table."""
    if not lessons:
        console.print("No lessons found.")
        return

    packages: dict[str, list[dict]] = {}
    for lesson in lessons:
        pkg = lesson["package"]
        packages.setdefault(pkg, []).append(lesson)

    table = Table(show_header=True, header_style="bold", width=60)
    table.add_column("Lesson", style="cyan")
    table.add_column("Description")

    for pkg, pkg_lessons in packages.items():
        table.add_row(f"[bold]-- {pkg} --[/bold]", "")
        for les in pkg_lessons:
            desc = truncate_description(les.get("description", ""))
            table.add_row(f"  {les['lesson_id']}", desc)

    console.print()
    console.print(table)
    console.print()
