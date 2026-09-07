# Does PathFinder actually recommend well?

A passing test suite proves the system does what it was told. It says nothing
about whether what it was told is any good. This is the second question.

Reproduce everything here with:

```bash
cd backend && python -m app.ml.evaluate --size 60 --json ../docs/evaluation.json
```

## Why not precision, recall and NDCG

The standard recommender metrics all work the same way: hold out items the
user chose, then score the system on how well it predicted that choice. That
design assumes the user's own preference is the ground truth.

For a learning path it is the wrong target. A path is not a prediction of what
a learner would pick — it is a claim about what will get them to a goal
fastest, in an order they can actually follow. A learner who knew which
courses to choose would not need the product. Ranking the courses someone
already likes is precisely the failure mode we are trying to avoid.

So the metrics measure what the system actually claims.

| Metric | What it asks |
|---|---|
| **Gain (achievable)** | How much importance-weighted goal readiness the learner actually gains, counting **only items they can reach** |
| Gain (if perfect) | The same, assuming the learner completes everything handed to them — the optimistic number |
| **Gain / 100h** | Achievable gain per unit of the learner's time. Budgets are hours, not items |
| **Prerequisite validity** | Fraction of items whose prerequisites are met *at the moment they are scheduled*. Below 1.0 is a path that cannot be followed as written |
| Wasted items | Chosen items teaching nothing the learner lacks |
| Scaffolding | Items pulled in only to unlock later ones. Reported separately from waste — it is the price of a followable path |
| Cold-start gain | Achievable gain for learners with no history at all |
| Distinct items | Items used across the whole cohort — catches "everyone gets the same five popular courses" |

The split between **achievable** and **if perfect** is the important one. A
strategy that ignores prerequisites looks strong under the optimistic number
and collapses under the honest one, because the gain sitting behind a wall the
learner cannot climb never arrives.

## Method

60 synthetic learners, seeded and reproducible: every role in the catalog, all
three experience levels, weekly budgets from 3 to 20 hours, and a third of them
cold starts with no history. Synthetic cohorts are the standard design in the
learning-path literature — real learners do not come with ground-truth mastery
labels, and without ground truth there is nothing to measure against.

Each history is **prerequisite-closed**: nobody has finished Advanced PyTorch
without finishing Python. Sampling random item subsets would invent learners
the world never sends us and flatter the graph-aware strategy for the wrong
reason. A test asserts this property holds.

PathFinder runs first, and its hour spend becomes the budget every baseline is
held to. Comparing at equal cost is the only fair test: a strategy that
recommends 400 hours will always "cover" more than one that recommends 250.

### What it is compared against

| Strategy | What it represents |
|---|---|
| `popularity` | Rank by rating and enrolment. No learner model — what a catalog with a "Top courses" shelf does |
| `semantic` | Rank by similarity to the goal text. An embedding-only or LLM-only system with no learner model behaves like this |
| `coverage_only` | Greedy skill-gap coverage per hour, with no prerequisite graph and no ordering. The **ablation** — it isolates what the graph contributes |
| `pathfinder` | The full system |

## Results

60 learners · 238 items · 116 skills · 22 roles · seed 20260907

| metric | popularity | semantic | coverage_only | **pathfinder** |
|---|---|---|---|---|
| Gain (if perfect) | 0.153 | 0.506 | **0.834** | 0.776 |
| **Gain (achievable)** | 0.121 | 0.185 | 0.315 | **0.776** |
| **Gain / 100h** | 0.041 | 0.077 | 0.139 | **0.276** |
| **Prerequisite validity** | 74.6% | 41.7% | 42.6% | **100.0%** |
| Wasted items | 76.8% | 36.0% | **0.0%** | **0.0%** |
| Scaffolding | 0.0% | 0.0% | 0.0% | 10.5% |
| Has 2+ projects | 26.7% | 100.0% | 96.7% | **100.0%** |
| Distinct items | 35 | 193 | 198 | 179 |
| Mean hours | 294 | 294 | 263 | 294 |
| **Cold-start gain** | 0.142 | 0.195 | 0.299 | **0.922** |

