# Medicine News Scraper

A FastAPI-based web scraper service that fetches the latest medicine-related news from Google search results. Supports multiple scraping backends (BeautifulSoup, Scrapy, Playwright) with configurable rate limiting, caching, and error handling.

## Features

- 🔍 **Flexible Search**: Query Google News for medicine-related keywords
- 🚀 **FastAPI Backend**: Modern, async web framework with automatic API docs
- 🔄 **Multiple Scraper Backends**: Choose between BeautifulSoup (default), Scrapy, or Playwright
- 💾 **Smart Caching**: In-memory TTL cache to reduce requests
- ⚙️ **Configurable**: Environment-based configuration for all settings
- 🛡️ **Error Handling**: Exponential backoff, rate limit detection, and clear error messages
- 🧪 **Tested**: Comprehensive unit tests with mocked responses
- 🐳 **Docker Ready**: Multi-stage Dockerfile for production deployment

## Quick Start

### Prerequisites

- Python 3.9+
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone or create the project directory**:
```bash
cd medicine-news-scraper
```

2. **Install dependencies with Poetry**:
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies (default: bs4 backend)
poetry install

# For Scrapy backend (optional):
poetry install --extras scrapy

# For Playwright backend (optional):
poetry install --extras playwright
# Note: Playwright requires additional browser installation
poetry run playwright install chromium
```

3. **Configure environment variables** (optional):

Create a `.env` file in the project root:
```env
# Application settings
DEBUG=false
MAX_RESULTS=10

# Scraper backend: bs4 (default), scrapy, or playwright
SCRAPER_BACKEND=bs4

# Request settings
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
REQUEST_TIMEOUT=10
REQUEST_DELAY=1.0

# Cache settings
CACHE_TTL=3600
CACHE_MAX_SIZE=100

# Retry settings
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0
```

### Running the Service

#### With Poetry (Development)

```bash
# Run with Poetry
poetry run uvicorn app.main:app --reload

# Or activate the virtual environment first
poetry shell
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### With Docker

```bash
# Build the Docker image (default: bs4 backend)
docker build -t medicine-news-scraper .

# Build with Scrapy backend
docker build --build-arg SCRAPER_BACKEND=scrapy -t medicine-news-scraper:scrapy .

# Build with Playwright backend
docker build --build-arg SCRAPER_BACKEND=playwright -t medicine-news-scraper:playwright .

# Run the container
docker run -p 8000:8000 \
  -e SCRAPER_BACKEND=bs4 \
  -e REQUEST_DELAY=2.0 \
  medicine-news-scraper
```

#### With Docker Compose (recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      args:
        SCRAPER_BACKEND: bs4
    ports:
      - "8000:8000"
    environment:
      - SCRAPER_BACKEND=bs4
      - DEBUG=false
      - REQUEST_DELAY=2.0
      - CACHE_TTL=3600
    restart: unless-stopped
```

Run with:
```bash
docker-compose up
```

## API Usage

### Search for Medicine News

**Endpoint**: `GET /api/v1/search`

**Parameters**:
- `q` (required): Search query (e.g., "Insulin", "Metformin")
- `limit` (optional): Maximum results to return (default: 10, max: configured MAX_RESULTS)

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/search?q=Insulin&limit=5"
```

**Example Response**:
```json
{
  "query": "Insulin",
  "results": [
    {
      "title": "New Insulin Treatment Shows Promise",
      "url": "https://example.com/insulin-news",
      "snippet": "Researchers have developed a new insulin formulation...",
      "source": "Medical News Today",
      "published_date": "2 days ago"
    }
  ],
  "count": 5,
  "cached": false
}
```

### Health Check

**Endpoint**: `GET /api/v1/health`

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "backend": "bs4",
  "cache_size": 5
}
```

## Scraper Backends

The service supports three scraping backends, selected via the `SCRAPER_BACKEND` environment variable:

### 1. BeautifulSoup (bs4) - Default

**When to use**: Simple, static content scraping with minimal dependencies.

**Pros**:
- Lightweight and fast
- Easy to understand and debug
- Low memory footprint
- Works for most static search results

**Cons**:
- Cannot handle JavaScript-heavy pages
- May miss dynamically loaded content

**Installation**:
```bash
poetry install  # Included by default
```

### 2. Scrapy

**When to use**: High-throughput scraping, custom pipelines, or complex crawling logic.

**Pros**:
- Built for large-scale scraping
- Powerful pipeline system
- Excellent for multiple pages/sites
- Built-in rate limiting and middleware

**Cons**:
- Heavier dependency
- More complex setup
- Overkill for simple use cases

**Installation**:
```bash
poetry install --extras scrapy
```

**Note**: Scrapy backend implementation would require:
- Custom spider in `app/scraper/google_search_scrapy.py`
- Item pipeline for Article models
- Settings configuration

### 3. Playwright

**When to use**: JavaScript-heavy pages, interactive content, or when BeautifulSoup fails.

**Pros**:
- Executes JavaScript
- Handles dynamic content
- Better anti-bot evasion
- Can screenshot for debugging

**Cons**:
- Heavier (requires browser installation)
- Slower execution
- Higher resource usage

**Installation**:
```bash
poetry install --extras playwright
poetry run playwright install chromium
```

**Docker considerations**: Uncomment Playwright installation in Dockerfile when using this backend.

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_scraper.py -v

# Run tests with output
poetry run pytest -v -s
```

