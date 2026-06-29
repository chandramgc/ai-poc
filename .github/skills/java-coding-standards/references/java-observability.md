# Java Observability & Monitoring Reference Guide

This reference details the three pillars of observability, Spring Boot Actuator configuration, Micrometer metrics, OpenTelemetry distributed tracing, structured logging, and SLI/SLO definition templates.

---

## 1. Three Pillars of Observability

| Pillar | Purpose | Tool/Library | Signal Type |
|--------|---------|--------------|-------------|
| **Traces** | Follow a request across service boundaries | OpenTelemetry, Micrometer Tracing | Distributed spans with parent-child relationships |
| **Metrics** | Quantify system behavior over time | Micrometer, Prometheus | Counters, timers, gauges, histograms |
| **Logs** | Record discrete events with context | SLF4J + Logback, structured JSON | Timestamped, leveled messages with MDC context |

**How they connect:** A single request generates a `traceId` (trace), increments a request counter (metric), and writes log entries tagged with that `traceId` (log). Correlation via `traceId` and `spanId` lets you jump between signals in your observability platform.

---

## 2. Spring Boot Actuator

### Health Endpoints Configuration

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
      base-path: /actuator
  endpoint:
    health:
      show-details: when_authorized  # never | when_authorized | always
      show-components: when_authorized
  health:
    db:
      enabled: true
    diskSpace:
      enabled: true
    redis:
      enabled: true
```

### Custom Health Indicator

```java
@Component
public class PaymentGatewayHealthIndicator implements HealthIndicator {

    private final PaymentGatewayClient client;

    public PaymentGatewayHealthIndicator(PaymentGatewayClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        try {
            boolean reachable = client.ping();
            if (reachable) {
                return Health.up()
                    .withDetail("gateway", "reachable")
                    .withDetail("latencyMs", client.lastPingLatency())
                    .build();
            }
            return Health.down()
                .withDetail("gateway", "unreachable")
                .build();
        } catch (Exception ex) {
            return Health.down(ex)
                .withDetail("gateway", "error")
                .build();
        }
    }
}
```

### Info Endpoint Customization

```yaml
# application.yml
info:
  app:
    name: ${spring.application.name}
    version: '@project.version@'
    java-version: ${java.version}
    spring-boot-version: '@spring-boot.version@'
  build:
    timestamp: '@build.timestamp@'
```

### Secure Actuator Exposure

```java
@Configuration
@EnableWebSecurity
public class ActuatorSecurityConfig {

    @Bean
    @Order(1)
    public SecurityFilterChain actuatorFilterChain(HttpSecurity http) throws Exception {
        return http
            .securityMatcher("/actuator/**")
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/actuator/info").permitAll()
                .requestMatchers("/actuator/**").hasRole("OPS"))
            .httpBasic(Customizer.withDefaults())
            .build();
    }
}
```

---

## 3. Micrometer Metrics

### Counter (Request Counts)

```java
@Service
public class OrderService {

    private final Counter orderCounter;

    public OrderService(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.created")
            .description("Total orders created")
            .tag("type", "api")
            .register(registry);
    }

    public OrderResponse createOrder(OrderRequest request) {
        // ... business logic ...
        orderCounter.increment();
        return response;
    }
}
```

### Timer (Response Times)

```java
@Service
public class PaymentService {

    private final Timer paymentTimer;

    public PaymentService(MeterRegistry registry) {
        this.paymentTimer = Timer.builder("payments.processing.duration")
            .description("Payment processing time")
            .publishPercentiles(0.5, 0.95, 0.99)
            .publishPercentileHistogram(true)
            .register(registry);
    }

    public PaymentResult processPayment(PaymentRequest request) {
        return paymentTimer.record(() -> {
            // ... payment processing logic ...
            return gateway.charge(request);
        });
    }
}
```

### Gauge (Active Connections)

```java
@Component
public class ConnectionPoolMetrics {

