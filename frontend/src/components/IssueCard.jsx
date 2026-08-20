const SEVERITY_CLASS = {
  CRITICAL: 'severity-critical',
  HIGH: 'severity-high',
  MEDIUM: 'severity-medium',
  LOW: 'severity-low',
  INFO: 'severity-info',
};

export default function IssueCard({ issue }) {
  const severityClass = SEVERITY_CLASS[issue.severity] || 'severity-info';
  const location = issue.line ? `${issue.file}:${issue.line}` : issue.file;

  return (
    <article className={`issue-card ${severityClass}`}>
      <div className="issue-header">
        <span className="severity-badge">{issue.severity}</span>
        <span className="category-badge">{issue.category}</span>
      </div>
      <p className="issue-location">{location}</p>
      <p className="issue-message">{issue.message}</p>
      <div className="issue-suggestion">
        <strong>Suggestion:</strong>
        <p>{issue.suggestion}</p>
      </div>
    </article>
  );
}
