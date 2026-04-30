import { FormEvent, useEffect, useState } from "react";
import { createProduct, deleteProduct, fetchCategories, fetchProducts, updateProduct } from "../api/productApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import type { Category, Product, ProductComponentType, ProductCreateRequest } from "../types";

const componentTypes: ProductComponentType[] = ["CPU", "GPU", "MOTHERBOARD", "RAM", "STORAGE", "PSU", "CASE", "OTHER"];

function parseCsv(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

function buildInitialPayload(categoryId: number): ProductCreateRequest {
  return {
    name: "",
    description: "",
    brand: "",
    price: 0,
    currency: "RUB",
    inStock: true,
    stockQuantity: 1,
    categoryId,
    componentType: "OTHER",
    socket: "",
    supportedSockets: [],
    ramType: "",
    gpuTdp: 0,
    cpuTdp: 0,
    psuWatts: 0,
    supportsWifi: false,
    scoreGaming: 0,
    scoreWork: 0,
    scoreStudy: 0,
    scoreGeneral: 0,
    notes: ""
  };
}

export function AdminProductsPage() {
  const { token } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingProductId, setEditingProductId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [supportedSocketsText, setSupportedSocketsText] = useState("");
  const [payload, setPayload] = useState<ProductCreateRequest>(buildInitialPayload(0));

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [categoriesData, productsPage] = await Promise.all([
          fetchCategories(),
          fetchProducts({ page: 0, size: 200 })
        ]);
        if (cancelled) {
          return;
        }
        setCategories(categoriesData);
        setProducts(productsPage.items);
        setPayload((prev) => {
          if (prev.categoryId > 0 || categoriesData.length === 0) {
            return prev;
          }
          return { ...prev, categoryId: categoriesData[0].id };
        });
      } catch {
        if (!cancelled) {
          setError("Не удалось загрузить данные админ-панели");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  function resetForm() {
    setEditingProductId(null);
    setSupportedSocketsText("");
    setPayload(buildInitialPayload(categories[0]?.id ?? 0));
  }

  function startEdit(product: Product) {
    setEditingProductId(product.id);
    setSupportedSocketsText((product.supportedSockets ?? []).join(", "));
    setPayload({
      name: product.name,
      description: product.description ?? "",
      brand: product.brand,
      price: product.price,
      currency: product.currency,
      inStock: product.inStock,
      stockQuantity: product.stockQuantity,
      categoryId: product.category.id,
      componentType: product.componentType ?? "OTHER",
      socket: product.socket ?? "",
      supportedSockets: product.supportedSockets ?? [],
      ramType: product.ramType ?? "",
      gpuTdp: product.gpuTdp ?? 0,
      cpuTdp: product.cpuTdp ?? 0,
      psuWatts: product.psuWatts ?? 0,
      supportsWifi: product.supportsWifi ?? false,
      scoreGaming: product.scoreGaming ?? 0,
      scoreWork: product.scoreWork ?? 0,
      scoreStudy: product.scoreStudy ?? 0,
      scoreGeneral: product.scoreGeneral ?? 0,
      notes: product.notes?.join(", ") ?? ""
    });
    setError(null);
    setSuccess(`Редактирование товара #${product.id}`);
  }

  async function onDelete(product: Product) {
    if (!token) {
      setError("Войдите как администратор");
      return;
    }
    if (!window.confirm(`Удалить товар «${product.name}» (#${product.id})?`)) {
      return;
    }

    setError(null);
    setSuccess(null);
    try {
      await deleteProduct(token, product.id);
      setProducts((prev) => prev.filter((item) => item.id !== product.id));
      if (editingProductId === product.id) {
        resetForm();
      }
      setSuccess(`Товар #${product.id} удален`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось удалить товар");
      }
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setError("Войдите как администратор");
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccess(null);

    const requestPayload: ProductCreateRequest = {
      ...payload,
      description: payload.description?.trim() ? payload.description.trim() : null,
      socket: payload.socket?.trim() ? payload.socket.trim() : null,
      ramType: payload.ramType?.trim() ? payload.ramType.trim() : null,
      notes: payload.notes?.trim() ? payload.notes.trim() : null,
      supportedSockets: parseCsv(supportedSocketsText)
    };

    try {
      if (editingProductId == null) {
        const created = await createProduct(token, requestPayload);
        setProducts((prev) => [created, ...prev]);
        setSuccess(`Товар создан: #${created.id} ${created.name}`);
      } else {
        const updated = await updateProduct(token, editingProductId, requestPayload);
        setProducts((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        setSuccess(`Товар обновлен: #${updated.id} ${updated.name}`);
      }
      resetForm();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError(editingProductId == null ? "Не удалось создать товар" : "Не удалось обновить товар");
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <p>Загрузка админ-панели...</p>;
  }

  return (
    <section className="stack">
      <div className="card">
        <h1>{editingProductId == null ? "Админ-панель: добавление товара" : `Админ-панель: редактирование #${editingProductId}`}</h1>
        <form className="form" onSubmit={onSubmit}>
          <label>
            Название
            <input type="text" value={payload.name} onChange={(e) => setPayload({ ...payload, name: e.target.value })} required maxLength={180} />
          </label>

          <label>
            Бренд
            <input type="text" value={payload.brand} onChange={(e) => setPayload({ ...payload, brand: e.target.value })} required maxLength={120} />
          </label>

          <label>
            Описание
            <textarea value={payload.description ?? ""} onChange={(e) => setPayload({ ...payload, description: e.target.value })} maxLength={2000} />
          </label>

          <label>
            Категория
            <select value={payload.categoryId} onChange={(e) => setPayload({ ...payload, categoryId: Number(e.target.value) })}>
              {categories.map((category) => (
                <option value={category.id} key={category.id}>
                  {category.name} ({category.slug})
                </option>
              ))}
            </select>
          </label>

          <label>
            Тип компонента
            <select value={payload.componentType} onChange={(e) => setPayload({ ...payload, componentType: e.target.value as ProductComponentType })}>
              {componentTypes.map((type) => (
                <option value={type} key={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label>
            Цена
            <input type="number" min={0.01} step={0.01} value={payload.price} onChange={(e) => setPayload({ ...payload, price: Number(e.target.value) })} required />
          </label>

          <label>
            Валюта
            <input type="text" value={payload.currency} onChange={(e) => setPayload({ ...payload, currency: e.target.value.toUpperCase() })} maxLength={8} required />
          </label>

          <label>
            Количество на складе
            <input type="number" min={0} value={payload.stockQuantity} onChange={(e) => setPayload({ ...payload, stockQuantity: Number(e.target.value) })} required />
          </label>

          <label className="checkbox">
            <input type="checkbox" checked={payload.inStock} onChange={(e) => setPayload({ ...payload, inStock: e.target.checked })} />
            В наличии
          </label>

          <label>
            Socket
            <input type="text" value={payload.socket ?? ""} onChange={(e) => setPayload({ ...payload, socket: e.target.value })} maxLength={40} />
          </label>

          <label>
            Поддерживаемые сокеты (через запятую)
            <input type="text" value={supportedSocketsText} onChange={(e) => setSupportedSocketsText(e.target.value)} placeholder="Например: LGA1700, Socket V" />
          </label>

          <label>
            Тип RAM
            <input type="text" value={payload.ramType ?? ""} onChange={(e) => setPayload({ ...payload, ramType: e.target.value })} maxLength={20} />
          </label>

          <label>
            CPU TDP
            <input type="number" min={0} value={payload.cpuTdp} onChange={(e) => setPayload({ ...payload, cpuTdp: Number(e.target.value) })} />
          </label>

          <label>
            GPU TDP
            <input type="number" min={0} value={payload.gpuTdp} onChange={(e) => setPayload({ ...payload, gpuTdp: Number(e.target.value) })} />
          </label>

          <label>
            Мощность БП (W)
            <input type="number" min={0} value={payload.psuWatts} onChange={(e) => setPayload({ ...payload, psuWatts: Number(e.target.value) })} />
          </label>

          <label className="checkbox">
            <input type="checkbox" checked={payload.supportsWifi} onChange={(e) => setPayload({ ...payload, supportsWifi: e.target.checked })} />
            Поддержка Wi-Fi
          </label>

          <label>
            Оценка для игр (0..10)
            <input type="number" min={0} max={10} step={0.01} value={payload.scoreGaming} onChange={(e) => setPayload({ ...payload, scoreGaming: Number(e.target.value) })} />
          </label>

          <label>
            Оценка для работы (0..10)
            <input type="number" min={0} max={10} step={0.01} value={payload.scoreWork} onChange={(e) => setPayload({ ...payload, scoreWork: Number(e.target.value) })} />
          </label>

          <label>
            Оценка для учебы (0..10)
            <input type="number" min={0} max={10} step={0.01} value={payload.scoreStudy} onChange={(e) => setPayload({ ...payload, scoreStudy: Number(e.target.value) })} />
          </label>

          <label>
            Общая оценка (0..10)
            <input type="number" min={0} max={10} step={0.01} value={payload.scoreGeneral} onChange={(e) => setPayload({ ...payload, scoreGeneral: Number(e.target.value) })} />
          </label>

          <label>
            Примечания (через запятую)
            <input type="text" value={payload.notes ?? ""} onChange={(e) => setPayload({ ...payload, notes: e.target.value })} maxLength={1000} />
          </label>

          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <div className="row">
            <button className="btn btn-primary" type="submit" disabled={submitting}>
              {submitting ? "Сохраняем..." : editingProductId == null ? "Создать товар" : "Сохранить изменения"}
            </button>
            {editingProductId != null && (
              <button className="btn btn-secondary" type="button" onClick={resetForm}>
                Отменить редактирование
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Товары</h2>
        {products.length === 0 ? (
          <p className="muted">Товары не найдены.</p>
        ) : (
          <div className="stack">
            {products.map((product) => (
              <article key={product.id} className="card">
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <strong>
                    #{product.id} {product.name}
                  </strong>
                  <span>
                    {product.price} {product.currency}
                  </span>
                </div>
                <p className="muted">
                  {product.brand} | {product.category.name} | {product.componentType ?? "OTHER"} | Склад: {product.stockQuantity}
                </p>
                <div className="row">
                  <button className="btn btn-secondary" type="button" onClick={() => startEdit(product)}>
                    Редактировать
                  </button>
                  <button className="btn btn-secondary" type="button" onClick={() => void onDelete(product)}>
                    Удалить
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
