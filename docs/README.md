# docs

## Purpose
Hosts product and engineering reference documentation, standards, and governance guides.

## Responsibilities
- Maintain single source of truth for product and engineering docs.
- Define review cadence and document lifecycle policy.
- Preserve architecture-to-requirement traceability.

## Ownership
Product and Engineering Documentation Council

## Coding Standards
- No implementation code in this folder unless approved by Architecture Review Board and Product Governance.
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.

## Prompt 43 Runbook
- `PERFORMANCE_TESTING.md`: load, stress, benchmark, and optimization guidance.

## Prompt 44 Security Review
- `SECURITY_REVIEW_OWASP.md`: OWASP Top 10 assessment.
- `THREAT_MODEL.md`: STRIDE threat model.
- `PEN_TESTING_CHECKLIST.md`: penetration testing checklist with sign-off table.

## Prompt 46 Documentation Suite
- `DEVELOPER_GUIDE.md`: backend/frontend setup, project layout, testing, CI reference.
- `USER_GUIDE.md`: end-user walkthrough for the platform dashboard and AI features.
- `ADMIN_GUIDE.md`: organisation, RBAC, secrets, backup, monitoring, security ops.
- `ARCHITECTURE_GUIDE.md`: component diagrams, data flow, deployment topology, design decisions.
- `API_DOCS.md`: full REST API reference for auth, health, admin, config, and metrics.
- `PLUGIN_SDK.md`: developer guide for building custom connectors and validators.

## Prompt 50 Final Review
- `PRODUCTION_READINESS_REPORT.md`: ARB production readiness assessment — scores, blockers, findings, and verdict.
