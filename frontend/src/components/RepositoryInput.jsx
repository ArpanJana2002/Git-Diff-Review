const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function RepositoryInput({ repository, onRepositoryChange, onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading && repository.trim()) {
      onSubmit();
    }
  };

  return (
    <form className="repository-input" onSubmit={handleSubmit}>
      <label htmlFor="repository-path">Repository Path</label>
      <input
        id="repository-path"
        type="text"
        value={repository}
        onChange={(e) => onRepositoryChange(e.target.value)}
        placeholder="/path/to/repository"
        disabled={loading}
      />
      <button type="submit" disabled={loading || !repository.trim()}>
        {loading ? 'Analyzing...' : 'Review Changes'}
      </button>
    </form>
  );
}

export { API_BASE };
