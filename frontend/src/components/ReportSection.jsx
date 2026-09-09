/**
 * A titled bullet list from the report. Renders a placeholder line instead
 * of an empty list, since "nothing missing" is a meaningful result.
 */
export default function ReportSection({ title, items, emptyText }) {
  return (
    <section className="report-section">
      <h3>{title}</h3>
      {items?.length ? (
        <ul>
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">{emptyText}</p>
      )}
    </section>
  )
}
