package com.chernousov.diploma.order.dto;

import com.chernousov.diploma.order.domain.OrderStatus;
import jakarta.validation.constraints.NotNull;

public record UpdateOrderStatusRequest(
        @NotNull OrderStatus status
) {
}