from fastapi import FastAPI, HTTPException

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
    except ConfiguratorEngine.BudgetConstraintError as error:
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(error),
                "minimumRequiredBudget": error.minimum_required_budget,
                "providedBudget": error.budget,
            },
        ) from error


@app.post("/api/configurator/generate", response_model=ConfigurationResponse)
def generate_configuration(payload: ConfigurationRequest) -> ConfigurationResponse:
    # Backward-compatible alias for older clients.
    return recommend_configuration(payload)
