from fastapi.testclient import TestClient

from app.main import app


def test_openapi_custom_metadata_is_exposed() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["x-api-audience"] == "internal-platform"
    assert payload["info"]["title"]
