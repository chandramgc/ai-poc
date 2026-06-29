# Modern Java Features Reference (Java 21+)

This reference details modern Java language features from Java 15 through Java 21+, including records, sealed classes, pattern matching, text blocks, virtual threads, structured concurrency, and enhanced switch expressions.

---

## 1. Records (Java 16+)

Records are immutable data carriers that replace verbose DTO and value object boilerplate. The compiler auto-generates `equals()`, `hashCode()`, `toString()`, and accessor methods.

### Basic Record as DTO

```java
// ✅ Replaces a 40+ line POJO with getters, equals, hashCode, toString
public record OrderResponse(
    String orderId,
    String status,
    BigDecimal totalAmount,
    Instant createdAt
) {}
```

### Record with JSON Serialization

```java
public record CreateOrderRequest(
    @JsonProperty("product_id")
    @NotBlank(message = "Product ID is required")
    String productId,

    @JsonProperty("quantity")
    @Min(value = 1, message = "Quantity must be at least 1")
    int quantity,

    @JsonProperty("shipping_address")
    @Valid @NotNull
    AddressDto shippingAddress
) {}
```

### Record with Compact Constructor Validation

```java
public record Money(BigDecimal amount, String currency) {
    // ✅ Compact constructor — validates on creation
    public Money {
        Objects.requireNonNull(amount, "Amount must not be null");
        Objects.requireNonNull(currency, "Currency must not be null");
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount must be non-negative");
        }
        currency = currency.toUpperCase(Locale.ROOT);
    }
}
```

> [!TIP]
> Use records for DTOs, API request/response bodies, event payloads, and value objects. Avoid records for JPA entities (they require mutable fields and no-arg constructors).

---

## 2. Sealed Classes (Java 17+)

Sealed classes restrict which classes can extend them, creating closed hierarchies ideal for domain modeling and exhaustive pattern matching.

### Domain Model with Sealed Interface

```java
public sealed interface PaymentResult
    permits PaymentResult.Success, PaymentResult.Declined, PaymentResult.Error {

    record Success(String transactionId, Instant processedAt) implements PaymentResult {}
    record Declined(String reason, String code) implements PaymentResult {}
    record Error(String message, Exception cause) implements PaymentResult {}
}
```

### Exception Hierarchy with Sealed Classes

```java
public sealed abstract class OrderException extends RuntimeException
    permits OrderNotFoundException, OrderValidationException, OrderConflictException {

    protected OrderException(String message) {
        super(message);
    }
}

public final class OrderNotFoundException extends OrderException {
    public OrderNotFoundException(String orderId) {
        super("Order not found: " + orderId);
    }
}

public final class OrderValidationException extends OrderException {
    private final List<String> violations;

    public OrderValidationException(List<String> violations) {
        super("Validation failed: " + String.join(", ", violations));
        this.violations = List.copyOf(violations);
    }

    public List<String> violations() { return violations; }
}

public final class OrderConflictException extends OrderException {
    public OrderConflictException(String orderId) {
        super("Order conflict: " + orderId);
    }
}
```

### Exhaustive Handling with Sealed Types

```java
// ✅ Compiler enforces exhaustiveness — adding a new permit forces updates
public String describeResult(PaymentResult result) {
    return switch (result) {
        case PaymentResult.Success s   -> "Paid: " + s.transactionId();
        case PaymentResult.Declined d  -> "Declined: " + d.reason();
        case PaymentResult.Error e     -> "Error: " + e.message();
    };
}
```

---

## 3. Pattern Matching

### instanceof Pattern Matching (Java 16+)

```java
// ❌ Old style — cast after instanceof check
if (shape instanceof Circle) {
    Circle c = (Circle) shape;
    return Math.PI * c.radius() * c.radius();
}

// ✅ Pattern matching — binding variable in one step
if (shape instanceof Circle c) {
    return Math.PI * c.radius() * c.radius();
}
```

### Switch Expressions with Patterns (Java 21+)

```java
public double calculateArea(Shape shape) {
    return switch (shape) {
        case Circle c    -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t  -> 0.5 * t.base() * t.height();
        // No default needed if Shape is sealed and all permits are covered
    };
}
```

### Record Patterns (Java 21+)

```java
// ✅ Destructure records directly in patterns
public String formatEntry(Object obj) {
    return switch (obj) {
        case Money(var amount, var currency)
            -> String.format("%s %s", currency, amount);
        case Point(var x, var y)
            -> String.format("(%d, %d)", x, y);
        default
            -> obj.toString();
    };
}
```

### Guarded Patterns (Java 21+)

```java
public String classifyOrder(Order order) {
    return switch (order) {
        case Order o when o.total().compareTo(new BigDecimal("1000")) > 0
            -> "HIGH_VALUE";
        case Order o when o.items().size() > 10
            -> "BULK";
        case Order o when o.isPriority()
            -> "PRIORITY";
        default
            -> "STANDARD";
    };
}
```

---

## 4. Text Blocks (Java 15+)

### Multi-line Strings for SQL, JSON, HTML

```java
// ✅ SQL query — clean, readable, no concatenation
String sql = """
    SELECT o.id, o.status, o.total_amount
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE c.email = :email
      AND o.created_at > :since
    ORDER BY o.created_at DESC
    LIMIT :limit
    """;

// ✅ JSON template
String jsonTemplate = """
    {
        "orderId": "%s",
        "status": "%s",
        "amount": %.2f
    }
    """.formatted(orderId, status, amount);

// ✅ HTML email template
String html = """
    <html>
    <body>
        <h1>Order Confirmation</h1>
        <p>Your order <strong>%s</strong> has been placed.</p>
        <p>Total: $%.2f</p>
    </body>
    </html>
    """.formatted(orderId, totalAmount);
```

