package com.chernousov.diploma.order.dto;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

public record CartItemRequest(
        @NotNull Long productId,
        @NotBlank @Size(max = 180) String productName,
        @NotNull @Min(1) Integer quantity,
        @NotNull @DecimalMin(value = "0.0", inclusive = false) BigDecimal unitPrice,
        @NotBlank @Size(min = 3, max = 16) String currency
) {
}

