package com.chernousov.diploma.order.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.List;

public record CreateOrderRequest(
        @Valid @NotEmpty List<CreateOrderItemRequest> items,
        @Size(max = 500) String note,
        @NotNull @Size(min = 3, max = 16) String currency
) {
}