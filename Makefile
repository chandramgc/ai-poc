.PHONY: install run test lint typecheck format clean

install:
	poetry install

run:
	uvicorn app.main:app --reload

test:
	poetry run pytest tests/ -v --cov=app

lint:
	poetry run ruff check .
	poetry run ruff format --check .

format:
	poetry run ruff check --fix .
	poetry run ruff format .

typecheck:
	poetry run mypy app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .mypy_cache -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .ruff_cache -exec rm -r {} +