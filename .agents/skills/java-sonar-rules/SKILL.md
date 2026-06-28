---
name: java-sonar-rules
description: >
  Audits Java source files against SonarQube (self-hosted) quality rules and Java best practices.
  Generates a structured report of violations, severity levels, and actionable remediation guidance.
  Trigger this skill whenever a user asks to review Java code quality, check Sonar compliance,
  identify code smells, security hotspots, or Java best-practice violations.
---

# Java SonarQube Rules & Best Practices Skill

## Overview

This skill audits Java code and produces a structured quality report aligned with:
- **SonarQube (self-hosted)** — SQALE model severity levels (Blocker → Info)
- **SonarJava rule set** — the canonical Java analyzer used by SonarQube
- **Spring Boot 3.x best practices** — dependency injection, REST layer, data layer, testing slices
- **Java best practices** — modern Java (17–21) idioms, Clean Code, and SOLID principles

---

## How to Use This Skill

When activated, perform the following steps in order:

### Step 1 — Identify Scope
Determine what to audit:
- A single file, a package, or the entire `src/` tree
- If the user says "review my code", default to all modified/new `.java` files

### Step 2 — Run Static Analysis (if tooling available)
If SonarQube CLI (`sonar-scanner`) or SonarLint is available in the project:
```bash
# From project root — requires sonar-project.properties
./gradlew clean build jacocoTestReport sonar \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=$SONAR_TOKEN
```
If not available, perform manual review using the rules below.

### Step 3 — Generate the Report
Produce a **Sonar Quality Report** using the format defined in `references/REPORT_TEMPLATE.md`.

### Step 4 — Prioritize Fixes
Triage by SQALE severity:
1. **BLOCKER** — Must fix before merge
2. **CRITICAL** — Must fix before release
3. **MAJOR** — Should fix in the same sprint
4. **MINOR** — Fix in next sprint
5. **INFO** — Note only; non-blocking

---

## SonarJava Rule Categories

### 🔴 BLOCKER Rules (Zero Tolerance)

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `S2068` | Hard-coded credentials | Never embed passwords, tokens, API keys in source code |
| `S106`  | Standard outputs | Do not use `System.out.println` — use SLF4J logger |
| `S2095` | Resources closed | All `Closeable` resources must be in try-with-resources |
| `S2259` | Null dereference | Check for null before dereferencing; use `Optional` |
| `S3329` | IV reuse in crypto | Never reuse IVs in encryption; use secure random |
| `S4818` | Sockets | Avoid raw socket usage without security controls |
| `S2755` | XML external entities | Disable XXE in XML parsers |

### 🔴 CRITICAL Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `S1168` | Return empty, not null | Return `Collections.emptyList()` not `null` for collections |
| `S2166` | Comparison of classes | Use `.equals()` not `==` for object comparison |
| `S1764` | Identical expressions | Avoid `a == a` or `x && x` — likely a bug |
| `S2583` | Conditions always true/false | Remove dead conditions that can never change |
| `S1186` | Empty methods | All methods must have a body or a `// intentionally empty` comment |
| `S112`  | Raw exception types | Never `throw new Exception()` — use specific exceptions |
| `S2077` | SQL injection | Use prepared statements, never string-concatenated SQL |
| `S5131` | Reflected XSS | Sanitize all user input before writing to response |

### 🟡 MAJOR Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `S1066` | Merging if-else | Collapse nested `if` with same condition |
| `S1135` | TODO comments | Replace `TODO` with a tracked issue before merge |
| `S1192` | String literal duplication | Extract repeated string literals to constants |
| `S1481` | Unused local variables | Remove all declared but unused variables |
| `S1172` | Unused method parameters | Remove unused parameters or mark `@SuppressWarnings` with justification |
| `S3776` | Cognitive complexity | Method cognitive complexity must stay ≤ 15 |
| `S107`  | Too many parameters | Methods must have ≤ 7 parameters; use a parameter object |
| `S138`  | Too many lines in method | Methods must be ≤ 60 lines |
| `S1118` | Utility class constructor | Utility classes must have a private constructor |
| `S2157` | Cloneable usage | Prefer copy constructors over `Cloneable` |
| `S1144` | Unused private methods | Remove or expose unused private methods |
| `S4144` | Duplicate method implementation | Extract duplicated method bodies to a shared method |

