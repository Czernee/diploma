from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from .engine import ConfiguratorEngine
from .models import (
    AssistantMessage,
    ConfigurationRequest,
    ConfigurationResponse,
    ConfiguratorAssistantRequest,
    ConfiguratorAssistantResponse,
    PerformanceEstimate,
    Purpose,
)

# Имена переменных окружения вынесены отдельно, чтобы было понятно,
# чем управляется подключение к локальной LLM Ollama.
OLLAMA_BASE_URL_ENV = "OLLAMA_BASE_URL"
OLLAMA_MODEL_ENV = "OLLAMA_MODEL"
OLLAMA_TIMEOUT_ENV = "OLLAMA_TIMEOUT_SECONDS"

# Значения по умолчанию для локального запуска без дополнительной настройки.
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b-instruct-q4_0"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = "12"

# Параметры HTTP-запроса к Ollama.
OLLAMA_CHAT_ENDPOINT = "/api/chat"
OLLAMA_JSON_FORMAT = "json"
LLM_TEMPERATURE = 0.2
LLM_HISTORY_LIMIT = 6

# Значения по умолчанию для сценария "подбери самый дешевый ПК".
CHEAPEST_REQUEST_BUDGET = 30_000
DEFAULT_TARGET_RESOLUTION = "1080p"
DEFAULT_BRAND_PREFERENCE = "any"
DEFAULT_MIN_RAM_GB = 0
DEFAULT_MIN_VRAM_GB = 0

# Ограничения для безопасного преобразования ответа LLM в ConfigurationRequest.
ALLOWED_TARGET_RESOLUTIONS = {"1080p", "1440p", "4k"}
ALLOWED_CPU_BRANDS = {"intel", "amd", "any"}
ALLOWED_GPU_BRANDS = {"nvidia", "amd", "intel", "any"}
ALLOWED_PREFERRED_BRANDS = {"intel", "amd", "nvidia", "any"}

# Настройки извлечения бюджета из свободного текста пользователя.
MIN_REASONABLE_BUDGET = 30_000
BUDGET_THOUSAND_MULTIPLIER = 1_000
BUDGET_THOUSANDS_PATTERN = re.compile(r"(?:до|за|бюджет)?\s*(\d{2,4})\s*(?:тыс|тысяч|к|k)\b")
BUDGET_FULL_AMOUNT_PATTERN = re.compile(r"\b\d[\d ]{4,}\b")

# Маркеры intent='recommendation'. Они помогают не зависеть полностью от LLM,
# если пользователь явно просит подобрать ПК естественным русским текстом.
RECOMMENDATION_KEYWORDS = (
    "собери",
    "подбери",
    "подобрать",
    "предложи",
    "посоветуй",
    "посоветуешь",
    "что посоветуешь",
    "варианты",
    "сборк",
    "конфигурац",
    "игровой пк",
    "рабочий пк",
    "дешевый пк",
    "дешевый комп",
    "бюджетный пк",
    "бюджетный комп",
    "максимально дешев",
    "самый дешев",
    "компик",
    "компьютер для",
    "пк для",
    "хочу компьютер",
    "хочу пк",
    "хочу комп",
    "нужен компьютер",
    "нужен пк",
    "нужен комп",
    "компьютер до",
    "пк до",
)
RECOMMENDATION_COMPUTER_WORD_PATTERN = re.compile(r"\b(пк|комп|компьютер)\b")
RECOMMENDATION_ACTION_MARKERS = (
    "предлож",
    "вариант",
    "подбор",
    "дешев",
    "бюджет",
    "для работы",
    "для игр",
    "для учебы",
)
FAST_RULE_BASED_RECOMMENDATION_MARKERS = (
    "компик",
    "дешев",
    "бюджет",
    "сериал",
    "фильм",
    "кино",
    "ютуб",
    "youtube",
    "браузер",
    "офис",
    "учеб",
    "работ",
)

# Отдельные маркеры для запроса без бюджета, где пользователь явно хочет минимум цены.
CHEAPEST_REQUEST_MARKERS = (
    "максимально дешев",
    "самый дешев",
    "самую дешев",
    "минимальн",
    "дешевый",
    "дешевле",
    "бюджетный",
    "бюджетн",
)

