# Python Single-Line Programming Reference Guide

This reference details techniques and templates for writing concise, expressive, and memory-efficient Python single-line code blocks.

---

## 1. List, Set, and Dictionary Comprehensions

Comprehensions provide a concise way to create lists, sets, and dictionaries instead of writing full `for` loops.

### List Comprehensions
```python
# Multi-line loop:
squares = []
for x in range(10):
    squares.append(x**2)

#  Single-line comprehension:
squares = [x**2 for x in range(10)]
```

### With Conditional Filtering
```python
# Get even squares:
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

### Dictionary Comprehensions
```python
# Map user name to length:
user_lengths = {user.name: len(user.name) for user in users if user.is_active}
```

---

## 2. Conditional Expressions (Ternary Operator)

Use conditional expressions for quick variable assignment based on a condition instead of standard `if-else` blocks.

```python
# Multi-line:
if age >= 18:
    status = "adult"
else:
    status = "minor"

#  Single-line:
status = "adult" if age >= 18 else "minor"
```

---

## 3. Lambda Expressions & Higher-Order Functions

Use lambdas for small, throwaway anonymous functions inside operations like `map()`, `filter()`, or `sorted()`.

```python
# Sorting a list of dicts by a key:
records = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 20}]

# Sort in a single line:
sorted_records = sorted(records, key=lambda x: x["age"])
```

---

## 4. Built-in Collection Aggregations

Use built-in aggregation functions (`any()`, `all()`, `sum()`, `zip()`, `enumerate()`) to perform bulk evaluations in a single line.

```python
# Check if any user is an admin:
has_admin = any(user.is_admin for user in users)

# Check if all processes are running:
all_running = all(p.status == "RUNNING" for p in processes)

# Zip lists to dict:
keys = ["a", "b", "c"]
values = [1, 2, 3]
mapped = dict(zip(keys, values))
```

---

## 5. Generator Expressions

For large datasets, use generator expressions (using parentheses `(...)` instead of brackets `[...]`) to stream items on-demand, saving RAM.

```python
# Stream sum of line lengths in a file without loading all lines:
total_chars = sum(len(line) for line in open("file.txt"))
```

---

## 6. Expression Unpacking and Destructuring

Use multiple assignment and unpacking to swap or assign variables in a single line.

```python
# Swapping variables:
a, b = b, a

# Unpacking list items:
first, *middle, last = [1, 2, 3, 4, 5]
```
