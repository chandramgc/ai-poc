# Modern Python Features Reference (3.10+)

This reference details modern Python language features introduced in Python 3.10, 3.11, and 3.12+ that enable cleaner, more expressive, and more performant code.

---

## 1. Structural Pattern Matching (3.10+)

### Basic match/case Syntax

```python
def handle_command(command: str) -> str:
    match command.split():
        case ["quit"]:
            return "Exiting application"
        case ["hello", name]:
            return f"Hello, {name}!"
        case ["move", direction, distance]:
            return f"Moving {direction} by {distance}"
        case _:
            return "Unknown command"
```

### Class Patterns

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Circle:
    center: Point
    radius: float

@dataclass
class Rectangle:
    corner: Point
    width: float
    height: float

def describe_shape(shape) -> str:
    match shape:
        case Circle(center=Point(x=0, y=0), radius=r):
            return f"Circle at origin with radius {r}"
        case Circle(radius=r) if r > 100:
            return f"Large circle with radius {r}"
        case Rectangle(width=w, height=h) if w == h:
            return f"Square with side {w}"
        case Rectangle(width=w, height=h):
            return f"Rectangle {w}×{h}"
        case _:
            return "Unknown shape"
```

### OR Patterns and Guards

```python
def classify_status(status: int) -> str:
    match status:
        case 200 | 201 | 204:
            return "success"
        case 301 | 302:
            return "redirect"
        case 400 | 422:
            return "client_error"
        case 401 | 403:
            return "auth_error"
        case 500 | 502 | 503 if is_retryable():
            return "retryable_server_error"
        case 500 | 502 | 503:
            return "server_error"
        case _:
            return "unknown"
```

### API Routing / State Machine Example

```python
def handle_event(event: dict) -> None:
    match event:
        case {"type": "user.created", "data": {"email": email}}:
            send_welcome_email(email)
        case {"type": "order.placed", "data": {"id": order_id, "total": total}} if total > 1000:
            flag_for_review(order_id)
        case {"type": "order.placed", "data": {"id": order_id}}:
            process_order(order_id)
        case {"type": str(event_type)}:
            log.warning("unhandled_event", event_type=event_type)
```

---

## 2. ExceptionGroups (3.11+)

### Basic ExceptionGroup

```python
# Raise multiple exceptions at once
def validate_form(data: dict) -> None:
    errors = []
    if not data.get("name"):
        errors.append(ValueError("Name is required"))
    if not data.get("email"):
        errors.append(ValueError("Email is required"))
    if data.get("age", 0) < 0:
        errors.append(ValueError("Age must be non-negative"))

    if errors:
        raise ExceptionGroup("Validation failed", errors)
```

### except* Syntax

```python
try:
    validate_form({"name": "", "email": "", "age": -1})
except* ValueError as eg:
    # eg is an ExceptionGroup containing only ValueError instances
    for error in eg.exceptions:
        print(f"Validation error: {error}")
except* TypeError as eg:
    # Handle TypeError instances separately
    for error in eg.exceptions:
        print(f"Type error: {error}")
```

### Use Case: Concurrent Task Errors

```python
import asyncio

