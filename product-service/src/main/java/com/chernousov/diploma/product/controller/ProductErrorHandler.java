package com.chernousov.diploma.product.controller;

import com.chernousov.diploma.product.exception.ProductNotFoundException;
import jakarta.validation.ConstraintViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ProductErrorHandler {

    @ExceptionHandler(ProductNotFoundException.class)
    public ProblemDetail handleNotFound(ProductNotFoundException exception) {
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, exception.getMessage());
        problemDetail.setTitle("Product not found");
        return problemDetail;
    }

    @ExceptionHandler({IllegalArgumentException.class, ConstraintViolationException.class, MethodArgumentNotValidException.class})
    public ProblemDetail handleBadRequest(Exception exception) {
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, exception.getMessage());
        problemDetail.setTitle("Invalid request");
        return problemDetail;
    }
}
