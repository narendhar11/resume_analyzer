import { apiPostForm } from './client'

/**
 * Send a resume file plus a job description (pasted text or an uploaded
 * file) to the backend and return the analysis report.
 */
export function analyzeResume({ resumeFile, jdText, jdFile }) {
  const formData = new FormData()
  formData.append('resume', resumeFile)

  if (jdFile) {
    formData.append('jd_file', jdFile)
  } else {
    formData.append('jd_text', jdText)
  }

  return apiPostForm('/api/analyze', formData)
}