### Formatting with `formatted()` and `indent()`

```java
// ✅ formatted() replaces String.format()
String msg = """
    Hello %s,
    Your account balance is $%.2f.
    """.formatted(name, balance);

// ✅ indent() adjusts indentation
String indented = "line1\nline2\nline3".indent(4);
// Result: "    line1\n    line2\n    line3\n"
```

---

## 5. Virtual Threads (Java 21+)

Virtual threads (Project Loom) are lightweight threads managed by the JVM, enabling massive concurrency without the overhead of OS threads. Ideal for I/O-bound workloads.

### When to Use Virtual Threads vs Platform Threads

| Scenario | Thread Type | Reason |
|----------|-------------|--------|
| HTTP request handling | Virtual | I/O-bound, high concurrency |
| Database queries | Virtual | Blocking I/O, many concurrent queries |
| File I/O operations | Virtual | Blocking I/O |
| CPU-intensive computation | Platform | Virtual threads don't help CPU-bound work |
| `synchronized` blocks with I/O | Platform | Virtual threads pin to carrier in `synchronized` |

### Spring Boot Virtual Thread Configuration

```yaml
# application.yml — Spring Boot 3.2+
spring:
  threads:
    virtual:
      enabled: true
```

That single property configures Tomcat, scheduled tasks, and async executors to use virtual threads.

### Manual Virtual Thread Usage

```java
// ✅ Simple virtual thread
Thread.startVirtualThread(() -> {
    var result = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
    processResult(result);
});

// ✅ Virtual thread executor for bulk I/O
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> futures = urls.stream()
        .map(url -> executor.submit(() -> fetchUrl(url)))
        .toList();

    List<String> results = futures.stream()
        .map(f -> {
            try { return f.get(); }
            catch (Exception e) { throw new RuntimeException(e); }
        })
        .toList();
}
```

> [!WARNING]
> Avoid `synchronized` blocks with I/O inside virtual threads — this pins the virtual thread to a carrier thread. Use `ReentrantLock` instead.

```java
// ❌ Pins virtual thread
synchronized (lock) {
    database.query(sql);
}

// ✅ Safe with virtual threads
private final ReentrantLock lock = new ReentrantLock();

lock.lock();
try {
    database.query(sql);
} finally {
    lock.unlock();
}
```

---

## 6. Structured Concurrency (Java 21+ Preview)

Structured concurrency treats groups of related concurrent tasks as a single unit of work, ensuring proper cleanup and error propagation.

### ShutdownOnFailure Pattern

```java
// ✅ All-or-nothing — if any task fails, cancel the rest
public OrderDetails fetchOrderDetails(String orderId) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
        Subtask<Order> orderTask = scope.fork(() -> orderService.findById(orderId));
        Subtask<Customer> customerTask = scope.fork(() -> customerService.findByOrderId(orderId));
        Subtask<List<Item>> itemsTask = scope.fork(() -> itemService.findByOrderId(orderId));

        scope.join();            // Wait for all tasks
        scope.throwIfFailed();   // Propagate first failure

        return new OrderDetails(
            orderTask.get(),
            customerTask.get(),
            itemsTask.get()
        );
    }
}
```

### ShutdownOnSuccess Pattern

```java
// ✅ First-success-wins — cancel remaining tasks after first result
public String fetchFromFastestMirror(String resourceId) throws Exception {
    try (var scope = new StructuredTaskScope.ShutdownOnSuccess<String>()) {
        scope.fork(() -> mirror1.fetch(resourceId));
        scope.fork(() -> mirror2.fetch(resourceId));
        scope.fork(() -> mirror3.fetch(resourceId));

        scope.join();
        return scope.result();  // Returns the first successful result
    }
}
```

> [!IMPORTANT]
> Structured concurrency is a **preview feature** in Java 21. Enable with `--enable-preview` flag. API may change in future releases.

---

## 7. Enhanced Switch Expressions

### Arrow Syntax

```java
// ✅ Arrow syntax — no fall-through, can return values
String label = switch (status) {
    case PENDING   -> "⏳ Pending";
    case APPROVED  -> "✅ Approved";
    case REJECTED  -> "❌ Rejected";
    case CANCELLED -> "🚫 Cancelled";
};
```

### Exhaustiveness Checking

```java
// ✅ Compiler enforces all enum values are handled
// Adding a new enum constant forces a compilation error here
public BigDecimal calculateDiscount(CustomerTier tier) {
    return switch (tier) {
        case BRONZE   -> new BigDecimal("0.05");
        case SILVER   -> new BigDecimal("0.10");
        case GOLD     -> new BigDecimal("0.15");
        case PLATINUM -> new BigDecimal("0.20");
        // No default — compiler verifies exhaustiveness for enums
    };
}
```

### Multi-line Switch Arms with `yield`

```java
String description = switch (httpStatus) {
    case 200 -> "OK";
    case 404 -> "Not Found";
    case 500 -> {
        log.error("Internal server error encountered");
        alertService.notifyOps("HTTP 500 detected");
        yield "Internal Server Error";
    }
    default -> "Unknown status: " + httpStatus;
};
```

### Guard Patterns in Switch

```java
// ✅ Combine type patterns with guard conditions
public String evaluate(Object input) {
    return switch (input) {
        case String s when s.isBlank()    -> "Empty string";
        case String s when s.length() > 100 -> "Long string: " + s.substring(0, 100) + "...";
        case String s                     -> "String: " + s;
        case Integer i when i < 0         -> "Negative: " + i;
        case Integer i                    -> "Number: " + i;
        case null                         -> "Null value";
        default                           -> "Unknown: " + input;
    };
}
```

> [!TIP]
> Prefer switch expressions over if-else chains when branching on type or value. The compiler's exhaustiveness checking catches missing cases at compile time, not runtime.
