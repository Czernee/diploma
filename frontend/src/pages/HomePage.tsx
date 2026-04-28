import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">Интерфейс дипломного проекта</p>
      <h1>Микросервисный магазин комплектующих с ИИ-помощником сборки ПК</h1>
      <p>
        Просматривайте каталог, оформляйте заказы и генерируйте готовую конфигурацию ПК через уже подключенные
        backend-сервисы.
      </p>
      <div className="row">
        <Link to="/catalog" className="btn btn-primary">
          Открыть каталог
        </Link>
        <Link to="/configurator" className="btn btn-secondary">
          Запустить конфигуратор
        </Link>
      </div>
    </section>
  );
}
