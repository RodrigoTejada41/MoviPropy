from fastapi.testclient import TestClient

from moviprogy_api.database import DatabaseStatus
from moviprogy_api.main import create_app


def test_readiness_reports_database_not_configured(monkeypatch):
    monkeypatch.setattr(
        "moviprogy_api.routes.health.check_database",
        lambda: DatabaseStatus(configured=False, available=False),
    )
    client = TestClient(create_app())

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "not_configured",
    }


def test_readiness_reports_database_unavailable(monkeypatch):
    monkeypatch.setattr(
        "moviprogy_api.routes.health.check_database",
        lambda: DatabaseStatus(configured=True, available=False),
    )
    client = TestClient(create_app())

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "status": "error",
            "database": "unavailable",
        }
    }
