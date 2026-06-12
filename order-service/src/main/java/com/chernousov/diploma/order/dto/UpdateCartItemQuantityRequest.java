package com.chernousov.diploma.order.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public record UpdateCartItemQuantityRequest(
        @NotNull @Min(0) Integer quantity
) {
}

