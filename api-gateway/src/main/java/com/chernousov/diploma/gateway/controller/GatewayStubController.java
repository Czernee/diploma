package com.chernousov.diploma.gateway.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class GatewayStubController {

    @GetMapping("/status")
    public ResponseEntity<String> status() {
        return ResponseEntity.ok("api-gateway is running");
    }
}
