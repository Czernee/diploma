package com.chernousov.diploma.order.service.event;

import com.chernousov.diploma.order.domain.OrderStatusHistory;
import com.chernousov.diploma.order.repository.OrderStatusHistoryRepository;
import com.chernousov.diploma.order.service.event.model.OrderCreatedEvent;
import com.chernousov.diploma.order.service.event.model.OrderStatusChangedEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@ConditionalOnProperty(prefix = "app.kafka", name = "enabled", havingValue = "true", matchIfMissing = true)
public class OrderEventAuditConsumer {

    private final OrderStatusHistoryRepository historyRepository;
    private final ObjectMapper objectMapper = new ObjectMapper().findAndRegisterModules();

    @KafkaListener(
            topics = "${app.kafka.topics.order-created:order.created.v1}",
            groupId = "${app.kafka.consumer-groups.audit:order-service-audit}"
    )
    @Transactional
    public void onOrderCreated(String payload) {
        try {
            OrderCreatedEvent event = objectMapper.readValue(payload, OrderCreatedEvent.class);
            historyRepository.save(OrderStatusHistory.builder()
                    .orderId(event.orderId())
                    .userId(event.userId())
                    .username(event.username())
                    .previousStatus(null)
                    .newStatus(event.status().name())
                    .eventType("ORDER_CREATED")
                    .changedAt(event.occurredAt() == null ? Instant.now() : event.occurredAt())
                    .build());
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to consume order created event", exception);
        }
    }

    @KafkaListener(
            topics = "${app.kafka.topics.order-status-changed:order.status.changed.v1}",
            groupId = "${app.kafka.consumer-groups.audit:order-service-audit}"
    )
    @Transactional
    public void onOrderStatusChanged(String payload) {
        try {
            OrderStatusChangedEvent event = objectMapper.readValue(payload, OrderStatusChangedEvent.class);
            historyRepository.save(OrderStatusHistory.builder()
                    .orderId(event.orderId())
                    .userId(event.userId())
                    .username(event.username())
                    .previousStatus(event.previousStatus().name())
                    .newStatus(event.newStatus().name())
                    .eventType("ORDER_STATUS_CHANGED")
                    .changedAt(event.occurredAt() == null ? Instant.now() : event.occurredAt())
                    .build());
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to consume order status changed event", exception);
        }
    }
}
