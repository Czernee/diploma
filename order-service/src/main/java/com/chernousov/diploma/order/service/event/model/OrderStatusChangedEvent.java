package com.chernousov.diploma.order.service.event.model;

import com.chernousov.diploma.order.domain.OrderStatus;

import java.time.Instant;

public record OrderStatusChangedEvent(
        Long orderId,
        Long userId,
        String username,
        OrderStatus previousStatus,
        OrderStatus newStatus,
        Instant occurredAt
) {
}
