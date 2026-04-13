package com.chernousov.diploma.order.service;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderItem;
import com.chernousov.diploma.order.domain.OrderStatus;
import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.CreateOrderItemRequest;
import com.chernousov.diploma.order.dto.CreateOrderRequest;
import com.chernousov.diploma.order.dto.OrderItemResponse;
import com.chernousov.diploma.order.dto.OrderResponse;
import com.chernousov.diploma.order.exception.InvalidOrderStatusTransitionException;
import com.chernousov.diploma.order.exception.OrderNotFoundException;
import com.chernousov.diploma.order.repository.CustomerOrderRepository;
import com.chernousov.diploma.order.service.event.OrderEventPublisher;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class OrderService {

    private final CustomerOrderRepository orderRepository;
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
        return orderRepository.findByUserIdOrderByCreatedAtDesc(user.userId())
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public OrderResponse getOrder(AuthenticatedUserHeader user, Long orderId) {
        CustomerOrder order = orderRepository.findByIdAndUserId(orderId, user.userId())
                .orElseThrow(() -> new OrderNotFoundException(orderId));
        return toResponse(order);
    }

    @Transactional
    public OrderResponse updateStatus(AuthenticatedUserHeader user, Long orderId, OrderStatus newStatus) {
        CustomerOrder order = orderRepository.findByIdAndUserId(orderId, user.userId())
                .orElseThrow(() -> new OrderNotFoundException(orderId));

        if (order.getStatus() == OrderStatus.DELIVERED || order.getStatus() == OrderStatus.CANCELLED) {
            if (order.getStatus() != newStatus) {
                throw new InvalidOrderStatusTransitionException(
                        "Order in terminal state " + order.getStatus() + " cannot be changed to " + newStatus
                );
            }
        }

        OrderStatus previousStatus = order.getStatus();
        if (previousStatus != newStatus) {
            order.setStatus(newStatus);
            orderEventPublisher.publishOrderStatusChanged(order, previousStatus);
        }
        return toResponse(order);
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
