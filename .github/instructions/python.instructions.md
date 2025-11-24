---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions

## 🧠 Context

- **Project Type**: Web API / Data Pipeline / CLI Tool / ML App
- **Language**: Python
- **Framework / Libraries**: FastAPI / Flask / Django / Pandas / Pydantic / Poetry
- **Architecture**: MVC / Clean Architecture / Event-Driven / Microservices

## Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.
- Use poetry for dependency management.

## General Instructions

- Always prioritize readability and clarity.¬¬l
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.
- Avoid unused imports.
- Except Readme.md other documentation files should be created under docs/ folder.

## Code Style and Formatting

- Use Pythonic patterns (PEP8, PEP257).
- Prefer named functions and class-based structures over inline lambdas.
- Use type hints where applicable (`typing` module).
- Follow black or isort for formatting and import order.
- Use meaningful naming; avoid cryptic variables.
- Emphasize simplicity, readability, and DRY principles.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 79 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.
- Use is or is not for comparisons to None, not ==.

## Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.

## Example of Proper Documentation

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.
    
    Parameters:
    radius (float): The radius of the circle.
    
    Returns:
    float: The area of the circle, calculated as π * radius^2.
    """
    import math
    return math.pi * radius ** 2
```

## 📁 File Structure

Use this structure as a guide when creating or updating files:

```text
src/
  controllers/
  services/
  repositories/
  schemas/
  utils/
  config/
tests/
  unit/
  integration/
```

## 🧶 Patterns

### ✅ Patterns to Follow

- Use the Repository Pattern and Dependency Injection (e.g., via `Depends` in FastAPI).
- Validate data using Pydantic models.
- Use custom exceptions and centralized error handling.
- Use environment variables via `dotenv` or `os.environ`.
- Use logging via the `logging` module or structlog.
- Write modular, reusable code organized by concerns (e.g., controller, service, data layer).
- Favor async endpoints for I/O-bound services (FastAPI, aiohttp).
- Document functions and classes with docstrings.

### 🚫 Patterns to Avoid

- Don’t use wildcard imports (`from module import *`).
- Avoid global state unless encapsulated in a singleton or config manager.
- Don’t hardcode secrets or config values—use `.env`.
- Don’t expose internal stack traces in production environments.
- Avoid business logic inside views/routes.

### API

- Implement API rate limiting base on host ip and any uniqe_id (example client_id or any id).
- Authentication API (API Keys, OAuth 2.0 or Bearer Tokens).
- Enable Documentation and Data validation for request and response.

### Configuration

- Auto-load environment variables from a `.env` file using `python-dotenv` before loading other config.
- Load `config.yaml` into a dict.
- Merge values so that any key present in both `.env` and `config.yaml` uses the `.env` value (i.e., `.env` overrides).
- Convert `.env` string values to appropriate types based on the YAML type when possible (int, float, bool, JSON arrays/objects).
- Provide clear validation: accept a list of required keys and raise a descriptive error if missing after merge.
- Return a single merged config object (dict) into singleton `load_config(config_path="config.yaml", env_path=".env", required_keys=[])`.
- Include unit tests demonstrating overrides, type conversion, and missing-key errors.
- Provide example files and expected merged output.

Example inputs:

.env
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
FEATURE_FLAG=true
API_KEYS='["k1","k2"]'

config.yaml
DATABASE:
  HOST: ${DATABASE_HOST}
  PORT: ${DATABASE_PORT}
FEATURE_FLAG: false
TIMEOUT: 30

Expected merged result (types preserved):
{
  "DATABASE": {"HOST": "db.example.com", "PORT": 5432},
  "FEATURE_FLAG": false,
  "TIMEOUT": 30
}

## 🧪 Testing Guidelines

- Use `pytest` for unit and integration tests.
- Mock external services with `pytest-mock`.
- Use fixtures to set up and tear down test data.
- Aim for high coverage on core logic and low-level utilities.
- Test both happy paths and edge cases.

## 🧩 Example Prompts

- `Copilot, create a FastAPI endpoint that returns all users from the database.`
- `Copilot, write a Pydantic model for a product with id, name, and optional price.`
- `Copilot, implement a CLI command that uploads a CSV file and logs a summary.`
- `Copilot, write a pytest test for the transform_data function using a mock input.`

## 🔁 Iteration & Review

- Review Copilot output before committing.
- Add comments to clarify intent if Copilot generates incorrect or unclear suggestions.
- Use linters (flake8, pylint) and formatters (black, isort) as part of the review pipeline.
- Refactor output to follow project conventions.


## 📚 References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Django Documentation](https://docs.djangoproject.com/en/stable/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/en/stable/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Poetry](https://python-poetry.org/docs/)
