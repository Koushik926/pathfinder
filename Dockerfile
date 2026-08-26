# Build the frontend, then serve everything from one Python process.
FROM node:20-slim AS web
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

COPY backend/pyproject.toml ./backend/
COPY backend/app ./backend/app
RUN pip install --no-cache-dir -e ./backend

COPY --from=web /build/dist ./frontend/dist

ENV PORT=8000
EXPOSE 8000
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
