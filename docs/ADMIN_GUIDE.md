# Administration Guide — tkk-UniversalValidator

## Administration Console

Platform and organisation admins access the admin console via **Administration** in the left navigation.

---

## Organisation Management

**Required role:** Platform Admin

Actions:
- Create, rename, activate, and deactivate organisations
- Assign organisation owner
- Configure organisation settings (slug, SSO domain, retention policies)
- View organisation-level audit logs

REST endpoints:
- `POST /api/v1/admin/organizations`
- `GET /api/v1/admin/organizations/{id}`
- `PATCH /api/v1/admin/organizations/{id}`
- `DELETE /api/v1/admin/organizations/{id}`

---

## Team Management

**Required role:** Organisation Admin or higher

Actions:
- Create and manage teams within an organisation
- Assign team owner and members
- Configure team-level settings
- Deactivate teams

---

## User Management

**Required role:** Organisation Admin or higher

Actions:
- Invite users by email
- Assign roles and permissions
- Deactivate and delete accounts
- Transfer ownership
- View login and security audit logs per user

### Inviting a user

```
POST /api/v1/admin/organizations/{org_id}/invite
{
  "email": "new.user@company.com",
  "role": "qa_engineer",
  "team_id": "team-uuid"
}
```

The invited user receives an email with an acceptance link. Until accepted, the invitation is in `pending` state.

---

## RBAC and Permissions

**Required role:** Organisation Admin or higher

### Default roles

| Role | Key |
|---|---|
| Platform Admin | `platform_admin` |
| Organisation Admin | `organization_admin` |
| Architect | `architect` |
| QA Lead | `qa_lead` |
| QA Engineer | `qa_engineer` |
| Viewer | `viewer` |
| Guest | `guest` |

### Custom roles

Create a custom role:
```
POST /api/v1/admin/roles
{
  "name": "Data Steward",
  "permissions": ["can_view_reports", "can_download_reports", "can_run_validation"]
}
```

### Available permissions

| Permission | Description |
|---|---|
| `can_create_connections` | Create new data connections |
| `can_delete_connections` | Remove data connections |
| `can_run_validation` | Execute validation jobs |
| `can_view_reports` | View validation reports |
| `can_download_reports` | Download report files |
| `can_delete_reports` | Delete historical reports |
| `can_configure_ai` | Configure LLM providers |
| `can_manage_secrets` | Create and read encrypted secrets |
| `can_configure_schedulers` | Create and modify job schedules |

---

## Secrets Management

**Required role:** Architect or higher

All secrets are encrypted with Fernet (AES-128-CBC + HMAC-SHA256) derived from `CONFIG_ENCRYPTION_KEY`. Secrets are never returned in plaintext via the API.

Supported secret types:
- Database connections
- Cloud storage credentials
- API keys
- SMTP, Slack, Teams, LLM provider credentials

Rotation: update the secret value via `PATCH /api/v1/configs/{id}`. Cached values are invalidated after `SECRET_CACHE_TTL_SECONDS` (default 300 s).

---

## Authentication Configuration

### MFA

Users enable MFA via **Settings → Security → Enable MFA**. Supported authenticators:
- Google Authenticator
- Microsoft Authenticator

Recovery codes are generated at setup time. Lost authenticator recovery uses a recovery code.

### Account Lockout

After `MAX_FAILED_LOGIN_ATTEMPTS` (default 5) consecutive failures, the account is locked for `ACCOUNT_LOCKOUT_MINUTES` (default 15). Platform Admins can manually unlock accounts.

### OAuth / SSO

Configure provider credentials in environment variables:
- `OAUTH_GOOGLE_CLIENT_ID`, `OAUTH_GOOGLE_CLIENT_SECRET`
- `OAUTH_MICROSOFT_CLIENT_ID`, `OAUTH_MICROSOFT_CLIENT_SECRET`
- `OAUTH_AZURE_AD_CLIENT_ID`, `OAUTH_AZURE_AD_CLIENT_SECRET`
- `OAUTH_OKTA_CLIENT_ID`, `OAUTH_OKTA_CLIENT_SECRET`

---

## Audit Logs

**Required role:** Architect or higher (read-only for Viewer)

Audit logs record:
- Login events (IP, user agent, geo-country, timestamp)
- Permission changes
- Secret access
- Configuration changes

Retrieve logs:
```
GET /api/v1/admin/audit?tenant_id={id}&limit=50
```

---

## Backup and Disaster Recovery

See the full runbook at `docs/BACKUP_RESTORE_DR.md`.

Quick reference:
```bash
# Local backup
bash scripts/backup/backup_postgres.sh

# Local restore
bash scripts/restore/restore_postgres.sh ./backups/tkk_uv_<timestamp>.dump

# Schema migration
DATABASE_URL=<url> bash scripts/migration/run_alembic_migration.sh head
```

For Kubernetes:
```bash
kubectl apply -f kubernetes/manifests/postgres-backup-cronjob.yaml
kubectl apply -f kubernetes/manifests/backend-migration-job.yaml
```

RPO target: 15 minutes. RTO target: 60 minutes.

---

## Monitoring and Observability

Refer to `docs/MONITORING_OBSERVABILITY.md` for full setup instructions.

Key dashboards:
- Prometheus metrics: `http://<prometheus>:9090`
- Grafana — TKK Backend Overview: `http://<grafana>:3000`
- Kibana: `http://<kibana>:5601`

Alert thresholds to configure in Grafana:
- Login failure rate > 5% over 5 minutes
- HTTP 5xx rate > 1% over 5 minutes
- P95 latency > 2 seconds sustained for 3 minutes
- Backup CronJob failure

---

## Security Operations

Refer to `docs/SECURITY_REVIEW_OWASP.md`, `docs/THREAT_MODEL.md`, and `docs/PEN_TESTING_CHECKLIST.md`.

Key hardening actions before production:
- Set `ALLOWED_ORIGINS` to the exact frontend origin (never `*`).
- Rotate all default credentials (Grafana admin, PostgreSQL, Redis).
- Source `JWT_SECRET_KEY` and `CONFIG_ENCRYPTION_KEY` from a managed secret store.
- Enable Redis AUTH and TLS.
- Enable Kubernetes network policies to restrict egress from backend pods.
