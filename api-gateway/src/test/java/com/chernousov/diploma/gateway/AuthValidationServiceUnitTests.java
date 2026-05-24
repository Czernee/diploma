package com.chernousov.diploma.gateway;

import com.chernousov.diploma.gateway.config.GatewayServicesProperties;
import com.chernousov.diploma.gateway.service.AuthValidationService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

class AuthValidationServiceUnitTests {

    private MockRestServiceServer mockServer;
    private AuthValidationService authValidationService;

    @BeforeEach
    void setUp() {
        RestClient.Builder restClientBuilder = RestClient.builder();
        mockServer = MockRestServiceServer.bindTo(restClientBuilder).build();
        authValidationService = new AuthValidationService(
                new GatewayServicesProperties("http://auth-service", "http://product", "http://order", "http://ai"),
                restClientBuilder
        );
    }

    @Test
    void requireUserReturnsAuthenticatedUserForValidToken() {
        mockServer.expect(requestTo("http://auth-service/api/auth/me"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(
                        """
                        {"id":42,"username":"alice","email":"alice@example.com","role":"USER"}
                        """,
                        MediaType.APPLICATION_JSON
                ));

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("test-token");

        var user = authValidationService.requireUser(headers);

        assertThat(user.id()).isEqualTo(42L);
        assertThat(user.username()).isEqualTo("alice");
        assertThat(user.role()).isEqualTo("USER");
        mockServer.verify();
    }

    @Test
    void requireUserReturnsUnauthorizedForAuthService4xx() {
        mockServer.expect(requestTo("http://auth-service/api/auth/me"))
                .andRespond(withStatus(HttpStatus.UNAUTHORIZED));

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("expired-token");

        assertThatThrownBy(() -> authValidationService.requireUser(headers))
                .isInstanceOf(ResponseStatusException.class)
                .satisfies(error -> assertThat(((ResponseStatusException) error).getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED));
    }

    @Test
    void requireUserReturnsBadGatewayForAuthService5xx() {
        mockServer.expect(requestTo("http://auth-service/api/auth/me"))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR));

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth("token");

        assertThatThrownBy(() -> authValidationService.requireUser(headers))
                .isInstanceOf(ResponseStatusException.class)
                .satisfies(error -> assertThat(((ResponseStatusException) error).getStatusCode()).isEqualTo(HttpStatus.BAD_GATEWAY));
    }
}