**2.5× the achievable readiness gain** of the strongest baseline, **2.0× the
gain per hour**, and **3.1× on cold starts** — at the same hour budget.

## Reading the results honestly

**The ablation appears to win, and that is the finding.** `coverage_only`
optimises the same objective as PathFinder and posts a *higher* optimistic gain
(0.834 vs 0.776). Then prerequisite validity comes in at 42.6%: fewer than half
its items are reachable when they arrive. Its achievable gain is 0.315 — **62%
of what it promised is fiction.** PathFinder loses nothing between the two
numbers, because everything it schedules can be started when it is scheduled.

This is the entire case for the prerequisite graph, measured rather than
asserted. It also explains why the greedy coverage objective alone is not
enough, which is the part most systems get wrong.

**Cold start is where the gap is widest, and that is not a coincidence.**
Collaborative filtering has nothing to work with for a learner who has done
nothing. PathFinder's ranker leans on skill coverage, the goal embedding and
the graph — all available on turn one — so a brand-new learner gets 0.922
achievable gain against 0.299 for the best baseline.

**Popularity is the most instructive failure.** It posts respectable
prerequisite validity (74.6%) for a trivial reason: it recommends beginner
content, which has no prerequisites. It also reuses just 35 distinct items
across 60 learners — the same shelf for everyone — and 76.8% of what it
recommends teaches nothing the learner is missing.

**Where PathFinder does not lead.** `coverage_only` uses 198 distinct items to
our 179. Spread is a real property and we give some up, because prerequisite
closure repeatedly pulls the same foundational items into different learners'
paths. We think that trade is correct — those items are the ones that make the
rest reachable — but it is a trade, not a free win.

**Scaffolding is 10.5%, and it is not waste.** Those are items that teach
nothing new toward the goal but unlock something that does. An earlier version
of this report counted them as redundancy, which punished the exact mechanism
that produces 100% validity. They are now reported separately. Baselines have
no scaffolding because they have no graph, so the split never flatters us.

## What this caught

The harness is not decoration; it found a real defect on its first full run.
`_ensure_projects` guaranteed every path contained hands-on work, and hit the
quota with the best-scoring project available — regardless of whether that
project served the learner's goal. A security analyst was being handed *Ship a
Mobile App to Store*. Two of 543 items across the cohort, invisible to 188
passing tests and to any amount of manual clicking.

The planner now requires a topped-up project to cover outstanding gap, and
leaves the path shorter when the catalog has no on-goal project to offer.
Wasted items went from 0.4% to 0.0%, and `test_no_item_is_chosen_that_teaches_
nothing_needed` keeps it there.

## What is tested

`backend/tests/test_evaluation.py` asserts the *properties* rather than the
numbers — pinning the numbers would make every genuine improvement look like a
regression:

- synthetic histories are prerequisite-closed
- the cohort covers every role and contains cold starts
- PathFinder's prerequisite validity is exactly 1.0
- PathFinder beats every baseline on achievable gain and on gain per hour
- no chosen item teaches nothing needed
- the ablation delivers under 60% of what it promises — the instrument is
  actually capable of detecting the difference
- scoring is blind to which strategy produced the path
- the whole evaluation is reproducible for a fixed seed

## Limitations

Worth stating plainly, because a panel will ask.

**Simulated mastery is a model, not a measurement.** Gain is computed with the
same noisy-OR update the planner uses, so the evaluation shares the planner's
assumption that finishing an item confers its skills at the modelled rate. It
measures *selection and sequencing quality* under a fixed learning model. It
cannot tell you the learning model itself is right — only a trial with real
learners does that.

**Synthetic learners have clean histories.** Real ones have half-finished
courses, skills from work that no catalog item represents, and self-reports
that are wrong in both directions.

**The catalog is 238 items.** Coverage and diversity numbers would move on a
catalog of 50,000.

The relative comparison survives all three, because every strategy is scored by
the same instrument under the same assumptions at the same hour budget.
