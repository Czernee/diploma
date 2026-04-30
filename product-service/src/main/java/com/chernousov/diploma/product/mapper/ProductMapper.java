package com.chernousov.diploma.product.mapper;

import com.chernousov.diploma.product.domain.Category;
import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.dto.CategoryResponse;
import com.chernousov.diploma.product.dto.ProductResponse;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.stream.Collectors;

@Mapper(componentModel = "spring")
public interface ProductMapper {

    @Mapping(target = "supportedSockets", expression = "java(splitCsvUppercase(product.getSupportedSockets()))")
    @Mapping(target = "notes", expression = "java(splitCsvRaw(product.getNotes()))")
    ProductResponse toResponse(Product product);

    CategoryResponse toResponse(Category category);

    List<CategoryResponse> toCategoryResponses(List<Category> categories);

    default List<String> splitCsvUppercase(String csv) {
        if (csv == null || csv.isBlank()) {
            return List.of();
        }
        return Arrays.stream(csv.split(","))
                .map(String::trim)
                .filter(value -> !value.isBlank())
                .map(value -> value.toUpperCase(Locale.ROOT))
                .filter(Objects::nonNull)
                .distinct()
                .collect(Collectors.toList());
    }

    default List<String> splitCsvRaw(String csv) {
        if (csv == null || csv.isBlank()) {
            return List.of();
        }
        return Arrays.stream(csv.split(","))
                .map(String::trim)
                .filter(value -> !value.isBlank())
                .filter(Objects::nonNull)
                .distinct()
                .collect(Collectors.toList());
    }
}
