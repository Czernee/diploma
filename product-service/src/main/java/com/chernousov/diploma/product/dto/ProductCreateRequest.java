package com.chernousov.diploma.product.dto;

import com.chernousov.diploma.product.domain.ProductComponentType;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.util.List;

public record ProductCreateRequest(
        @NotBlank
        @Size(max = 180)
        String name,
        @Size(max = 2000)
        String description,
        @NotBlank
        @Size(max = 120)
        String brand,
        @NotNull
        @DecimalMin(value = "0.01")
        BigDecimal price,
        @NotBlank
        @Pattern(regexp = "^[A-Za-z]{3,8}$")
        String currency,
        @NotNull
        Boolean inStock,
        @NotNull
        @Min(0)
        Integer stockQuantity,
        @NotNull
        Long categoryId,
        ProductComponentType componentType,
        @Size(max = 40)
        String socket,
        List<@Size(max = 40) String> supportedSockets,
        @Size(max = 20)
        String ramType,
        @NotNull
        @Min(0)
        Integer gpuTdp,
        @NotNull
        @Min(0)
        Integer cpuTdp,
        @NotNull
        @Min(0)
        Integer psuWatts,
        @NotNull
        Boolean supportsWifi,
        @NotNull
        @DecimalMin(value = "0.00")
        @DecimalMax(value = "10.00")
        BigDecimal scoreGaming,
        @NotNull
        @DecimalMin(value = "0.00")
        @DecimalMax(value = "10.00")
        BigDecimal scoreWork,
        @NotNull
        @DecimalMin(value = "0.00")
        @DecimalMax(value = "10.00")
        BigDecimal scoreStudy,
        @NotNull
        @DecimalMin(value = "0.00")
        @DecimalMax(value = "10.00")
        BigDecimal scoreGeneral,
        @Size(max = 1000)
        String notes
) {
}
