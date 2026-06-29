# Implementation Plan: [FEATURE]

**Jira ID**: `[JIRA_KEY]` | **Branch**: `[JIRA_KEY]-[feature-name]` | **Date**: [DATE] | **Spec**: [link to spec.md]

---

## 1. Summary & Architectural Approach

### Summary
[Extract primary requirement and functional boundaries from feature spec]

### Architectural & Design Decisions
[Describe the chosen design, patterns, and trade-offs made. E.g., why custom wrappers or specific database structures were chosen]

| Decision Point | Chosen Approach | Rationale | Alternatives Considered & Rejected |
|:---|:---|:---|:---|
| **Storage / DB** | [e.g. JPA Entity mapping] | [why it fits] | [e.g. JDBC templates - rejected for development speed] |
| **Logic Layer** | [e.g. Service Interface + Impl] | [why it fits] | [direct controller calls - rejected for layering violation] |

---

## 2. Technical Context

- **Language & Runtime:** [e.g., Java 17 / OpenJDK]
- **Primary Dependencies:** [e.g., Spring Boot Starter Web, JPA, Lombok]
- **Storage/DB Engine:** [e.g., PostgreSQL / H2 in-memory for tests]
- **Testing Slices:** [e.g., JUnit 5, Mockito, MockMvc]
- **Performance Targets:** [e.g., API response &le; 200ms p95]
- **Resource Constraints:** [e.g., zero package-level circular dependencies]

---

## 3. Constitution Gate Compliance

*GATE: Must pass before Phase 0 research. Re-verify post-design.*

| Governance Gate | Status | Justification / Notes |
|:---|:---|:---|
| **Spec-Driven Validation** | [PASS / FAIL] | [Spec exists and is approved] |
| **Jira Requirement** | [PASS / FAIL] | [Jira ID linked in folder prefix] |
| **Chronological Directory** | [PASS / FAIL] | [Created under specs/YYYY/Month/] |
| **Simplicity Guard (Ponytail)** | [PASS / FAIL] | [Followed laziness ladder] |
| **Java/Python Quality Rules** | [PASS / FAIL] | [Compliance with respective skill sets verified] |
| **Security-First** | [PASS / FAIL] | [OWASP compliance verified] |
| **Observability Standards** | [PASS / FAIL] | [OTel instrumentation planned] |
| **API-First Design** | [PASS / FAIL] | [OpenAPI spec created] |
| **Accessibility Compliance** | [PASS / FAIL] | [WCAG AA requirements identified] |
| **Data Privacy** | [PASS / FAIL] | [PII impact assessed] |
| **AI Code Guardrails** | [PASS / FAIL] | [AI-generated code review planned] |
| **Git Workflow** | [PASS / FAIL] | [Conventional Commits configured] |
| **IaC Governance** | [PASS / FAIL] | [Infrastructure changes via code] |
| **Dependency Management** | [PASS / FAIL] | [CVE scan passed] |

---

## 4. Project Directory Tree

### Documentation Artifacts (this feature)
```text
specs/YYYY/Month/[JIRA_KEY]-[feature-name]/
├── plan.md              # This file (tech design and layout)
├── research.md          # Phase 0: research, options, and findings
├── data-model.md        # Phase 1: database entities and schemas
├── quickstart.md        # Phase 1: verification and runs guide
├── contracts/           # Phase 1: REST API definitions / endpoints
└── tasks.md             # Phase 2: executable implementation checklists
```

### Source Code Structures (repository paths)
```text
src/
├── models/             # Entity schemas / DTOs
├── services/           # Service Interfaces + Implementations
├── controllers/        # REST APIs / controllers
└── exceptions/         # Exception Advice handlers
tests/
├── unit/               # Unit tests (Mockito-based)
├── integration/        # Full context tests (@SpringBootTest)
└── contract/           # API slice validation tests (@WebMvcTest)
```

---

## 5. Complexity Justification Tracker

> **Fill ONLY if Constitution Gate check has violations that must be justified (e.g. bypassing a rule)**

| Rule Violation | Reason for Exception | Simpler Alternative Evaluated & Rejected | Approval Status |
|:---|:---|:---|:---|
| [Rule ID, e.g. S112] | [why needed] | [why standard exceptions are insufficient] | [Pending Review] |

