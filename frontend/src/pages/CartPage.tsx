import { FormEvent, useState } from "react";
import { createOrder } from "../api/orderApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import type { Order } from "../types";

export function CartPage() {
  const { items, totalAmount, setQuantity, removeItem, clear } = useCart();
  const { token } = useAuth();

  const [note, setNote] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [createdOrder, setCreatedOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);

  async function onCheckout(event: FormEvent) {
    event.preventDefault();
    if (!token || items.length === 0) {
      return;
    }
    setMessage(null);
    setCreatedOrder(null);
    setLoading(true);
    try {
      const order = await createOrder(token, {
        items: items.map((item) => ({
          productId: item.productId,
          productName: item.productName,
          quantity: item.quantity,
          unitPrice: item.unitPrice
        })),
        note: note || undefined,
        currency: "RUB"
      });
      setCreatedOrder(order);
      clear();
      setNote("");
    } catch (err) {
      if (err instanceof ApiError) {
        setMessage(err.message);
      } else {
        setMessage("Не удалось создать заказ");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>Корзина</h1>
      {items.length === 0 ? <p>Корзина пуста.</p> : null}
      <div className="card">
        {items.map((item) => (
          <div key={item.productId} className="cart-row">
            <div>
              <strong>{item.productName}</strong>
              <p className="muted">{item.unitPrice} {item.currency}</p>
            </div>
            <input
              type="number"
              min={1}
              value={item.quantity}
              onChange={(event) => setQuantity(item.productId, Number(event.target.value))}
            />
            <button className="btn btn-secondary" onClick={() => removeItem(item.productId)}>
              Удалить
            </button>
          </div>
        ))}
      </div>

      <p className="total">
        Итого: <strong>{totalAmount.toFixed(2)} RUB</strong>
      </p>

      <form className="card form" onSubmit={onCheckout}>
        <label>
          Комментарий к заказу (необязательно)
          <textarea
            maxLength={500}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Пожелания к доставке..."
          />
        </label>
        {!token && <p className="error">Войдите в аккаунт, чтобы оформить заказ.</p>}
        {message && <p className="error">{message}</p>}
        <button className="btn btn-primary" disabled={!token || items.length === 0 || loading}>
          {loading ? "Создаем заказ..." : "Оформить заказ"}
        </button>
      </form>

      {createdOrder && (
        <p className="success">Заказ №{createdOrder.id} создан, статус: {createdOrder.status}.</p>
      )}
    </section>
  );
}
