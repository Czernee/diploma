package com.chernousov.diploma.order;

import com.chernousov.diploma.order.domain.OrderStatus;
import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CreateOrderItemRequest;
import com.chernousov.diploma.order.dto.CreateOrderRequest;
import com.chernousov.diploma.order.exception.InvalidOrderStatusTransitionException;
import com.chernousov.diploma.order.exception.OrderNotFoundException;
import com.chernousov.diploma.order.service.OrderService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.math.BigDecimal;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
class OrderServiceIntegrationTests {

    @Autowired
    private OrderService orderService;

    @Test
    void createAndFetchOwnOrderWorks() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(101L, "alice");

        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(
                        new CreateOrderItemRequest(1L, "CPU", 1, new BigDecimal("300.00")),
                        new CreateOrderItemRequest(2L, "GPU", 1, new BigDecimal("700.00"))
                ),
                "Need fast delivery",
                "RUB"
        ));

        assertThat(created.id()).isNotNull();
        assertThat(created.status()).isEqualTo(OrderStatus.CREATED);
        assertThat(created.totalAmount()).isEqualByComparingTo("1000.00");
        assertThat(created.items()).hasSize(2);

        var loaded = orderService.getOrder(user, created.id());
        assertThat(loaded.id()).isEqualTo(created.id());
        assertThat(loaded.username()).isEqualTo("alice");
    }

    @Test
    void myOrdersReturnsOnlyCurrentUserOrders() {
        AuthenticatedUserHeader alice = new AuthenticatedUserHeader(201L, "alice");
        AuthenticatedUserHeader bob = new AuthenticatedUserHeader(202L, "bob");

        orderService.createOrder(alice, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(1L, "CPU", 1, new BigDecimal("100.00"))),
                null,
                "RUB"
        ));
        orderService.createOrder(bob, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(2L, "GPU", 1, new BigDecimal("200.00"))),
                null,
                "RUB"
        ));

        var aliceOrders = orderService.myOrders(alice);
        assertThat(aliceOrders).hasSize(1);
        assertThat(aliceOrders.getFirst().userId()).isEqualTo(201L);
    }

    @Test
    void orderCannotBeAccessedByAnotherUser() {
        AuthenticatedUserHeader owner = new AuthenticatedUserHeader(301L, "owner");
        AuthenticatedUserHeader stranger = new AuthenticatedUserHeader(302L, "stranger");

        var created = orderService.createOrder(owner, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(3L, "RAM", 2, new BigDecimal("50.00"))),
                null,
                "RUB"
        ));

        assertThatThrownBy(() -> orderService.getOrder(stranger, created.id()))
                .isInstanceOf(OrderNotFoundException.class);
    }

    @Test
    void terminalStatusCannotBeChanged() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(401L, "alice");
        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(4L, "SSD", 1, new BigDecimal("80.00"))),
                null,
                "RUB"
        ));

        orderService.updateStatus(user, created.id(), OrderStatus.DELIVERED);

        assertThatThrownBy(() -> orderService.updateStatus(user, created.id(), OrderStatus.CANCELLED))
                .isInstanceOf(InvalidOrderStatusTransitionException.class);
    }
}
