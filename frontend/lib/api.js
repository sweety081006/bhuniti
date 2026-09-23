export const API = process.env.NEXT_PUBLIC_API_URL || "https://exs-dapps1k9v7es739gqe90.onrender.com";

function authHeaders() {
  if (typeof window === "undefined") return {};
  const t = localStorage.getItem("bhuniti_token");
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export async function get(path) {
  const r = await fetch(`${API}${path}`, { headers: { ...authHeaders() }, cache: "no-store" });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

export async function post(path, body) {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

export async function login(email, password) {
  const form = new URLSearchParams({ username: email, password });
  const r = await fetch(`${API}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });
  if (!r.ok) throw new Error("Incorrect email or password");
  const data = await r.json();
  localStorage.setItem("bhuniti_token", data.access_token);
  localStorage.setItem("bhuniti_user", JSON.stringify(data.user));
  return data.user;
}

export function logout() {
  localStorage.removeItem("bhuniti_token");
  localStorage.removeItem("bhuniti_user");
}

export function currentUser() {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("bhuniti_user");
  return raw ? JSON.parse(raw) : null;
}

export const inr = (n) =>
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(n || 0);
