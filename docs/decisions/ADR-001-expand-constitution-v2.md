# ADR-001: Expand Constitution from 5 to 14 Articles (v2)

**Status:** Accepted

**Date:** 2026-06-29

**Authors:** Girish Chandra

**Jira ID:** N/A (governance initiative)

---

## Decision Drivers

- Industry compliance gaps identified during architecture audit
- OWASP 2025 Top 10 compliance requirements
- OpenTelemetry adoption as industry-standard observability framework
- WCAG 2.2 Level AA accessibility mandate
- EU AI Act regulatory compliance requirements
- SLSA/supply-chain security standards adoption

## Context and Problem Statement

The original project constitution contained 5 articles focused on Spec-Driven Development (SDD), Jira integration, and code simplicity. A comprehensive industry audit revealed 9 missing governance areas critical for production-grade software delivery. These gaps spanned security, observability, accessibility, architecture decision tracking, git workflow standards, and regulatory compliance. Without addressing these, the project would remain non-compliant with current industry standards and regulatory requirements.

## Considered Options

| Option | Pros | Cons |
|:---|:---|:---|
| **Option 1: Keep 5 articles + add ad-hoc guidelines** | Minimal change, quick to implement | Scattered governance, hard to enforce consistently, guidelines may be missed or ignored |
| **Option 2: Expand to 14 articles in constitution** | Single source of truth, comprehensive governance, enforceable by AI agents, clear audit trail | Longer document, requires team training, higher initial effort |
| **Option 3: Create separate governance documents per concern** | Each concern self-contained, easier to update independently | Fragmented governance, no single authority, risk of conflicting policies, harder for AI agents to enforce |

## Decision Outcome

**Chosen:** Option 2 — Expand to 14 articles in the constitution

**Rationale:** A single authoritative document ensures all governance policies are discoverable, enforceable, and consistent. AI agents (Copilot, Antigravity) can load one file to understand all project constraints. This avoids the fragmentation risk of Option 3 and the inconsistency risk of Option 1. The trade-off of a longer document is acceptable given that the constitution is primarily machine-consumed and referenced by section.

## Consequences

- **Good:** Comprehensive governance coverage across security, observability, accessibility, and compliance. AI agents can enforce all standards from a single source. Clear audit trail for regulatory inquiries. Alignment with OWASP, WCAG 2.2, OpenTelemetry, SLSA, and EU AI Act standards.
- **Bad:** Longer constitution document requiring more maintenance. Team members need training on new articles. Initial onboarding overhead increases.
- **Neutral:** Constitution becomes the primary governance artifact, shifting authority from informal practices to documented policy. Existing workflows remain unchanged; new articles codify what should already be best practice.

## Links

- Supersedes: Original 5-article constitution (v1)
- Related: `.specify/constitution.md`, `.github/copilot-instructions.md`, `AGENTS.md`
