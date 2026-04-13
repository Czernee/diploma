package com.chernousov.diploma.order.service.event.model;

import com.chernousov.diploma.order.domain.OrderStatus;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

public record OrderCreatedEvent(
        Long orderId,
        Long userId,
        String username,
        OrderStatus status,
        BigDecimal totalAmount,
        String currency,
        String note,
        Instant occurredAt,
        List<OrderItemEvent> items
) {
}
