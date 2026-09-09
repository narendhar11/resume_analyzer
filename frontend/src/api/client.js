const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Unwrap a backend response, throwing an Error carrying the backend's
 * `detail` message on non-2xx.
 */
async function unwrap(response) {
  let body = null

  try {
    body = await response.json()
  } catch {
    // Non-JSON body (network error page, empty 502, ...) — fall through.
  }

  if (!response.ok) {
    const detail = body?.detail || `Request failed with status ${response.status}`
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }

  return body
}

/** GET `path` on the backend. */
export async function apiGet(path) {
  return unwrap(await fetch(`${BASE_URL}${path}`))
}

/**
 * POST multipart form data to `path`. The browser sets the multipart
 * Content-Type (with boundary) itself, so no headers are passed here.
 */
export async function apiPostForm(path, formData) {
  return unwrap(await fetch(`${BASE_URL}${path}`, { method: 'POST', body: formData }))
}
