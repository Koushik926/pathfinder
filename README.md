# PathFinder

**AI-powered personalized learning path recommender.**
Describe a goal in your own words; PathFinder profiles what you already know,
finds the skill gaps that stand between you and that goal, and generates an
ordered roadmap of courses, projects and assessments — explaining every
recommendation from the arithmetic that produced it.

Built for HCLTech Round 2 by **Critical Path**, REVA University.

---

## Quick start

Two commands. **No API key required** — PathFinder is fully functional offline.

```bash
# 1. Backend (Python 3.10+)
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e .
python -m app.seed.build          # compiles the catalog (already committed, safe to re-run)

# 2. Frontend (Node 18+)
cd ../frontend
npm install && npm run build

# 3. Run — serves API *and* UI on one port
cd ../backend
uvicorn app.main:app --port 8000
```

Open **http://localhost:8000**. Interactive API docs at **/docs**.

### Sharing or resuming a path

Any session can be reopened by URL, which makes a generated path shareable and
lets a reviewer jump straight to a populated view:

```
http://localhost:8000/?s=<session-id>            # restore a session
http://localhost:8000/?s=<session-id>&tab=progress   # open on the dashboard
```

### Development mode (hot reload)

```bash
cd backend  && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev        # http://localhost:5173, proxies /api
```

### Optional: enable Claude

PathFinder runs entirely on local models. Setting an API key upgrades *wording
and intent extraction only* — it never changes what is recommended.

```bash
cp .env.example .env      # add ANTHROPIC_API_KEY
cd backend && pip install -e ".[llm]"
```

With no key the header reads **Offline mode** and template explanations are used.
Every LLM call fails soft: no key, no package, no network, rate limit, or a
malformed response all fall back silently to the deterministic path.

### Tests

```bash
cd backend && pip install -e ".[dev]" && pytest -q      # 198 tests, ~5s
```

Verified on **Python 3.10 and 3.12** (numpy 2.2/2.5, scikit-learn 1.7/1.9).
The suite includes a reproducibility check asserting the committed catalog
matches a fresh rebuild byte-for-byte on either interpreter.

---

## Does it actually recommend well?

A passing test suite proves the system does what it was told. It says nothing
about whether what it was told is any good, so we measured that separately.

```bash
cd backend && python -m app.ml.evaluate            # ~20s
```

60 synthetic learners — every role, all three levels, a third of them cold
starts with no history — against three alternatives, each held to **the same
hour budget PathFinder spends**, so the difference comes from what gets picked
rather than from spending more of the learner's time.

| metric | popularity | embedding-only | no graph | **PathFinder** |
|---|---|---|---|---|
| Readiness gain (achievable) | 0.121 | 0.185 | 0.315 | **0.776** |
| Gain per 100 hours | 0.041 | 0.077 | 0.139 | **0.276** |
| Prerequisites met when scheduled | 74.6% | 41.7% | 42.6% | **100%** |
| Items teaching nothing needed | 76.8% | 36.0% | 0.0% | **0.0%** |
| Cold start, no history | 0.142 | 0.195 | 0.299 | **0.922** |

The usual recommender metrics don't transfer — precision, recall and NDCG score
you on reproducing a choice the user already made, and a learner who knew which
courses to pick wouldn't need this. So the harness measures the claim the system
actually makes: how much goal readiness a learner gains from items they can
*reach*, per hour spent.

That distinction is the whole story of the third column. Remove the prerequisite
graph and keep everything else, and it beats PathFinder on paper — 0.834 gain to
our 0.776. Then only 42.6% of its items are startable when they come up, so it
delivers 0.315. **62% of what it promises is fiction.** PathFinder loses nothing
between the two numbers.

Full method, baselines, limitations and the defect this caught on its first
run: **[docs/EVALUATION.md](docs/EVALUATION.md)**.

---

## What it does

| Requirement | Where it lives |
|---|---|
| Conversational interface | `backend/app/ml/conversation.py` — slot-filling dialogue, works offline |
| Learner profiling engine | `backend/app/ml/profiler.py` — noisy-OR mastery with recency decay |
| Recommendation engine | `backend/app/ml/recommender.py` — six-signal hybrid ranker |
| Learning path generator | `backend/app/ml/planner.py` — greedy submodular coverage over a prerequisite DAG |
| Explanation assistant | `backend/app/ml/explain.py` — explanations derived from ranker attributions |
| Answers learner queries | `backend/app/ml/qa.py` — ordering, duration, skipping, difficulty, progress, next steps |
| Progress dashboard | `frontend/src/components/Dashboard.jsx` — skill radar, gaps, milestones, next actions |

Every recommended item also links out to the provider so a learner can actually
go and take it, and the conversation transcript is restored on reload.

---

## How the recommendation works

```
  learner goal (free text)
        │
        ▼
  ┌───────────────┐   TF-IDF (word 1-2gram + char 3-5gram) → SVD 128d
  │ Semantic space│   items · skills · roles · goals share one space
  └───────┬───────┘
          ▼
  ┌───────────────┐   noisy-OR over completions, discounted by
  │   Profiler    │   depth × recency × assessment score
  └───────┬───────┘
          ▼  mastery vector
  ┌───────────────┐   target(role) − mastery, weighted by importance
  │  Gap engine   │
  └───────┬───────┘
          ▼  weighted gap vector
  ┌───────────────────────────────────────────┐
  │ Hybrid ranker                             │
  │  0.38 gap coverage    0.12 level fit      │
  │  0.18 semantic match  0.10 quality prior  │
  │  0.14 item-item CF    0.08 modality fit   │
  └───────┬───────────────────────────────────┘
          ▼  scored candidates + per-component attribution
  ┌───────────────┐   greedy submodular max-coverage under a time budget,
  │    Planner    │   simulated mastery gain after each pick,
  │               │   prerequisite closure → topological sort → milestones
  └───────┬───────┘
          ▼
   roadmap + explanations + schedule
```

