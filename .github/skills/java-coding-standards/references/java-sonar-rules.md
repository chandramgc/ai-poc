# Java SonarQube Rules Reference Guide

This reference details the static analysis quality gates, severity categories, and rule definitions for Java codebase audits.

---

## 1. Static Analysis Quality Gates

Before committing Java changes, verify compliance with these gates:
- **0 BLOCKER** issues
- **0 CRITICAL** issues
- **New Code Coverage:** &ge; 80%
- **Cognitive Complexity:** &le; 15 per method
- **No Duplicated Code**

Run verification locally:
```bash
./gradlew clean build jacocoTestReport sonar
```

---

## 2. SonarJava Rule Categories

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
| `S3776` | Cognitive complexity | Method cognitive complexity must stay &le; 15 |
| `S107`  | Too many parameters | Methods must have &le; 7 parameters; use a parameter object |
| `S138`  | Too many lines in method | Methods must be &le; 60 lines |
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

## 3. Report Output Format

When generating a Sonar compliance report, use this markdown structure:

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
```
