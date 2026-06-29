---
name: java-coding-standards
description: >
  Main entry point for Java 17+ coding standards, Spring Boot architecture, SonarQube rules, and circular dependency validations.
  Trigger this skill automatically whenever a user asks to review Java design, check Sonar compliance,
  write services, controllers, exceptions, or tests, or inspect package-level dependency cycles.
---

# Java Coding Standards & Quality Gates

This skill enforces strict project-wide coding standards, quality gates, and Spring Boot practices. It organizes detailed rules and templates into modular reference sub-documents.

---

## 🧭 References Roadmap

To write compliant Java code, consult these dedicated reference files:

- 📊 **[SonarQube Quality Rules](references/java-sonar-rules.md):** Detailed SQALE Blocker, Critical, Major, and Minor rule tables (e.g. S2068, S106, S2095, S2259).
- ⚙️ **[Spring Boot Examples & Layering](references/spring-boot-examples.md):** Architecture guides and clean templates (constructor DI, thin controllers, exception advice, WebMvc slice tests).
- ☕ **[Effective Java (Bloch) Rules](references/effective-java-rules.md):** Best practices checklist adapted from Joshua Bloch's *Effective Java*.
- 📋 **[General Java Best Practices](references/java-best-practices.md):** Everyday cheat-sheet covering null safety, collections, stream processing, and secure variables.
- 🔐 **[Security & OWASP Rules](references/java-security-owasp.md):** OWASP Top 10 Java-specific rules, SAST/DAST tool integration, and secure coding patterns.
- 📡 **[Observability & Monitoring Patterns](references/java-observability.md):** Spring Boot Actuator, Micrometer metrics, and OpenTelemetry distributed tracing patterns.
- 🚀 **[Modern Java Features (21+)](references/java-modern-features.md):** Records, sealed classes, pattern matching, virtual threads, and structured concurrency patterns.

---

## 🛡️ Circular Dependency Prevention

> [!IMPORTANT]
> Directed cyclic dependency loops between packages or classes (e.g. Package A depending on Package B which depends on Package A) are strictly prohibited. Cycles indicate tight architectural coupling, break unit test boundaries, and block application startup.

### Codebase Validation Rules
1. **No Package Cycles:** Separate package boundaries cleanly. Use interfaces or spring event publication (`ApplicationEventPublisher`) to communicate between features.
2. **Spring Context Fail-Fast:** Constructor injection must be used to ensure any circular reference loop triggers a crash immediately at context startup. Keep circular references blocked in your configs:
   ```yaml
   spring:
     main:
       allow-circular-references: false
   ```

---

## ☕ General Coding standards Checklist

Ensure all Java modifications comply with these base standards:

- **Naming Conventions:** Use **PascalCase** for classes, **camelCase** for methods/variables, **SCREAMING_SNAKE_CASE** for constants, and reverse domain **lowercase** for package paths.
- **Clean Code:** Use Javadoc comments on public methods. Limit method size to &le; 60 lines. Eliminate magic numbers.
- **Null Safety:** Return `Optional<T>` instead of returning `null` for individual items. Use Collections helper methods (e.g. `Collections.emptyList()`) instead of returning `null` collections.
- **Logging:** Use SLF4J loggers. Use parameterized templates (e.g., `log.info("msg {}", arg)`) instead of string concatenation. Do not use `System.out.println` (S106 blocker).
- **Resources:** Always use try-with-resources blocks for closing open streams, readers, or connections (S2095 blocker).
- **Security:** Sanitize inputs, bind SQL variables to prepared statements (S2077 critical), and fetch credentials from environment variables (S2068 blocker).
