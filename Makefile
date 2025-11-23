.PHONY: install install-scrapy install-playwright install-all run dev test test-cov clean docker-build docker-run docker-stop help

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies with Poetry (default: bs4 backend)
	poetry install

install-scrapy: ## Install dependencies with Scrapy backend
	poetry install --extras scrapy

install-playwright: ## Install dependencies with Playwright backend
	poetry install --extras playwright
	poetry run playwright install chromium

install-all: ## Install all dependencies including extras
	poetry install --extras all
	poetry run playwright install chromium

run: ## Run the FastAPI application
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001

dev: ## Run the FastAPI application in development mode with auto-reload
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

test: ## Run tests
	poetry run pytest -v

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	poetry run ptw

clean: ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache htmlcov .coverage

lint: ## Run linting (if ruff is installed)
	poetry run ruff check app tests || echo "Install ruff for linting: poetry add --group dev ruff"

format: ## Format code (if black is installed)
	poetry run black app tests || echo "Install black for formatting: poetry add --group dev black"

docker-build: ## Build Docker image
	docker build -t medicine-news-scraper:latest .

docker-build-scrapy: ## Build Docker image with Scrapy backend
	docker build --build-arg SCRAPER_BACKEND=scrapy -t medicine-news-scraper:scrapy .

docker-build-playwright: ## Build Docker image with Playwright backend
	docker build --build-arg SCRAPER_BACKEND=playwright -t medicine-news-scraper:playwright .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --name medicine-news-scraper medicine-news-scraper:latest

docker-stop: ## Stop and remove Docker container
	docker stop medicine-news-scraper || true
	docker rm medicine-news-scraper || true

docker-compose-up: ## Start services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	docker-compose down

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

shell: ## Open Poetry shell
	poetry shell

search: ## Test search endpoint (requires running server)
	curl "http://localhost:8001/api/v1/search?q=Insulin&limit=5" | python -m json.tool

health: ## Test health endpoint (requires running server)
	curl http://localhost:8001/api/v1/health | python -m json.tool
