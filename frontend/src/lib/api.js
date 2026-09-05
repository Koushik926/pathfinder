/**
 * Thin API client. Every call returns parsed JSON or throws an Error carrying
 * the backend's `detail` message, so the UI can show something specific
 * instead of a generic failure.
 */

const BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}) {
  const response = await fetch(`${BASE}/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const body = await response.json()
      if (body?.detail) detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch { /* response had no JSON body */ }
    throw new Error(detail)
  }
  return response.json()
}

export const api = {
  meta: () => request('/meta'),
  roles: () => request('/roles'),
  createSession: () => request('/session', { method: 'POST' }),
  chat: (id, message) =>
    request(`/session/${id}/chat`, { method: 'POST', body: JSON.stringify({ message }) }),
  path: (id, refresh = false) => request(`/session/${id}/path${refresh ? '?refresh=true' : ''}`),
  dashboard: (id) => request(`/session/${id}/dashboard`),
  history: (id) => request(`/session/${id}/history`),
  explain: (id, itemId) => request(`/session/${id}/explain/${itemId}`),
  updateProfile: (id, payload) =>
    request(`/session/${id}/profile`, { method: 'PUT', body: JSON.stringify(payload) }),
  feedback: (id, payload) =>
    request(`/session/${id}/feedback`, { method: 'POST', body: JSON.stringify(payload) }),
  search: (q, limit = 12) =>
    request(`/catalog/search?q=${encodeURIComponent(q)}&limit=${limit}`),
}

const SESSION_KEY = 'pathfinder.session'

export function storedSession() {
  try { return localStorage.getItem(SESSION_KEY) } catch { return null }
}

export function storeSession(id) {
  try { localStorage.setItem(SESSION_KEY, id) } catch { /* private mode */ }
}

export function clearSession() {
  try { localStorage.removeItem(SESSION_KEY) } catch { /* private mode */ }
}
