# LLM FastAPI Service

Production-ready FastAPI service for deploying Hugging Face LLMs with comprehensive observability, security, and performance features.

## 🚀 Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **Hugging Face Integration**: Text generation using `transformers` pipeline wrapped with LangChain
- **Poetry Dependency Management**: Modern Python packaging with locked dependencies
- **Configuration Management**: YAML + .env with Pydantic validation (.env overrides YAML)
- **Security**: API key authentication, input validation, PII filtering, rate limiting
- **Observability**: Structured JSON logging, Prometheus metrics, request timing
- **Caching**: LRU cache with TTL for identical prompts
- **Docker**: Multi-stage Dockerfile with non-root user
- **Testing**: Comprehensive pytest suite with mocking
- **Streaming**: SSE streaming support for chat responses (where supported)

## 📋 Requirements

- Python 3.11+
- Poetry 1.7+
- Docker (optional, for containerized deployment)
- Hugging Face API token (for gated models)

## 🛠️ Installation

### Local Development

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ai-poc
```

2. **Install dependencies with Poetry**:
```bash
poetry install
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your HUGGINGFACE_TOKEN and API key
```

4. **Update configuration** (optional):
Edit `config.yml` to customize model, ports, rate limits, etc.

5. **Run the service**:
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the Makefile:
```bash
make run
```

## 🔧 Configuration

### config.yml

Default configuration with sensible defaults:

```yaml
app:
  name: "LLM FastAPI Service"
  host: "0.0.0.0"
  port: 8000

model:
  name: "google/gemma-2-2b-it"
  source: "hub"  # or "local"
  device: "cpu"   # or "cuda"
  max_tokens: 512
  temperature: 0.7

security:
  api_key: "change-me-in-env"
  max_prompt_chars: 4000

rate_limit:
  enabled: true
  requests_per_minute: 10

cache:
  enabled: true
  size: 100
  ttl_seconds: 3600

chat_history:
  enabled: true
  ttl_seconds: 7200  # 2 hours
```

### .env

Environment variables override config.yml:

```bash
# Model Configuration
MODEL__NAME=google/gemma-2-2b-it
HUGGINGFACE_TOKEN=your_token_here

# Security
SECURITY__API_KEY=your-secure-api-key-here

# Rate Limiting
RATE_LIMIT__REQUESTS_PER_MINUTE=10

# Cache
CACHE__ENABLED=true
CACHE__SIZE=100
```

## 📡 API Endpoints

### Health & Status

#### GET /health
Check service health and model status.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "google/gemma-2-2b-it"
}
```

#### GET /status
Get detailed service status with cache statistics.

```bash
curl http://localhost:8000/status
```

### Text Generation

#### POST /v1/generate
Generate text from a prompt.

```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

Response:
```json
{
  "generated_text": "Quantum computing is...",
  "prompt": "Explain quantum computing in simple terms",
  "model": "google/gemma-2-2b-it",
  "tokens_generated": 45,
  "cached": false
}
```

### Chat

#### POST /v1/chat
Chat with conversation history.

**Basic request (no session)**:
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

**With session history** (maintains conversation across requests):
```bash
# First message
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "session_id": "user-123-conversation",
    "messages": [
      {"role": "user", "content": "What is Python?"}
    ],
    "max_tokens": 100
  }'

# Follow-up (automatically includes previous context)
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "session_id": "user-123-conversation",
    "messages": [
      {"role": "user", "content": "What are its main features?"}
    ],
    "max_tokens": 100
  }'
```

Response:
```json
{
  "message": {
    "role": "assistant",
    "content": "The capital of France is Paris."
  },
  "model": "google/gemma-2-2b-it",
  "tokens_generated": 8,
  "cached": false
}
```

**Session History Features**:
- `session_id`: Optional string to maintain conversation history
- History TTL: 2 hours (configurable via `chat_history.ttl_seconds`)
- Automatic context merging: Previous messages are automatically included
- Memory efficient: Old sessions auto-expire after TTL

#### Streaming Response
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "messages": [{"role": "user", "content": "Tell me a story"}],
    "stream": true
  }'
```

### Metrics

#### GET /metrics
Prometheus-formatted metrics.

```bash
curl http://localhost:8000/metrics
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t llm-fastapi-service:latest .
```

