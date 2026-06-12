package com.chernousov.diploma.order;

import com.chernousov.diploma.order.domain.OrderStatusHistory;
import com.chernousov.diploma.order.repository.OrderStatusHistoryRepository;
import com.chernousov.diploma.order.service.event.OrderEventAuditConsumer;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

class OrderEventAuditConsumerUnitTests {

    @Test
    void orderCreatedEventIsPersistedAsStatusHistory() {
        OrderStatusHistoryRepository repository = mock(OrderStatusHistoryRepository.class);
        OrderEventAuditConsumer consumer = new OrderEventAuditConsumer(repository);

        consumer.onOrderCreated("""
                {
                  "orderId": 15,
                  "userId": 42,
                  "username": "alice",
                  "status": "CREATED",
                  "totalAmount": 1000,
                  "currency": "RUB",
                  "note": null,
                  "occurredAt": "2026-06-04T10:00:00Z",
                  "items": []
                }
                """);

        ArgumentCaptor<OrderStatusHistory> captor = ArgumentCaptor.forClass(OrderStatusHistory.class);
        verify(repository).save(captor.capture());
        assertThat(captor.getValue().getOrderId()).isEqualTo(15L);
        assertThat(captor.getValue().getNewStatus()).isEqualTo("CREATED");
        assertThat(captor.getValue().getEventType()).isEqualTo("ORDER_CREATED");
    }
}
