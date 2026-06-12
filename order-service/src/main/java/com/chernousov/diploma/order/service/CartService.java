package com.chernousov.diploma.order.service;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CartItemRequest;
import com.chernousov.diploma.order.dto.CartItemResponse;
import com.chernousov.diploma.order.dto.CartResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

@Service
@RequiredArgsConstructor
public class CartService {

    private static final Duration CART_TTL = Duration.ofDays(7);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper().findAndRegisterModules();

    public CartResponse getCart(AuthenticatedUserHeader user) {
        return toResponse(readCart(user.userId()));
    }

    public CartResponse addItem(AuthenticatedUserHeader user, CartItemRequest request) {
        RedisCart cart = readCart(user.userId());
        List<RedisCartItem> items = new ArrayList<>(cart.items());
        RedisCartItem incoming = new RedisCartItem(
                request.productId(),
                request.productName().trim(),
                request.quantity(),
                request.unitPrice(),
                request.currency().trim().toUpperCase(Locale.ROOT)
        );

        boolean updated = false;
        for (int index = 0; index < items.size(); index++) {
            RedisCartItem item = items.get(index);
            if (item.productId().equals(incoming.productId())) {
                items.set(index, new RedisCartItem(
                        item.productId(),
                        incoming.productName(),
                        item.quantity() + incoming.quantity(),
                        incoming.unitPrice(),
                        incoming.currency()
                ));
                updated = true;
                break;
            }
        }
        if (!updated) {
            items.add(incoming);
        }

        RedisCart nextCart = new RedisCart(items);
        writeCart(user.userId(), nextCart);
        return toResponse(nextCart);
    }

    public CartResponse setQuantity(AuthenticatedUserHeader user, Long productId, Integer quantity) {
        RedisCart cart = readCart(user.userId());
        List<RedisCartItem> items = cart.items()
                .stream()
                .filter(item -> !item.productId().equals(productId))
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);

        if (quantity > 0) {
            cart.items().stream()
                    .filter(item -> item.productId().equals(productId))
                    .findFirst()
                    .ifPresent(item -> items.add(new RedisCartItem(
                            item.productId(),
                            item.productName(),
                            quantity,
                            item.unitPrice(),
                            item.currency()
                    )));
        }

        RedisCart nextCart = new RedisCart(items);
        writeCart(user.userId(), nextCart);
        return toResponse(nextCart);
    }

    public CartResponse removeItem(AuthenticatedUserHeader user, Long productId) {
        return setQuantity(user, productId, 0);
    }

    public CartResponse clear(AuthenticatedUserHeader user) {
        redisTemplate.delete(cartKey(user.userId()));
        return toResponse(new RedisCart(List.of()));
    }

    private RedisCart readCart(Long userId) {
        String raw = redisTemplate.opsForValue().get(cartKey(userId));
        if (raw == null || raw.isBlank()) {
            return new RedisCart(List.of());
        }
        try {
            RedisCart cart = objectMapper.readValue(raw, RedisCart.class);
            return cart.items() == null ? new RedisCart(List.of()) : cart;
        } catch (JsonProcessingException exception) {
            return new RedisCart(List.of());
        }
    }

    private void writeCart(Long userId, RedisCart cart) {
        try {
            redisTemplate.opsForValue().set(cartKey(userId), objectMapper.writeValueAsString(cart), CART_TTL);
        } catch (JsonProcessingException exception) {
            throw new IllegalStateException("Unable to serialize cart state", exception);
        }
    }

    private CartResponse toResponse(RedisCart cart) {
        List<CartItemResponse> items = cart.items()
                .stream()
                .map(item -> new CartItemResponse(
                        item.productId(),
                        item.productName(),
                        item.quantity(),
                        item.unitPrice(),
                        item.currency(),
                        item.unitPrice().multiply(BigDecimal.valueOf(item.quantity()))
                ))
                .toList();

        BigDecimal total = items.stream()
                .map(CartItemResponse::lineTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        String currency = items.isEmpty() ? "RUB" : items.getFirst().currency();
        return new CartResponse(items, total, currency);
    }

    private String cartKey(Long userId) {
        return "cart:user:" + userId;
    }

    private record RedisCart(List<RedisCartItem> items) {
    }

    private record RedisCartItem(
            Long productId,
            String productName,
            Integer quantity,
            BigDecimal unitPrice,
            String currency
    ) {
    }
}