# Маркеры для простого rule-based извлечения назначения, разрешения и Wi-Fi
# в сценарии самого дешевого ПК, где LLM не вызывается.
WORK_PURPOSE_MARKERS = ("работ",)
GAMING_PURPOSE_MARKERS = ("игр", "гейм")
STUDY_PURPOSE_MARKERS = ("учеб", "учебы")
LIGHT_USAGE_PURPOSE_MARKERS = ("сериал", "фильм", "кино", "ютуб", "youtube", "браузер", "интернет")
FOUR_K_RESOLUTION_MARKERS = ("4k", "4к")
TWO_K_RESOLUTION_MARKERS = ("1440", "2k", "2к")
WIFI_MARKERS = ("wi-fi", "wifi", "вайфай")
NVIDIA_GPU_MARKERS = ("nvidia", "нвидиа", "geforce", "rtx")
AMD_GPU_MARKERS = ("radeon", "rx ")
INTEL_GPU_MARKERS = ("intel arc", "arc a")
INTEL_CPU_MARKERS = ("intel", "core i3", "core i5", "core i7", "core i9", "celeron", "pentium")
AMD_CPU_MARKERS = ("ryzen", "amd")
RAM_CAPACITY_PATTERN = re.compile(r"(\d{1,3})\s*(?:гб|gb)\s*(?:ram|озу|оператив)")
VRAM_CAPACITY_PATTERN = re.compile(r"(\d{1,3})\s*(?:гб|gb)\s*(?:vram|видеопам)")

# Если LLM на обычный вопрос ответила слишком уклончиво, эти маркеры помогают
# заменить ответ заранее подготовленным объяснением компонента.
UNCERTAIN_CHAT_ANSWER_MARKERS = ("уточните", "укажите бюджет", "могу ли я помочь")
TRUE_BOOL_MARKERS = {"true", "yes", "1", "да", "нужен", "нужно"}

# Процент показывается пользователю как понятный score, а не как внутренняя ML-метрика.
MATCH_SCORE_PERCENT_MULTIPLIER = 100

# Системные prompt'ы вынесены в константы: так проще объяснить,
# какую роль выполняет LLM на каждом шаге.
EXTRACT_REQUEST_SYSTEM_PROMPT = (
    "Ты анализируешь запрос пользователя для магазина компьютерных комплектующих. "
    "Верни только JSON без markdown. Если пользователь просит подобрать или собрать ПК, "
    "intent='recommendation'. Если это просто вопрос, intent='chat'. "
    "Если пользователь спрашивает, зачем нужен компонент или как он работает, это intent='chat'. "
    "Допустимые поля JSON: intent, budget, purpose, target_resolution, "
    "minimum_performance, needs_wifi, cpu_brand_preference, gpu_brand_preference, "
    "preferred_brand, min_ram_gb, min_vram_gb. "
    "purpose: gaming|work|study|general. target_resolution: 1080p|1440p|4k. "
    "minimum_performance: entry|mid|high|null. Бюджет указывай в RUB числом. "
    "Если значение не указано, используй null. Не выдумывай параметры."
)

CHAT_SYSTEM_PROMPT = (
    "Ты русскоязычный ИИ-помощник интернет-магазина компьютерной техники. "
    "Отвечай кратко, понятно и честно. Помогай выбрать комплектующие, объясняй "
    "назначение сервисов, корзины, заказов и конфигуратора. Не выдумывай товары, цены "
    "и наличие. Если пользователь спрашивает про конкретный компонент, например блок питания, "
    "процессор или видеокарту, объясни его роль напрямую. Проси бюджет только тогда, когда "
    "пользователь явно хочет собрать или подобрать ПК."
)

EXPLAIN_RECOMMENDATION_SYSTEM_PROMPT = (
    "Ты ИИ-помощник магазина компьютерной техники. Объясни результат подбора на русском. "
    "Не добавляй товаров, которых нет в переданном списке. Не называй R2, MAE и внутренние "
    "метрики обучения. Объясни, что техническая совместимость проверена экспертными правилами, "
    "а вариант выбран среди допустимых сборок."
)

BUDGET_REQUIRED_ANSWER = (
    "Я могу подобрать такой компьютер, но мне нужен бюджет. "
    "Я выбираю только из товаров, которые есть в каталоге магазина, поэтому не буду советовать "
    "несуществующие ноутбуки, бренды или цвета. Напишите, например: "
    "'простой ПК для работы до 70000 рублей, желательно красивый корпус'. "
    "Если цвет корпуса важен, я учту это только в пределах характеристик, которые есть у товаров каталога."
)

