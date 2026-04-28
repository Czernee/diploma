import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct } from "../api/productApi";
import { ApiError } from "../api/http";
import { useCart } from "../context/CartContext";
import type { Product } from "../types";

export function ProductDetailsPage() {
  const { productId } = useParams();
  const { addProduct } = useCart();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!productId) {
        setError("Не указан идентификатор товара");
        setLoading(false);
        return;
      }

      const numericProductId = Number(productId);
      if (!Number.isFinite(numericProductId)) {
        setError("Некорректный идентификатор товара");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await fetchProduct(numericProductId);
        setProduct(response);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Не удалось загрузить товар");
        }
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [productId]);

  if (loading) {
    return <p>Загрузка товара...</p>;
  }

  if (error) {
    return (
      <section className="stack">
        <p className="error">{error}</p>
        <Link to="/catalog" className="btn btn-secondary">
          Вернуться в каталог
        </Link>
      </section>
    );
  }

  if (!product) {
    return <p>Товар не найден.</p>;
  }

  return (
    <section className="card product-details">
      <p className="muted">{product.category.name}</p>
      <h1>{product.name}</h1>
      <p className="muted">Бренд: {product.brand}</p>
      <p>{product.description}</p>
      <p className={product.inStock ? "stock in" : "stock out"}>
        {product.inStock ? `В наличии: ${product.stockQuantity}` : "Нет в наличии"}
      </p>
      <p className="total">
        Цена:{" "}
        <strong>
          {product.price} {product.currency}
        </strong>
      </p>

      <div className="row">
        <button className="btn btn-primary" disabled={!product.inStock} onClick={() => addProduct(product)}>
          В корзину
        </button>
        <Link to="/catalog" className="btn btn-secondary">
          Назад в каталог
        </Link>
      </div>
    </section>
  );
}
