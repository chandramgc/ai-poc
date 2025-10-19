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

# Or

lsof -ti:8000 | xargs kill -9 2>/dev/null; cd /Users/girish/MyDrive/Workspace/ai-poc && poetry run uvicorn app.main:app --reload

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

### REST API

#### GET /relationship - Exact Match

```bash
curl "http://localhost:8000/relationship?name=Saanvi" \
  -H "X-API-Key: dev"
```

**Response (200 OK):**
```json
{
  "person": "Saanvi",
  "relationship_to_girish": "Daughter",
  "confidence": "High",
  "matching": {
    "strategy": "exact",
    "score": 1.0
  },
  "source": {
    "file": "data/relationships.xlsx",
    "last_loaded_at": "2025-10-18T13:48:06.755000",
    "rows": 14
  }
}
```

#### GET /relationship - Fuzzy Match

```bash
curl "http://localhost:8000/relationship?name=Saani" \
  -H "X-API-Key: dev"
```

**Response (200 OK):**
```json
{
  "person": "Saanvi",
  "relationship_to_girish": "Daughter",
  "confidence": "Medium",
  "matching": {
    "strategy": "fuzzy",
    "score": 0.83
  },
  "source": {
    "file": "data/relationships.xlsx",
    "last_loaded_at": "2025-10-18T13:48:06.755000",
    "rows": 14
  }
}
```

#### GET /relationship - No Match Found

```bash
curl "http://localhost:8000/relationship?name=UnknownPerson" \
  -H "X-API-Key: dev"
```

**Response (404 Not Found):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "No confident match found for name: UnknownPerson",
    "traceId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### GET /relationship - Missing API Key

```bash
curl "http://localhost:8000/relationship?name=Saanvi"
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing API key"
}
```

#### POST /reload - Reload Data

```bash
curl -X POST "http://localhost:8000/reload" \
  -H "X-API-Key: dev"
```

**Response (204 No Content):**
```bash
# No response body
```

#### GET /healthz - Health Check

```bash
curl "http://localhost:8000/healthz"
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "data": {
    "last_loaded": "2025-10-18T13:48:06.755000",
    "row_count": 14
  }
}
```

### WebSocket API

#### /relationship/stream - Streaming Workflow

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/relationship/stream');

// Send request with API key in headers
ws.onopen = () => {
  // IMPORTANT: Use double quotes for JSON property names
  ws.send(JSON.stringify({
    "name": "Saanvi",
    "trace": true
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);

  switch(data.event) {
    case 'start':
      console.log(`Starting lookup for: ${data.name}`);
      break;
    case 'node':
      console.log(`Processing: ${data.node}`);
      break;
    case 'result':
      console.log('Final result:', data.payload);
      break;
    case 'error':
      console.error('Error:', data.error);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**WebSocket Headers (for authentication):**
```javascript
// WebSocket authentication is done via headers during the initial handshake
// In browsers, you may need to use a different approach or proxy
const ws = new WebSocket('ws://localhost:8000/relationship/stream', [], {
  headers: {
    'X-API-Key': 'dev'
  }
});
```

**Note:** WebSocket header authentication may not work in all browsers due to security restrictions. For browser-based clients, consider using query parameters or token-based authentication instead.

**Streaming Events:**
```json
{"event": "start", "name": "Saanvi"}
{"event": "node", "node": "normalize"}
{"event": "node", "node": "exact_lookup"}
{"event": "result", "payload": {
  "person": "Saanvi",
  "relationship_to_girish": "Daughter",
  "confidence": "High",
  "matching": {"strategy": "exact", "score": 1.0},
  "source": {
    "file": "data/relationships.xlsx",
    "last_loaded_at": "2025-10-18T13:48:06.755000",
    "rows": 14
  }
}}
```

**Error Event:**
```json
{
  "event": "error",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "File not found: data/relationships.xlsx",
    "traceId": "550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**Python WebSocket Example:**
```python
import asyncio
import websockets
import json

async def lookup_relationship():
    uri = "ws://localhost:8000/relationship/stream"

    async with websockets.connect(uri, extra_headers={"X-API-Key": "dev"}) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "name": "Saanvi",
            "trace": True
        }))

        # Receive events
        async for message in websocket:
            data = json.loads(message)
            print(f"Event: {data['event']}")

            if data['event'] == 'result':
                print(f"Result: {data['payload']}")
            elif data['event'] == 'error':
                print(f"Error: {data['error']}")

asyncio.run(lookup_relationship())
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
│   ├── csv_loader.py    # CSV data loading
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