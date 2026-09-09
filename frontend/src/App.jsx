import ResumeReview from './pages/ResumeReview'

export default function App() {
  return (
    <main className="app">
      <h1>Resume Analyzer</h1>
      <p className="muted">
        Upload a resume and a job description to get a fitment score and
        recommendations.
      </p>
      <ResumeReview />
    </main>
  )
}
