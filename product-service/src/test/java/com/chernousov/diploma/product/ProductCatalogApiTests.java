package com.chernousov.diploma.product;

import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.dto.ProductCreateRequest;
import com.chernousov.diploma.product.domain.ProductComponentType;
import com.chernousov.diploma.product.exception.ProductNotFoundException;
import com.chernousov.diploma.product.service.ProductService;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.math.BigDecimal;
import java.util.List;

@SpringBootTest
class ProductCatalogApiTests {

    @Autowired
    private ProductService productService;

    @Test
    void searchReturnsSeedData() {
        var result = productService.search(new ProductSearchRequest(null, null, null, null, null, 0, 20));
        assertThat(result.totalItems()).isGreaterThanOrEqualTo(10);
        assertThat(result.items()).hasSizeGreaterThanOrEqualTo(10);
    }

    @Test
    void searchRejectsInvalidPriceRange() {
        assertThatThrownBy(() -> productService.search(new ProductSearchRequest(
                null, null, new BigDecimal("20000"), new BigDecimal("10000"), null, 0, 20
        )))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("minPrice must be less than or equal to maxPrice");
    }

    @Test
    void searchCapsPageSizeToOneHundred() {
        var result = productService.search(new ProductSearchRequest(null, null, null, null, null, 0, 1000));
        assertThat(result.size()).isEqualTo(100);
    }

    @Test
    void searchFiltersByCategoryAndStock() {
        var result = productService.search(new ProductSearchRequest(
                null, "graphics-cards", null, null, true, 0, 20
        ));
        assertThat(result.items()).hasSizeGreaterThanOrEqualTo(4);
        assertThat(result.items()).extracting("name")
                .contains("GeForce RTX 3050 8GB", "GeForce RTX 4060 8GB", "GeForce RTX 4070 Super");
    }

    @Test
    void getByIdReturnsNotFoundForUnknownProduct() {
        assertThatThrownBy(() -> productService.getById(99999L))
                .isInstanceOf(ProductNotFoundException.class);
    }

    @Test
    void categoriesReturnsSeededCategories() {
        var categories = productService.listCategories();
        assertThat(categories).hasSizeGreaterThanOrEqualTo(7);
        assertThat(categories).extracting("slug")
                .contains("graphics-cards", "memory", "processors", "motherboards", "storage", "power-supplies", "cases");
    }

    @Test
    void configuratorCatalogReturnsOnlyConfiguratorItems() {
        var items = productService.listConfiguratorComponents(true);
        assertThat(items).isNotEmpty();
        assertThat(items).extracting("componentType")
                .doesNotContain("OTHER");
        assertThat(items).allMatch(item -> item.price().intValue() > 0);
        assertThat(items).allMatch(item -> item.inStock());
    }

    @Test
    void createProductAddsNewCatalogItem() {
        Long categoryId = productService.listCategories().stream()
                .filter(category -> "processors".equals(category.slug()))
                .findFirst()
                .orElseThrow()
                .id();

        var created = productService.createProduct(new ProductCreateRequest(
                "Test Admin CPU",
                "Created via admin panel flow",
                "TestBrand",
                new BigDecimal("12345.00"),
                "RUB",
                true,
                7,
                categoryId,
                ProductComponentType.CPU,
                "AM5",
                List.of("AM5"),
                null,
                0,
                95,
                0,
                false,
                new BigDecimal("7.50"),
                new BigDecimal("7.30"),
                new BigDecimal("7.10"),
                new BigDecimal("7.40"),
                "test,note"
        ));

        assertThat(created.id()).isNotNull();
        assertThat(created.name()).isEqualTo("Test Admin CPU");
        assertThat(created.category().slug()).isEqualTo("processors");
    }

    @Test
    void updateProductEditsExistingCatalogItem() {
        Long categoryId = productService.listCategories().stream()
                .filter(category -> "memory".equals(category.slug()))
                .findFirst()
                .orElseThrow()
                .id();

        var created = productService.createProduct(new ProductCreateRequest(
                "Test Admin RAM",
                "Created for update test",
                "TestBrand",
                new BigDecimal("10000.00"),
                "RUB",
                true,
                5,
                categoryId,
                ProductComponentType.RAM,
                null,
                List.of(),
                "DDR5",
                0,
                0,
                0,
                false,
                new BigDecimal("6.50"),
                new BigDecimal("6.70"),
                new BigDecimal("6.90"),
                new BigDecimal("6.60"),
                "before,update"
        ));

        var updated = productService.updateProduct(created.id(), new ProductCreateRequest(
                "Test Admin RAM Updated",
                "Updated description",
                "UpdatedBrand",
                new BigDecimal("11111.00"),
                "RUB",
                true,
                8,
                categoryId,
                ProductComponentType.RAM,
                null,
                List.of(),
                "DDR5",
                0,
                0,
                0,
                false,
                new BigDecimal("7.00"),
                new BigDecimal("7.20"),
                new BigDecimal("7.40"),
                new BigDecimal("7.10"),
                "after,update"
        ));

        assertThat(updated.id()).isEqualTo(created.id());
        assertThat(updated.name()).isEqualTo("Test Admin RAM Updated");
        assertThat(updated.brand()).isEqualTo("UpdatedBrand");
        assertThat(updated.price()).isEqualByComparingTo("11111.00");
    }

    @Test
    void updateProductFailsForUnknownId() {
        Long categoryId = productService.listCategories().stream()
                .filter(category -> "memory".equals(category.slug()))
                .findFirst()
                .orElseThrow()
                .id();

        assertThatThrownBy(() -> productService.updateProduct(999999L, new ProductCreateRequest(
                "Unknown Product",
                "desc",
                "Brand",
                new BigDecimal("11111.00"),
                "RUB",
                true,
                8,
                categoryId,
                ProductComponentType.RAM,
                null,
                List.of(),
                "DDR5",
                0,
                0,
                0,
                false,
                new BigDecimal("7.00"),
                new BigDecimal("7.20"),
                new BigDecimal("7.40"),
                new BigDecimal("7.10"),
                "note"
        )))
                .isInstanceOf(ProductNotFoundException.class);
    }

    @Test
    void deleteProductRemovesCatalogItem() {
        Long categoryId = productService.listCategories().stream()
                .filter(category -> "storage".equals(category.slug()))
                .findFirst()
                .orElseThrow()
                .id();

        var created = productService.createProduct(new ProductCreateRequest(
                "Test Admin SSD Delete",
                "Created for delete test",
                "TestBrand",
                new BigDecimal("9999.00"),
                "RUB",
                true,
                3,
                categoryId,
                ProductComponentType.STORAGE,
                null,
                List.of(),
                null,
                0,
                0,
                0,
                false,
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                "delete,test"
        ));

        productService.deleteProduct(created.id());

        assertThatThrownBy(() -> productService.getById(created.id()))
                .isInstanceOf(ProductNotFoundException.class);
    }

    @Test
    void deleteProductFailsForUnknownId() {
        assertThatThrownBy(() -> productService.deleteProduct(999999L))
                .isInstanceOf(ProductNotFoundException.class);
    }

    @Test
    void createProductFailsForUnknownCategory() {
        assertThatThrownBy(() -> productService.createProduct(new ProductCreateRequest(
                "Test Product",
                "desc",
                "Brand",
                new BigDecimal("9999.00"),
                "RUB",
                true,
                3,
                999999L,
                ProductComponentType.STORAGE,
                null,
                List.of(),
                null,
                0,
                0,
                0,
                false,
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                new BigDecimal("6.20"),
                "test"
        )))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Category not found");
    }
}
