import os
import subprocess
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmpdir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmpdir,
            check=True,
            capture_output=True,
        )
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("initial\n")
        subprocess.run(["git", "add", "test.txt"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial"],
            cwd=tmpdir,
            check=True,
            capture_output=True,
        )
        yield tmpdir


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Git Diff Reviewer API"
    assert data["status"] == "running"


def test_review_valid_repository_no_changes(temp_git_repo):
    response = client.post("/api/review", json={"repository": temp_git_repo})
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "No changes found in the repository."
    assert data["issues"] == []
    assert data["overall_score"] == 10


def test_review_valid_repository_with_changes(temp_git_repo):
    test_file = os.path.join(temp_git_repo, "test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("modified with TODO\n")
    response = client.post("/api/review", json={"repository": temp_git_repo})
    assert response.status_code == 200
    data = response.json()
    assert "issues" in data
    assert "summary" in data


def test_review_invalid_repository():
    response = client.post("/api/review", json={"repository": "/nonexistent/path/99999"})
    assert response.status_code == 400
    assert "detail" in response.json()


def test_review_not_git_repository():
    with tempfile.TemporaryDirectory() as tmpdir:
        response = client.post("/api/review", json={"repository": tmpdir})
        assert response.status_code == 400
        assert "not a Git repository" in response.json()["detail"]


def test_status_valid_repository(temp_git_repo):
    response = client.get("/api/status", params={"repository": temp_git_repo})
    assert response.status_code == 200
    assert "status" in response.json()


def test_status_with_changes(temp_git_repo):
    test_file = os.path.join(temp_git_repo, "test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("changed\n")
    response = client.get("/api/status", params={"repository": temp_git_repo})
    assert response.status_code == 200
    assert "test.txt" in response.json()["status"]


def test_status_invalid_repository():
    response = client.get("/api/status", params={"repository": "/nonexistent/path/99999"})
    assert response.status_code == 400
