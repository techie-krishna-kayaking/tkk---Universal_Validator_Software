# Threat Model — tkk-UniversalValidator

**Methodology:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
**Date:** 2026-07-01
**Scope:** Full platform — backend API, frontend, data connectors, AI chatbot, scheduler, deployment infrastructure.

---

## System Components

| Component | Description |
|---|---|
| Frontend (React SPA) | Browser-based dashboard served via NGINX |
| Backend API (FastAPI) | REST API with auth, validation, scheduling, reporting |
| PostgreSQL | Primary relational data store |
| Redis | Cache and Celery broker |
| Celery Workers | Background task execution |
| Connectors | Plugin-based data source/target adapters |
| AI Chatbot | LLM-backed natural language interface |
| Monitoring Stack | Prometheus, Grafana, ELK, OTEL Collector |
| Kubernetes / Helm | Container orchestration |
| Terraform | Infrastructure provisioning |
| GitHub Actions | CI/CD pipeline |

---

## Trust Boundaries

1. **Browser ↔ NGINX/Ingress** — public internet boundary; TLS required.
2. **NGINX ↔ Backend API** — internal cluster boundary; encrypted via mTLS or cluster network policy.
3. **Backend API ↔ PostgreSQL / Redis** — internal cluster boundary; credential-authenticated.
4. **Backend API ↔ External Connectors** — trusted internal execution context; external data sources may be hostile.
5. **Backend API ↔ LLM Providers** — external API boundary; prompt injection risk.
6. **CI/CD Pipelines ↔ Infrastructure** — privileged boundary; secrets required.

---

## STRIDE Analysis

### 1. Frontend / Authentication Layer

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| Session token theft via XSS | Spoofing | CSP headers, `X-XSS-Protection`, short-lived JWTs | Low — CSP may need refinement |
| CSRF attacks on state-modifying requests | Tampering | Double-submit CSRF cookie/header validation | Low |
| Credential brute-force | Spoofing | Rate limiting on login, account lockout | Low |
| Login bypass via OAuth callback manipulation | Spoofing | State parameter validation in OAuth flow | Medium — state verification must be strictly enforced |
| Password reset token reuse | Spoofing | Single-use tokens with 30-minute expiry, SHA-256 hashed storage | Low |
| Audit log denial by client | Repudiation | Server-side login audit with IP and user agent | Low |

---

### 2. Backend API

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| JWT forgery | Spoofing | HS256 JWT with secret; audience and issuer validation | Medium — RS256 with key rotation preferred for production |
| Token replay after logout | Spoofing | Refresh token revocation in progress; access token is short-lived (15 min) | Medium — revocation list should be implemented |
| Unauthorized resource access (IDOR) | Elevation of Privilege | RBAC middleware; tenant isolation on all queries | Low |
| Mass assignment via Pydantic | Tampering | `extra="ignore"` on all Pydantic models | Low |
| Internal server error detail exposure | Information Disclosure | Global exception handler returns generic message + request ID only | Low |
| Request ID spoofing | Tampering | Request ID is overwritten server-side; not trusted from client | Low |
| Secrets in logs | Information Disclosure | Credential masking in config service; no password/key logging | Low |
| YAML injection via workflow upload | Tampering | Schema validation on all YAML workflows before execution | Medium — ensure custom SQL/Python validators are sandboxed |
| Rate limit bypass via IP rotation | DoS | IP-based in-memory rate limiter (per-IP sliding window) | Medium — distributed rate limiter (Redis-backed) for multi-node deployments |

---

### 3. Data Connectors

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| SSRF via user-supplied connection URL | SSRF / Info Disclosure | Connector URLs require explicit configuration; URL allowlist needed | High — implement allowlist before production connector use |
| Credential leakage via connector error | Information Disclosure | Connector errors return structured codes, not raw exception detail | Low |
| SQL injection via connector query params | Tampering | Parameterized queries enforced in all DB connectors | Low |
| Malicious file upload (CSV, Excel) | Tampering | File type validation; execution in isolated engine context | Medium — sandbox large file parsing |
| Data exfiltration via connector | Information Disclosure | RBAC controls who can create and run connectors | Low |

---

### 4. AI Chatbot / LLM Integration

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| Prompt injection via user input | Tampering | Input sanitization; system prompt isolation | High — LLM responses should never be executed directly |
| Context leakage between tenants | Information Disclosure | Conversation context scoped to tenant and user session | Medium — validate isolation in LLM context window |
| LLM-generated SQL execution without review | Elevation of Privilege | Generated SQL presented for review before execution | Medium — enforce human-in-the-loop for SQL execution |
| Credential extraction via crafted prompts | Information Disclosure | Never include secrets in LLM context | High — enforce strict context filtering |

---

### 5. Scheduler and Background Workers

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| Celery task poisoning via Redis | Tampering | Redis not publicly exposed; password authentication in production | Medium — enable Redis AUTH and TLS |
| Scheduled job runs with stale permissions | Elevation of Privilege | Jobs run under the permission context of the creating user/role | Medium — validate RBAC at job execution time, not only at creation |
| DoS via job queue flooding | DoS | Celery concurrency and priority limits; rate limiting on job creation | Medium |

---

### 6. Infrastructure

| Threat | Category | Mitigation | Residual Risk |
|---|---|---|---|
| Container escape | Elevation of Privilege | Non-root containers (`appuser`); read-only filesystems where possible | Low |
| Kubernetes secret exposure | Information Disclosure | Secrets in Kubernetes Secret resources; mount as env vars | Medium — use external secret store (Vault/CSI driver) in production |
| Supply chain attack via base images | Tampering | Pinned image versions; image signing (pending) | Medium — enable Sigstore cosign signing |
| Terraform state exposure | Information Disclosure | Remote state with encryption; no secrets in tfvars files tracked in git | Low |
| CI/CD pipeline secret exfiltration | Information Disclosure | Secrets as GitHub encrypted secrets; not printed in logs | Low |
| kubeconfig credential exposure | Spoofing | Base64-encoded kubeconfig stored as GitHub secret | Low — rotate kubeconfig regularly |

---

## Risk Priority Matrix

| Risk | Severity | Likelihood | Priority |
|---|---|---|---|
| SSRF via connector URL | High | Medium | **P1** |
| LLM prompt injection with direct execution | High | High | **P1** |
| LLM context leaking secrets | High | Medium | **P1** |
| JWT HS256 → RS256 upgrade | Medium | Low | **P2** |
| Redis without AUTH/TLS in production | Medium | Medium | **P2** |
| ALLOWED_ORIGINS=* in production | High | High | **P1** |
| Token replay (no revocation list) | Medium | Low | **P2** |
| Image signing absent | Medium | Low | **P3** |
| Dependency vulnerabilities | Medium | Medium | **P2** |

---

## Remediation Ownership

| Priority | Owner | Target Resolution |
|---|---|---|
| P1 | Security Engineering | Before production launch |
| P2 | Platform Engineering | Within 30 days of prod launch |
| P3 | DevSecOps | Within 90 days of prod launch |
