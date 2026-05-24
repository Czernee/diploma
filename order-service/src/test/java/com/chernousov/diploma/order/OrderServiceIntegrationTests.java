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
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(101L, "alice", "USER");

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
        AuthenticatedUserHeader alice = new AuthenticatedUserHeader(201L, "alice", "USER");
        AuthenticatedUserHeader bob = new AuthenticatedUserHeader(202L, "bob", "USER");

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
        AuthenticatedUserHeader owner = new AuthenticatedUserHeader(301L, "owner", "USER");
        AuthenticatedUserHeader stranger = new AuthenticatedUserHeader(302L, "stranger", "USER");

        var created = orderService.createOrder(owner, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(3L, "RAM", 2, new BigDecimal("50.00"))),
                null,
                "RUB"
        ));

        assertThatThrownBy(() -> orderService.getOrder(stranger, created.id()))
                .isInstanceOf(OrderNotFoundException.class);
    }

    @Test
    void userCannotSetOperationalStatus() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(401L, "alice", "USER");
        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(4L, "SSD", 1, new BigDecimal("80.00"))),
                null,
                "RUB"
        ));

        assertThatThrownBy(() -> orderService.updateStatus(user, created.id(), OrderStatus.CONFIRMED))
                .isInstanceOf(InvalidOrderStatusTransitionException.class);
    }

    @Test
    void userCanCancelOwnOrderBeforeShipping() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(402L, "alice", "USER");
        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(5L, "Case", 1, new BigDecimal("70.00"))),
                null,
                "RUB"
        ));

        var cancelled = orderService.updateStatus(user, created.id(), OrderStatus.CANCELLED);
        assertThat(cancelled.status()).isEqualTo(OrderStatus.CANCELLED);
    }

    @Test
    void adminCanUpdateStatusForAnotherUsersOrder() {
        AuthenticatedUserHeader customer = new AuthenticatedUserHeader(501L, "customer", "USER");
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(999L, "admin", "ADMIN");

        var created = orderService.createOrder(customer, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(6L, "GPU", 1, new BigDecimal("100.00"))),
                null,
                "RUB"
        ));

        var confirmed = orderService.updateStatus(admin, created.id(), OrderStatus.CONFIRMED);
        assertThat(confirmed.status()).isEqualTo(OrderStatus.CONFIRMED);
    }

    @Test
    void adminCanViewAllOrders() {
        AuthenticatedUserHeader alice = new AuthenticatedUserHeader(601L, "alice", "USER");
        AuthenticatedUserHeader bob = new AuthenticatedUserHeader(602L, "bob", "USER");
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(999L, "admin", "ADMIN");

        orderService.createOrder(alice, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(7L, "CPU", 1, new BigDecimal("100.00"))),
                null,
                "RUB"
        ));
        orderService.createOrder(bob, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(8L, "GPU", 1, new BigDecimal("200.00"))),
                null,
                "RUB"
        ));

        var adminOrders = orderService.myOrders(admin);
        assertThat(adminOrders).extracting("userId").contains(601L, 602L);
    }

    @Test
    void adminCanGetAnotherUsersOrder() {
        AuthenticatedUserHeader owner = new AuthenticatedUserHeader(701L, "owner", "USER");
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(999L, "admin", "ADMIN");

        var created = orderService.createOrder(owner, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(9L, "RAM", 1, new BigDecimal("90.00"))),
                null,
                "RUB"
        ));

        var loaded = orderService.getOrder(admin, created.id());
        assertThat(loaded.id()).isEqualTo(created.id());
        assertThat(loaded.userId()).isEqualTo(701L);
    }

    @Test
    void userCannotCancelAfterOrderWasShipped() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(801L, "user", "USER");
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(999L, "admin", "ADMIN");

        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(10L, "GPU", 1, new BigDecimal("100.00"))),
                null,
                "RUB"
        ));
        orderService.updateStatus(admin, created.id(), OrderStatus.CONFIRMED);
        orderService.updateStatus(admin, created.id(), OrderStatus.PROCESSING);
        orderService.updateStatus(admin, created.id(), OrderStatus.SHIPPED);

        assertThatThrownBy(() -> orderService.updateStatus(user, created.id(), OrderStatus.CANCELLED))
                .isInstanceOf(InvalidOrderStatusTransitionException.class)
                .hasMessageContaining("can no longer be cancelled");
    }

    @Test
    void orderCannotBeChangedAfterDeliveredTerminalState() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(802L, "user", "USER");
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(999L, "admin", "ADMIN");

        var created = orderService.createOrder(user, new CreateOrderRequest(
                List.of(new CreateOrderItemRequest(11L, "CPU", 1, new BigDecimal("100.00"))),
                null,
                "RUB"
        ));
        orderService.updateStatus(admin, created.id(), OrderStatus.CONFIRMED);
        orderService.updateStatus(admin, created.id(), OrderStatus.PROCESSING);
        orderService.updateStatus(admin, created.id(), OrderStatus.SHIPPED);
        orderService.updateStatus(admin, created.id(), OrderStatus.DELIVERED);

        assertThatThrownBy(() -> orderService.updateStatus(admin, created.id(), OrderStatus.CANCELLED))
                .isInstanceOf(InvalidOrderStatusTransitionException.class)
                .hasMessageContaining("terminal state");
    }
}
