import json
import logging

from fastapi.testclient import TestClient

from moviprogy_api.main import create_app


def test_request_log_is_structured_and_does_not_include_authorization(caplog):
    assert logging.getLogger("moviprogy.request").isEnabledFor(logging.INFO)
    assert logging.getLogger("moviprogy.request").handlers
    app = create_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="moviprogy.request"):
        response = client.get(
            "/health",
            headers={"Authorization": "Bearer secret-that-must-not-be-logged"},
        )

    assert response.status_code == 200
    record = next(item for item in caplog.records if item.name == "moviprogy.request")
    payload = json.loads(record.message)
    assert payload["event"] == "http_request"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] >= 0
    assert payload["request_id"] == response.headers["X-Request-ID"]
    assert "secret-that-must-not-be-logged" not in record.message