    public ConnectionPoolMetrics(MeterRegistry registry, DataSource dataSource) {
        if (dataSource instanceof HikariDataSource hikari) {
            HikariPoolMXBean pool = hikari.getHikariPoolMXBean();

            Gauge.builder("db.connections.active", pool, HikariPoolMXBean::getActiveConnections)
                .description("Active database connections")
                .register(registry);

            Gauge.builder("db.connections.idle", pool, HikariPoolMXBean::getIdleConnections)
                .description("Idle database connections")
                .register(registry);
        }
    }
}
```

### DistributionSummary (Request Sizes)

```java
@Component
public class RequestSizeMetrics {

    private final DistributionSummary requestSizeSummary;

    public RequestSizeMetrics(MeterRegistry registry) {
        this.requestSizeSummary = DistributionSummary.builder("http.request.size")
            .description("HTTP request body size in bytes")
            .baseUnit("bytes")
            .publishPercentiles(0.5, 0.95)
            .maximumExpectedValue(10_000_000.0)
            .register(registry);
    }

    public void recordRequestSize(long sizeInBytes) {
        requestSizeSummary.record(sizeInBytes);
    }
}
```

### Custom Tags and Naming Conventions

| Convention | Example | Description |
|------------|---------|-------------|
| Dot-separated names | `orders.created.total` | Use lowercase dots for metric hierarchy |
| Static tags | `.tag("env", "prod")` | Environment, region, service |
| Dynamic tags | `.tag("status", statusCode)` | Keep cardinality low — avoid IDs or emails |
| Base units | `.baseUnit("milliseconds")` | Always specify units explicitly |

> [!WARNING]
> High-cardinality tags (user IDs, request IDs, email addresses) will cause metric explosion and OOM in your metrics backend. Use traces for high-cardinality correlation instead.

---

## 4. OpenTelemetry Integration

### Spring Boot OTel Auto-Instrumentation

```groovy
// build.gradle
dependencies {
    implementation 'io.opentelemetry.instrumentation:opentelemetry-spring-boot-starter:2.11.0'
}
```

```yaml
# application.yml
otel:
  service:
    name: ${spring.application.name}
  exporter:
    otlp:
      endpoint: http://otel-collector:4317
      protocol: grpc
  traces:
    exporter: otlp
  metrics:
    exporter: otlp
  logs:
    exporter: otlp
```

### Manual Span Creation

```java
@Service
public class InventoryService {

    private final Tracer tracer;

    public InventoryService(Tracer tracer) {
        this.tracer = tracer;
    }

    public boolean checkAvailability(String productId, int quantity) {
        Span span = tracer.spanBuilder("inventory.checkAvailability")
            .setSpanKind(SpanKind.INTERNAL)
            .startSpan();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("product.id", productId);
            span.setAttribute("requested.quantity", quantity);

            boolean available = repository.hasStock(productId, quantity);
            span.setAttribute("result.available", available);
            return available;

        } catch (Exception ex) {
            span.setStatus(StatusCode.ERROR, ex.getMessage());
            span.recordException(ex);
            throw ex;
        } finally {
            span.end();
        }
    }
}
```

### Custom Attributes on Spans

```java
// ✅ Add business context to spans for debugging
Span.current().setAttribute("order.id", orderId);
Span.current().setAttribute("customer.tier", "premium");
Span.current().setAttribute("payment.method", "credit_card");

// ✅ Record events within a span
Span.current().addEvent("payment.authorized", Attributes.of(
    AttributeKey.stringKey("provider"), "stripe",
    AttributeKey.doubleKey("amount"), 99.99
));
```

### Context Propagation

```java
// ✅ Context propagation happens automatically with OTel Spring Boot starter.
// For manual async propagation:
@Service
public class AsyncOrderService {

    private final ExecutorService executor;

    public AsyncOrderService() {
        // ✅ Wrap executor to propagate OTel context
        this.executor = Context.taskWrapping(
            Executors.newFixedThreadPool(10));
    }

    public CompletableFuture<Void> processAsync(Order order) {
        return CompletableFuture.runAsync(
            () -> processOrder(order), executor);
    }
}
```

### Baggage for Correlation IDs

```java
// ✅ Set baggage at the entry point (e.g., filter or interceptor)
@Component
public class CorrelationFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {

        String correlationId = ((HttpServletRequest) req)
            .getHeader("X-Correlation-Id");

        if (correlationId == null) {
            correlationId = UUID.randomUUID().toString();
        }

