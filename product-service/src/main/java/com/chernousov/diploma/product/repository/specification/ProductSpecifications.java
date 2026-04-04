package com.chernousov.diploma.product.repository.specification;

import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import org.springframework.data.jpa.domain.Specification;

import java.math.BigDecimal;

public final class ProductSpecifications {

    private ProductSpecifications() {
    }

    public static Specification<Product> bySearchRequest(ProductSearchRequest request) {
        Specification<Product> specification = (root, query, cb) -> cb.conjunction();
        specification = andIfPresent(specification, hasQuery(request.query()));
        specification = andIfPresent(specification, hasCategory(request.category()));
        specification = andIfPresent(specification, priceFrom(request.minPrice()));
        specification = andIfPresent(specification, priceTo(request.maxPrice()));
        specification = andIfPresent(specification, hasInStock(request.inStock()));
        return specification;
    }

    private static Specification<Product> andIfPresent(
            Specification<Product> current,
            Specification<Product> candidate
    ) {
        return candidate == null ? current : current.and(candidate);
    }

    private static Specification<Product> hasQuery(String query) {
        if (query == null || query.isBlank()) {
            return null;
        }

        String like = "%" + query.trim().toLowerCase() + "%";
        return (root, ignored, cb) -> cb.or(
                cb.like(cb.lower(root.get("name")), like),
                cb.like(cb.lower(root.get("description")), like),
                cb.like(cb.lower(root.get("brand")), like)
        );
    }

    private static Specification<Product> hasCategory(String categorySlug) {
        if (categorySlug == null || categorySlug.isBlank()) {
            return null;
        }

        String slug = categorySlug.trim().toLowerCase();
        return (root, ignored, cb) -> cb.equal(cb.lower(root.get("category").get("slug")), slug);
    }

    private static Specification<Product> priceFrom(BigDecimal minPrice) {
        if (minPrice == null) {
            return null;
        }

        return (root, ignored, cb) -> cb.greaterThanOrEqualTo(root.get("price"), minPrice);
    }

    private static Specification<Product> priceTo(BigDecimal maxPrice) {
        if (maxPrice == null) {
            return null;
        }

        return (root, ignored, cb) -> cb.lessThanOrEqualTo(root.get("price"), maxPrice);
    }

    private static Specification<Product> hasInStock(Boolean inStock) {
        if (inStock == null) {
            return null;
        }

        return (root, ignored, cb) -> cb.equal(root.get("inStock"), inStock);
    }
}