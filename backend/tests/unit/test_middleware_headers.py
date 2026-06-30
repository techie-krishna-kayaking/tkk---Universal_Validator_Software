from fastapi.testclient import TestClient

from app.main import app


def test_security_and_request_headers_present() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/login")

    assert response.status_code in {405, 404}
    assert "X-Request-ID" in response.headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
