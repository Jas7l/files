import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await login(username, password);
      navigate("/app");
    } catch (err: any) {
      setError(err.message || "Ошибка входа");
    }
  };

  return (
    <div style={styles.page}>
      <form onSubmit={handleSubmit} style={styles.card}>
        <h2>Вход</h2>

        {error && <div style={styles.error}>{error}</div>}

        <input
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          style={styles.input}
        />

        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={styles.input}
        />

        <button style={styles.button}>
          Войти
        </button>

        <div style={styles.footer}>
          Нет аккаунта? <Link to="/register">Регистрация</Link>
        </div>
      </form>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f7f6",
  },
  card: {
    width: 320,
    padding: 24,
    background: "#fff",
    borderRadius: 8,
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  input: {
    padding: 10,
    fontSize: 14,
  },
  button: {
    padding: 10,
    background: "#4caf50",
    color: "#fff",
    border: "none",
    cursor: "pointer",
  },
  error: {
    color: "red",
    fontSize: 13,
  },
  footer: {
    fontSize: 13,
    textAlign: "center",
  },
};
