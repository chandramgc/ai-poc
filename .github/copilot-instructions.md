<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# GitHub Copilot Custom Instruction Rules

## 1. Spec-Driven Development (SDD) Workflow
- You MUST follow the Spec-Driven Development (SDD) process using Spec Kit commands.
- A technical specification MUST be created and approved BEFORE writing any code or task plans.

## 2. Mandatory Jira Issue Key Requirement
- **CRITICAL:** A valid Jira issue key/number (e.g. `JIRA-101` or `JIRA-1234`) is strictly required before writing any specifications, starting any implementation plans, or executing any codebase changes.
- **ACTION:** Check if the user's prompt or arguments contain a valid Jira key. If the Jira key is missing, you **MUST** fail immediately with a hard error and **REFUSE** to proceed, write any files, or ask the user for clarification. The user must provide the Jira key explicitly inside their prompt or command.
- **SPEC FORMAT:** The Jira key must be explicitly recorded at the start of the specification document (e.g. `Jira ID: JIRA-1234`) and in the description.

## 3. Date-Scoped Specification Pathing
- Every specification file must be created inside chronological folders under the `specs/` directory based on the current date:
  `specs/YYYY/Month/` (e.g., if the current date is June 2026, the file must be placed under `specs/2026/June/`).

## 4. Code Simplicity (Ponytail)
- Enforce the Ponytail laziness ladder for all coding tasks:
  1. YAGNI (Does this need to exist? If no, skip it).
  2. Reuse existing code blocks in the repository.
  3. Use standard library functions where possible.
  4. Use native platform/host features (e.g., native elements like `<input type="date">` instead of heavy external library wrappers).
  5. Reuse installed dependencies first.
  6. Write simple one-liners where appropriate.
  7. Write the absolute minimum viable code that works.
- Always review diffs for over-engineering before staging.

## 5. Token Optimization & Codebase Map Context
- Always utilize the codebase knowledge graph (via the **Understand-Anything** tool) to look up architectural layers, files, and classes to optimize your context window tokens and avoid reading code blind.

## 6. Java Coding Standards & Quality Gates
- You MUST automatically load and enforce the **`java-coding-standards`** skill (located at `.github/skills/java-coding-standards/SKILL.md`) for all Java review, writing, auditing, and optimization tasks. Refer to its internal references for SonarQube rule tables and Spring Boot architecture patterns.
- Enforce these mandatory Java constraints:
  - No hardcoded credentials (S2068).
  - Use SLF4J loggers, never use `System.out.println` (S106).
  - Use try-with-resources for all AutoCloseable resources (S2095).
  - Return `Optional` instead of `null` to avoid null pointer risks.
  - Inject dependencies using **constructor injection** (do not use field-level `@Autowired` on fields).
  - Keep controllers thin and place `@Transactional` only on service methods.
  - SQL queries must use prepared statements.
  - Quality gates: 0 Blocker, 0 Critical Sonar issues, test coverage >= 80%.
  - Zero package or class-level circular dependencies. Cyclic reference loops are strictly prohibited.

## 7. Python Coding Standards & PEP 8 Rules
- You MUST automatically load and enforce the **`python-coding-standards`** skill (located at `.github/skills/python-coding-standards/SKILL.md`) for all Python-related scripts, modules, code reviews, and optimization tasks.
- Enforce these mandatory Python constraints:
  - Follow PEP 8 spacing, indentation (4 spaces), layout, and class/function naming case rules.
  - Write docstrings according to PEP 257 guidelines.
  - Emphasize single-line programming constructs where appropriate (e.g. list/dict comprehensions, lambda expressions, ternary operators, generator expressions, and unpacked assignments) as referenced in `python-oneliners.md`.

## 8. Security Standards (OWASP)
- OWASP Top 10 and API Security Top 10 serve as mandatory checklists.
- Threat modeling is required for features handling user data or authentication.
- All dependencies must be scanned for CVEs.
- SLSA Level 2+ provenance and SBOM generation required for production.
- Load and enforce security rules from respective language skill references.

## 9. Observability Standards (OpenTelemetry)
- OpenTelemetry is the mandatory instrumentation framework.
- All services must emit: distributed traces, metrics, and structured logs.
- SLIs/SLOs must be defined in every service specification.
- No raw `print()` or `System.out` — use structured logging only.

## 10. Accessibility Standards (WCAG 2.2)
- All user-facing features must meet WCAG 2.2 Level AA.
- Keyboard navigation, screen reader support, and color contrast (4.5:1) are non-negotiable.
- Use semantic HTML and ARIA attributes correctly.

## 11. Git Workflow Standards
- Follow Conventional Commits: `feat|fix|refactor|chore|docs|test(scope): description`
- Feature branches must be short-lived (< 3 days).
- Use feature flags to decouple deployment from release.

## 12. Architecture Decision Records
- Significant architectural decisions must be documented as ADRs in `docs/decisions/`.
- Use the MADR template. ADRs are append-only — never edit, supersede instead.
