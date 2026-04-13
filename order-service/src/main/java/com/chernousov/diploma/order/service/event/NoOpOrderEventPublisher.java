package com.chernousov.diploma.order.service.event;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderStatus;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(prefix = "app.kafka", name = "enabled", havingValue = "false")
public class NoOpOrderEventPublisher implements OrderEventPublisher {

    @Override
    public void publishOrderCreated(CustomerOrder order) {
        // no-op
    }

    @Override
    public void publishOrderStatusChanged(CustomerOrder order, OrderStatus previousStatus) {
        // no-op
    }
}
