import ReportSection from './ReportSection'

// Accent for each fit tier. Keyed off the label rather than re-deriving
// tiers from the score, so the colour can never disagree with the text.
const TIER_CLASS = {
  'Strong fit': 'strong',
  'Moderate fit': 'moderate',
  'Weak fit': 'weak',
}

/** Renders a completed analysis: headline score, summary, then the lists. */
export default function AnalysisReport({ result }) {
  const { report, model, resume_filename, jd_source } = result

  return (
    <article className="card report">
      <header className={`score score-${TIER_CLASS[report.fit_label] ?? 'moderate'}`}>
        <span className="score-value">{report.fit_score}</span>
        <span className="score-meta">
          <strong>{report.fit_label}</strong>
          <span className="muted">out of 100</span>
        </span>
      </header>

      <p>{report.summary}</p>

      <ReportSection
        title="Strengths"
        items={report.strengths}
        emptyText="No clear strengths matched this job description."
      />
      <ReportSection
        title="Missing keywords"
        items={report.missing_keywords}
        emptyText="Nothing significant from the job description is missing."
      />
      <ReportSection
        title="Skill gaps"
        items={report.skill_gaps}
        emptyText="No notable skill gaps found."
      />
      <ReportSection
        title="Recommendations"
        items={report.recommendations}
        emptyText="No changes suggested."
      />

      <footer className="muted">
        {resume_filename} · job description from {jd_source} · analyzed by {model}
      </footer>
    </article>
  )
}
