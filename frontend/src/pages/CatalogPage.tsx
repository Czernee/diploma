import { FormEvent, useCallback, useEffect, useState } from "react";
import { fetchCategories, fetchProducts } from "../api/productApi";
import { ApiError } from "../api/http";
import { ProductCard } from "../components/ProductCard";
import { useCart } from "../context/CartContext";
import type { Category, Product } from "../types";

export function CatalogPage() {
  const { addProduct } = useCart();

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [categoryResult, pageResult] = await Promise.all([
        fetchCategories(),
        fetchProducts({
          query,
          category,
          inStock: inStockOnly ? true : undefined,
          page: 0,
          size: 24
        })
      ]);
      setCategories(categoryResult);
      setProducts(pageResult.items);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось загрузить каталог");
      }
    } finally {
      setLoading(false);
    }
  }, [category, inStockOnly, query]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSearch(event: FormEvent) {
    event.preventDefault();
    await load();
  }

  return (
    <section>
      <h1>Каталог товаров</h1>
      <form className="card filters" onSubmit={onSearch}>
        <input placeholder="Поиск по названию" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="">Все категории</option>
          {categories.map((item) => (
            <option key={item.id} value={item.slug}>
              {item.name}
            </option>
          ))}
        </select>
        <label className="checkbox">
          <input type="checkbox" checked={inStockOnly} onChange={(event) => setInStockOnly(event.target.checked)} />
          Только в наличии
        </label>
        <button className="btn btn-primary" type="submit">
          Применить фильтры
        </button>
      </form>

      {loading && <p>Загрузка каталога...</p>}
      {error && <p className="error">{error}</p>}

      <div className="grid catalog-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} onAddToCart={addProduct} />
        ))}
      </div>
    </section>
  );
}
