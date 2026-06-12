from __future__ import annotations

import hashlib
import itertools
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from .catalog import ComponentOption
from .models import ComponentType, ConfigurationRequest, PerformanceEstimate, Purpose


# Фиксируем случайность, чтобы обучение и демонстрация давали стабильный результат.
DEFAULT_RANDOM_STATE = 42
MIN_TRAINING_SAMPLES = 30
TRAIN_TEST_SPLIT_RATIO = 0.2
METRIC_ROUND_DIGITS = 4

# Параметры градиентного бустинга.
# Модель специально небольшая: задача табличная, поэтому тяжелая нейросеть здесь не нужна.
GRADIENT_BOOSTING_ESTIMATORS = 120
GRADIENT_BOOSTING_LEARNING_RATE = 0.05
GRADIENT_BOOSTING_MAX_DEPTH = 3

# Настройки синтетической обучающей выборки.
# Модель обучается не на истории покупок, а на сгенерированных запросах и экспертной оценке сборок.
DEFAULT_MAX_CANDIDATES = 700
TRAINING_CANDIDATES_PER_REQUEST = 30
TRAINING_MIN_BUDGET = 30000
TRAINING_DYNAMIC_BUDGET_HEADROOM = 5000
TRAINING_STATIC_BUDGETS = (60000, 120000, 200000)
CONFIGURATOR_MAX_BUDGET = 600000
TRAINING_RESOLUTIONS = ("1080p", "1440p")
TRAINING_WIFI_OPTIONS = (False,)

# Инженерные допущения для проверки блока питания и дорогих игровых сборок.
PLATFORM_POWER_RESERVE_WATTS = 150
PSU_HEADROOM_FULL_SCORE_WATTS = 350
HIGH_END_GAMING_BUDGET = 200000

# Границы нормализации признаков.
# Они приводят рубли, ватты, объем RAM/VRAM и оценки компонентов к сопоставимым числам.
MAX_COMPONENT_SCORE = 10
MAX_CPU_TDP = 300
MAX_GPU_TDP = 500
MAX_PSU_WATTS = 1200
MAX_RAM_GB = 256
MAX_VRAM_GB = 64
VALUE_PRICE_SCALE_RUB = 10000
MIN_VALUE_PRICE_DENOMINATOR = 0.5

# Границы экспертного скоринга.
# Именно эту экспертную оценку потом учится приближать GradientBoostingRegressor.
TARGET_BUDGET_USAGE_RATIO = 0.9
MIN_PRICE_RATIO_FOR_VALUE_SCORE = 0.35
MAX_RAW_VALUE_SCORE = 1.25
SCORE_MIN = 0.0
SCORE_MAX = 1.0

# В пул кандидатов попадают и выгодные по цене детали, и производительные детали.
# Так поиск не застревает только на самых дешевых или только на самых дорогих товарах.
CANDIDATE_VALUE_POOL_LIMITS = {
    ComponentType.CPU: 8,
    ComponentType.GPU: 10,
    ComponentType.STORAGE: 5,
    ComponentType.CASE: 5,
}
CANDIDATE_PERFORMANCE_POOL_LIMITS = {
    ComponentType.CPU: 5,
    ComponentType.GPU: 6,
    ComponentType.STORAGE: 3,
    ComponentType.CASE: 3,
}
MOTHERBOARD_TOP_LIMIT = 6
RAM_TOP_LIMIT = 5
PSU_TOP_LIMIT = 4

# Веса экспертной оценки для обычных запросов.
# Здесь важны не только производительность, но и попадание в бюджет, баланс и выгодность.
EXPERT_LABEL_WEIGHTS_DEFAULT = {
    "performance": 0.32,
    "value": 0.22,
    "budget_fit": 0.13,
    "balance": 0.12,
    "psu_headroom": 0.08,
    "capacity": 0.08,
    "resolution": 0.05,
    "wifi": 0.02,
}

# Веса экспертной оценки для дорогих игровых/4K-сборок.
# В таких сборках производительность важнее экономии на каждом рубле.
EXPERT_LABEL_WEIGHTS_HIGH_END_GAMING = {
    "performance": 0.42,
    "value": 0.12,
    "budget_fit": 0.16,
    "balance": 0.12,
    "psu_headroom": 0.08,
    "capacity": 0.05,
    "resolution": 0.04,
    "wifi": 0.01,
}

