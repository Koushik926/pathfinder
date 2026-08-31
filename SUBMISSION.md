# Submission — HCLTech Amplified Round 2

Team **Critical Path** · REVA University
Deadline: 31 Aug 2026, 11:59 pm IST

---

## 1. Source code (ZIP)

Upload: **`PathFinder-CriticalPath.zip`** (712 KB, 79 files)

Built with `./package.sh` from `git archive`, so it contains exactly what is
committed — no virtual environment, no `node_modules`, no build output, no
caches. Includes a README with setup and execution instructions.

## 2. Source code repository

```
https://github.com/Koushik926/pathfinder
```

Public. 12 commits reflecting the development process: skeleton → data →
semantic layer → ML engines → API + tests → web UI → docs → fixes.

## 3. Solution documentation

Upload: **`docs/PathFinder-Solution-Documentation.pdf`** (8 pages)

Covers all six required areas: problem understanding, solution approach,
system architecture, AI/ML techniques used, key features and workflows, and
challenges faced.

## 4. Demo video URL

Record using `docs/DEMO_SCRIPT.md` — timed to 4:40, with the explainability
section as the centrepiece. Upload to YouTube (unlisted is fine) and paste
the link.

## 5. Deployed application URL

Optional. Leave blank, or deploy via `render.yaml` (see `docs/DEPLOYMENT.md`).
The local setup instructions below satisfy this requirement on their own.

---

## Local setup & execution instructions

> Paste the block below into the form's "Local setup & execution
> instructions" field.

```
PathFinder — AI-Powered Personalized Learning Path Recommender

REQUIREMENTS
  Python 3.10+ (verified on 3.10 and 3.12)
  Node.js 18+ (verified on Node 20+)
  No API key required. No database. No network access needed at runtime.

SETUP — three commands

  1) Backend
     cd backend
     python -m venv .venv && source .venv/bin/activate
        (Windows: .venv\Scripts\activate)
     pip install -e .

  2) Frontend
     cd ../frontend
     npm install && npm run build

  3) Run — serves the API and the UI on one port
     cd ../backend
     uvicorn app.main:app --port 8000

  Open http://localhost:8000
  Interactive API docs: http://localhost:8000/docs

USING IT
  Type a goal in plain language, e.g. "I want to become a generative AI
  engineer". Answer the three follow-up questions (experience level, what
  you have already completed, hours per week). The roadmap generates
  automatically.
  Click "Why this?" on any item to see the ranking components that placed
  it there. Use the Progress tab for the skill radar and next actions.

TESTS
  cd backend
  pip install -e ".[dev]"
  pytest -q            -> 73 tests, ~2 seconds

OPTIONAL — enable Claude
  The application is fully functional offline; this only improves the
  wording of replies and explanations, never what is recommended.
     cp .env.example .env      # add ANTHROPIC_API_KEY
     cd backend && pip install -e ".[llm]"

DOCKER (alternative)
  docker build -t pathfinder .
  docker run -p 8000:8000 pathfinder

NOTES FOR EVALUATORS
  - Runs completely offline. The header shows "Offline mode" when no API
    key is set; every feature works in that state.
  - The course catalog is committed to the repo, so nothing is fetched at
    runtime and the demo cannot fail on a network call.
  - Rebuilding the catalog (python -m app.seed.build) reproduces the
    committed data byte-for-byte on any supported Python version.
```

---

## Pre-submit checklist

- [x] ZIP excludes venv, node_modules, build artefacts — verified
- [x] README with setup and execution instructions included
- [x] Repo public and reachable unauthenticated (HTTP 200)
- [x] Commit history reflects development process
- [x] PDF covers all six required documentation areas
- [x] Clean-room verified: install → build → 73 tests → serve, on Python 3.12
- [ ] Demo video recorded and uploaded
- [ ] Form submitted before 11:59 pm IST
