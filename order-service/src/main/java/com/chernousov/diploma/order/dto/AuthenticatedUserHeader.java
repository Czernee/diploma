package com.chernousov.diploma.order.dto;

public record AuthenticatedUserHeader(
        Long userId,
        String username,
        String role
) {
    public boolean isAdmin() {
        return "ADMIN".equalsIgnoreCase(role);
    }
}
