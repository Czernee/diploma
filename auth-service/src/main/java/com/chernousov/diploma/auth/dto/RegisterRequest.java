package com.chernousov.diploma.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
        @NotBlank(message = "Username is required")
        @Size(min = 3, max = 120, message = "Username must be between 3 and 120 characters")
        @Pattern(regexp = "^[A-Za-z0-9._-]+$", message = "Username may contain only letters, digits, dot, underscore and dash")
        String username,

        @NotBlank(message = "Email is required")
        @Email(message = "Email format is invalid")
        @Size(max = 180, message = "Email must be at most 180 characters")
        String email,

        @NotBlank(message = "Password is required")
        @Size(min = 8, max = 120, message = "Password must be between 8 and 120 characters")
        @Pattern(
                regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^\\w\\s])(?!.*\\s).+$",
                message = "Password must include uppercase, lowercase, digit and special character, and must not contain spaces"
        )
        String password
) {
}
