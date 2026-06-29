# Python Observability & Monitoring Reference Guide

This reference details structured logging, distributed tracing, metrics instrumentation, and SLI/SLO patterns for Python applications.

---

## 1. Structured Logging with structlog

### Configuration Setup

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # JSON output for log aggregation
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Binding Context

```python
import structlog

log = structlog.get_logger()

# Bind context that persists across log calls
log = log.bind(service="user-api", environment="production")

def handle_request(request_id: str, user_id: str):
    # Bind request-scoped context
    log_ctx = log.bind(request_id=request_id, user_id=user_id)

    log_ctx.info("request_started", path="/api/users")
    # Output: {"event": "request_started", "path": "/api/users",
    #          "request_id": "abc-123", "user_id": "usr-42",
    #          "service": "user-api", "level": "info", "timestamp": "..."}

    log_ctx.info("request_completed", status=200, duration_ms=45)
```

### Log Levels Policy

| Level | Use For |
|:---|:---|
| **DEBUG** | Detailed diagnostic info (disabled in production) |
| **INFO** | Normal operational events (request started, job completed) |
| **WARNING** | Unexpected but recoverable situations (retry, fallback) |
| **ERROR** | Failures requiring attention (unhandled exception, service down) |
| **CRITICAL** | System-wide failures (database unreachable, data corruption) |

---

## 2. OpenTelemetry Python SDK

### Auto-instrumentation Setup

```python
# Install: pip install opentelemetry-distro opentelemetry-exporter-otlp
# Auto-instrument: opentelemetry-bootstrap -a install

# Run with auto-instrumentation:
# opentelemetry-instrument --service_name my-service python app.py
```

### Manual Span Creation

```python
from opentelemetry import trace

tracer = trace.get_tracer("myapp.tracer")

def process_order(order_id: str) -> dict:
    with tracer.start_as_current_span(
        "process_order",
        attributes={"order.id": order_id},
    ) as span:
        # Nested span for sub-operation
        with tracer.start_as_current_span("validate_payment") as child:
            child.set_attribute("payment.method", "credit_card")
            validate_payment(order_id)

        with tracer.start_as_current_span("update_inventory"):
            update_inventory(order_id)

        span.set_attribute("order.status", "completed")
        return {"order_id": order_id, "status": "completed"}
```

### Context Propagation

```python
from opentelemetry import context
from opentelemetry.propagate import inject, extract
import requests

def call_downstream_service(url: str, data: dict) -> dict:
    """Propagate trace context to downstream HTTP calls."""
    headers = {}
    inject(headers)  # Injects traceparent header

    response = requests.post(url, json=data, headers=headers)
    return response.json()

def handle_incoming_request(headers: dict):
    """Extract trace context from incoming request."""
    ctx = extract(headers)
    token = context.attach(ctx)
    try:
        # All spans created here are children of the upstream trace
        with tracer.start_as_current_span("handle_request"):
            process_request()
    finally:
        context.detach(token)
```

### Exporter Configuration

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource.create({"service.name": "my-service", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)

# OTLP exporter (Jaeger, Grafana Tempo, etc.)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

trace.set_tracer_provider(provider)
```

---

## 3. Metrics with prometheus-client

### Metric Types

```python
from prometheus_client import Counter, Gauge, Histogram, Summary

# Counter — monotonically increasing (requests served, errors)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "endpoint", "status"],
)

# Gauge — value that goes up and down (active connections, queue depth)
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active WebSocket connections",
)

# Histogram — distribution of values (request duration, response size)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    labelnames=["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Summary — similar to Histogram but calculates quantiles client-side
RESPONSE_SIZE = Summary(
    "http_response_size_bytes",
    "Response payload size in bytes",
)
```

### Using Metrics

```python
import time

def handle_request(method: str, endpoint: str):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status="200").inc()
    ACTIVE_CONNECTIONS.inc()

    start = time.perf_counter()
    try:
        result = process_request()
        return result
    finally:
        duration = time.perf_counter() - start
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        ACTIVE_CONNECTIONS.dec()
```

### Naming Conventions

| Pattern | Example | Use For |
|:---|:---|:---|
| `*_total` | `http_requests_total` | Counters |
| `*_seconds` | `request_duration_seconds` | Durations |
| `*_bytes` | `response_size_bytes` | Sizes |
| `*_info` | `build_info` | Metadata gauges |
| `*_created` | `process_start_time_created` | Timestamps |

---

## 4. FastAPI / Flask Integration

### FastAPI Middleware for Request Tracing

```python
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        log.info("request_started", method=request.method, path=request.url.path)

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        response.headers["X-Request-ID"] = request_id
        return response
```

### Health Check Endpoint

```python
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }

@app.get("/ready")
async def readiness_check():
    """Check dependencies (database, cache, etc.)."""
    checks = {
        "database": await check_database(),
        "cache": await check_cache(),
    }
    all_healthy = all(checks.values())
    return {"status": "ready" if all_healthy else "degraded", "checks": checks}
```

### Metrics Endpoint (Prometheus)

```python
from prometheus_client import make_asgi_app

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## 5. SLI / SLO Patterns

### Defining SLIs in Code

```python
from prometheus_client import Counter, Histogram

# SLI: Availability — ratio of successful requests
SLI_REQUESTS_TOTAL = Counter(
    "sli_requests_total", "Total requests for SLI", labelnames=["status_class"]
)

# SLI: Latency — proportion of requests below threshold
SLI_LATENCY = Histogram(
    "sli_request_duration_seconds",
    "Request duration for SLI",
    buckets=[0.1, 0.25, 0.5, 1.0],  # SLO thresholds
)

def record_sli(status_code: int, duration: float):
    status_class = "success" if 200 <= status_code < 500 else "error"
    SLI_REQUESTS_TOTAL.labels(status_class=status_class).inc()
    SLI_LATENCY.observe(duration)
```

### SLO Tracking

```python
# SLO Definitions:
# - Availability: 99.9% of requests return non-5xx in a 30-day window
# - Latency:      95% of requests complete within 500ms
#
# PromQL queries for SLO dashboards:
#
# Availability SLO:
#   1 - (sum(rate(sli_requests_total{status_class="error"}[30d]))
#        / sum(rate(sli_requests_total[30d])))
#
# Latency SLO:
#   histogram_quantile(0.95, sum(rate(sli_request_duration_seconds_bucket[30d])) by (le))
#
# Error Budget Remaining:
#   1 - ((1 - availability_slo_actual) / (1 - 0.999))
```
