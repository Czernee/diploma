from configurator.catalog import ComponentOption, InMemoryCatalogProvider
from configurator.engine import ConfiguratorEngine
from configurator.llm import ConfiguratorAssistant
from configurator.models import (
    AssistantMessage,
    ComponentType,
    ConfiguratorAssistantRequest,
)


class FakeLLMClient:
    model = "fake-open-llm"

    def __init__(self, extracted: dict):
        self.extracted = extracted
        self.extract_called = False
        self.explain_called = False

    def extract_request(self, message: str, history: list[AssistantMessage]) -> dict:
        self.extract_called = True
        return self.extracted

    def answer_question(self, message: str, history: list[AssistantMessage]) -> str:
        return "Это ответ чат-LLM на русском языке."

    def explain_recommendation(self, message, config_request, recommendation) -> str:
        self.explain_called = True
        return "LLM поняла запрос и объяснила подобранную конфигурацию."


def _catalog() -> dict[ComponentType, list[ComponentOption]]:
    return {
        ComponentType.CPU: [
            ComponentOption(ComponentType.CPU, "AMD Ryzen 5 5600", "amd", 11000, 7.6, 7.2, 7.0, 7.2, socket="AM4", cpu_tdp=65),
        ],
        ComponentType.GPU: [
            ComponentOption(ComponentType.GPU, "NVIDIA RTX 4060", "nvidia", 32000, 8.0, 7.0, 6.5, 7.0, gpu_tdp=115),
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


def test_assistant_turns_natural_language_into_recommendation() -> None:
    llm = FakeLLMClient(
        {
            "intent": "recommendation",
            "budget": 120000,
            "purpose": "gaming",
            "target_resolution": "1440p",
            "gpu_brand_preference": "nvidia",
            "min_ram_gb": 32,
        }
    )
    assistant = ConfiguratorAssistant(
        llm
    )
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(message="Собери игровой ПК до 120 тысяч для 1440p"),
        engine,
    )

    assert response.mode == "recommendation"
    assert response.llm_used is True
    assert response.llm_model == "fake-open-llm"
    assert response.extracted_request is not None
    assert response.extracted_request.budget == 120000
    assert response.recommendation is not None
    assert response.recommendation.total_price <= 120000
    assert "AMD Ryzen 5 5600" in response.answer
    assert "NVIDIA RTX 4060" in response.answer
    assert "LLM поняла запрос" not in response.answer
    assert llm.explain_called is False


def test_assistant_answers_general_chat_question() -> None:
    assistant = ConfiguratorAssistant(FakeLLMClient({"intent": "chat"}))
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(message="Объясни, как работает конфигуратор"),
        engine,
    )

    assert response.mode == "chat"
    assert response.recommendation is None
    assert "LLM" in response.answer


def test_assistant_asks_for_budget_when_recommendation_has_no_budget() -> None:
    assistant = ConfiguratorAssistant(FakeLLMClient({"intent": "recommendation", "purpose": "gaming"}))
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(message="Собери игровой ПК"),
        engine,
    )

    assert response.mode == "chat"
    assert response.recommendation is None
    assert "бюджет" in response.answer.lower()


def test_assistant_does_not_invent_products_for_vague_pc_request_without_budget() -> None:
    assistant = ConfiguratorAssistant(FakeLLMClient({"intent": "chat"}))
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(
            message="хочу простой компик для работы. чтобы был красненьким и красивеньким!! что посоветуешь?"
        ),
        engine,
    )

    assert response.mode == "chat"
    assert response.recommendation is None
    assert "бюджет" in response.answer.lower()
    assert "каталог" in response.answer.lower()
    assert "acer" not in response.answer.lower()
    assert "lenovo" not in response.answer.lower()
    assert "hp" not in response.answer.lower()


def test_assistant_builds_cheapest_pc_from_catalog_without_inventing_products() -> None:
    assistant = ConfiguratorAssistant(FakeLLMClient({"intent": "chat"}))
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(
            message="\u043c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u043e \u0434\u0435\u0448\u0435\u0432\u044b\u0439 \u043a\u043e\u043c\u043f. \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438 \u0432\u0430\u0440\u0438\u0430\u043d\u0442\u044b"
        ),
        engine,
    )

    assert response.mode == "recommendation"
    assert response.llm_used is False
    assert response.extracted_request is not None
    assert response.recommendation is not None
    assert response.extracted_request.budget >= response.recommendation.total_price
    assert "AMD Ryzen 5 5600" in response.answer
    assert "NVIDIA RTX 4060" in response.answer
    assert "Intel Celeron" not in response.answer
    assert "Zotac" not in response.answer
    assert "EVGA" not in response.answer
    assert "WD Blue SN550" not in response.answer


def test_assistant_uses_fast_path_for_simple_media_pc_request_with_budget() -> None:
    llm = FakeLLMClient({"intent": "chat"})
    assistant = ConfiguratorAssistant(llm)
    engine = ConfiguratorEngine(catalog_provider=InMemoryCatalogProvider(_catalog()))

    response = assistant.handle(
        ConfiguratorAssistantRequest(
            message="\u0445\u043e\u0447\u0443 \u043a\u043e\u043c\u043f\u0438\u043a \u0434\u043b\u044f \u0441\u0435\u0440\u0438\u0430\u043b\u043e\u0432 \u0434\u043e 80\u043a"
        ),
        engine,
    )

    assert response.mode == "recommendation"
    assert response.llm_used is False
    assert llm.extract_called is False
    assert response.extracted_request is not None
    assert response.extracted_request.budget == 80000
    assert response.recommendation is not None
    assert response.recommendation.total_price <= 80000
