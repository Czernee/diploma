import type { Order, OrderStatus } from "../types";
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
