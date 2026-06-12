from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Purpose(str, Enum):
    GAMING = "gaming"
    WORK = "work"
    STUDY = "study"
    GENERAL = "general"


class PerformanceEstimate(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    HIGH = "high"


class ComponentType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    MOTHERBOARD = "motherboard"
    RAM = "ram"
    STORAGE = "storage"
    PSU = "psu"
    CASE = "case"


class ConfigurationRequest(BaseModel):
    budget: int = Field(..., ge=30000, le=600000)
    purpose: Purpose
    preferred_brand: Literal["intel", "amd", "nvidia", "any"] = "any"
    needs_wifi: bool = False
    target_resolution: Literal["1080p", "1440p", "4k"] = "1080p"
    minimum_performance: PerformanceEstimate | None = None
    cpu_brand_preference: Literal["intel", "amd", "any"] = "any"
    gpu_brand_preference: Literal["nvidia", "amd", "intel", "any"] = "any"
    min_ram_gb: int = Field(default=0, ge=0, le=256)
    min_vram_gb: int = Field(default=0, ge=0, le=64)


class SelectedComponent(BaseModel):
    product_id: int | None = None
    type: ComponentType
    model: str
    brand: str
    price: int
    score: float
    notes: list[str] = Field(default_factory=list)


class ConfigurationVariant(BaseModel):
    purpose: Purpose
    budget: int
    total_price: int
    currency: Literal["RUB"] = "RUB"
    performance_estimate: PerformanceEstimate
    ml_score: float = Field(default=0.0, ge=0.0, le=1.0)
    components: list[SelectedComponent]
    compatibility_checks: list[str]
    explanation: list[str]

    @field_validator("components")
    @classmethod
    def components_must_not_be_empty(cls, value: list[SelectedComponent]) -> list[SelectedComponent]:
        if not value:
            raise ValueError("components must not be empty")
        return value


class ConfigurationAlternatives(BaseModel):
    cheaper: ConfigurationVariant | None = None
    pricier: ConfigurationVariant | None = None


class ConfigurationResponse(ConfigurationVariant):
    alternatives: ConfigurationAlternatives | None = None


class AssistantMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ConfiguratorAssistantRequest(BaseModel):
    message: str = Field(..., min_length=3, max_length=4000)
    history: list[AssistantMessage] = Field(default_factory=list, max_length=10)


class ConfiguratorAssistantResponse(BaseModel):
    mode: Literal["chat", "recommendation"]
    answer: str
    extracted_request: ConfigurationRequest | None = None
    recommendation: ConfigurationResponse | None = None
    llm_model: str | None = None
    llm_used: bool = False