        Baggage.current()
            .toBuilder()
            .put("correlation.id", correlationId)
            .build()
            .makeCurrent();

        chain.doFilter(req, res);
    }
}
```

---

## 5. Structured Logging

### SLF4J + Logback JSON Encoder

```groovy
// build.gradle
dependencies {
    implementation 'net.logstash.logback:logstash-logback-encoder:8.0'
}
```

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <includeMdcKeyName>userId</includeMdcKeyName>
            <includeMdcKeyName>requestId</includeMdcKeyName>
        </encoder>
    </appender>

    <springProfile name="prod">
        <root level="INFO">
            <appender-ref ref="JSON" />
        </root>
    </springProfile>

    <springProfile name="dev">
        <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
            <encoder>
                <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} [%mdc] - %msg%n</pattern>
            </encoder>
        </appender>
        <root level="DEBUG">
            <appender-ref ref="CONSOLE" />
        </root>
    </springProfile>
</configuration>
```

### MDC for Request Context

```java
@Component
public class MdcFilter implements Filter {

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpReq = (HttpServletRequest) req;

        try {
            MDC.put("requestId", UUID.randomUUID().toString());
            MDC.put("userId", extractUserId(httpReq));
            MDC.put("method", httpReq.getMethod());
            MDC.put("path", httpReq.getRequestURI());
            // traceId and spanId are auto-populated by OTel

            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }

    private String extractUserId(HttpServletRequest req) {
        // Extract from JWT or session — return "anonymous" if absent
        return Optional.ofNullable(req.getUserPrincipal())
            .map(Principal::getName)
            .orElse("anonymous");
    }
}
```

### Log Levels Policy

| Level | When to Use | Example |
|-------|-------------|---------|
| **ERROR** | Unrecoverable failures, data loss, SLA violations | `log.error("Payment failed for order={}", orderId, ex)` |
| **WARN** | Degraded operation, retried failures, approaching limits | `log.warn("Cache miss — falling back to DB for key={}", key)` |
| **INFO** | Significant business events, state transitions | `log.info("Order {} transitioned to SHIPPED", orderId)` |
| **DEBUG** | Diagnostic detail for development/troubleshooting | `log.debug("Query returned {} results for filter={}", count, filter)` |

> [!IMPORTANT]
> Production log level should be **INFO**. Never log sensitive data (passwords, tokens, PII) at any level. Use `log.atDebug().log(...)` for expensive log message construction to avoid allocation when DEBUG is disabled.

---

## 6. SLI/SLO Definition Templates

### Service Level Indicators & Objectives

| SLI Name | Measurement | Target (SLO) | Alert Threshold |
|----------|-------------|---------------|-----------------|
| **Availability** | `1 - (5xx responses / total responses)` | ≥ 99.9% over 30d rolling | < 99.5% over 5m window |
| **Latency (p50)** | `http.server.requests` timer p50 | ≤ 100ms | > 200ms over 5m window |
| **Latency (p95)** | `http.server.requests` timer p95 | ≤ 500ms | > 1000ms over 5m window |
| **Latency (p99)** | `http.server.requests` timer p99 | ≤ 1000ms | > 2000ms over 5m window |
| **Error Rate** | `errors.total / requests.total` | ≤ 0.1% over 30d rolling | > 1% over 5m window |
| **Saturation** | `db.connections.active / db.connections.max` | ≤ 80% | > 90% over 5m window |
| **Throughput** | `requests.total` rate per second | ≥ baseline ± 50% | < 50% of baseline over 15m |

### Prometheus Alert Rule Example

```yaml
# prometheus-alerts.yml
groups:
  - name: service-slos
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m]))
          /
          sum(rate(http_server_requests_seconds_count[5m]))
          > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate exceeds 1% SLO"
          description: "{{ $labels.service }} error rate is {{ $value | humanizePercentage }}"

      - alert: HighP95Latency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_server_requests_seconds_bucket[5m])) by (le, service))
          > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency exceeds 1s SLO"
```

> [!TIP]
> Use error budgets to balance reliability with feature velocity. If your 30-day error budget is exhausted, freeze feature releases and focus on reliability improvements.
