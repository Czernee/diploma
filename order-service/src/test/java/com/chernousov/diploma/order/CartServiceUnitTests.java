package com.chernousov.diploma.order;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CartItemRequest;
import com.chernousov.diploma.order.service.CartService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.math.BigDecimal;
import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CartServiceUnitTests {

    @Mock
    private StringRedisTemplate redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    @Test
    void addItemStoresCartInRedisAndCanReadItBack() {
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
        when(valueOperations.get("cart:user:42")).thenReturn(null);
        CartService cartService = new CartService(redisTemplate);

        var user = new AuthenticatedUserHeader(42L, "alice", "USER");
        var response = cartService.addItem(user, new CartItemRequest(
                10L,
                "Test GPU",
                2,
                new BigDecimal("15000.00"),
                "rub"
        ));

        ArgumentCaptor<String> jsonCaptor = ArgumentCaptor.forClass(String.class);
        verify(valueOperations).set(eq("cart:user:42"), jsonCaptor.capture(), any(Duration.class));

        when(valueOperations.get("cart:user:42")).thenReturn(jsonCaptor.getValue());
        var loaded = cartService.getCart(user);

        assertThat(response.totalAmount()).isEqualByComparingTo("30000.00");
        assertThat(loaded.items()).hasSize(1);
        assertThat(loaded.items().getFirst().productId()).isEqualTo(10L);
        assertThat(loaded.items().getFirst().currency()).isEqualTo("RUB");
    }
}

