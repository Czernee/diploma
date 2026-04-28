import { useCallback, useEffect, useState } from "react";
import { fetchMyOrders, updateOrderStatus } from "../api/orderApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import type { Order, OrderStatus } from "../types";

const statusLabels: Record<string, string> = {
  CREATED: "Создан",
  CONFIRMED: "Подтвержден",
  PROCESSING: "В обработке",
  SHIPPED: "Отправлен",
  DELIVERED: "Доставлен",
  CANCELLED: "Отменен"
};

const USER_CANCELLABLE_STATUSES = new Set<OrderStatus>(["CREATED", "CONFIRMED", "PROCESSING"]);

function adminAllowedStatuses(currentStatus: OrderStatus): OrderStatus[] {
  switch (currentStatus) {
    case "CREATED":
      return ["CREATED", "CONFIRMED", "CANCELLED"];
    case "CONFIRMED":
      return ["CONFIRMED", "PROCESSING", "CANCELLED"];
    case "PROCESSING":
      return ["PROCESSING", "SHIPPED", "CANCELLED"];
    case "SHIPPED":
      return ["SHIPPED", "DELIVERED"];
    case "DELIVERED":
      return ["DELIVERED"];
    case "CANCELLED":
      return ["CANCELLED"];
    default:
      return [currentStatus];
  }
}

function availableStatuses(currentStatus: OrderStatus, isAdmin: boolean): OrderStatus[] {
  if (isAdmin) {
    return adminAllowedStatuses(currentStatus);
  }
  if (USER_CANCELLABLE_STATUSES.has(currentStatus)) {
    return [currentStatus, "CANCELLED"];
  }
  return [currentStatus];
}

function formatStatus(status: string): string {
  return statusLabels[status] ?? status;
}

export function OrdersPage() {
  const { token, user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const isAdmin = user?.role?.toUpperCase() === "ADMIN";

  const load = useCallback(async () => {
    if (!token) {
      setOrders([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await fetchMyOrders(token);
      setOrders(result);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось загрузить заказы");
      }
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onChangeStatus(orderId: number, status: OrderStatus) {
    if (!token) {
      return;
    }

    const currentOrder = orders.find((item) => item.id === orderId);
    if (!currentOrder || currentOrder.status === status) {
      return;
    }

    setError(null);
    try {
      const updated = await updateOrderStatus(token, orderId, status);
      setOrders((previous) => previous.map((item) => (item.id === orderId ? updated : item)));
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось обновить статус");
      }
    }
  }

  if (!token) {
    return <p>Войдите в аккаунт, чтобы увидеть ваши заказы.</p>;
  }

  return (
    <section>
      <h1>{isAdmin ? "Все заказы" : "Мои заказы"}</h1>
      {loading && <p>Загрузка заказов...</p>}
      {error && <p className="error">{error}</p>}
      <div className="stack">
        {orders.map((order) => {
          const statuses = availableStatuses(order.status, isAdmin);
          const canChangeStatus = statuses.length > 1;

          return (
            <article className="card" key={order.id}>
              <div className="order-head">
                <h3>Заказ №{order.id}</h3>
                <p>
                  {order.totalAmount} {order.currency}
                </p>
              </div>
              <p className="muted">Создан: {new Date(order.createdAt).toLocaleString()}</p>
              {isAdmin && (
                <p className="muted">
                  Пользователь: {order.username} (ID: {order.userId})
                </p>
              )}
              <p>Текущий статус: {formatStatus(order.status)}</p>
              <div className="row">
                {canChangeStatus ? (
                  <select value={order.status} onChange={(e) => void onChangeStatus(order.id, e.target.value as OrderStatus)}>
                    {statuses.map((status) => (
                      <option value={status} key={status}>
                        {formatStatus(status)}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="muted">Изменение статуса недоступно</span>
                )}
              </div>
              <ul>
                {order.items.map((item) => (
                  <li key={`${order.id}-${item.productId}`}>
                    {item.productName} x{item.quantity} - {item.lineTotal} {order.currency}
                  </li>
                ))}
              </ul>
            </article>
          );
        })}
      </div>
    </section>
  );
}
