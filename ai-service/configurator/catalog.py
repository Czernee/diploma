from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx

from .models import ComponentType, Purpose


@dataclass(frozen=True)
class ComponentOption:
    type: ComponentType
    model: str
    brand: str
    price: int
    score_gaming: float
    score_work: float
    score_study: float
    score_general: float
    socket: str | None = None
    supported_sockets: tuple[str, ...] = field(default_factory=tuple)
    ram_type: str | None = None
    gpu_tdp: int = 0
    cpu_tdp: int = 0
    psu_watts: int = 0
    supports_wifi: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)
    product_id: int | None = None

    def score_for(self, purpose: Purpose) -> float:
        if purpose == Purpose.GAMING:
            return self.score_gaming
        if purpose == Purpose.WORK:
            return self.score_work
        if purpose == Purpose.STUDY:
            return self.score_study
        return self.score_general

    def socket_candidates(self) -> tuple[str, ...]:
        candidates = []
        if self.socket:
            candidates.append(self.socket)
        candidates.extend(self.supported_sockets)
        return tuple(dict.fromkeys(candidates))


class CatalogLoadError(RuntimeError):
    pass


class ProductCatalogProvider:
    def __init__(self, base_url: str | None = None, timeout_seconds: float = 5.0):
        self._base_url = (base_url or os.getenv("PRODUCT_SERVICE_URL") or "http://localhost:8082").rstrip("/")
        self._timeout_seconds = timeout_seconds

    def load_catalog(self) -> dict[ComponentType, list[ComponentOption]]:
        url = f"{self._base_url}/api/products/configurator"
        try:
            response = httpx.get(url, params={"inStock": "true"}, timeout=self._timeout_seconds)
            response.raise_for_status()
        except Exception as error:
            raise CatalogLoadError(f"Failed to load product catalog from {url}") from error

        payload = response.json()
        if not isinstance(payload, list):
            raise CatalogLoadError("Product catalog response must be a JSON array")

        catalog: dict[ComponentType, list[ComponentOption]] = {component_type: [] for component_type in ComponentType}
        for item in payload:
            try:
                component_type = ComponentType(str(item["componentType"]).strip().lower())
            except Exception as error:
                raise CatalogLoadError(f"Invalid componentType in product item: {item}") from error

            price = int(round(float(item.get("price", 0))))
            option = ComponentOption(
                type=component_type,
                model=str(item.get("name", "")).strip(),
                brand=str(item.get("brand", "")).strip().lower(),
                price=price,
                score_gaming=float(item.get("scoreGaming", 0.0)),
                score_work=float(item.get("scoreWork", 0.0)),
                score_study=float(item.get("scoreStudy", 0.0)),
                score_general=float(item.get("scoreGeneral", 0.0)),
                socket=_normalize_str(item.get("socket")),
                supported_sockets=tuple(_normalize_upper_list(item.get("supportedSockets"))),
                ram_type=_normalize_upper(item.get("ramType")),
                gpu_tdp=int(item.get("gpuTdp") or 0),
                cpu_tdp=int(item.get("cpuTdp") or 0),
                psu_watts=int(item.get("psuWatts") or 0),
                supports_wifi=bool(item.get("supportsWifi", False)),
                notes=tuple(_normalize_notes(item.get("notes"))),
                product_id=_to_int(item.get("id")),
            )

            if option.model and option.price > 0:
                catalog[component_type].append(option)

        self._validate_catalog(catalog)
        return catalog

    def _validate_catalog(self, catalog: dict[ComponentType, list[ComponentOption]]) -> None:
        missing = [component_type.value for component_type, items in catalog.items() if not items]
        if missing:
            raise CatalogLoadError(f"Catalog is incomplete. Missing component groups: {', '.join(missing)}")


class InMemoryCatalogProvider:
    def __init__(self, catalog: dict[ComponentType, list[ComponentOption]]):
        self._catalog = catalog

    def load_catalog(self) -> dict[ComponentType, list[ComponentOption]]:
        return self._catalog


def _normalize_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_upper(value: object) -> str | None:
    normalized = _normalize_str(value)
    if normalized is None:
        return None
    return normalized.upper()


def _normalize_upper_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _normalize_upper(item)
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def _normalize_notes(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    notes: list[str] = []
    for item in value:
        text = _normalize_str(item)
        if text and text not in notes:
            notes.append(text)
    return notes


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
