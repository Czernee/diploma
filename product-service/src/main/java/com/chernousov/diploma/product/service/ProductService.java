package com.chernousov.diploma.product.service;

import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ConfiguratorComponentResponse;
import com.chernousov.diploma.product.dto.ProductCreateRequest;
import com.chernousov.diploma.product.dto.ProductPageResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.domain.Category;
import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.domain.ProductComponentType;
import com.chernousov.diploma.product.exception.ProductNotFoundException;
import com.chernousov.diploma.product.mapper.ProductMapper;
import com.chernousov.diploma.product.repository.CategoryRepository;
import com.chernousov.diploma.product.repository.ProductRepository;
import com.chernousov.diploma.product.repository.specification.ProductSpecifications;
import lombok.RequiredArgsConstructor;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.Caching;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;

@RequiredArgsConstructor
@Service
@Transactional(readOnly = true)
public class ProductService {

    private static final String PRODUCTS_SEARCH_CACHE = "products:search";
    private static final String PRODUCT_BY_ID_CACHE = "products:by-id";
    private static final String CATEGORIES_CACHE = "products:categories";
    private static final String CONFIGURATOR_CACHE = "products:configurator";

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    private final ProductMapper productMapper;

    @Cacheable(cacheNames = PRODUCTS_SEARCH_CACHE)
    public ProductPageResponse search(ProductSearchRequest request) {
        if (request.minPrice() != null && request.maxPrice() != null
                && request.minPrice().compareTo(request.maxPrice()) > 0) {
            throw new IllegalArgumentException("minPrice must be less than or equal to maxPrice");
        }

        PageRequest pageRequest = PageRequest.of(
                request.pageOrDefault(),
                request.sizeOrDefault(),
                Sort.by(Sort.Direction.ASC, "name")
        );

        Page<ProductResponse> page = productRepository
                .findAll(ProductSpecifications.bySearchRequest(request), pageRequest)
                .map(productMapper::toResponse);

        return new ProductPageResponse(
                page.getContent(),
                page.getNumber(),
                page.getSize(),
                page.getTotalElements(),
                page.getTotalPages()
        );
    }

    @Cacheable(cacheNames = PRODUCT_BY_ID_CACHE, key = "#productId")
    public ProductResponse getById(Long productId) {
        return productRepository.findById(productId)
                .map(productMapper::toResponse)
                .orElseThrow(() -> new ProductNotFoundException(productId));
    }

    @Cacheable(cacheNames = CATEGORIES_CACHE)
    public List<CategoryResponse> listCategories() {
        return productMapper.toCategoryResponses(categoryRepository.findAll(Sort.by(Sort.Direction.ASC, "name")));
    }

