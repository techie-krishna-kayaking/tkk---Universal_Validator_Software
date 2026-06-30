def test_health_endpoints_contract(client, auth_headers):
    health = client.get("/api/v1/health", headers=auth_headers)
    liveness = client.get("/api/v1/health/liveness", headers=auth_headers)
    readiness = client.get("/api/v1/health/readiness", headers=auth_headers)

    assert health.status_code == 200
    assert liveness.status_code == 200
    assert readiness.status_code == 200

    assert health.json()["status"] == "healthy"
    assert liveness.json()["status"] == "alive"
    assert "status" in readiness.json()
