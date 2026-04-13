from __future__ import annotations

from dataclasses import dataclass

from .catalog import CATALOG, ComponentOption
from .models import (
    ComponentType,
    ConfigurationRequest,
    ConfigurationResponse,
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


class ConfiguratorEngine:
    class BudgetConstraintError(ValueError):
        def __init__(self, budget: int, minimum_required_budget: int):
            super().__init__(
                f"Budget {budget} RUB is too low for a compatible build. "
                f"Minimum required budget is {minimum_required_budget} RUB."
            )
            self.budget = budget
            self.minimum_required_budget = minimum_required_budget

    def recommend(self, request: ConfigurationRequest) -> ConfigurationResponse:
        minimum_required_budget = self._minimum_required_budget(request.needs_wifi)
        if request.budget < minimum_required_budget:
            raise self.BudgetConstraintError(request.budget, minimum_required_budget)

        profile = ALLOCATION_BY_PURPOSE[request.purpose]
        allocations = self._build_allocations(request.budget, profile)

        cpu = self._pick_best(
            ComponentType.CPU,
            budget_limit=allocations[ComponentType.CPU],
            purpose=request.purpose,
            preferred_brand=request.preferred_brand,
        )
        gpu = self._pick_best(
            ComponentType.GPU,
            budget_limit=allocations[ComponentType.GPU],
            purpose=request.purpose,
            preferred_brand=request.preferred_brand,
        )
        motherboard = self._pick_motherboard(cpu, request.needs_wifi, allocations[ComponentType.MOTHERBOARD], request.purpose)
        ram = self._pick_ram(motherboard, allocations[ComponentType.RAM], request.purpose)
        storage = self._pick_best(ComponentType.STORAGE, allocations[ComponentType.STORAGE], request.purpose, "any")
        psu = self._pick_psu(cpu, gpu, allocations[ComponentType.PSU], request.purpose)
        case = self._pick_best(ComponentType.CASE, allocations[ComponentType.CASE], request.purpose, "any")

        selected = {
            ComponentType.CPU: cpu,
            ComponentType.GPU: gpu,
            ComponentType.MOTHERBOARD: motherboard,
            ComponentType.RAM: ram,
            ComponentType.STORAGE: storage,
            ComponentType.PSU: psu,
            ComponentType.CASE: case,
        }

        self._fit_into_budget(selected, request.budget, request.purpose, request.needs_wifi)
        if sum(component.price for component in selected.values()) > request.budget:
            selected = self._build_minimum_configuration(request.needs_wifi, request.purpose)

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
        explanation = self._build_explanation(request, selected, total_price, performance)

        return ConfigurationResponse(
            purpose=request.purpose,
            budget=request.budget,
            total_price=total_price,
            components=components,
            performance_estimate=performance,
            compatibility_checks=compatibility,
            explanation=explanation,
        )

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

    def _pick_best(self, component_type: ComponentType, budget_limit: int, purpose: Purpose, preferred_brand: str) -> ComponentOption:
        options = CATALOG[component_type]
        affordable = [option for option in options if option.price <= budget_limit]
        if not affordable:
            affordable = options
        preferred_affordable = self._preferred_subset(affordable, preferred_brand)
        if preferred_affordable:
            affordable = preferred_affordable
        scored = sorted(
            affordable,
            key=lambda option: self._composite_score(option, purpose, preferred_brand),
            reverse=True,
        )
        return scored[0]

    def _pick_motherboard(self, cpu: ComponentOption, needs_wifi: bool, budget_limit: int, purpose: Purpose) -> ComponentOption:
        options = [
            option for option in CATALOG[ComponentType.MOTHERBOARD]
            if option.socket == cpu.socket and (not needs_wifi or option.supports_wifi)
        ]
        if not options:
            options = [option for option in CATALOG[ComponentType.MOTHERBOARD] if option.socket == cpu.socket]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _pick_ram(self, motherboard: ComponentOption, budget_limit: int, purpose: Purpose) -> ComponentOption:
        options = [option for option in CATALOG[ComponentType.RAM] if option.ram_type == motherboard.ram_type]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _pick_psu(self, cpu: ComponentOption, gpu: ComponentOption, budget_limit: int, purpose: Purpose) -> ComponentOption:
        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
        options = [option for option in CATALOG[ComponentType.PSU] if option.psu_watts >= required_watts]
        affordable = [option for option in options if option.price <= budget_limit] or options
        return sorted(affordable, key=lambda option: option.score_for(purpose), reverse=True)[0]

    def _fit_into_budget(
        self,
        selected: dict[ComponentType, ComponentOption],
        budget: int,
        purpose: Purpose,
        needs_wifi: bool,
    ) -> None:
        def total() -> int:
            return sum(component.price for component in selected.values())

        downgrade_order = [ComponentType.GPU, ComponentType.CPU, ComponentType.STORAGE, ComponentType.CASE]
        while total() > budget:
            changed = False
            for component_type in downgrade_order:
                current = selected[component_type]
                candidates = [
                    option for option in CATALOG[component_type]
                    if option.price < current.price and self._is_compatible_swap(component_type, option, selected)
                ]
                if not candidates:
                    continue
                replacement = sorted(candidates, key=lambda option: option.score_for(purpose), reverse=True)[0]
                selected[component_type] = replacement
                if component_type in (ComponentType.CPU, ComponentType.GPU):
                    selected[ComponentType.PSU] = self._pick_psu(
                        selected[ComponentType.CPU],
                        selected[ComponentType.GPU],
                        budget_limit=budget,
                        purpose=purpose,
                    )
                    selected[ComponentType.MOTHERBOARD] = self._pick_motherboard(
                        selected[ComponentType.CPU],
                        needs_wifi=needs_wifi,
                        budget_limit=budget,
                        purpose=purpose,
                    )
                    selected[ComponentType.RAM] = self._pick_ram(selected[ComponentType.MOTHERBOARD], budget, purpose)
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
            return motherboard.socket == candidate.socket
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
            Purpose.GAMING: {ComponentType.CPU: 0.25, ComponentType.GPU: 0.55, ComponentType.RAM: 0.12, ComponentType.STORAGE: 0.08},
            Purpose.WORK: {ComponentType.CPU: 0.38, ComponentType.GPU: 0.30, ComponentType.RAM: 0.20, ComponentType.STORAGE: 0.12},
            Purpose.STUDY: {ComponentType.CPU: 0.35, ComponentType.GPU: 0.25, ComponentType.RAM: 0.22, ComponentType.STORAGE: 0.18},
            Purpose.GENERAL: {ComponentType.CPU: 0.34, ComponentType.GPU: 0.30, ComponentType.RAM: 0.20, ComponentType.STORAGE: 0.16},
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

        checks.append("CPU socket matches motherboard socket" if cpu.socket == motherboard.socket else "CPU socket mismatch")
        checks.append("RAM type is compatible with motherboard" if ram.ram_type == motherboard.ram_type else "RAM type mismatch")

        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
        checks.append(
            f"PSU headroom check passed ({psu.psu_watts}W >= {required_watts}W)"
            if psu.psu_watts >= required_watts else
            f"PSU headroom check failed ({psu.psu_watts}W < {required_watts}W)"
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
            preferred_satisfied = any(
                component.brand == request.preferred_brand
                for component in selected.values()
            )
            if not preferred_satisfied:
                explanation.append(
                    f"Preferred brand '{request.preferred_brand}' was not selected because no compatible option fit the optimization constraints."
                )
        return explanation

    def _to_selected(self, component_type: ComponentType, option: ComponentOption, purpose: Purpose) -> SelectedComponent:
        return SelectedComponent(
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

    def _build_minimum_configuration(self, needs_wifi: bool, purpose: Purpose) -> dict[ComponentType, ComponentOption]:
        cheapest_storage = min(CATALOG[ComponentType.STORAGE], key=lambda option: option.price)
        cheapest_case = min(CATALOG[ComponentType.CASE], key=lambda option: option.price)

        best: dict[ComponentType, ComponentOption] | None = None
        best_total: int | None = None

        for cpu in CATALOG[ComponentType.CPU]:
            motherboards = [
                option for option in CATALOG[ComponentType.MOTHERBOARD]
                if option.socket == cpu.socket and (not needs_wifi or option.supports_wifi)
            ]
            for motherboard in motherboards:
                rams = [option for option in CATALOG[ComponentType.RAM] if option.ram_type == motherboard.ram_type]
                for ram in rams:
                    for gpu in CATALOG[ComponentType.GPU]:
                        required_watts = cpu.cpu_tdp + gpu.gpu_tdp + 150
                        psus = [option for option in CATALOG[ComponentType.PSU] if option.psu_watts >= required_watts]
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
            raise ValueError("Unable to build a compatible configuration from current catalog")
        return best

    def _candidate_score(self, candidate: dict[ComponentType, ComponentOption], purpose: Purpose) -> float:
        return sum(component.score_for(purpose) for component in candidate.values())

    def _minimum_required_budget(self, needs_wifi: bool) -> int:
        minimum = self._build_minimum_configuration(needs_wifi, Purpose.GENERAL)
        return sum(component.price for component in minimum.values())
