import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { recommendConfiguration } from "../api/configuratorApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import type { ConfigurationVariant, ConfiguratorRequest, ConfiguratorResponse, Purpose } from "../types";

const defaultPayload: ConfiguratorRequest = {
  budget: 100000,
  purpose: "gaming",
  preferred_brand: "any",
  needs_wifi: false,
  target_resolution: "1080p",
  minimum_performance: null,
  cpu_brand_preference: "any",
  gpu_brand_preference: "any",
  min_ram_gb: 0,
  min_vram_gb: 0
};

const purposes: Purpose[] = ["gaming", "work", "study", "general"];
const purposeLabels: Record<Purpose, string> = {
  gaming: "Игры",
  work: "Работа",
  study: "Учеба",
  general: "Универсальная"
};

const performanceLabels: Record<string, string> = {
  entry: "Базовый",
  mid: "Средний",
  high: "Высокий"
};

const componentTypeLabels: Record<string, string> = {
  cpu: "Процессор",
  gpu: "Видеокарта",
  motherboard: "Материнская плата",
  ram: "Оперативная память",
  storage: "Накопитель",
  psu: "Блок питания",
  case: "Корпус"
};

function formatComponentType(type: string): string {
  return componentTypeLabels[type.toLowerCase()] ?? type.toUpperCase();
}

