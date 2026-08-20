import pytest

from app.reviewer.mock import MockReviewer


@pytest.fixture
def reviewer():
    return MockReviewer()


def _make_diff(file_path: str, added_lines: list[str]) -> str:
    lines = [
        f"diff --git a/{file_path} b/{file_path}",
        f"--- a/{file_path}",
        f"+++ b/{file_path}",
        "@@ -1,3 +1,4 @@",
        " context line",
    ]
    for line in added_lines:
        lines.append(f"+{line}")
    return "\n".join(lines)


def test_empty_diff(reviewer):
    result = reviewer.review("")
    assert result.summary == "No changes found in the repository."
    assert result.issues == []
    assert result.positives == []
    assert result.overall_score == 10


def test_detect_todo(reviewer):
    diff = _make_diff("src/main.py", ["# TODO: fix this later"])
    result = reviewer.review(diff)
    assert any(i.category == "CODE_SMELL" and "TODO" in i.message for i in result.issues)


def test_detect_print(reviewer):
    diff = _make_diff("src/debug.py", ["print('debug info')"])
    result = reviewer.review(diff)
    assert any(i.category == "DEBUG_CODE" for i in result.issues)


def test_detect_console_log(reviewer):
    diff = _make_diff("src/app.js", ["console.log('debug');"])
    result = reviewer.review(diff)
    assert any(i.category == "DEBUG_CODE" for i in result.issues)


def test_detect_bare_except(reviewer):
    diff = _make_diff("src/handler.py", ["except:"])
    result = reviewer.review(diff)
    assert any(i.category == "ERROR_HANDLING" and i.severity == "MEDIUM" for i in result.issues)


def test_detect_password(reviewer):
    diff = _make_diff("src/auth.py", ["password = 'secret123'"])
    result = reviewer.review(diff)
    assert any(i.category == "SECURITY" and i.severity == "HIGH" for i in result.issues)


def test_detect_api_key(reviewer):
    diff = _make_diff("src/config.py", ["api_key = 'abc123'"])
    result = reviewer.review(diff)
    assert any(i.category == "SECURITY" and i.severity == "HIGH" for i in result.issues)


def test_overall_score_range(reviewer):
    diff = _make_diff("src/auth.py", ["password = 'secret'", "print('debug')"])
    result = reviewer.review(diff)
    assert 0 <= result.overall_score <= 10


def test_positives_generated(reviewer):
    diff = _make_diff("src/main.py", ["x = 1"])
    result = reviewer.review(diff)
    assert len(result.positives) > 0
