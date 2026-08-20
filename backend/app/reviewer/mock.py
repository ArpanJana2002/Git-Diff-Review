import re

from app.reviewer.base import Reviewer
from app.schemas.review import ReviewIssue, ReviewResult

DEBUG_PATTERNS = [
    (re.compile(r"print\s*\("), "print("),
    (re.compile(r"console\.log\s*\("), "console.log("),
    (re.compile(r"System\.out\.println\s*\("), "System.out.println("),
]

TODO_PATTERN = re.compile(r"\b(TODO|FIXME)\b")

BARE_EXCEPT_PATTERN = re.compile(r"^\s*except\s*:")

CREDENTIAL_PATTERNS = [
    (re.compile(r"password\s*=", re.IGNORECASE), "password ="),
    (re.compile(r"api_key\s*=", re.IGNORECASE), "api_key ="),
    (re.compile(r"secret\s*=", re.IGNORECASE), "secret ="),
    (re.compile(r"token\s*=", re.IGNORECASE), "token ="),
]

HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


class MockReviewer(Reviewer):
    def review(self, diff: str) -> ReviewResult:
        if not diff.strip():
            return ReviewResult(
                summary="No changes found in the repository.",
                issues=[],
                positives=[],
                overall_score=10,
            )

        issues = self._analyze_diff(diff)
        positives = self._generate_positives(diff, issues)
        overall_score = self._calculate_score(issues)
        summary = self._generate_summary(issues)

        return ReviewResult(
            summary=summary,
            issues=issues,
            positives=positives,
            overall_score=overall_score,
        )

    def _analyze_diff(self, diff: str) -> list[ReviewIssue]:
        issues: list[ReviewIssue] = []
        current_file = ""
        current_line: int | None = None
        seen: set[tuple[str, str, str, int | None]] = set()

        for raw_line in diff.splitlines():
            if raw_line.startswith("+++ ") and not raw_line.startswith("+++ /dev/null"):
                current_file = raw_line[4:].strip()
                if current_file.startswith("b/"):
                    current_file = current_file[2:]
                continue

            hunk_match = HUNK_HEADER.match(raw_line)
            if hunk_match:
                current_line = int(hunk_match.group(1))
                continue

            if not raw_line.startswith("+") or raw_line.startswith("+++"):
                if raw_line.startswith(" ") and current_line is not None:
                    current_line += 1
                continue

            added_content = raw_line[1:]
            line_number = current_line
            if current_line is not None:
                current_line += 1

            self._check_patterns(
                added_content,
                current_file,
                line_number,
                issues,
                seen,
            )

        return issues

    def _check_patterns(
        self,
        content: str,
        file_path: str,
        line_number: int | None,
        issues: list[ReviewIssue],
        seen: set[tuple[str, str, str, int | None]],
    ) -> None:
        for pattern, label in DEBUG_PATTERNS:
            if pattern.search(content):
                self._add_issue(
                    issues,
                    seen,
                    severity="LOW",
                    category="DEBUG_CODE",
                    file=file_path or "unknown",
                    line=line_number,
                    message=f"Debug statement detected: {label}",
                    suggestion="Remove debug statements before committing.",
                )

        if TODO_PATTERN.search(content):
            self._add_issue(
                issues,
                seen,
                severity="LOW",
                category="CODE_SMELL",
                file=file_path or "unknown",
                line=line_number,
                message="TODO or FIXME comment found in changed code.",
                suggestion="Resolve or track the TODO/FIXME before merging.",
            )

        if BARE_EXCEPT_PATTERN.search(content):
            self._add_issue(
                issues,
                seen,
                severity="MEDIUM",
                category="ERROR_HANDLING",
                file=file_path or "unknown",
                line=line_number,
                message="Bare except clause detected.",
                suggestion="Catch specific exceptions instead of using a bare except.",
            )

        for pattern, label in CREDENTIAL_PATTERNS:
            if pattern.search(content):
                self._add_issue(
                    issues,
                    seen,
                    severity="HIGH",
                    category="SECURITY",
                    file=file_path or "unknown",
                    line=line_number,
                    message=f"Potential hardcoded credential detected ({label}).",
                    suggestion="Move the credential to an environment variable.",
                )

    def _add_issue(
        self,
        issues: list[ReviewIssue],
        seen: set[tuple[str, str, str, int | None]],
        severity: str,
        category: str,
        file: str,
        line: int | None,
        message: str,
        suggestion: str,
    ) -> None:
        key = (severity, category, file, line)
        if key in seen:
            return
        seen.add(key)
        issues.append(
            ReviewIssue(
                severity=severity,
                category=category,
                file=file,
                line=line,
                message=message,
                suggestion=suggestion,
            )
        )

    def _generate_positives(self, diff: str, issues: list[ReviewIssue]) -> list[str]:
        positives: list[str] = []
        added_lines = sum(
            1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")
        )

        if added_lines <= 50:
            positives.append("Changes are relatively small.")
        else:
            positives.append("Changes span multiple areas of the codebase.")

        categories = {issue.category for issue in issues}
        if "PERFORMANCE" not in categories:
            positives.append("No obvious performance problems were detected.")

        if not any(issue.severity in ("CRITICAL", "HIGH") for issue in issues):
            positives.append("No critical or high severity issues were found.")

        return positives

    def _calculate_score(self, issues: list[ReviewIssue]) -> int:
        if not issues:
            return 10

        penalty = 0
        for issue in issues:
            if issue.severity == "CRITICAL":
                penalty += 3
            elif issue.severity == "HIGH":
                penalty += 2
            elif issue.severity == "MEDIUM":
                penalty += 1
            elif issue.severity == "LOW":
                penalty += 0.5

        score = max(0, min(10, round(10 - penalty)))
        return score

    def _generate_summary(self, issues: list[ReviewIssue]) -> str:
        if not issues:
            return "The changes look good with no obvious issues detected."

        high_count = sum(1 for i in issues if i.severity in ("CRITICAL", "HIGH"))
        if high_count > 0:
            return "The changes contain several potential issues."

        return f"The changes contain {len(issues)} minor issue(s) to review."
