from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from .catalog import CatalogLoadError, ComponentOption, ProductCatalogProvider
from .models import (
    ComponentType,
    ConfigurationAlternatives,
    ConfigurationRequest,
    ConfigurationResponse,
    ConfigurationVariant,
    PerformanceEstimate,
    Purpose,
    SelectedComponent,
)


@dataclass(frozen=True)
class AllocationProfile:
    cpu: float
    gpu: float
    motherboard: float
    ram: float
    storage: float
    psu: float
    case: float


ALLOCATION_BY_PURPOSE: dict[Purpose, AllocationProfile] = {
    Purpose.GAMING: AllocationProfile(0.19, 0.38, 0.10, 0.10, 0.08, 0.08, 0.07),
    Purpose.WORK: AllocationProfile(0.26, 0.25, 0.12, 0.12, 0.11, 0.08, 0.06),
    Purpose.STUDY: AllocationProfile(0.22, 0.22, 0.12, 0.12, 0.12, 0.10, 0.10),
    Purpose.GENERAL: AllocationProfile(0.22, 0.24, 0.12, 0.12, 0.11, 0.10, 0.09),
}

SOCKET_ALIASES: dict[str, set[str]] = {
    "AM4": {"AM4"},
    "AM5": {"AM5"},
    "LGA1700": {"LGA1700", "SOCKET V"},
}


class CatalogProvider(Protocol):
    def load_catalog(self) -> dict[ComponentType, list[ComponentOption]]:
        ...


