import os
import subprocess


class GitError(Exception):
    """Raised when a Git operation fails."""


class GitService:
    def validate_repository(self, path: str) -> bool:
        if not os.path.exists(path):
            raise GitError("The provided path does not exist.")
        if not os.path.isdir(path):
            raise GitError("The provided path is not a directory.")

        abs_path = os.path.normpath(os.path.abspath(path))
        git_dir = os.path.join(abs_path, ".git")
        has_git = os.path.isdir(git_dir) or os.path.isfile(git_dir)

        try:
            result = subprocess.run(
                ["git", "-C", abs_path, "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            raise GitError("Git is not installed or not available in PATH.") from None

        if result.returncode != 0 or result.stdout.strip() != "true":
            raise GitError("The provided path is not a Git repository.")

        top_result = subprocess.run(
            ["git", "-C", abs_path, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if top_result.returncode != 0:
            raise GitError("The provided path is not a Git repository.")

        top_level = os.path.normpath(os.path.abspath(top_result.stdout.strip()))
        if not has_git and abs_path != top_level:
            raise GitError("The provided path is not a Git repository.")

        return True

    def get_status(self, path: str) -> str:
        self.validate_repository(path)
        return self._run_git(path, ["git", "status", "--short"])

    def get_diff(self, path: str) -> str:
        self.validate_repository(path)
        return self._run_git(path, ["git", "diff"])

    def _run_git(self, path: str, command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                cwd=path,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            raise GitError("Git is not installed or not available in PATH.") from None
        if result.returncode != 0:
            stderr = result.stderr.strip() or "Git command failed."
            raise GitError(stderr)
        return result.stdout
