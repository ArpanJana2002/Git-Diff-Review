export default function ReviewSummary({ summary, score }) {
  if (!summary) return null;

  const isNoChanges = summary === 'No changes found in the repository.';

  return (
    <section className="review-summary">
      <h2>Review Summary</h2>
      {isNoChanges ? (
        <p className="no-changes">No changes found.</p>
      ) : (
        <>
          <p className="summary-text">{summary}</p>
          <p className="score">
            Score: <strong>{score}/10</strong>
          </p>
        </>
      )}
    </section>
  );
}