Or use Makefile:
```bash
make build-docker
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -e HUGGINGFACE_TOKEN=your_token \
  -e SECURITY__API_KEY=your_key \
  -v $(pwd)/config.yml:/app/config.yml \
  --name llm-service \
  llm-fastapi-service:latest
```

Or use Makefile:
```bash
make run-docker
```

### Check Logs

```bash
docker logs -f llm-service
```

Or:
```bash
make logs
```

## 🧪 Testing

### Run All Tests

```bash
poetry run pytest tests/ -v --cov=app --cov-report=term-missing
```

Or use Makefile:
```bash
make test
```

### Run Specific Test

```bash
poetry run pytest tests/test_config.py -v
```

### Test Coverage

```bash
make test
# Coverage report will be in htmlcov/index.html
```

## 🔍 Code Quality

### Lint

```bash
make lint
```

### Format

```bash
make format
```

### Type Check

```bash
make type-check
```

### Run All Checks

```bash
make check-all
```

## 📊 Observability

### Structured Logging

Logs are output in JSON format (configurable):

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "llm_service",
  "message": "POST /v1/generate - 200",
  "method": "POST",
  "route": "/v1/generate",
  "status_code": 200,
  "latency_ms": 1234.56
}
```

### Prometheus Metrics

Available at `/metrics`:

- `http_requests_total`: Total HTTP requests by method, endpoint, status
- `tokens_generated_total`: Total tokens generated by model
- `http_request_duration_seconds`: Request latency histogram

### Performance Headers

Each response includes `X-Process-Time` header with request processing time.

## 🔒 Security Features

- **API Key Authentication**: Required for all generation endpoints
- **Rate Limiting**: Token bucket algorithm by IP or API key
- **Input Validation**: Pydantic models with strict validation
- **Prompt Length Limits**: Configurable maximum prompt size
- **PII Filtering**: Optional content filtering (basic patterns provided)
- **Output Sanitization**: Configurable response filtering

## 🎯 Project Structure

```
ai-poc/
├── app/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── chat.py          # Chat endpoint
│   │   │   ├── health.py        # Health checks
│   │   │   └── inference.py     # Text generation
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── schemas.py           # Pydantic models
│   ├── core/
│   │   ├── cache.py             # Response caching
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Structured logging
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── security.py          # Security utilities
│   ├── llm/
│   │   ├── chain.py             # LangChain integration
│   │   ├── loader.py            # Model loading
│   │   └── prompts/
│   │       └── base_system.txt  # System prompt
│   ├── utils/
│   │   ├── errors.py            # Error handling
│   │   └── timing.py            # Performance utilities
│   └── main.py                  # FastAPI application
├── tests/
│   ├── test_config.py           # Config tests
│   └── test_inference.py        # API tests
├── config.yml                   # Configuration file
├── .env.example                 # Environment template
├── pyproject.toml               # Poetry configuration
├── Dockerfile                   # Multi-stage Docker build
├── Makefile                     # Development shortcuts
└── README.md                    # This file
```

## 🚦 Common Issues

### Model Download Timeout

If model download takes too long, consider:
- Using a smaller model for testing
- Pre-downloading the model locally
- Setting `MODEL__SOURCE=local` and providing local path

### CUDA Out of Memory

If using GPU:
- Reduce `MODEL__MAX_TOKENS`
- Use CPU: `MODEL__DEVICE=cpu`
- Use a smaller model

### Rate Limit Issues

Adjust in `.env`:
```bash
RATE_LIMIT__REQUESTS_PER_MINUTE=50
RATE_LIMIT__BURST_SIZE=100
```

## 📝 Development

### Add New Dependencies

```bash
poetry add package-name
```

### Update Dependencies

```bash
poetry update
```

### Create New Endpoint

1. Add schema to `app/api/schemas.py`
2. Create router in `app/api/routers/`
3. Register router in `app/main.py`
4. Add tests in `tests/`

## 📄 License

[Your License Here]

## 🤝 Contributing

[Contribution Guidelines]

## 📧 Support

[Support Contact Information]

---

**Model Used**: `google/gemma-2-2b-it` (configurable)  
**Framework**: FastAPI + Hugging Face Transformers + LangChain  
**Built with**: Poetry, Pydantic, Docker