import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section>
      <h1>Страница не найдена</h1>
      <p>
        Такой страницы нет. <Link to="/">Вернуться на главную</Link>
      </p>
    </section>
  );
}
