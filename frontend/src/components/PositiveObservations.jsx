export default function PositiveObservations({ positives }) {
  if (!positives || positives.length === 0) return null;

  return (
    <section className="positive-observations">
      <h2>Positive Observations</h2>
      <ul className="positive-list">
        {positives.map((item, index) => (
          <li key={index}>
            <span className="checkmark" aria-hidden="true">✓</span> {item}
          </li>
        ))}
      </ul>
    </section>
  );
}
