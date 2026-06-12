package com.chernousov.diploma.product.dto;

import java.io.Serializable;

public record CategoryResponse(
        Long id,
        String name,
        String slug
) implements Serializable {
}
