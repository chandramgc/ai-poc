# Spring Boot Architecture & Code Examples Reference

This reference details the Spring Boot 3.x layering guidelines, DI constraints, transactional policies, and clean code implementation templates.

---

## 1. Spring Boot Layer Guidelines

### ✅ Dependency Injection (DI)
- Field-level `@Autowired` is prohibited. Always inject dependencies through final fields and constructor parameters.
- Single-constructor beans do not require the `@Autowired` annotation (Spring auto-detects).
- Configuration properties use `@ConfigurationProperties` + `@EnableConfigurationProperties` for type-safe config binding.

### ✅ REST Layer (`@RestController`)
- Controllers are **thin** — no business logic or database calls are allowed.
- All response types wrapped in `ResponseEntity<T>` for HTTP status control.
- All request parameters annotated with `@Valid` to enforce validation constraints.
- Request/response use **DTOs**, not `@Entity` classes directly to prevent ORM leakage.
- A single `@RestControllerAdvice` handles exceptions project-wide.
- No `@RequestMapping` at method level — use specific shortcut annotations.

### ✅ Service Layer (`@Service`)
- Service interfaces defined; implementations contain the business logic.
- `@Transactional` only on service methods — **never** on controllers or repositories.
- `@Transactional(readOnly = true)` on read-only operations for performance.

### ✅ Data Layer (`@Repository` / Spring Data JPA)
- All repositories extend `JpaRepository<Entity, ID>`.
- Use lazy mapping (`FetchType.LAZY`) on all entity relationships.
- Secrets and credentials must reside in `application.yml` via `${ENV_VAR}` placeholders.

---

## 2. Code Templates

### Constructor Injection (DI)
```java
@Service
public class OrderService {
    private final OrderRepository repository;
    private final NotificationService notificationService;

    // ✅ Constructor injection — no @Autowired needed (single constructor)
    public OrderService(OrderRepository repository,
                        NotificationService notificationService) {
        this.repository = Objects.requireNonNull(repository);
        this.notificationService = Objects.requireNonNull(notificationService);
    }
}
```

### Thin Controller
```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<OrderResponse> create(@Valid @RequestBody OrderRequest request) {
        // ✅ Delegate immediately — no logic here
        OrderResponse response = orderService.createOrder(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
```

### Global Exception Handler (Advice)
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(OrderNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(OrderNotFoundException ex) {
        log.warn("Order not found: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse("NOT_FOUND", ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(new ErrorResponse("VALIDATION_FAILED", message));
    }
}
```

### slice Controller Test (WebMvcTest)
```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void createOrder_whenValidRequest_returnsCreated() throws Exception {
        when(orderService.createOrder(any())).thenReturn(new OrderResponse("123"));

        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId": "P1", "quantity": 2}""")
            )
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.orderId").value("123"));
    }
}
```
