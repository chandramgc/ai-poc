# Multi-stage Dockerfile for Medicine News Scraper
# Optimized for production with Poetry dependency management

# Stage 1: Builder stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without dev dependencies)
# For default (bs4) backend, no extras needed
# For scrapy: poetry install --no-dev --extras scrapy
# For playwright: poetry install --no-dev --extras playwright
ARG SCRAPER_BACKEND=bs4
RUN if [ "$SCRAPER_BACKEND" = "scrapy" ]; then \
        poetry install --no-dev --extras scrapy; \
    elif [ "$SCRAPER_BACKEND" = "playwright" ]; then \
        poetry install --no-dev --extras playwright; \
    else \
        poetry install --no-dev; \
    fi

# Stage 2: Runtime stage
FROM python:3.11-slim as runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    SCRAPER_BACKEND=bs4

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app ./app

# If using Playwright backend, install browsers
# Uncomment the following lines if SCRAPER_BACKEND=playwright
# ARG SCRAPER_BACKEND=bs4
# RUN if [ "$SCRAPER_BACKEND" = "playwright" ]; then \
#         apt-get update && \
#         apt-get install -y wget gnupg && \
#         playwright install chromium && \
#         playwright install-deps chromium && \
#         rm -rf /var/lib/apt/lists/*; \
#     fi

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health', timeout=5)"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
