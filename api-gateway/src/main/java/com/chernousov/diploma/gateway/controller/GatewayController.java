package com.chernousov.diploma.gateway.controller;

import com.chernousov.diploma.gateway.config.GatewayServicesProperties;
import com.chernousov.diploma.gateway.service.AuthValidationService;
import com.chernousov.diploma.gateway.service.AuthenticatedUser;
import com.chernousov.diploma.gateway.service.GatewayProxyService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
public class GatewayController {

    private final GatewayProxyService gatewayProxyService;
    private final AuthValidationService authValidationService;
    private final GatewayServicesProperties services;

    public GatewayController(
            GatewayProxyService gatewayProxyService,
            AuthValidationService authValidationService,
            GatewayServicesProperties services
    ) {
        this.gatewayProxyService = gatewayProxyService;
        this.authValidationService = authValidationService;
        this.services = services;
    }

    @RequestMapping("/api/status")
    public ResponseEntity<String> status() {
        return ResponseEntity.ok("api-gateway is running");
    }

    @RequestMapping({"/api/auth", "/api/auth/**"})
    public ResponseEntity<byte[]> auth(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, services.auth(), false);
    }

    @RequestMapping({"/api/products", "/api/products/**"})
    public ResponseEntity<byte[]> products(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        if (HttpMethod.GET.matches(request.getMethod())) {
            return proxy(request, body, services.product(), false);
        }
        return proxyProductsWrite(request, body);
    }

    @RequestMapping({"/api/orders", "/api/orders/**"})
    public ResponseEntity<byte[]> orders(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, services.order(), true);
    }

    @RequestMapping({"/api/configurator", "/api/configurator/**"})
    public ResponseEntity<byte[]> configurator(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, services.ai(), true);
    }

    private ResponseEntity<byte[]> proxy(
            HttpServletRequest request,
            byte[] body,
            String serviceBaseUrl,
            boolean authRequired
    ) {
        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        HttpHeaders headers = extractHeaders(request);
        if (authRequired) {
            AuthenticatedUser user = authValidationService.requireUser(headers);
            if (user.id() != null) {
                headers.set("X-User-Id", String.valueOf(user.id()));
            }
            if (user.username() != null) {
                headers.set("X-User-Name", user.username());
            }
            if (user.email() != null) {
                headers.set("X-User-Email", user.email());
            }
            if (user.role() != null) {
                headers.set("X-User-Role", user.role());
            }
        }
        return gatewayProxyService.forward(
                serviceBaseUrl,
                request.getRequestURI(),
                request.getQueryString(),
                method,
                headers,
                body
        );
    }

    private HttpHeaders extractHeaders(HttpServletRequest request) {
        HttpHeaders headers = new HttpHeaders();
        request.getHeaderNames().asIterator().forEachRemaining(name -> {
            var values = request.getHeaders(name);
            java.util.List<String> collected = new java.util.ArrayList<>();
            while (values.hasMoreElements()) {
                collected.add(values.nextElement());
            }
            headers.put(name, collected);
        });
        return headers;
    }

    private ResponseEntity<byte[]> proxyProductsWrite(HttpServletRequest request, byte[] body) {
        HttpHeaders headers = extractHeaders(request);
        AuthenticatedUser user = authValidationService.requireUser(headers);
        if (user.role() == null || !"ADMIN".equalsIgnoreCase(user.role())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin role is required for product management");
        }
        if (user.id() != null) {
            headers.set("X-User-Id", String.valueOf(user.id()));
        }
        if (user.username() != null) {
            headers.set("X-User-Name", user.username());
        }
        if (user.email() != null) {
            headers.set("X-User-Email", user.email());
        }
        if (user.role() != null) {
            headers.set("X-User-Role", user.role());
        }
        return gatewayProxyService.forward(
                services.product(),
                request.getRequestURI(),
                request.getQueryString(),
                HttpMethod.valueOf(request.getMethod()),
                headers,
                body
        );
    }
}