Full design rationale, including why each choice was made and what was
rejected, is in **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## Data

The catalog is curated and committed, so results are reproducible and the demo
never depends on a network call.

| | |
|---|---|
| Items | **238** — 190 courses, 27 projects, 21 assessments |
| Skills | **116** across 13 categories |
| Career roles | **22** target skill profiles |
| Prerequisite graph | validated acyclic at build time, max depth **9** |
| Interaction log | 4,000 synthetic sessions (fixed seed) for collaborative filtering |

Sources are real providers (Coursera, edX, freeCodeCamp, NPTEL, DeepLearning.AI,
Hugging Face, AWS, and others); items authored for this project are marked
`PathFinder Labs`. Rebuild with `python -m app.seed.build` — the build fails
loudly on a dangling prerequisite, an unknown skill, a duplicate id or a cycle.

### How much of this does a public standard already cover?

Hand-authoring 116 skills invites a fair question: where did they come from,
and does that scale? So we checked them against **ESCO**, the EU's public
occupational classification (13,890 level-4 skills, one stable URI each).

```bash
python scripts/map_esco.py     # offline, cached, committed as data
```

**10 of 116 have an unambiguous ESCO concept.** ESCO has entries for
statistics, natural language processing, cyber security, SQL, JavaScript and
C++ — and none at all for PyTorch, RAG, Kubernetes, React, Next.js or
diffusion models.

That gap is the finding, not a bug in the mapping. It is the coverage boundary
of a public standard against fast-moving technical skills, and it is the same
reason the prerequisite edges had to be authored: no public dataset carries
those either.

Getting to an honest 10 meant throwing away three scoring rules, each of which
"succeeded" more impressively than the last:

| rule | claimed | what it actually matched |
|---|---|---|
| character similarity | 93/116 | Bash & Shell → *airport terminal standards* |
| token overlap | 93/116 | Computer Vision → *computer programming* |
| overlap after stopwords | 35/116 | BI Tools → *follow reporting procedures* |
| **names must be the same name** | **10/116** | — |

The surviving rule gives up real matches too — "Machine Learning" against
ESCO's *machine learning algorithms* is declined — and those refusals are
recorded in the tests rather than hidden. A small correct answer is worth more
than a large plausible one, particularly for a credibility claim.

Live at `GET /api/meta` under `taxonomy`, gaps included.

> **On the interaction log:** we have no real enrolment data, so the
> collaborative-filtering component is fitted on a *simulated* one, generated
> from a fixed seed. It is a genuine item-item CF model over genuine
> co-occurrence structure, but the co-occurrences are synthetic. It contributes
> 14% of the ranking weight; the other 86% uses no simulated data.

---

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/meta` | Catalog stats, model dimensions, LLM status |
| `POST` | `/api/session` | Start a session |
| `POST` | `/api/session/{id}/chat` | One conversational turn |
| `PUT` | `/api/session/{id}/profile` | Set the profile directly (form alternative to chat) |
| `GET` | `/api/session/{id}/path` | Generate / fetch the roadmap |
| `GET` | `/api/session/{id}/explain/{item}` | Why this item was recommended |
| `GET` | `/api/session/{id}/dashboard` | Progress, skill coverage, next actions |
| `POST` | `/api/session/{id}/feedback` | Completion, reaction, or pace change |
| `GET` | `/api/catalog/search?q=` | Semantic catalog search |

---

## Project layout

```
backend/
  app/
    seed/          catalog source of truth (pipe-delimited) + build script
    data/          compiled JSON artefacts
    ml/            embeddings, profiler, gap, graph, recommender,
                   planner, explain, feedback, conversation
    api/routes.py  HTTP layer (thin — all reasoning lives in ml/)
    llm.py         optional Claude integration, fails soft everywhere
  tests/           102 tests
frontend/
  src/components/  Chat, Roadmap, Dashboard, Primitives
docs/              architecture, demo script
```

## The engine is not about software careers

The reasoning is domain-independent: every engine takes a catalog as an
argument, and none of them knows what a course is *about*. `examples/medicine/`
contains a clinical-medicine catalog that shares no skill, role, item id or
category with the shipped one. The same engine, with no code change, produces a
coherent clinical curriculum from it — anatomy before physiology before
pharmacology, ward rotations at the end — and answers "can I skip anatomy?"
by naming physiology, read from that catalog's own prerequisite graph.

```bash
python examples/medicine/build_catalog.py
cp examples/medicine/data/*.json backend/app/data/    # then restart the server
git checkout backend/app/data                          # restore the software catalog
```

`backend/tests/test_catalog_agnostic.py` exercises this end to end, so a domain
assumption leaking into an algorithm fails the build.

## Deployment

`render.yaml` and `Dockerfile` are included; see
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Team

**Critical Path** — REVA University
R Koushik · Chethan H S · Khushi Katwe · Sandeep N · Chethan Kumar H M
