import { FormEvent, useCallback, useEffect, useState } from "react";
import { fetchCategories, fetchProducts } from "../api/productApi";
import { ApiError } from "../api/http";
import { ProductCard } from "../components/ProductCard";
import { useCart } from "../context/CartContext";
import type { Category, Product } from "../types";

const CATALOG_PAGE_SIZE = 24;

export function CatalogPage() {
  const { addProduct } = useCart();

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [page, setPage] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
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
          page,
          size: CATALOG_PAGE_SIZE
        })
      ]);
      setCategories(categoryResult);
      setProducts(pageResult.items);
      setTotalItems(pageResult.totalItems);
      setTotalPages(pageResult.totalPages);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось загрузить каталог");
      }
    } finally {
      setLoading(false);
    }
  }, [category, inStockOnly, page, query]);

  useEffect(() => {
    void load();
  }, [load]);

  function onSearch(event: FormEvent) {
    event.preventDefault();
    setPage(0);
  }

  function onQueryChange(value: string) {
    setQuery(value);
    setPage(0);
  }

  function onCategoryChange(value: string) {
    setCategory(value);
    setPage(0);
  }

  function onInStockChange(value: boolean) {
    setInStockOnly(value);
    setPage(0);
  }

  const currentPage = totalPages === 0 ? 0 : page + 1;
  const canGoBack = page > 0 && !loading;
  const canGoForward = page + 1 < totalPages && !loading;
  const showPagination = !error && totalItems > 0;

  function renderPagination() {
    if (!showPagination) {
      return null;
    }

    return (
      <div className="pagination card">
        <button className="btn btn-secondary" type="button" disabled={!canGoBack} onClick={() => setPage((value) => value - 1)}>
          Назад
        </button>
        <p>
          Страница {currentPage} из {totalPages}. Всего товаров: {totalItems}
        </p>
        <button className="btn btn-secondary" type="button" disabled={!canGoForward} onClick={() => setPage((value) => value + 1)}>
          Вперед
        </button>
      </div>
    );
  }

  return (
    <section>
      <h1>Каталог товаров</h1>
      <form className="card filters" onSubmit={onSearch}>
        <input placeholder="Поиск по названию" value={query} onChange={(event) => onQueryChange(event.target.value)} />
        <select value={category} onChange={(event) => onCategoryChange(event.target.value)}>
          <option value="">Все категории</option>
          {categories.map((item) => (
            <option key={item.id} value={item.slug}>
              {item.name}
            </option>
          ))}
        </select>
        <label className="checkbox">
          <input type="checkbox" checked={inStockOnly} onChange={(event) => onInStockChange(event.target.checked)} />
          Только в наличии
        </label>
        <button className="btn btn-primary" type="submit">
          Применить фильтры
        </button>
      </form>

      {loading && <p>Загрузка каталога...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && products.length === 0 && <p className="muted">Товары по выбранным фильтрам не найдены.</p>}
      {renderPagination()}

      <div className="grid catalog-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} onAddToCart={addProduct} />
        ))}
      </div>

      {renderPagination()}
    </section>
  );
}
