import { useState } from 'react'
import { analyzeResume } from '../api/analyze'
import AnalysisReport from '../components/AnalysisReport'
import ResumeUploadForm from '../components/ResumeUploadForm'

/** Upload a resume and job description, then show the analysis report. */
export default function ResumeReview() {
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleSubmit(input) {
    setStatus('loading')
    setResult(null)
    setError(null)

    try {
      setResult(await analyzeResume(input))
      setStatus('success')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }

  return (
    <>
      <ResumeUploadForm onSubmit={handleSubmit} busy={status === 'loading'} />
      {status === 'error' && <p className="error">{error}</p>}
      {status === 'success' && <AnalysisReport result={result} />}
    </>
  )
}
