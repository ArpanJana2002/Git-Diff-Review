export default function ChangedFiles({ status }) {
  if (!status || !status.trim()) {
    return (
      <section className="changed-files">
        <h2>Changed Files</h2>
        <p className="no-changes">No changes found.</p>
      </section>
    );
  }

  const files = status
    .split('\n')
    .filter((line) => line.trim())
    .map((line) => line.trim().replace(/^\?\?\s+/, '').replace(/^[MADRCU!?]+\s+/, ''));

  return (
    <section className="changed-files">
      <h2>Changed Files</h2>
      <ul className="file-list">
        {files.map((file, index) => (
          <li key={`${file}-${index}`}>
            <span className="checkmark" aria-hidden="true">✓</span> {file}
          </li>
        ))}
      </ul>
    </section>
  );
}
