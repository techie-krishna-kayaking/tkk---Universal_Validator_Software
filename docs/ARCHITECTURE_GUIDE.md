# Architecture Guide — tkk-UniversalValidator

## Platform Overview

tkk-UniversalValidator is a modular monolith backend paired with a single-page React frontend, deployed as containerised services. The design prioritises simplicity of operation at the current scale while retaining clean boundary separation that enables a future microservices split if necessary.

---

## High-Level Component Diagram

```
Browser (React SPA)
        │ HTTPS
        ▼
   NGINX / Ingress
   ┌────────────────────────────────┐
   │     Backend API (FastAPI)      │
   │                                │
   │  Auth ─ RBAC ─ Tenant Layer    │
   │  Connector Framework           │
   │  Validation Engine             │
   │  YAML Workflow Engine          │
   │  Execution Engine (Pandas /    │
   │    PySpark / Polars / DuckDB)  │
   │  Profiling Engine              │
   │  Great Expectations            │
   │  Anomaly Detection (IsoForest) │
   │  Report Generator              │
   │  Scheduler (Celery)            │
   │  AI / LLM Integration          │
   └──────────┬─────────────────────┘
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
 PostgreSQL  Redis   External
             (cache,  Connectors /
              queue)  Data Sources
```

---

## Backend Architecture

### Application factory

`backend/app/core/application.py::create_app()` builds the FastAPI instance and registers:
1. CORS, GZip, security headers, CSRF, rate-limiting middleware
2. Request context (request ID injection)
3. Prometheus metrics middleware
4. Exception handlers
5. API router (versioned under `/api/v1`)
6. OpenTelemetry instrumentation (when `OTEL_ENABLED=true`)

### Configuration management

`backend/app/config/settings.py` — Pydantic `BaseSettings` with `lru_cache`. All configuration is resolved from environment variables. Optional sources: `.env` file, AWS Secrets Manager, Azure Key Vault, Google Secret Manager, HashiCorp Vault (via `config_service.py`).

### Dependency injection

The `AppContainer` dataclass (`app/dependencies/container.py`) is the composition root. It is built at startup (`app/core/lifecycle.py`) and attached to `app.state`. Route handlers resolve services via `Depends(get_container)`. There is no global mutable state.

### Authentication and RBAC

- JWT tokens (HS256) with issuer, audience, JTI, and type claims.
- Short-lived access tokens (15 min) paired with long-lived refresh tokens (30 days).
- TOTP-based MFA via `pyotp`.
- Passwords hashed with `pbkdf2_sha256` (passlib).
- Feature-level permissions stored per user; evaluated by `require_permission()` dependency.
- Tenant isolation enforced on every authenticated endpoint via `X-Tenant-ID` header.

### Plugin architecture

Both connectors and validators use the same structural pattern:
1. `BaseConnector` / `BaseValidator` — abstract interface with typed SDK dataclasses.
2. `ConnectorRegistry` / `ValidatorRegistry` — in-memory registries keyed by spec `key`.
3. `ConnectorLoader` / `ValidatorLoader` — discovers implementations from the `plugins/` directory using import scanning.
4. `ConnectorFactory` / `ValidatorFactory` — resolves and instantiates implementations.

---

## Frontend Architecture

### Technology stack

| Layer | Technology |
|---|---|
| Framework | React 19 |
| Language | TypeScript 5.8 |
| Build | Vite 7 |
| UI components | MUI 7 |
| Routing | React Router 7 |
| Charts | Recharts 3 |
| State | React Context (Auth, Localization, ColorMode) |
| Testing | Vitest + React Testing Library |
| E2E | Playwright |

### Context providers (in `main.tsx` wrapping order)

`ColorModeProvider` → `ThemeProvider` → `BrowserRouter` → `LocalizationProvider` → `AuthProvider` → `App`

### Route structure

All routes are defined in `App.tsx` with `ProtectedRoute` wrappers. Navigation items in `navigation.ts` are the authoritative source for role visibility and path mapping.

---

## Data Flow — Validation Job Execution

```
User creates job (Validation Builder)
        │
        ▼
Backend validates request schema (Pydantic)
        │
        ▼
YAML Workflow Engine compiles configuration
        │
        ▼
Execution Engine Selector picks engine
(Pandas / PySpark / Polars / DuckDB)
        │
        ▼
Connector Framework reads source and target
        │
        ▼
Validator Pipeline runs selected validators
        │
        ▼
Results stored (Database / Parquet / HTML / Excel)
        │
        ▼
Report Generator creates HTML/PDF report
        │
        ▼
Notifications sent (email / Slack / Teams)
```

---

## Deployment Architecture

```
GitHub Actions (CI/CD)
        │ image push
        ▼
GHCR Image Registry
        │ Helm deploy
        ▼
Kubernetes Cluster (EKS / AKS / GKE)
  ├── tkk-backend Deployment (HPA min 2, max 8)
  ├── tkk-frontend Deployment (HPA min 2, max 6)
  ├── PostgreSQL StatefulSet (or managed RDS/CloudSQL)
  ├── Redis StatefulSet (or managed ElastiCache)
  ├── Nginx Ingress (TLS termination)
  └── Monitoring Stack (Prometheus / Grafana / OTel Collector / ELK)
```

Infrastructure is provisioned via Terraform modules (`terraform/modules/aws|azure|gcp`) with per-cloud environment wrappers under `terraform/environments/`.

---

## Security Architecture

Layers:
1. **Transport** — TLS at ingress; HSTS header enforced.
2. **Authentication** — JWT with short expiry; MFA; OAuth2/OIDC federation.
3. **Authorisation** — Role + permission middleware on every endpoint; tenant isolation.
4. **Input validation** — Pydantic schema validation rejects unexpected fields.
5. **Secrets** — Fernet encryption for stored credentials; never logged.
6. **Headers** — CSP, X-Frame-Options, X-Content-Type-Options, HSTS applied by middleware.
7. **Scanning** — bandit + pip-audit + npm audit in CI on every push.

Full assessment: `docs/SECURITY_REVIEW_OWASP.md` and `docs/THREAT_MODEL.md`.

---

## Observability Architecture

- **Metrics** — Prometheus exposition at `/api/v1/metrics`; scraped by Prometheus; visualised in Grafana.
- **Tracing** — OpenTelemetry SDK with OTLP export to OTel Collector; propagates to backend spans.
- **Logs** — Structlog JSON logs; Logstash pipeline → Elasticsearch → Kibana.
- **Request IDs** — injected by `RequestContextMiddleware`; included in all error responses.

---

## Architectural Decisions

Key decisions recorded in `architecture/TECHNOLOGY_DECISION_RECORD.md`:
- Modular monolith chosen over microservices for initial delivery velocity and operational simplicity.
- Pydantic v2 for high-performance schema validation.
- Plugin pattern for connectors and validators to enable third-party extensibility without core changes.
- Celery + Redis for background task queue; designed for distributed worker scaling.
- Alembic for schema migrations; all schema changes must pass through migration scripts.
