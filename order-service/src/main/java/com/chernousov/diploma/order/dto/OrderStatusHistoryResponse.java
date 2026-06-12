package com.chernousov.diploma.order.dto;

import java.time.Instant;

public record OrderStatusHistoryResponse(
        Long id,
        Long orderId,
        String previousStatus,
        String newStatus,
        String eventType,
        Instant changedAt
) {
}
