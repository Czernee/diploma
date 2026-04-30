from fastapi import FastAPI, HTTPException

from configurator.catalog import CatalogLoadError
from configurator.engine import ConfiguratorEngine
from configurator.models import ConfigurationRequest, ConfigurationResponse

app = FastAPI(title="ai-service", version="0.1.0")
engine = ConfiguratorEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post("/api/configurator/recommend", response_model=ConfigurationResponse)
def recommend_configuration(payload: ConfigurationRequest) -> ConfigurationResponse:
    try:
        return engine.recommend(payload)
    except CatalogLoadError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Configurator catalog is unavailable",
                "reason": str(error),
            },
        ) from error
    except ConfiguratorEngine.BudgetConstraintError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(error),
                "minimumRequiredBudget": error.minimum_required_budget,
                "providedBudget": error.budget,
            },
        ) from error
    except ConfiguratorEngine.PreferenceConstraintError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(error),
            },
        ) from error
    except ConfiguratorEngine.PerformanceConstraintError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(error),
                "minimumPerformance": error.minimum_requested.value,
                "actualPerformance": error.actual.value,
            },
        ) from error


@app.post("/api/configurator/generate", response_model=ConfigurationResponse)
def generate_configuration(payload: ConfigurationRequest) -> ConfigurationResponse:
    # Backward-compatible alias for older clients.
    return recommend_configuration(payload)
