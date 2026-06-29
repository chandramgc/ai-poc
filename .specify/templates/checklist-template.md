# [CHECKLIST_TYPE] Checklist: [FEATURE NAME]

**Jira ID**: `[JIRA_KEY]` | **Created**: [DATE] | **Feature Spec**: [link to spec.md]

---

## 🧭 Audit Context & Setup

Review code, configurations, or designs against this structured checklist prior to merging.

| Item ID | Category | Audit Verification Item | Status | Inspector Comments / Findings |
|:---|:---|:---|:---|:---|
| **CHK-001** | **Gate Check** | Checked for hardcoded secrets, keys, or passwords (S2068 blocker) | `[ ]` | |
| **CHK-002** | **Gate Check** | Checked that all logs use parameterized SLF4J loggers (S106 blocker) | `[ ]` | |
| **CHK-003** | **Architecture** | Verified zero circular class/package dependencies | `[ ]` | |
| **CHK-004** | **Architecture** | Checked that dependencies are constructor-injected (no `@Autowired` fields) | `[ ]` | |
| **CHK-005** | **Layering** | Verified that controllers are thin and logic resides in services | `[ ]` | |
| **CHK-006** | **Security** | Checked that SQL queries use parameter-bound prepared statements (S2077) | `[ ]` | |
| **CHK-007** | **Quality** | Verified cognitive complexity is &le; 15 per method (S3776) | `[ ]` | |
| **CHK-008** | **Quality** | Checked that all open streams are wrapped in try-with-resources (S2095) | `[ ]` | |
| **CHK-009** | **Testing** | Confirmed unit test coverage &ge; 80% on new logic | `[ ]` | |
| **CHK-010** | **Observability** | Verified OpenTelemetry traces are emitted for key operations | `[ ]` | |
| **CHK-011** | **Observability** | Verified structured logging with correlation IDs (no raw stdout) | `[ ]` | |
| **CHK-012** | **Observability** | Confirmed monitoring dashboard exists and alerts are configured | `[ ]` | |
| **CHK-013** | **Accessibility** | Verified WCAG 2.2 Level AA compliance on all new UI components | `[ ]` | |
| **CHK-014** | **Accessibility** | Tested keyboard navigation flow end-to-end | `[ ]` | |
| **CHK-015** | **Accessibility** | Verified screen reader compatibility (ARIA labels, roles, live regions) | `[ ]` | |
| **CHK-016** | **Accessibility** | Confirmed color contrast ratios meet minimum 4.5:1 | `[ ]` | |
| **CHK-017** | **Data Privacy** | Verified PII fields are classified and handled per retention policy | `[ ]` | |
| **CHK-018** | **Data Privacy** | Confirmed consent collection follows GDPR/CCPA requirements | `[ ]` | |
| **CHK-019** | **Data Privacy** | Checked that no PII appears in logs or error responses | `[ ]` | |
| **CHK-020** | **API Contract** | Verified OpenAPI spec matches implemented endpoints | `[ ]` | |
| **CHK-021** | **API Contract** | Confirmed contract tests pass for all API changes | `[ ]` | |
| **CHK-022** | **API Contract** | Checked API versioning for any breaking changes | `[ ]` | |
| **CHK-023** | **Performance** | Verified response times meet spec NFR targets (p95 ≤ threshold) | `[ ]` | |
| **CHK-024** | **Performance** | Confirmed load test results are within acceptable bounds | `[ ]` | |
| **CHK-025** | **Performance** | Checked Core Web Vitals (LCP < 2.5s, INP < 200ms) for UI changes | `[ ]` | |
| **CHK-026** | **Dependency** | Verified no new CVEs introduced by dependency changes | `[ ]` | |
| **CHK-027** | **Dependency** | Confirmed license compliance for all new dependencies | `[ ]` | |
| **CHK-028** | **Dependency** | Checked that all dependencies are pinned to exact versions | `[ ]` | |

---

## 📝 Inspector Findings & Action Items

- **Finding 1:** [Describe findings, if any]
  - **Remediation Task:** [e.g. Create TXXX task to wrap resource in try-with-resources]
- **Finding 2:** [Describe findings]
  - **Remediation Task:** [Action item]

---

## Notes
- Check off verified items using `[x]`.
- All failing items must be remediated or documented with justified waivers before this checklist is signed off.
