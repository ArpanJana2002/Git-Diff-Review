from typing import Literal

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    category: str
    file: str
    line: int | None
    message: str
    suggestion: str


class ReviewResult(BaseModel):
    summary: str
    issues: list[ReviewIssue]
    positives: list[str]
    overall_score: int = Field(ge=0, le=10)


class ReviewRequest(BaseModel):
    repository: str


class StatusResponse(BaseModel):
    status: str
