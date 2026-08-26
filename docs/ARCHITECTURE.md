# PathFinder — Architecture & Design Rationale

## 1. The problem, precisely

Course recommenders answer "what is relevant to this topic?" Learners need an
answer to a harder question: *"given what I already know, what should I do
next, in what order, to reach a goal I can only describe vaguely?"*

That reframing drives every decision below. It means the system needs four
things a similarity-based recommender does not have:

1. a model of what the learner **already knows**, so it stops recommending it;
2. a model of what the goal **requires**, so "relevant" becomes measurable;
3. **ordering**, because a course you are not ready for is worse than useless;
4. **explanations**, because a learner who does not trust the ordering abandons it.

## 2. System shape

```
React SPA ──HTTP──▶ FastAPI (thin routes)
                        │
                        ▼
                   ML engines (pure Python, no I/O)
        embeddings · profiler · gap · graph · recommender · planner · explain
                        │
                        ▼
                 Catalog (in-memory, compiled from committed seeds)
```

The route layer contains no reasoning. Every engine is a pure function over a
profile and the catalog, which is why the 67-test suite can exercise the
algorithms directly without HTTP, and why a path is reproducible: the same
profile always yields the same path.

## 3. Representation

### 3.1 Semantic space

Items, skills, roles and free-text goals are embedded into **one** 128-dimensional
space so any of them can be compared with a dot product. The space is TF-IDF →
truncated SVD (latent semantic analysis) over a document built per entity.

Two feature views are unioned before the SVD:

| View | Range | Role |
|---|---|---|
| word | 1–2 grams | carries topical meaning |
| char | 3–5 grams (`char_wb`) | morphological robustness |

**Why the character view exists.** With a word-only model, the goal
*"designing beautiful websites"* produced a **zero vector** — none of those
word forms appear in the catalog — and the learner received no recommendations
at all. Character n-grams let "websites" reach "web design" through shared
substrings. This is covered by a regression test
(`test_unseen_word_forms_still_match`).

**Why not a neural sentence encoder.** A sentence-transformer would embed
better, but costs a ~500 MB model download, non-determinism across versions,
and a hard dependency for anyone evaluating the project. LSA fits in under a
second, is byte-reproducible, and runs with no network. At 238 items the
accuracy difference does not change the ranking in practice; the honest
trade-off is that on a catalog 100× larger, a neural encoder would win.

### 3.2 Catalog

Curated rather than scraped, for three reasons: prerequisite edges do not exist
in any public course dataset and are the backbone of this system; a committed
catalog means the demo cannot fail on a network call; and correctness is
enforceable. `python -m app.seed.build` refuses to produce output if any
prerequisite dangles, any skill is unknown, any id repeats, or the graph
contains a cycle.

## 4. Learner profiling

Mastery per skill combines evidence with a **noisy-OR**:

```
mastery(skill) = 1 − Π (1 − contributionᵢ)
contributionᵢ  = weight × depth × recency × score × kind
```

Summing would be wrong: two courses each teaching Python at 0.5 do not produce
a Python expert — they overlap heavily. Noisy-OR gives the diminishing returns
that real learning shows, and cannot exceed 1.0. The consequence that matters
downstream: the gap engine naturally stops asking for more Python once the
learner clearly knows Python.

| Factor | Effect |
|---|---|
| `depth` | advanced items teach more deeply (0.85 / 1.0 / 1.15 by level) |
| `recency` | `0.5^(months/24)`, floored at 0.35 — skills fade but do not vanish |
| `score` | assessment results are direct evidence; default 0.85 for a completion |
| `kind` | projects and assessments count 1.1× — building beats watching |

A parallel **confidence** vector records how much evidence backs each estimate,
so the interface can distinguish "we know you know this" from "you told us you do".

## 5. Gap analysis

A role is a target vector: skill → importance. The gap is

```
gap        = max(0, target − mastery)
weighted   = gap × target        ← the ranking quantity
```

Weighting by importance is what stops a large gap in a peripheral skill from
outranking a moderate gap in a central one. Skills the learner names directly
("I want to learn RAG") are merged into the target at a floor of 0.55, so an
explicit request is never treated as trivia.

## 6. Ranking

Six independent signals, linearly combined, weights summing to 1:

| Signal | Weight | What it contributes | Fails alone because |
|---|---|---|---|
| gap coverage | 0.38 | progress toward the goal | ignores quality and readiness |
| semantic | 0.18 | intent the role target misses | ignores what you know |
| item-item CF | 0.14 | "learners like you took this next" | cold start; echoes popularity |
| level fit | 0.12 | anti-frustration | ignores the goal entirely |
| quality prior | 0.10 | Bayesian-smoothed rating × log popularity | popularity ≠ relevance |
| modality | 0.08 | format preference | cosmetic on its own |

