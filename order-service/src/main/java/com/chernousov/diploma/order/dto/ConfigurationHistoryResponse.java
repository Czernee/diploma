package com.chernousov.diploma.order.dto;

import java.math.BigDecimal;
import java.time.Instant;

public record ConfigurationHistoryResponse(
        Long id,
        Long userId,
        String username,
        String purpose,
        BigDecimal budget,
        BigDecimal totalPrice,
        String currency,
        String performanceEstimate,
        Instant createdAt
) {
}
