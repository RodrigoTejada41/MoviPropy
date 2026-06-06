from fastapi.testclient import TestClient

from moviprogy_api.main import create_app


def test_production_disables_openapi_and_docs(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MOVIPROGY_ENVIRONMENT", "production")
    monkeypatch.setenv("MOVIPROGY_ALLOWED_HOSTS", "prod.moviprogy.example")
    client = TestClient(
        create_app(),
        base_url="http://prod.moviprogy.example",
    )

    assert client.get("/openapi.json").status_code == 404
    assert client.get("/docs").status_code == 404


def test_allowed_hosts_rejects_unknown_host(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MOVIPROGY_ENVIRONMENT", "development")
    monkeypatch.setenv("MOVIPROGY_ALLOWED_HOSTS", "dev.moviprogy.example")
    client = TestClient(create_app(), base_url="http://unknown.example")

    assert client.get("/health").status_code == 400
