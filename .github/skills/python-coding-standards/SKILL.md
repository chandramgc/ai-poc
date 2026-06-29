---
name: python-coding-standards
description: >
  Main entry point for Python PEP 8 coding standards and Python single-line programming best practices.
  Trigger this skill automatically whenever a user asks to review Python design, check PEP 8 compliance,
  write clean Python scripts, or utilize single-line programming constructs like list comprehensions.
---

# Python Coding Standards & PEP 8 Rules

This skill enforces strict Python best practices, formatting structures according to the official PEP 8 style guide, and guides clean, readable, and simplified coding patterns.

---

## 🧭 References Roadmap

To write compliant Python code, consult these dedicated reference files:

- 🎨 **[PEP 8 Style Rules](references/python-pep8-rules.md):** Complete formatting rules covering class naming, camelCase vs snake_case, indentation spacing, import layouts, and docstrings.
- ⚡ **[Python Single-Line Coding Examples](references/python-oneliners.md):** Practical code templates and guide checklists for writing expression-based single-line Python blocks (list/dict comprehensions, lambdas, conditional expressions, ternary operators, zip/map/filter, and generators).

---

## 🐍 Core Principles

1. **Explicit is better than implicit:** Keep code blocks readable and explicit. Avoid obscure hacks unless they significantly simplify execution without sacrificing clarity.
2. **Simple is better than complex:** Leverage Python's rich built-in functions (`any()`, `all()`, `zip()`, `enumerate()`, `sum()`) before writing custom nested iterations.
3. **Follow the Simplicity Ladder (Ponytail):** Write minimal changes. If a clean, Pythonic one-liner solves the problem, use it. Otherwise, write the absolute minimum necessary lines of code.
4. **Use Type Hints:** Always include type annotations in function signatures to catch typing errors early:
   ```python
   def process_data(records: list[str]) -> dict[str, int]:
       return {record: len(record) for record in records}
   ```
