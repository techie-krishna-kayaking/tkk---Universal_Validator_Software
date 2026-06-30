# Configuration Management API

## Base Path
- /api/v1/admin/configs

## Endpoints
- POST /connections
- GET /connections
- GET /connections/{connection_id}
- PUT /connections/{connection_id}
- DELETE /connections/{connection_id}
- POST /connections/{connection_id}/validate
- POST /connections/{connection_id}/test
- POST /connections/{connection_id}/rotate
- POST /reload
- GET /snapshots
- GET /audits

## Security
- Bearer token is required.
- X-Tenant-ID header is required for tenant-scoped routes.
- Write operations require can_manage_secrets.
- Read operations require can_view_reports.
