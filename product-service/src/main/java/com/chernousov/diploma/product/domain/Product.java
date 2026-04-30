package com.chernousov.diploma.product.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Locale;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
@Table(name = "products")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 180)
    private String name;

    @Column(length = 2000)
    private String description;

    @Column(nullable = false, length = 120)
    private String brand;

    @Column(nullable = false, precision = 12, scale = 2)
    private BigDecimal price;

    @Column(nullable = false, length = 8)
    private String currency;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private ProductComponentType componentType;

    @Column(length = 40)
    private String socket;

    @Column(length = 255)
    private String supportedSockets;

    @Column(length = 20)
    private String ramType;

    @Column(nullable = false)
    private Integer gpuTdp;

    @Column(nullable = false)
    private Integer cpuTdp;

    @Column(nullable = false)
    private Integer psuWatts;

    @Column(nullable = false)
    private boolean supportsWifi;

    @Column(nullable = false, precision = 4, scale = 2)
    private BigDecimal scoreGaming;

    @Column(nullable = false, precision = 4, scale = 2)
    private BigDecimal scoreWork;

    @Column(nullable = false, precision = 4, scale = 2)
    private BigDecimal scoreStudy;

    @Column(nullable = false, precision = 4, scale = 2)
    private BigDecimal scoreGeneral;

    @Column(length = 1000)
    private String notes;

    @Column(nullable = false)
    private boolean inStock;

    @Column(nullable = false)
    private Integer stockQuantity;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    @PrePersist
    void onCreate() {
        Instant now = Instant.now();
        createdAt = now;
        updatedAt = now;
        if (componentType == null) {
            componentType = ProductComponentType.OTHER;
        }
        if (gpuTdp == null) {
            gpuTdp = 0;
        }
        if (cpuTdp == null) {
            cpuTdp = 0;
        }
        if (psuWatts == null) {
            psuWatts = 0;
        }
        if (scoreGaming == null) {
            scoreGaming = BigDecimal.ZERO;
        }
        if (scoreWork == null) {
            scoreWork = BigDecimal.ZERO;
        }
        if (scoreStudy == null) {
            scoreStudy = BigDecimal.ZERO;
        }
        if (scoreGeneral == null) {
            scoreGeneral = BigDecimal.ZERO;
        }
    }

    @PreUpdate
    void onUpdate() {
        updatedAt = Instant.now();
    }

    public static Product create(
            String name,
            String description,
            String brand,
            BigDecimal price,
            String currency,
            boolean inStock,
            Integer stockQuantity,
            Category category,
            ProductComponentType componentType,
            String socket,
            String supportedSockets,
            String ramType,
            Integer gpuTdp,
            Integer cpuTdp,
            Integer psuWatts,
            boolean supportsWifi,
            BigDecimal scoreGaming,
            BigDecimal scoreWork,
            BigDecimal scoreStudy,
            BigDecimal scoreGeneral,
            String notes
    ) {
        Product product = new Product();
        product.apply(
                name,
                description,
                brand,
                price,
                currency,
                inStock,
                stockQuantity,
                category,
                componentType,
                socket,
                supportedSockets,
                ramType,
                gpuTdp,
                cpuTdp,
                psuWatts,
                supportsWifi,
                scoreGaming,
                scoreWork,
                scoreStudy,
                scoreGeneral,
                notes
        );
        return product;
    }

    public void update(
            String name,
            String description,
            String brand,
            BigDecimal price,
            String currency,
            boolean inStock,
            Integer stockQuantity,
            Category category,
            ProductComponentType componentType,
            String socket,
            String supportedSockets,
            String ramType,
            Integer gpuTdp,
            Integer cpuTdp,
            Integer psuWatts,
            boolean supportsWifi,
            BigDecimal scoreGaming,
            BigDecimal scoreWork,
            BigDecimal scoreStudy,
            BigDecimal scoreGeneral,
            String notes
    ) {
        apply(
                name,
                description,
                brand,
                price,
                currency,
                inStock,
                stockQuantity,
                category,
                componentType,
                socket,
                supportedSockets,
                ramType,
                gpuTdp,
                cpuTdp,
                psuWatts,
                supportsWifi,
                scoreGaming,
                scoreWork,
                scoreStudy,
                scoreGeneral,
                notes
        );
    }

    private void apply(
            String name,
            String description,
            String brand,
            BigDecimal price,
            String currency,
            boolean inStock,
            Integer stockQuantity,
            Category category,
            ProductComponentType componentType,
            String socket,
            String supportedSockets,
            String ramType,
            Integer gpuTdp,
            Integer cpuTdp,
            Integer psuWatts,
            boolean supportsWifi,
            BigDecimal scoreGaming,
            BigDecimal scoreWork,
            BigDecimal scoreStudy,
            BigDecimal scoreGeneral,
            String notes
    ) {
        this.name = normalize(name);
        this.description = normalizeNullable(description);
        this.brand = normalize(brand);
        this.price = price;
        this.currency = normalizeCurrency(currency);
        this.inStock = inStock;
        this.stockQuantity = stockQuantity;
        this.category = category;
        this.componentType = componentType == null ? ProductComponentType.OTHER : componentType;
        this.socket = normalizeNullable(socket);
        this.supportedSockets = normalizeNullable(supportedSockets);
        this.ramType = normalizeNullable(ramType);
        this.gpuTdp = gpuTdp == null ? 0 : gpuTdp;
        this.cpuTdp = cpuTdp == null ? 0 : cpuTdp;
        this.psuWatts = psuWatts == null ? 0 : psuWatts;
        this.supportsWifi = supportsWifi;
        this.scoreGaming = scoreGaming == null ? BigDecimal.ZERO : scoreGaming;
        this.scoreWork = scoreWork == null ? BigDecimal.ZERO : scoreWork;
        this.scoreStudy = scoreStudy == null ? BigDecimal.ZERO : scoreStudy;
        this.scoreGeneral = scoreGeneral == null ? BigDecimal.ZERO : scoreGeneral;
        this.notes = normalizeNullable(notes);
    }

    private static String normalize(String value) {
        return value == null ? "" : value.trim();
    }

    private static String normalizeNullable(String value) {
        if (value == null) {
            return null;
        }
        String normalized = value.trim();
        return normalized.isBlank() ? null : normalized;
    }

    private static String normalizeCurrency(String value) {
        return normalize(value).toUpperCase(Locale.ROOT);
    }
}
