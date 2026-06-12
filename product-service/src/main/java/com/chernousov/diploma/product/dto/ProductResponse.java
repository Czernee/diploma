package com.chernousov.diploma.product.dto;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

public record ProductResponse(
        Long id,
        String name,
        String description,
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
        boolean inStock,
        Integer stockQuantity,
        CategoryResponse category
) implements Serializable {
}
