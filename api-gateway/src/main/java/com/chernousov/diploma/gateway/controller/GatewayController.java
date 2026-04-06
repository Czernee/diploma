package com.chernousov.diploma.gateway.controller;

import com.chernousov.diploma.gateway.config.GatewayServicesProperties;
import com.chernousov.diploma.gateway.service.GatewayProxyService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GatewayController {

    private final GatewayProxyService gatewayProxyService;
    private final GatewayServicesProperties services;

    public GatewayController(
            GatewayProxyService gatewayProxyService,
            GatewayServicesProperties services
    ) {
        this.gatewayProxyService = gatewayProxyService;
        this.services = services;
    }

    @RequestMapping("/api/status")
    public ResponseEntity<String> status() {
        return ResponseEntity.ok("api-gateway is running");
    }

    @RequestMapping({"/api/auth", "/api/auth/**"})
    public ResponseEntity<byte[]> auth(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, "/api/auth", services.auth());
    }

    @RequestMapping({"/api/products", "/api/products/**"})
    public ResponseEntity<byte[]> products(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, "/api/products", services.product());
    }

    @RequestMapping({"/api/orders", "/api/orders/**"})
    public ResponseEntity<byte[]> orders(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, "/api/orders", services.order());
    }

    @RequestMapping({"/api/configurator", "/api/configurator/**"})
    public ResponseEntity<byte[]> configurator(HttpServletRequest request, @RequestBody(required = false) byte[] body) {
        return proxy(request, body, "/api/configurator", services.ai());
    }

    private ResponseEntity<byte[]> proxy(
            HttpServletRequest request,
            byte[] body,
            String routePrefix,
            String serviceBaseUrl
    ) {
        String path = request.getRequestURI();
        String forwardedPath = path.length() <= routePrefix.length()
                ? routePrefix
                : path.substring(routePrefix.length());

        HttpMethod method = HttpMethod.valueOf(request.getMethod());
        HttpHeaders headers = extractHeaders(request);
        return gatewayProxyService.forward(
                serviceBaseUrl,
                forwardedPath,
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
}
