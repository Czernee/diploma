package com.chernousov.diploma.auth.dto;

public record UserProfileResponse(
        Long id,
        String username,
        String email,
        String role
) {
}
