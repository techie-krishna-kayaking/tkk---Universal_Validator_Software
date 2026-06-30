from app.models.config_mgmt import ConnectionType


def test_configuration_management_endpoints(client, admin_headers):
    create_response = client.post(
        "/api/v1/admin/configs/connections",
        json={
            "tenant_id": "tenant-admin",
            "name": "main-api",
            "connection_type": ConnectionType.API.value,
            "source": "environment",
            "credentials": {
                "base_url": "https://api.example.com",
                "auth_type": "bearer",
                "token": "api-token-value",
            },
            "metadata": {"owner": "platform-team"},
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    connection_id = create_response.json()["id"]

    list_response = client.get("/api/v1/admin/configs/connections?tenant_id=tenant-admin", headers=admin_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    validate_response = client.post(
        f"/api/v1/admin/configs/connections/{connection_id}/validate",
        headers=admin_headers,
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["valid"] is True

    test_response = client.post(
        f"/api/v1/admin/configs/connections/{connection_id}/test",
        headers=admin_headers,
    )
    assert test_response.status_code == 200
    assert test_response.json()["success"] is True

    rotate_response = client.post(
        f"/api/v1/admin/configs/connections/{connection_id}/rotate",
        json={"key": "token", "value": "api-token-value-v2"},
        headers=admin_headers,
    )
    assert rotate_response.status_code == 200
    assert rotate_response.json()["version"] == 2

    reload_response = client.post(
        "/api/v1/admin/configs/reload",
        json={"tenant_id": "tenant-admin"},
        headers=admin_headers,
    )
    assert reload_response.status_code == 200

    snapshots_response = client.get("/api/v1/admin/configs/snapshots?tenant_id=tenant-admin", headers=admin_headers)
    assert snapshots_response.status_code == 200
    assert len(snapshots_response.json()) >= 1

    audits_response = client.get("/api/v1/admin/configs/audits?tenant_id=tenant-admin", headers=admin_headers)
    assert audits_response.status_code == 200
    assert len(audits_response.json()) >= 1
