from configurator.catalog import ComponentOption, InMemoryCatalogProvider
from configurator.engine import ConfiguratorEngine
from configurator.models import ComponentType, ConfigurationRequest, Purpose
import pytest


def _test_catalog() -> dict[ComponentType, list[ComponentOption]]:
    return {
        ComponentType.CPU: [
            ComponentOption(ComponentType.CPU, "AMD Ryzen 5 5600", "amd", 11000, 7.6, 7.2, 7.0, 7.2, socket="AM4", cpu_tdp=65),
            ComponentOption(ComponentType.CPU, "Intel Core i5-13400F", "intel", 18500, 8.2, 8.1, 7.8, 7.9, socket="LGA1700", cpu_tdp=65),
            ComponentOption(ComponentType.CPU, "Intel Core i7-14700F", "intel", 22000, 9.0, 9.1, 8.4, 8.8, socket="LGA1700", cpu_tdp=125),
        ],
        ComponentType.GPU: [
            ComponentOption(ComponentType.GPU, "NVIDIA RTX 4060", "nvidia", 32000, 8.0, 7.0, 6.5, 7.0, gpu_tdp=115),
            ComponentOption(ComponentType.GPU, "AMD Radeon RX 7600", "amd", 29000, 7.8, 6.9, 6.3, 6.8, gpu_tdp=165),
            ComponentOption(ComponentType.GPU, "NVIDIA RTX 4070 Super", "nvidia", 43000, 9.2, 8.1, 7.1, 8.2, gpu_tdp=220),
        ],
        ComponentType.MOTHERBOARD: [
            ComponentOption(ComponentType.MOTHERBOARD, "MSI B550-A PRO", "msi", 11500, 7.0, 7.0, 7.0, 7.0, socket="AM4", ram_type="DDR4"),
            ComponentOption(ComponentType.MOTHERBOARD, "Gigabyte B760M DS3H", "gigabyte", 15000, 7.8, 7.8, 7.5, 7.6, socket="LGA1700", supported_sockets=("Socket V",), ram_type="DDR4"),
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


def _engine() -> ConfiguratorEngine:
    return ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_test_catalog()))


def test_recommendation_stays_within_budget() -> None:
    engine = _engine()
    response = engine.recommend(
        ConfigurationRequest(
            budget=120000,
            purpose=Purpose.GAMING,
            preferred_brand="nvidia",
            target_resolution="1440p",
        )
    )

    assert response.total_price <= response.budget
    assert len(response.components) == 7


def test_recommendation_includes_alternatives() -> None:
    engine = _engine()
    response = engine.recommend(
        ConfigurationRequest(
            budget=120000,
            purpose=Purpose.GAMING,
            preferred_brand="any",
        )
    )

    assert response.alternatives is not None
    assert response.alternatives.pricier is not None
    assert response.alternatives.pricier.total_price > response.total_price
    if response.alternatives.cheaper is not None:
        assert response.alternatives.cheaper.total_price < response.total_price


def test_compatibility_is_reported() -> None:
    engine = _engine()
    response = engine.recommend(
        ConfigurationRequest(
                budget=120000,
                purpose=Purpose.WORK,
                preferred_brand="intel",
                needs_wifi=False,
            )
        )

    component_types = {component.type for component in response.components}
    assert ComponentType.CPU in component_types
    assert ComponentType.MOTHERBOARD in component_types
    assert any("socket" in check.lower() for check in response.compatibility_checks)


def test_too_low_budget_raises_budget_constraint_error() -> None:
    engine = _engine()
    with pytest.raises(ConfiguratorEngine.BudgetConstraintError):
        engine.recommend(
            ConfigurationRequest(
                budget=30000,
                purpose=Purpose.GAMING,
                preferred_brand="nvidia",
                target_resolution="1440p",
            )
        )


def test_socket_alias_and_supported_sockets_are_supported() -> None:
    engine = _engine()
    cpu = next(option for option in _test_catalog()[ComponentType.CPU] if option.socket == "LGA1700")
    motherboard = ComponentOption(
        type=ComponentType.MOTHERBOARD,
        model="Alias Board",
        brand="test",
        price=15000,
        score_gaming=7.0,
        score_work=7.0,
        score_study=7.0,
        score_general=7.0,
        supported_sockets=("Socket V",),
        ram_type="DDR5",
    )

    assert engine._is_socket_compatible(cpu, motherboard)  # type: ignore[attr-defined]


def test_minimum_performance_requirement_is_enforced() -> None:
    engine = _engine()
    with pytest.raises(ConfiguratorEngine.PerformanceConstraintError):
        engine.recommend(
            ConfigurationRequest(
                budget=120000,
                purpose=Purpose.GAMING,
                preferred_brand="any",
                target_resolution="4k",
                minimum_performance="high",
            )
        )


def test_minimum_ram_requirement_is_enforced() -> None:
    engine = _engine()
    response = engine.recommend(
        ConfigurationRequest(budget=120000, purpose=Purpose.WORK, min_ram_gb=32)
    )
    ram = next(component for component in response.components if component.type == ComponentType.RAM)
    assert "32GB" in ram.model


def test_too_high_ram_requirement_raises_error() -> None:
    engine = _engine()
    with pytest.raises(ConfiguratorEngine.PreferenceConstraintError):
        engine.recommend(
            ConfigurationRequest(
                budget=120000,
                purpose=Purpose.GAMING,
                min_ram_gb=64,
            )
        )


def test_too_high_vram_requirement_raises_error() -> None:
    engine = _engine()
    with pytest.raises(ConfiguratorEngine.PreferenceConstraintError):
        engine.recommend(
            ConfigurationRequest(
                budget=120000,
                purpose=Purpose.GAMING,
                min_vram_gb=24,
            )
        )
