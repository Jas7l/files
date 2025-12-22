import { apiFetch } from "./http";

export async function login(username: string, password: string) {
  const res = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  return res.json(); // { token: "..." }
}

export async function register(username: string, password: string) {
  const res = await apiFetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  return res.json();
}

export async function getMe() {
  const res = await apiFetch("/api/auth/me");
  return res.json();
}
