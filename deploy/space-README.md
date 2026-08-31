---
title: PathFinder
emoji: 🧭
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
license: mit
short_description: AI-powered personalized learning path recommender
---

# PathFinder

**AI-powered personalized learning path recommender.** Describe a goal in your
own words; PathFinder profiles what you already know, finds the skill gaps
between you and that goal, and generates an ordered roadmap of courses,
projects and assessments — explaining every recommendation from the arithmetic
that produced it.

Built for HCLTech Amplified Round 2 by **Team Critical Path**, REVA University.

## Try it

Type something like *"I want to become a generative AI engineer"*, answer the
three follow-up questions, and the roadmap generates. Click **Why this?** on any
item to see the six ranking components that placed it there.

This Space runs **fully offline** — no API key, no external calls. The header
shows "Offline mode", and every feature works in that state.

## How it works

| Stage | Technique |
|---|---|
| Goal understanding | Word + character TF-IDF → truncated SVD, 128 dimensions |
| Learner profiling | Noisy-OR mastery with recency decay |
| Gap analysis | Importance-weighted shortfall against a career target vector |
| Ranking | Six-signal hybrid with per-component attribution |
| Path planning | Greedy submodular max-coverage over a prerequisite DAG |
| Explanation | Derived from the ranker's own attributions, never narrated after the fact |

Source: https://github.com/Koushik926/pathfinder
