package com.chernousov.diploma.gateway.service;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Set;

@Service
public class GatewayProxyService {

    private static final Set<String> HOP_BY_HOP_HEADERS = Set.of(
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailer",
            "transfer-encoding",
            "upgrade",
            "host",
            "content-length"
    );

    private final RestClient restClient;

    public GatewayProxyService(RestClient.Builder restClientBuilder) {
        this.restClient = restClientBuilder.build();
    }

    public ResponseEntity<byte[]> forward(
            String serviceBaseUrl,
            String forwardedPath,
            String queryString,
            HttpMethod method,
            HttpHeaders headers,
            byte[] body
    ) {
        URI targetUri = UriComponentsBuilder
                .fromUriString(serviceBaseUrl)
                .path(normalizePath(forwardedPath))
                .query(queryString)
                .build(true)
                .toUri();

        return restClient.method(method)
                .uri(targetUri)
                .headers(targetHeaders -> copyRequestHeaders(headers, targetHeaders))
                .body(body == null ? new byte[0] : body)
                .exchange((request, response) -> {
                    HttpHeaders responseHeaders = new HttpHeaders();
                    copyResponseHeaders(response.getHeaders(), responseHeaders);
                    byte[] responseBody = readBody(response);
                    return ResponseEntity.status(response.getStatusCode())
                            .headers(responseHeaders)
                            .body(responseBody);
                });
    }

    private void copyRequestHeaders(HttpHeaders source, HttpHeaders target) {
        source.forEach((name, values) -> {
            if (!isHopByHop(name)) {
                target.put(name, new ArrayList<>(values));
            }
        });
    }

    private void copyResponseHeaders(HttpHeaders source, HttpHeaders target) {
        source.forEach((name, values) -> {
            if (!isHopByHop(name)) {
                target.put(name, new ArrayList<>(values));
            }
        });
    }

    private boolean isHopByHop(String headerName) {
        return HOP_BY_HOP_HEADERS.contains(headerName.toLowerCase());
    }

    private byte[] readBody(org.springframework.http.client.ClientHttpResponse response) throws IOException {
        if (response.getBody() == null) {
            return new byte[0];
        }
        return StreamUtils.copyToByteArray(response.getBody());
    }

    private String normalizePath(String path) {
        if (path == null || path.isBlank()) {
            return "/";
        }
        return path.startsWith("/") ? path : "/" + path;
    }
}
