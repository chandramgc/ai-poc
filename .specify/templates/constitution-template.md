# [PROJECT_NAME] Constitution

This document sets the non-negotiable architectural principles, quality gates, and governance constraints for the [PROJECT_NAME] project. All designs, plans, and code implementations must align with this constitution.

---

## Core Principles

### I. Spec-Driven Development (SDD)
Every new feature, bug fix, or component enhancement must begin with an executable specification created via Spec Kit commands (`/speckit.*`), including `clarify`, `checklist`, and `analyze` commands for requirement refinement and consistency checks. Tasks planning or coding is prohibited until the specification is finalized and approved.

### II. Strict Jira Issue Alignment
- Every feature folder, git branch, task list, and commit must start with or reference a valid Jira issue number (e.g. `JIRA-1234`).
- **Zero-tolerance validation check:** If a Jira issue key is missing from the input, all generation commands must abort immediately with a hard error.

### III. Date-Scoped Chronological Paths
- Specifications, implementation plans, and related design documents must be stored inside chronological folders under the `specs/` directory:
  `specs/YYYY/Month/<jira-number>-<short-name>/` (e.g., `specs/2026/June/JIRA-101-user-auth/`).

### IV. Simplicity First & The Laziness Ladder
All coding processes must adhere to the Ponytail simplicity guidelines, evaluating proposals top-down using the 7-step Laziness Ladder:
1. **YAGNI:** Does this need to exist? If not, skip it.
2. **Reuse:** Leverage existing codebase components rather than re-implementing.
3. **Stdlib:** Prefer native language standard libraries.
4. **Native platform:** Use native web/host features (e.g. native HTML5 tags) before adding heavy dependencies.
5. **Existing dependencies:** Reuse imported packages.
6. **One-line solutions:** Keep statements short and direct.
7. **Absolute minimum:** Write the minimal viable code that fulfills the requirement.

> **Exception:** Security measures, input validation, error handling, and accessibility must never be simplified or skipped regardless of the laziness ladder.

### V. Codebase Graph & Token Optimization
Leverage the codebase map and interactive knowledge graph (via the Understand-Anything tool) to perform dependency reviews and optimize token contexts before writing code or plans.

### VI. Security-First Development
- OWASP Top 10 and API Security Top 10 are mandatory checklists during spec/design.
- Threat modeling required for features handling user data or authentication.
- All dependencies scanned for CVEs in CI ([SCANNING_TOOL]).
- No hardcoded secrets — environment variables or vault only.
- SQL injection prevention: parameterized queries only.
- SLSA Level 2+ provenance required for production artifacts.
- SBOM ([SBOM_FORMAT]) auto-generated in CI pipeline.

### VII. Observability Standards
- [OBSERVABILITY_FRAMEWORK] is the mandatory instrumentation framework.
- All services must emit: traces (distributed), metrics (counters/histograms), structured logs.
- SLIs/SLOs must be defined in every service spec (availability, latency, error budget).
- Semantic Conventions must use standard attributes.
- Cardinality control: no high-cardinality metric labels.

### VIII. API-First Design
- APIs designed before implementation using [API_SPEC_FORMAT] specifications.
- Contract testing validates spec-code alignment in CI.
- Breaking changes require a new API version and ADR.
- HATEOAS for REST; schema-first for GraphQL.

### IX. Accessibility Compliance
- All user-facing features must meet [ACCESSIBILITY_STANDARD].
- POUR principles (Perceivable, Operable, Understandable, Robust) guide all UI decisions.
- Accessibility testing integrated into CI ([A11Y_TESTING_TOOL]).
- Keyboard navigation, screen reader support, and color contrast are non-negotiable.

### X. Data Privacy & Compliance
- [PRIVACY_REGULATIONS] compliance by design.
- Personal data processing requires documented lawful basis.
- Data classification labels required for all data stores.
- Privacy code scanning integrated into CI/CD pipeline.
- Data retention policies defined per entity.

### XI. AI-Generated Code Guardrails
- All AI-generated code must pass the same quality gates as human code.
- AI agents must follow the constitution — no exceptions.
- Human-in-the-loop review required for security-critical or data-handling code.
- AI code inventory: track which code was AI-generated via commit metadata.

### XII. Git Workflow Standards
- Conventional Commits required: `feat|fix|refactor|chore|docs|test(scope): description`
- [GIT_BRANCHING_STRATEGY]: feature branches < [MAX_BRANCH_DAYS] days.
- Feature flags decouple deployment from release.
- All CI actions pinned by full SHA (not tags).
- Artifact signing before deployment.

### XIII. Infrastructure as Code
- All infrastructure defined in code ([IAC_TOOL]).
- Zero ClickOps for production environments.
- [POLICY_ENGINE] validates IaC plans before apply.
- Remote state backend with locking; no state files in Git.
- IaC modules require automated tests.

### XIV. Dependency Management
- Dependencies pinned by exact version or SHA.
- Automated vulnerability scanning on every PR.
- Reachability analysis: prioritize CVEs where vulnerable function is actually called.
- License compliance checks in CI.
- [DEPENDENCY_REVIEW_CADENCE] dependency hygiene review.

---

## Coding & Quality Standards

### 1. [PRIMARY_LANGUAGE] Guidelines
- [PRIMARY_LANGUAGE_STANDARDS]

### 2. [SECONDARY_LANGUAGE] Guidelines
- [SECONDARY_LANGUAGE_STANDARDS]

---

## Governance

All Pull Requests, code reviews, and implementation cycles must be audited against this constitution. Version updates require documentation and team ratification.

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
