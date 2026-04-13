package com.chernousov.diploma.product.controller;

import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ProductPageResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

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

    @GetMapping("/{productId}")
    public ProductResponse getById(@PathVariable("productId") Long productId) {
        return productService.getById(productId);
    }

    @GetMapping("/categories")
    public List<CategoryResponse> categories() {
        return productService.listCategories();
    }
}
