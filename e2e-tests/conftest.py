import os
import time
from typing import Any

import pytest
import requests


def _env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


@pytest.fixture(scope="session")
def base_url() -> str:
    return _env("E2E_BASE_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session")
def timeout_seconds() -> int:
    return int(_env("E2E_TIMEOUT_SECONDS", "5"))


@pytest.fixture(scope="session", autouse=True)
def wait_for_gateway(base_url: str, timeout_seconds: int) -> None:
    deadline = time.time() + 90
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/api/status", timeout=timeout_seconds)
            if response.status_code == 200:
                return
        except Exception as error:  # noqa: BLE001
            last_error = error
        time.sleep(2)
    message = "Gateway is not ready at /api/status"
    if last_error is not None:
        message += f": {last_error}"
    raise RuntimeError(message)


@pytest.fixture(scope="session")
def http(timeout_seconds: int) -> requests.Session:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.timeout = timeout_seconds  # type: ignore[attr-defined]
    return session


def _request(
    session: requests.Session,
    method: str,
    url: str,
    **kwargs: Any,
) -> requests.Response:
    timeout = getattr(session, "timeout", 5)
    return session.request(method, url, timeout=timeout, **kwargs)


@pytest.fixture(scope="session")
def call():
    return _request
