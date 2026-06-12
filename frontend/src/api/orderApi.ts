import type { CartResponse, ConfigurationHistory, Order, OrderStatus } from "../types";
import { apiRequest } from "./http";

export function createOrder(
  token: string,
  payload: {
    items: Array<{
      productId: number;
      productName: string;
      quantity: number;
      unitPrice: number;
    }>;
    note?: string;
    currency: string;
  }
): Promise<Order> {
  return apiRequest<Order>("/api/orders", {
    method: "POST",
    token,
    body: payload
  });
}

export function fetchMyOrders(token: string): Promise<Order[]> {
  return apiRequest<Order[]>("/api/orders", { token });
}

export function fetchOrder(token: string, orderId: number): Promise<Order> {
  return apiRequest<Order>(`/api/orders/${orderId}`, { token });
}

export function updateOrderStatus(token: string, orderId: number, status: OrderStatus): Promise<Order> {
  return apiRequest<Order>(`/api/orders/${orderId}/status`, {
    method: "POST",
    token,
    body: { status }
  });
}

export function fetchCart(token: string): Promise<CartResponse> {
  return apiRequest<CartResponse>("/api/orders/cart", { token });
}

export function addCartItem(
  token: string,
  payload: {
    productId: number;
    productName: string;
    quantity: number;
    unitPrice: number;
    currency: string;
  }
): Promise<CartResponse> {
  return apiRequest<CartResponse>("/api/orders/cart/items", {
    method: "POST",
    token,
    body: payload
  });
}

export function updateCartItemQuantity(token: string, productId: number, quantity: number): Promise<CartResponse> {
  return apiRequest<CartResponse>(`/api/orders/cart/items/${productId}`, {
    method: "PUT",
    token,
    body: { quantity }
  });
}

export function deleteCartItem(token: string, productId: number): Promise<CartResponse> {
  return apiRequest<CartResponse>(`/api/orders/cart/items/${productId}`, {
    method: "DELETE",
    token
  });
}

export function clearServerCart(token: string): Promise<CartResponse> {
  return apiRequest<CartResponse>("/api/orders/cart", {
    method: "DELETE",
    token
  });
}

export function fetchConfigurationHistory(token: string): Promise<ConfigurationHistory[]> {
  return apiRequest<ConfigurationHistory[]>("/api/orders/configurations", { token });
}
