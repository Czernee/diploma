package com.chernousov.diploma.order.dto;

public record AuthenticatedUserHeader(
        Long userId,
        String username
) {
}