---

## 6. Architecture Decision Records

| ADR ID | Title | Status | Link |
|:---|:---|:---|:---|
| **ADR-001** | [e.g., "Use PostgreSQL over MongoDB for transactional data"] | [Accepted / Proposed / Superseded] | [link to ADR document] |
| **ADR-002** | [e.g., "Adopt event-driven architecture for order processing"] | [Accepted / Proposed / Superseded] | [link to ADR document] |
| **ADR-003** | [e.g., "Select OpenTelemetry for observability instrumentation"] | [Accepted / Proposed / Superseded] | [link to ADR document] |

---

## 7. Observability Plan

- **Traces to Emit:**
  - [Operation name] → [Span description, e.g., "HTTP request → service method → DB query"]
  - [Operation name] → [Span description]
- **Metrics to Collect:**
  - Counters: [e.g., `requests.total`, `errors.total`, `orders.created`]
  - Histograms: [e.g., `request.duration.ms`, `db.query.duration.ms`]
- **Dashboards Required:**
  - [e.g., "Service Health Dashboard: request rate, error rate, latency percentiles"]
  - [e.g., "Business Metrics Dashboard: orders per minute, revenue throughput"]
- **Alerting Rules:**
  - [e.g., "Error rate > 1% for 5 minutes → PagerDuty P2"]
  - [e.g., "p95 latency > 500ms for 10 minutes → Slack #engineering"]

---

## 8. Security Review

- **OWASP Top 10 Applicable Items:**
  - [e.g., A01:2021 – Broken Access Control: [describe applicability]]
  - [e.g., A03:2021 – Injection: [describe applicability]]
  - [e.g., A07:2021 – Identification and Authentication Failures: [describe applicability]]
- **Attack Surface Assessment:**
  - [e.g., "New REST endpoints exposed: POST /api/orders, GET /api/orders/{id}"]
  - [e.g., "File upload endpoint accepts user-provided content"]
- **Authentication/Authorization Changes:**
  - [e.g., "New RBAC role: ORDER_MANAGER with permissions to approve/reject orders"]
- **Input Validation Requirements:**
  - [e.g., "All request DTOs validated via Jakarta Bean Validation annotations"]
  - [e.g., "File uploads limited to 5MB, allowed types: PDF, PNG, JPEG"]

---

## 9. Rollback & Migration Plan

- **Database Migration Strategy:**
  - [e.g., "Expand-contract pattern: add nullable column → backfill → enforce NOT NULL"]
  - [e.g., "Migration scripts managed via Flyway, versioned as V202X.XX.XX"]
- **Rollback Procedure:**
  - [e.g., "Revert to previous deployment via CI/CD rollback; disable feature flag"]
  - [e.g., "Database: run corresponding undo migration script"]
- **Feature Flag Configuration:**
  - [e.g., "Flag: `enable-new-checkout` — boolean — default OFF"]
  - [e.g., "Rollout: internal → 10% beta → 50% → 100%"]
- **Zero-Downtime Deployment Approach:**
  - [e.g., "Blue-green deployment with health check validation before traffic switch"]

---

## 10. Dependency Impact Analysis

| Dependency | Version | License | Known CVEs | Justification |
|:---|:---|:---|:---|:---|
| [e.g., spring-boot-starter-web] | [e.g., 3.2.1] | [e.g., Apache 2.0] | [e.g., None] | [e.g., Core web framework] |
| [e.g., jackson-databind] | [e.g., 2.16.0] | [e.g., Apache 2.0] | [e.g., CVE-XXXX-XXXX (mitigated)] | [e.g., JSON serialization] |
| [e.g., opentelemetry-sdk] | [e.g., 1.32.0] | [e.g., Apache 2.0] | [e.g., None] | [e.g., Observability instrumentation] |

---

## 11. API Contract Reference (if applicable)

- **OpenAPI Spec Location:** [e.g., `docs/api/openapi.yaml` or URL to hosted spec]
- **Breaking Changes from Previous Version:**
  - [e.g., "Removed `GET /api/v1/orders` — replaced by `GET /api/v2/orders` with pagination"]
  - [e.g., "Changed `status` field from string to enum in response body"]
- **Contract Test Location:** [e.g., `tests/contract/` or link to Pact broker]
