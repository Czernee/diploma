package com.chernousov.diploma.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "gateway.services")
public record GatewayServicesProperties(
        String auth,
        String product,
        String order,
        String ai
) {
}
