// Helper for calling the Crowdsurf backend. Every API call should go through
// this instead of calling fetch() directly.
//
// It adds the /api/v1 prefix, sends the body as JSON, attaches the host or
// guest token if you pass one, and throws an Error with the backend's message
// if the request fails. Example:
//
//   const room = await api("/rooms", { method: "POST", body: { mode: "vote" }, token });
//
// Paths are relative because Vite proxies /api to the backend (see vite.config.js).

const BASE = "/api/v1";

export async function api(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const resp = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    throw new Error(detail.detail ?? `${method} ${path} failed (${resp.status})`);
  }
  return resp.status === 204 ? null : resp.json();
}
