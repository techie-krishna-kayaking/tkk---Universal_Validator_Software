from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
from app.main import app
from app.models.user_mgmt import DEFAULT_ROLES
from app.services.auth_service import AuthService


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    email = f"user-{uuid4().hex[:8]}@example.com"
    tenant_id = "tenant-alpha"
    password = "AuthPass#12345"

    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id, "remember_me": True},
        headers={"X-Geo-Country": "US"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": tenant_id}


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    email = f"admin-{uuid4().hex[:8]}@example.com"
    tenant_id = "tenant-admin"
    password = "AdminPass#12345"

    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id, "remember_me": True},
        headers={"X-Geo-Country": "US"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    auth_service = AuthService(repository=app.state.container.auth_repository, settings=app.state.container.settings)
    session = auth_service.get_session_info_from_access_token(token)
    user = auth_service.repository.get_user_by_id(session.user_id)
    assert user is not None
    user.role = "organization_admin"
    user.permissions = DEFAULT_ROLES["organization_admin"]
    auth_service.repository.update_user(user)

    elevated_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id},
        headers={"X-Geo-Country": "US"},
    )
    assert elevated_login.status_code == 200
    elevated_token = elevated_login.json()["access_token"]
    return {"Authorization": f"Bearer {elevated_token}", "X-Tenant-ID": tenant_id}
