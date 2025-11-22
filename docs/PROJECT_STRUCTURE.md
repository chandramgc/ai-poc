# Project Structure Summary

## Complete File Tree

```
ai-poc/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── schemas.py               # Pydantic request/response models
│   │   ├── dependencies.py          # FastAPI dependency injection
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py            # Health check endpoints
│   │       ├── inference.py         # Text generation endpoint
│   │       └── chat.py              # Chat endpoint with streaming
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration with Pydantic Settings
│   │   ├── logging.py               # Structured JSON logging
│   │   ├── rate_limit.py            # Token bucket rate limiter
│   │   ├── security.py              # API key validation, content filtering
│   │   └── cache.py                 # LRU cache with TTL
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── loader.py                # HuggingFace pipeline loader
│   │   ├── chain.py                 # LangChain integration
│   │   └── prompts/
│   │       └── base_system.txt      # Default system prompt
│   │
│   └── utils/
│       ├── __init__.py
│       ├── errors.py                # Custom exceptions and handlers
│       └── timing.py                # Performance timing utilities
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py               # Configuration tests
│   └── test_inference.py            # API endpoint tests
│
├── config.yml                       # Main configuration file
├── .env.example                     # Environment variables template
├── pyproject.toml                   # Poetry dependencies and config
├── poetry.lock                      # Locked dependencies (generated)
│
├── Dockerfile                       # Multi-stage Docker build
├── .dockerignore                    # Docker build exclusions
├── Makefile                         # Development shortcuts
│
├── README.md                        # Comprehensive documentation
├── QUICKSTART.md                    # Quick start guide
├── examples.sh                      # Example API calls
└── .gitignore                       # Git exclusions
```

## Key Files Overview

### Application Core

- **app/main.py**: FastAPI application with middleware, startup/shutdown, metrics
- **app/core/config.py**: Configuration management (YAML + .env with Pydantic)
- **app/llm/loader.py**: Model loading and text generation
- **app/llm/chain.py**: LangChain wrapper for the pipeline

### API Layer

- **app/api/routers/health.py**: `/health`, `/status` endpoints
- **app/api/routers/inference.py**: `/v1/generate` endpoint with caching
- **app/api/routers/chat.py**: `/v1/chat` endpoint with streaming support
- **app/api/schemas.py**: Pydantic models for all requests/responses

### Core Utilities

- **app/core/rate_limit.py**: Token bucket rate limiter by IP/API key
- **app/core/security.py**: API key validation, PII filtering, input validation
- **app/core/cache.py**: LRU cache for response caching
- **app/core/logging.py**: Structured JSON logging

### Configuration

- **config.yml**: Default configuration (model, ports, limits)
- **.env**: Environment-specific overrides (tokens, secrets)
- **pyproject.toml**: Poetry dependencies, scripts, tool configs

### Deployment

- **Dockerfile**: Multi-stage build with Poetry, non-root user
- **Makefile**: Development commands (run, test, build, etc.)

### Testing

- **tests/test_config.py**: Configuration loading tests
- **tests/test_inference.py**: API endpoint tests with mocking

### Documentation

- **README.md**: Full documentation with examples
- **QUICKSTART.md**: 5-minute setup guide
- **examples.sh**: Executable curl examples

## Technology Stack

### Core Framework
- FastAPI 0.109+
- Uvicorn (ASGI server)
- Pydantic 2.5+ (validation)

### ML/AI
- Transformers 4.36+ (Hugging Face)
- PyTorch 2.1+
- LangChain 0.1+
- Model: google/gemma-2-2b-it (configurable)

### Utilities
- python-dotenv (environment)
- PyYAML (configuration)
- prometheus-client (metrics)
- cachetools (caching)

### Development
- Poetry (dependency management)
- Ruff (linting)
- Black (formatting)
- Pytest (testing)
- MyPy (type checking)

## Configuration Precedence

```
.env (highest priority)
    ↓
config.yml
    ↓
Default values (lowest priority)
```

## API Authentication Flow

```
Request → API Key Header Check → Rate Limit Check → Input Validation → Handler
                ↓                      ↓                    ↓
            401/403               429 Error           400 Error
```

## Request Processing Flow

```
Request
  ↓
Middleware (timing, metrics)
  ↓
Authentication (API key)
  ↓
Rate Limiting (token bucket)
  ↓
Input Validation (Pydantic)
  ↓
Content Filtering (PII, profanity)
  ↓
Cache Check
  ↓ (cache miss)
Model Generation
  ↓
Output Sanitization
  ↓
Cache Store
  ↓
Response (with metrics, timing)
```

## Metrics Collected

- `http_requests_total`: Counter by method, endpoint, status
- `tokens_generated_total`: Counter by model
- `http_request_duration_seconds`: Histogram by method, endpoint

## Logging Format

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "llm_service",
  "message": "Request details",
  "method": "POST",
  "route": "/v1/generate",
  "status_code": 200,
  "latency_ms": 1234.56
}
```

## Environment Variables

### Required
- `HUGGINGFACE_TOKEN`: HuggingFace API token
- `SECURITY__API_KEY`: Service API key

### Optional (with defaults)
- `MODEL__NAME`: Model identifier
- `MODEL__DEVICE`: cpu or cuda
- `APP__PORT`: Server port (8000)
- `RATE_LIMIT__REQUESTS_PER_MINUTE`: Rate limit (10)
- `CACHE__ENABLED`: Enable caching (true)
- `CACHE__SIZE`: Cache size (100)

## Docker Image Details

- Base: `python:3.11-slim`
- Multi-stage build
- Non-root user (appuser, UID 1000)
- Health check included
- Port: 8000
- Working directory: /app

## Testing Strategy

- Mock transformers pipeline to avoid model download
- Test configuration loading and merging
- Test all API endpoints (success and error cases)
- Test authentication and rate limiting
- Test input validation
- Coverage reporting with pytest-cov

## Production Checklist

- [ ] Set strong `SECURITY__API_KEY`
- [ ] Configure `HUGGINGFACE_TOKEN` for gated models
- [ ] Adjust `RATE_LIMIT__REQUESTS_PER_MINUTE` for load
- [ ] Set appropriate `MODEL__MAX_TOKENS`
- [ ] Configure `LOG_LEVEL` (INFO or WARNING for prod)
- [ ] Enable metrics collection
- [ ] Set up monitoring for `/health` endpoint
- [ ] Configure proper CORS if needed
- [ ] Use HTTPS in production
- [ ] Set up log aggregation
- [ ] Configure backup for model cache

## Next Steps

1. Run `poetry install` to install dependencies
2. Copy `.env.example` to `.env` and configure
3. Run `make run` to start the service
4. Test with `./examples.sh`
5. Run tests with `make test`
6. Build Docker image with `make build-docker`
7. Deploy to your infrastructure

---

**Model**: google/gemma-2-2b-it (2B parameters, instruction-tuned)  
**Framework**: FastAPI + HuggingFace Transformers + LangChain  
**Deployment**: Docker + Poetry  
**Architecture**: Production-ready with observability, security, and performance features
