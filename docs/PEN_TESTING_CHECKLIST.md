# Penetration Testing Checklist — tkk-UniversalValidator

**Standard:** Based on OWASP Testing Guide (OTG) v4 and PTES
**Date:** 2026-07-01
**Scope:** Backend API, Frontend SPA, Infrastructure

---

## 1. Reconnaissance and Discovery

- [ ] Enumerate all API endpoints via `/openapi.json`.
- [ ] Confirm `/openapi.json`, `/docs`, and `/redoc` are disabled in staging/prod.
- [ ] Identify exposed service ports via nmap scan on all cluster services.
- [ ] Confirm no direct database or Redis ports exposed beyond cluster boundary.
- [ ] Check HTTP response headers for information leakage (server version, framework identifiers).
- [ ] Verify no `.env` files, backup files, or config files accessible via web server.

---

## 2. Authentication Testing

- [ ] Attempt login with blank, whitespace-only, and extremely long credentials.
- [ ] Verify account lockout triggers after configured failed attempts (`MAX_FAILED_LOGIN_ATTEMPTS`).
- [ ] Verify lockout duration matches `ACCOUNT_LOCKOUT_MINUTES`.
- [ ] Test for username enumeration via timing differences in login response.
- [ ] Verify password reset tokens are single-use and expire in 30 minutes.
- [ ] Confirm JWT tokens contain issuer, audience, expiry, and JTI claims.
- [ ] Attempt replaying an expired JWT and verify 401 response.
- [ ] Attempt modifying JWT payload without valid signature and verify 401.
- [ ] Attempt using an access token after issuing a logout request.
- [ ] Test MFA bypass: attempt login without TOTP code when MFA is enabled.
- [ ] Test MFA code reuse within valid window.
- [ ] Test OAuth state parameter: omit or replay the state value and verify rejection.

---

## 3. Authorization and Access Control

- [ ] Test all RBAC roles: confirm each role only accesses permitted endpoints.
- [ ] Attempt horizontal privilege escalation: access another tenant's resources using own valid token.
- [ ] Attempt vertical privilege escalation: use a Viewer token to call admin-only endpoints.
- [ ] Verify `X-Tenant-ID` header is validated and cannot be spoofed to access another tenant.
- [ ] Test IDOR: substitute resource IDs (UUIDs) belonging to other tenants.
- [ ] Confirm metrics endpoint (`/api/v1/metrics`) is not accessible without network-level protection in production.

---

## 4. Input Validation and Injection

- [ ] Submit SQL injection payloads in all string fields (email, name, query params).
- [ ] Verify Pydantic schema validation rejects unexpected fields (`extra="ignore"`).
- [ ] Submit oversized payloads (multi-MB JSON bodies) and verify graceful rejection.
- [ ] Submit malformed JSON and verify structured error responses, not stack traces.
- [ ] Upload a YAML workflow with embedded shell commands and verify schema rejection.
- [ ] Submit CSV/Excel files with formula injection (`=CMD(...)`) and verify handling.
- [ ] Test connector URL fields with `http://169.254.169.254/` (AWS IMDS) — verify rejection.
- [ ] Test connector URL fields with `http://localhost/` and RFC 1918 IPs.
- [ ] Submit malformed JWT (truncated, wrong algorithm header) and verify 401.

---

## 5. CSRF and Session Management

- [ ] Call a state-modifying endpoint from a cross-origin request without the CSRF header and verify 403.
- [ ] Verify that state-modifying requests with a mismatched CSRF cookie/header are rejected.
- [ ] Confirm refresh token is invalidated on logout.
- [ ] Confirm access token lifespan matches configured `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`.

---

## 6. Security Headers

- [ ] Verify `Strict-Transport-Security` header is present on all HTTPS responses.
- [ ] Verify `X-Content-Type-Options: nosniff` is present.
- [ ] Verify `X-Frame-Options: DENY` is present.
- [ ] Verify `Content-Security-Policy` is present and does not include `unsafe-inline` or `unsafe-eval`.
- [ ] Verify `Referrer-Policy: strict-origin-when-cross-origin` is present.
- [ ] Confirm `Access-Control-Allow-Origin` does not include `*` in production.

---

## 7. Rate Limiting and DoS

- [ ] Send >10 login requests from same IP within 60 seconds and confirm 429 response.
- [ ] Confirm rate limit applies to `/auth/refresh` endpoint.
- [ ] Attempt to create large numbers of validation jobs in rapid succession.
- [ ] Submit deeply nested JSON payloads and confirm memory/timeout limits.

---

## 8. Secrets and Credentials

- [ ] Scan all API responses for leaked credentials, tokens, or key material.
- [ ] Confirm error responses do not include database connection strings or internal paths.
- [ ] Search application logs for passwords, JWT secrets, or encryption keys.
- [ ] Verify `.env` files are excluded via `.gitignore` and `.dockerignore`.
- [ ] Run `git log --all -- '*.env'` to confirm no historical secret commits.

---

## 9. Infrastructure and Container Security

- [ ] Confirm all containers run as non-root users.
- [ ] Verify Kubernetes Secrets are not mounted unnecessarily.
- [ ] Confirm PostgreSQL and Redis are not reachable from outside the cluster.
- [ ] Test Kubernetes API server access with expired/invalid kubeconfig.
- [ ] Confirm monitoring endpoints (Prometheus, Grafana, Kibana) are not publicly exposed.
- [ ] Check Grafana default credentials have been rotated.
- [ ] Confirm Terraform state file does not contain sensitive values.

---

## 10. Dependency and Supply Chain

- [ ] Run `pip-audit` or `safety check` against backend requirements and verify no high/critical CVEs.
- [ ] Run `npm audit --audit-level=high` against frontend and verify no high/critical CVEs.
- [ ] Verify all Docker base image digests match expected pinned values.
- [ ] Confirm GitHub Actions workflows do not use unpinned `@main` third-party actions.

---

## Sign-Off Requirements

Before production launch, the following must be completed and evidenced:

| Test Area | Completed By | Date | Notes |
|---|---|---|---|
| Authentication | | | |
| Authorization / RBAC | | | |
| Injection | | | |
| CSRF and Session | | | |
| Security Headers | | | |
| Rate Limiting | | | |
| Secrets | | | |
| Infrastructure | | | |
| Dependency Scan | | | |
