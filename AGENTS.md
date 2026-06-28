# AGENTS.md — AI Agent Guidance for ai-poc

This file provides persistent context and behavioural rules for all AI coding
agents (Antigravity, Cursor, GitHub Copilot, Claude, etc.) working in this repository.

---

## Project Overview

**Name**: ai-poc  
**Language**: Java (Java 17+)  
**Framework**: Spring Boot 3.x  
**Build Tool**: Gradle  
**Architecture**: Clean Architecture / Layered (controller → service → repository)  
**Quality Enforcement**: SonarQube (self-hosted, `http://localhost:9000`)  
**Test Framework**: JUnit 5 + Mockito + AssertJ + Spring Boot Test

---

## Mandatory Rules for All Agents

1. **Java only** — This project is Java. Do not generate Python, JavaScript, or any other language unless explicitly asked.
2. **Follow the `java-sonar-rules` skill** — Any code generation must pass the Sonar rules checklist defined in `.agents/skills/java-sonar-rules/SKILL.md`.
3. **No hardcoded secrets** — Sonar rule S2068 is a BLOCKER. Always use `application.yml` with `${ENV_VAR}` placeholders or Spring Cloud Config.
4. **No `System.out.println`** — Sonar rule S106 is a BLOCKER. Always use SLF4J logger (Spring Boot auto-configures Logback).
5. **Try-with-resources only** — Sonar rule S2095. All `Closeable` resources must use try-with-resources.
6. **Return `Optional`, not null** — For methods that may have no result, return `Optional<T>`.
7. **Javadoc on all public API** — Every `public` class and method must have a Javadoc comment.
8. **Constructor injection only** — Never use `@Autowired` on fields. Always inject via constructor (supports immutability + testability).
9. **Thin controllers** — `@RestController` classes must contain zero business logic. Delegate everything to `@Service`.
10. **Global exception handler** — Use a single `@RestControllerAdvice` class for all HTTP error responses. Never return raw exceptions.
11. **Bean Validation** — Annotate all request DTOs with `@Valid`; use `@NotNull`, `@NotBlank`, `@Size` constraints.
12. **No `@Transactional` on controllers** — Only `@Service` methods may be transactional.

---

## Build Commands

```bash
# Build
./gradlew build

# Compile only
./gradlew compileJava

# Run Spring Boot application locally
./gradlew bootRun

# Run tests
./gradlew test

# Run only integration tests (@SpringBootTest)
./gradlew integrationTest

# Run Sonar analysis (requires SONAR_TOKEN env var)
./gradlew sonar -Dsonar.token=$SONAR_TOKEN

# Generate coverage report (JaCoCo)
./gradlew jacocoTestReport

# Run Checkstyle
./gradlew checkstyleMain

# Full verify (compile + test + coverage + Sonar)
./gradlew clean build jacocoTestReport sonar

# Build production JAR
./gradlew bootJar
```

---

## Project Structure (expected)

```
src/
  main/
    java/
      com/example/
        controller/      # @RestController — thin, delegates to service
        service/         # @Service — business logic interfaces + implementations
        repository/      # @Repository — Spring Data JPA interfaces
        domain/          # @Entity — JPA entities and value objects
        dto/             # Request/Response POJOs with Bean Validation annotations
        config/          # @Configuration — Spring beans, security, CORS, etc.
        exception/       # Custom exceptions + @RestControllerAdvice handler
        util/            # Utility classes (private constructor, static methods only)
    resources/
      application.yml          # Base config (no secrets)
      application-dev.yml      # Dev profile overrides
      application-prod.yml     # Prod profile overrides
  test/
    java/
      com/example/
        controller/      # @WebMvcTest slice tests
        service/         # @ExtendWith(MockitoExtension) unit tests
        repository/      # @DataJpaTest slice tests
        integration/     # @SpringBootTest full-context tests
docs/
  SONAR_RULES.md         # Human-readable Sonar rule reference
.agents/
  skills/
    java-sonar-rules/    # AI skill for Sonar review and Java best practices
sonar-project.properties # SonarQube self-hosted configuration
```

---

## Coding Standards Summary

See full detail in `.agents/skills/java-sonar-rules/SKILL.md`.

| Area | Standard |
|------|---------|
| Naming | PascalCase classes, camelCase methods/vars, SCREAMING_SNAKE constants |
| Logging | SLF4J only, parameterized messages, no sensitive data |
| Exceptions | Specific types, never swallow, always log with stack trace |
| Collections | Use `List.of()`, `isEmpty()`, streams for transforms |
| Nulls | `Objects.requireNonNull()` for params, return `Optional` not null |
| Testing | JUnit 5 + Mockito + Spring Boot Test slices, ≥ 80% coverage on new code |
| Security | PreparedStatement, SecureRandom, `application.yml` env placeholders |
| Spring DI | Constructor injection only — no `@Autowired` fields |
| Spring Web | Thin `@RestController`, global `@RestControllerAdvice`, `@Valid` on DTOs |
| Spring Data | Spring Data JPA repositories only — no raw EntityManager unless essential |

---

## Safety Boundaries

**Never modify without explicit instruction:**
- `sonar-project.properties`
- `.agents/skills/java-sonar-rules/SKILL.md`
- `AGENTS.md` (this file)
- Any file under `.git/`

---

## Quality Gate (SonarQube self-hosted)

Before marking any task complete, verify:
- [ ] 0 new BLOCKER issues
- [ ] 0 new CRITICAL issues  
- [ ] New code coverage ≥ 80%
- [ ] Duplications ≤ 3%
- [ ] Cognitive complexity ≤ 15 per method

---

## Activated Skills

- **`java-sonar-rules`** — Use when reviewing Java code, checking quality, generating a Sonar report,
  or writing new Java features. Trigger automatically for any `.java` file change.