DIRECT_COMPONENT_ANSWERS = (
    (
        "блок питания",
        "Блок питания преобразует электричество из розетки в напряжения, которые нужны компонентам ПК. "
        "Он должен иметь достаточную мощность для процессора и видеокарты, а также запас по нагрузке. "
        "Если блок питания слабый или некачественный, компьютер может выключаться, работать нестабильно "
        "или даже повредить комплектующие.",
    ),
    (
        "процессор",
        "Процессор выполняет основные вычисления компьютера и влияет на скорость работы системы, игр, "
        "программ и фоновых задач. При подборе важно учитывать сокет, производительность, TDP и баланс "
        "с видеокартой.",
    ),
    (
        "видеокарт",
        "Видеокарта отвечает за обработку графики: игры, 3D, монтаж, рендеринг и работу с видеопамятью. "
        "Для игр особенно важны производительность GPU, объем VRAM, энергопотребление и соответствие "
        "выбранному разрешению.",
    ),
)

# LLM может слишком смело интерпретировать "игровой ПК для 1440p" как явное
# требование minimum_performance=mid. На практике пользователь задал сценарий и
# разрешение, а не порог производительности, поэтому порог принимаем только по
# прямым словам вроде "средний", "высокий" или "базовый".
ENTRY_PERFORMANCE_MARKERS = ("базов", "начальн", "entry")
MID_PERFORMANCE_MARKERS = ("средн", "mid")
HIGH_PERFORMANCE_MARKERS = ("высок", "топов", "мощн", "high")


class LLMUnavailableError(RuntimeError):
    """Ошибка внешней LLM, чтобы сервис мог явно отличить ее от ошибок конфигуратора."""


class LLMClient(Protocol):
    """Протокол клиента LLM: его можно заменить fake-клиентом в тестах."""

    model: str

    def extract_request(self, message: str, history: list[AssistantMessage]) -> dict[str, Any]:
        ...

    def answer_question(self, message: str, history: list[AssistantMessage]) -> str:
        ...

    def explain_recommendation(
        self,
        message: str,
        config_request: ConfigurationRequest,
        recommendation: ConfigurationResponse,
    ) -> str:
        ...


