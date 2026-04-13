package com.chernousov.diploma.order.service.event;

import com.chernousov.diploma.order.domain.CustomerOrder;
import com.chernousov.diploma.order.domain.OrderStatus;

public interface OrderEventPublisher {

    void publishOrderCreated(CustomerOrder order);

    void publishOrderStatusChanged(CustomerOrder order, OrderStatus previousStatus);
}
