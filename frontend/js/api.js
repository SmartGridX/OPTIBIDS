// api.js — OPTIBOTS HTTP wrapper with JWT auth

const BASE = 'http://localhost:8000';

async function rawFetch(path, opts = {}) {
  const url = BASE + path;
  const headers = { ...(opts.headers || {}) };

  const token = localStorage.getItem('token');
  if (token) headers.Authorization = `Bearer ${token}`;

  // JSON body unless FormData
  if (opts.body && !(opts.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(url, {
    method: opts.method || 'GET',
    body: opts.body,
    headers,
  });

  // Unauthorized → clear token and redirect to login
  if (res.status === 401) {
    localStorage.removeItem('token');
    if (!window.location.pathname.includes('login')) {
      window.location.href = '/login.html';
    }
    throw new Error('Unauthorized');
  }

  // Non-2xx errors
  if (!res.ok) {
    let errMsg = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      errMsg = data.detail || JSON.stringify(data) || errMsg;
    } catch {}
    throw new Error(errMsg);
  }

  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res.text();
}

window.api = {
  get:    (path)        => rawFetch(path, { method: 'GET' }),
  post:   (path, body)  => rawFetch(path, {
    method: 'POST',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  upload: (path, form)  => rawFetch(path, { method: 'POST', body: form }),
};
