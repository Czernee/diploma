package com.chernousov.diploma.order.dto;

import com.chernousov.diploma.order.domain.OrderStatus;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

public record OrderResponse(
        Long id,
        Long userId,
        String username,
        OrderStatus status,
        BigDecimal totalAmount,
        String currency,
        String note,
        Instant createdAt,
        List<OrderItemResponse> items
) {
}