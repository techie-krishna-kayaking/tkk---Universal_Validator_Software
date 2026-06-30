# Admin User Management API

## Base Path
- /api/v1/admin

## Endpoints
- POST /organizations
- GET /organizations
- PUT /organizations/{organization_id}
- DELETE /organizations/{organization_id}
- POST /teams
- GET /teams
- PUT /teams/{team_id}
- DELETE /teams/{team_id}
- POST /projects
- GET /projects
- PUT /projects/{project_id}
- DELETE /projects/{project_id}
- POST /roles
- PUT /roles/{role_name}
- GET /roles
- POST /permissions
- GET /permissions
- POST /invitations
- POST /invitations/accept
- POST /memberships/deactivate
- DELETE /memberships
- POST /ownership/transfer
- PUT /organizations/{organization_id}/settings
- PUT /teams/{team_id}/settings
- PUT /projects/{project_id}/settings
- GET /audits

## Security Requirements
- Authorization: Bearer token
- Required header: X-Tenant-ID
- Permission middleware enforced per endpoint
