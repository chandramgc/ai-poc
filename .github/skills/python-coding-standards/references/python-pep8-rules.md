# Python PEP 8 Style Guide Reference

This guide summarizes formatting, naming, and layout standards based on the canonical **PEP 8** specification.

---

## 1. Naming Conventions

Follow these strict naming patterns for variables, functions, classes, and packages:

| Element | Case | Example |
|:---|:---|:---|
| **Packages / Modules** | Short, lowercase names (no underscores unless required) | `urllib`, `requests`, `utils` |
| **Classes** | CapWords / PascalCase | `UserRecord`, `DatabaseConnection` |
| **Exceptions** | CapWords ending with `Error` | `ConnectionTimeoutError` |
| **Functions / Methods** | lowercase_with_underscores (snake_case) | `calculate_total()`, `fetch_record()` |
| **Variables** | lowercase_with_underscores (snake_case) | `user_name`, `total_amount` |
| **Constants** | UPPERCASE_WITH_UNDERSCORES | `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT` |

---

## 2. Spacing, Indentation & Layout

### Indentation
- Always use **4 spaces** per indentation level. Never use tabs.

### Line Length
- Limit all lines to a maximum of **79 characters**.
- For docstrings or comments, limit lines to **72 characters**.

### Blank Lines
- Surround top-level function and class definitions with **two blank lines**.
- Surround method definitions inside a class with **a single blank line**.

### Source File Encoding
- Always use **UTF-8** encoding for Python source files.

---

## 3. Imports

### Layout
- Imports should always be written on separate lines at the top of the file:
```python
#  CORRECT
import os
import sys

# ❌ WRONG
import os, sys
```

- Group imports in the following order (separated by a blank line):
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library-specific imports

### Absolute vs Relative
- **Absolute imports** are highly recommended as they are more readable and behave better:
```python
#  CORRECT
from mypackage.utils import helper

# ❌ WRONG (unless package is local/internal)
from .utils import helper
```

---

## 4. Comments & Docstrings

- Write docstrings (`"""Docstring"""`) for all public modules, functions, classes, and methods.
- Write docstrings according to **PEP 257** conventions:
```python
def fetch_user(user_id: int) -> User:
    """Fetch user profile information from database.

    Args:
        user_id: Unique identifier for the user.

    Returns:
        User object containing active profile data.
    """
    ...
```