# Пороги баланса CPU/GPU.
# Они защищают от неадекватных пар вроде слабого процессора с флагманской видеокартой.
FLAGSHIP_GPU_SCORE = 9.5
HIGH_GPU_SCORE = 8.8
GAMING_FLAGSHIP_MIN_CPU_SCORE = 8.6
GAMING_HIGH_GPU_MIN_CPU_SCORE = 7.5
GENERAL_FLAGSHIP_MIN_CPU_SCORE = 8.2
FLAGSHIP_MIN_RAM_GB = 32
HIGH_GPU_MIN_RAM_GB = 16
MAX_GAMING_GPU_CPU_SCORE_GAP = 2.2
MAX_GENERAL_GPU_CPU_SCORE_GAP = 2.6
BALANCE_GAP_FULL_PENALTY = 3.5
FLAGSHIP_RAM_PENALTY = 0.35
HIGH_GPU_RAM_PENALTY = 0.25

# Важность компонентов зависит от назначения ПК.
# Для игр важнее GPU, для работы CPU/RAM, для учебы - недорогой сбалансированный набор.
PERFORMANCE_WEIGHTS_BY_PURPOSE = {
    Purpose.GAMING: {
        ComponentType.CPU: 0.22,
        ComponentType.GPU: 0.50,
        ComponentType.RAM: 0.12,
        ComponentType.STORAGE: 0.08,
        ComponentType.MOTHERBOARD: 0.04,
        ComponentType.PSU: 0.02,
        ComponentType.CASE: 0.02,
    },
    Purpose.WORK: {
        ComponentType.CPU: 0.36,
        ComponentType.GPU: 0.24,
        ComponentType.RAM: 0.18,
        ComponentType.STORAGE: 0.12,
        ComponentType.MOTHERBOARD: 0.04,
        ComponentType.PSU: 0.03,
        ComponentType.CASE: 0.03,
    },
    Purpose.STUDY: {
        ComponentType.CPU: 0.30,
        ComponentType.GPU: 0.20,
        ComponentType.RAM: 0.20,
        ComponentType.STORAGE: 0.16,
        ComponentType.MOTHERBOARD: 0.05,
        ComponentType.PSU: 0.04,
        ComponentType.CASE: 0.05,
    },
    Purpose.GENERAL: {
        ComponentType.CPU: 0.30,
        ComponentType.GPU: 0.24,
        ComponentType.RAM: 0.18,
        ComponentType.STORAGE: 0.14,
        ComponentType.MOTHERBOARD: 0.05,
        ComponentType.PSU: 0.04,
        ComponentType.CASE: 0.05,
    },
}

# Минимальный ожидаемый уровень видеокарты для каждого разрешения.
RESOLUTION_SCORE_THRESHOLDS = {
    "1080p": 6.5,
    "1440p": 8.0,
    "4k": 9.2,
}

# Категориальные значения кодируются числами, потому что sklearn работает с числовыми признаками.
PURPOSE_CODES = {
    Purpose.GAMING: 0.0,
    Purpose.WORK: 0.33,
    Purpose.STUDY: 0.66,
    Purpose.GENERAL: 1.0,
}
RESOLUTION_CODES = {
    "1080p": 0.0,
    "1440p": 0.5,
    "4k": 1.0,
}
PERFORMANCE_CODES = {
    PerformanceEstimate.ENTRY: 0.33,
    PerformanceEstimate.MID: 0.66,
    PerformanceEstimate.HIGH: 1.0,
}

# Алиасы сокетов нужны, потому что в каталоге один и тот же сокет может называться по-разному.
SOCKET_ALIASES = {
    "AM4": {"AM4"},
    "AM5": {"AM5"},
    "LGA1700": {"LGA1700", "SOCKET V"},
    "SOCKET V": {"LGA1700", "SOCKET V"},
}

# Эвристика для определения VRAM, если в названии/notes не получилось явно найти объем в GB.
# Это используется только для признаков модели, а не для проверки совместимости.
VRAM_CAPACITY_HEURISTICS = {
    "RTX 4090": 24,
    "RTX 4080": 16,
    "RTX 4070": 12,
    "RTX 4060": 8,
    "RTX 3050": 8,
    "GTX 1650": 4,
    "GT 1030": 2,
    "RX 7900": 20,
    "RX 7800": 16,
    "RX 7700": 12,
    "RX 7600": 8,
    "RX 6400": 4,
    "ARC A770": 16,
    "ARC A750": 8,
}
CATALOG_HASH_LENGTH = 12


