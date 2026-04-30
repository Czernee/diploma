import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { token, user, isReady } = useAuth();
  const location = useLocation();

  if (!isReady) {
    return <p>Проверяем доступ...</p>;
  }

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (user?.role?.toUpperCase() !== "ADMIN") {
    return <Navigate to="/catalog" replace />;
  }

  return <>{children}</>;
}
