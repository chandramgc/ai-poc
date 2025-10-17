# Relationship Finder MCP

A Model Communication Protocol (MCP) service to find relationships between people using FastAPI and LangGraph. The service provides both HTTP and WebSocket endpoints for relationship lookups with support for exact and fuzzy name matching.

## Features

- FastAPI HTTP + WebSocket endpoints
- LangGraph-based relationship lookup workflow
- Exact and fuzzy name matching with confidence scores
- Real-time streaming of workflow steps
- Excel-based data source with hot reload support
- Python and Node.js CLI clients
- Comprehensive test suite
- Docker support with optional Redis for workflow state

## Prerequisites

- Python 3.11+
- Node.js 20+ (for Node client)
- Docker & Docker Compose (optional)
- Poetry (recommended for Python dependency management)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/chandramgc/ai-poc.git
cd ai-poc
```

2. Install Python dependencies:

```bash
poetry install
```

3. Set up environment:

```bash
cp .env.example .env
```

## Running the Service

### Local Development

```bash
# Using Poetry
poetry run uvicorn app.main:app --reload

# Or using Make
make run
```

### Docker

```bash
docker compose up --build
```

The service will be available at:
- HTTP API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- WebSocket endpoint: ws://localhost:8000/relationship/stream

## Using the Clients

### Python Client

```bash
# HTTP request
poetry run python -m clients.python.cli --name "Saanvi"

# WebSocket streaming
poetry run python -m clients.python.cli --name "Saanvi" --stream
```

### Node.js Client

```bash
# Install dependencies
cd clients/node
npm install

# HTTP request
node cli.mjs --name "Saanvi"

# WebSocket streaming
node cli.mjs --name "Saanvi" --stream
```

## API Examples

### HTTP GET /relationship

```bash
curl "http://localhost:8000/relationship?name=Saanvi" \
  -H "X-API-Key: dev"
```

Response:
```json
{
  "person": "Saanvi",
  "relationshipToGirish": "Daughter",
  "confidence": "High",
  "matching": {
    "strategy": "exact",
    "score": 1.0
  },
  "source": {
    "file": "data/relationships.xlsx",
    "lastLoadedAt": "2025-10-16T20:00:00Z",
    "rows": 14
  }
}
```

### WebSocket /relationship/stream

```javascript
const ws = new WebSocket('ws://localhost:8000/relationship/stream');
ws.send(JSON.stringify({ name: "Saanvi", trace: true }));
```

Events:
```json
{"event": "start", "name": "Saanvi"}
{"event": "graph.node", "node": "normalize"}
{"event": "graph.node", "node": "exact_lookup", "result": {...}}
{"event": "result", "payload": {...}}
{"event": "end", "durationMs": 37}
```

## Development

### Running Tests

```bash
make test
```

### Linting & Type Checking

```bash
make lint
make typecheck
```

### Reloading Data

```bash
curl -X POST http://localhost:8000/reload \
  -H "X-API-Key: dev"
```

## Project Structure

```
relationship-finder-mcp/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings and configuration
│   ├── schemas.py        # Pydantic models
│   ├── excel_loader.py   # Excel data loading
│   ├── match.py          # Name matching utilities
│   ├── graph.py          # LangGraph workflow
│   └── service.py        # Main service layer
├── clients/
│   ├── python/          # Python CLI client
│   └── node/            # Node.js CLI client
├── data/
│   ├── relationships.xlsx    # Sample data
│   └── sample_queries.jsonl  # Test queries
├── tests/               # Test suite
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml      # Python dependencies
└── README.md
```

## Configuration

The service can be configured via environment variables:

- `PORT`: HTTP port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `ALLOW_FUZZY`: Enable fuzzy matching (default: true)
- `REDIS_URL`: Optional Redis URL for workflow state
- `CORS_ORIGINS`: Allowed CORS origins
- `API_KEY`: API key for authentication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (`make test`)
5. Submit a pull request

## License

MIT