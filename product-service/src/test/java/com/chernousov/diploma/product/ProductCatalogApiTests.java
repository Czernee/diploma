package com.chernousov.diploma.product;

import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.exception.ProductNotFoundException;
import com.chernousov.diploma.product.service.ProductService;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest
class ProductCatalogApiTests {

    @Autowired
    private ProductService productService;

    @Test
    void searchReturnsSeedData() {
        var result = productService.search(new ProductSearchRequest(null, null, null, null, null, 0, 20));
        assertThat(result.totalItems()).isEqualTo(5);
        assertThat(result.items()).hasSize(5);
    }

    @Test
    void searchFiltersByCategoryAndStock() {
        var result = productService.search(new ProductSearchRequest(
                null, "graphics-cards", null, null, true, 0, 20
        ));
        assertThat(result.items()).hasSize(1);
        assertThat(result.items().getFirst().name()).isEqualTo("GeForce RTX 4070 Super");
    }

    @Test
    void getByIdReturnsNotFoundForUnknownProduct() {
        assertThatThrownBy(() -> productService.getById(99999L))
                .isInstanceOf(ProductNotFoundException.class);
    }

    @Test
    void categoriesReturnsSeededCategories() {
        var categories = productService.listCategories();
        assertThat(categories).hasSize(3);
        assertThat(categories.get(0).slug()).isEqualTo("graphics-cards");
        assertThat(categories.get(1).slug()).isEqualTo("memory");
        assertThat(categories.get(2).slug()).isEqualTo("processors");
    }
}
