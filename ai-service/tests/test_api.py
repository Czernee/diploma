from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_recommend_endpoint() -> None:
    payload = {
        "budget": 100000,
        "purpose": "gaming",
        "preferred_brand": "any",
        "needs_wifi": False,
        "target_resolution": "1080p",
    }
    response = client.post("/api/configurator/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["purpose"] == "gaming"
    assert body["total_price"] <= 100000
    assert len(body["components"]) == 7


def test_generate_alias_endpoint() -> None:
    payload = {
        "budget": 120000,
        "purpose": "study",
        "preferred_brand": "any",
        "needs_wifi": True,
        "target_resolution": "1080p",
    }
    response = client.post("/api/configurator/generate", json=payload)
    assert response.status_code == 200
    assert response.json()["purpose"] == "study"


def test_recommend_endpoint_returns_422_for_too_low_budget() -> None:
    payload = {
        "budget": 30000,
        "purpose": "gaming",
        "preferred_brand": "nvidia",
        "needs_wifi": False,
        "target_resolution": "1440p",
    }
    response = client.post("/api/configurator/recommend", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["providedBudget"] == 30000
    assert detail["minimumRequiredBudget"] > 30000
