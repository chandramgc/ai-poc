# ai-poc

A Java project with spec-driven development, SonarQube quality enforcement, and AI-native tooling.

---

## Tech Stack

- **Language**: Java 17+
- **Framework**: Spring Boot 3.x
- **Build**: Gradle
- **Quality**: SonarQube (self-hosted)
- **Testing**: JUnit 5 + Mockito + AssertJ + Spring Boot Test (WebMvcTest / DataJpaTest / SpringBootTest)
- **Logging**: SLF4J + Logback (Spring Boot auto-configured)

---

## AI-Native Development

This project uses **Spec-Driven Development (SDD)** — specifications are the source of truth,
AI agents generate code against them.

| Tool | Purpose |
|------|---------|
| `AGENTS.md` | Cross-agent behavioural rules |
| `.agents/skills/java-sonar-rules/` | Skill: Java quality report + Sonar rules |
| `sonar-project.properties` | SonarQube self-hosted config |

### Running the Java Sonar Rules Skill

Ask your AI agent:
> *"Review this Java file using the java-sonar-rules skill and generate a quality report."*

The skill will check all SonarJava rules (Blocker → Info) and Java best practices,
then produce a structured report with fixes.

---

## SonarQube Analysis

```bash
# Requires SonarQube running at http://localhost:9000
# Set your token:
export SONAR_TOKEN=<your-token>

# Run full analysis
./gradlew clean build jacocoTestReport sonar -Dsonar.token=$SONAR_TOKEN

# View results at:
open http://localhost:9000/dashboard?id=ai-poc
```

---

## Quality Gate Thresholds

| Metric | Threshold |
|--------|-----------|
| New Code Coverage | ≥ 80% |
| New Duplications | ≤ 3% |
| New Blocker Issues | 0 |
| New Critical Issues | 0 |

---

## Project Structure

```
src/main/java/       — Production Java code
src/test/java/       — JUnit 5 tests
docs/                — Project documentation
.agents/skills/      — AI agent skills
```