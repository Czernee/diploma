package com.chernousov.diploma.order.repository;

import com.chernousov.diploma.order.domain.CustomerOrder;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CustomerOrderRepository extends JpaRepository<CustomerOrder, Long> {

    List<CustomerOrder> findAllByOrderByCreatedAtDesc();

    List<CustomerOrder> findByUserIdOrderByCreatedAtDesc(Long userId);

    Optional<CustomerOrder> findByIdAndUserId(Long id, Long userId);
}