### Code Quality

```bash
# Format code (if you add black/ruff)
poetry run black app tests

# Lint code
poetry run ruff check app tests

# Type checking
poetry run mypy app
```

### Project Structure

```
medicine-news-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration and settings
│   │   └── cache.py            # TTL cache implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── article.py          # Pydantic models
│   └── scraper/
│       ├── __init__.py
│       └── google_search.py    # BeautifulSoup scraper
├── tests/
│   ├── __init__.py
│   └── test_scraper.py         # Unit tests
├── Dockerfile                  # Multi-stage Docker build
├── pyproject.toml              # Poetry dependencies
├── poetry.lock                 # Locked dependencies
└── README.md                   # This file
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug logging |
| `MAX_RESULTS` | `10` | Maximum search results |
| `USER_AGENT` | Mozilla/5.0... | HTTP User-Agent header |
| `REQUEST_TIMEOUT` | `10` | Request timeout (seconds) |
| `REQUEST_DELAY` | `1.0` | Delay between requests (seconds) |
| `SCRAPER_BACKEND` | `bs4` | Backend: bs4, scrapy, or playwright |
| `CACHE_TTL` | `3600` | Cache expiration (seconds) |
| `CACHE_MAX_SIZE` | `100` | Maximum cached items |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `RETRY_BACKOFF_FACTOR` | `2.0` | Exponential backoff multiplier |

## Legal and Ethical Considerations

⚠️ **IMPORTANT**: Please read and understand the following:

### Robots.txt and Terms of Service

- **Google's Terms**: This scraper may violate Google's Terms of Service. Use at your own risk.
- **robots.txt**: While this scraper respects rate limits, it does not automatically check robots.txt. You are responsible for compliance.
- **Rate Limiting**: The default `REQUEST_DELAY` of 1 second is a minimum. Consider increasing it to be more respectful.

### Responsible Use Guidelines

1. **Don't overwhelm servers**: Use appropriate delays between requests
2. **Respect rate limits**: If you receive 429 or 503 errors, back off significantly
3. **Use official APIs when available**: Consider Google Custom Search API or News API for production use
4. **Don't bypass anti-bot measures**: This scraper does not attempt to bypass CAPTCHAs or anti-bot systems
5. **Monitor your usage**: Keep logs and be prepared to stop if requested
6. **Consider alternatives**: For production, use official APIs or licensed data feeds

### Anti-Bot Detection

If Google detects unusual traffic:
- You may receive CAPTCHA challenges
- Your IP may be temporarily blocked
- The scraper will return a clear error message

**Mitigation strategies**:
- Increase `REQUEST_DELAY` (e.g., 5-10 seconds)
- Use rotating proxies (not implemented in this project)
- Switch to Playwright backend for better handling
- Consider using official APIs instead

### Alternative Data Sources

For production applications, consider:
- **Google Custom Search API**: Official, legal, with generous free tier
- **News API**: Aggregated news from multiple sources
- **PubMed API**: For medical/scientific articles
- **Licensed data feeds**: Commercial options with legal guarantees

## Troubleshooting

### Issue: Import errors for bs4

**Solution**: Install dependencies
```bash
poetry install
```

### Issue: "Rate limited by Google"

**Solutions**:
1. Increase `REQUEST_DELAY` in `.env`
2. Wait before retrying
3. Switch to Playwright backend
4. Consider using a proxy

### Issue: No results returned

**Causes**:
- Google HTML structure changed
- Blocked by anti-bot measures
- Network issues

**Solutions**:
1. Check logs for detailed errors
2. Verify internet connection
3. Try different search queries
4. Update parser selectors in `google_search.py`

### Issue: Docker build fails

**Solutions**:
```bash
# Clean build
docker build --no-cache -t medicine-news-scraper .

# Check build args
docker build --build-arg SCRAPER_BACKEND=bs4 -t medicine-news-scraper .
```

### Issue: Tests fail

**Solutions**:
```bash
# Install dev dependencies
poetry install --with dev

# Run tests with verbose output
poetry run pytest -v -s
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is provided for educational purposes only. Users are responsible for ensuring their use complies with all applicable laws, terms of service, and ethical guidelines. The authors assume no liability for misuse or legal consequences.

---

**Need help?** Open an issue or check the [FastAPI documentation](https://fastapi.tiangolo.com/) for framework-specific questions.