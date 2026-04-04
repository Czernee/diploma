package com.chernousov.diploma.order.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/orders")
public class OrderStubController {

    @PostMapping
    public ResponseEntity<Map<String, Object>> createOrder(@RequestBody Map<String, Object> payload) {
        return ResponseEntity.ok(Map.of(
                "orderId", UUID.randomUUID().toString(),
                "status", "CREATED",
                "payload", payload
        ));
    }

    @PostMapping("/{orderId}/status")
    public ResponseEntity<Map<String, String>> trackOrder(@PathVariable String orderId) {
        return ResponseEntity.ok(Map.of(
                "orderId", orderId,
                "status", "CREATED"
        ));
    }
}
