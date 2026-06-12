package com.chernousov.diploma.order.service;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderItem;
import com.chernousov.diploma.order.domain.OrderStatus;
import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CreateOrderItemRequest;
import com.chernousov.diploma.order.dto.CreateOrderRequest;
import com.chernousov.diploma.order.dto.OrderItemResponse;
import com.chernousov.diploma.order.dto.OrderResponse;
import com.chernousov.diploma.order.dto.OrderStatusHistoryResponse;
import com.chernousov.diploma.order.exception.InvalidOrderStatusTransitionException;
import com.chernousov.diploma.order.exception.OrderNotFoundException;
import com.chernousov.diploma.order.repository.CustomerOrderRepository;
import com.chernousov.diploma.order.repository.OrderStatusHistoryRepository;
import com.chernousov.diploma.order.service.event.OrderEventPublisher;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class OrderService {

    private static final Set<OrderStatus> TERMINAL_STATUSES = EnumSet.of(OrderStatus.DELIVERED, OrderStatus.CANCELLED);
    private static final Set<OrderStatus> USER_CANCELLABLE_STATUSES = EnumSet.of(
            OrderStatus.CREATED,
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING
    );
    private static final Map<OrderStatus, Set<OrderStatus>> ADMIN_ALLOWED_TRANSITIONS = Map.of(
            OrderStatus.CREATED, EnumSet.of(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
            OrderStatus.CONFIRMED, EnumSet.of(OrderStatus.PROCESSING, OrderStatus.CANCELLED),
            OrderStatus.PROCESSING, EnumSet.of(OrderStatus.SHIPPED, OrderStatus.CANCELLED),
            OrderStatus.SHIPPED, EnumSet.of(OrderStatus.DELIVERED),
            OrderStatus.DELIVERED, EnumSet.noneOf(OrderStatus.class),
            OrderStatus.CANCELLED, EnumSet.noneOf(OrderStatus.class)
    );

    private final CustomerOrderRepository orderRepository;
    private final OrderStatusHistoryRepository orderStatusHistoryRepository;
    private final OrderEventPublisher orderEventPublisher;

    @Transactional
    public OrderResponse createOrder(AuthenticatedUserHeader user, CreateOrderRequest request) {
        BigDecimal total = request.items().stream()
                .map(item -> item.unitPrice().multiply(BigDecimal.valueOf(item.quantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        CustomerOrder order = CustomerOrder.builder()
                .userId(user.userId())
                .username(user.username())
                .status(OrderStatus.CREATED)
                .totalAmount(total)
                .currency(request.currency().trim().toUpperCase())
                .note(request.note())
                .build();

        for (CreateOrderItemRequest item : request.items()) {
            BigDecimal lineTotal = item.unitPrice().multiply(BigDecimal.valueOf(item.quantity()));
            order.addItem(OrderItem.builder()
                    .productId(item.productId())
                    .productName(item.productName())
                    .quantity(item.quantity())
                    .unitPrice(item.unitPrice())
                    .lineTotal(lineTotal)
                    .build());
        }

        CustomerOrder savedOrder = orderRepository.save(order);
        orderEventPublisher.publishOrderCreated(savedOrder);
        return toResponse(savedOrder);
    }

    public List<OrderResponse> myOrders(AuthenticatedUserHeader user) {
        List<CustomerOrder> orders = user.isAdmin()
                ? orderRepository.findAllByOrderByCreatedAtDesc()
                : orderRepository.findByUserIdOrderByCreatedAtDesc(user.userId());
        return orders
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public OrderResponse getOrder(AuthenticatedUserHeader user, Long orderId) {
        CustomerOrder order;
        if (user.isAdmin()) {
            order = orderRepository.findById(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
        } else {
            order = orderRepository.findByIdAndUserId(orderId, user.userId())
                    .orElseThrow(() -> new OrderNotFoundException(orderId));
        }
        return toResponse(order);
    }

    public List<OrderStatusHistoryResponse> orderStatusHistory(AuthenticatedUserHeader user, Long orderId) {
        getOrder(user, orderId);
        return orderStatusHistoryRepository.findByOrderIdOrderByChangedAtAsc(orderId)
                .stream()
                .map(history -> new OrderStatusHistoryResponse(
                        history.getId(),
                        history.getOrderId(),
                        history.getPreviousStatus(),
                        history.getNewStatus(),
                        history.getEventType(),
                        history.getChangedAt()
                ))
                .toList();
    }

    @Transactional
    public OrderResponse updateStatus(AuthenticatedUserHeader user, Long orderId, OrderStatus newStatus) {
        CustomerOrder order = findOrderForStatusUpdate(user, orderId);

        OrderStatus previousStatus = order.getStatus();
        validateStatusUpdatePermission(user, previousStatus, newStatus);
        if (previousStatus != newStatus) {
            order.setStatus(newStatus);
            orderEventPublisher.publishOrderStatusChanged(order, previousStatus);
        }
        return toResponse(order);
    }

    private CustomerOrder findOrderForStatusUpdate(AuthenticatedUserHeader user, Long orderId) {
        if (user.isAdmin()) {
            return orderRepository.findById(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
        }
        return orderRepository.findByIdAndUserId(orderId, user.userId())
                .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    private void validateStatusUpdatePermission(AuthenticatedUserHeader user, OrderStatus previousStatus, OrderStatus newStatus) {
        if (previousStatus == newStatus) {
            return;
        }
        if (TERMINAL_STATUSES.contains(previousStatus)) {
            throw new InvalidOrderStatusTransitionException(
                    "Order in terminal state " + previousStatus + " cannot be changed to " + newStatus
            );
        }
        if (user.isAdmin()) {
            validateAdminTransition(previousStatus, newStatus);
            return;
        }
        validateUserTransition(previousStatus, newStatus);
    }

    private void validateAdminTransition(OrderStatus previousStatus, OrderStatus newStatus) {
        Set<OrderStatus> allowed = ADMIN_ALLOWED_TRANSITIONS.getOrDefault(previousStatus, Set.of());
        if (allowed.contains(newStatus)) {
            return;
        }
        throw new InvalidOrderStatusTransitionException(
                "Admin cannot change status from " + previousStatus + " to " + newStatus
        );
    }

    private void validateUserTransition(OrderStatus previousStatus, OrderStatus newStatus) {
        if (newStatus != OrderStatus.CANCELLED) {
            throw new InvalidOrderStatusTransitionException(
                    "User can only change order status to CANCELLED"
            );
        }
        if (USER_CANCELLABLE_STATUSES.contains(previousStatus)) {
            return;
        }
        throw new InvalidOrderStatusTransitionException(
                "Order status " + previousStatus + " can no longer be cancelled by user"
        );
    }

    private OrderResponse toResponse(CustomerOrder order) {
        return new OrderResponse(
                order.getId(),
                order.getUserId(),
                order.getUsername(),
                order.getStatus(),
                order.getTotalAmount(),
                order.getCurrency(),
                order.getNote(),
                order.getCreatedAt(),
                order.getItems().stream()
                        .map(item -> new OrderItemResponse(
                                item.getProductId(),
                                item.getProductName(),
                                item.getQuantity(),
                                item.getUnitPrice(),
                                item.getLineTotal()
                        ))
                        .toList()
        );
    }
}
