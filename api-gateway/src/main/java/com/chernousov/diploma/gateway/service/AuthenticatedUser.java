package com.chernousov.diploma.gateway.service;

public record AuthenticatedUser(
        Long id,
        String username,
        String email,
        String role
) {
}
