package com.chernousov.diploma.product.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;

import java.math.BigDecimal;

public record ProductSearchRequest(
        String query,
        String category,
        @DecimalMin(value = "0.0", inclusive = true) BigDecimal minPrice,
        @DecimalMin(value = "0.0", inclusive = true) BigDecimal maxPrice,
        Boolean inStock,
        @Min(0) Integer page,
        @Min(1) Integer size
) {

    public int pageOrDefault() {
        return page == null ? 0 : page;
    }

    public int sizeOrDefault() {
        return size == null ? 20 : Math.min(size, 100);
    }
}
