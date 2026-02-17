# blendtutor

A framework for creating interactive Python coding lessons with AI-powered feedback -- like [learnr](https://rstudio.github.io/learnr/) for Python, but for the console with LLM evaluation.

# IMPORTANT NOTE

This package is under active development and breaking changes are likely.

THis Python package is based on the [{blendtutor}](https://github.com/mcmullarkey/blendtutor) R package. While current features should be at parity this Python version has not been tested as extensively. There may be unexpected bugs not present in the R package.

## What is blendtutor?

**blendtutor** lets educators build lesson packages that give students instant, personalized feedback on coding exercises. You write lesson YAML files describing the exercise and how to grade it, and blendtutor handles the interactive session + AI evaluation via [Fireworks AI](https://fireworks.ai).

Inspired by [swirl](https://swirlstats.com/) and originally designed to complement the [Just Enough Software Engineering](https://mcmullarkey.github.io/just-enough-software-engineering/) textbook.

## Installation

```bash
uv add blendtutor
```

Or from a local clone:

```bash
git clone https://github.com/mcmullarkey/blendtutor-py.git
cd blendtutor-py
uv pip install -e .
```

## Prerequisites

AI evaluation requires a Fireworks API key:

1. Sign up at [fireworks.ai](https://fireworks.ai)
2. Get your key from [fireworks.ai/api-keys](https://fireworks.ai/api-keys)
3. Add to your environment:
   ```bash
   export FIREWORKS_API_KEY=fw_...
   ```
   Or add it to a `.env` file.

## Creating a lesson package

The main use case is scaffolding your own package of lessons:

```python
from blendtutor import create_lesson_package

create_lesson_package("~/my-lessons", lesson_name="pseudocode_planning")
```

This creates a Python package with:

```
my_lessons/
  pyproject.toml            # blendtutor in dependencies
  src/my_lessons/
    lessons/                # Lesson YAML files
  evals/                    # Eval scripts for testing grading accuracy
  .claude/skills/           # Claude Code skill for guided lesson authoring
  README.md                 # Step-by-step walkthrough
```

### Writing lessons

Lessons are YAML files in `src/<pkg>/lessons/`. The key fields:

```yaml
lesson_name: "Writing Pseudocode"
description: "Practice translating requirements into pseudocode"

exercise:
  prompt: |
    Write pseudocode for a function that finds the maximum value in a list.
  llm_evaluation_prompt: |
    You are evaluating student code for a software engineering course.
    Exercise: Write pseudocode for finding the max value in a list.

    Student submitted:
    {student_code}

    Evaluate and call respond_with_feedback with your assessment.
```

The `{student_code}` placeholder is required -- blendtutor inserts the student's submission before sending to the LLM.

### Adding more lessons to an existing package

```python
from blendtutor import use_blendtutor_lesson, use_blendtutor_evals

use_blendtutor_lesson("loop_basics")
use_blendtutor_evals("loop_basics")
```

### Validating and testing

```python
from blendtutor import validate_lesson

# Check a lesson for required fields and common issues
validate_lesson("src/my_lessons/lessons/pseudocode_planning.yaml")
```

```bash
# Run evals to test your grading prompt against known submissions
deepeval test run evals/eval_pseudocode_planning.py
```

### Installing your lesson package

```bash
uv pip install -e .
```

```python
from blendtutor import invalidate_lesson_cache, list_lessons
invalidate_lesson_cache()
list_lessons()
```

If you push to GitHub, students can install your package and all its lessons appear alongside any others.

## Student workflow

Once a lesson package is installed, students interact with it in Python:

```python
from blendtutor import list_lessons, start_lesson, open_editor, submit_code

list_lessons()                       # See available lessons across all packages
start_lesson("pseudocode_planning")  # Start a lesson

open_editor()                        # Opens editor with template
# Write code, save, close
submit_code()                        # Get AI feedback

# Iterate: open_editor() -> edit -> submit_code()
```

Code persists between submissions -- students refine based on feedback rather than starting over.

### Example session

blendtutor ships with a built-in example lesson:

```python
>>> from blendtutor import start_lesson, submit_code
>>> start_lesson("add_two_numbers")

╭─── Blendtutor: Interactive Coding Lessons ───╮
│ Lesson: Writing Your First Function          │
│ Reference: Just Enough Software Engineering  │
╰──────────────────────────────────────────────╯

Write a function called 'add_two' that takes two numeric
arguments (x and y) and returns their sum.

>>> submit_code("def add_two(x, y):\n    return x + y")

Evaluating your code with AI...

╭──── FEEDBACK ────╮
│ Excellent work!  │
╰──────────────────╯

Congratulations! Lesson complete!
```

## API reference

### Educator functions

| Function | Description |
|---|---|
| `create_lesson_package(path)` | Scaffold a new lesson package |
| `use_blendtutor_lesson(name)` | Add a lesson YAML template |
| `use_blendtutor_evals(name)` | Add an eval script template |
| `validate_lesson(path)` | Check a lesson YAML for issues |

### Student functions

| Function | Description |
|---|---|
| `list_lessons()` | Show all available lessons |
| `start_lesson(name)` | Begin a lesson |
| `open_editor()` | Open code in your editor |
| `submit_code()` | Submit for AI evaluation |
| `reset_lesson()` | Clear current lesson state |

### Discovery

| Function | Description |
|---|---|
| `invalidate_lesson_cache()` | Clear cached lesson index |

## Cross-package discovery

blendtutor automatically discovers lessons from any installed package that registers a `blendtutor.lessons` entry point and has YAML files in its `lessons/` directory. Students see all lessons from all packages in a single `list_lessons()` call. Use `invalidate_lesson_cache()` after installing or removing lesson packages.

Entry point convention for lesson packages:

```toml
[project.entry-points."blendtutor.lessons"]
my_package = "my_package"
```

## Related projects

- [learnr](https://rstudio.github.io/learnr/) -- Interactive tutorials with Shiny
- [swirl](https://swirlstats.com/) -- Console-based interactive R learning
- [blendtutor (R)](https://github.com/mcmullarkey/blendtutor) -- The original R version
- [Fireworks AI](https://fireworks.ai) -- Fast inference API
- [Just Enough Software Engineering](https://mcmullarkey.github.io/just-enough-software-engineering/) -- Companion textbook

## License

MIT License -- see LICENSE file for details.
