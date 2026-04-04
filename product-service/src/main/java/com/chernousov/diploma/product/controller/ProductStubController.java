package com.chernousov.diploma.product.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/products")
public class ProductStubController {

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> search(
            @RequestParam(name = "query", required = false) String query
    ) {
        return ResponseEntity.ok(List.of(
                Map.of("id", 1, "name", "CPU Placeholder", "query", query == null ? "" : query),
                Map.of("id", 2, "name", "GPU Placeholder", "query", query == null ? "" : query)
        ));
    }
}