@dataclass(frozen=True)
class ModelMetrics:
    algorithm: str
    train_samples: int
    test_samples: int
    r2: float
    mae: float
    catalog_hash: str


class MLConfigurationRanker:

    def __init__(self, random_state: int = DEFAULT_RANDOM_STATE):
        self._random_state = random_state
        self._model: GradientBoostingRegressor | None = None
        self._metrics: ModelMetrics | None = None
        self._catalog_hash: str | None = None

    @property
    def metrics(self) -> ModelMetrics | None:
        return self._metrics

    def save_artifact(self, path: str | Path) -> None:
        if self._model is None or self._metrics is None:
            raise RuntimeError("ML model is not trained yet")
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self._model,
                "metrics": asdict(self._metrics),
                "catalog_hash": self._catalog_hash,
            },
            target,
        )

    def ensure_trained(self, catalog: dict[ComponentType, list[ComponentOption]]) -> None:
        # Модель переобучается только тогда, когда изменился каталог.
        # Это важно: новые товары или цены должны влиять на ранжирование сборок.
        catalog_hash = self._hash_catalog(catalog)
        if self._model is not None and self._catalog_hash == catalog_hash:
            return

        features, targets = self._build_training_dataset(catalog)
        if len(features) < MIN_TRAINING_SAMPLES:
            # Если в каталоге слишком мало комбинаций, ML-модель обучать бессмысленно.
            # В этом случае используется та же экспертная функция, но без Gradient Boosting.
            self._model = None
            self._metrics = ModelMetrics(
                algorithm="expert-fallback",
                train_samples=len(features),
                test_samples=0,
                r2=0.0,
                mae=0.0,
                catalog_hash=catalog_hash,
            )
            self._catalog_hash = catalog_hash
            return

        x_train, x_test, y_train, y_test = train_test_split(
            features,
            targets,
            test_size=TRAIN_TEST_SPLIT_RATIO,
            random_state=self._random_state,
        )
        # GradientBoostingRegressor учится предсказывать экспертную оценку конфигурации.
        # То есть модель не "знает" совместимость сама, а учится ранжировать уже допустимые сборки.
        model = GradientBoostingRegressor(
            random_state=self._random_state,
            n_estimators=GRADIENT_BOOSTING_ESTIMATORS,
            learning_rate=GRADIENT_BOOSTING_LEARNING_RATE,
            max_depth=GRADIENT_BOOSTING_MAX_DEPTH,
        )
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)

        self._model = model
        self._catalog_hash = catalog_hash
        self._metrics = ModelMetrics(
            algorithm="GradientBoostingRegressor",
            train_samples=len(x_train),
            test_samples=len(x_test),
            r2=round(float(r2_score(y_test, predictions)), METRIC_ROUND_DIGITS),
            mae=round(float(mean_absolute_error(y_test, predictions)), METRIC_ROUND_DIGITS),
            catalog_hash=catalog_hash,
        )

    def select_best(
        self,
        request: ConfigurationRequest,
        catalog: dict[ComponentType, list[ComponentOption]],
        fallback: dict[ComponentType, ComponentOption],
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> tuple[dict[ComponentType, ComponentOption], float]:
        self.ensure_trained(catalog)
        candidates = self._generate_candidates(request, catalog, max_candidates=max_candidates)
        if not candidates:
            # Fallback приходит из основного конфигуратора. Он уже прошел базовые правила совместимости.
            return fallback, self.score(request, fallback)

        candidates.append(fallback)
        scored = [(candidate, self.score(request, candidate)) for candidate in candidates]
        return max(scored, key=lambda item: item[1])

    def score(self, request: ConfigurationRequest, selected: dict[ComponentType, ComponentOption]) -> float:
        features = self._features(request, selected)
        if self._model is None:
            # Если ML не обучен, используем экспертную формулу напрямую.
            prediction = self._expert_label(request, selected)
        else:
            prediction = float(self._model.predict([features])[0])
        return round(max(SCORE_MIN, min(SCORE_MAX, prediction)), METRIC_ROUND_DIGITS)

    def _build_training_dataset(
        self,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> tuple[list[list[float]], list[float]]:
        rng = random.Random(self._random_state)
        requests = self._training_requests(catalog)
        features: list[list[float]] = []
        targets: list[float] = []

        for request in requests:
            # Для каждого искусственного запроса генерируем совместимые варианты сборок.
            # Целевой ответ для обучения - не пользовательская оценка, а экспертный скоринг.
            candidates = self._generate_candidates(
                request,
                catalog,
                max_candidates=TRAINING_CANDIDATES_PER_REQUEST,
                rng=rng,
            )
            for candidate in candidates:
                features.append(self._features(request, candidate))
                targets.append(self._expert_label(request, candidate))

        return features, targets

    def _training_requests(self, catalog: dict[ComponentType, list[ComponentOption]]) -> list[ConfigurationRequest]:
        cheapest_total = self._rough_minimum_total(catalog)
        budgets = sorted(
            {
                # Динамический бюджет нужен, чтобы обучающая выборка не была ниже реальной минимальной сборки.
                max(TRAINING_MIN_BUDGET, cheapest_total + TRAINING_DYNAMIC_BUDGET_HEADROOM),
                *TRAINING_STATIC_BUDGETS,
            }
        )

        requests: list[ConfigurationRequest] = []
        for purpose, budget, resolution, needs_wifi in itertools.product(
            Purpose,
            budgets,
            TRAINING_RESOLUTIONS,
            TRAINING_WIFI_OPTIONS,
        ):
            if budget < TRAINING_MIN_BUDGET or budget > CONFIGURATOR_MAX_BUDGET:
                continue
            requests.append(
                ConfigurationRequest(
                    budget=budget,
                    purpose=purpose,
                    target_resolution=resolution,
                    needs_wifi=needs_wifi,
                )
            )
        return requests

    def _generate_candidates(
        self,
        request: ConfigurationRequest,
        catalog: dict[ComponentType, list[ComponentOption]],
        max_candidates: int,
        rng: random.Random | None = None,
    ) -> list[dict[ComponentType, ComponentOption]]:
        # Сначала сужаем каталог до разумного пула кандидатов.
        # Полный перебор всех товаров быстро разрастается комбинаторно.
        cpus = self._candidate_pool(
            catalog[ComponentType.CPU],
            request.purpose,
            value_limit=CANDIDATE_VALUE_POOL_LIMITS[ComponentType.CPU],
            performance_limit=CANDIDATE_PERFORMANCE_POOL_LIMITS[ComponentType.CPU],
        )
        gpus = self._candidate_pool(
            catalog[ComponentType.GPU],
            request.purpose,
            value_limit=CANDIDATE_VALUE_POOL_LIMITS[ComponentType.GPU],
            performance_limit=CANDIDATE_PERFORMANCE_POOL_LIMITS[ComponentType.GPU],
        )
        # Если пользователь указал предпочтительный бренд, ML-ранжирование должно сравнивать сначала такие варианты.
        # Если подходящих товаров этого бренда нет, оставляем общий пул, чтобы система все равно могла подобрать сборку.
        cpus = self._apply_brand_preference(cpus, request.cpu_brand_preference)
        gpus = self._apply_brand_preference(gpus, request.gpu_brand_preference)
        storages = self._candidate_pool(
            catalog[ComponentType.STORAGE],
            request.purpose,
            value_limit=CANDIDATE_VALUE_POOL_LIMITS[ComponentType.STORAGE],
            performance_limit=CANDIDATE_PERFORMANCE_POOL_LIMITS[ComponentType.STORAGE],
        )
        cases = self._candidate_pool(
            catalog[ComponentType.CASE],
            request.purpose,
            value_limit=CANDIDATE_VALUE_POOL_LIMITS[ComponentType.CASE],
            performance_limit=CANDIDATE_PERFORMANCE_POOL_LIMITS[ComponentType.CASE],
        )
        candidates: list[dict[ComponentType, ComponentOption]] = []

        for cpu in cpus:
            # Материнская плата фильтруется по сокету CPU и требованию Wi-Fi.
            motherboards = [
                board
                for board in catalog[ComponentType.MOTHERBOARD]
                if self._socket_compatible(cpu, board) and (not request.needs_wifi or board.supports_wifi)
            ]
            for motherboard in self._top_options(motherboards, request.purpose, limit=MOTHERBOARD_TOP_LIMIT):
                # RAM должна соответствовать типу памяти материнской платы: DDR4 к DDR4, DDR5 к DDR5.
                rams = [ram for ram in catalog[ComponentType.RAM] if ram.ram_type == motherboard.ram_type]
                for ram in self._top_options(rams, request.purpose, limit=RAM_TOP_LIMIT):
                    for gpu in gpus:
                        # К TDP CPU и GPU добавляется запас на остальные компоненты и безопасную работу.
                        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + PLATFORM_POWER_RESERVE_WATTS
                        psus = [psu for psu in catalog[ComponentType.PSU] if psu.psu_watts >= required_watts]
                        for psu in self._top_options(psus, request.purpose, limit=PSU_TOP_LIMIT):
                            for storage in storages:
                                for case in cases:
                                    candidate = {
                                        ComponentType.CPU: cpu,
                                        ComponentType.GPU: gpu,
                                        ComponentType.MOTHERBOARD: motherboard,
                                        ComponentType.RAM: ram,
                                        ComponentType.STORAGE: storage,
                                        ComponentType.PSU: psu,
                                        ComponentType.CASE: case,
                                    }
                                    if (
                                        sum(option.price for option in candidate.values()) <= request.budget
                                        and self._is_balanced_candidate(request, candidate)
                                    ):
                                        # В ML попадают только сборки, которые помещаются в бюджет и не имеют явного перекоса.
                                        candidates.append(candidate)
                                        # Ранняя остановка нужна только при обучении, где важна скорость генерации выборки.
                                        # Для реального подбора ниже сортируем кандидатов и выбираем лучшие варианты.
                                        if rng is not None and len(candidates) >= max_candidates:
                                            return candidates

        if rng is None:
            candidates = self._prefer_resolution_ready_candidates(request, candidates)

        if rng is not None and len(candidates) > max_candidates:
            # При обучении используем случайную выборку, чтобы модель видела разные допустимые варианты.
            candidates = rng.sample(candidates, max_candidates)
        elif len(candidates) > max_candidates:
            # При реальном подборе оставляем лучшие по экспертной оценке варианты.
            candidates = sorted(candidates, key=lambda candidate: self._expert_label(request, candidate), reverse=True)
        return candidates[:max_candidates]

    def _prefer_resolution_ready_candidates(
        self,
        request: ConfigurationRequest,
        candidates: list[dict[ComponentType, ComponentOption]],
    ) -> list[dict[ComponentType, ComponentOption]]:
        # Для игрового 1440p/4K слабая видеокарта формально может быть совместимой,
        # но рекомендация будет выглядеть странно. Если в бюджете есть варианты с GPU,
        # подходящей под целевое разрешение, ранжируем именно их.
        if request.purpose != Purpose.GAMING or request.target_resolution == "1080p":
            return candidates

        threshold = RESOLUTION_SCORE_THRESHOLDS[request.target_resolution]
        ready = [
            candidate
            for candidate in candidates
            if candidate[ComponentType.GPU].score_for(request.purpose) >= threshold
        ]
        return ready or candidates

    def _features(self, request: ConfigurationRequest, selected: dict[ComponentType, ComponentOption]) -> list[float]:
        # Признаки - это числовое описание запроса и выбранной сборки.
        # Именно этот список подается в sklearn-модель.
        total_price = sum(option.price for option in selected.values())
        cpu = selected[ComponentType.CPU]
        gpu = selected[ComponentType.GPU]
        motherboard = selected[ComponentType.MOTHERBOARD]
        ram = selected[ComponentType.RAM]
        storage = selected[ComponentType.STORAGE]
        psu = selected[ComponentType.PSU]
        case = selected[ComponentType.CASE]
        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + PLATFORM_POWER_RESERVE_WATTS
        scores = [selected[component_type].score_for(request.purpose) for component_type in ComponentType]
        balance_score = self._balance_score(request, selected)

        return [
            # Бюджет и цена.
            request.budget / CONFIGURATOR_MAX_BUDGET,
            total_price / max(request.budget, 1),
            total_price / CONFIGURATOR_MAX_BUDGET,
            # Пользовательские требования.
            self._purpose_code(request.purpose),
            self._resolution_code(request.target_resolution),
            1.0 if request.needs_wifi else 0.0,
            self._performance_code(request.minimum_performance),
            request.min_ram_gb / MAX_RAM_GB,
            request.min_vram_gb / MAX_VRAM_GB,
            # Оценки отдельных компонентов под назначение пользователя.
            cpu.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            gpu.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            motherboard.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            ram.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            storage.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            psu.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            case.score_for(request.purpose) / MAX_COMPONENT_SCORE,
            sum(scores) / (MAX_COMPONENT_SCORE * len(scores)),
            # Электропотребление, запас блока питания и объемы памяти.
            cpu.cpu_tdp / MAX_CPU_TDP,
            gpu.gpu_tdp / MAX_GPU_TDP,
            psu.psu_watts / MAX_PSU_WATTS,
            max(0, psu.psu_watts - required_watts) / MAX_PSU_WATTS,
            self._ram_capacity_gb(ram) / MAX_RAM_GB,
            self._vram_capacity_gb(gpu) / MAX_VRAM_GB,
            # Дополнительные признаки удобства и баланса.
            1.0 if motherboard.supports_wifi else 0.0,
            balance_score,
        ]

    def _expert_label(self, request: ConfigurationRequest, selected: dict[ComponentType, ComponentOption]) -> float:
        # Экспертная оценка - это "учитель" для ML-модели.
        # Она объединяет производительность, цену, попадание в бюджет, баланс и требования пользователя.
        total_price = sum(option.price for option in selected.values())
        price_ratio = total_price / max(request.budget, 1)
        performance = self._weighted_performance(request.purpose, selected) / MAX_COMPONENT_SCORE

        # Сборка не обязана тратить весь бюджет, но слишком дешевая или слишком дорогая сборка получает штраф.
        budget_fit = max(SCORE_MIN, SCORE_MAX - abs(TARGET_BUDGET_USAGE_RATIO - price_ratio))

        # Value score показывает, сколько производительности пользователь получает за потраченные деньги.
        value_score = performance / max(price_ratio, MIN_PRICE_RATIO_FOR_VALUE_SCORE)
        value_score = min(value_score, MAX_RAW_VALUE_SCORE) / MAX_RAW_VALUE_SCORE

        cpu = selected[ComponentType.CPU]
        gpu = selected[ComponentType.GPU]
        psu = selected[ComponentType.PSU]

        # Запас блока питания считается отдельно: мощность должна покрывать CPU, GPU и системный резерв.
        headroom = min(
            max(psu.psu_watts - cpu.cpu_tdp - gpu.gpu_tdp - PLATFORM_POWER_RESERVE_WATTS, 0)
            / PSU_HEADROOM_FULL_SCORE_WATTS,
            SCORE_MAX,
        )
        wifi_score = SCORE_MAX if not request.needs_wifi or selected[ComponentType.MOTHERBOARD].supports_wifi else SCORE_MIN
        capacity_score = self._capacity_score(request, selected)
        resolution_score = self._resolution_score(request, selected)
        balance_score = self._balance_score(request, selected)

        if request.purpose == Purpose.GAMING and (
            request.target_resolution == "4k" or request.budget >= HIGH_END_GAMING_BUDGET
        ):
            # Для дорогих игровых сборок больше весит чистая производительность.
            weights = EXPERT_LABEL_WEIGHTS_HIGH_END_GAMING
        else:
            # Для обычных сборок важнее баланс цены, качества и соответствия требованиям.
            weights = EXPERT_LABEL_WEIGHTS_DEFAULT

        weighted_score = (
            weights["performance"] * performance
            + weights["value"] * value_score
            + weights["budget_fit"] * budget_fit
            + weights["balance"] * balance_score
            + weights["psu_headroom"] * headroom
            + weights["capacity"] * capacity_score
            + weights["resolution"] * resolution_score
            + weights["wifi"] * wifi_score
        )

        return max(SCORE_MIN, min(SCORE_MAX, weighted_score))

    def _is_balanced_candidate(
        self,
        request: ConfigurationRequest,
        selected: dict[ComponentType, ComponentOption],
    ) -> bool:
        # Жесткий фильтр баланса. Он не дает ML-модели рассматривать явно странные варианты.
        cpu = selected[ComponentType.CPU]
        gpu = selected[ComponentType.GPU]
        ram = selected[ComponentType.RAM]
        cpu_score = cpu.score_for(request.purpose)
        gpu_score = gpu.score_for(request.purpose)
        ram_gb = self._ram_capacity_gb(ram)

        if request.purpose == Purpose.GAMING:
            # В играх слабый процессор сильнее мешает мощной видеокарте, поэтому пороги строже.
            if gpu_score >= FLAGSHIP_GPU_SCORE:
                return cpu_score >= GAMING_FLAGSHIP_MIN_CPU_SCORE and ram_gb >= FLAGSHIP_MIN_RAM_GB
            if gpu_score >= HIGH_GPU_SCORE:
                return cpu_score >= GAMING_HIGH_GPU_MIN_CPU_SCORE and ram_gb >= HIGH_GPU_MIN_RAM_GB
            return gpu_score - cpu_score <= MAX_GAMING_GPU_CPU_SCORE_GAP

        if gpu_score >= FLAGSHIP_GPU_SCORE:
            return cpu_score >= GENERAL_FLAGSHIP_MIN_CPU_SCORE and ram_gb >= FLAGSHIP_MIN_RAM_GB
        return gpu_score - cpu_score <= MAX_GENERAL_GPU_CPU_SCORE_GAP

    def _balance_score(
        self,
        request: ConfigurationRequest,
        selected: dict[ComponentType, ComponentOption],
    ) -> float:
        # Мягкая оценка баланса от 0 до 1. В отличие от _is_balanced_candidate,
        # она не отбрасывает сборку, а снижает ее итоговый ML-score.
        cpu_score = selected[ComponentType.CPU].score_for(request.purpose)
        gpu_score = selected[ComponentType.GPU].score_for(request.purpose)
        ram_gb = self._ram_capacity_gb(selected[ComponentType.RAM])

        score_gap = max(gpu_score - cpu_score, 0.0)
        gap_penalty = min(score_gap / BALANCE_GAP_FULL_PENALTY, SCORE_MAX)
        ram_penalty = SCORE_MIN
        if gpu_score >= FLAGSHIP_GPU_SCORE and ram_gb < FLAGSHIP_MIN_RAM_GB:
            ram_penalty = FLAGSHIP_RAM_PENALTY
        elif gpu_score >= HIGH_GPU_SCORE and ram_gb < HIGH_GPU_MIN_RAM_GB:
            ram_penalty = HIGH_GPU_RAM_PENALTY

        return max(SCORE_MIN, SCORE_MAX - gap_penalty - ram_penalty)

    def _weighted_performance(
        self,
        purpose: Purpose,
        selected: dict[ComponentType, ComponentOption],
    ) -> float:
        # Сводим оценки отдельных компонентов в одну производительность.
        # Веса зависят от назначения: игровой ПК сильнее зависит от GPU, рабочий - от CPU/RAM.
        weights = PERFORMANCE_WEIGHTS_BY_PURPOSE[purpose]
        return sum(selected[component].score_for(purpose) * weight for component, weight in weights.items())

    def _capacity_score(
        self,
        request: ConfigurationRequest,
        selected: dict[ComponentType, ComponentOption],
    ) -> float:
        # Проверяем, выполняются ли требования пользователя по RAM и VRAM.
        # Если пользователь не задавал минимум, считаем требование выполненным.
        ram_capacity = self._ram_capacity_gb(selected[ComponentType.RAM])
        vram_capacity = self._vram_capacity_gb(selected[ComponentType.GPU])
        ram_score = SCORE_MAX if request.min_ram_gb == 0 else min(ram_capacity / request.min_ram_gb, SCORE_MAX)
        vram_score = SCORE_MAX if request.min_vram_gb == 0 else min(vram_capacity / request.min_vram_gb, SCORE_MAX)
        return (ram_score + vram_score) / 2

    def _resolution_score(
        self,
        request: ConfigurationRequest,
        selected: dict[ComponentType, ComponentOption],
    ) -> float:
        # Чем выше целевое разрешение, тем более сильная видеокарта нужна для хорошей оценки.
        gpu_score = selected[ComponentType.GPU].score_for(request.purpose)
        return min(gpu_score / RESOLUTION_SCORE_THRESHOLDS[request.target_resolution], SCORE_MAX)

    def _top_options(
        self,
        options: Iterable[ComponentOption],
        purpose: Purpose,
        limit: int,
    ) -> list[ComponentOption]:
        # Берем лучшие варианты по соотношению "оценка / цена" и дополнительно учитываем чистую оценку.
        return sorted(
            options,
            key=lambda option: (
                option.score_for(purpose) / max(option.price / VALUE_PRICE_SCALE_RUB, MIN_VALUE_PRICE_DENOMINATOR),
                option.score_for(purpose),
            ),
            reverse=True,
        )[:limit]

    def _candidate_pool(
        self,
        options: Iterable[ComponentOption],
        purpose: Purpose,
        value_limit: int,
        performance_limit: int,
    ) -> list[ComponentOption]:
        # Объединяем два набора: выгодные по цене товары и самые производительные товары.
        # Ключ option_key нужен, чтобы один и тот же товар не попал в пул дважды.
        pool: dict[str, ComponentOption] = {}
        for option in self._top_options(options, purpose, limit=value_limit):
            pool[self._option_key(option)] = option
        for option in sorted(options, key=lambda option: (option.score_for(purpose), option.price), reverse=True)[
            :performance_limit
        ]:
            pool[self._option_key(option)] = option
        return list(pool.values())

    def _apply_brand_preference(self, options: list[ComponentOption], preferred_brand: str) -> list[ComponentOption]:
        if preferred_brand == "any":
            return options
        preferred = [option for option in options if option.brand == preferred_brand]
        return preferred or options

    def _option_key(self, option: ComponentOption) -> str:
        return f"{option.product_id}:{option.type.value}:{option.model}:{option.price}"

    def _rough_minimum_total(self, catalog: dict[ComponentType, list[ComponentOption]]) -> int:
        # Грубая нижняя оценка бюджета нужна только для генерации обучающих запросов.
        # Совместимость здесь не проверяется, поэтому это не финальная минимальная цена сборки.
        return sum(min(options, key=lambda item: item.price).price for options in catalog.values() if options)

    def _socket_compatible(self, cpu: ComponentOption, motherboard: ComponentOption) -> bool:
        # Сокет процессора должен совпадать с одним из сокетов, поддерживаемых материнской платой.
        if cpu.socket is None:
            return False
        cpu_family = self._socket_family(cpu.socket)
        return any(cpu_family & self._socket_family(socket) for socket in motherboard.socket_candidates())

    def _socket_family(self, socket_name: str) -> set[str]:
        normalized = socket_name.strip().upper()
        return SOCKET_ALIASES.get(normalized, {normalized})

    def _purpose_code(self, purpose: Purpose) -> float:
        return PURPOSE_CODES[purpose]

    def _resolution_code(self, resolution: str) -> float:
        return RESOLUTION_CODES[resolution]

    def _performance_code(self, tier: PerformanceEstimate | None) -> float:
        if tier is None:
            return 0.0
        return PERFORMANCE_CODES[tier]

    def _ram_capacity_gb(self, option: ComponentOption) -> int:
        # Объем RAM берем из названия или notes, например "DDR4 16GB Kit".
        return _extract_first_gb_value(" ".join([option.model, *option.notes]))

    def _vram_capacity_gb(self, option: ComponentOption) -> int:
        # Сначала пытаемся найти явное "8GB/16GB" в названии или notes.
        combined = " ".join([option.model, *option.notes]).upper()
        explicit = _extract_first_gb_value(combined)
        if explicit > 0:
            return explicit

        # Если явного объема нет, используем безопасную эвристику по названию видеокарты.
        for marker, value in VRAM_CAPACITY_HEURISTICS.items():
            if marker in combined:
                return value
        return 0

    def _hash_catalog(self, catalog: dict[ComponentType, list[ComponentOption]]) -> str:
        # Хэш каталога нужен, чтобы понять, надо ли переобучать модель после изменения товаров.
        payload = []
        for component_type in sorted(catalog, key=lambda item: item.value):
            for option in sorted(catalog[component_type], key=lambda item: (item.type.value, item.model, item.price)):
                payload.append(
                    "|".join(
                        [
                            option.type.value,
                            option.model,
                            option.brand,
                            str(option.price),
                            str(option.score_gaming),
                            str(option.score_work),
                            str(option.score_study),
                            str(option.score_general),
                            str(option.socket),
                            str(option.ram_type),
                            str(option.gpu_tdp),
                            str(option.cpu_tdp),
                            str(option.psu_watts),
                        ]
                    )
                )
        return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()[:CATALOG_HASH_LENGTH]


def _extract_first_gb_value(text: str) -> int:
    import re

    match = re.search(r"(\d{1,3})\s*GB", text, flags=re.IGNORECASE)
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0
