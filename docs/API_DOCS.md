# API Reference — tkk-UniversalValidator

**Base URL:** `/api/v1`
**Authentication:** Bearer JWT (`Authorization: Bearer <access_token>`)
**Tenant context:** `X-Tenant-ID: <tenant_id>` header required on all protected endpoints
**OpenAPI spec:** `/openapi.json` | Interactive docs: `/docs`

---

## Authentication

All auth endpoints under `/api/v1/auth`.

### POST /auth/register
Register a new user.

**Request:**
```json
{ "email": "user@example.com", "password": "Secure#Pass99!", "tenant_id": "my-org" }
```
**Response 201:** `SessionInfo`
```json
{ "user_id": "uuid", "email": "...", "tenant_id": "...", "role": "qa_engineer", "permissions": [] }
```

---

### POST /auth/login
Authenticate and obtain tokens.

**Request:**
```json
{ "email": "user@example.com", "password": "...", "tenant_id": "my-org", "remember_me": true }
```
**Response 200:** `LoginResponse`
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900 }
```
**Errors:** `401 invalid_credentials`, `429 rate_limited`, `403 account_locked`

---

### POST /auth/refresh
Exchange a refresh token for a new access token.

**Request:** `{ "refresh_token": "..." }`
**Response 200:** `LoginResponse`

---

### POST /auth/logout
Invalidate a refresh token.
**Auth required.**
**Request:** `{ "refresh_token": "..." }`
**Response 200:** `{ "message": "Logout complete" }`

---

### GET /auth/session
Return current session details from the Bearer token.
**Auth required.**
**Response 200:** `SessionInfo`

---

### POST /auth/forgot-password
Initiate password reset flow.
**Request:** `{ "email": "...", "tenant_id": "..." }`
**Response 200:** `{ "message": "...", "token": "..." }` (token omitted in production)

---

### POST /auth/reset-password
Complete password reset.
**Request:** `{ "token": "...", "new_password": "..." }`
**Response 200:** `{ "message": "Password reset complete" }`

---

### POST /auth/mfa/setup
Generate TOTP secret and recovery codes.
**Auth required.**
**Response 200:** `{ "secret": "...", "otpauth_url": "..." }`

---

### POST /auth/mfa/verify
Enable MFA after TOTP setup.
**Auth required.**
**Request:** `{ "code": "123456" }`
**Response 200:** `{ "message": "MFA enabled" }`

---

### GET /auth/oauth/{provider}/authorize
Initiate OAuth2 / OIDC authorisation flow.
**Providers:** `google`, `microsoft`, `azure_ad`, `okta`
**Query params:** `redirect_uri`, `state`
**Response 200:** `{ "provider": "...", "authorization_url": "..." }`

---

## Health

### GET /health
General health check.
**Auth required.**
**Response 200:** `{ "status": "alive", "service": "...", "version": "..." }`

### GET /health/liveness
Kubernetes liveness probe.
**Response 200:** liveness payload

### GET /health/readiness
Kubernetes readiness probe with dependency status.
**Response 200:** `{ "status": "ready", "database": {...}, "redis": {...}, "celery": {...} }`

---

## Metrics

### GET /metrics
Prometheus exposition format. Not JWT-protected; protect at network/ingress level.
**Response 200:** `text/plain; version=0.0.4`

---

## Administration — User Management

All under `/api/v1/admin`.

### Organisations

| Method | Path | Description | Min Role |
|---|---|---|---|
| POST | `/organizations` | Create organisation | Platform Admin |
| GET | `/organizations/{id}` | Get organisation | Org Admin |
| PATCH | `/organizations/{id}` | Update organisation | Org Admin |
| DELETE | `/organizations/{id}` | Delete organisation | Platform Admin |
| GET | `/organizations/{id}/members` | List members | Org Admin |
| POST | `/organizations/{id}/invite` | Invite user | Org Admin |
| POST | `/organizations/{id}/transfer-ownership` | Transfer owner | Org Admin |

### Teams

| Method | Path | Min Role |
|---|---|---|
| POST | `/teams` | Org Admin |
| GET | `/teams/{id}` | Org Admin |
| PATCH | `/teams/{id}` | Org Admin |
| DELETE | `/teams/{id}` | Org Admin |

### Projects

| Method | Path | Min Role |
|---|---|---|
| POST | `/projects` | Architect |
| GET | `/projects/{id}` | QA Engineer |
| PATCH | `/projects/{id}` | Architect |
| DELETE | `/projects/{id}` | Org Admin |

### Users

| Method | Path | Description |
|---|---|---|
| POST | `/users/accept-invitation` | Accept email invitation |
| POST | `/users/deactivate` | Deactivate user |
| POST | `/users/delete` | Delete user |

### Roles and Permissions

| Method | Path |
|---|---|
| POST | `/roles` |
| PATCH | `/roles/{id}` |
| DELETE | `/roles/{id}` |
| POST | `/permissions` |
| DELETE | `/permissions/{id}` |

### Audit

| Method | Path |
|---|---|
| GET | `/audit` |

---

## Configuration Management (Secrets)

All under `/api/v1/configs`.

| Method | Path | Description | Min Role |
|---|---|---|---|
| POST | `/configs` | Create encrypted config | Architect |
| GET | `/configs` | List configs (masked) | Architect |
| GET | `/configs/{id}` | Get config (masked) | Architect |
| PATCH | `/configs/{id}` | Update config | Architect |
| DELETE | `/configs/{id}` | Delete config | Org Admin |
| POST | `/configs/{id}/test` | Test connection | Architect |

---

## Common Error Codes

| HTTP Status | Code | Description |
|---|---|---|
| 400 | `validation_error` | Pydantic schema validation failure |
| 401 | `invalid_credentials` | Bad email/password |
| 401 | `token_expired` | JWT expired |
| 401 | `token_invalid` | JWT malformed or wrong signature |
| 403 | `permission_denied` | Insufficient role or permission |
| 403 | `csrf_validation_failed` | CSRF token mismatch |
| 403 | `account_locked` | Account locked after failed attempts |
| 422 | `unprocessable_entity` | Missing required fields |
| 429 | `rate_limited` | Too many requests |
| 500 | `internal_error` | Unexpected server error (with `request_id`) |