### 🟢 MINOR Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `S1125` | Avoid unnecessary boolean literals | Use `return condition` not `return condition == true` |
| `S1155` | Use `isEmpty()` | Use `collection.isEmpty()` not `collection.size() == 0` |
| `S1596` | `Collections.EMPTY_LIST` usage | Prefer `Collections.emptyList()` (type-safe) |
| `S2293` | Diamond operator | Use `<>` instead of explicit type in generics (Java 7+) |
| `S1117` | Variable shadowing | Local variable must not shadow a field name |
| `S1149` | Synchronized classes | Prefer `java.util.concurrent` over `synchronized` blocks |

### ☕ Spring Boot — Additional Sonar Rules

| Rule ID | Rule Name | Description |
|---------|-----------|-------------|
| `S6813` | Field injection (`@Autowired`) | Use constructor injection — field injection breaks testability and immutability |
| `S6810` | `@Autowired` unnecessary | Remove `@Autowired` on single-constructor beans (Spring auto-detects) |
| `S6821` | `@Transactional` on interface | Place `@Transactional` on the implementation class, not the interface |
| `S6809` | `@Controller` without mapping | Every `@Controller` method must have an `@RequestMapping` or shortcut annotation |
| `S2699` | Assertion in tests | All `@Test` methods in `@SpringBootTest` must have at least one assertion |
| `S5976` | Parameterized tests | Replace duplicate test methods with `@ParameterizedTest` |
| `S6830` | Missing `@Valid` | Request body parameters must be annotated with `@Valid` for Bean Validation to activate |

---

## Java Best Practices Checklist

When reviewing Java code, verify ALL of the following:

### ✅ Naming & Structure
- [ ] Classes use **PascalCase** (e.g., `OrderService`)
- [ ] Methods and variables use **camelCase** (e.g., `getUserById`)
- [ ] Constants use **SCREAMING_SNAKE_CASE** (e.g., `MAX_RETRY_COUNT`)
- [ ] Package names are all **lowercase** with reverse domain (e.g., `com.company.feature`)
- [ ] Test classes are named `ClassNameTest` or `ClassNameIT` (integration)

### ✅ Clean Code
- [ ] Every public class and method has a **Javadoc** comment
- [ ] Methods do **one thing** (Single Responsibility Principle)
- [ ] Method length is **≤ 60 lines**; prefer ≤ 30
- [ ] No magic numbers — all literals are named constants
- [ ] No commented-out dead code in committed files
- [ ] No `TODO` or `FIXME` without a linked issue number

### ✅ OOP & SOLID
- [ ] Prefer **interfaces** over concrete types in method signatures
- [ ] Classes are **closed for modification, open for extension** (Open/Closed Principle)
- [ ] No God classes (> 500 lines or > 20 methods)
- [ ] Dependencies are **injected**, not instantiated with `new` inside logic
- [ ] Use **factory methods** or builders for complex object construction

### ✅ Exception Handling
- [ ] Never catch `Exception` or `Throwable` unless re-throwing
- [ ] Never swallow exceptions silently (empty catch blocks are BLOCKER)
- [ ] Always log exceptions with **full stack trace** at ERROR level
- [ ] Use **custom checked exceptions** for business-rule violations
- [ ] Use **unchecked exceptions** (RuntimeException subclasses) for programming errors
- [ ] Clean up resources in `finally` or use **try-with-resources**

