import { apiGet } from './client'

/** Ask the backend to call Gemini with its hardcoded smoke-test prompt. */
export function pingGemini() {
  return apiGet('/api/ping-gemini')
}
