# Python Security & Bandit SAST Reference Guide

This reference details security-focused rules, input validation techniques, and secure coding patterns for Python applications.

---

## 1. Bandit Rule Categories

Bandit is a tool designed to find common security issues in Python code. The table below lists the most critical rules to enforce.

| Rule ID | Severity | Description |
|:---|:---|:---|
| **B101** | Low | `assert_used` — Don't use `assert` for security checks; assertions are stripped in optimized mode (`-O`). |
| **B102** | High | `exec_used` — Never use `exec()`; it executes arbitrary code strings. |
| **B103** | Medium | `set_bad_file_permissions` — Use restrictive file permissions (e.g., `0o600` not `0o777`). |
| **B104** | Medium | `hardcoded_bind_all_interfaces` — Don't bind to `0.0.0.0` by default; bind to specific interfaces. |
| **B105–B107** | High | `hardcoded_password` / `hardcoded_password_funcarg` / `hardcoded_password_default` — Never hardcode passwords or API keys; use environment variables or secret managers. |
| **B108** | Medium | `hardcoded_tmp_directory` — Don't hardcode `/tmp`; use the `tempfile` module for safe temp file handling. |
| **B110** | Low | `try_except_pass` — Don't silently swallow exceptions with bare `except: pass`. |
| **B301–B303** | High | `pickle` / `marshal` / `md5` — Never unpickle untrusted data; avoid weak hashes for security. |
| **B501–B503** | High | `request_with_no_cert_validation` / `ssl_with_bad_version` / `ssl_with_bad_defaults` — Never disable certificate verification or use deprecated TLS versions. |
| **B601–B607** | High | `paramiko_calls` / `start_process_with_shell` / `subprocess_popen` — Use `subprocess` with `shell=False` and pass arguments as a list. |
| **B608** | High | `hardcoded_sql_expressions` — Use parameterized queries; never interpolate user input into SQL strings. |

---

## 2. Input Validation with Pydantic

Use Pydantic models to validate and sanitize all external input at application boundaries.

### Basic Model with Constraints

```python
from pydantic import BaseModel, Field, field_validator


class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: str = Field(max_length=254)
    age: int = Field(gt=0, lt=150)
    role: str = Field(default="viewer")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"viewer", "editor", "admin"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v
```

### Strict Mode (Prevent Type Coercion)

```python
from pydantic import BaseModel, ConfigDict


class StrictInput(BaseModel):
    model_config = ConfigDict(strict=True)

    count: int    # Rejects "5" (string) — only accepts int
    flag: bool    # Rejects 1 (int) — only accepts bool
```

---

## 3. Secure Coding Patterns

### Secret Management

```python
# ✅ Use python-dotenv for local development
from dotenv import load_dotenv
import os

load_dotenv()
db_password = os.environ["DB_PASSWORD"]  # Fails loudly if missing

# ❌ NEVER hardcode secrets
db_password = "super_secret_123"  # B105 violation
```

### Password Hashing

```python
# ✅ Use bcrypt or argon2 — never store plaintext passwords
import bcrypt

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12))

def verify_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)
```

### JWT Validation

```python
import jwt

def decode_token(token: str, public_key: str) -> dict:
    """Decode and validate a JWT token with strict algorithm enforcement."""
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],         # ✅ Explicitly whitelist algorithms
        options={"require": ["exp", "iss", "sub"]},
    )
```

### CORS Configuration (FastAPI)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # ✅ Explicit origins
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
    allow_credentials=True,
)
# ❌ NEVER use allow_origins=["*"] with allow_credentials=True
```

### Rate Limiting (FastAPI)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    ...
```

---

## 4. SAST Integration

### Bandit Configuration (`.bandit.yml`)

```yaml
# .bandit.yml
skips: []
tests:
  - B101
  - B102
  - B103
  - B104
  - B105
  - B106
  - B107
  - B108
  - B110
  - B301
  - B302
  - B303
  - B501
  - B502
  - B503
  - B601
  - B602
  - B603
  - B604
  - B605
  - B606
  - B607
  - B608
exclude_dirs:
  - tests
  - .venv
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        args: ["-c", ".bandit.yml", "-r", "."]
        exclude: ^tests/
```

### CI Pipeline Integration

```yaml
# GitHub Actions step
- name: Run Bandit SAST
  run: |
    pip install bandit
    bandit -c .bandit.yml -r src/ -f json -o bandit-report.json || true
    bandit -c .bandit.yml -r src/ -f screen
```

### Suppressing False Positives

```python
# Use #nosec ONLY with justification
password_hash = hashlib.sha256(data).hexdigest()  # nosec B303 — not used for security, only content hashing
```
