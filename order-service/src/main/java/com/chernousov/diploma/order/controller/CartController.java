package com.chernousov.diploma.order.controller;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CartItemRequest;
import com.chernousov.diploma.order.dto.CartResponse;
import com.chernousov.diploma.order.dto.UpdateCartItemQuantityRequest;
import com.chernousov.diploma.order.exception.InvalidUserHeaderException;
import com.chernousov.diploma.order.service.CartService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/orders/cart")
public class CartController {

    private final CartService cartService;

    @GetMapping
    public CartResponse getCart(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader
    ) {
        return cartService.getCart(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader));
    }

    @PostMapping("/items")
    public CartResponse addItem(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @Valid @RequestBody CartItemRequest request
    ) {
        return cartService.addItem(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), request);
    }

    @PutMapping("/items/{productId}")
    public CartResponse setQuantity(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @PathVariable(name = "productId") Long productId,
            @Valid @RequestBody UpdateCartItemQuantityRequest request
    ) {
        return cartService.setQuantity(
                parseUserHeader(userIdHeader, usernameHeader, userRoleHeader),
                productId,
                request.quantity()
        );
    }

    @DeleteMapping("/items/{productId}")
    public CartResponse removeItem(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader,
            @PathVariable(name = "productId") Long productId
    ) {
        return cartService.removeItem(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader), productId);
    }

    @DeleteMapping
    public CartResponse clear(
            @RequestHeader(name = "X-User-Id") String userIdHeader,
            @RequestHeader(name = "X-User-Name") String usernameHeader,
            @RequestHeader(name = "X-User-Role", required = false) String userRoleHeader
    ) {
        return cartService.clear(parseUserHeader(userIdHeader, usernameHeader, userRoleHeader));
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

