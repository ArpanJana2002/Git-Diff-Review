import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.review import router as review_router

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(title="Git Diff Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"message": "Git Diff Reviewer API", "status": "running"}
