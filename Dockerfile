# Two stages: build the frontend with Node, then serve everything from one
# Python process. See .dockerignore — the host's node_modules must never reach
# the build context or it will clobber the container's Linux binaries.

FROM node:20-slim AS web
WORKDIR /build
# Copy manifests first so the dependency layer caches independently of source.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM python:3.11-slim

# Hugging Face Spaces (and most managed container hosts) run the image as a
# non-root user. Create one explicitly rather than relying on the default.
RUN useradd --create-home --uid 1000 app
WORKDIR /app

COPY --chown=app:app backend/pyproject.toml ./backend/
COPY --chown=app:app backend/app ./backend/app
RUN pip install --no-cache-dir -e ./backend

COPY --from=web --chown=app:app /build/dist ./frontend/dist

USER app

# Port is configurable so the same image runs on Render, Fly, HF Spaces, etc.
ENV PORT=8000 \
    PYTHONUNBUFFERED=1
EXPOSE 8000

WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