class ConfiguratorEngine:
    class BudgetConstraintError(ValueError):
        def __init__(self, budget: int, minimum_required_budget: int):
            super().__init__(
                f"Budget {budget} RUB is too low for a compatible build. "
                f"Minimum required budget is {minimum_required_budget} RUB."
            )
            self.budget = budget
            self.minimum_required_budget = minimum_required_budget

    class PreferenceConstraintError(ValueError):
        pass

    class PerformanceConstraintError(ValueError):
        def __init__(self, minimum_requested: PerformanceEstimate, actual: PerformanceEstimate):
            super().__init__(
                f"Unable to satisfy minimum performance tier '{minimum_requested.value}'. "
                f"Best achievable tier for current constraints is '{actual.value}'."
            )
            self.minimum_requested = minimum_requested
            self.actual = actual

    def __init__(self, catalog_provider: CatalogProvider | None = None):
        self._catalog_provider = catalog_provider or ProductCatalogProvider()

    def recommend(self, request: ConfigurationRequest) -> ConfigurationResponse:
        catalog = self._catalog_provider.load_catalog()
        catalog = self._apply_capacity_preferences(request, catalog)

        minimum_required_budget = self._minimum_required_budget(request.needs_wifi, catalog)
        if request.budget < minimum_required_budget:
            raise self.BudgetConstraintError(request.budget, minimum_required_budget)

        primary = self._recommend_single(request, catalog)
        alternatives = self._build_alternatives(request, primary, catalog, minimum_required_budget)
        if alternatives.cheaper is None and alternatives.pricier is None:
            alternatives = None

        return ConfigurationResponse(
            **primary.model_dump(),
            alternatives=alternatives,
        )

    def _recommend_single(
        self,
        request: ConfigurationRequest,
        catalog: dict[ComponentType, list[ComponentOption]],
        optimize_for_performance: bool = False,
    ) -> ConfigurationVariant:

        profile = ALLOCATION_BY_PURPOSE[request.purpose]
        allocations = self._build_allocations(request.budget, profile)

        cpu_brand_preference = self._resolve_cpu_brand_preference(request)
        gpu_brand_preference = self._resolve_gpu_brand_preference(request)

        cpu = self._pick_best(
            ComponentType.CPU,
            budget_limit=allocations[ComponentType.CPU],
            purpose=request.purpose,
            preferred_brand=cpu_brand_preference,
            catalog=catalog,
            optimize_for_performance=optimize_for_performance,
        )
        gpu = self._pick_best(
            ComponentType.GPU,
            budget_limit=allocations[ComponentType.GPU],
            purpose=request.purpose,
            preferred_brand=gpu_brand_preference,
            catalog=catalog,
            optimize_for_performance=optimize_for_performance,
        )
        motherboard = self._pick_motherboard(
            cpu,
            request.needs_wifi,
            allocations[ComponentType.MOTHERBOARD],
            request.purpose,
            catalog,
        )
        ram = self._pick_ram(
            motherboard,
            allocations[ComponentType.RAM],
            request.purpose,
            catalog,
        )
        storage = self._pick_best(
            ComponentType.STORAGE,
            allocations[ComponentType.STORAGE],
            request.purpose,
            "any",
            catalog,
            optimize_for_performance=optimize_for_performance,
        )
        psu = self._pick_psu(
            cpu,
            gpu,
            allocations[ComponentType.PSU],
            request.purpose,
            catalog,
        )
        case = self._pick_best(
            ComponentType.CASE,
            allocations[ComponentType.CASE],
            request.purpose,
            "any",
            catalog,
            optimize_for_performance=optimize_for_performance,
        )

        selected = {
            ComponentType.CPU: cpu,
            ComponentType.GPU: gpu,
            ComponentType.MOTHERBOARD: motherboard,
            ComponentType.RAM: ram,
            ComponentType.STORAGE: storage,
            ComponentType.PSU: psu,
            ComponentType.CASE: case,
        }

        self._validate_selected_configuration(selected, request.needs_wifi)
        self._fit_into_budget(
            selected,
            request.budget,
            request.purpose,
            request.needs_wifi,
            catalog,
        )
        if sum(component.price for component in selected.values()) > request.budget:
            selected = self._build_minimum_configuration(request.needs_wifi, request.purpose, catalog)

        components = [
            self._to_selected(ComponentType.CPU, selected[ComponentType.CPU], request.purpose),
            self._to_selected(ComponentType.GPU, selected[ComponentType.GPU], request.purpose),
            self._to_selected(ComponentType.MOTHERBOARD, selected[ComponentType.MOTHERBOARD], request.purpose),
            self._to_selected(ComponentType.RAM, selected[ComponentType.RAM], request.purpose),
            self._to_selected(ComponentType.STORAGE, selected[ComponentType.STORAGE], request.purpose),
            self._to_selected(ComponentType.PSU, selected[ComponentType.PSU], request.purpose),
            self._to_selected(ComponentType.CASE, selected[ComponentType.CASE], request.purpose),
        ]

        total_price = sum(component.price for component in components)
        compatibility = self._compatibility_checks(selected, request.needs_wifi)
        performance = self._estimate_performance(selected, request.purpose, request.target_resolution)
        if request.minimum_performance is not None and self._performance_rank(performance) < self._performance_rank(
            request.minimum_performance
        ):
            raise self.PerformanceConstraintError(request.minimum_performance, performance)
        explanation = self._build_explanation(request, selected, total_price, performance)

        return ConfigurationVariant(
            purpose=request.purpose,
            budget=request.budget,
            total_price=total_price,
            components=components,
            performance_estimate=performance,
            compatibility_checks=compatibility,
            explanation=explanation,
        )

    def _build_alternatives(
        self,
        request: ConfigurationRequest,
        primary: ConfigurationVariant,
        catalog: dict[ComponentType, list[ComponentOption]],
        minimum_required_budget: int,
    ) -> ConfigurationAlternatives:
        cheaper = self._try_build_alternative(
            request=request,
            primary=primary,
            catalog=catalog,
            target_budget=self._cheaper_budget_target(request, primary, minimum_required_budget),
            mode="cheaper",
        )
        pricier = self._try_build_alternative(
            request=request,
            primary=primary,
            catalog=catalog,
            target_budget=self._pricier_budget_target(request, primary),
            mode="pricier",
        )
        return ConfigurationAlternatives(cheaper=cheaper, pricier=pricier)

    def _try_build_alternative(
        self,
        request: ConfigurationRequest,
        primary: ConfigurationVariant,
        catalog: dict[ComponentType, list[ComponentOption]],
        target_budget: int | None,
        mode: str,
    ) -> ConfigurationVariant | None:
        if target_budget is None:
            return None
        if mode == "cheaper" and target_budget >= primary.total_price:
            return None
        if mode == "pricier" and target_budget <= primary.total_price:
            return None

        try:
            alternative_request = request.model_copy(update={"budget": target_budget})
            alternative = self._recommend_single(
                alternative_request,
                catalog,
                optimize_for_performance=(mode == "pricier"),
            )
        except (self.BudgetConstraintError, self.PreferenceConstraintError, self.PerformanceConstraintError):
            return None

        if mode == "cheaper" and alternative.total_price >= primary.total_price:
            return None
        if mode == "pricier" and alternative.total_price <= primary.total_price:
            return None
        return alternative

    def _cheaper_budget_target(
        self,
        request: ConfigurationRequest,
        primary: ConfigurationVariant,
        minimum_required_budget: int,
    ) -> int | None:
        if primary.total_price <= minimum_required_budget:
            return None
        reduced_by_percent = int(primary.total_price * 0.85)
        reduced_by_step = primary.total_price - 10000
        target = max(minimum_required_budget, min(reduced_by_percent, reduced_by_step))
        if target >= primary.total_price:
            return None
        return target

    def _pricier_budget_target(self, request: ConfigurationRequest, primary: ConfigurationVariant) -> int | None:
        upper_bound = 600000
        if request.budget >= upper_bound and primary.total_price >= upper_bound:
            return None
        increased_by_percent = int(primary.total_price * 1.15)
        increased_by_step = primary.total_price + 10000
        target = min(upper_bound, max(increased_by_percent, increased_by_step, request.budget + 1))
        if target <= primary.total_price:
            return None
        return target

    def _build_allocations(self, budget: int, profile: AllocationProfile) -> dict[ComponentType, int]:
        return {
            ComponentType.CPU: int(budget * profile.cpu),
            ComponentType.GPU: int(budget * profile.gpu),
            ComponentType.MOTHERBOARD: int(budget * profile.motherboard),
            ComponentType.RAM: int(budget * profile.ram),
            ComponentType.STORAGE: int(budget * profile.storage),
            ComponentType.PSU: int(budget * profile.psu),
            ComponentType.CASE: int(budget * profile.case),
        }

    def _pick_best(
        self,
        component_type: ComponentType,
        budget_limit: int,
        purpose: Purpose,
        preferred_brand: str,
        catalog: dict[ComponentType, list[ComponentOption]],
        optimize_for_performance: bool = False,
    ) -> ComponentOption:
        options = catalog[component_type]
        affordable = [option for option in options if option.price <= budget_limit]
        if not affordable:
            affordable = options
        preferred_affordable = self._preferred_subset(affordable, preferred_brand)
        if preferred_affordable:
            affordable = preferred_affordable
        if optimize_for_performance:
            scored = sorted(
                affordable,
                key=lambda option: (option.score_for(purpose), option.price),
                reverse=True,
            )
        else:
            scored = sorted(
                affordable,
                key=lambda option: self._composite_score(option, purpose, preferred_brand),
                reverse=True,
            )
        return scored[0]

    def _pick_motherboard(
        self,
        cpu: ComponentOption,
        needs_wifi: bool,
        budget_limit: int,
        purpose: Purpose,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> ComponentOption:
        options = [
            option
            for option in catalog[ComponentType.MOTHERBOARD]
            if self._is_socket_compatible(cpu, option) and (not needs_wifi or option.supports_wifi)
        ]
        if not options:
            options = [
                option for option in catalog[ComponentType.MOTHERBOARD] if self._is_socket_compatible(cpu, option)
            ]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _pick_ram(
        self,
        motherboard: ComponentOption,
        budget_limit: int,
        purpose: Purpose,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> ComponentOption:
        options = [option for option in catalog[ComponentType.RAM] if option.ram_type == motherboard.ram_type]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _pick_psu(
        self,
        cpu: ComponentOption,
        gpu: ComponentOption,
        budget_limit: int,
        purpose: Purpose,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> ComponentOption:
        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
        options = [option for option in catalog[ComponentType.PSU] if option.psu_watts >= required_watts]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _fit_into_budget(
        self,
        selected: dict[ComponentType, ComponentOption],
        budget: int,
        purpose: Purpose,
        needs_wifi: bool,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> None:
        def total() -> int:
            return sum(component.price for component in selected.values())

        downgrade_order = [ComponentType.GPU, ComponentType.CPU, ComponentType.STORAGE, ComponentType.CASE]
        while total() > budget:
            changed = False
            for component_type in downgrade_order:
                current = selected[component_type]
                candidates = [
                    option
                    for option in catalog[component_type]
                    if option.price < current.price and self._is_compatible_swap(component_type, option, selected)
                ]
                if not candidates:
                    continue
                snapshot = dict(selected)
                replacement = sorted(candidates, key=lambda option: option.score_for(purpose), reverse=True)[0]
                selected[component_type] = replacement
                if component_type in (ComponentType.CPU, ComponentType.GPU):
                    selected[ComponentType.PSU] = self._pick_psu(
                        selected[ComponentType.CPU],
                        selected[ComponentType.GPU],
                        budget_limit=budget,
                        purpose=purpose,
                        catalog=catalog,
                    )
                    selected[ComponentType.MOTHERBOARD] = self._pick_motherboard(
                        selected[ComponentType.CPU],
                        needs_wifi=needs_wifi,
                        budget_limit=budget,
                        purpose=purpose,
                        catalog=catalog,
                    )
                    selected[ComponentType.RAM] = self._pick_ram(
                        selected[ComponentType.MOTHERBOARD],
                        budget,
                        purpose,
                        catalog,
                    )
                    if not self._is_selection_valid(selected, needs_wifi):
                        selected.clear()
                        selected.update(snapshot)
                        continue
                changed = True
                break
            if not changed:
                break

    def _is_compatible_swap(
        self,
        component_type: ComponentType,
        candidate: ComponentOption,
        selected: dict[ComponentType, ComponentOption],
    ) -> bool:
        if component_type == ComponentType.CPU:
            motherboard = selected[ComponentType.MOTHERBOARD]
            return self._is_socket_compatible(candidate, motherboard)
        if component_type == ComponentType.GPU:
            psu = selected[ComponentType.PSU]
            required = selected[ComponentType.CPU].cpu_tdp + candidate.gpu_tdp + 150
            return psu.psu_watts >= required
        return True

    def _composite_score(self, option: ComponentOption, purpose: Purpose, preferred_brand: str) -> float:
        score = option.score_for(purpose)
        if preferred_brand != "any" and option.brand == preferred_brand:
            score += 0.35
        return score / max(option.price / 10000, 0.5)

    def _estimate_performance(
        self,
        selected: dict[ComponentType, ComponentOption],
        purpose: Purpose,
        target_resolution: str,
    ) -> PerformanceEstimate:
        weights = {
            Purpose.GAMING: {
                ComponentType.CPU: 0.25,
                ComponentType.GPU: 0.55,
                ComponentType.RAM: 0.12,
                ComponentType.STORAGE: 0.08,
            },
            Purpose.WORK: {
                ComponentType.CPU: 0.38,
                ComponentType.GPU: 0.30,
                ComponentType.RAM: 0.20,
                ComponentType.STORAGE: 0.12,
            },
            Purpose.STUDY: {
                ComponentType.CPU: 0.35,
                ComponentType.GPU: 0.25,
                ComponentType.RAM: 0.22,
                ComponentType.STORAGE: 0.18,
            },
            Purpose.GENERAL: {
                ComponentType.CPU: 0.34,
                ComponentType.GPU: 0.30,
                ComponentType.RAM: 0.20,
                ComponentType.STORAGE: 0.16,
            },
        }[purpose]

        score = sum(selected[comp].score_for(purpose) * weight for comp, weight in weights.items())
        if purpose == Purpose.GAMING and target_resolution == "4k":
            score -= 0.4
        if purpose == Purpose.GAMING and target_resolution == "1440p":
            score -= 0.15

        if score >= 8.6:
            return PerformanceEstimate.HIGH
        if score >= 7.3:
            return PerformanceEstimate.MID
        return PerformanceEstimate.ENTRY

    def _compatibility_checks(
        self,
        selected: dict[ComponentType, ComponentOption],
        needs_wifi: bool,
    ) -> list[str]:
        checks = []
        cpu = selected[ComponentType.CPU]
        motherboard = selected[ComponentType.MOTHERBOARD]
        ram = selected[ComponentType.RAM]
        psu = selected[ComponentType.PSU]
        gpu = selected[ComponentType.GPU]

        checks.append(
            "CPU socket matches motherboard socket"
            if self._is_socket_compatible(cpu, motherboard)
            else f"CPU socket mismatch (CPU: {cpu.socket}, Motherboard: {motherboard.socket_candidates()})"
        )
        checks.append(
            "RAM type is compatible with motherboard" if ram.ram_type == motherboard.ram_type else "RAM type mismatch"
        )

        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
        checks.append(
            f"PSU headroom check passed ({psu.psu_watts}W >= {required_watts}W)"
            if psu.psu_watts >= required_watts
            else f"PSU headroom check failed ({psu.psu_watts}W < {required_watts}W)"
        )

        if needs_wifi:
            checks.append(
                "Motherboard has onboard Wi-Fi" if motherboard.supports_wifi else "Wi-Fi not onboard (requires adapter)"
            )

        return checks

    def _build_explanation(
        self,
        request: ConfigurationRequest,
        selected: dict[ComponentType, ComponentOption],
        total_price: int,
        performance: PerformanceEstimate,
    ) -> list[str]:
        cpu = selected[ComponentType.CPU]
        gpu = selected[ComponentType.GPU]
        motherboard = selected[ComponentType.MOTHERBOARD]
        explanation = [
            f"Configuration optimized for {request.purpose.value} workload within {request.budget} RUB budget.",
            f"CPU ({cpu.model}) and GPU ({gpu.model}) chosen as the best value/performance pair.",
            f"Motherboard ({motherboard.model}) selected for socket and memory compatibility.",
            f"Total cost is {total_price} RUB with performance tier {performance.value}.",
        ]
        if request.preferred_brand != "any":
            preferred_satisfied = any(component.brand == request.preferred_brand for component in selected.values())
            if not preferred_satisfied:
                explanation.append(
                    f"Preferred brand '{request.preferred_brand}' was not selected because no compatible option fit the optimization constraints."
                )
        if request.minimum_performance is not None:
            explanation.append(
                f"Minimum performance tier requirement: {request.minimum_performance.value} (achieved: {performance.value})."
            )
        if request.min_ram_gb > 0:
            explanation.append(f"Minimum RAM requirement: {request.min_ram_gb} GB.")
        if request.min_vram_gb > 0:
            explanation.append(f"Minimum GPU VRAM requirement: {request.min_vram_gb} GB.")
        return explanation

    def _to_selected(self, component_type: ComponentType, option: ComponentOption, purpose: Purpose) -> SelectedComponent:
        return SelectedComponent(
            product_id=option.product_id,
            type=component_type,
            model=option.model,
            brand=option.brand,
            price=option.price,
            score=option.score_for(purpose),
            notes=list(option.notes),
        )

    def _preferred_subset(self, options: list[ComponentOption], preferred_brand: str) -> list[ComponentOption]:
        if preferred_brand == "any":
            return []
        preferred = [option for option in options if option.brand == preferred_brand]
        return preferred

    def _build_minimum_configuration(
        self,
        needs_wifi: bool,
        purpose: Purpose,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> dict[ComponentType, ComponentOption]:
        cheapest_storage = min(catalog[ComponentType.STORAGE], key=lambda option: option.price)
        cheapest_case = min(catalog[ComponentType.CASE], key=lambda option: option.price)

        best: dict[ComponentType, ComponentOption] | None = None
        best_total: int | None = None

        for cpu in catalog[ComponentType.CPU]:
            motherboards = [
                option
                for option in catalog[ComponentType.MOTHERBOARD]
                if self._is_socket_compatible(cpu, option) and (not needs_wifi or option.supports_wifi)
            ]
            for motherboard in motherboards:
                rams = [option for option in catalog[ComponentType.RAM] if option.ram_type == motherboard.ram_type]
                for ram in rams:
                    for gpu in catalog[ComponentType.GPU]:
                        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
                        psus = [option for option in catalog[ComponentType.PSU] if option.psu_watts >= required_watts]
                        if not psus:
                            continue
                        psu = min(psus, key=lambda option: option.price)
                        candidate = {
                            ComponentType.CPU: cpu,
                            ComponentType.GPU: gpu,
                            ComponentType.MOTHERBOARD: motherboard,
                            ComponentType.RAM: ram,
                            ComponentType.STORAGE: cheapest_storage,
                            ComponentType.PSU: psu,
                            ComponentType.CASE: cheapest_case,
                        }
                        total = sum(component.price for component in candidate.values())
                        if best is None or total < best_total:  # type: ignore[operator]
                            best = candidate
                            best_total = total
                        elif total == best_total:
                            assert best is not None
                            candidate_score = self._candidate_score(candidate, purpose)
                            best_score = self._candidate_score(best, purpose)
                            if candidate_score > best_score:
                                best = candidate
                                best_total = total

        if best is None:
            raise CatalogLoadError("Unable to build a compatible configuration from loaded product catalog")
        return best

    def _candidate_score(self, candidate: dict[ComponentType, ComponentOption], purpose: Purpose) -> float:
        return sum(component.score_for(purpose) for component in candidate.values())

    def _minimum_required_budget(self, needs_wifi: bool, catalog: dict[ComponentType, list[ComponentOption]]) -> int:
        minimum = self._build_minimum_configuration(needs_wifi, Purpose.GENERAL, catalog)
        return sum(component.price for component in minimum.values())

    def _resolve_cpu_brand_preference(self, request: ConfigurationRequest) -> str:
        if request.cpu_brand_preference != "any":
            return request.cpu_brand_preference
        if request.preferred_brand in {"intel", "amd"}:
            return request.preferred_brand
        return "any"

    def _resolve_gpu_brand_preference(self, request: ConfigurationRequest) -> str:
        if request.gpu_brand_preference != "any":
            return request.gpu_brand_preference
        if request.preferred_brand in {"nvidia", "amd", "intel"}:
            return request.preferred_brand
        return "any"

    def _performance_rank(self, tier: PerformanceEstimate) -> int:
        return {
            PerformanceEstimate.ENTRY: 1,
            PerformanceEstimate.MID: 2,
            PerformanceEstimate.HIGH: 3,
        }[tier]

    def _is_selection_valid(
        self,
        selected: dict[ComponentType, ComponentOption],
        needs_wifi: bool,
    ) -> bool:
        cpu = selected[ComponentType.CPU]
        gpu = selected[ComponentType.GPU]
        motherboard = selected[ComponentType.MOTHERBOARD]
        ram = selected[ComponentType.RAM]
        psu = selected[ComponentType.PSU]

        if not self._is_socket_compatible(cpu, motherboard):
            return False
        if ram.ram_type != motherboard.ram_type:
            return False
        if needs_wifi and not motherboard.supports_wifi:
            return False
        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
        if psu.psu_watts < required_watts:
            return False
        return True

    def _validate_selected_configuration(
        self,
        selected: dict[ComponentType, ComponentOption],
        needs_wifi: bool,
    ) -> None:
        if not self._is_selection_valid(selected, needs_wifi):
            raise self.PreferenceConstraintError(
                "Selected parameter constraints produced an incompatible configuration. "
                "Adjust requested parameters or Wi-Fi requirement."
            )

    def _apply_capacity_preferences(
        self,
        request: ConfigurationRequest,
        catalog: dict[ComponentType, list[ComponentOption]],
    ) -> dict[ComponentType, list[ComponentOption]]:
        filtered = {component_type: list(options) for component_type, options in catalog.items()}

        if request.min_ram_gb > 0:
            ram_options = [
                option for option in filtered[ComponentType.RAM] if self._ram_capacity_gb(option) >= request.min_ram_gb
            ]
            if not ram_options:
                raise self.PreferenceConstraintError(
                    f"No RAM options found with capacity at least {request.min_ram_gb} GB."
                )
            filtered[ComponentType.RAM] = ram_options

        if request.min_vram_gb > 0:
            gpu_options = [
                option for option in filtered[ComponentType.GPU] if self._vram_capacity_gb(option) >= request.min_vram_gb
            ]
            if not gpu_options:
                raise self.PreferenceConstraintError(
                    f"No GPU options found with VRAM at least {request.min_vram_gb} GB."
                )
            filtered[ComponentType.GPU] = gpu_options

        return filtered

    def _ram_capacity_gb(self, option: ComponentOption) -> int:
        combined = " ".join([option.model, *option.notes])
        return self._extract_first_gb_value(combined)

    def _vram_capacity_gb(self, option: ComponentOption) -> int:
        combined = " ".join([option.model, *option.notes]).upper()
        explicit = self._extract_first_gb_value(combined)
        if explicit > 0:
            return explicit

        heuristics: dict[str, int] = {
            "RTX 4090": 24,
            "RTX 4080": 16,
            "RTX 4070": 12,
            "RTX 4060": 8,
            "RX 7900": 20,
            "RX 7800": 16,
            "RX 7700": 12,
            "RX 7600": 8,
            "ARC A770": 16,
            "ARC A750": 8,
        }
        for marker, value in heuristics.items():
            if marker in combined:
                return value
        return 0

    def _extract_first_gb_value(self, text: str) -> int:
        match = re.search(r"(\d{1,3})\s*GB", text, flags=re.IGNORECASE)
        if not match:
            return 0
        try:
            return int(match.group(1))
        except ValueError:
            return 0

    def _socket_family(self, socket_name: str) -> set[str]:
        normalized = socket_name.strip().upper()
        return SOCKET_ALIASES.get(normalized, {normalized})

    def _is_socket_compatible(self, cpu: ComponentOption, motherboard: ComponentOption) -> bool:
        if cpu.socket is None:
            return False
        cpu_socket_family = self._socket_family(cpu.socket)
        motherboard_sockets = motherboard.socket_candidates()
        if not motherboard_sockets:
            return False
        for board_socket in motherboard_sockets:
            if cpu_socket_family & self._socket_family(board_socket):
                return True
        return False
