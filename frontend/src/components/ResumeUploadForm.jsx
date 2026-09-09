import { useState } from 'react'

const RESUME_ACCEPT = '.pdf,.md'
const JD_ACCEPT = '.pdf,.md,.txt'

/**
 * Collects a resume file and a job description — pasted or uploaded — and
 * hands them to `onSubmit`. Submission is blocked until both are present.
 */
export default function ResumeUploadForm({ onSubmit, busy }) {
  const [resumeFile, setResumeFile] = useState(null)
  const [jdMode, setJdMode] = useState('paste')
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState(null)

  const usingFile = jdMode === 'file'
  const hasJd = usingFile ? Boolean(jdFile) : jdText.trim().length > 0
  const canSubmit = Boolean(resumeFile) && hasJd && !busy

  function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) return
    onSubmit({
      resumeFile,
      jdText,
      jdFile: usingFile ? jdFile : null,
    })
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <label className="field">
        <span className="field-label">Resume</span>
        <input
          type="file"
          accept={RESUME_ACCEPT}
          onChange={(event) => setResumeFile(event.target.files[0] ?? null)}
        />
        <span className="muted">PDF or Markdown, up to 5 MB.</span>
      </label>

      <fieldset className="field">
        <legend className="field-label">Job description</legend>

        <div className="toggle">
          <label>
            <input
              type="radio"
              name="jdMode"
              value="paste"
              checked={!usingFile}
              onChange={() => setJdMode('paste')}
            />
            Paste text
          </label>
          <label>
            <input
              type="radio"
              name="jdMode"
              value="file"
              checked={usingFile}
              onChange={() => setJdMode('file')}
            />
            Upload file
          </label>
        </div>

        {usingFile ? (
          <>
            <input
              type="file"
              accept={JD_ACCEPT}
              onChange={(event) => setJdFile(event.target.files[0] ?? null)}
            />
            <span className="muted">PDF, Markdown or plain text.</span>
          </>
        ) : (
          <textarea
            rows={10}
            value={jdText}
            placeholder="Paste the job description here…"
            onChange={(event) => setJdText(event.target.value)}
          />
        )}
      </fieldset>

      <button type="submit" disabled={!canSubmit}>
        {busy ? 'Analyzing…' : 'Analyze resume'}
      </button>
    </form>
  )
}
