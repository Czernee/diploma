import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function AppLayout() {
  const { user, logout } = useAuth();
  const { items } = useCart();

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          Магазин комплектующих
        </Link>
        <nav className="nav">
          <NavLink to="/catalog">Каталог</NavLink>
          <NavLink to="/configurator">ИИ-конфигуратор</NavLink>
          <NavLink to="/orders">Заказы</NavLink>
          <NavLink to="/cart">Корзина ({items.length})</NavLink>
        </nav>
        <div className="authbox">
          {user ? (
            <>
              <span>{user.username}</span>
              <button className="btn btn-secondary" onClick={logout}>
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-secondary">
                Вход
              </Link>
              <Link to="/register" className="btn btn-primary">
                Регистрация
              </Link>
            </>
          )}
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
