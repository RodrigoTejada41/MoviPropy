from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EndpointResult:
    name: str
    requests: int
    errors: int
    p50_ms: float
    p95_ms: float
    max_ms: float


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * percent)))
    return ordered[index]


def request_once(url: str, token: str | None = None) -> tuple[float, int]:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    request = urllib.request.Request(url, headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    elapsed_ms = (time.perf_counter() - started) * 1000
    return elapsed_ms, status


def run_endpoint(
    name: str,
    url: str,
    requests: int,
    concurrency: int,
    token: str | None = None,
) -> EndpointResult:
    durations: list[float] = []
    errors = 0
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(request_once, url, token) for _ in range(requests)]
        for future in as_completed(futures):
            try:
                duration, status = future.result()
                durations.append(duration)
                if status != 200:
                    errors += 1
            except Exception:
                errors += 1

    return EndpointResult(
        name=name,
        requests=requests,
        errors=errors,
        p50_ms=round(statistics.median(durations), 2) if durations else 0.0,
        p95_ms=round(percentile(durations, 0.95), 2),
        max_ms=round(max(durations), 2) if durations else 0.0,
    )


def login(base_url: str, email: str, password: str) -> str:
    payload = json.dumps({"email": email, "senha": password}).encode()
    request = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read())["access_token"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--player-url", default="http://127.0.0.1:8091")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--max-p95-ms", type=float, default=1000)
    args = parser.parse_args()

    email = os.getenv("MOVIPROGY_ADMIN_EMAIL")
    password = os.getenv("MOVIPROGY_ADMIN_PASSWORD")
    if not email or not password:
        raise SystemExit("MOVIPROGY_ADMIN_EMAIL e MOVIPROGY_ADMIN_PASSWORD sao obrigatorios.")

    token = login(args.base_url, email, password)
    targets = [
        ("frontend", args.base_url, None),
        ("player", args.player_url, None),
        ("health", f"{args.base_url}/health", None),
        ("readiness", f"{args.base_url}/health/ready", None),
        ("clientes", f"{args.base_url}/api/admin/clientes?limit=50&offset=0", token),
    ]
    results = [
        run_endpoint(name, url, args.requests, args.concurrency, target_token)
        for name, url, target_token in targets
    ]
    print(json.dumps([asdict(result) for result in results], ensure_ascii=True))

    failed = any(result.errors or result.p95_ms > args.max_p95_ms for result in results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
