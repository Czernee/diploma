package com.chernousov.diploma.gateway.service;

import com.chernousov.diploma.gateway.config.GatewayServicesProperties;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.util.UriComponentsBuilder;

@Service
public class AuthValidationService {

    private final GatewayServicesProperties services;
    private final RestClient restClient;

    public AuthValidationService(
            GatewayServicesProperties services,
            RestClient.Builder restClientBuilder
    ) {
        this.services = services;
        this.restClient = restClientBuilder.build();
    }

    public AuthenticatedUser requireUser(HttpHeaders incomingHeaders) {
        String authorization = incomingHeaders.getFirst(HttpHeaders.AUTHORIZATION);
        if (authorization == null || authorization.isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing Authorization header");
        }

        String meUrl = UriComponentsBuilder.fromUriString(services.auth())
                .path("/api/auth/me")
                .toUriString();
        try {
            AuthenticatedUser response = restClient.get()
                    .uri(meUrl)
                    .header(HttpHeaders.AUTHORIZATION, authorization)
                    .retrieve()
                    .body(AuthenticatedUser.class);
            if (response == null || response.username() == null || response.username().isBlank()) {
                throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid authentication response");
            }
            return response;
        } catch (RestClientResponseException exception) {
            if (exception.getStatusCode().is4xxClientError()) {
                throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or expired token");
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Auth service is unavailable");
        } catch (ResponseStatusException exception) {
            throw exception;
        } catch (Exception exception) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Auth service is unavailable");
        }
    }
}
