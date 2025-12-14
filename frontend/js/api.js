// api.js — safe HTTP wrapper with correct token injection

const BASE = "http://localhost:8000";

async function rawFetch(path, opts = {}) {
  const url = BASE + path;

  const headers = { ...(opts.headers || {}) };

  // Inject token
  const token = localStorage.getItem("token");
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  // JSON body handling (do NOT touch FormData)
  if (opts.body && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url, {
    method: opts.method || "GET",
    body: opts.body,
    headers
  });

  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login.html";
    throw new Error("Unauthorized");
  }

  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    return res.json();
  }

  return res.text();
}

window.api = {
  get: (path) => rawFetch(path, { method: "GET" }),
  post: (path, body) =>
    rawFetch(path, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body),
    }),
  upload: (path, formData) =>
    rawFetch(path, {
      method: "POST",
      body: formData,
    }),
};
