# Java Best Practices — Quick Reference Sheet

A condensed, opinionated reference for writing production-quality Java code
aligned with SonarQube, Google Style Guide, and SOLID principles.

---

## 1. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Class / Interface | PascalCase | `OrderService`, `Payable` |
| Method / Variable | camelCase | `getUserById`, `isActive` |
| Constant (`static final`) | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Package | lowercase, reverse domain | `com.acme.order.service` |
| Test class | Suffix `Test` or `IT` | `OrderServiceTest` |
| Test method | `method_state_expected` | `save_whenNullInput_throwsException` |

---

## 2. Class Design

```java
// ✅ Good class structure order (per Google Java Style Guide)
public final class OrderService {

    // 1. Static constants
    private static final int MAX_ITEMS = 100;

    // 2. Static fields
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);

    // 3. Instance fields
    private final OrderRepository repository;

    // 4. Constructors
    public OrderService(OrderRepository repository) {
        this.repository = Objects.requireNonNull(repository, "repository must not be null");
    }

    // 5. Static factory methods (if any)
    // 6. Public methods
    // 7. Package-private / protected methods
    // 8. Private methods
    // 9. Equals, hashCode, toString
}
```

---

## 3. Logging Pattern

```java
// ✅ Standard SLF4J pattern
private static final Logger log = LoggerFactory.getLogger(MyClass.class);

// ✅ Parameterized — never string concat
log.debug("Processing order id={} for user={}", orderId, userId);
log.info("Order {} completed in {}ms", orderId, elapsed);
log.warn("Retry attempt {} for order {}", attempt, orderId);
log.error("Failed to process order {}", orderId, exception); // pass exception as last arg

// ❌ Avoid — always evaluated, even when DEBUG is off
log.debug("Order: " + order.toString());

// ✅ Guard expensive string operations
if (log.isDebugEnabled()) {
    log.debug("Full payload: {}", buildDetailedPayload(order));
}
```

---

## 4. Exception Handling

```java
// ✅ Business exception — checked
public class OrderNotFoundException extends Exception {
    public OrderNotFoundException(String orderId) {
        super("Order not found: " + orderId);
    }
}

// ✅ Programming error — unchecked
public class InvalidStateException extends RuntimeException {
    public InvalidStateException(String message) {
        super(message);
    }
}

// ✅ Proper catch — never swallow
try {
    processOrder(order);
} catch (OrderNotFoundException e) {
    log.warn("Order not found, skipping: {}", e.getMessage());
    throw e;                   // re-throw after logging
} catch (Exception e) {
    log.error("Unexpected error processing order {}", orderId, e);
    throw new ServiceException("Order processing failed", e);  // wrap
}

// ❌ Never do this
try {
    processOrder(order);
} catch (Exception e) {
    // silent swallow — BLOCKER in Sonar
}
```

---

## 5. Optional Usage

```java
// ✅ Return Optional instead of null
public Optional<User> findById(String id) {
    return Optional.ofNullable(repository.findById(id));
}

// ✅ Consumer side — safe access
userService.findById(id)
    .map(User::getEmail)
    .ifPresentOrElse(
        email -> sendNotification(email),
        () -> log.warn("User {} not found for notification", id)
    );

// ❌ Never call .get() without guard
Optional<User> user = findById(id);
user.get().getEmail();  // throws NoSuchElementException — Sonar flags this

// ❌ Never use Optional as a field or parameter type
private Optional<String> name; // anti-pattern
```

---

## 6. Collections

```java
// ✅ Immutable (Java 9+) — prefer these for read-only data
List<String> roles = List.of("ADMIN", "USER");
Map<String, Integer> codes = Map.of("OK", 200, "NOT_FOUND", 404);
Set<String> tags = Set.of("java", "sonar");

// ✅ Mutable when you need to add/remove
List<Order> orders = new ArrayList<>();
Map<String, User> cache = new HashMap<>();

// ✅ Use isEmpty() not size() == 0
if (orders.isEmpty()) { ... }         // ✅ Sonar S1155
if (orders.size() == 0) { ... }       // ❌ Sonar S1155

// ✅ Stream for transformations
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .sorted()
    .collect(Collectors.toList());
```

---

## 7. Null Safety

```java
// ✅ Validate method arguments early
public void save(Order order) {
    Objects.requireNonNull(order, "order must not be null");
    Objects.requireNonNull(order.getId(), "order.id must not be null");
    // ...
}

// ✅ Use @NonNull / @Nullable annotations (Lombok or Jakarta)
public void process(@NonNull String id, @Nullable String note) { ... }

// ✅ String null-safe comparison
"expected".equals(actual);          // safe — won't NPE if actual is null
actual.equals("expected");          // ❌ NPE if actual is null
Objects.equals(actual, "expected"); // ✅ null-safe both ways
```

---

## 8. Concurrency

```java
// ✅ Prefer concurrent collections
Map<String, Session> sessions = new ConcurrentHashMap<>();

// ✅ AtomicInteger over synchronized int
private final AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();

// ✅ CompletableFuture for async
CompletableFuture<Order> future = CompletableFuture
    .supplyAsync(() -> fetchOrder(id), executor)
    .thenApply(this::enrich)
    .exceptionally(ex -> {
        log.error("Order fetch failed", ex);
        return Order.empty();
    });

// ❌ Avoid raw synchronized blocks
synchronized (this) { ... }  // use java.util.concurrent instead
```

---

## 9. Builder Pattern (complex objects)

```java
// ✅ Use builder for objects with > 4 fields (or Lombok @Builder)
Order order = Order.builder()
    .id(UUID.randomUUID().toString())
    .userId(userId)
    .items(items)
    .status(OrderStatus.PENDING)
    .createdAt(Instant.now())
    .build();
```

---

## 10. Testing Standards (JUnit 5 + AssertJ + Mockito)

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository repository;

    @InjectMocks
    private OrderService orderService;

    @Test
    void processOrder_whenValidOrder_returnsConfirmation() {
        // Arrange
        Order order = Order.builder().id("123").build();
        when(repository.save(any(Order.class))).thenReturn(order);

        // Act
        OrderConfirmation result = orderService.processOrder(order);

        // Assert
        assertThat(result).isNotNull();
        assertThat(result.getOrderId()).isEqualTo("123");
        verify(repository).save(order);
    }

    @Test
    void processOrder_whenNullOrder_throwsException() {
        assertThatThrownBy(() -> orderService.processOrder(null))
            .isInstanceOf(NullPointerException.class)
            .hasMessageContaining("order must not be null");
    }
}
```

---

## Sonar Quality Gate Thresholds (self-hosted defaults)

| Metric | Threshold |
|--------|-----------|
| New Code Coverage | ≥ 80% |
| New Duplications | ≤ 3% |
| New Blocker Issues | 0 |
| New Critical Issues | 0 |
| New Code Smells Debt | ≤ 5 days |
| Cognitive Complexity (per method) | ≤ 15 |
| Lines per Method | ≤ 60 |
| Parameters per Method | ≤ 7 |
