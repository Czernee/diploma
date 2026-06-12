package com.chernousov.diploma.order.controller;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.ConfigurationHistoryResponse;
import com.chernousov.diploma.order.exception.InvalidUserHeaderException;
import com.chernousov.diploma.order.service.ConfigurationHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import tools.jackson.databind.JsonNode;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/orders/configurations")
public class ConfigurationHistoryController {

    private final ConfigurationHistoryService configurationHistoryService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ConfigurationHistoryResponse save(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @RequestBody JsonNode payload
    ) {
        return configurationHistoryService.save(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), payload);
    }

    @GetMapping
    public List<ConfigurationHistoryResponse> list(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader
    ) {
        return configurationHistoryService.list(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader));
    }

    @GetMapping("/{configurationId:\\d+}")
    public ConfigurationHistoryResponse getById(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @PathVariable Long configurationId
    ) {
        return configurationHistoryService.findById(
                parseUserHeader(userIdHeader, usernameHeader, userRoleHeader),
                configurationId
        );
    }

    private AuthenticatedUserHeader parseUserHeader(String userIdHeader, String usernameHeader, String userRoleHeader) {
        if (usernameHeader == null || usernameHeader.isBlank()) {
            throw new InvalidUserHeaderException("X-User-Name header is required");
        }
        try {
            String normalizedRole = (userRoleHeader == null || userRoleHeader.isBlank())
                    ? "USER"
                    : userRoleHeader.trim().toUpperCase();
            return new AuthenticatedUserHeader(Long.parseLong(userIdHeader), usernameHeader, normalizedRole);
        } catch (NumberFormatException exception) {
            throw new InvalidUserHeaderException("X-User-Id header must be numeric");
        }
    }
}