Two details worth naming. The quality prior is **Bayesian-smoothed**
(`(rating·n + 4.6·50000) / (n + 50000)`) so a 4.9 from 200 raters does not
outrank a 4.8 from 200,000. The CF similarity is **shrunk**
(`co/(co+12)`) so a pair co-occurring twice is not trusted like a pair
co-occurring two hundred times.

**Components are kept separate rather than collapsed into a score**, because
they *are* the explanation (§8).

Ties and near-duplicates are handled by MMR re-ranking, which trades a little
relevance for breadth — otherwise the top five are five near-identical intro
courses.

## 7. Path construction

Choosing a path is budgeted maximum coverage: pick items covering as much
weighted gap as possible within a time budget, respecting prerequisites. The
objective is **submodular** (each additional course on a topic adds less), so
greedy selection carries the standard (1 − 1/e) approximation guarantee and
runs in milliseconds.

After each pick, the planner **simulates the mastery the learner would gain**
using the same noisy-OR rule the profiler uses, then recomputes the remaining
gap. This is what prevents four overlapping intro-ML courses: once the first is
taken, the rest lose most of their marginal value.

Then:

1. **Prerequisite closure** — pull in unmet prerequisites (already-known ones are skipped).
2. **Priority propagation** — a prerequisite inherits the priority of the most urgent item it unlocks. *Without this, filler courses sorted to the back of the path on zero priority and dragged the high-value items that needed them along too, so foundations landed after the material built on them.*
3. **Topological sort** — Kahn's algorithm, deterministic tie-breaking.
4. **Milestone chunking** — split on cumulative hours so phases are comparable in duration, which is what makes a progress bar meaningful.
5. **Scheduling** — milestone dates from the learner's weekly budget.

### The projects guarantee

Coverage-per-hour has a blind spot: a 20-hour project consolidating four
already-taught skills scores worse than two 10-hour courses each introducing a
new one. Left alone, the planner produced a **reading list with no hands-on work
at all**. Projects and assessments get a selection bonus (1.3× / 1.15×), and a
minimum of two projects is guaranteed after greedy selection. A path you cannot
show anyone is not a path.

## 8. Explanations

The explanation layer reads the **same component attributions that produced the
ranking**. Every sentence traces to a number the ranker used: the share each
signal contributed, the skills covered and by how much, the prerequisite state,
what the item unlocks.

This is a deliberate architectural constraint. A system that ranks with one
model and explains with another can produce fluent, confident, *wrong*
justifications. Here the explanation cannot drift from the ranking, because it
is computed from it.

When an API key is present, Claude rewrites those facts into warmer prose. It
is given the facts and instructed to introduce no others. Claude is **never**
asked to choose or order recommendations — that stays deterministic, so results
are reproducible and defensible.

## 9. Adaptation

Feedback is folded back into the **profile**, and the path is regenerated —
never patched in place. One source of truth means the roadmap cannot drift from
the learner model. Regeneration takes milliseconds, which is what makes this
affordable.

| Signal | Effect |
|---|---|
| completion (+ score) | credited as mastery; a low score credits only partially |
| "too easy" | credit the skills, raise the difficulty target |
| "too hard" | lower the target and insert groundwork — the item is not dropped |
| "not interested" | de-emphasise the topic, but keep what the goal still requires |
| "more like this" | bias the goal vector toward it |
| pace change | rescales the entire schedule |

## 10. Honest limitations

- **The interaction log is synthetic.** Item-item CF is fitted on 4,000
  simulated sessions, not real enrolments. It is a real CF model over real
  co-occurrence structure, but the co-occurrences were generated. It carries
  14% of the ranking weight.
- **Ranking weights are hand-set, not learned.** With no real engagement data
  there is nothing to fit them against. They were tuned against the behaviours
  in the test suite. Real usage data would allow learning them.
- **238 items is a prototype catalog.** The architecture scales — the ranker is
  vectorised and the graph algorithms are near-linear — but retrieval would need
  an ANN index beyond ~10⁵ items.
- **LSA under-performs a neural encoder** on paraphrase-heavy input. The
  character n-gram view narrows the gap; it does not close it.
- **Sessions are in-memory**, capped at 500 and lost on restart. Swapping
  `app/sessions.py` for Redis or Postgres is the only change needed.
- **Mastery is inferred, not measured.** Completing a course is weak evidence of
  learning it. Assessment scores sharpen this, which is why assessments are
  first-class catalog items rather than an afterthought.
