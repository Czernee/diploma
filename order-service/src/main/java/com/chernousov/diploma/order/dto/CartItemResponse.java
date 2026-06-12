package com.chernousov.diploma.order.dto;

import java.math.BigDecimal;

public record CartItemResponse(
        Long productId,
        String productName,
        Integer quantity,
        BigDecimal unitPrice,
        String currency,
        BigDecimal lineTotal
) {
}