### ✅ Logging (SLF4J Standard)
- [ ] Use `private static final Logger log = LoggerFactory.getLogger(ClassName.class)`
- [ ] Use **parameterized logging** `log.debug("Processing user {}", userId)` — never string concat
- [ ] Log at correct levels: ERROR (failures), WARN (degraded), INFO (milestones), DEBUG (detail)
- [ ] Never log sensitive data (passwords, tokens, PII)
- [ ] Do not use `System.out` or `System.err` — BLOCKER rule S106

### ✅ Collections & Streams
- [ ] Prefer `List.of()`, `Map.of()`, `Set.of()` for immutable collections (Java 9+)
- [ ] Use **streams** for transformations; avoid imperative loops for filtering/mapping
- [ ] Always handle empty `Optional` — never call `.get()` without `.isPresent()` check
- [ ] Return `Optional<T>` instead of `null` for methods that may have no result
- [ ] Prefer `computeIfAbsent` over `containsKey` + `put` pattern on maps

### ✅ Concurrency
- [ ] Prefer `java.util.concurrent` types (`ConcurrentHashMap`, `AtomicInteger`) over `synchronized`
- [ ] Never use `Thread.sleep()` in production logic
- [ ] Always name threads or use a named `ThreadFactory`
- [ ] Use `CompletableFuture` for async flows
- [ ] Immutable objects do not need synchronization — prefer immutability

### ✅ Testing
- [ ] Use **JUnit 5** (`@Test`, `@BeforeEach`, `@ExtendWith`)
- [ ] Use **Mockito** for mocking dependencies
- [ ] Test method names follow `methodName_stateUnderTest_expectedBehavior` pattern
- [ ] Every public method has at least one happy-path and one edge-case test
- [ ] Use **AssertJ** fluent assertions over `assertTrue`/`assertEquals`
- [ ] Code coverage on new code must be **≥ 80%** (Sonar quality gate)

### ✅ Security (OWASP Top 10 for Java)
- [ ] All user inputs are **validated and sanitized** before use
- [ ] SQL queries use **PreparedStatement** or an ORM — never string concat
- [ ] Secrets come from **environment variables or a secrets manager** — never hardcoded
- [ ] Serialize only trusted data; use `serialVersionUID` and review `readObject`
- [ ] HTTP clients set connection and read timeouts
- [ ] Use `SecureRandom` not `Random` for security-sensitive values

---

## Spring Boot Best Practices Checklist

In addition to the core Java checklist above, verify all Spring Boot-specific rules:

### ✅ Dependency Injection
- [ ] All beans use **constructor injection** — no `@Autowired` on fields
- [ ] Single-constructor beans have **no `@Autowired`** annotation (Spring 4.3+ auto-detects)
- [ ] `@Component`, `@Service`, `@Repository`, `@Controller` annotations are on the correct layer
- [ ] No `new` instantiation of Spring-managed beans inside other beans
- [ ] Configuration properties use `@ConfigurationProperties` + `@EnableConfigurationProperties` for type-safe config binding

### ✅ REST Layer (`@RestController`)
- [ ] Controllers are **thin** — no business logic, no repository calls
- [ ] All response types wrapped in `ResponseEntity<T>` for explicit HTTP status control
- [ ] All request body parameters annotated with `@Valid` (activates Bean Validation)
- [ ] Request/response use **DTOs**, not `@Entity` classes directly (prevents over-fetching, ORM leakage)
- [ ] A single `@RestControllerAdvice` handles all exceptions and maps them to HTTP status codes
- [ ] API endpoints documented with **SpringDoc OpenAPI** (`@Operation`, `@ApiResponse`)
- [ ] No `@RequestMapping` at method level — use specific `@GetMapping`, `@PostMapping`, etc.

