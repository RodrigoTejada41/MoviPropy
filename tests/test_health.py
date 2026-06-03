from fastapi.testclient import TestClient

from moviprogy_api.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_system_info_returns_project_contract():
    response = client.get("/api/system/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": "MoviProgy",
        "mode": "api",
        "offline_first": True,
    }
