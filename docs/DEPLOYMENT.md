# Deployment

PathFinder is one process: FastAPI serves the API *and* the built frontend, so
there is a single URL and no CORS configuration in production.

## Build

```bash
cd frontend && npm ci && npm run build     # emits frontend/dist
cd ../backend && pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Render (render.yaml included)

Push to GitHub, then **New → Blueprint** and point Render at the repo. The
blueprint builds the frontend, installs the backend, and starts uvicorn.
Free tier is sufficient — the app holds ~40 MB resident and needs no database.

Optional: set `ANTHROPIC_API_KEY` in the Render dashboard to enable Claude.
Leave it unset and the app runs in offline mode.

## Docker

```bash
docker build -t pathfinder .
docker run -p 8000:8000 pathfinder
# with Claude:
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... pathfinder
```

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | 8000 | Listen port |
| `ANTHROPIC_API_KEY` | *unset* | Optional. Enables Claude narration. |
| `ANTHROPIC_MODEL` | `claude-opus-5` | Model used when a key is set |
| `PATHFINDER_CORS_ORIGINS` | localhost:5173 | Only needed if the frontend is hosted separately |
| `PATHFINDER_LOG_LEVEL` | INFO | Log verbosity |

## Notes for evaluators

- **No API key is required.** The app is fully functional offline.
- No database, no external services, no network calls at request time.
- Cold start is ~1 s (the SVD is fitted at import).
- Sessions are in-memory and capped at 500; a restart clears them.

---

## Submission deliverable 3 — solution documentation

`docs/solution-documentation.html` is the presentation document (problem
understanding, approach, architecture, AI/ML techniques, features, challenges).
It is print-styled: open it in a browser and **Print → Save as PDF** to produce
the PDF for submission. It is also published at:

https://claude.ai/code/artifact/c70f67b4-f363-47a1-892a-800e51925a30
