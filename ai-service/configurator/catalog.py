from __future__ import annotations

from dataclasses import dataclass, field

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
    ram_type: str | None = None
    gpu_tdp: int = 0
    cpu_tdp: int = 0
    psu_watts: int = 0
    supports_wifi: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    def score_for(self, purpose: Purpose) -> float:
        if purpose == Purpose.GAMING:
            return self.score_gaming
        if purpose == Purpose.WORK:
            return self.score_work
        if purpose == Purpose.STUDY:
            return self.score_study
        return self.score_general


CATALOG: dict[ComponentType, list[ComponentOption]] = {
    ComponentType.CPU: [
        ComponentOption(ComponentType.CPU, "AMD Ryzen 5 5600", "amd", 11000, 7.6, 7.2, 7.0, 7.2, socket="AM4", cpu_tdp=65),
        ComponentOption(ComponentType.CPU, "AMD Ryzen 5 7600", "amd", 19000, 8.5, 8.3, 8.0, 8.2, socket="AM5", cpu_tdp=65),
        ComponentOption(ComponentType.CPU, "Intel Core i5-13400F", "intel", 18500, 8.2, 8.1, 7.8, 7.9, socket="LGA1700", cpu_tdp=65),
        ComponentOption(ComponentType.CPU, "Intel Core i7-13700", "intel", 29000, 9.0, 9.3, 8.2, 8.8, socket="LGA1700", cpu_tdp=65),
    ],
    ComponentType.GPU: [
        ComponentOption(ComponentType.GPU, "NVIDIA RTX 4060", "nvidia", 32000, 8.0, 7.0, 6.5, 7.0, gpu_tdp=115),
        ComponentOption(ComponentType.GPU, "NVIDIA RTX 4070 SUPER", "nvidia", 62000, 9.3, 8.2, 6.8, 8.0, gpu_tdp=220),
        ComponentOption(ComponentType.GPU, "AMD Radeon RX 7600", "amd", 29000, 7.8, 6.9, 6.3, 6.8, gpu_tdp=165),
        ComponentOption(ComponentType.GPU, "AMD Radeon RX 7800 XT", "amd", 56000, 9.0, 8.0, 6.7, 7.8, gpu_tdp=263),
    ],
    ComponentType.MOTHERBOARD: [
        ComponentOption(ComponentType.MOTHERBOARD, "MSI B550-A PRO", "msi", 11500, 7.0, 7.0, 7.0, 7.0, socket="AM4", ram_type="DDR4"),
        ComponentOption(ComponentType.MOTHERBOARD, "ASUS TUF B650-PLUS WIFI", "asus", 22000, 8.5, 8.5, 8.2, 8.4, socket="AM5", ram_type="DDR5", supports_wifi=True),
        ComponentOption(ComponentType.MOTHERBOARD, "Gigabyte B760M DS3H", "gigabyte", 15000, 7.8, 7.8, 7.5, 7.6, socket="LGA1700", ram_type="DDR4"),
        ComponentOption(ComponentType.MOTHERBOARD, "ASRock B760 Pro RS", "asrock", 17000, 8.0, 8.1, 7.6, 7.8, socket="LGA1700", ram_type="DDR5"),
    ],
    ComponentType.RAM: [
        ComponentOption(ComponentType.RAM, "32GB DDR4 3200 (2x16)", "kingston", 8000, 8.0, 8.2, 7.5, 7.8, ram_type="DDR4"),
        ComponentOption(ComponentType.RAM, "16GB DDR4 3200 (2x8)", "kingston", 5000, 7.2, 7.2, 7.3, 7.2, ram_type="DDR4"),
        ComponentOption(ComponentType.RAM, "32GB DDR5 6000 (2x16)", "gskill", 13000, 8.8, 9.0, 8.0, 8.4, ram_type="DDR5"),
        ComponentOption(ComponentType.RAM, "16GB DDR5 5600 (2x8)", "crucial", 8500, 7.9, 8.0, 7.6, 7.7, ram_type="DDR5"),
    ],
    ComponentType.STORAGE: [
        ComponentOption(ComponentType.STORAGE, "NVMe SSD 1TB PCIe 4.0", "wd", 7000, 8.0, 8.3, 7.8, 7.9),
        ComponentOption(ComponentType.STORAGE, "NVMe SSD 2TB PCIe 4.0", "samsung", 13000, 8.8, 9.0, 8.0, 8.4),
        ComponentOption(ComponentType.STORAGE, "NVMe SSD 512GB PCIe 3.0", "kingston", 4500, 6.8, 6.8, 7.0, 6.9),
    ],
    ComponentType.PSU: [
        ComponentOption(ComponentType.PSU, "650W 80+ Bronze", "deepcool", 5500, 7.5, 7.5, 7.3, 7.4, psu_watts=650),
        ComponentOption(ComponentType.PSU, "750W 80+ Gold", "corsair", 9000, 8.6, 8.6, 8.2, 8.4, psu_watts=750),
        ComponentOption(ComponentType.PSU, "850W 80+ Gold", "bequiet", 12000, 9.0, 9.0, 8.5, 8.8, psu_watts=850),
    ],
    ComponentType.CASE: [
        ComponentOption(ComponentType.CASE, "ATX Mid Tower Airflow", "zalman", 5000, 7.5, 7.5, 7.5, 7.5),
        ComponentOption(ComponentType.CASE, "ATX Mid Tower Premium", "lianli", 9000, 8.7, 8.5, 8.2, 8.4),
    ],
}
