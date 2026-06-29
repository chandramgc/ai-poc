# Python Testing Patterns Reference Guide

This reference details pytest best practices, fixture patterns, mocking strategies, coverage configuration, and test design patterns.

---

## 1. pytest Fundamentals

### Test Discovery Conventions

pytest automatically discovers tests using these naming patterns:

| Element | Convention |
|:---|:---|
| **Test files** | `test_*.py` or `*_test.py` |
| **Test classes** | `Test*` (no `__init__` method) |
| **Test functions** | `test_*` |

### Assert Patterns

```python
# ✅ Use plain assert — pytest rewrites them with rich diffs
def test_addition():
    assert 1 + 1 == 2
    assert "hello" in "hello world"
    assert len([1, 2, 3]) == 3

# ❌ Don't use unittest-style assertions
# self.assertEqual(1 + 1, 2)
```

### Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Fast, isolated tests
│   ├── test_models.py
│   └── test_utils.py
├── integration/         # Tests with external dependencies
│   ├── test_database.py
│   └── test_api.py
└── e2e/                 # End-to-end workflow tests
    └── test_workflows.py
```

---

## 2. Fixtures

### Scope Levels

```python
import pytest

@pytest.fixture(scope="function")   # Default — runs per test
def fresh_user():
    return User(name="test")

@pytest.fixture(scope="class")      # Shared across class
def db_session():
    session = create_session()
    yield session
    session.close()

@pytest.fixture(scope="module")     # Shared across module
def api_client():
    return TestClient(app)

@pytest.fixture(scope="session")    # Shared across entire test run
def database():
    db = setup_database()
    yield db
    teardown_database(db)
```

### Yield Fixtures (Setup / Teardown)

```python
@pytest.fixture
def temp_directory():
    """Create a temp directory, yield it, then clean up."""
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path)
```

### Fixture Composition

```python
@pytest.fixture
def db_connection(database):
    """Depends on the session-scoped 'database' fixture."""
    conn = database.connect()
    yield conn
    conn.rollback()
    conn.close()

@pytest.fixture
def populated_db(db_connection):
    """Depends on 'db_connection', which depends on 'database'."""
    db_connection.execute("INSERT INTO users VALUES ('alice')")
    return db_connection
```

### conftest.py Organization

```
tests/
├── conftest.py              # Global fixtures (db, client)
├── unit/
│   └── conftest.py          # Unit-specific fixtures (mocks)
└── integration/
    └── conftest.py          # Integration-specific fixtures (live db)
```

---

## 3. Parametrize

### Basic Parametrize

```python
import pytest

@pytest.mark.parametrize("input_val,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input_val: int, expected: int):
    assert input_val ** 2 == expected
```

### Multiple Parameter Sets with IDs

```python
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("invalid-email", False),
    ("", False),
    ("a@b.co", True),
], ids=["valid_email", "no_at_sign", "empty_string", "minimal_valid"])
def test_email_validation(email: str, is_valid: bool):
    assert validate_email(email) == is_valid
```

### Indirect Parametrize (Fixture Args)

```python
@pytest.fixture
def user(request):
    """Create user with role from parametrize."""
    return User(role=request.param)

@pytest.mark.parametrize("user", ["admin", "editor", "viewer"], indirect=True)
def test_user_permissions(user):
    assert user.role in {"admin", "editor", "viewer"}
```

---

## 4. Mocking

### Patching with pytest-mock

```python
def test_fetch_user(mocker):
    """Mock an external API call."""
    mock_get = mocker.patch("myapp.services.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}

    user = fetch_user(user_id=1)

    assert user["name"] == "Alice"
    mock_get.assert_called_once()
```

### MagicMock vs Mock vs AsyncMock

```python
from unittest.mock import MagicMock, Mock, AsyncMock

# MagicMock — supports magic methods (__len__, __iter__, etc.)
mock_list = MagicMock()
mock_list.__len__.return_value = 5

# Mock — basic mock without magic method support
mock_service = Mock()
mock_service.process.return_value = "done"

# AsyncMock — for async functions
mock_async = AsyncMock(return_value={"status": "ok"})
result = await mock_async()
```

### Side Effects

```python
def test_retry_logic(mocker):
    """Simulate transient failures then success."""
    mock_call = mocker.patch("myapp.client.api_call")
    mock_call.side_effect = [
        ConnectionError("timeout"),
        ConnectionError("timeout"),
        {"status": "ok"},
    ]

    result = resilient_api_call()
    assert result == {"status": "ok"}
    assert mock_call.call_count == 3
```

### Mocking Database Queries

```python
def test_get_active_users(mocker):
    mock_db = mocker.patch("myapp.repo.db_session")
    mock_db.query.return_value.filter.return_value.all.return_value = [
        User(id=1, name="Alice", active=True),
    ]

    users = get_active_users()
    assert len(users) == 1
    assert users[0].name == "Alice"
```

---

## 5. Coverage Configuration

### pytest-cov Setup

```ini
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
branch = true
source = ["src"]
omit = [
    "src/migrations/*",
    "src/config.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### CI Coverage Threshold

```yaml
# GitHub Actions step
- name: Run tests with coverage
  run: |
    pytest --cov=src --cov-fail-under=80
```

---

## 6. Async Testing

### pytest-asyncio Setup

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com/data")
    assert result["status"] == "ok"
```

### Async Fixtures

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
```

---

## 7. Test Patterns

### Arrange-Act-Assert (AAA)

```python
def test_discount_calculation():
    # Arrange
    cart = ShoppingCart()
    cart.add_item(Item("Widget", price=100))

    # Act
    cart.apply_discount(percent=10)

    # Assert
    assert cart.total == 90
```

### Testing Exceptions

```python
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        1 / 0

def test_invalid_user_raises():
    with pytest.raises(ValueError, match="Username.*required"):
        create_user(username="")
```

### Test Doubles Summary

| Double | Purpose | Example |
|:---|:---|:---|
| **Stub** | Returns predetermined values | `mock.return_value = 42` |
| **Mock** | Verifies interactions occurred | `mock.assert_called_once_with(...)` |
| **Fake** | Working implementation (e.g., in-memory DB) | `FakeRepository()` |
| **Spy** | Records calls while delegating to real code | `mocker.spy(obj, "method")` |
