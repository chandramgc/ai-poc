.PHONY: install run test lint format build-docker run-docker clean help

# Variables
PYTHON := poetry run python
PYTEST := poetry run pytest
RUFF := poetry run ruff
BLACK := poetry run black
UVICORN := poetry run uvicorn

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

install-dev: ## Install all dependencies including dev
	poetry install --with dev,test

run: ## Run the application locally
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests with coverage
	$(PYTEST) tests/ -v --cov=app --cov-report=term-missing --cov-report=html

test-quick: ## Run tests without coverage
	$(PYTEST) tests/ -v

lint: ## Run linter (ruff)
	$(RUFF) check app tests

lint-fix: ## Run linter and fix issues
	$(RUFF) check --fix app tests

format: ## Format code with black
	$(BLACK) app tests

format-check: ## Check code formatting
	$(BLACK) --check app tests

type-check: ## Run type checking with mypy
	poetry run mypy app

check-all: format lint type-check test ## Run all checks

build-docker: ## Build Docker image
	docker build -t llm-fastapi-service:latest .

run-docker: ## Run Docker container
	docker run -p 8000:8000 \
		--env-file .env \
		-v $(PWD)/config.yml:/app/config.yml \
		llm-fastapi-service:latest

stop-docker: ## Stop running Docker container
	docker stop $$(docker ps -q --filter ancestor=llm-fastapi-service:latest)

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage

poetry-lock: ## Update poetry.lock file
	poetry lock --no-update

poetry-update: ## Update all dependencies
	poetry update

shell: ## Open Poetry shell
	poetry shell

logs: ## Show Docker container logs
	docker logs $$(docker ps -q --filter ancestor=llm-fastapi-service:latest) -f
