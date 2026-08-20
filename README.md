# Git Diff Reviewer

A local-first web application that analyzes changes in a Git repository and provides automated code review findings using a mock reviewer (with future support for Ollama + local LLM).

## Features

- Accept a local Git repository path
- Detect current Git changes (`git status --short`)
- Extract working-tree diff (`git diff`)
- Analyze changes with a deterministic mock reviewer
- Return structured code-review findings (issues, positives, score)
- Display results in a clean React web UI

## Architecture

```
React Frontend
       |
       | HTTP/JSON
       v
FastAPI Backend
       |
       +----------------+
       |                |
       v                v
Git Service       Reviewer Service
       |                |
       v                v
   Git CLI          Mock LLM
                         |
                         |
                  Future: Ollama
```

## Tech Stack

| Layer    | Technology              |
|----------|-------------------------|
| Frontend | React, Vite, JavaScript |
| Backend  | Python, FastAPI, Pydantic |
| Git      | Git CLI via subprocess  |
| Reviewer | MockReviewer (MVP)      |
| Testing  | pytest                  |

## Project Structure

```
GIT_DIFF_REVIEWER/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── review.py
│   │   ├── git/
│   │   │   ├── repository.py
│   │   │   └── diff.py
│   │   ├── reviewer/
│   │   │   ├── base.py
│   │   │   └── mock.py
│   │   └── schemas/
│   │       └── review.py
│   ├── tests/
│   │   ├── test_git.py
│   │   ├── test_reviewer.py
│   │   └── test_api.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RepositoryInput.jsx
│   │   │   ├── ChangedFiles.jsx
│   │   │   ├── ReviewSummary.jsx
│   │   │   ├── IssueCard.jsx
│   │   │   └── PositiveObservations.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

## Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Frontend Setup

```bash
cd frontend
npm install
```

## How to Run

Start the backend (from `backend/` directory):

```bash
uvicorn app.main:app --reload --port 8000
```

Start the frontend (from `frontend/` directory):

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Example Usage

1. Make some changes in a local Git repository (e.g., add a `TODO` comment or `print()` statement).
2. Open the web app at `http://localhost:5173`.
3. Enter the absolute path to your repository (e.g., `C:\Users\you\projects\my-app`).
4. Click **Review Changes**.
5. View changed files, review summary, score, detected issues, and positive observations.

### API Examples

**Health check:**

```bash
curl http://localhost:8000/
```

**Review a repository:**

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"repository": "/path/to/repository"}'
```

**Get repository status:**

```bash
curl "http://localhost:8000/api/status?repository=/path/to/repository"
```

## Running Tests

```bash
cd backend
pytest -v
```

## Mock Reviewer Detections

The mock reviewer uses deterministic rules to detect:

| Pattern | Category | Severity |
|---------|----------|----------|
| `print(`, `console.log(`, `System.out.println(` | DEBUG_CODE | LOW |
| `TODO`, `FIXME` | CODE_SMELL | LOW |
| `except:` (bare except) | ERROR_HANDLING | MEDIUM |
| `password =`, `api_key =`, `secret =`, `token =` | SECURITY | HIGH |

## Future Ollama Integration

The reviewer is isolated behind a `Reviewer` interface in `backend/app/reviewer/base.py`. To add Ollama support:

1. Create `backend/app/reviewer/ollama.py` implementing the `Reviewer` interface.
2. Send the Git diff to a local Ollama instance with a structured JSON prompt.
3. Validate the response with Pydantic `ReviewResult`.
4. Swap `MockReviewer` for `OllamaReviewer` in `backend/app/api/review.py`.

Configure via environment variables (see `.env.example`):

```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=<model-name>
```

## License

MIT
