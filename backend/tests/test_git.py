import os
import subprocess
import tempfile

import pytest

from app.git.repository import GitError, GitService


@pytest.fixture
def git_service():
    return GitService()


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
            f.write("initial content\n")
        subprocess.run(["git", "add", "test.txt"], cwd=tmpdir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmpdir,
            check=True,
            capture_output=True,
        )
        yield tmpdir


def test_validate_valid_repository(git_service, temp_git_repo):
    assert git_service.validate_repository(temp_git_repo) is True


def test_validate_nonexistent_path(git_service):
    with pytest.raises(GitError, match="does not exist"):
        git_service.validate_repository("/nonexistent/path/12345")


def test_validate_not_a_directory(git_service, temp_git_repo):
    file_path = os.path.join(temp_git_repo, "somefile.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("content")
    with pytest.raises(GitError, match="not a directory"):
        git_service.validate_repository(file_path)


def test_validate_not_a_git_repository(git_service):
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(GitError, match="not a Git repository"):
            git_service.validate_repository(tmpdir)


def test_get_status_with_changes(git_service, temp_git_repo):
    test_file = os.path.join(temp_git_repo, "test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("modified content\n")
    status = git_service.get_status(temp_git_repo)
    assert "test.txt" in status


def test_get_diff_with_changes(git_service, temp_git_repo):
    test_file = os.path.join(temp_git_repo, "test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("modified content\n")
    diff = git_service.get_diff(temp_git_repo)
    assert "modified content" in diff


def test_get_diff_no_changes(git_service, temp_git_repo):
    diff = git_service.get_diff(temp_git_repo)
    assert diff == ""
