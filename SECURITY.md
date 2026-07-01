# Security Policy

## Reporting a Vulnerability

Do **not** disclose vulnerabilities publicly until a fix has been released.

To report a security issue:
1. Open a GitHub Security Advisory (private) on this repository, or
2. Email the security owners through internal secure channels.

Include: affected component, description, reproduction steps, and potential impact.

Response SLAs:
- Critical / High: acknowledged within 24 hours, remediation within 7 days.
- Medium: acknowledged within 72 hours, remediation within 30 days.
- Low: acknowledged within 7 days, remediation within 90 days.

## Security Artifacts (Prompt 44)

- `docs/SECURITY_REVIEW_OWASP.md`: OWASP Top 10 2021 assessment mapped to actual implementation.
- `docs/THREAT_MODEL.md`: STRIDE threat model covering all platform components and trust boundaries.
- `docs/PEN_TESTING_CHECKLIST.md`: Pre-release penetration testing checklist with sign-off requirements.
- `.github/workflows/security-scan.yml`: Automated bandit, pip-audit, and npm-audit scanning on every push and weekly schedule.

## Automated Scanning

- Backend: `bandit` static analysis + `pip-audit` dependency audit (runs in CI on every push/PR to main).
- Frontend: `npm audit --audit-level=high` (runs in CI on every push/PR to main).
- Schedule: Weekly Monday 03:00 UTC.

## Security Baseline Requirements
- Zero-trust principles and least privilege.
- Tenant isolation is mandatory — validated by integration tests.
- No plaintext secrets in code, logs, or config files tracked in git.
- Auditability and traceability for all security-impacting decisions.
- `ALLOWED_ORIGINS` must be set to an explicit frontend origin in all non-local environments.

## Security Review Triggers
A security review is required when changes affect:
- Authentication or authorization architecture.
- Secrets management or credential handling.
- New connector types accepting user-supplied URLs or shell parameters.
- LLM/AI integration and context window management.
- Data retention, backup, or disaster recovery controls.

## Coordinated Disclosure
All findings are triaged by the security owner and tracked through internal governance workflow with severity classification, remediation deadlines, and closure evidence.
