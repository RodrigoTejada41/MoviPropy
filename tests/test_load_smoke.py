from scripts.load_smoke import percentile, run_endpoint


def test_percentile_handles_empty_and_ordered_values():
    assert percentile([], 0.95) == 0.0
    assert percentile([30.0, 10.0, 20.0], 0.5) == 20.0
    assert percentile([10.0, 20.0, 30.0, 40.0], 0.95) == 40.0


def test_run_endpoint_reports_success(monkeypatch):
    monkeypatch.setattr("scripts.load_smoke.request_once", lambda *_: (12.5, 200))

    result = run_endpoint("health", "http://example.test/health", requests=5, concurrency=2)

    assert result.requests == 5
    assert result.errors == 0
    assert result.p50_ms == 12.5
    assert result.p95_ms == 12.5
