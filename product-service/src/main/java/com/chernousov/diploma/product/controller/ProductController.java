package com.chernousov.diploma.product.controller;

import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ConfiguratorComponentResponse;
import com.chernousov.diploma.product.dto.ProductCreateRequest;
import com.chernousov.diploma.product.dto.ProductPageResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.service.ProductService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.math.BigDecimal;
import java.util.List;

@Validated
@RequiredArgsConstructor
@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService productService;

    @GetMapping
    public ProductPageResponse search(
            @RequestParam(name = "query", required = false) String query,
            @RequestParam(name = "category", required = false) String category,
            @RequestParam(name = "minPrice", required = false) BigDecimal minPrice,
            @RequestParam(name = "maxPrice", required = false) BigDecimal maxPrice,
            @RequestParam(name = "inStock", required = false) Boolean inStock,
            @RequestParam(name = "page", required = false) Integer page,
            @RequestParam(name = "size", required = false) Integer size
    ) {
        ProductSearchRequest request = new ProductSearchRequest(
                query,
                category,
                minPrice,
                maxPrice,
                inStock,
                page,
                size
        );
        return productService.search(request);
    }

    @GetMapping("/{productId:\\d+}")
    public ProductResponse getById(@PathVariable(name = "productId") Long productId) {
        return productService.getById(productId);
    }

    @PostMapping
    public ProductResponse create(
            @RequestHeader(name = "X-User-Role", required = false) String userRole,
            @Valid @RequestBody ProductCreateRequest request
    ) {
        assertAdminRole(userRole);
        return productService.createProduct(request);
    }

    @PutMapping("/{productId:\\d+}")
    public ProductResponse update(
            @PathVariable(name = "productId") Long productId,
            @RequestHeader(name = "X-User-Role", required = false) String userRole,
            @Valid @RequestBody ProductCreateRequest request
    ) {
        assertAdminRole(userRole);
        return productService.updateProduct(productId, request);
    }

    @DeleteMapping("/{productId:\\d+}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(
            @PathVariable(name = "productId") Long productId,
            @RequestHeader(name = "X-User-Role", required = false) String userRole
    ) {
        assertAdminRole(userRole);
        productService.deleteProduct(productId);
    }

    @GetMapping("/categories")
    public List<CategoryResponse> categories() {
        return productService.listCategories();
    }

    @GetMapping("/configurator")
    public List<ConfiguratorComponentResponse> configuratorCatalog(
            @RequestParam(name = "inStock", required = false) Boolean inStock
    ) {
        return productService.listConfiguratorComponents(inStock);
    }

    private void assertAdminRole(String userRole) {
        if (userRole == null || !"ADMIN".equalsIgnoreCase(userRole)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin role is required");
        }
    }
}