export function ConfiguratorPage() {
  const { token } = useAuth();
  const { addItem } = useCart();
  const navigate = useNavigate();

  const [payload, setPayload] = useState<ConfiguratorRequest>(defaultPayload);
  const [result, setResult] = useState<ConfiguratorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cartMessage, setCartMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function addComponentToCart(component: ConfigurationVariant["components"][number], variantLabel: string) {
    if (!component.product_id) {
      setCartMessage(`Не удалось добавить «${component.model}»: у товара нет ID в каталоге.`);
      return;
    }
    addItem(
      {
        productId: component.product_id,
        productName: component.model,
        unitPrice: component.price,
        currency: "RUB"
      },
      1
    );
    setCartMessage(`Добавлено в корзину (${variantLabel}): ${component.model}`);
  }

  function addAllComponentsToCartFromVariant(variant: ConfigurationVariant, variantLabel: string): number {
    const addable = variant.components.filter((component) => component.product_id);
    if (addable.length === 0) {
      setCartMessage("В этой конфигурации нет компонентов, связанных с товарами каталога.");
      return 0;
    }

    addable.forEach((component) => {
      addItem(
        {
          productId: component.product_id as number,
          productName: component.model,
          unitPrice: component.price,
          currency: "RUB"
        },
        1
      );
    });

    setCartMessage(`Добавлено в корзину (${variantLabel}) компонентов: ${addable.length}`);
    return addable.length;
  }

  function checkoutVariant(variant: ConfigurationVariant, variantLabel: string) {
    const added = addAllComponentsToCartFromVariant(variant, variantLabel);
    if (added > 0) {
      navigate("/cart");
    }
  }

  function renderVariant(title: string, variant: ConfigurationVariant, labelForCart: string) {
    return (
      <section className="card">
        <h2>{title}</h2>
        <p>
          Уровень производительности: <strong>{performanceLabels[variant.performance_estimate]}</strong>
        </p>
        <p>
          Итого: <strong>{variant.total_price} RUB</strong>
        </p>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <button className="btn btn-primary" type="button" onClick={() => addAllComponentsToCartFromVariant(variant, labelForCart)}>
            Добавить этот комплект в корзину
          </button>
          <button className="btn btn-secondary" type="button" onClick={() => checkoutVariant(variant, labelForCart)}>
            Оформить этот комплект
          </button>
        </div>

        <ul>
          {variant.components.map((component) => (
            <li key={`${title}-${component.type}-${component.model}`}>
              {formatComponentType(component.type)}: {component.model} ({component.brand}) - {component.price} RUB{" "}
              <button className="btn btn-secondary" type="button" onClick={() => addComponentToCart(component, labelForCart)}>
                В корзину
              </button>
            </li>
          ))}
        </ul>
      </section>
    );
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setError("Войдите в аккаунт, чтобы пользоваться ИИ-конфигуратором.");
      return;
    }

    setError(null);
    setCartMessage(null);
    setResult(null);
    setLoading(true);

    try {
      const response = await recommendConfiguration(token, payload);
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось сгенерировать конфигурацию.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="stack">
      <section>
        <h1>ИИ-конфигуратор ПК</h1>
        <form className="card form" onSubmit={onSubmit}>
          <label>
            Бюджет (RUB)
            <input
              type="number"
              min={30000}
              max={600000}
              value={payload.budget}
              onChange={(e) => setPayload({ ...payload, budget: Number(e.target.value) })}
            />
          </label>

          <label>
            Цель
            <select value={payload.purpose} onChange={(e) => setPayload({ ...payload, purpose: e.target.value as Purpose })}>
              {purposes.map((purpose) => (
                <option value={purpose} key={purpose}>
                  {purposeLabels[purpose]}
                </option>
              ))}
            </select>
          </label>

          <label>
            Разрешение
            <select
              value={payload.target_resolution}
              onChange={(e) =>
                setPayload({
                  ...payload,
                  target_resolution: e.target.value as ConfiguratorRequest["target_resolution"]
                })
              }
            >
              <option value="1080p">1080p</option>
              <option value="1440p">1440p</option>
              <option value="4k">4k</option>
            </select>
          </label>

          <label>
            Минимальный уровень производительности
            <select
              value={payload.minimum_performance ?? ""}
              onChange={(e) =>
                setPayload({
                  ...payload,
                  minimum_performance: e.target.value
                    ? (e.target.value as NonNullable<ConfiguratorRequest["minimum_performance"]>)
                    : null
                })
              }
            >
              <option value="">Без ограничения</option>
              <option value="entry">Базовый</option>
              <option value="mid">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </label>

          <label>
            Минимум RAM (ГБ)
            <input
              type="number"
              min={0}
              max={256}
              value={payload.min_ram_gb ?? 0}
              onChange={(e) => setPayload({ ...payload, min_ram_gb: Number(e.target.value) })}
            />
          </label>

          <label>
            Минимум VRAM видеокарты (ГБ)
            <input
              type="number"
              min={0}
              max={64}
              value={payload.min_vram_gb ?? 0}
              onChange={(e) => setPayload({ ...payload, min_vram_gb: Number(e.target.value) })}
            />
          </label>

          <label>
            Предпочтение бренда CPU
            <select
              value={payload.cpu_brand_preference ?? "any"}
              onChange={(e) =>
                setPayload({
                  ...payload,
                  cpu_brand_preference: e.target.value as NonNullable<ConfiguratorRequest["cpu_brand_preference"]>
                })
              }
            >
              <option value="any">Любой</option>
              <option value="intel">Intel</option>
              <option value="amd">AMD</option>
            </select>
          </label>

          <label>
            Предпочтение бренда GPU
            <select
              value={payload.gpu_brand_preference ?? "any"}
              onChange={(e) =>
                setPayload({
                  ...payload,
                  gpu_brand_preference: e.target.value as NonNullable<ConfiguratorRequest["gpu_brand_preference"]>
                })
              }
            >
              <option value="any">Любой</option>
              <option value="nvidia">NVIDIA</option>
              <option value="amd">AMD</option>
              <option value="intel">Intel</option>
            </select>
          </label>

          <label className="checkbox">
            <input
              type="checkbox"
              checked={payload.needs_wifi}
              onChange={(e) => setPayload({ ...payload, needs_wifi: e.target.checked })}
            />
            Нужен Wi-Fi на материнской плате
          </label>

          {error && <p className="error">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Подбираем конфигурацию..." : "Подобрать конфигурацию"}
          </button>
        </form>
      </section>

      {cartMessage && <p>{cartMessage}</p>}

      {result && (
        <>
          {renderVariant("Основная конфигурация", result, "основная")}
          {result.alternatives?.cheaper && renderVariant("Альтернатива: подешевле", result.alternatives.cheaper, "подешевле")}
          {result.alternatives?.pricier && renderVariant("Альтернатива: подороже", result.alternatives.pricier, "подороже")}
        </>
      )}
    </section>
  );
}
