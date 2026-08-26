"""PathFinder API entry point.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
import warnings

# numpy 2.x on macOS/Accelerate emits spurious divide-by-zero and overflow
# RuntimeWarnings from BLAS matmul even on clean finite inputs (reproducible
# with random data and no NaNs anywhere). Our matrices are checked for NaN in
# the test suite; silencing this keeps real numerical warnings visible.
warnings.filterwarnings("ignore", message=".*encountered in matmul.*", category=RuntimeWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

logging.basicConfig(
    level=os.environ.get("PATHFINDER_LOG_LEVEL", "INFO"),
    format="%(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title="PathFinder",
    version="1.0.0",
    description=(
        "AI-powered personalized learning path recommender. Profiles a learner, "
        "analyses skill gaps against a career goal, and generates an ordered, "
        "explained roadmap of courses, projects and assessments."
    ),
)

# The frontend is served separately in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "PATHFINDER_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "name": "PathFinder",
        "docs": "/docs",
        "health": "/api/health",
    }
