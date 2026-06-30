from uuid import uuid4


def test_auth_register_login_refresh_logout(client):
    email = f"auth-{uuid4().hex[:8]}@example.com"
    tenant_id = "tenant-red"
    password = "AuthPass#12345"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id, "remember_me": False},
        headers={"X-Geo-Country": "US"},
    )
    assert login.status_code == 200
    login_payload = login.json()

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": login_payload["refresh_token"]})
    assert refresh.status_code == 200

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh.json()["refresh_token"]},
        headers={"Authorization": f"Bearer {refresh.json()['access_token']}", "X-Tenant-ID": tenant_id},
    )
    assert logout.status_code == 200


def test_protected_health_requires_auth(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 401
