import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">Интерфейс дипломного проекта</p>
      <h1>Микросервисный магазин комплектующих с ИИ-помощником для сборки ПК</h1>
      <p>
        Просматривайте каталог, оформляйте заказы и подбирайте конфигурацию ПК через подключенные backend-сервисы.
      </p>
      <div className="row">
        <Link to="/catalog" className="btn btn-primary">
          Открыть каталог
        </Link>
        <Link to="/configurator" className="btn btn-secondary">
          Запустить ИИ-конфигуратор
        </Link>
      </div>
    </section>
  );
}
