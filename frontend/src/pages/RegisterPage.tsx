import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register as registerApi } from "../api/auth";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== password2) {
      setError("Пароли не совпадают");
      return;
    }

    setLoading(true);
    try {
      await registerApi(username, password);
      navigate("/login");
    } catch (err: any) {
      setError(err.message || "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <form onSubmit={handleSubmit} style={styles.card}>
        <h2>Регистрация</h2>

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

        <input
          type="password"
          placeholder="Повторите пароль"
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
          required
          style={styles.input}
        />

        <button disabled={loading} style={styles.button}>
          {loading ? "Создание..." : "Создать аккаунт"}
        </button>

        <div style={styles.footer}>
          Уже есть аккаунт? <Link to="/login">Войти</Link>
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
