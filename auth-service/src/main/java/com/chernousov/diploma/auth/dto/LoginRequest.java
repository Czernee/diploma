package com.chernousov.diploma.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record LoginRequest(
        @NotBlank @Size(min = 3, max = 180) String username,
        @NotBlank @Size(min = 8, max = 120) String password
) {
}
