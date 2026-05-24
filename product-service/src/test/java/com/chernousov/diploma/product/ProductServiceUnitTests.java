package com.chernousov.diploma.product;

import com.chernousov.diploma.product.domain.Category;
import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.domain.ProductComponentType;
import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ProductCreateRequest;
import com.chernousov.diploma.product.dto.ProductResponse;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.mapper.ProductMapper;
import com.chernousov.diploma.product.repository.CategoryRepository;
import com.chernousov.diploma.product.repository.ProductRepository;
import com.chernousov.diploma.product.service.ProductService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ProductServiceUnitTests {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private CategoryRepository categoryRepository;

    @Mock
    private ProductMapper productMapper;

    @InjectMocks
    private ProductService productService;

    @Test
    void searchRejectsInvalidPriceRange() {
        assertThatThrownBy(() -> productService.search(
                new ProductSearchRequest(null, null, new BigDecimal("100"), new BigDecimal("10"), null, 0, 20)
        ))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("minPrice must be less than or equal to maxPrice");
    }

    @Test
    void createProductNormalizesSupportedSocketsToUppercaseCsv() {
        Category category = org.mockito.Mockito.mock(Category.class);
        when(categoryRepository.findById(10L)).thenReturn(Optional.of(category));
        when(productRepository.save(any(Product.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(productMapper.toResponse(any(Product.class))).thenAnswer(invocation -> {
            Product product = invocation.getArgument(0);
            return new ProductResponse(
                    1L,
                    product.getName(),
                    product.getDescription(),
                    product.getBrand(),
                    product.getPrice(),
                    product.getCurrency(),
                    product.getComponentType().name(),
                    product.getSocket(),
                    List.of(),
                    product.getRamType(),
                    product.getGpuTdp(),
                    product.getCpuTdp(),
                    product.getPsuWatts(),
                    product.isSupportsWifi(),
                    product.getScoreGaming(),
                    product.getScoreWork(),
                    product.getScoreStudy(),
                    product.getScoreGeneral(),
                    List.of(),
                    product.isInStock(),
                    product.getStockQuantity(),
                    new CategoryResponse(10L, "Processors", "processors")
            );
        });

        productService.createProduct(new ProductCreateRequest(
                "CPU Test",
                "desc",
                "Brand",
                new BigDecimal("15999.99"),
                "rub",
                true,
                3,
                10L,
                ProductComponentType.CPU,
                "AM5",
                List.of(" am5 ", "AM4", "am5"),
                null,
                0,
                65,
                0,
                false,
                new BigDecimal("8.0"),
                new BigDecimal("7.0"),
                new BigDecimal("6.0"),
                new BigDecimal("7.5"),
                "note"
        ));

        ArgumentCaptor<Product> savedCaptor = ArgumentCaptor.forClass(Product.class);
        verify(productRepository).save(savedCaptor.capture());
        Product saved = savedCaptor.getValue();

        assertThat(saved.getSupportedSockets()).isEqualTo("AM5,AM4");
        assertThat(saved.getCurrency()).isEqualTo("RUB");
    }

    @Test
    void createProductFailsWhenCategoryDoesNotExist() {
        when(categoryRepository.findById(999L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.createProduct(new ProductCreateRequest(
                "CPU Test",
                "desc",
                "Brand",
                new BigDecimal("15999.99"),
                "RUB",
                true,
                3,
                999L,
                ProductComponentType.CPU,
                "AM5",
                List.of("AM5"),
                null,
                0,
                65,
                0,
                false,
                new BigDecimal("8.0"),
                new BigDecimal("7.0"),
                new BigDecimal("6.0"),
                new BigDecimal("7.5"),
                "note"
        )))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Category not found");
    }
}
