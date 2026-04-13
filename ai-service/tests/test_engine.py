from configurator.engine import ConfiguratorEngine
from configurator.models import ComponentType, ConfigurationRequest, Purpose
import pytest


def test_recommendation_stays_within_budget() -> None:
    engine = ConfiguratorEngine()
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


def test_compatibility_is_reported() -> None:
    engine = ConfiguratorEngine()
    response = engine.recommend(
        ConfigurationRequest(
                budget=120000,
                purpose=Purpose.WORK,
                preferred_brand="intel",
                needs_wifi=True,
            )
        )

    component_types = {component.type for component in response.components}
    assert ComponentType.CPU in component_types
    assert ComponentType.MOTHERBOARD in component_types
    assert any("socket" in check.lower() for check in response.compatibility_checks)


def test_too_low_budget_raises_budget_constraint_error() -> None:
    engine = ConfiguratorEngine()
    with pytest.raises(ConfiguratorEngine.BudgetConstraintError):
        engine.recommend(
            ConfigurationRequest(
                budget=30000,
                purpose=Purpose.GAMING,
                preferred_brand="nvidia",
                target_resolution="1440p",
            )
        )
