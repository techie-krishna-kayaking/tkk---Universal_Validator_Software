from fastapi.testclient import TestClient

from app.core.application import create_app


def test_create_app_has_auth_and_health_routes() -> None:
    app = create_app()
    with TestClient(app) as client:
        assert client.post("/api/v1/auth/login", json={}).status_code in {422, 401}
        assert client.get("/api/v1/health").status_code == 401
