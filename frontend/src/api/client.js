const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Thin fetch wrapper around the backend API.
 * Throws an Error carrying the backend's `detail` message on non-2xx.
 */
export async function apiGet(path) {
  const response = await fetch(`${BASE_URL}${path}`)
  let body = null

  try {
    body = await response.json()
  } catch {
    // Non-JSON body (network error page, empty 502, ...) — fall through.
  }

  if (!response.ok) {
    const detail = body?.detail || `Request failed with status ${response.status}`
    throw new Error(detail)
  }

  return body
}
