# Medicine News Scraper - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### Step 2: Run the Service

```bash
# Using Poetry
poetry run uvicorn app.main:app --reload

# Or using Make
make dev
```

### Step 3: Test the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

Or use curl:
```bash
# Search for Insulin news
curl "http://localhost:8000/api/v1/search?q=Insulin&limit=5"

# Or using Make
make search
```

## 📝 Example Usage

### Python Requests

```python
import requests

# Search for medicine news
response = requests.get(
    "http://localhost:8000/api/v1/search",
    params={"q": "Insulin", "limit": 5}
)

data = response.json()
for article in data["results"]:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Source: {article['source']}")
    print("---")
```

### JavaScript/Fetch

```javascript
// Search for medicine news
fetch('http://localhost:8000/api/v1/search?q=Insulin&limit=5')
  .then(response => response.json())
  .then(data => {
    data.results.forEach(article => {
      console.log(`Title: ${article.title}`);
      console.log(`URL: ${article.url}`);
      console.log(`Source: ${article.source}`);
      console.log('---');
    });
  });
```

## 🐳 Docker Quick Start

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🧪 Testing

```bash
# Run tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Or using Make
make test
make test-cov
```

## 🔧 Configuration

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` to customize:
- `SCRAPER_BACKEND`: bs4, scrapy, or playwright
- `REQUEST_DELAY`: Increase for more polite scraping
- `CACHE_TTL`: Cache duration in seconds

## 📚 Common Commands

Using Make (recommended):
```bash
make help              # Show all available commands
make install           # Install dependencies
make dev               # Run in development mode
make test              # Run tests
make docker-build      # Build Docker image
make docker-compose-up # Start with docker-compose
```

Using Poetry directly:
```bash
poetry install                                    # Install deps
poetry run uvicorn app.main:app --reload        # Run dev server
poetry run pytest                                 # Run tests
poetry shell                                      # Activate venv
```

## ⚠️ Important Notes

1. **Rate Limiting**: Be respectful of Google's servers. Increase `REQUEST_DELAY` if needed.
2. **Legal**: This may violate Google's ToS. Use at your own risk for educational purposes.
3. **Anti-Bot**: Google may block automated requests. Consider using official APIs for production.

## 🆘 Troubleshooting

### Port already in use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Import errors
```bash
# Reinstall dependencies
poetry install
```

### Docker issues
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📖 Full Documentation

See [README.md](README.md) for complete documentation including:
- Scraper backend options
- Configuration reference
- API documentation
- Legal considerations
- Contributing guidelines

---

**Happy scraping! 🔍**
