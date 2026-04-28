import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/authApi";
import { ApiError } from "../api/http";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { setAuth } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await register({ username, email, password });
      setAuth(response.token, response.user);
      navigate("/catalog", { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Непредвиденная ошибка при регистрации");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="auth-page">
      <h1>Регистрация</h1>
      <form onSubmit={onSubmit} className="card form">
        <label>
          Логин
          <input value={username} onChange={(e) => setUsername(e.target.value)} required minLength={3} />
        </label>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} required type="email" />
        </label>
        <label>
          Пароль
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            type="password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Создаем..." : "Создать аккаунт"}
        </button>
      </form>
      <p>
        Уже зарегистрированы? <Link to="/login">Перейти ко входу</Link>
      </p>
    </section>
  );
}
