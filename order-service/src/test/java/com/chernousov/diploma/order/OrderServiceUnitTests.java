package com.chernousov.diploma.order;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderStatus;
import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.exception.InvalidOrderStatusTransitionException;
import com.chernousov.diploma.order.repository.CustomerOrderRepository;
import com.chernousov.diploma.order.repository.OrderStatusHistoryRepository;
import com.chernousov.diploma.order.service.OrderService;
import com.chernousov.diploma.order.service.event.OrderEventPublisher;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceUnitTests {

    @Mock
    private CustomerOrderRepository orderRepository;

    @Mock
    private OrderStatusHistoryRepository orderStatusHistoryRepository;

    @Mock
    private OrderEventPublisher orderEventPublisher;

    @InjectMocks
    private OrderService orderService;

    @Test
    void adminCanMoveOrderFromCreatedToConfirmed() {
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(1L, "admin", "ADMIN");
        CustomerOrder order = CustomerOrder.builder()
                .userId(10L)
                .username("alice")
                .status(OrderStatus.CREATED)
                .totalAmount(new BigDecimal("100.00"))
                .currency("RUB")
                .build();
        when(orderRepository.findById(15L)).thenReturn(Optional.of(order));

        var updated = orderService.updateStatus(admin, 15L, OrderStatus.CONFIRMED);

        assertThat(updated.status()).isEqualTo(OrderStatus.CONFIRMED);
        verify(orderEventPublisher).publishOrderStatusChanged(eq(order), eq(OrderStatus.CREATED));
    }

    @Test
    void regularUserCannotSetOperationalStatus() {
        AuthenticatedUserHeader user = new AuthenticatedUserHeader(10L, "alice", "USER");
        CustomerOrder order = CustomerOrder.builder()
                .userId(10L)
                .username("alice")
                .status(OrderStatus.CREATED)
                .totalAmount(new BigDecimal("100.00"))
                .currency("RUB")
                .build();
        when(orderRepository.findByIdAndUserId(15L, 10L)).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> orderService.updateStatus(user, 15L, OrderStatus.PROCESSING))
                .isInstanceOf(InvalidOrderStatusTransitionException.class)
                .hasMessageContaining("User can only change order status to CANCELLED");

        verify(orderEventPublisher, never()).publishOrderStatusChanged(org.mockito.ArgumentMatchers.any(), org.mockito.ArgumentMatchers.any());
    }

    @Test
    void adminOrdersUsesGlobalQueryInsteadOfUserScopedOne() {
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(1L, "admin", "ADMIN");
        CustomerOrder order = CustomerOrder.builder()
                .userId(10L)
                .username("alice")
                .status(OrderStatus.CREATED)
                .totalAmount(new BigDecimal("100.00"))
                .currency("RUB")
                .build();
        when(orderRepository.findAllByOrderByCreatedAtDesc()).thenReturn(List.of(order));

        var orders = orderService.myOrders(admin);

        assertThat(orders).hasSize(1);
        verify(orderRepository).findAllByOrderByCreatedAtDesc();
        verify(orderRepository, never()).findByUserIdOrderByCreatedAtDesc(org.mockito.ArgumentMatchers.anyLong());
    }

    @Test
    void adminCannotSkipIntermediateStatusTransitions() {
        AuthenticatedUserHeader admin = new AuthenticatedUserHeader(1L, "admin", "ADMIN");
        CustomerOrder order = CustomerOrder.builder()
                .userId(10L)
                .username("alice")
                .status(OrderStatus.CREATED)
                .totalAmount(new BigDecimal("100.00"))
                .currency("RUB")
                .build();
        when(orderRepository.findById(16L)).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> orderService.updateStatus(admin, 16L, OrderStatus.DELIVERED))
                .isInstanceOf(InvalidOrderStatusTransitionException.class)
                .hasMessageContaining("Admin cannot change status");

        verify(orderEventPublisher, never()).publishOrderStatusChanged(org.mockito.ArgumentMatchers.any(), org.mockito.ArgumentMatchers.any());
    }
}
