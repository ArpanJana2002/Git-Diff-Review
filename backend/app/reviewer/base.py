from app.schemas.review import ReviewResult


class Reviewer:
    def review(self, diff: str) -> ReviewResult:
        raise NotImplementedError
