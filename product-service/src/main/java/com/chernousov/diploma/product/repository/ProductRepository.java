package com.chernousov.diploma.product.repository;

import com.chernousov.diploma.product.domain.Product;
import com.chernousov.diploma.product.domain.ProductComponentType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Long>, JpaSpecificationExecutor<Product> {

    List<Product> findByComponentTypeNot(ProductComponentType componentType);
}
