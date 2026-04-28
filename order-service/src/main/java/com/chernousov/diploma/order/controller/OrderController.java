package com.chernousov.diploma.order.controller;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CreateOrderRequest;
import com.chernousov.diploma.order.dto.OrderResponse;
import com.chernousov.diploma.order.dto.UpdateOrderStatusRequest;
import com.chernousov.diploma.order.exception.InvalidUserHeaderException;
import com.chernousov.diploma.order.service.OrderService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
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
@RequestMapping("/api/orders")
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse createOrder(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @Valid @RequestBody CreateOrderRequest request
    ) {
        return orderService.createOrder(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), request);
    }

    @GetMapping
    public List<OrderResponse> myOrders(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader
    ) {
        return orderService.myOrders(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader));
    }

    @GetMapping("/{orderId}")
    public OrderResponse getOrder(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @PathVariable(name = "orderId") Long orderId
    ) {
        return orderService.getOrder(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), orderId);
    }

    @PostMapping("/{orderId}/status")
    public OrderResponse updateStatus(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @PathVariable(name = "orderId") Long orderId,
            @Valid @RequestBody UpdateOrderStatusRequest request
    ) {
        return orderService.updateStatus(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), orderId, request.status());
    }

    private AuthenticatedUserHeader parseUserHeader(String userIdHeader, String usernameHeader, String userRoleHeader) {
        if (usernameHeader == null || usernameHeader.isBlank()) {
            throw new InvalidUserHeaderException("X-User-Name header is required");
        }

        try {
            String normalizedRole = (userRoleHeader == null || userRoleHeader.isBlank()) ? "USER" : userRoleHeader.trim().toUpperCase();
            return new AuthenticatedUserHeader(Long.parseLong(userIdHeader), usernameHeader, normalizedRole);
        } catch (NumberFormatException exception) {
            throw new InvalidUserHeaderException("X-User-Id header must be numeric");
        }
    }
}
