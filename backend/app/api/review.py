from fastapi import APIRouter, HTTPException, Query

from app.git.repository import GitError, GitService
from app.reviewer.mock import MockReviewer
from app.schemas.review import ReviewRequest, ReviewResult, StatusResponse

router = APIRouter(prefix="/api", tags=["review"])

git_service = GitService()
reviewer = MockReviewer()


@router.post("/review", response_model=ReviewResult)
def review_changes(request: ReviewRequest) -> ReviewResult:
    try:
        git_service.validate_repository(request.repository)
        diff = git_service.get_diff(request.repository)
        return reviewer.review(diff)
    except GitError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while reviewing the repository.",
        ) from exc


@router.get("/status", response_model=StatusResponse)
def get_status(repository: str = Query(...)) -> StatusResponse:
    try:
        status = git_service.get_status(repository)
        return StatusResponse(status=status)
    except GitError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving repository status.",
        ) from exc