@dataclass(frozen=True)
class OllamaSettings:
    """Настройки подключения к локальной Ollama-модели."""

    base_url: str = os.getenv(OLLAMA_BASE_URL_ENV, DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    model: str = os.getenv(OLLAMA_MODEL_ENV, DEFAULT_OLLAMA_MODEL)
    timeout: float = float(os.getenv(OLLAMA_TIMEOUT_ENV, DEFAULT_OLLAMA_TIMEOUT_SECONDS))


class OllamaLLMClient:
    """Тонкая обертка над HTTP API Ollama."""

    def __init__(self, settings: OllamaSettings | None = None):
        self._settings = settings or OllamaSettings()
        self.model = self._settings.model

    def extract_request(self, message: str, history: list[AssistantMessage]) -> dict[str, Any]:
        # Первый режим LLM: не отвечает пользователю, а превращает свободный текст
        # в структурированный JSON для ML-конфигуратора.
        response = self._chat(
            [
                {"role": "system", "content": EXTRACT_REQUEST_SYSTEM_PROMPT},
                *self._history_messages(history),
                {"role": "user", "content": message},
            ],
            json_mode=True,
        )
        return _parse_json_object(response)

    def answer_question(self, message: str, history: list[AssistantMessage]) -> str:
        # Второй режим LLM: обычный чат-ответ, когда пользователь спрашивает
        # не подбор конкретной сборки, а объяснение или консультацию.
        return self._chat(
            [
                {"role": "system", "content": CHAT_SYSTEM_PROMPT},
                *self._history_messages(history),
                {"role": "user", "content": message},
            ],
            json_mode=False,
        )

    def explain_recommendation(
        self,
        message: str,
        config_request: ConfigurationRequest,
        recommendation: ConfigurationResponse,
    ) -> str:
        # Этот метод оставлен как отдельный режим объяснения результата.
        # В основном сценарии ответ формируется безопасно без LLM, чтобы модель
        # не добавила товары, которых нет в каталоге.
        components = [
            {
                "type": component.type.value if hasattr(component.type, "value") else str(component.type),
                "model": component.model,
                "brand": component.brand,
                "price": component.price,
            }
            for component in recommendation.components
        ]
        return self._chat(
            [
                {"role": "system", "content": EXPLAIN_RECOMMENDATION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "user_message": message,
                            "request": config_request.model_dump(mode="json"),
                            "total_price": recommendation.total_price,
                            "performance": recommendation.performance_estimate.value,
                            "match_score_percent": round(recommendation.ml_score * MATCH_SCORE_PERCENT_MULTIPLIER),
                            "components": components,
                            "compatibility_checks": recommendation.compatibility_checks,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            json_mode=False,
        )

    def _chat(self, messages: list[dict[str, str]], json_mode: bool) -> str:
        # Единая точка вызова Ollama. Все настройки запроса собраны в константах,
        # чтобы не держать endpoint, temperature и формат ответа прямо в теле метода.
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": LLM_TEMPERATURE,
            },
        }
        if json_mode:
            payload["format"] = OLLAMA_JSON_FORMAT

        try:
            response = httpx.post(
                f"{self._settings.base_url}{OLLAMA_CHAT_ENDPOINT}",
                json=payload,
                timeout=self._settings.timeout,
            )
            response.raise_for_status()
            body = response.json()
            content = body.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise LLMUnavailableError("LLM returned an empty response")
            return content.strip()
        except httpx.HTTPError as error:
            raise LLMUnavailableError(f"LLM service is unavailable: {error}") from error

    def _history_messages(self, history: list[AssistantMessage]) -> list[dict[str, str]]:
        # История ограничивается последними сообщениями, чтобы не раздувать prompt
        # и не отправлять в LLM слишком большой контекст.
        return [{"role": item.role, "content": item.content} for item in history[-LLM_HISTORY_LIMIT:]]


class ConfiguratorAssistant:
    """Оркестратор: решает, когда отвечать чатом, а когда запускать ML-подбор."""

    def __init__(self, llm_client: LLMClient | None = None):
        self._llm = llm_client or OllamaLLMClient()

    def handle(
        self,
        payload: ConfiguratorAssistantRequest,
        engine: ConfiguratorEngine,
    ) -> ConfiguratorAssistantResponse:
        # Быстрые эвристики нужны как страховка: LLM может ошибиться с intent,
        # а явный запрос "подбери ПК" должен попадать в конфигуратор.
        looks_like_recommendation = _looks_like_recommendation_request(payload.message)
        has_budget = _budget_from_message(payload.message) is not None

        # Особый безопасный сценарий: пользователь просит максимально дешевый ПК
        # без конкретного бюджета. В таком случае берем минимальный стартовый бюджет,
        # а если каталог дороже, engine сам подскажет минимально возможную сумму.
        if looks_like_recommendation and not has_budget and _looks_like_cheapest_request(payload.message):
            config_request = _cheapest_configuration_request(payload.message)
            config_request, recommendation = self._recommend_with_minimum_budget(engine, config_request)
            return ConfiguratorAssistantResponse(
                mode="recommendation",
                answer=self._safe_recommendation_answer(
                    config_request,
                    recommendation,
                    llm_used_for_understanding=False,
                ),
                extracted_request=config_request,
                recommendation=recommendation,
                llm_model=self._llm.model,
                llm_used=False,
            )

        # Если человек просит подобрать ПК, но не указал бюджет, лучше уточнить,
        # чем заставить LLM выдумывать условные модели и цены.
        if looks_like_recommendation and not has_budget:
            return ConfiguratorAssistantResponse(
                mode="chat",
                answer=_budget_required_answer(),
                llm_model=self._llm.model,
                llm_used=True,
            )

        # Для простых и частых запросов с явным бюджетом не ждем Ollama.
        # Например: "хочу компик для сериалов до 50к" полностью покрывается правилами:
        # бюджет, назначение и базовые пожелания извлекаются из текста, а товары выбирает engine.
        if looks_like_recommendation and has_budget and _should_use_fast_rule_based_recommendation(payload.message):
            config_request = self._to_configuration_request({}, payload.message)
            if config_request is not None:
                config_request, recommendation = self._recommend_with_minimum_budget(engine, config_request)
                return ConfiguratorAssistantResponse(
                    mode="recommendation",
                    answer=self._safe_recommendation_answer(
                        config_request,
                        recommendation,
                        llm_used_for_understanding=False,
                    ),
                    extracted_request=config_request,
                    recommendation=recommendation,
                    llm_model=self._llm.model,
                    llm_used=False,
                )

        # LLM используется здесь как NLU-слой: извлекает intent и параметры,
        # но не принимает финальное решение о товарах.
        try:
            extracted = self._llm.extract_request(payload.message, payload.history)
        except LLMUnavailableError:
            if looks_like_recommendation and has_budget:
                config_request = self._to_configuration_request({}, payload.message)
                if config_request is not None:
                    config_request, recommendation = self._recommend_with_minimum_budget(engine, config_request)
                    return ConfiguratorAssistantResponse(
                        mode="recommendation",
                        answer=self._safe_recommendation_answer(
                            config_request,
                            recommendation,
                            llm_used_for_understanding=False,
                        ),
                        extracted_request=config_request,
                        recommendation=recommendation,
                        llm_model=self._llm.model,
                        llm_used=False,
                    )
            raise
        intent = str(extracted.get("intent") or "chat").lower()
        direct_answer = _direct_component_answer(payload.message)

        # Для очевидных вопросов про компоненты возвращаем стабильный ответ,
        # чтобы модель не просила бюджет там, где он не нужен.
        if direct_answer and not looks_like_recommendation:
            return ConfiguratorAssistantResponse(
                mode="chat",
                answer=direct_answer,
                llm_model=self._llm.model,
                llm_used=True,
            )

        # Если LLM не распознала подбор, но эвристика видит явный запрос сборки,
        # исправляем intent в сторону recommendation.
        if intent != "recommendation" and looks_like_recommendation:
            intent = "recommendation"

        if intent != "recommendation":
            answer = self._llm.answer_question(payload.message, payload.history)
            return ConfiguratorAssistantResponse(
                mode="chat",
                answer=_repair_chat_answer(payload.message, answer),
                llm_model=self._llm.model,
                llm_used=True,
            )

        config_request = self._to_configuration_request(extracted, payload.message)
        if config_request is None:
            if not looks_like_recommendation:
                answer = self._llm.answer_question(payload.message, payload.history)
                return ConfiguratorAssistantResponse(
                    mode="chat",
                    answer=_repair_chat_answer(payload.message, answer),
                    llm_model=self._llm.model,
                    llm_used=True,
                )
            return ConfiguratorAssistantResponse(
                mode="chat",
                answer=_budget_required_answer(),
                llm_model=self._llm.model,
                llm_used=True,
            )

        # Финальный подбор всегда делает ConfiguratorEngine: он берет реальные товары
        # из каталога и проверяет совместимость экспертными правилами.
        recommendation = engine.recommend(config_request)
        answer = self._safe_recommendation_answer(config_request, recommendation)

        return ConfiguratorAssistantResponse(
            mode="recommendation",
            answer=answer,
            extracted_request=config_request,
            recommendation=recommendation,
            llm_model=self._llm.model,
            llm_used=True,
        )

    def _to_configuration_request(self, extracted: dict[str, Any], message: str) -> ConfigurationRequest | None:
        # Бюджет сначала ищется в исходном сообщении, потому что регулярное выражение
        # надежнее для русских форматов вроде "до 70 тыс". Если не нашли, берем JSON от LLM.
        budget = _budget_from_message(message) or _as_int(extracted.get("budget"))
        if budget is None:
            return None

        # Все значения от LLM валидируются whitelist'ами и enum'ами. Это защищает
        # backend от неожиданных строк и не дает LLM сломать контракт API.
        purpose = _purpose_from_message(message) or _enum_value(extracted.get("purpose"), Purpose, Purpose.GENERAL)
        minimum_performance = _minimum_performance_from_message(message)
        target_resolution = _target_resolution_from_message(message) or _one_of(
            extracted.get("target_resolution"),
            ALLOWED_TARGET_RESOLUTIONS,
            DEFAULT_TARGET_RESOLUTION,
        )
        cpu_brand = _cpu_brand_from_message(message) or _one_of(
            extracted.get("cpu_brand_preference"),
            ALLOWED_CPU_BRANDS,
            DEFAULT_BRAND_PREFERENCE,
        )
        gpu_brand = _gpu_brand_from_message(message) or _one_of(
            extracted.get("gpu_brand_preference"),
            ALLOWED_GPU_BRANDS,
            DEFAULT_BRAND_PREFERENCE,
        )
        preferred_brand = _one_of(extracted.get("preferred_brand"), ALLOWED_PREFERRED_BRANDS, DEFAULT_BRAND_PREFERENCE)
        min_ram_gb = _ram_capacity_from_message(message) or _as_int(extracted.get("min_ram_gb")) or DEFAULT_MIN_RAM_GB
        min_vram_gb = _vram_capacity_from_message(message) or _as_int(extracted.get("min_vram_gb")) or DEFAULT_MIN_VRAM_GB

        try:
            return ConfigurationRequest(
                budget=budget,
                purpose=purpose,
                preferred_brand=preferred_brand,
                needs_wifi=_needs_wifi_from_message(message),
                target_resolution=target_resolution,
                minimum_performance=minimum_performance,
                cpu_brand_preference=cpu_brand,
                gpu_brand_preference=gpu_brand,
                min_ram_gb=min_ram_gb,
                min_vram_gb=min_vram_gb,
            )
        except ValidationError as error:
            raise ConfiguratorEngine.PreferenceConstraintError(str(error)) from error

    def _recommend_with_minimum_budget(
        self,
        engine: ConfiguratorEngine,
        config_request: ConfigurationRequest,
    ) -> tuple[ConfigurationRequest, ConfigurationResponse]:
        # Для запроса "самый дешевый" стартуем с маленького бюджета. Если ниже
        # минимальной возможной сборки, engine вернет minimum_required_budget.
        try:
            return config_request, engine.recommend(config_request)
        except ConfiguratorEngine.BudgetConstraintError as error:
            adjusted_request = config_request.model_copy(update={"budget": error.minimum_required_budget})
            return adjusted_request, engine.recommend(adjusted_request)

    def _safe_recommendation_answer(
        self,
        config_request: ConfigurationRequest,
        recommendation: ConfigurationResponse,
        llm_used_for_understanding: bool = True,
    ) -> str:
        # Ответ по рекомендации формируется кодом, а не свободной генерацией LLM.
        # Поэтому здесь перечисляются только компоненты из результата engine.recommend().
        component_lines = "\n".join(
            f"- {component.type.value}: {component.model} ({component.brand}) - {component.price} RUB"
            for component in recommendation.components
        )
        checks = "\n".join(f"- {check}" for check in recommendation.compatibility_checks)
        source_note = (
            "Я учел ваш текстовый запрос и подобрал товары из каталога магазина. "
            if llm_used_for_understanding
            else "Я подобрал подходящий вариант из каталога магазина. "
        )

        return (
            "Я понял запрос и подобрал конфигурацию только из товаров, которые есть в каталоге.\n\n"
            f"Бюджет: {config_request.budget} RUB\n"
            f"Итоговая стоимость: {recommendation.total_price} RUB\n"
            f"Оценка соответствия требованиям: {round(recommendation.ml_score * MATCH_SCORE_PERCENT_MULTIPLIER)}%\n\n"
            "Выбранные товары:\n"
            f"{component_lines}\n\n"
            "Проверки совместимости:\n"
            f"{checks}\n\n"
            f"{source_note}Все позиции из списка можно использовать как готовую основу для корзины."
        )


def _parse_json_object(content: str) -> dict[str, Any]:
    # LLM иногда возвращает JSON в markdown-блоке. Перед парсингом убираем ```json.
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as error:
        raise LLMUnavailableError(f"LLM returned invalid JSON: {content[:200]}") from error
    if not isinstance(parsed, dict):
        raise LLMUnavailableError("LLM JSON response is not an object")
    return parsed


def _budget_required_answer() -> str:
    return BUDGET_REQUIRED_ANSWER


def _as_int(value: Any) -> int | None:
    # Приводит числа от LLM и строки пользователя к int. Например: "70 тыс" -> 70000.
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        normalized = value.lower().replace(" ", "").replace("_", "")
        normalized = normalized.replace("рублей", "").replace("руб", "").replace("rub", "")
        multiplier = BUDGET_THOUSAND_MULTIPLIER if normalized.endswith(("к", "k", "тысяч", "тыс")) else 1
        normalized = normalized.removesuffix("тысяч").removesuffix("тыс").rstrip("кk")
        digits = re.sub(r"[^\d]", "", normalized)
        return int(digits) * multiplier if digits else None
    return None


def _budget_from_message(message: str) -> int | None:
    # Извлекает бюджет из русской фразы. Это сделано отдельно от LLM,
    # потому что числа и "тыс" надежнее обрабатывать регулярками.
    normalized = _normalize_text(message)

    thousands_match = BUDGET_THOUSANDS_PATTERN.search(normalized)
    if thousands_match:
        return int(thousands_match.group(1)) * BUDGET_THOUSAND_MULTIPLIER

    full_amounts = [int(item.replace(" ", "")) for item in BUDGET_FULL_AMOUNT_PATTERN.findall(normalized)]
    reasonable = [amount for amount in full_amounts if amount >= MIN_REASONABLE_BUDGET]
    return max(reasonable) if reasonable else None


def _normalize_text(message: str) -> str:
    # Нормализация нужна для устойчивого поиска русских маркеров.
    return message.lower().replace("ё", "е").replace("\u00a0", " ")


def _purpose_from_message(message: str) -> Purpose | None:
    # Назначение лучше извлекать правилом из исходной фразы: это стабильнее, чем каждый раз ждать одинакового JSON от LLM.
    normalized = _normalize_text(message)
    if any(marker in normalized for marker in GAMING_PURPOSE_MARKERS):
        return Purpose.GAMING
    if any(marker in normalized for marker in WORK_PURPOSE_MARKERS):
        return Purpose.WORK
    if any(marker in normalized for marker in STUDY_PURPOSE_MARKERS):
        return Purpose.STUDY
    if any(marker in normalized for marker in LIGHT_USAGE_PURPOSE_MARKERS):
        return Purpose.GENERAL
    return None


def _should_use_fast_rule_based_recommendation(message: str) -> bool:
    # Быстрый путь нужен для типовых бытовых формулировок, где LLM может быть медленнее,
    # чем сам подбор. Сложные запросы без этих маркеров по-прежнему могут идти через LLM.
    normalized = _normalize_text(message)
    return any(marker in normalized for marker in FAST_RULE_BASED_RECOMMENDATION_MARKERS)


def _target_resolution_from_message(message: str) -> str | None:
    # Разрешение экрана часто пишут коротко: 1440p, 2K, 4K. Регулярная LLM здесь не обязательна.
    normalized = _normalize_text(message)
    if any(marker in normalized for marker in FOUR_K_RESOLUTION_MARKERS):
        return "4k"
    if any(marker in normalized for marker in TWO_K_RESOLUTION_MARKERS):
        return "1440p"
    if "1080" in normalized or "full hd" in normalized or "fhd" in normalized:
        return "1080p"
    return None


def _needs_wifi_from_message(message: str) -> bool:
    # Wi-Fi должен включаться только по явному упоминанию. Иначе LLM может ошибочно поставить True из-за слова "желательно".
    normalized = _normalize_text(message)
    return any(marker in normalized for marker in WIFI_MARKERS)


def _gpu_brand_from_message(message: str) -> str | None:
    # Бренд видеокарты является пользовательским предпочтением, поэтому фиксируем очевидные маркеры до JSON от LLM.
    normalized = _normalize_text(message)
    if any(marker in normalized for marker in NVIDIA_GPU_MARKERS):
        return "nvidia"
    if any(marker in normalized for marker in INTEL_GPU_MARKERS):
        return "intel"
    if any(marker in normalized for marker in AMD_GPU_MARKERS):
        return "amd"
    return None


def _cpu_brand_from_message(message: str) -> str | None:
    # CPU-бренд извлекаем только по характерным словам, чтобы не путать AMD-процессоры и AMD-видеокарты Radeon.
    normalized = _normalize_text(message)
    if any(marker in normalized for marker in INTEL_CPU_MARKERS):
        return "intel"
    if "ryzen" in normalized:
        return "amd"
    return None


def _ram_capacity_from_message(message: str) -> int | None:
    # Пример: "минимум 32 ГБ RAM" или "32gb оперативной памяти".
    match = RAM_CAPACITY_PATTERN.search(_normalize_text(message))
    return int(match.group(1)) if match else None


def _vram_capacity_from_message(message: str) -> int | None:
    # Пример: "12 ГБ VRAM" или "не меньше 8 ГБ видеопамяти".
    match = VRAM_CAPACITY_PATTERN.search(_normalize_text(message))
    return int(match.group(1)) if match else None


def _minimum_performance_from_message(message: str) -> PerformanceEstimate | None:
    # Не доверяем этому полю из JSON LLM без явного маркера в исходном тексте.
    # Иначе обычный запрос "для 1440p" превращается в жесткое требование mid/high
    # и может необоснованно завершиться ошибкой вместо подбора лучшего варианта.
    normalized = _normalize_text(message)
    if any(marker in normalized for marker in HIGH_PERFORMANCE_MARKERS):
        return PerformanceEstimate.HIGH
    if any(marker in normalized for marker in MID_PERFORMANCE_MARKERS):
        return PerformanceEstimate.MID
    if any(marker in normalized for marker in ENTRY_PERFORMANCE_MARKERS):
        return PerformanceEstimate.ENTRY
    return None


def _looks_like_recommendation_request(message: str) -> bool:
    # Быстрая проверка intent без LLM: пользователь просит подобрать/собрать ПК.
    normalized = _normalize_text(message)
    if any(keyword in normalized for keyword in RECOMMENDATION_KEYWORDS):
        return True

    computer_word = RECOMMENDATION_COMPUTER_WORD_PATTERN.search(normalized) is not None
    action_word = any(marker in normalized for marker in RECOMMENDATION_ACTION_MARKERS)
    return computer_word and action_word


def _looks_like_cheapest_request(message: str) -> bool:
    # Отдельно распознаем "дешево/бюджетно", чтобы не требовать бюджет повторно.
    normalized = _normalize_text(message)
    return any(marker in normalized for marker in CHEAPEST_REQUEST_MARKERS)


def _cheapest_configuration_request(message: str) -> ConfigurationRequest:
    # Rule-based запрос для самой дешевой сборки. LLM здесь не нужна:
    # безопаснее дать engine подобрать минимум из реального каталога.
    normalized = _normalize_text(message)
    purpose = Purpose.GENERAL
    if any(marker in normalized for marker in WORK_PURPOSE_MARKERS):
        purpose = Purpose.WORK
    elif any(marker in normalized for marker in GAMING_PURPOSE_MARKERS):
        purpose = Purpose.GAMING
    elif any(marker in normalized for marker in STUDY_PURPOSE_MARKERS):
        purpose = Purpose.STUDY

    target_resolution = DEFAULT_TARGET_RESOLUTION
    if any(marker in normalized for marker in FOUR_K_RESOLUTION_MARKERS):
        target_resolution = "4k"
    elif any(marker in normalized for marker in TWO_K_RESOLUTION_MARKERS):
        target_resolution = "1440p"

    return ConfigurationRequest(
        budget=CHEAPEST_REQUEST_BUDGET,
        purpose=purpose,
        preferred_brand=DEFAULT_BRAND_PREFERENCE,
        needs_wifi=any(marker in normalized for marker in WIFI_MARKERS),
        target_resolution=target_resolution,
        minimum_performance=None,
        cpu_brand_preference=DEFAULT_BRAND_PREFERENCE,
        gpu_brand_preference=DEFAULT_BRAND_PREFERENCE,
        min_ram_gb=DEFAULT_MIN_RAM_GB,
        min_vram_gb=DEFAULT_MIN_VRAM_GB,
    )


def _repair_chat_answer(message: str, answer: str) -> str:
    # Защита от неудачного чат-ответа: если модель вместо объяснения компонента
    # просит уточнить бюджет, заменяем ответ на заранее подготовленный текст.
    normalized_answer = answer.lower()
    looks_uncertain = any(word in normalized_answer for word in UNCERTAIN_CHAT_ANSWER_MARKERS)

    direct_answer = _direct_component_answer(message)
    if looks_uncertain and direct_answer:
        return direct_answer

    return answer


def _direct_component_answer(message: str) -> str | None:
    # Готовые объяснения для частых вопросов. Это делает ответы стабильнее
    # и уменьшает риск, что LLM уйдет в подбор там, где нужен простой ответ.
    normalized_message = _normalize_text(message)
    for marker, answer in DIRECT_COMPONENT_ANSWERS:
        if marker in normalized_message:
            return answer
    return None


def _as_bool(value: Any) -> bool:
    # LLM может вернуть булево значение строкой, поэтому явно поддерживаем несколько форм.
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in TRUE_BOOL_MARKERS
    return False


def _one_of(value: Any, allowed: set[str], default: str) -> str:
    # Whitelist-защита для строковых параметров от LLM.
    if not isinstance(value, str):
        return default
    normalized = value.strip().lower()
    return normalized if normalized in allowed else default


def _enum_value(value: Any, enum_type: type[Purpose], default: Purpose) -> Purpose:
    # Преобразование строки LLM в enum с безопасным fallback.
    if not isinstance(value, str):
        return default
    try:
        return enum_type(value.strip().lower())
    except ValueError:
        return default


def _optional_enum_value(value: Any, enum_type: type[PerformanceEstimate]) -> PerformanceEstimate | None:
    # Опциональная enum-оценка производительности: если LLM не указала значение,
    # оставляем None, чтобы конфигуратор сам выбрал подходящий уровень.
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return None
    try:
        return enum_type(value.strip().lower())
    except ValueError:
        return None
