from fastapi.testclient import TestClient

import app as app_module
from configurator.catalog import ComponentOption, InMemoryCatalogProvider
from configurator.engine import ConfiguratorEngine
from configurator.models import ComponentType


def _test_catalog() -> dict[ComponentType, list[ComponentOption]]:
    return {
        ComponentType.CPU: [
            ComponentOption(ComponentType.CPU, "AMD Ryzen 5 5600", "amd", 11000, 7.6, 7.2, 7.0, 7.2, socket="AM4", cpu_tdp=65),
            ComponentOption(ComponentType.CPU, "Intel Core i7-14700F", "intel", 22000, 9.0, 9.1, 8.4, 8.8, socket="AM4", cpu_tdp=125),
        ],
        ComponentType.GPU: [
            ComponentOption(ComponentType.GPU, "NVIDIA RTX 4060", "nvidia", 32000, 8.0, 7.0, 6.5, 7.0, gpu_tdp=115),
            ComponentOption(ComponentType.GPU, "NVIDIA RTX 4070 Super", "nvidia", 43000, 9.2, 8.1, 7.1, 8.2, gpu_tdp=220),
        ],
        ComponentType.MOTHERBOARD: [
            ComponentOption(
                ComponentType.MOTHERBOARD,
                "MSI B550-A PRO",
                "msi",
                11500,
                7.0,
                7.0,
                7.0,
                7.0,
                socket="AM4",
                ram_type="DDR4",
                supports_wifi=True,
            ),
        ],
        ComponentType.RAM: [
            ComponentOption(ComponentType.RAM, "32GB DDR4 3200", "kingston", 8000, 8.0, 8.2, 7.5, 7.8, ram_type="DDR4"),
        ],
        ComponentType.STORAGE: [
            ComponentOption(ComponentType.STORAGE, "NVMe SSD 1TB", "wd", 7000, 8.0, 8.3, 7.8, 7.9),
        ],
        ComponentType.PSU: [
            ComponentOption(ComponentType.PSU, "650W 80+ Bronze", "deepcool", 5500, 7.5, 7.5, 7.3, 7.4, psu_watts=650),
        ],
        ComponentType.CASE: [
            ComponentOption(ComponentType.CASE, "ATX Mid Tower Airflow", "zalman", 5000, 7.5, 7.5, 7.5, 7.5),
        ],
    }


app_module.engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_test_catalog()))
client = TestClient(app_module.app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_recommend_endpoint() -> None:
    payload = {
        "budget": 120000,
        "purpose": "gaming",
        "preferred_brand": "any",
        "needs_wifi": False,
        "target_resolution": "1080p",
    }
    response = client.post("/api/configurator/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["purpose"] == "gaming"
    assert body["total_price"] <= 120000
    assert len(body["components"]) == 7
    assert "alternatives" in body
    assert body["alternatives"] is None or body["alternatives"].get("pricier") is not None


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


def test_recommend_endpoint_returns_422_for_unreachable_vram_requirement() -> None:
    payload = {
        "budget": 120000,
        "purpose": "gaming",
        "min_vram_gb": 24,
    }
    response = client.post("/api/configurator/recommend", json=payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "vram" in detail["message"].lower()
