package com.chernousov.diploma.product.mapper;

import com.chernousov.diploma.product.domain.Category;
import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import org.mapstruct.Mapper;

import java.util.List;

@Mapper(componentModel = "spring")
public interface ProductMapper {

    ProductResponse toResponse(Product product);

    CategoryResponse toResponse(Category category);

    List<CategoryResponse> toCategoryResponses(List<Category> categories);
}