package com.chernousov.diploma.order.service.event;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderItem;
import com.chernousov.diploma.order.domain.OrderStatus;
import com.chernousov.diploma.order.service.event.model.OrderCreatedEvent;
import com.chernousov.diploma.order.service.event.model.OrderItemEvent;
import com.chernousov.diploma.order.service.event.model.OrderStatusChangedEvent;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.List;

@Component
@RequiredArgsConstructor
@ConditionalOnProperty(prefix = "app.kafka", name = "enabled", havingValue = "true", matchIfMissing = true)
public class KafkaOrderEventPublisher implements OrderEventPublisher {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Value("${app.kafka.topics.order-created:order.created.v1}")
    private String orderCreatedTopic;

    @Value("${app.kafka.topics.order-status-changed:order.status.changed.v1}")
    private String orderStatusChangedTopic;

    @Override
    public void publishOrderCreated(CustomerOrder order) {
        OrderCreatedEvent event = new OrderCreatedEvent(
                order.getId(),
                order.getUserId(),
                order.getUsername(),
                order.getStatus(),
                order.getTotalAmount(),
                order.getCurrency(),
                order.getNote(),
                Instant.now(),
                toItems(order.getItems())
        );

        kafkaTemplate.send(orderCreatedTopic, String.valueOf(order.getId()), event);
    }

    @Override
    public void publishOrderStatusChanged(CustomerOrder order, OrderStatus previousStatus) {
        OrderStatusChangedEvent event = new OrderStatusChangedEvent(
                order.getId(),
                order.getUserId(),
                order.getUsername(),
                previousStatus,
                order.getStatus(),
                Instant.now()
        );

        kafkaTemplate.send(orderStatusChangedTopic, String.valueOf(order.getId()), event);
    }

    private List<OrderItemEvent> toItems(List<OrderItem> items) {
        return items.stream()
                .map(item -> new OrderItemEvent(
                        item.getProductId(),
                        item.getProductName(),
                        item.getQuantity(),
                        item.getUnitPrice(),
                        item.getLineTotal()
                ))
                .toList();
    }
}
