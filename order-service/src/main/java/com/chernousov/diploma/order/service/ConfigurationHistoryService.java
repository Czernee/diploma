package com.chernousov.diploma.order.service;

import com.chernousov.diploma.order.dto.AuthenticatedUserHeader;
import com.chernousov.diploma.order.dto.ConfigurationHistoryResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.node.MissingNode;

import java.math.BigDecimal;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ConfigurationHistoryService {

    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional
    public ConfigurationHistoryResponse save(AuthenticatedUserHeader user, JsonNode payload) {
        String purpose = text(payload, "purpose", "purpose");
        BigDecimal budget = decimal(payload, "budget", "budget");
        BigDecimal totalPrice = decimal(payload, "total_price", "totalPrice");
        String currency = text(payload, "currency", "currency", "RUB").toUpperCase();
        String performance = text(payload, "performance_estimate", "performanceEstimate");

        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            PreparedStatement statement = connection.prepareStatement(
                    """
                            INSERT INTO pc_configurations
                            (user_id, username, purpose, budget, total_price, currency, performance_estimate, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                    Statement.RETURN_GENERATED_KEYS
            );
            statement.setLong(1, user.userId());
            statement.setString(2, user.username());
            statement.setString(3, purpose);
            statement.setBigDecimal(4, budget);
            statement.setBigDecimal(5, totalPrice);
            statement.setString(6, currency);
            statement.setString(7, performance);
            statement.setTimestamp(8, Timestamp.from(Instant.now()));
            return statement;
        }, keyHolder);

        Long configurationId = ((Number) keyHolder.getKeyList().getFirst().get("id")).longValue();
        saveComponents(configurationId, array(payload, "components", "components"));
        saveChecks(configurationId, array(payload, "compatibility_checks", "compatibilityChecks"));
        saveAlternatives(configurationId, node(payload, "alternatives", "alternatives"));

        return findById(user, configurationId);
    }

    public List<ConfigurationHistoryResponse> list(AuthenticatedUserHeader user) {
        String sql = """
                SELECT id, user_id, username, purpose, budget, total_price, currency, performance_estimate, created_at
                FROM pc_configurations
                """;
        if (user.isAdmin()) {
            return jdbcTemplate.query(sql + " ORDER BY created_at DESC", this::mapHistoryRow);
        }
        return jdbcTemplate.query(
                sql + " WHERE user_id = ? ORDER BY created_at DESC",
                this::mapHistoryRow,
                user.userId()
        );
    }

    public ConfigurationHistoryResponse findById(AuthenticatedUserHeader user, Long configurationId) {
        String sql = """
                SELECT id, user_id, username, purpose, budget, total_price, currency, performance_estimate, created_at
                FROM pc_configurations
                WHERE id = ?
                """;
        if (!user.isAdmin()) {
            sql += " AND user_id = ?";
            return jdbcTemplate.queryForObject(sql, this::mapHistoryRow, configurationId, user.userId());
        }
        return jdbcTemplate.queryForObject(sql, this::mapHistoryRow, configurationId);
    }

    private void saveComponents(Long configurationId, JsonNode components) {
        if (!components.isArray()) {
            return;
        }
        for (JsonNode component : components) {
            jdbcTemplate.update(
                    """
                            INSERT INTO pc_configuration_items
                            (configuration_id, product_id, component_type, product_name, brand, quantity, price, score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                    configurationId,
                    nullableLong(component, "product_id", "productId"),
                    text(component, "type", "type"),
                    text(component, "model", "model"),
                    text(component, "brand", "brand"),
                    1,
                    decimal(component, "price", "price"),
                    decimal(component, "score", "score", BigDecimal.ZERO)
            );
        }
    }

    private void saveChecks(Long configurationId, JsonNode checks) {
        if (!checks.isArray()) {
            return;
        }
        for (JsonNode check : checks) {
            String message = check.asText();
            String status = message.toLowerCase().contains("fail") || message.toLowerCase().contains("mismatch")
                    ? "FAILED"
                    : "PASSED";
            jdbcTemplate.update(
                    """
                            INSERT INTO compatibility_checks
                            (configuration_id, check_type, check_status, message, checked_at)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                    configurationId,
                    "compatibility",
                    status,
                    message,
                    Timestamp.from(Instant.now())
            );
        }
    }

    private void saveAlternatives(Long configurationId, JsonNode alternatives) {
        if (alternatives == null || alternatives.isMissingNode() || alternatives.isNull()) {
            return;
        }
        saveAlternative(configurationId, "cheaper", node(alternatives, "cheaper", "cheaper"));
        saveAlternative(configurationId, "pricier", node(alternatives, "pricier", "pricier"));
    }

    private void saveAlternative(Long configurationId, String alternativeType, JsonNode alternative) {
        if (alternative == null || alternative.isMissingNode() || alternative.isNull()) {
            return;
        }
        try {
            jdbcTemplate.update(
                    """
                            INSERT INTO recommendation_alternatives
                            (configuration_id, alternative_type, total_price, payload_json)
                            VALUES (?, ?, ?, ?)
                            """,
                    configurationId,
                    alternativeType,
                    decimal(alternative, "total_price", "totalPrice"),
                    objectMapper.writeValueAsString(alternative)
            );
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to save configuration alternative", exception);
        }
    }

    private ConfigurationHistoryResponse mapHistoryRow(java.sql.ResultSet rs, int rowNum) throws java.sql.SQLException {
        return new ConfigurationHistoryResponse(
                rs.getLong("id"),
                rs.getLong("user_id"),
                rs.getString("username"),
                rs.getString("purpose"),
                rs.getBigDecimal("budget"),
                rs.getBigDecimal("total_price"),
                rs.getString("currency"),
                rs.getString("performance_estimate"),
                rs.getTimestamp("created_at").toInstant()
        );
    }

    private JsonNode node(JsonNode root, String snakeName, String camelName) {
        JsonNode value = root.get(snakeName);
        if (value == null) {
            value = root.get(camelName);
        }
        return value == null ? MissingNode.getInstance() : value;
    }

    private JsonNode array(JsonNode root, String snakeName, String camelName) {
        return node(root, snakeName, camelName);
    }

    private String text(JsonNode root, String snakeName, String camelName) {
        return text(root, snakeName, camelName, null);
    }

    private String text(JsonNode root, String snakeName, String camelName, String defaultValue) {
        JsonNode value = node(root, snakeName, camelName);
        if (value.isMissingNode() || value.isNull() || value.asText().isBlank()) {
            if (defaultValue != null) {
                return defaultValue;
            }
            throw new IllegalArgumentException("Missing required field: " + snakeName);
        }
        return value.asText().trim();
    }

    private BigDecimal decimal(JsonNode root, String snakeName, String camelName) {
        return decimal(root, snakeName, camelName, null);
    }

    private BigDecimal decimal(JsonNode root, String snakeName, String camelName, BigDecimal defaultValue) {
        JsonNode value = node(root, snakeName, camelName);
        if (value.isMissingNode() || value.isNull()) {
            if (defaultValue != null) {
                return defaultValue;
            }
            throw new IllegalArgumentException("Missing required field: " + snakeName);
        }
        return new BigDecimal(value.asText());
    }

    private Long nullableLong(JsonNode root, String snakeName, String camelName) {
        JsonNode value = node(root, snakeName, camelName);
        if (value.isMissingNode() || value.isNull()) {
            return null;
        }
        return value.asLong();
    }
}
