package com.chernousov.diploma.auth.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "auth.jwt")
public record AuthJwtProperties(
        String secret,
        long expirationMinutes
) {
}
