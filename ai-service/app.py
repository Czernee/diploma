import logging
import os

import httpx
from fastapi import FastAPI, Header, HTTPException

from configurator.catalog import CatalogLoadError
from configurator.engine import ConfiguratorEngine
from configurator.llm import ConfiguratorAssistant, LLMUnavailableError
from configurator.models import (
    ConfigurationRequest,
    ConfigurationResponse,
    ConfiguratorAssistantRequest,
    ConfiguratorAssistantResponse,
)

app = FastAPI(title="ai-service", version="0.1.0")
engine = ConfiguratorEngine()
assistant = ConfiguratorAssistant()
logger = logging.getLogger(__name__)
ORDER_SERVICE_URL = (os.getenv("ORDER_SERVICE_URL") or "").rstrip("/")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/api/configurator/model")
def model_info() -> dict[str, object]:
    return engine.model_info()


@app.post("/api/configurator/recommend", response_model=ConfigurationResponse)
def recommend_configuration(
    payload: ConfigurationRequest,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> ConfigurationResponse:
    try:
        response = engine.recommend(payload)
        _persist_configuration_history(response, x_user_id, x_user_name, x_user_role)
        return response
    except CatalogLoadError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Каталог товаров временно недоступен. Попробуйте повторить подбор позже.",
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
def generate_configuration(
    payload: ConfigurationRequest,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> ConfigurationResponse:
    # Backward-compatible alias for older clients.
    return recommend_configuration(payload, x_user_id, x_user_name, x_user_role)


@app.post("/api/configurator/assistant", response_model=ConfiguratorAssistantResponse)
def assistant_message(
    payload: ConfiguratorAssistantRequest,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> ConfiguratorAssistantResponse:
    try:
        response = assistant.handle(payload, engine)
        if response.recommendation is not None:
            _persist_configuration_history(response.recommendation, x_user_id, x_user_name, x_user_role)
        return response
    except LLMUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "message": (
                    "LLM-сервис временно недоступен. Проверьте, что Ollama запущена "
                    "и модель загружена."
                ),
                "reason": str(error),
            },
        ) from error
    except CatalogLoadError as error:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Каталог товаров временно недоступен. Попробуйте повторить подбор позже.",
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


def _persist_configuration_history(
    response: ConfigurationResponse,
    user_id: str | None,
    username: str | None,
    role: str | None,
) -> None:
    if not ORDER_SERVICE_URL or not user_id or not username:
        return

    try:
        httpx.post(
            f"{ORDER_SERVICE_URL}/api/orders/configurations",
            json=response.model_dump(mode="json"),
            headers={
                "X-User-Id": user_id,
                "X-User-Name": username,
                "X-User-Role": role or "USER",
            },
            timeout=3.0,
        ).raise_for_status()
    except Exception as error:
        logger.warning("Failed to persist configuration history: %s", error)
