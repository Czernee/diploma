import { Link } from "react-router-dom";
import type { Product } from "../types";

export function ProductCard({
  product,
  onAddToCart
}: {
  product: Product;
  onAddToCart: (product: Product) => void;
}) {
  return (
    <article className="card product-card">
      <div>
        <p className="product-category">{product.category.name}</p>
        <h3>{product.name}</h3>
        <p className="muted">{product.brand}</p>
        <p className="description">{product.description}</p>
      </div>
      <div className="product-footer">
        <strong>
          {product.price} {product.currency}
        </strong>
        <p className={product.inStock ? "stock in" : "stock out"}>
          {product.inStock ? `В наличии: ${product.stockQuantity}` : "Нет в наличии"}
        </p>
        <div className="product-actions">
          <button className="btn btn-primary" disabled={!product.inStock} onClick={() => onAddToCart(product)}>
            В корзину
          </button>
          <Link to={`/catalog/${product.id}`} className="btn btn-secondary">
            Подробнее
          </Link>
        </div>
      </div>
    </article>
  );
}
