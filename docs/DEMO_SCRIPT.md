# Demo video script (3–5 minutes)

Record at 1920×1080. Run `uvicorn app.main:app --port 8000` and open
`http://localhost:8000` — one window, no terminal switching mid-demo.

**Before recording:** click *Start over* so the chat is clean, and have a second
browser tab on `/docs` ready for the API shot.

---

### 0:00 – 0:25 · The problem

> "Search any learning platform for 'machine learning' and you get thousands of
> courses. Every one of them is relevant. None of them tells you which to take
> first, which you're not ready for, or which you can skip because you already
> know it. That's the gap PathFinder closes."

*On screen: the landing view, catalog counter visible in the header.*

### 0:25 – 1:10 · Conversation

Type: **"I want to become a generative AI engineer"**

> "It resolves that to a career profile — 14 target skills, each weighted by how
> central it is to the job."

Answer the level prompt: **"some grounding"**
Then: **"I did Python for Everybody and Prompt Engineering for Developers"**

> "It's matching what I said against the real catalog, so those two become
> evidence in my profile — not just text."

Then: **"15 hours a week, hands-on"**

*Point at the four slot chips turning green as they fill.*

> "Four things it needs: goal, level, history, pace. It asks for exactly what's
> missing and stops the moment it has enough."

### 1:10 – 2:10 · The roadmap

*Roadmap renders.*

> "289 hours across five milestones — and note the starting point: it puts me at
> 10% ready today and 89% at the end. That number is computed against the role's
> weighted skill profile, not a guess."

Scroll through the milestones.

> "The ordering is a topological sort over a prerequisite graph, so nothing
> appears before what it depends on. These amber items are prerequisites I was
> missing — it pulled them in automatically."

Point at a project and an assessment.

> "And it's not a reading list. Projects and assessments are first-class: the
> planner guarantees hands-on work, because coverage-per-hour alone will happily
> hand you twenty videos and nothing to show for it."

### 2:10 – 3:00 · Explainability — *the core differentiator*

Click **"Why this?"** on any item.

> "This is the part I'd point at. These bars aren't a narrative generated after
> the fact — they're the actual scoring components the ranker used to place this
> item here. Gap coverage contributed this much, difficulty fit this much,
> collaborative filtering this much."

> "That matters because a system that ranks with one model and explains with
> another can produce a confident, fluent, completely wrong justification. Here
> the explanation is computed *from* the ranking, so it can't drift."

*Point at the header chip reading "Offline mode".*

> "And notice — this is running with no API key. All of this is local models:
> TF-IDF with SVD embeddings, a noisy-OR mastery model, submodular path
> selection. Add a Claude key and it rewrites the wording; it never changes what
> gets recommended."

### 3:00 – 3:45 · Adaptation

Click **"Too hard"** on an advanced item.

> "Feedback goes back into the profile and the whole path regenerates — it isn't
> patched. One source of truth, so the roadmap can never disagree with the
> learner model."

Mark two items complete, then switch to **Progress**.

> "The radar is my mastery against the goal's target profile. The gaps are ranked
> by how much the goal actually depends on them. And 'Do next' only shows items
> whose prerequisites I've genuinely cleared."

### 3:45 – 4:20 · Under the hood

Switch to the `/docs` tab, then show the terminal running `pytest -q`.

> "FastAPI backend, React frontend, 238 curated items with a validated acyclic
> prerequisite graph, 116 skills, 22 career profiles. 77 tests covering the
> catalog invariants and the algorithms — including regressions for two real
> bugs we hit: goals being silently logged as completed history, and unseen word
> forms returning no recommendations at all."

### 4:20 – 4:40 · Close

> "PathFinder turns 'I want to get into AI' into an ordered, scheduled,
> explained plan that starts from what you already know — and every
> recommendation can show its work."

---

## Checklist

- [ ] Slot chips filling green are clearly visible
- [ ] "Why this?" bars shown full-screen — this is the differentiator
- [ ] "Offline mode" chip called out explicitly
- [ ] A project **and** an assessment pointed at in the roadmap
- [ ] Path regeneration after feedback shown, not just described
- [ ] Test suite passing on screen
- [ ] Under 5:00
