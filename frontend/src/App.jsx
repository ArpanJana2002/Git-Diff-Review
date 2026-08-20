import { useState } from 'react';
import RepositoryInput, { API_BASE } from './components/RepositoryInput';
import ChangedFiles from './components/ChangedFiles';
import ReviewSummary from './components/ReviewSummary';
import IssueCard from './components/IssueCard';
import PositiveObservations from './components/PositiveObservations';
import './App.css';

function App() {
  const [repository, setRepository] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [review, setReview] = useState(null);

  const handleReview = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    setReview(null);

    try {
      const [statusRes, reviewRes] = await Promise.all([
        fetch(`${API_BASE}/api/status?repository=${encodeURIComponent(repository.trim())}`),
        fetch(`${API_BASE}/api/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repository: repository.trim() }),
        }),
      ]);

      if (!statusRes.ok) {
        const errData = await statusRes.json().catch(() => ({}));
        throw new Error(errData.detail || 'Unable to retrieve repository status.');
      }

      if (!reviewRes.ok) {
        const errData = await reviewRes.json().catch(() => ({}));
        throw new Error(errData.detail || 'Unable to review repository.');
      }

      const statusData = await statusRes.json();
      const reviewData = await reviewRes.json();

      setStatus(statusData.status);
      setReview(reviewData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Git Diff Reviewer</h1>
        <p className="subtitle">Review your Git changes locally.</p>
      </header>

      <main className="main">
        <RepositoryInput
          repository={repository}
          onRepositoryChange={setRepository}
          onSubmit={handleReview}
          loading={loading}
        />

        {loading && (
          <div className="loading-state" role="status">
            Analyzing Git changes...
          </div>
        )}

        {error && (
          <div className="error-state" role="alert">
            <p className="error-title">Unable to review repository.</p>
            <p className="error-detail">{error}</p>
          </div>
        )}

        {!loading && !error && review && (
          <div className="results">
            <ChangedFiles status={status} />
            <ReviewSummary summary={review.summary} score={review.overall_score} />

            {review.issues.length > 0 && (
              <section className="issues-section">
                <h2>Issues Found ({review.issues.length})</h2>
                <div className="issues-list">
                  {review.issues.map((issue, index) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
                </div>
              </section>
            )}

            <PositiveObservations positives={review.positives} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
