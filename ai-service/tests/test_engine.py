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


def _high_end_catalog() -> dict[ComponentType, list[ComponentOption]]:
    catalog = _test_catalog()
    catalog[ComponentType.CPU] = [
        ComponentOption(ComponentType.CPU, "Core i3-12100F", "intel", 9000, 6.9, 6.6, 6.4, 6.5, socket="LGA1700", cpu_tdp=58),
        ComponentOption(ComponentType.CPU, "Core i7-14700F", "intel", 36000, 9.1, 9.2, 8.6, 8.9, socket="LGA1700", cpu_tdp=125),
    ]
    catalog[ComponentType.GPU] = [
        ComponentOption(ComponentType.GPU, "GeForce RTX 4090", "nvidia", 190000, 9.95, 9.8, 8.0, 9.4, gpu_tdp=450, notes=("24GB VRAM",)),
        ComponentOption(ComponentType.GPU, "GeForce RTX 4070 Super", "nvidia", 65000, 9.0, 8.2, 7.2, 8.4, gpu_tdp=220, notes=("12GB VRAM",)),
    ]
    catalog[ComponentType.RAM] = [
        ComponentOption(ComponentType.RAM, "16GB DDR4 3200", "kingston", 4500, 7.1, 7.1, 7.0, 7.1, ram_type="DDR4", notes=("16GB total",)),
        ComponentOption(ComponentType.RAM, "32GB DDR4 3600", "kingston", 8500, 8.2, 8.4, 7.7, 8.0, ram_type="DDR4", notes=("32GB total",)),
    ]
    catalog[ComponentType.PSU] = [
        ComponentOption(ComponentType.PSU, "1000W 80+ Gold PSU", "corsair", 18000, 9.2, 9.2, 8.5, 9.0, psu_watts=1000),
    ]
    return catalog


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
    assert response.alternatives.cheaper is not None or response.alternatives.pricier is not None
    assert response.ml_score > 0
    assert any("Оценка соответствия требованиям" in item for item in response.explanation)
    if response.alternatives.cheaper is not None:
        assert response.alternatives.cheaper.total_price < response.total_price
    if response.alternatives.pricier is not None:
        assert response.alternatives.pricier.total_price > response.total_price


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
    assert any("сокет" in check.lower() for check in response.compatibility_checks)


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


def test_high_end_gpu_is_not_paired_with_budget_cpu() -> None:
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_high_end_catalog()))
    response = engine.recommend(
        ConfigurationRequest(
            budget=280000,
            purpose=Purpose.GAMING,
            target_resolution="4k",
            preferred_brand="nvidia",
        )
    )

    cpu = next(component for component in response.components if component.type == ComponentType.CPU)
    gpu = next(component for component in response.components if component.type == ComponentType.GPU)
    ram = next(component for component in response.components if component.type == ComponentType.RAM)

    if gpu.model == "GeForce RTX 4090":
        assert cpu.model == "Core i7-14700F"
        assert "32GB" in ram.model
    assert any("Баланс CPU/GPU" in check for check in response.compatibility_checks)
