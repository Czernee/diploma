package com.chernousov.diploma.product.dto;

import java.math.BigDecimal;
import java.util.List;

public record ConfiguratorComponentResponse(
        Long id,
        String name,
        String brand,
        BigDecimal price,
        String currency,
        String componentType,
        String socket,
        List<String> supportedSockets,
        String ramType,
        Integer gpuTdp,
        Integer cpuTdp,
        Integer psuWatts,
        boolean supportsWifi,
        BigDecimal scoreGaming,
        BigDecimal scoreWork,
        BigDecimal scoreStudy,
        BigDecimal scoreGeneral,
        List<String> notes,
        boolean inStock
) {
}