async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs, collecting all errors."""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    # If any task fails, TaskGroup raises ExceptionGroup
    return [t.result() for t in tasks]

async def main():
    try:
        results = await fetch_all(["https://a.com", "https://b.com"])
    except* ConnectionError as eg:
        print(f"{len(eg.exceptions)} connections failed")
    except* TimeoutError as eg:
        print(f"{len(eg.exceptions)} requests timed out")
```

---

## 3. Type Parameter Syntax (3.12+)

### Generic Functions

```python
# 3.12+ syntax — no TypeVar import needed
def first[T](items: list[T]) -> T:
    return items[0]

def merge[K, V](d1: dict[K, V], d2: dict[K, V]) -> dict[K, V]:
    return {**d1, **d2}
```

### Generic Classes

```python
# 3.12+ syntax
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T:
        return self._items[-1]

# Pre-3.12 equivalent
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    ...
```

### ParamSpec and TypeVarTuple

```python
from typing import ParamSpec, TypeVarTuple

# ParamSpec — capture callable signatures for decorators
def retry[**P, R](func: Callable[P, R], retries: int = 3) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception:
                if attempt == retries - 1:
                    raise
    return wrapper

# TypeVarTuple — variadic generics
def zip_strict[*Ts](*iterables: *Ts) -> Iterator[tuple[*Ts]]:
    ...
```

---

## 4. Modern Typing Patterns

### type Statement (3.12+)

```python
# 3.12+ — cleaner type alias syntax
type Vector = list[float]
type Matrix = list[Vector]
type UserID = int
type Callback[T] = Callable[[T], None]

# Pre-3.12 equivalent
from typing import TypeAlias
Vector: TypeAlias = list[float]
```

### Self Type

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self._name: str = ""
        self._value: int = 0

    def with_name(self, name: str) -> Self:
        self._name = name
        return self  # ✅ Returns Self, not Builder — works with subclasses

    def with_value(self, value: int) -> Self:
        self._value = value
        return self

# Enables fluent chaining:
result = Builder().with_name("test").with_value(42)
```

### Never Type

```python
from typing import Never

def raise_error(msg: str) -> Never:
    """Function that never returns normally."""
    raise RuntimeError(msg)

def unreachable() -> Never:
    """Marks code paths that should be unreachable."""
    raise AssertionError("This code should never execute")
```

### TypeGuard for Type Narrowing

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    """Narrow type from list[object] to list[str]."""
    return all(isinstance(item, str) for item in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # Type checker knows items is list[str] here
        print(", ".join(items))
```

### Unpack for Typed **kwargs

```python
from typing import Unpack, TypedDict

class RequestOptions(TypedDict, total=False):
    timeout: float
    retries: int
    headers: dict[str, str]

def make_request(url: str, **kwargs: Unpack[RequestOptions]) -> dict:
    timeout = kwargs.get("timeout", 30.0)
    retries = kwargs.get("retries", 3)
    ...
```

---

## 5. f-string Improvements (3.12+)

### Nested f-strings

```python
# 3.12+ allows arbitrary nesting — no escaping needed
matrix = [[1, 2], [3, 4]]
display = f"Matrix: {'\n'.join(f'  Row: {", ".join(str(x) for x in row)}' for row in matrix)}"
```

### Multi-line Expressions

```python
# 3.12+ allows multi-line f-string expressions
message = f"Result: {
    some_long_function_call(
        argument_one,
        argument_two,
    )
}"
```

### Backslash in f-strings

```python
# 3.12+ allows backslashes inside f-string expressions
items = ["a", "b", "c"]
result = f"Items: {'\n'.join(items)}"  # Was a SyntaxError before 3.12
```

---

## 6. Performance Features

### Faster CPython (3.11+)

Python 3.11 introduced significant performance improvements:
- **10–60% faster** than Python 3.10 for most workloads
- Specialized adaptive interpreter
- Zero-cost exception handling (no overhead when exceptions aren't raised)
- Faster startup time

### Per-interpreter GIL (3.12+)

```python
# 3.12+ — each sub-interpreter can have its own GIL
# Enables true parallelism for CPU-bound Python code
# Currently accessible via C API; Python API is evolving
```

### When to Use Each Concurrency Model

| Model | Best For | GIL Impact |
|:---|:---|:---|
| `asyncio` | I/O-bound (HTTP, DB, files) | N/A — cooperative, single-threaded |
| `threading` | I/O-bound with blocking libraries | Released during I/O waits |
| `multiprocessing` | CPU-bound (data processing, ML) | Bypassed — separate processes |
| Sub-interpreters (3.12+) | CPU-bound with shared memory | Per-interpreter GIL |

```python
# asyncio — best for I/O-bound
async def fetch_all(urls: list[str]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        return await asyncio.gather(*tasks)

# multiprocessing — best for CPU-bound
from concurrent.futures import ProcessPoolExecutor

def compute_heavy(data: list[float]) -> list[float]:
    with ProcessPoolExecutor() as pool:
        return list(pool.map(expensive_calculation, data))
```