    @Cacheable(cacheNames = CONFIGURATOR_CACHE, key = "#inStockOnly")
    public List<ConfiguratorComponentResponse> listConfiguratorComponents(Boolean inStockOnly) {
        return productRepository.findByComponentTypeNot(ProductComponentType.OTHER)
                .stream()
                .filter(product -> inStockOnly == null || !inStockOnly || product.isInStock())
                .filter(product -> product.getPrice().compareTo(BigDecimal.ZERO) > 0)
                .map(this::toConfiguratorComponent)
                .toList();
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = PRODUCTS_SEARCH_CACHE, allEntries = true),
            @CacheEvict(cacheNames = PRODUCT_BY_ID_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CATEGORIES_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CONFIGURATOR_CACHE, allEntries = true)
    })
    public ProductResponse createProduct(ProductCreateRequest request) {
        Category category = findCategory(request.categoryId());

        Product product = Product.create(
                request.name(),
                request.description(),
                request.brand(),
                request.price(),
                request.currency(),
                request.inStock(),
                request.stockQuantity(),
                category,
                request.componentType(),
                request.socket(),
                joinCsvUppercase(request.supportedSockets()),
                request.ramType(),
                request.gpuTdp(),
                request.cpuTdp(),
                request.psuWatts(),
                request.supportsWifi(),
                request.scoreGaming(),
                request.scoreWork(),
                request.scoreStudy(),
                request.scoreGeneral(),
                request.notes()
        );
        Product saved = productRepository.save(product);
        return productMapper.toResponse(saved);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = PRODUCTS_SEARCH_CACHE, allEntries = true),
            @CacheEvict(cacheNames = PRODUCT_BY_ID_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CATEGORIES_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CONFIGURATOR_CACHE, allEntries = true)
    })
    public ProductResponse updateProduct(Long productId, ProductCreateRequest request) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ProductNotFoundException(productId));
        Category category = findCategory(request.categoryId());

        product.update(
                request.name(),
                request.description(),
                request.brand(),
                request.price(),
                request.currency(),
                request.inStock(),
                request.stockQuantity(),
                category,
                request.componentType(),
                request.socket(),
                joinCsvUppercase(request.supportedSockets()),
                request.ramType(),
                request.gpuTdp(),
                request.cpuTdp(),
                request.psuWatts(),
                request.supportsWifi(),
                request.scoreGaming(),
                request.scoreWork(),
                request.scoreStudy(),
                request.scoreGeneral(),
                request.notes()
        );

        return productMapper.toResponse(product);
    }

    @Transactional
    @Caching(evict = {
            @CacheEvict(cacheNames = PRODUCTS_SEARCH_CACHE, allEntries = true),
            @CacheEvict(cacheNames = PRODUCT_BY_ID_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CATEGORIES_CACHE, allEntries = true),
            @CacheEvict(cacheNames = CONFIGURATOR_CACHE, allEntries = true)
    })
    public void deleteProduct(Long productId) {
        Product product = productRepository.findById(productId)
                .orElseThrow(() -> new ProductNotFoundException(productId));
        productRepository.delete(product);
    }

    private ConfiguratorComponentResponse toConfiguratorComponent(Product product) {
        return new ConfiguratorComponentResponse(
                product.getId(),
                product.getName(),
                product.getBrand(),
                product.getPrice(),
                product.getCurrency(),
                product.getComponentType().name(),
                product.getSocket(),
                splitCsvUppercase(product.getSupportedSockets()),
                product.getRamType(),
                product.getGpuTdp(),
                product.getCpuTdp(),
                product.getPsuWatts(),
                product.isSupportsWifi(),
                scoreOrDefault(product.getScoreGaming()),
                scoreOrDefault(product.getScoreWork()),
                scoreOrDefault(product.getScoreStudy()),
                scoreOrDefault(product.getScoreGeneral()),
                splitCsvRaw(product.getNotes()),
                product.isInStock()
        );
    }

    private List<String> splitCsvUppercase(String csv) {
        if (csv == null || csv.isBlank()) {
            return List.of();
        }
        return Arrays.stream(csv.split(","))
                .map(String::trim)
                .filter(value -> !value.isBlank())
                .map(value -> value.toUpperCase(Locale.ROOT))
                .filter(Objects::nonNull)
                .distinct()
                .toList();
    }

    private List<String> splitCsvRaw(String csv) {
        if (csv == null || csv.isBlank()) {
            return List.of();
        }
        return Arrays.stream(csv.split(","))
                .map(String::trim)
                .filter(value -> !value.isBlank())
                .filter(Objects::nonNull)
                .distinct()
                .toList();
    }

    private String joinCsvUppercase(List<String> values) {
        if (values == null || values.isEmpty()) {
            return null;
        }
        String joined = values.stream()
                .filter(Objects::nonNull)
                .map(String::trim)
                .filter(value -> !value.isBlank())
                .map(value -> value.toUpperCase(Locale.ROOT))
                .distinct()
                .reduce((left, right) -> left + "," + right)
                .orElse("");
        return joined.isBlank() ? null : joined;
    }

    private Category findCategory(Long categoryId) {
        return categoryRepository.findById(categoryId)
                .orElseThrow(() -> new IllegalArgumentException("Category not found: " + categoryId));
    }

    private BigDecimal scoreOrDefault(BigDecimal value) {
        if (value == null) {
            return BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP);
        }
        return value.setScale(2, RoundingMode.HALF_UP);
    }
}
