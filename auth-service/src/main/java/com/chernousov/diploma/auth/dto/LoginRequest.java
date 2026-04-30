package com.chernousov.diploma.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record LoginRequest(
        @NotBlank(message = "Username is required")
        @Size(min = 3, max = 120, message = "Username must be between 3 and 120 characters")
        @Pattern(regexp = "^[A-Za-z0-9._-]+$", message = "Username may contain only letters, digits, dot, underscore and dash")
        String username,

        @NotBlank(message = "Password is required")
        @Size(min = 8, max = 120, message = "Password must be between 8 and 120 characters")
        String password
) {
}
