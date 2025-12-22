// Header.tsx
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header style={styles.header}>
      <h1 style={styles.title}>Облачное хранилище</h1>
      {user && (
        <div style={styles.userBlock}>
          <span style={styles.username}>{user.username}</span>
          <button onClick={handleLogout} style={styles.button}>Выйти</button>
        </div>
      )}
    </header>
  );
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    width: "100%",
    height: 60,
    padding: "0 16px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#4caf50",
    color: "#fff",
    boxSizing: "border-box",
    flexShrink: 0,
  },
  title: { margin: 0, fontSize: 20 },
  userBlock: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    flexShrink: 0,
  },
  username: { fontWeight: "bold" },
  button: {
    padding: "6px 12px",
    backgroundColor: "#fff",
    color: "#4caf50",
    border: "none",
    borderRadius: 4,
    cursor: "pointer",
    flexShrink: 0,
  },
};
