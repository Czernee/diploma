package com.chernousov.diploma.order.service.event.model;

import java.math.BigDecimal;

public record OrderItemEvent(
        Long productId,
        String productName,
        Integer quantity,
        BigDecimal unitPrice,
        BigDecimal lineTotal
) {
}
