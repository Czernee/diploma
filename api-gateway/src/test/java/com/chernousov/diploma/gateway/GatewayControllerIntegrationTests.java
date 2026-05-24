package com.chernousov.diploma.gateway;

import com.chernousov.diploma.gateway.service.AuthValidationService;
import com.chernousov.diploma.gateway.service.AuthenticatedUser;
import com.chernousov.diploma.gateway.service.GatewayProxyService;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.web.server.ResponseStatusException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class GatewayControllerIntegrationTests {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private GatewayProxyService gatewayProxyService;

    @MockitoBean
    private AuthValidationService authValidationService;

    @Test
    void statusEndpointReturnsOk() throws Exception {
        mockMvc.perform(get("/api/status"))
                .andExpect(status().isOk())
                .andExpect(content().string("api-gateway is running"));
    }

    @Test
    void productWriteIsForbiddenForNonAdmin() throws Exception {
        when(authValidationService.requireUser(any(HttpHeaders.class)))
                .thenReturn(new AuthenticatedUser(10L, "alice", "alice@example.com", "USER"));

        mockMvc.perform(post("/api/products")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isForbidden());

        verify(gatewayProxyService, never()).forward(any(), any(), any(), any(), any(), any());
    }

    @Test
    void productWriteForAdminIsForwarded() throws Exception {
        when(authValidationService.requireUser(any(HttpHeaders.class)))
                .thenReturn(new AuthenticatedUser(99L, "admin", "admin@example.com", "ADMIN"));
        when(gatewayProxyService.forward(any(), any(), any(), any(), any(), any()))
                .thenReturn(ResponseEntity.ok("{\"result\":\"ok\"}".getBytes()));

        mockMvc.perform(post("/api/products")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer admin-token")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"item\"}"))
                .andExpect(status().isOk())
                .andExpect(content().json("{\"result\":\"ok\"}"));

        verify(gatewayProxyService).forward(eq("http://localhost:8082"), eq("/api/products"), isNull(),
                eq(HttpMethod.POST), any(HttpHeaders.class), any(byte[].class));
    }

    @Test
    void ordersRequestInjectsAuthenticatedHeadersBeforeForwarding() throws Exception {
        when(authValidationService.requireUser(any(HttpHeaders.class)))
                .thenReturn(new AuthenticatedUser(55L, "alice", "alice@example.com", "USER"));
        when(gatewayProxyService.forward(any(), any(), any(), any(), any(), any()))
                .thenReturn(ResponseEntity.ok("ok".getBytes()));

        mockMvc.perform(get("/api/orders?page=1")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer user-token"))
                .andExpect(status().isOk())
                .andExpect(content().string("ok"));

        ArgumentCaptor<HttpHeaders> headersCaptor = ArgumentCaptor.forClass(HttpHeaders.class);
        verify(gatewayProxyService).forward(eq("http://localhost:8083"), eq("/api/orders"), eq("page=1"),
                eq(HttpMethod.GET), headersCaptor.capture(), any());

        HttpHeaders forwardedHeaders = headersCaptor.getValue();
        assertThat(forwardedHeaders.getFirst("X-User-Id")).isEqualTo("55");
        assertThat(forwardedHeaders.getFirst("X-User-Name")).isEqualTo("alice");
        assertThat(forwardedHeaders.getFirst("X-User-Email")).isEqualTo("alice@example.com");
        assertThat(forwardedHeaders.getFirst("X-User-Role")).isEqualTo("USER");
    }

    @Test
    void productsGetIsForwardedWithoutAuthenticationValidation() throws Exception {
        when(gatewayProxyService.forward(any(), any(), any(), any(), any(), any()))
                .thenReturn(ResponseEntity.ok("products".getBytes()));

        mockMvc.perform(get("/api/products?query=cpu"))
                .andExpect(status().isOk())
                .andExpect(content().string("products"));

        verify(authValidationService, never()).requireUser(any(HttpHeaders.class));
        verify(gatewayProxyService).forward(eq("http://localhost:8082"), eq("/api/products"), eq("query=cpu"),
                eq(HttpMethod.GET), any(HttpHeaders.class), any());
    }

    @Test
    void configuratorRequestWithoutAuthReturnsUnauthorized() throws Exception {
        when(authValidationService.requireUser(any(HttpHeaders.class)))
                .thenThrow(new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing Authorization header"));

        mockMvc.perform(get("/api/configurator/recommend"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void configuratorRequestReturnsBadGatewayWhenAuthServiceUnavailable() throws Exception {
        when(authValidationService.requireUser(any(HttpHeaders.class)))
                .thenThrow(new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Auth service is unavailable"));

        mockMvc.perform(get("/api/configurator/recommend")
                        .header(HttpHeaders.AUTHORIZATION, "Bearer token"))
                .andExpect(status().isBadGateway());
    }
}
