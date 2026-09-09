import { useState } from 'react'
import { pingGemini } from '../api/ping'

/**
 * One button that exercises the whole stack: frontend -> backend -> Gemini.
 * Renders the live reply on success, or the backend's error detail on failure.
 */
export default function GeminiPingCard() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleClick() {
    setStatus('loading')
    setResult(null)
    setError(null)

    try {
      setResult(await pingGemini())
      setStatus('success')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }

  return (
    <section className="card">
      <h2>Gemini connectivity check</h2>
      <p className="muted">
        Sends a hardcoded prompt through the FastAPI backend to the Gemini API.
      </p>

      <button onClick={handleClick} disabled={status === 'loading'}>
        {status === 'loading' ? 'Calling Gemini…' : 'Ping Gemini'}
      </button>

      {status === 'success' && (
        <div className="result">
          <p className="muted">Model: {result.model}</p>
          <p className="muted">Prompt: {result.prompt}</p>
          <pre>{result.reply}</pre>
        </div>
      )}

      {status === 'error' && <p className="error">{error}</p>}
    </section>
  )
}
