import { FormEvent, useState } from "react";
import { recommendConfiguration } from "../api/configuratorApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";
import type { ConfiguratorRequest, ConfiguratorResponse, Purpose } from "../types";

const defaultPayload: ConfiguratorRequest = {
  budget: 100000,
  purpose: "gaming",
  preferred_brand: "any",
  needs_wifi: false,
  target_resolution: "1080p"
};

const purposes: Purpose[] = ["gaming", "work", "study", "general"];
const purposeLabels: Record<Purpose, string> = {
  gaming: "Игры",
  work: "Работа",
  study: "Учеба",
  general: "Универсальная"
};

const performanceLabels: Record<string, string> = {
  entry: "Начальный",
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
  const [payload, setPayload] = useState<ConfiguratorRequest>(defaultPayload);
  const [result, setResult] = useState<ConfiguratorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      setError("Войдите в аккаунт, чтобы пользоваться конфигуратором");
      return;
    }

    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const response = await recommendConfiguration(token, payload);
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Не удалось сгенерировать конфигурацию");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>ИИ-конфигуратор</h1>
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
          <select
            value={payload.purpose}
            onChange={(e) => setPayload({ ...payload, purpose: e.target.value as Purpose })}
          >
            {purposes.map((purpose) => (
              <option value={purpose} key={purpose}>
                {purposeLabels[purpose]}
              </option>
            ))}
          </select>
        </label>

        <label>
          Предпочитаемый бренд
          <select
            value={payload.preferred_brand}
            onChange={(e) =>
              setPayload({
                ...payload,
                preferred_brand: e.target.value as ConfiguratorRequest["preferred_brand"]
              })
            }
          >
            <option value="any">любой</option>
            <option value="intel">intel</option>
            <option value="amd">amd</option>
            <option value="nvidia">nvidia</option>
          </select>
        </label>

        <label>
          Целевое разрешение
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

        <label className="checkbox">
          <input
            type="checkbox"
            checked={payload.needs_wifi}
            onChange={(e) => setPayload({ ...payload, needs_wifi: e.target.checked })}
          />
          Нужен Wi-Fi
        </label>

        {error && <p className="error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Генерируем..." : "Сгенерировать конфигурацию"}
        </button>
      </form>

      {result && (
        <section className="card">
          <h2>Результат конфигурации</h2>
          <p>
            Уровень производительности: <strong>{performanceLabels[result.performance_estimate]}</strong>
          </p>
          <p>
            Итого: <strong>{result.total_price} RUB</strong>
          </p>
          <ul>
            {result.components.map((component) => (
              <li key={`${component.type}-${component.model}`}>
                {formatComponentType(component.type)}: {component.model} ({component.brand}) - {component.price} RUB
              </li>
            ))}
          </ul>
        </section>
      )}
    </section>
  );
}