### ✅ Service Layer (`@Service`)
- [ ] Service interfaces defined; implementation class is a separate `@Service`-annotated class
- [ ] `@Transactional` only on service methods — **never** on controllers or repositories
- [ ] `@Transactional(readOnly = true)` on all read-only service methods (performance)
- [ ] No `@Transactional` on `private` methods (Spring AOP proxy won't intercept them)
- [ ] Business exceptions thrown as unchecked `RuntimeException` subclasses

### ✅ Data Layer (`@Repository` / Spring Data JPA)
- [ ] All repositories extend `JpaRepository<Entity, ID>` or `CrudRepository`
- [ ] No raw `EntityManager` or native SQL unless performance-critical (and documented)
- [ ] Named queries use Spring Data JPA method naming or `@Query` with JPQL (not native SQL unless required)
- [ ] Entities have `@Entity`, `@Table`, `@Id`, `@GeneratedValue` correctly configured
- [ ] No `FetchType.EAGER` on relationships — use `LAZY` with explicit join fetches
- [ ] Database secrets always in `application.yml` via `${ENV_VAR}` placeholders, never hardcoded

### ✅ Configuration (`application.yml`)
- [ ] Secrets and credentials reference environment variables: `password: ${DB_PASSWORD}`
- [ ] Spring profiles used for environment differences (`dev`, `prod`) — no if/else in code
- [ ] `application.yml` base config has no environment-specific values
- [ ] Actuator endpoints restricted: only `/health` and `/info` exposed publicly in production
- [ ] `@ConfigurationProperties` classes have `@Validated` for startup-time validation

### ✅ Spring Boot Testing
- [ ] **Unit tests** use `@ExtendWith(MockitoExtension.class)` — no Spring context loaded
- [ ] **Controller tests** use `@WebMvcTest(ControllerClass.class)` — only web layer loaded
- [ ] **Repository tests** use `@DataJpaTest` — only JPA layer loaded (H2 in-memory)
- [ ] **Integration tests** use `@SpringBootTest` + `@AutoConfigureMockMvc` for full-context
- [ ] `MockMvc` used to test HTTP endpoints; asserts status code, response body, and headers
- [ ] No production `@SpringBootTest` for tests that only need a single unit — use slices
- [ ] Test configuration in `src/test/resources/application-test.yml`

### ✅ Example Patterns

**Constructor Injection (mandatory):**
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

**Thin Controller (mandatory):**
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

**Global Exception Handler (mandatory):**
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

**@WebMvcTest slice test:**
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

---

## Report Output Format

When generating a report, use this structure:

```markdown
# Java Sonar Quality Report
**Generated**: <date>
**Scope**: <file/package/project>
**Sonar Host**: http://localhost:9000 (self-hosted)

## Summary
| Severity | Count |
|----------|-------|
| 🔴 BLOCKER  | X |
| 🔴 CRITICAL | X |
| 🟡 MAJOR    | X |
| 🟢 MINOR    | X |
| ℹ️ INFO     | X |

## Issues

### [BLOCKER] S2068 — Hard-coded credentials
**File**: `src/main/java/com/example/Config.java:42`
**Code**:
```java
String password = "admin123"; // ❌ hard-coded
```
**Fix**:
```java
String password = System.getenv("DB_PASSWORD"); // ✅
```

---

## Best Practice Violations
- [ ] Missing Javadoc on `OrderService.processOrder()` [MAJOR]
- [ ] `System.out.println` in `DataLoader.java:77` [BLOCKER — S106]

## Quality Gate Status
- [ ] PASS / ❌ FAIL
- Coverage: X% (threshold: 80%)
- Duplications: X% (threshold: 3%)
- New Blocker Issues: X (threshold: 0)
```

---

## References

- [SonarJava Rules Explorer](https://rules.sonarsource.com/java/)
- [SonarQube Quality Gates docs](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/)
- [OWASP Top 10 for Java](https://owasp.org/www-project-top-ten/)
- [Spring Boot 3.x Reference](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Spring Boot Testing Guide](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
- [Effective Java (Bloch) — key rules](references/effective-java-rules.md)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Java Best Practices reference sheet](references/java-best-practices.md)
