package com.chernousov.diploma.product.service;

import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ProductPageResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import com.chernousov.diploma.product.dto.ProductSearchRequest;
import com.chernousov.diploma.product.exception.ProductNotFoundException;
import com.chernousov.diploma.product.mapper.ProductMapper;
import com.chernousov.diploma.product.repository.CategoryRepository;
import com.chernousov.diploma.product.repository.ProductRepository;
import com.chernousov.diploma.product.repository.specification.ProductSpecifications;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@RequiredArgsConstructor
@Service
@Transactional(readOnly = true)
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;
    private final ProductMapper productMapper;

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

    public ProductResponse getById(Long productId) {
        return productRepository.findById(productId)
                .map(productMapper::toResponse)
                .orElseThrow(() -> new ProductNotFoundException(productId));
    }

    public List<CategoryResponse> listCategories() {
        return productMapper.toCategoryResponses(categoryRepository.findAll(Sort.by(Sort.Direction.ASC, "name")));
    }
}
