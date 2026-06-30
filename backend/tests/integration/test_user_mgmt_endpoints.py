from uuid import uuid4

from app.main import app
from app.models.user_mgmt import DEFAULT_ROLES
from app.services.auth_service import AuthService


def test_admin_user_management_flow(client):
    email = f"admin-{uuid4().hex[:8]}@example.com"
    tenant_id = "tenant-admin"
    password = "AdminPass#12345"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id},
        headers={"X-Geo-Country": "US"},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant_id}

    auth_service = AuthService(repository=app.state.container.auth_repository, settings=app.state.container.settings)
    session = auth_service.get_session_info_from_access_token(token)
    user = auth_service.repository.get_user_by_id(session.user_id)
    assert user is not None
    user.role = "organization_admin"
    user.permissions = DEFAULT_ROLES["organization_admin"]
    auth_service.repository.update_user(user)

    relogin = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id},
        headers={"X-Geo-Country": "US"},
    )
    assert relogin.status_code == 200
    headers = {"Authorization": f"Bearer {relogin.json()['access_token']}", "X-Tenant-ID": tenant_id}

    org_response = client.post(
        "/api/v1/admin/organizations",
        json={"name": "Org Admin", "slug": "org-admin", "settings": {"region": "us"}},
        headers=headers,
    )
    assert org_response.status_code == 201
    org_id = org_response.json()["id"]

    team_response = client.post(
        "/api/v1/admin/teams",
        json={"organization_id": org_id, "name": "Team Admin", "settings": {}},
        headers=headers,
    )
    assert team_response.status_code == 201
    team_id = team_response.json()["id"]

    project_response = client.post(
        "/api/v1/admin/projects",
        json={"organization_id": org_id, "team_id": team_id, "name": "Project Admin", "settings": {}},
        headers=headers,
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    invitation_response = client.post(
        "/api/v1/admin/invitations",
        json={
            "email": "invited@example.com",
            "organization_id": org_id,
            "team_id": team_id,
            "project_id": project_id,
            "role_name": "viewer",
        },
        headers=headers,
    )
    assert invitation_response.status_code == 200
    token_value = invitation_response.json()["token"]

    accept_response = client.post(
        "/api/v1/admin/invitations/accept",
        json={"token": token_value, "user_id": "invited-user-1"},
        headers=headers,
    )
    assert accept_response.status_code == 200

    membership_id = accept_response.json()["id"]
    deactivate = client.post(
        "/api/v1/admin/memberships/deactivate",
        json={"membership_id": membership_id},
        headers=headers,
    )
    assert deactivate.status_code == 200

    transfer = client.post(
        "/api/v1/admin/ownership/transfer",
        json={"entity_type": "project", "entity_id": project_id, "to_user_id": "invited-user-1"},
        headers=headers,
    )
    assert transfer.status_code == 200

    audits = client.get("/api/v1/admin/audits", headers=headers)
    assert audits.status_code == 200
    assert len(audits.json()) >= 1
