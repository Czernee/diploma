import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { askConfiguratorAssistant, recommendConfiguration } from "../api/configuratorApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import type {
  ConfigurationVariant,
  ConfiguratorAssistantResponse,
  ConfiguratorRequest,
  ConfiguratorResponse,
  Purpose
} from "../types";

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

function formatPercent(value: number | undefined): string {
  return `${Math.round((value ?? 0) * 100)}%`;
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
  const [cartLoading, setCartLoading] = useState(false);
  const [assistantMessage, setAssistantMessage] = useState(
    "Собери игровой ПК до 120000 рублей для 1440p, минимум 32 ГБ RAM, желательно NVIDIA."
  );
  const [assistantAnswer, setAssistantAnswer] = useState<ConfiguratorAssistantResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState(false);

  async function addComponentToCart(component: ConfigurationVariant["components"][number], variantLabel: string) {
    if (!component.product_id) {
      setCartMessage(`Не удалось добавить "${component.model}": у товара нет ID в каталоге.`);
      return;
    }

    setCartLoading(true);
    try {
      await addItem(
        {
          productId: component.product_id,
          productName: component.model,
          unitPrice: component.price,
          currency: "RUB"
        },
        1
      );
      setCartMessage(`Добавлено в корзину (${variantLabel}): ${component.model}`);
    } catch {
      setCartMessage(`Не удалось добавить "${component.model}" в корзину. Попробуйте еще раз.`);
    } finally {
      setCartLoading(false);
    }
  }

  async function addAllComponentsToCartFromVariant(variant: ConfigurationVariant, variantLabel: string): Promise<number> {
    const addable = variant.components.filter((component) => component.product_id);
    if (addable.length === 0) {
      setCartMessage("В этой конфигурации нет компонентов, связанных с товарами каталога.");
      return 0;
    }

    setCartLoading(true);
    try {
      for (const component of addable) {
        await addItem(
          {
            productId: component.product_id as number,
            productName: component.model,
            unitPrice: component.price,
            currency: "RUB"
          },
          1
        );
      }

      setCartMessage(`Добавлено в корзину (${variantLabel}) компонентов: ${addable.length}`);
      return addable.length;
    } catch {
      setCartMessage("Не удалось добавить весь комплект в корзину. Попробуйте еще раз.");
      return 0;
    } finally {
      setCartLoading(false);
    }
  }

  async function checkoutVariant(variant: ConfigurationVariant, variantLabel: string) {
    const added = await addAllComponentsToCartFromVariant(variant, variantLabel);
    if (added > 0) {
      navigate("/cart");
    }
  }

  function renderVariant(title: string, variant: ConfigurationVariant, labelForCart: string) {
    return (
      <section className="card configurator-result">
        <div className="order-head">
          <div>
            <h2>{title}</h2>
            <p className="muted">
              Подбор выполнен гибридным модулем: правила совместимости + ML-ранжирование.
            </p>
          </div>
          <div className="ml-score">
            <span>Оценка соответствия</span>
            <strong>{formatPercent(variant.ml_score)}</strong>
          </div>
        </div>

        <div className="configurator-summary">
          <p>
            Производительность: <strong>{performanceLabels[variant.performance_estimate]}</strong>
          </p>
          <p>
            Итоговая стоимость: <strong>{variant.total_price} RUB</strong>
          </p>
          <p>
            Бюджет: <strong>{variant.budget} RUB</strong>
          </p>
        </div>

        <div className="ml-meter" aria-label={`Оценка соответствия ${formatPercent(variant.ml_score)}`}>
          <span style={{ width: formatPercent(variant.ml_score) }} />
        </div>

        <div className="row">
          <button
            className="btn btn-primary"
            type="button"
            disabled={cartLoading}
            onClick={() => void addAllComponentsToCartFromVariant(variant, labelForCart)}
          >
            {cartLoading ? "Добавляем комплект..." : "Добавить комплект в корзину"}
          </button>
          <button
            className="btn btn-secondary"
            type="button"
            disabled={cartLoading}
            onClick={() => void checkoutVariant(variant, labelForCart)}
          >
            {cartLoading ? "Добавляем комплект..." : "Оформить этот комплект"}
          </button>
        </div>

        <div className="configuration-grid">
          {variant.components.map((component) => (
            <article className="component-card" key={`${title}-${component.type}-${component.model}`}>
              <p className="product-category">{formatComponentType(component.type)}</p>
              <h3>{component.model}</h3>
              <p className="muted">{component.brand}</p>
              <p>
                <strong>{component.price} RUB</strong>
              </p>
              <p className="muted">Оценка компонента: {component.score.toFixed(2)}</p>
              <button
                className="btn btn-secondary"
                type="button"
                disabled={cartLoading}
                onClick={() => void addComponentToCart(component, labelForCart)}
              >
                В корзину
              </button>
            </article>
          ))}
        </div>

        <details className="configurator-details">
          <summary>Почему выбрана эта конфигурация</summary>
          <ul>
            {variant.explanation.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </details>

        <details className="configurator-details">
          <summary>Проверки совместимости</summary>
          <ul>
            {variant.compatibility_checks.map((check) => (
              <li key={check}>{check}</li>
            ))}
          </ul>
        </details>
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

  async function onAssistantSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setError("Войдите в аккаунт, чтобы пользоваться ИИ-чатом конфигуратора.");
      return;
    }

    setError(null);
    setCartMessage(null);
    setAssistantAnswer(null);
    setAssistantLoading(true);

    try {
      const response = await askConfiguratorAssistant(token, { message: assistantMessage });
      setAssistantAnswer(response);
      if (response.extracted_request) {
        setPayload(response.extracted_request);
      }
      if (response.recommendation) {
        setResult(response.recommendation);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось получить ответ ИИ-помощника.");
      }
    } finally {
      setAssistantLoading(false);
    }
  }

  return (
    <section className="stack">
      <section>
        <h1>ИИ-конфигуратор ПК</h1>
        <p className="muted">
          Опишите задачу обычным языком или заполните форму вручную. LLM понимает запрос пользователя, а подбор реальных товаров выполняет модуль правил совместимости и ML-ранжирования.
        </p>

        <section className="card assistant-card">
          <div>
            <h2>Чат с LLM-помощником</h2>
            <p className="muted">
              Можно спросить совет или попросить собрать ПК: например, для игр, работы, учебы, 1440p, с нужным объемом RAM и VRAM.
            </p>
          </div>

          <form className="assistant-form" onSubmit={onAssistantSubmit}>
            <label>
              Запрос обычным языком
              <textarea
                value={assistantMessage}
                onChange={(e) => setAssistantMessage(e.target.value)}
                placeholder="Например: собери игровой ПК до 120000 рублей"
              />
            </label>
            <button className="btn btn-primary" type="submit" disabled={assistantLoading || !assistantMessage.trim()}>
              {assistantLoading ? "LLM анализирует запрос..." : "Спросить ИИ"}
            </button>
          </form>

          {assistantAnswer && (
            <div className="assistant-answer">
              <p>{assistantAnswer.answer}</p>
              <p className="assistant-meta">
                Режим: {assistantAnswer.mode === "recommendation" ? "подбор конфигурации" : "ответ на вопрос"}
                {assistantAnswer.llm_model ? ` · модель: ${assistantAnswer.llm_model}` : ""}
              </p>
            </div>
          )}
        </section>

        <form className="card form configurator-form" onSubmit={onSubmit}>
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
            Предпочтение CPU
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
            Предпочтение GPU
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

      {cartMessage && <p className="success">{cartMessage}</p>}

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
