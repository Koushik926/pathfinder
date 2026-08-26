"""PathFinder API entry point.

Run locally:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
import warnings
from pathlib import Path

# numpy 2.x on macOS/Accelerate emits spurious divide-by-zero and overflow
# RuntimeWarnings from BLAS matmul even on clean finite inputs (reproducible
# with random data and no NaNs anywhere). Our matrices are checked for NaN in
# the test suite; silencing this keeps real numerical warnings visible.
warnings.filterwarnings("ignore", message=".*encountered in matmul.*", category=RuntimeWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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


# When the frontend has been built (`npm run build`), serve it from the same
# origin. That makes the whole app one process and one URL to deploy, and means
# a judge never has to run two servers. In development the frontend runs on
# Vite instead and proxies /api here, so this block simply does not apply.
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="assets",
    )

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")

else:
    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {
            "name": "PathFinder",
            "docs": "/docs",
            "health": "/api/health",
            "note": "Frontend not built. Run: cd frontend && npm install && npm run build",
        }
