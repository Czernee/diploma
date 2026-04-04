package com.chernousov.diploma.product.dto;

import java.math.BigDecimal;

public record ProductResponse(
        Long id,
        String name,
        String description,
        String brand,
        BigDecimal price,
        String currency,
        boolean inStock,
        Integer stockQuantity,
        CategoryResponse category
) {
}
