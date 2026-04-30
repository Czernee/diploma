import type { Category, Product, ProductCreateRequest, ProductPage } from "../types";
import { apiRequest } from "./http";

type ProductSearchParams = {
  query?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
  page?: number;
  size?: number;
};

export function fetchProducts(params: ProductSearchParams): Promise<ProductPage> {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, String(value));
    }
  });

  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return apiRequest<ProductPage>(`/api/products${suffix}`);
}

export function fetchProduct(productId: number): Promise<Product> {
  return apiRequest<Product>(`/api/products/${productId}`);
}

export function fetchCategories(): Promise<Category[]> {
  return apiRequest<Category[]>("/api/products/categories");
}

export function createProduct(token: string, payload: ProductCreateRequest): Promise<Product> {
  return apiRequest<Product>("/api/products", {
    method: "POST",
    token,
    body: payload
  });
}

export function updateProduct(token: string, productId: number, payload: ProductCreateRequest): Promise<Product> {
  return apiRequest<Product>(`/api/products/${productId}`, {
    method: "PUT",
    token,
    body: payload
  });
}

export function deleteProduct(token: string, productId: number): Promise<void> {
  return apiRequest<void>(`/api/products/${productId}`, {
    method: "DELETE",
    token
  });
}
