# PathFinder — Diagnostic Dump

Reproduced by replaying the identical conversation through the same code path.
The original live session was in-memory on Render and no longer exists; the engine
is deterministic, and this reproduction was verified to match the live run on all
six reported figures (380h / 63.3w / 26 items / 2 projects / 7 fills / 5 milestones)
before anything below was computed. **Nothing was regenerated or modified.**

Generated on: 2026-09-07 · catalog: 238 items, 116 skills, 22 roles

Conversation replayed:

```
> hi               -> intent=ask_goal
> don't know       -> intent=choose_role
> Data Scientist   -> intent=ask_level
> beginner         -> intent=ask_history
> nothing          -> intent=ask_pace
> 6                -> intent=ready
```

## 1. LEARNER PROFILE

```
goal_text            : ''     <-- EMPTY (see §11.1)
role_id              : 'data-scientist'
role_title           : 'Data Scientist'
experience_level     : 1  (1=beginner 2=intermediate 3=advanced)
hours_per_week       : 6.0
completed            : []   <-- no history, cold start
declared_skills      : {}
goal_skills          : {}
preferred_modalities : []   <-- empty
interests            : []
implied_level(derived): 1.0
```

**All known skills and mastery scores:** `compute_mastery` returned **0 entries** — the learner has no completions and no declared
skills, so the mastery vector is empty. Every skill is at mastery 0.0.

**Evidence used per mastery score:** NONE. There is no evidence for any skill.
`profile.completed` is empty and `profile.declared_skills` is empty, so neither
the noisy-OR completion loop nor the declared-skill fold-in executed at all.

**Skills already covered:** none (0 of 17 target skills met).
**Skills partially covered:** none.

> Note: the learner answered 'beginner' and 'nothing'. `experience_level=1` is
> recorded, but that is a *difficulty preference* input to `level_fit`; it does
> **not** create mastery. Self-declared level only becomes mastery via
> `declared_skills`, which the conversation never populated here.

## 2. GOAL REQUIREMENTS

Target: **Data Scientist** (`data-scientist`), family `Data & AI`. 17 required skills.

In this implementation **required mastery and goal weight are the same number**:
`Role.skills[skill_id]` is used both as the required level and as the importance
weight. `weighted_gap = gap * target`, so importance is applied by squaring the
target's influence. There is no separate weight field.

| Skill | Category | Required Mastery | Current Mastery | Gap | Goal Weight | Weighted Gap |
|---|---|---|---|---|---|---|
| Data Analysis | Data | 0.95 | 0.0 | 0.95 | 0.95 | **0.9025** |
| ML Foundations | Machine Learning | 0.95 | 0.0 | 0.95 | 0.95 | **0.9025** |
| Python Fundamentals | Programming | 0.9 | 0.0 | 0.9 | 0.9 | **0.81** |
| Statistics | Mathematics | 0.9 | 0.0 | 0.9 | 0.9 | **0.81** |
| Data Wrangling | Data | 0.85 | 0.0 | 0.85 | 0.85 | **0.7225** |
| Model Evaluation | Machine Learning | 0.85 | 0.0 | 0.85 | 0.85 | **0.7225** |
| SQL | Programming | 0.85 | 0.0 | 0.85 | 0.85 | **0.7225** |
| Classification | Machine Learning | 0.8 | 0.0 | 0.8 | 0.8 | **0.64** |
| Data Visualization | Data | 0.8 | 0.0 | 0.8 | 0.8 | **0.64** |
| Feature Engineering | Data | 0.8 | 0.0 | 0.8 | 0.8 | **0.64** |
| Regression Models | Machine Learning | 0.8 | 0.0 | 0.8 | 0.8 | **0.64** |
| Probability | Mathematics | 0.75 | 0.0 | 0.75 | 0.75 | **0.5625** |
| Communication & Storytelling | Product & Design | 0.65 | 0.0 | 0.65 | 0.65 | **0.4225** |
| Ensemble Methods | Machine Learning | 0.6 | 0.0 | 0.6 | 0.6 | **0.36** |
| Linear Algebra | Mathematics | 0.6 | 0.0 | 0.6 | 0.6 | **0.36** |
| Clustering & Dim. Reduction | Machine Learning | 0.55 | 0.0 | 0.55 | 0.55 | **0.3025** |
| Responsible AI | Machine Learning | 0.45 | 0.0 | 0.45 | 0.45 | **0.2025** |

Total target skills: **17** · unmet gaps carried into ranking: **17** · met: **0**
Initial total weighted gap mass: **10.3625**

## 3. PREREQUISITE ANALYSIS

The catalog models prerequisites **between items, not between skills**. There is
one edge type — `Item.prereqs` — and it is treated as a **hard** constraint by
`prerequisite_closure` and `topological_order`. There is no soft/useful
prerequisite concept in the implementation. **Soft prerequisites: NOT AVAILABLE.**

Items present in the path *only* because something else needs them: **7** (`is_prerequisite_fill=True`).

| Prerequisite item | Skills it teaches | Enables (in path) | Hard/Soft | In path only as prereq? |
|---|---|---|---|---|
| Linear Algebra for Machine Learning (`math-101`) | Linear Algebra | Machine Learning Specialization | hard | YES |
| Python Data Structures (`py-103`) | Data Structures, Python Fundamentals | Data Analysis with Python, Machine Learning Specialization, Assessment: Python Proficiency Check | hard | YES |
| Data Analysis with Python (`da-101`) | Data Analysis, Python Fundamentals | Pandas in Depth, Data Visualization with Matplotlib/Seaborn | hard | YES |
| Data Visualization with Matplotlib/Seaborn (`da-105`) | Data Visualization | Storytelling with Data | hard | YES |
| Intro to Machine Learning (`ml-102`) | Classification, ML Foundations | Supervised Learning with scikit-learn | hard | YES |
| Model Evaluation & Validation (`ml-105`) | Model Evaluation, Statistics | Ensemble Methods & Gradient Boosting, Responsible AI & Model Explainability, Project: Predictive Model End-to-End | hard | YES |
| Unsupervised Learning & Clustering (`ml-107`) | Clustering & Dim. Reduction, Linear Algebra | Dimensionality Reduction: PCA, t-SNE, UMAP | hard | YES |

**Prerequisite chains present in the final path** (item-level, `A -> B` means A required before B):

```
Linear Algebra for Machine Learning [math-101] *(prereq fill)*
  -> Machine Learning Specialization [ml-101]
Probability & Statistics for Data Science [math-104]
  -> Statistical Inference [math-105]
Python for Everybody: Getting Started [py-101]
  -> Python Data Structures [py-103] *(prereq fill)*
    -> Data Analysis with Python [da-101] *(prereq fill)*
      -> Pandas in Depth [da-102]
        -> Data Cleaning & Preprocessing [da-103]
        -> Exploratory Data Analysis in Practice [da-104]
          -> Project: End-to-End EDA on Public Data [da-p01]
        -> Intro to Machine Learning [ml-102] *(prereq fill)*
          -> Supervised Learning with scikit-learn [ml-103]
            -> Feature Engineering for ML [ml-104]
            -> Model Evaluation & Validation [ml-105] *(prereq fill)*
            -> Unsupervised Learning & Clustering [ml-107] *(prereq fill)*
            -> Assessment: ML Fundamentals Quiz [ml-a01]
      -> Data Visualization with Matplotlib/Seaborn [da-105] *(prereq fill)*
        -> Storytelling with Data [da-106]
    -> Machine Learning Specialization [ml-101]
    -> Assessment: Python Proficiency Check [py-a01]
SQL for Data Science [sql-101]
  -> Intermediate SQL: Window Functions [sql-102]
```

Total prerequisite edges inside the path: **23**. Items with no in-path prerequisite: **4**.

## 4. CANDIDATE SELECTION

Formula actually used (`recommender.recommend`):

```python
components = {
  'coverage' : raw_coverage / peak_coverage,   # raw = sum(item.skills[s] * remaining_gap[s])
  'semantic' : max(0, cos(goal_vector, item_vector)),
  'collab'   : item-item CF score, normalised to peak
  'level_fit': exp(-(item.level - learner_level)**2 / (2 * 0.85**2)),
  'quality'  : bayesian_rating * log_popularity, normalised
  'modality' : 1.0 if no preference else (1.0 if item.modality in preferred else 0.35),
}
contributions = {k: WEIGHTS[k] * v for k, v in components.items()}
score = sum(contributions.values())
if missing_prereqs: score *= max(0.4, 1 - 0.12 * len(missing_prereqs))
```

Greedy then re-ranks the top-12 shortlist by **efficiency**, which is what
actually decides the pick:

```python
gain       = sum(candidate.covers.values())          # marginal weighted gap closed
efficiency = (gain * candidate.score * KIND_BONUS[kind]) / hours ** 0.5
```

### 1. Project: End-to-End EDA on Public Data — `da-p01`

- provider: PathFinder Labs · kind: **project** · level: **2** · hours: **14** · modality: project · rating 4.7 · 58,000 learners · depth 5
- skills taught: Data Analysis (0.45), Data Visualization (0.35), Data Wrangling (0.3)
- prereqs: ['da-104']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.7012 | 0.38 | 0.2664 | 62.7% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 14.1% |
| quality | 0.7624 | 0.1 | 0.0762 | 17.9% |
| modality | 1.0 | 0.08 | 0.08 | 18.8% |
| **FINAL SCORE** | | | **0.42482** | 100% |

- marginal weighted gap closed (`gain`): **0.8468**
- KIND_BONUS: 1.3 · hours^0.5 = 3.742
- **efficiency = (0.8468 x 0.42482 x 1.3) / 3.742 = 0.12499**
- gaps it covers: Data Analysis=0.4061, Data Visualization=0.224, Data Wrangling=0.2167

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Exploratory Data Analysis in Practice (`da-104`) | 0.44326 | 0.9097 | 14 | 0.10777 | lower ranking score |
| Project: Predictive Model End-to-End (`ml-p01`) | 0.42538 | 0.8379 | 20 | 0.10361 | lower gain |
| Supervised Learning with scikit-learn (`ml-103`) | 0.4478 | 0.9249 | 16 | 0.10354 | more hours for similar gain |

### 2. Project: Predictive Model End-to-End — `ml-p01`

- provider: PathFinder Labs · kind: **project** · level: **2** · hours: **20** · modality: project · rating 4.8 · 72,000 learners · depth 7
- skills taught: ML Foundations (0.4), Feature Engineering (0.35), Model Evaluation (0.35)
- prereqs: ['ml-105']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.6938 | 0.38 | 0.2636 | 62.0% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 14.1% |
| quality | 0.7968 | 0.1 | 0.0797 | 18.7% |
| modality | 1.0 | 0.08 | 0.08 | 18.8% |
| **FINAL SCORE** | | | **0.42538** | 100% |

- marginal weighted gap closed (`gain`): **0.8379**
- KIND_BONUS: 1.3 · hours^0.5 = 4.472
- **efficiency = (0.8379 x 0.42538 x 1.3) / 4.472 = 0.10361**
- gaps it covers: ML Foundations=0.361, Model Evaluation=0.2529, Feature Engineering=0.224

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Supervised Learning with scikit-learn (`ml-103`) | 0.4478 | 0.9249 | 16 | 0.10354 | lower ranking score |
| Machine Learning Specialization (`ml-101`) | 0.51218 | 1.2077 | 40 | 0.09780 | more hours for similar gain |
| Intro to Machine Learning (`ml-102`) | 0.41502 | 0.5981 | 8 | 0.08776 | lower gain |

### 3. Supervised Learning with scikit-learn — `ml-103`

- provider: DataCamp · kind: **course** · level: **2** · hours: **16** · modality: interactive · rating 4.6 · 420,000 learners · depth 5
- skills taught: Classification (0.55), Regression Models (0.5), Model Evaluation (0.35)
- prereqs: ['ml-102']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.8521 | 0.38 | 0.3238 | 67.9% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 12.6% |
| quality | 0.7777 | 0.1 | 0.0778 | 16.3% |
| modality | 1.0 | 0.08 | 0.08 | 16.8% |
| **FINAL SCORE** | | | **0.47663** | 100% |

- marginal weighted gap closed (`gain`): **0.8364**
- KIND_BONUS: 1.0 · hours^0.5 = 4.000
- **efficiency = (0.8364 x 0.47663 x 1.0) / 4.000 = 0.09966**
- gaps it covers: Classification=0.352, Regression Models=0.32, Model Evaluation=0.1644

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Probability & Statistics for Data Science (`math-104`) | 0.56521 | 0.7425 | 24 | 0.08566 | lower gain |
| Machine Learning Specialization (`ml-101`) | 0.51218 | 0.9816 | 40 | 0.07949 | more hours for similar gain |
| Statistical Inference (`math-105`) | 0.44763 | 0.7639 | 22 | 0.07290 | lower gain |

### 4. Probability & Statistics for Data Science — `math-104`

- provider: edX · kind: **course** · level: **1** · hours: **24** · modality: video · rating 4.6 · 420,000 learners · depth 0
- skills taught: Probability (0.6), Statistics (0.5)
- prereqs: —

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.972 | 0.38 | 0.3694 | 57.1% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 18.5% |
| quality | 0.7777 | 0.1 | 0.0778 | 12.0% |
| modality | 1.0 | 0.08 | 0.08 | 12.4% |
| **FINAL SCORE** | | | **0.64713** | 100% |

- marginal weighted gap closed (`gain`): **0.7425**
- KIND_BONUS: 1.0 · hours^0.5 = 4.899
- **efficiency = (0.7425 x 0.64713 x 1.0) / 4.899 = 0.09808**
- gaps it covers: Statistics=0.405, Probability=0.3375

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Statistical Inference (`math-105`) | 0.52179 | 0.7639 | 22 | 0.08498 | lower ranking score |
| Exploratory Data Analysis in Practice (`da-104`) | 0.46843 | 0.6329 | 14 | 0.07923 | lower gain |
| Pandas in Depth (`da-102`) | 0.44919 | 0.4482 | 10 | 0.06367 | lower gain |

### 5. Exploratory Data Analysis in Practice — `da-104`

- provider: DataCamp · kind: **course** · level: **2** · hours: **14** · modality: interactive · rating 4.6 · 350,000 learners · depth 4
- skills taught: Data Analysis (0.5), Data Visualization (0.4), Statistics (0.25)
- prereqs: ['da-102']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.8332 | 0.38 | 0.3166 | 67.4% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 12.8% |
| quality | 0.774 | 0.1 | 0.0774 | 16.5% |
| modality | 1.0 | 0.08 | 0.08 | 17.0% |
| **FINAL SCORE** | | | **0.47** | 100% |

- marginal weighted gap closed (`gain`): **0.5516**
- KIND_BONUS: 1.0 · hours^0.5 = 3.742
- **efficiency = (0.5516 x 0.47 x 1.0) / 3.742 = 0.06929**
- gaps it covers: Data Analysis=0.2696, Data Visualization=0.1608, Statistics=0.1212

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Pandas in Depth (`da-102`) | 0.47939 | 0.4482 | 10 | 0.06795 | lower gain |
| Intermediate SQL: Window Functions (`sql-102`) | 0.44988 | 0.5052 | 12 | 0.06561 | lower gain |
| Python for Everybody: Getting Started (`py-101`) | 0.5462 | 0.4455 | 18 | 0.05735 | lower gain |

### 6. Python for Everybody: Getting Started — `py-101`

- provider: Coursera · kind: **course** · level: **1** · hours: **18** · modality: video · rating 4.8 · 2,400,000 learners · depth 0
- skills taught: Python Fundamentals (0.55)
- prereqs: —

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.673 | 0.38 | 0.2557 | 46.8% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 22.0% |
| quality | 0.9048 | 0.1 | 0.0905 | 16.6% |
| modality | 1.0 | 0.08 | 0.08 | 14.6% |
| **FINAL SCORE** | | | **0.5462** | 100% |

- marginal weighted gap closed (`gain`): **0.4455**
- KIND_BONUS: 1.0 · hours^0.5 = 4.243
- **efficiency = (0.4455 x 0.5462 x 1.0) / 4.243 = 0.05735**
- gaps it covers: Python Fundamentals=0.4455

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| SQL for Data Science (`sql-101`) | 0.52828 | 0.4335 | 16 | 0.05725 | lower gain |
| Feature Engineering for ML (`ml-104`) | 0.41361 | 0.4331 | 10 | 0.05665 | lower gain |
| Intermediate SQL: Window Functions (`sql-102`) | 0.42473 | 0.4554 | 12 | 0.05584 | lower ranking score |

### 7. SQL for Data Science — `sql-101`

- provider: Coursera · kind: **course** · level: **1** · hours: **16** · modality: interactive · rating 4.6 · 950,000 learners · depth 0
- skills taught: SQL (0.6), Database Design (0.2)
- prereqs: —

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.6548 | 0.38 | 0.2488 | 47.1% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 22.7% |
| quality | 0.7944 | 0.1 | 0.0794 | 15.0% |
| modality | 1.0 | 0.08 | 0.08 | 15.1% |
| **FINAL SCORE** | | | **0.52828** | 100% |

- marginal weighted gap closed (`gain`): **0.4335**
- KIND_BONUS: 1.0 · hours^0.5 = 4.000
- **efficiency = (0.4335 x 0.52828 x 1.0) / 4.000 = 0.05725**
- gaps it covers: SQL=0.4335

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Feature Engineering for ML (`ml-104`) | 0.41361 | 0.4331 | 10 | 0.05665 | lower gain |
| Intermediate SQL: Window Functions (`sql-102`) | 0.42473 | 0.4554 | 12 | 0.05584 | lower ranking score |
| Data Cleaning & Preprocessing (`da-103`) | 0.4249 | 0.4545 | 12 | 0.05575 | lower ranking score |

### 8. Feature Engineering for ML — `ml-104`

- provider: Kaggle Learn · kind: **course** · level: **2** · hours: **10** · modality: interactive · rating 4.7 · 330,000 learners · depth 6
- skills taught: Feature Engineering (0.7), Data Wrangling (0.3)
- prereqs: ['ml-103']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.6542 | 0.38 | 0.2486 | 60.1% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 14.5% |
| quality | 0.8133 | 0.1 | 0.0813 | 19.7% |
| modality | 1.0 | 0.08 | 0.08 | 19.3% |
| **FINAL SCORE** | | | **0.41361** | 100% |

- marginal weighted gap closed (`gain`): **0.4331**
- KIND_BONUS: 1.0 · hours^0.5 = 3.162
- **efficiency = (0.4331 x 0.41361 x 1.0) / 3.162 = 0.05665**
- gaps it covers: Feature Engineering=0.2814, Data Wrangling=0.1517

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Data Cleaning & Preprocessing (`da-103`) | 0.4249 | 0.4545 | 12 | 0.05575 | more hours for similar gain |
| Machine Learning Specialization (`ml-101`) | 0.51218 | 0.6620 | 40 | 0.05361 | more hours for similar gain |
| Intro to Machine Learning (`ml-102`) | 0.42146 | 0.3406 | 8 | 0.05075 | lower gain |

### 9. Machine Learning Specialization — `ml-101`

- provider: DeepLearning.AI · kind: **course** · level: **1** · hours: **40** · modality: video · rating 4.9 · 1,500,000 learners · depth 2
- skills taught: ML Foundations (0.7), Regression Models (0.5), Classification (0.4)
- prereqs: ['py-103', 'math-101']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 1.0 | 0.38 | 0.38 | 74.2% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 23.4% |
| quality | 0.9392 | 0.1 | 0.0939 | 18.3% |
| modality | 1.0 | 0.08 | 0.08 | 15.6% |
| **FINAL SCORE** | | | **0.51218** | 100% |

- marginal weighted gap closed (`gain`): **0.6620**
- KIND_BONUS: 1.0 · hours^0.5 = 6.325
- **efficiency = (0.6620 x 0.51218 x 1.0) / 6.325 = 0.05361**
- gaps it covers: ML Foundations=0.4056, Regression Models=0.15, Classification=0.1064

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Intro to Machine Learning (`ml-102`) | 0.42146 | 0.3406 | 8 | 0.05075 | lower gain |
| Ensemble Methods & Gradient Boosting (`ml-106`) | 0.4118 | 0.4228 | 12 | 0.05026 | lower gain |
| Pandas in Depth (`da-102`) | 0.38569 | 0.2627 | 10 | 0.03204 | lower gain |

### 10. Ensemble Methods & Gradient Boosting — `ml-106`

- provider: Kaggle Learn · kind: **course** · level: **2** · hours: **12** · modality: interactive · rating 4.8 · 310,000 learners · depth 7
- skills taught: Ensemble Methods (0.75), Classification (0.3), Model Evaluation (0.25)
- prereqs: ['ml-105']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 1.0 | 0.38 | 0.38 | 71.3% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 11.3% |
| quality | 0.8519 | 0.1 | 0.0852 | 16.0% |
| modality | 1.0 | 0.08 | 0.08 | 15.0% |
| **FINAL SCORE** | | | **0.53263** | 100% |

- marginal weighted gap closed (`gain`): **0.3859**
- KIND_BONUS: 1.0 · hours^0.5 = 3.464
- **efficiency = (0.3859 x 0.53263 x 1.0) / 3.464 = 0.05933**
- gaps it covers: Ensemble Methods=0.27, Model Evaluation=0.073, Classification=0.0429

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Storytelling with Data (`da-106`) | 0.45069 | 0.2957 | 10 | 0.04214 | lower gain |
| Presenting & Storytelling for Tech (`com-102`) | 0.445 | 0.2958 | 10 | 0.04163 | lower gain |
| Model Evaluation & Validation (`ml-105`) | 0.45906 | 0.3097 | 12 | 0.04104 | lower gain |

### 11. Storytelling with Data — `da-106`

- provider: Coursera · kind: **course** · level: **2** · hours: **10** · modality: video · rating 4.7 · 280,000 learners · depth 4
- skills taught: Communication & Storytelling (0.5), Data Visualization (0.4)
- prereqs: ['da-105']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.8774 | 0.38 | 0.3334 | 68.3% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 12.3% |
| quality | 0.8091 | 0.1 | 0.0809 | 16.6% |
| modality | 1.0 | 0.08 | 0.08 | 16.4% |
| **FINAL SCORE** | | | **0.48787** | 100% |

- marginal weighted gap closed (`gain`): **0.2957**
- KIND_BONUS: 1.0 · hours^0.5 = 3.162
- **efficiency = (0.2957 x 0.48787 x 1.0) / 3.162 = 0.04562**
- gaps it covers: Communication & Storytelling=0.2113, Data Visualization=0.0844

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Presenting & Storytelling for Tech (`com-102`) | 0.48219 | 0.2958 | 10 | 0.04510 | lower ranking score |
| Dimensionality Reduction: PCA, t-SNE, UMAP (`clu-101`) | 0.44701 | 0.3075 | 10 | 0.04347 | lower ranking score |
| Unsupervised Learning & Clustering (`ml-107`) | 0.50529 | 0.3169 | 14 | 0.04280 | more hours for similar gain |

### 12. Dimensionality Reduction: PCA, t-SNE, UMAP — `clu-101`

- provider: PathFinder Labs · kind: **course** · level: **3** · hours: **10** · modality: mixed · rating 4.6 · 57,000 learners · depth 7
- skills taught: Clustering & Dim. Reduction (0.6), Linear Algebra (0.35)
- prereqs: ['ml-107']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.9125 | 0.38 | 0.3467 | 77.6% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.0628 | 0.12 | 0.0075 | 1.7% |
| quality | 0.737 | 0.1 | 0.0737 | 16.5% |
| modality | 1.0 | 0.08 | 0.08 | 17.9% |
| **FINAL SCORE** | | | **0.44701** | 100% |

- marginal weighted gap closed (`gain`): **0.3075**
- KIND_BONUS: 1.0 · hours^0.5 = 3.162
- **efficiency = (0.3075 x 0.44701 x 1.0) / 3.162 = 0.04347**
- gaps it covers: Clustering & Dim. Reduction=0.1815, Linear Algebra=0.126

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Unsupervised Learning & Clustering (`ml-107`) | 0.50529 | 0.3169 | 14 | 0.04280 | more hours for similar gain |
| Pandas in Depth (`da-102`) | 0.51366 | 0.2627 | 10 | 0.04267 | lower gain |
| Statistical Inference (`math-105`) | 0.52179 | 0.3370 | 22 | 0.03749 | more hours for similar gain |

### 13. Pandas in Depth — `da-102`

- provider: Kaggle Learn · kind: **course** · level: **1** · hours: **10** · modality: interactive · rating 4.8 · 690,000 learners · depth 3
- skills taught: Data Analysis (0.55), Data Wrangling (0.3)
- prereqs: ['da-101']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.7795 | 0.38 | 0.2962 | 57.7% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 23.4% |
| quality | 0.8749 | 0.1 | 0.0875 | 17.0% |
| modality | 1.0 | 0.08 | 0.08 | 15.6% |
| **FINAL SCORE** | | | **0.51366** | 100% |

- marginal weighted gap closed (`gain`): **0.2627**
- KIND_BONUS: 1.0 · hours^0.5 = 3.162
- **efficiency = (0.2627 x 0.51366 x 1.0) / 3.162 = 0.04267**
- gaps it covers: Data Analysis=0.1594, Data Wrangling=0.1033

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Statistical Inference (`math-105`) | 0.52179 | 0.3370 | 22 | 0.03749 | more hours for similar gain |
| Data Cleaning & Preprocessing (`da-103`) | 0.45123 | 0.2579 | 12 | 0.03359 | lower gain |
| Intermediate SQL: Window Functions (`sql-102`) | 0.44544 | 0.2527 | 12 | 0.03249 | lower gain |

### 14. Assessment: Python Proficiency Check — `py-a01`

- provider: PathFinder Labs · kind: **assessment** · level: **1** · hours: **2** · modality: interactive · rating 4.5 · 96,000 learners · depth 2
- skills taught: Python Fundamentals (0.3)
- prereqs: ['py-103']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.4027 | 0.38 | 0.153 | 40.9% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 1.0 | 0.12 | 0.12 | 32.1% |
| quality | 0.7169 | 0.1 | 0.0717 | 19.2% |
| modality | 1.0 | 0.08 | 0.08 | 21.4% |
| **FINAL SCORE** | | | **0.37374** | 100% |

- marginal weighted gap closed (`gain`): **0.1357**
- KIND_BONUS: 1.15 · hours^0.5 = 1.414
- **efficiency = (0.1357 x 0.37374 x 1.15) / 1.414 = 0.04124**
- gaps it covers: Python Fundamentals=0.1357

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Statistical Inference (`math-105`) | 0.52179 | 0.3370 | 22 | 0.03749 | more hours for similar gain |
| Project: Build a CLI Expense Tracker (`py-p01`) | 0.41981 | 0.1809 | 10 | 0.03122 | more hours for similar gain |
| Model Evaluation & Validation (`ml-105`) | 0.43162 | 0.2428 | 12 | 0.03025 | more hours for similar gain |

### 15. Statistical Inference — `math-105`

- provider: Coursera · kind: **course** · level: **2** · hours: **22** · modality: video · rating 4.5 · 260,000 learners · depth 1
- skills taught: Statistics (0.7), Probability (0.35)
- prereqs: ['math-104']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 1.0 | 0.38 | 0.38 | 72.8% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 11.5% |
| quality | 0.7288 | 0.1 | 0.0729 | 14.0% |
| modality | 1.0 | 0.08 | 0.08 | 15.3% |
| **FINAL SCORE** | | | **0.52179** | 100% |

- marginal weighted gap closed (`gain`): **0.3370**
- KIND_BONUS: 1.0 · hours^0.5 = 4.690
- **efficiency = (0.3370 x 0.52179 x 1.0) / 4.690 = 0.03749**
- gaps it covers: Statistics=0.2539, Probability=0.0831

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Model Evaluation & Validation (`ml-105`) | 0.43162 | 0.2428 | 12 | 0.03025 | lower gain |
| Intermediate SQL: Window Functions (`sql-102`) | 0.41885 | 0.2259 | 12 | 0.02731 | lower gain |
| Responsible AI & Model Explainability (`ml-110`) | 0.39421 | 0.2026 | 10 | 0.02526 | lower gain |

### 16. Assessment: ML Fundamentals Quiz — `ml-a01`

- provider: PathFinder Labs · kind: **assessment** · level: **2** · hours: **2** · modality: interactive · rating 4.6 · 156,000 learners · depth 6
- skills taught: ML Foundations (0.3), Model Evaluation (0.25)
- prereqs: ['ml-103']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.5728 | 0.38 | 0.2177 | 57.1% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 15.8% |
| quality | 0.7575 | 0.1 | 0.0758 | 19.9% |
| modality | 1.0 | 0.08 | 0.08 | 21.0% |
| **FINAL SCORE** | | | **0.38147** | 100% |

- marginal weighted gap closed (`gain`): **0.1294**
- KIND_BONUS: 1.15 · hours^0.5 = 1.414
- **efficiency = (0.1294 x 0.38147 x 1.15) / 1.414 = 0.04014**
- gaps it covers: ML Foundations=0.0787, Model Evaluation=0.0507

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Intermediate SQL: Window Functions (`sql-102`) | 0.52909 | 0.2259 | 12 | 0.03450 | more hours for similar gain |
| Responsible AI & Model Explainability (`ml-110`) | 0.49308 | 0.2026 | 10 | 0.03159 | more hours for similar gain |
| Data Cleaning & Preprocessing (`da-103`) | 0.4711 | 0.1863 | 12 | 0.02534 | more hours for similar gain |

### 17. Intermediate SQL: Window Functions — `sql-102`

- provider: Mode Analytics · kind: **course** · level: **2** · hours: **12** · modality: interactive · rating 4.7 · 310,000 learners · depth 1
- skills taught: SQL (0.55), Data Analysis (0.2)
- prereqs: ['sql-101']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 1.0 | 0.38 | 0.38 | 71.8% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 11.4% |
| quality | 0.8117 | 0.1 | 0.0812 | 15.3% |
| modality | 1.0 | 0.08 | 0.08 | 15.1% |
| **FINAL SCORE** | | | **0.52909** | 100% |

- marginal weighted gap closed (`gain`): **0.2259**
- KIND_BONUS: 1.0 · hours^0.5 = 3.464
- **efficiency = (0.2259 x 0.52909 x 1.0) / 3.464 = 0.03450**
- gaps it covers: SQL=0.1947, Data Analysis=0.0312

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Responsible AI & Model Explainability (`ml-110`) | 0.46718 | 0.1851 | 10 | 0.02735 | lower gain |
| Data Cleaning & Preprocessing (`da-103`) | 0.4711 | 0.1863 | 12 | 0.02534 | lower gain |
| Project: Build a CLI Expense Tracker (`py-p01`) | 0.43852 | 0.1339 | 10 | 0.02414 | lower gain |

### 18. Responsible AI & Model Explainability — `ml-110`

- provider: Google Cloud · kind: **course** · level: **2** · hours: **10** · modality: mixed · rating 4.7 · 165,000 learners · depth 7
- skills taught: Responsible AI (0.75), Model Evaluation (0.25)
- prereqs: ['ml-105']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 0.9936 | 0.38 | 0.3776 | 71.9% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 11.4% |
| quality | 0.7945 | 0.1 | 0.0794 | 15.1% |
| modality | 1.0 | 0.08 | 0.08 | 15.2% |
| **FINAL SCORE** | | | **0.52542** | 100% |

- marginal weighted gap closed (`gain`): **0.1851**
- KIND_BONUS: 1.0 · hours^0.5 = 3.162
- **efficiency = (0.1851 x 0.52542 x 1.0) / 3.162 = 0.03075**
- gaps it covers: Responsible AI=0.1519, Model Evaluation=0.0332

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Data Cleaning & Preprocessing (`da-103`) | 0.52972 | 0.1863 | 12 | 0.02849 | more hours for similar gain |
| Project: Build a CLI Expense Tracker (`py-p01`) | 0.48065 | 0.1339 | 10 | 0.02646 | lower gain |
| Automate the Boring Stuff with Python (`py-102`) | 0.5509 | 0.1674 | 22 | 0.01966 | lower gain |

### 19. Data Cleaning & Preprocessing — `da-103`

- provider: Kaggle Learn · kind: **course** · level: **2** · hours: **12** · modality: interactive · rating 4.7 · 410,000 learners · depth 4
- skills taught: Data Wrangling (0.7), Feature Engineering (0.25)
- prereqs: ['da-102']

| component | raw value | weight | contribution | share of score |
|---|---|---|---|---|
| coverage | 1.0 | 0.38 | 0.38 | 71.7% |
| semantic | 0.0 | 0.18 | 0.0 | 0.0% |
| collab | 0.0 | 0.14 | 0.0 | 0.0% |
| level_fit | 0.5006 | 0.12 | 0.0601 | 11.3% |
| quality | 0.8188 | 0.1 | 0.0819 | 15.5% |
| modality | 1.0 | 0.08 | 0.08 | 15.1% |
| **FINAL SCORE** | | | **0.52972** | 100% |

- marginal weighted gap closed (`gain`): **0.1863**
- KIND_BONUS: 1.0 · hours^0.5 = 3.464
- **efficiency = (0.1863 x 0.52972 x 1.0) / 3.464 = 0.02849**
- gaps it covers: Data Wrangling=0.1694, Feature Engineering=0.0169

Beaten at this step by efficiency:

| runner-up | score | gain | hours | efficiency | why it lost |
|---|---|---|---|---|---|
| Project: Build a CLI Expense Tracker (`py-p01`) | 0.48065 | 0.1339 | 10 | 0.02646 | lower gain |
| Automate the Boring Stuff with Python (`py-102`) | 0.5509 | 0.1674 | 22 | 0.01966 | lower gain |
| Intro to Machine Learning (`ml-102`) | 0.43286 | 0.1022 | 8 | 0.01564 | lower gain |

## 5. REJECTED / NOT SELECTED ITEMS

Ranked against the **initial** gap vector (all 238 items, top scorers not in the path).
Note `k` is a cap on returned candidates, so most rejections are *implicit*: the
item never entered a top-12 shortlist at any step.

| Item | Score | Coverage | Hours | Level | Reason not selected |
|---|---|---|---|---|---|
| Automate the Boring Stuff with Python (`py-102`) | 0.36257 | 0.4050 | 22 | 1 | unmet prereqs (1), score x0.88 |
| Project: Kaggle Competition Sprint (`ml-p02`) | 0.34429 | 0.7029 | 30 | 3 | unmet prereqs (1), score x0.88 |
| Essence of Linear Algebra (`math-102`) | 0.3441 | 0.1620 | 6 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0228) |
| Project: Build a CLI Expense Tracker (`py-p01`) | 0.33002 | 0.3240 | 10 | 1 | unmet prereqs (1), score x0.88 |
| Technical Writing for Engineers (`com-101`) | 0.32131 | 0.1268 | 8 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0144) |
| Behavioural Interviews & Resume Craft (`car-102`) | 0.31942 | 0.1479 | 8 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0167) |
| Product Management Fundamentals (`pm-101`) | 0.31811 | 0.1268 | 16 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0101) |
| Spreadsheets for Analysts (`excel-101`) | 0.31249 | 0.1354 | 8 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0150) |
| Agile & Scrum in Practice (`pm-102`) | 0.30512 | 0.0845 | 10 | 1 | redundant after earlier picks — marginal gain collapsed (initial eff 0.0082) |
| Applied Time Series with Prophet & ARIMA (`ts-101`) | 0.30361 | 0.4235 | 16 | 2 | unmet prereqs (1), score x0.88 |
| Assessment: Data Analyst Skills Audit (`da-a01`) | 0.30164 | 0.5793 | 2 | 2 | unmet prereqs (2), score x0.76 |
| Power BI for Business Analytics (`da-107`) | 0.29799 | 0.1920 | 16 | 1 | unmet prereqs (1), score x0.88 |
| Tableau Desktop Essentials (`da-108`) | 0.29364 | 0.1920 | 14 | 1 | unmet prereqs (1), score x0.88 |
| The Missing Semester of Your CS Education (`sh-101`) | 0.29059 | 0.0000 | 12 | 1 | **zero gap coverage** — teaches nothing this role requires |
| Responsive Web Design (`web-101`) | 0.29018 | 0.0000 | 25 | 1 | **zero gap coverage** — teaches nothing this role requires |

Items scoring >0 but covering **zero** gap: **158** of 238. These can never be picked — greedy skips any candidate with `gain <= 0`.

Explicit stop condition reached: coverage 0.8382 >= COVERAGE_TARGET 0.82 after 19 greedy picks (MAX_SELECTED=22 not reached).

## 6. PATH CONSTRUCTION (greedy selection order)

This is **selection** order, not the final study order (see §7).

**Step 1: Project: End-to-End EDA on Public Data** (`da-p01`) — 14h, project, level 2

- remaining weighted gap mass before: **10.3625** -> after: **9.5444**
- readiness before: **0.0000** -> after: **0.0716**  (delta **+0.0716**)
- efficiency **0.12499** = (gain 0.8468 x score 0.42482 x bonus 1.3) / 3.742
- gaps moved:
    - Data Analysis: 0.9025 -> 0.5391  (closed 0.3634)
    - Data Visualization: 0.6400 -> 0.4020  (closed 0.2380)
    - Data Wrangling: 0.7225 -> 0.5057  (closed 0.2168)

**Step 2: Project: Predictive Model End-to-End** (`ml-p01`) — 20h, project, level 2

- remaining weighted gap mass before: **9.5444** -> after: **8.7305**
- readiness before: **0.0716** -> after: **0.1433**  (delta **+0.0717**)
- efficiency **0.10361** = (gain 0.8379 x score 0.42538 x bonus 1.3) / 4.472
- gaps moved:
    - ML Foundations: 0.9025 -> 0.5795  (closed 0.3230)
    - Model Evaluation: 0.7225 -> 0.4696  (closed 0.2529)
    - Feature Engineering: 0.6400 -> 0.4020  (closed 0.2380)

**Step 3: Supervised Learning with scikit-learn** (`ml-103`) — 16h, course, level 2

- remaining weighted gap mass before: **8.7305** -> after: **7.8389**
- readiness before: **0.1433** -> after: **0.2277**  (delta **+0.0844**)
- efficiency **0.09966** = (gain 0.8364 x score 0.47663 x bonus 1.0) / 4.000
- gaps moved:
    - Classification: 0.6400 -> 0.2660  (closed 0.3740)
    - Regression Models: 0.6400 -> 0.3000  (closed 0.3400)
    - Model Evaluation: 0.4696 -> 0.2920  (closed 0.1776)

**Step 4: Probability & Statistics for Data Science** (`math-104`) — 24h, course, level 1

- remaining weighted gap mass before: **7.8389** -> after: **7.1886**
- readiness before: **0.2277** -> after: **0.2886**  (delta **+0.0609**)
- efficiency **0.09808** = (gain 0.7425 x score 0.64713 x bonus 1.0) / 4.899
- gaps moved:
    - Statistics: 0.8100 -> 0.4849  (closed 0.3251)
    - Probability: 0.5625 -> 0.2374  (closed 0.3251)

**Step 5: Exploratory Data Analysis in Practice** (`da-104`) — 14h, course, level 2

- remaining weighted gap mass before: **7.1886** -> after: **6.6260**
- readiness before: **0.2886** -> after: **0.3374**  (delta **+0.0488**)
- efficiency **0.06929** = (gain 0.5516 x score 0.47 x bonus 1.0) / 3.742
- gaps moved:
    - Data Analysis: 0.5391 -> 0.2898  (closed 0.2493)
    - Data Visualization: 0.4020 -> 0.2109  (closed 0.1911)
    - Statistics: 0.4849 -> 0.3627  (closed 0.1222)

**Step 6: Python for Everybody: Getting Started** (`py-101`) — 18h, course, level 1

- remaining weighted gap mass before: **6.6260** -> after: **6.2684**
- readiness before: **0.3374** -> after: **0.3679**  (delta **+0.0305**)
- efficiency **0.05735** = (gain 0.4455 x score 0.5462 x bonus 1.0) / 4.243
- gaps moved:
    - Python Fundamentals: 0.8100 -> 0.4524  (closed 0.3576)

**Step 7: SQL for Data Science** (`sql-101`) — 16h, course, level 1

- remaining weighted gap mass before: **6.2684** -> after: **5.8999**
- readiness before: **0.3679** -> after: **0.4011**  (delta **+0.0332**)
- efficiency **0.05725** = (gain 0.4335 x score 0.52828 x bonus 1.0) / 4.000
- gaps moved:
    - SQL: 0.7225 -> 0.3540  (closed 0.3685)

**Step 8: Feature Engineering for ML** (`ml-104`) — 10h, course, level 2

- remaining weighted gap mass before: **5.8999** -> after: **5.4041**
- readiness before: **0.4011** -> after: **0.4477**  (delta **+0.0466**)
- efficiency **0.05665** = (gain 0.4331 x score 0.41361 x bonus 1.0) / 3.162
- gaps moved:
    - Feature Engineering: 0.4020 -> 0.0676  (closed 0.3344)
    - Data Wrangling: 0.5057 -> 0.3443  (closed 0.1615)

**Step 9: Machine Learning Specialization** (`ml-101`) — 40h, course, level 1

- remaining weighted gap mass before: **5.4041** -> after: **4.7977**
- readiness before: **0.4477** -> after: **0.5010**  (delta **+0.0533**)
- efficiency **0.05361** = (gain 0.6620 x score 0.51218 x bonus 1.0) / 6.325
- gaps moved:
    - ML Foundations: 0.5795 -> 0.2624  (closed 0.3171)
    - Regression Models: 0.3000 -> 0.1338  (closed 0.1662)
    - Classification: 0.2660 -> 0.1429  (closed 0.1231)

**Step 10: Ensemble Methods & Gradient Boosting** (`ml-106`) — 12h, course, level 2

- remaining weighted gap mass before: **4.7977** -> after: **4.2713**
- readiness before: **0.5010** -> after: **0.5624**  (delta **+0.0614**)
- efficiency **0.05933** = (gain 0.3859 x score 0.53263 x bonus 1.0) / 3.464
- gaps moved:
    - Ensemble Methods: 0.3600 -> 0.0000  (closed 0.3600)
    - Model Evaluation: 0.2920 -> 0.2028  (closed 0.0891)
    - Classification: 0.1429 -> 0.0657  (closed 0.0772)

**Step 11: Storytelling with Data** (`da-106`) — 10h, course, level 2

- remaining weighted gap mass before: **4.2713** -> after: **3.8689**
- readiness before: **0.5624** -> after: **0.6070**  (delta **+0.0446**)
- efficiency **0.04562** = (gain 0.2957 x score 0.48787 x bonus 1.0) / 3.162
- gaps moved:
    - Communication & Storytelling: 0.4225 -> 0.1462  (closed 0.2763)
    - Data Visualization: 0.2109 -> 0.0848  (closed 0.1261)

**Step 12: Dimensionality Reduction: PCA, t-SNE, UMAP** (`clu-101`) — 10h, course, level 3

- remaining weighted gap mass before: **3.8689** -> after: **3.3612**
- readiness before: **0.6070** -> after: **0.6754**  (delta **+0.0684**)
- efficiency **0.04347** = (gain 0.3075 x score 0.44701 x bonus 1.0) / 3.162
- gaps moved:
    - Clustering & Dim. Reduction: 0.3025 -> 0.0000  (closed 0.3025)
    - Linear Algebra: 0.3600 -> 0.1547  (closed 0.2053)

**Step 13: Pandas in Depth** (`da-102`) — 10h, course, level 1

- remaining weighted gap mass before: **3.3612** -> after: **3.1249**
- readiness before: **0.6754** -> after: **0.6954**  (delta **+0.0200**)
- efficiency **0.04267** = (gain 0.2627 x score 0.51366 x bonus 1.0) / 3.162
- gaps moved:
    - Data Analysis: 0.2898 -> 0.1558  (closed 0.1340)
    - Data Wrangling: 0.3443 -> 0.2420  (closed 0.1023)

**Step 14: Assessment: Python Proficiency Check** (`py-a01`) — 2h, assessment, level 1

- remaining weighted gap mass before: **3.1249** -> after: **3.0073**
- readiness before: **0.6954** -> after: **0.7054**  (delta **+0.0100**)
- efficiency **0.04124** = (gain 0.1357 x score 0.37374 x bonus 1.15) / 1.414
- gaps moved:
    - Python Fundamentals: 0.4524 -> 0.3348  (closed 0.1176)

**Step 15: Statistical Inference** (`math-105`) — 22h, course, level 2

- remaining weighted gap mass before: **3.0073** -> after: **2.6115**
- readiness before: **0.7054** -> after: **0.7413**  (delta **+0.0359**)
- efficiency **0.03749** = (gain 0.3370 x score 0.52179 x bonus 1.0) / 4.690
- gaps moved:
    - Statistics: 0.3627 -> 0.0933  (closed 0.2694)
    - Probability: 0.2374 -> 0.1110  (closed 0.1264)

**Step 16: Assessment: ML Fundamentals Quiz** (`ml-a01`) — 2h, assessment, level 2

- remaining weighted gap mass before: **2.6115** -> after: **2.4623**
- readiness before: **0.7413** -> after: **0.7540**  (delta **+0.0127**)
- efficiency **0.04014** = (gain 0.1294 x score 0.38147 x bonus 1.15) / 1.414
- gaps moved:
    - ML Foundations: 0.2624 -> 0.1834  (closed 0.0790)
    - Model Evaluation: 0.2028 -> 0.1326  (closed 0.0702)

**Step 17: Intermediate SQL: Window Functions** (`sql-102`) — 12h, course, level 2

- remaining weighted gap mass before: **2.4623** -> after: **2.2027**
- readiness before: **0.7540** -> after: **0.7771**  (delta **+0.0231**)
- efficiency **0.03450** = (gain 0.2259 x score 0.52909 x bonus 1.0) / 3.464
- gaps moved:
    - SQL: 0.3540 -> 0.1289  (closed 0.2251)
    - Data Analysis: 0.1558 -> 0.1212  (closed 0.0346)

**Step 18: Responsible AI & Model Explainability** (`ml-110`) — 10h, course, level 2

- remaining weighted gap mass before: **2.2027** -> after: **1.9449**
- readiness before: **0.7771** -> after: **0.8165**  (delta **+0.0394**)
- efficiency **0.03075** = (gain 0.1851 x score 0.52542 x bonus 1.0) / 3.162
- gaps moved:
    - Responsible AI: 0.2025 -> 0.0000  (closed 0.2025)
    - Model Evaluation: 0.1326 -> 0.0774  (closed 0.0553)

**Step 19: Data Cleaning & Preprocessing** (`da-103`) — 12h, course, level 2

- remaining weighted gap mass before: **1.9449** -> after: **1.6766**
- readiness before: **0.8165** -> after: **0.8410**  (delta **+0.0245**)
- efficiency **0.02849** = (gain 0.1863 x score 0.52972 x bonus 1.0) / 3.464
- gaps moved:
    - Data Wrangling: 0.2420 -> 0.0222  (closed 0.2199)
    - Feature Engineering: 0.0676 -> 0.0192  (closed 0.0484)

## 7. PREREQUISITE CLOSURE + SEQUENCING

Greedy selected **19** items; `_ensure_projects` added **0**; prerequisite closure added **7** more.
Final path size: **26**.

Priority propagation (`generate_path`): a prerequisite inherits the priority of
the most urgent thing it unlocks, otherwise fillers (priority 0) sort to the back
and drag their dependents with them.

```python
while changed:
    for item_id in everything:
        for prereq in catalog.items[item_id].prereqs:
            if prereq in everything and priority[prereq] < priority[item_id]:
                priority[prereq] = priority[item_id]
```

Then Kahn's algorithm with this tie-break (`_learning_order`):

```python
key = (career_stage, item.level, item.depth, -priority, item_id)
# career_stage = 1 if dominant skill's category in {'Career'} else 0
```

**Final order with sort keys:**

| # | Item | stage | level | depth | priority | fill? |
|---|---|---|---|---|---|---|
| 1 | Probability & Statistics for Data Science | 0 | 1 | 0 | 0.64713 |  |
| 2 | Python for Everybody: Getting Started | 0 | 1 | 0 | 0.54620 |  |
| 3 | SQL for Data Science | 0 | 1 | 0 | 0.52909 |  |
| 4 | Linear Algebra for Machine Learning | 0 | 1 | 0 | 0.51218 | **YES** |
| 5 | Python Data Structures | 0 | 1 | 1 | 0.53263 | **YES** |
| 6 | Data Analysis with Python | 0 | 1 | 2 | 0.53263 | **YES** |
| 7 | Machine Learning Specialization | 0 | 1 | 2 | 0.51218 |  |
| 8 | Assessment: Python Proficiency Check | 0 | 1 | 2 | 0.37374 |  |
| 9 | Pandas in Depth | 0 | 1 | 3 | 0.53263 |  |
| 10 | Data Visualization with Matplotlib/Seaborn | 0 | 1 | 3 | 0.48787 | **YES** |
| 11 | Intro to Machine Learning | 0 | 1 | 4 | 0.53263 | **YES** |
| 12 | Intermediate SQL: Window Functions | 0 | 2 | 1 | 0.52909 |  |
| 13 | Statistical Inference | 0 | 2 | 1 | 0.52179 |  |
| 14 | Data Cleaning & Preprocessing | 0 | 2 | 4 | 0.52972 |  |
| 15 | Storytelling with Data | 0 | 2 | 4 | 0.48787 |  |
| 16 | Exploratory Data Analysis in Practice | 0 | 2 | 4 | 0.47000 |  |
| 17 | Supervised Learning with scikit-learn | 0 | 2 | 5 | 0.53263 |  |
| 18 | Project: End-to-End EDA on Public Data | 0 | 2 | 5 | 0.42482 |  |
| 19 | Model Evaluation & Validation | 0 | 2 | 6 | 0.53263 | **YES** |
| 20 | Unsupervised Learning & Clustering | 0 | 2 | 6 | 0.44701 | **YES** |
| 21 | Feature Engineering for ML | 0 | 2 | 6 | 0.41361 |  |
| 22 | Assessment: ML Fundamentals Quiz | 0 | 2 | 6 | 0.38147 |  |
| 23 | Ensemble Methods & Gradient Boosting | 0 | 2 | 7 | 0.53263 |  |
| 24 | Responsible AI & Model Explainability | 0 | 2 | 7 | 0.52542 |  |
| 25 | Project: Predictive Model End-to-End | 0 | 2 | 7 | 0.42538 |  |
| 26 | Dimensionality Reduction: PCA, t-SNE, UMAP | 0 | 3 | 7 | 0.44701 |  |

**Items in the path ONLY because they are prerequisites: 7** — `da-101`, `da-105`, `math-101`, `ml-102`, `ml-105`, `ml-107`, `py-103`

Ordering violations (a prerequisite scheduled after its dependent): **0** — NONE

## 8. READINESS CALCULATION

```python
# app/ml/gap.py
def readiness(profile, mastery, catalog):
    target = build_target(profile, catalog)
    total    = sum(target.values())
    achieved = sum(min(mastery.get(s, 0.0), required) for s, required in target.items())
    return achieved / total
```

Importance-weighted and clipped: mastery above a skill's target earns no extra credit.

- **Initial readiness: 0.0** (no evidence for any skill)
- **Final predicted readiness: 0.91**
- Total gain: **+0.9100**
- Path coverage of initial weighted gap mass: **0.8382**

Readiness after each item, in **final study order** (uses `_simulate_gain`, the
same noisy-OR rule as the profiler, with recency fixed at 1.0):

| # | Item | Hours | Readiness after | Delta | Delta per hour |
|---|---|---|---|---|---|
| 1 | Probability & Statistics for Data Science | 24 | 0.0609 | +0.0609 | 0.00254 |
| 2 | Python for Everybody: Getting Started | 18 | 0.0914 | +0.0305 | 0.00169 |
| 3 | SQL for Data Science | 16 | 0.1246 | +0.0332 | 0.00208 |
| 4 | Linear Algebra for Machine Learning | 20 | 0.1633 | +0.0387 | 0.00193 |
| 5 | Python Data Structures | 20 | 0.1767 | +0.0134 | 0.00067 |
| 6 | Data Analysis with Python | 20 | 0.2146 | +0.0379 | 0.00190 |
| 7 | Machine Learning Specialization | 40 | 0.3032 | +0.0886 | 0.00222 |
| 8 | Assessment: Python Proficiency Check | 2 | 0.3093 | +0.0061 | 0.00305 |
| 9 | Pandas in Depth | 10 | 0.3432 | +0.0339 | 0.00339 |
| 10 | Data Visualization with Matplotlib/Seaborn | 12 | 0.3819 | +0.0387 | 0.00323 |
| 11 | Intro to Machine Learning | 8 | 0.4060 | +0.0241 | 0.00301 |
| 12 | Intermediate SQL: Window Functions | 12 | 0.4308 | +0.0248 | 0.00207 |
| 13 | Statistical Inference | 22 | 0.4728 | +0.0420 | 0.00191 |
| 14 | Data Cleaning & Preprocessing | 12 | 0.5248 | +0.0520 | 0.00433 |
| 15 | Storytelling with Data | 10 | 0.5703 | +0.0455 | 0.00455 |
| 16 | Exploratory Data Analysis in Practice | 14 | 0.5922 | +0.0219 | 0.00156 |
| 17 | Supervised Learning with scikit-learn | 16 | 0.6557 | +0.0635 | 0.00397 |
| 18 | Project: End-to-End EDA on Public Data | 14 | 0.6679 | +0.0122 | 0.00087 |
| 19 | Model Evaluation & Validation | 12 | 0.7055 | +0.0376 | 0.00313 |
| 20 | Unsupervised Learning & Clustering | 14 | 0.7549 | +0.0494 | 0.00353 |
| 21 | Feature Engineering for ML | 10 | 0.7954 | +0.0405 | 0.00405 |
| 22 | Assessment: ML Fundamentals Quiz | 2 | 0.8061 | +0.0107 | 0.00535 |
| 23 | Ensemble Methods & Gradient Boosting | 12 | 0.8611 | +0.0550 | 0.00458 |
| 24 | Responsible AI & Model Explainability | 10 | 0.8962 | +0.0351 | 0.00351 |
| 25 | Project: Predictive Model End-to-End | 20 | 0.9100 | +0.0138 | 0.00069 |
| 26 | Dimensionality Reduction: PCA, t-SNE, UMAP | 10 | 0.9100 | +0.0000 | 0.00000 |

**Skills contributing most to the readiness increase:**

| Skill | Mastery reached | Target | Share of total readiness gain |
|---|---|---|---|
| Data Analysis | 0.8994 | 0.95 | 7.6% |
| Model Evaluation | 0.9126 | 0.85 | 7.2% |
| Statistics | 0.8396 | 0.9 | 7.1% |
| ML Foundations | 0.8360 | 0.95 | 7.0% |
| Data Wrangling | 0.8239 | 0.85 | 6.9% |
| Data Visualization | 0.8488 | 0.8 | 6.7% |
| Classification | 0.7791 | 0.8 | 6.6% |
| Feature Engineering | 0.7759 | 0.8 | 6.5% |
| Python Fundamentals | 0.7129 | 0.9 | 6.0% |
| SQL | 0.6983 | 0.85 | 5.9% |

Target skills still **below** the met threshold (0.9x target) after the whole path: **6**
- ML Foundations: reaches 0.836, needs 0.855
- Python Fundamentals: reaches 0.713, needs 0.810
- SQL: reaches 0.698, needs 0.765
- Regression Models: reaches 0.633, needs 0.720
- Probability: reaches 0.602, needs 0.675
- Communication & Storytelling: reaches 0.425, needs 0.585

## 9. MILESTONES AND DATES

```python
n_phases = max(3, min(5, round(total_hours / 45) or 3))
n_phases = min(n_phases, len(ordered))
target   = total_hours / n_phases        # split on cumulative HOURS, not item count
weeks    = round(hours / hours_per_week, 1)
ends     = cursor + timedelta(days=max(7, round(weeks * 7)))
```

- total_hours = **380** -> round(380/45) = **8** -> clamped to [3,5] = **5** milestones
- weekly pace used: **6.0 h/week** (from the conversation)
- total weeks: **63.3** = 380 / 6.0
- start: **2026-09-07** (`date.today()`) · end: **2027-11-24**

| # | Title | Items | Hours | Weeks | Starts | Ends | Focus skills |
|---|---|---|---|---|---|---|---|
| 1 | Foundations: Mathematics | 4 | 78 | 13.0 | 2026-09-07 | 2026-12-07 | Linear Algebra, Probability, SQL, Python Fundamentals |
| 2 | Building: Machine Learning | 3 | 80 | 13.3 | 2026-12-07 | 2027-03-10 | ML Foundations, Python Fundamentals, Data Analysis, Regression Models |
| 3 | Building: Data | 7 | 78 | 13.0 | 2027-03-10 | 2027-06-09 | Data Wrangling, Data Analysis, Data Visualization, Statistics |
| 4 | Building: Machine Learning | 6 | 80 | 13.3 | 2027-06-09 | 2027-09-10 | Data Visualization, Model Evaluation, Data Analysis, Clustering & Dim. Reduction |
| 5 | Mastery: Machine Learning | 6 | 64 | 10.7 | 2027-09-10 | 2027-11-24 | Model Evaluation, Feature Engineering, Ensemble Methods, Responsible AI |

Grouping rule: items are appended in final study order and the phase advances
once cumulative hours cross `target * (phase+1)`, provided enough items remain to
fill the remaining phases. **Milestones are contiguous slices of the ordered path,**
not thematic groupings — the title is derived *after* grouping, by dominant skill
category (`_phase_title`).

## 10. EXPLANATIONS

**Are explanations derived from the engine or generated separately?**

**Derived.** `explain_item(scored, ...)` takes the `ScoredItem` the ranker
produced and reads three fields off it: `contributions` (weight x component),
`covers` (per-skill weighted gap closed) and `missing_prereqs`. It computes no
scores of its own. Component sentences come from a fixed lookup keyed by
component name, and are emitted only for components with `share >= 0.10`:

```python
ordered = sorted(scored.contributions.items(), key=lambda kv: -kv[1])
for name, contribution in ordered[:3]:
    share = contribution / scored.score
    if share < 0.10: continue
    reasons.append(f'{COMPONENT_PHRASES[name].capitalize()} ({share:.0%} of the match score).')
```

LLM status this run: `{'enabled': False, 'model': None, 'reason': 'ANTHROPIC_API_KEY is not set', 'note': 'PathFinder runs fully offline; Claude only enriches wording.'}`. With no API key the text is the raw
attribution rendering. When a key is present `app.llm` rewrites the *same facts*
into warmer prose and is instructed not to add others — but that rewrite is not
verified programmatically. **Faithfulness under LLM rewriting: NOT VERIFIED.**

Per-item attribution behind each `Why this?`:

### Probability & Statistics for Data Science (`math-104`)

- headline: `Probability & Statistics for Data Science — because you still need Statistics and Probability.`
- reason: `It closes the skill gaps that matter most for your goal (46% of the match score).`
- reason: `It sits at the right difficulty for where you are now (23% of the match score).`
- reason: `It is in the learning format you prefer (16% of the match score).`
- reason: `Teaches Statistics at depth 50%; you are currently at 0%.`
- reason: `Teaches Probability at depth 60%; you are currently at 0%.`
- reason: `Opens up: Statistical Inference, Assessment: Math Readiness for ML, Reinforcement Learning Specialization.`
- attribution used: coverage=0.2336, level_fit=0.12, modality=0.08, quality=0.0778, semantic=0.0, collab=0.0
- covers: Statistics=0.405, Probability=0.3375

### Python for Everybody: Getting Started (`py-101`)

- headline: `Python for Everybody: Getting Started — because you still need Python Fundamentals.`
- reason: `It closes the skill gaps that matter most for your goal (33% of the match score).`
- reason: `It sits at the right difficulty for where you are now (28% of the match score).`
- reason: `It is exceptionally well rated by people who took it (21% of the match score).`
- reason: `Teaches Python Fundamentals at depth 55%; you are currently at 0%.`
- reason: `Opens up: Automate the Boring Stuff with Python, Python Data Structures.`
- attribution used: coverage=0.1402, level_fit=0.12, quality=0.0905, modality=0.08, semantic=0.0, collab=0.0
- covers: Python Fundamentals=0.4455

### SQL for Data Science (`sql-101`)

- headline: `SQL for Data Science — because you still need SQL.`
- reason: `It closes the skill gaps that matter most for your goal (33% of the match score).`
- reason: `It sits at the right difficulty for where you are now (29% of the match score).`
- reason: `It is in the learning format you prefer (19% of the match score).`
- reason: `Teaches SQL at depth 60%; you are currently at 0%.`
- reason: `Opens up: Intermediate SQL: Window Functions, Database Design & Normalisation, Django for Web Applications.`
- attribution used: coverage=0.1364, level_fit=0.12, modality=0.08, quality=0.0794, semantic=0.0, collab=0.0
- covers: SQL=0.4335

### Linear Algebra for Machine Learning (`math-101`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Python Data Structures (`py-103`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Data Analysis with Python (`da-101`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Machine Learning Specialization (`ml-101`)

- headline: `Machine Learning Specialization — because you still need ML Foundations, Regression Models and Classification.`
- reason: `It closes the skill gaps that matter most for your goal (74% of the match score).`
- reason: `It sits at the right difficulty for where you are now (23% of the match score).`
- reason: `It is exceptionally well rated by people who took it (18% of the match score).`
- reason: `Teaches ML Foundations at depth 70%; you are currently at 0%.`
- reason: `Teaches Regression Models at depth 50%; you are currently at 0%.`
- reason: `Scheduled after Python Data Structures and Linear Algebra for Machine Learning, which it builds on.`
- reason: `Opens up: Deep Learning Specialization, Reinforcement Learning Specialization.`
- attribution used: coverage=0.38, level_fit=0.12, quality=0.0939, modality=0.08, semantic=0.0, collab=0.0
- covers: ML Foundations=0.6317, Regression Models=0.32, Classification=0.256

### Assessment: Python Proficiency Check (`py-a01`)

- headline: `Assessment: Python Proficiency Check — because you still need Python Fundamentals.`
- reason: `It sits at the right difficulty for where you are now (39% of the match score).`
- reason: `It is in the learning format you prefer (26% of the match score).`
- reason: `It closes the skill gaps that matter most for your goal (25% of the match score).`
- reason: `Teaches Python Fundamentals at depth 30%; you are currently at 0%.`
- reason: `Scheduled after Python Data Structures, which it builds on.`
- attribution used: level_fit=0.12, modality=0.08, coverage=0.0765, quality=0.0717, semantic=0.0, collab=0.0
- covers: Python Fundamentals=0.243

### Pandas in Depth (`da-102`)

- headline: `Pandas in Depth — because you still need Data Analysis and Data Wrangling.`
- reason: `It closes the skill gaps that matter most for your goal (50% of the match score).`
- reason: `It sits at the right difficulty for where you are now (27% of the match score).`
- reason: `It is exceptionally well rated by people who took it (19% of the match score).`
- reason: `Teaches Data Analysis at depth 55%; you are currently at 0%.`
- reason: `Teaches Data Wrangling at depth 30%; you are currently at 0%.`
- reason: `Scheduled after Data Analysis with Python, which it builds on.`
- reason: `Opens up: Data Cleaning & Preprocessing, Exploratory Data Analysis in Practice, Intro to Machine Learning.`
- attribution used: coverage=0.2244, level_fit=0.12, quality=0.0875, modality=0.08, semantic=0.0, collab=0.0
- covers: Data Analysis=0.4964, Data Wrangling=0.2167

### Data Visualization with Matplotlib/Seaborn (`da-105`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Intro to Machine Learning (`ml-102`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Intermediate SQL: Window Functions (`sql-102`)

- headline: `Intermediate SQL: Window Functions — because you still need SQL and Data Analysis.`
- reason: `It closes the skill gaps that matter most for your goal (51% of the match score).`
- reason: `It is exceptionally well rated by people who took it (23% of the match score).`
- reason: `It is in the learning format you prefer (23% of the match score).`
- reason: `Teaches SQL at depth 55%; you are currently at 0%.`
- reason: `Teaches Data Analysis at depth 20%; you are currently at 0%.`
- reason: `Scheduled after SQL for Data Science, which it builds on.`
- reason: `Opens up: Assessment: SQL Query Challenge, Assessment: Data Analyst Skills Audit, Data Engineering Foundations.`
- attribution used: coverage=0.1818, quality=0.0812, modality=0.08, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: SQL=0.3974, Data Analysis=0.1805

### Statistical Inference (`math-105`)

- headline: `Statistical Inference — because you still need Statistics and Probability.`
- reason: `It closes the skill gaps that matter most for your goal (60% of the match score).`
- reason: `It is in the learning format you prefer (20% of the match score).`
- reason: `It is exceptionally well rated by people who took it (18% of the match score).`
- reason: `Teaches Statistics at depth 70%; you are currently at 0%.`
- reason: `Teaches Probability at depth 35%; you are currently at 0%.`
- reason: `Scheduled after Probability & Statistics for Data Science, which it builds on.`
- reason: `Opens up: Time Series Forecasting.`
- attribution used: coverage=0.2404, modality=0.08, quality=0.0729, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Statistics=0.567, Probability=0.1969

### Data Cleaning & Preprocessing (`da-103`)

- headline: `Data Cleaning & Preprocessing — because you still need Data Wrangling and Feature Engineering.`
- reason: `It closes the skill gaps that matter most for your goal (55% of the match score).`
- reason: `It is exceptionally well rated by people who took it (22% of the match score).`
- reason: `It is in the learning format you prefer (21% of the match score).`
- reason: `Teaches Data Wrangling at depth 70%; you are currently at 0%.`
- reason: `Teaches Feature Engineering at depth 25%; you are currently at 0%.`
- reason: `Scheduled after Pandas in Depth, which it builds on.`
- attribution used: coverage=0.2095, quality=0.0819, modality=0.08, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Data Wrangling=0.5058, Feature Engineering=0.16

### Storytelling with Data (`da-106`)

- headline: `Storytelling with Data — because you still need Data Visualization and Communication & Storytelling.`
- reason: `It closes the skill gaps that matter most for your goal (45% of the match score).`
- reason: `It is exceptionally well rated by people who took it (25% of the match score).`
- reason: `It is in the learning format you prefer (25% of the match score).`
- reason: `Teaches Data Visualization at depth 40%; you are currently at 0%.`
- reason: `Teaches Communication & Storytelling at depth 50%; you are currently at 0%.`
- reason: `Scheduled after Data Visualization with Matplotlib/Seaborn, which it builds on.`
- attribution used: coverage=0.147, quality=0.0809, modality=0.08, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Data Visualization=0.256, Communication & Storytelling=0.2112

### Exploratory Data Analysis in Practice (`da-104`)

- headline: `Exploratory Data Analysis in Practice — because you still need Data Analysis, Data Visualization and Statistics.`
- reason: `It closes the skill gaps that matter most for your goal (65% of the match score).`
- reason: `It is in the learning format you prefer (18% of the match score).`
- reason: `It is exceptionally well rated by people who took it (17% of the match score).`
- reason: `Teaches Data Analysis at depth 50%; you are currently at 0%.`
- reason: `Teaches Data Visualization at depth 40%; you are currently at 0%.`
- reason: `Scheduled after Pandas in Depth, which it builds on.`
- reason: `Opens up: Project: End-to-End EDA on Public Data, Assessment: Data Analyst Skills Audit, Data-Informed Product Decisions.`
- attribution used: coverage=0.2862, modality=0.08, quality=0.0774, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Data Analysis=0.4512, Data Visualization=0.256, Statistics=0.2025

### Supervised Learning with scikit-learn (`ml-103`)

- headline: `Supervised Learning with scikit-learn — because you still need Classification, Regression Models and Model Evaluation.`
- reason: `It closes the skill gaps that matter most for your goal (65% of the match score).`
- reason: `It is in the learning format you prefer (18% of the match score).`
- reason: `It is exceptionally well rated by people who took it (17% of the match score).`
- reason: `Teaches Classification at depth 55%; you are currently at 0%.`
- reason: `Teaches Regression Models at depth 50%; you are currently at 0%.`
- reason: `Scheduled after Intro to Machine Learning, which it builds on.`
- reason: `Opens up: Feature Engineering for ML, Model Evaluation & Validation, Unsupervised Learning & Clustering.`
- attribution used: coverage=0.291, modality=0.08, quality=0.0778, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Classification=0.352, Regression Models=0.32, Model Evaluation=0.2529

### Project: End-to-End EDA on Public Data (`da-p01`)

- headline: `Project: End-to-End EDA on Public Data — because you still need Data Analysis, Data Visualization and Data Wrangling.`
- reason: `It closes the skill gaps that matter most for your goal (63% of the match score).`
- reason: `It is in the learning format you prefer (19% of the match score).`
- reason: `It is exceptionally well rated by people who took it (18% of the match score).`
- reason: `Teaches Data Analysis at depth 45%; you are currently at 0%.`
- reason: `Teaches Data Visualization at depth 35%; you are currently at 0%.`
- reason: `Scheduled after Exploratory Data Analysis in Practice, which it builds on.`
- attribution used: coverage=0.2664, modality=0.08, quality=0.0762, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Data Analysis=0.4061, Data Visualization=0.224, Data Wrangling=0.2167

### Model Evaluation & Validation (`ml-105`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Unsupervised Learning & Clustering (`ml-107`)  *(prerequisite fill)*

Not ranked into the path — pulled in by prerequisite closure. `PathItem.reason_components`:
`{}` · `covers`: `{}`

> **Explanation source for fillers: attribution is empty.** The UI falls back
> to the 'consolidates what you have already started' headline. See §11.6.

### Feature Engineering for ML (`ml-104`)

- headline: `Feature Engineering for ML — because you still need Feature Engineering and Data Wrangling.`
- reason: `It closes the skill gaps that matter most for your goal (55% of the match score).`
- reason: `It is exceptionally well rated by people who took it (21% of the match score).`
- reason: `It is in the learning format you prefer (21% of the match score).`
- reason: `Teaches Feature Engineering at depth 70%; you are currently at 0%.`
- reason: `Teaches Data Wrangling at depth 30%; you are currently at 0%.`
- reason: `Scheduled after Supervised Learning with scikit-learn, which it builds on.`
- attribution used: coverage=0.2091, quality=0.0813, modality=0.08, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Feature Engineering=0.448, Data Wrangling=0.2167

### Assessment: ML Fundamentals Quiz (`ml-a01`)

- headline: `Assessment: ML Fundamentals Quiz — because you still need ML Foundations and Model Evaluation.`
- reason: `It closes the skill gaps that matter most for your goal (45% of the match score).`
- reason: `It is in the learning format you prefer (25% of the match score).`
- reason: `It is exceptionally well rated by people who took it (24% of the match score).`
- reason: `Teaches ML Foundations at depth 30%; you are currently at 0%.`
- reason: `Teaches Model Evaluation at depth 25%; you are currently at 0%.`
- reason: `Scheduled after Supervised Learning with scikit-learn, which it builds on.`
- attribution used: coverage=0.142, modality=0.08, quality=0.0758, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: ML Foundations=0.2707, Model Evaluation=0.1806

### Ensemble Methods & Gradient Boosting (`ml-106`)

- headline: `Ensemble Methods & Gradient Boosting — because you still need Ensemble Methods, Classification and Model Evaluation.`
- reason: `It closes the skill gaps that matter most for your goal (54% of the match score).`
- reason: `It is exceptionally well rated by people who took it (23% of the match score).`
- reason: `It is in the learning format you prefer (21% of the match score).`
- reason: `Teaches Ensemble Methods at depth 75%; you are currently at 0%.`
- reason: `Teaches Classification at depth 30%; you are currently at 0%.`
- reason: `Scheduled after Model Evaluation & Validation, which it builds on.`
- reason: `Opens up: Project: Kaggle Competition Sprint.`
- attribution used: coverage=0.2022, quality=0.0852, modality=0.08, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Ensemble Methods=0.27, Classification=0.192, Model Evaluation=0.1806

### Responsible AI & Model Explainability (`ml-110`)

- headline: `Responsible AI & Model Explainability — because you still need Model Evaluation and Responsible AI.`
- reason: `It closes the skill gaps that matter most for your goal (37% of the match score).`
- reason: `It is in the learning format you prefer (28% of the match score).`
- reason: `It is exceptionally well rated by people who took it (28% of the match score).`
- reason: `Teaches Model Evaluation at depth 25%; you are currently at 0%.`
- reason: `Teaches Responsible AI at depth 75%; you are currently at 0%.`
- reason: `Scheduled after Model Evaluation & Validation, which it builds on.`
- reason: `Opens up: Assessment: Model Fairness Audit.`
- attribution used: coverage=0.1046, modality=0.08, quality=0.0794, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: Model Evaluation=0.1806, Responsible AI=0.1519

### Project: Predictive Model End-to-End (`ml-p01`)

- headline: `Project: Predictive Model End-to-End — because you still need ML Foundations, Model Evaluation and Feature Engineering.`
- reason: `It closes the skill gaps that matter most for your goal (62% of the match score).`
- reason: `It is in the learning format you prefer (19% of the match score).`
- reason: `It is exceptionally well rated by people who took it (19% of the match score).`
- reason: `Teaches ML Foundations at depth 40%; you are currently at 0%.`
- reason: `Teaches Model Evaluation at depth 35%; you are currently at 0%.`
- reason: `Scheduled after Model Evaluation & Validation, which it builds on.`
- attribution used: coverage=0.2636, modality=0.08, quality=0.0797, level_fit=0.0601, semantic=0.0, collab=0.0
- covers: ML Foundations=0.361, Model Evaluation=0.2529, Feature Engineering=0.224

### Dimensionality Reduction: PCA, t-SNE, UMAP (`clu-101`)

- headline: `Dimensionality Reduction: PCA, t-SNE, UMAP — because you still need Clustering & Dim. Reduction and Linear Algebra.`
- reason: `It closes the skill gaps that matter most for your goal (43% of the match score).`
- reason: `It is in the learning format you prefer (35% of the match score).`
- reason: `It is exceptionally well rated by people who took it (32% of the match score).`
- reason: `Teaches Clustering & Dim. Reduction at depth 60%; you are currently at 0%.`
- reason: `Teaches Linear Algebra at depth 35%; you are currently at 0%.`
- reason: `Scheduled after Unsupervised Learning & Clustering, which it builds on.`
- attribution used: coverage=0.0968, modality=0.08, quality=0.0737, level_fit=0.0075, semantic=0.0, collab=0.0
- covers: Clustering & Dim. Reduction=0.1815, Linear Algebra=0.126

## 11. POTENTIAL PROBLEMS

### 11.1 Three of six ranking signals are inert for this learner — CONFIRMED

- `semantic` for every path item: **{0.0}**. `profile.goal_text` is `''`
  because the learner chose the role from a *button*, and the button handler sets
  `role_id` without ever writing the label into `goal_text`. `recommend()` then
  does `goal_vector = encode(goal_text) if goal_text else None` -> zeros.
- `collab` for every path item: **{0.0}**. Cold start, no completions.
- `modality` for every path item: **{1.0}** — a constant, since
  `1.0 if not preferred else ...`. It shifts every score by the same +0.08 and
  discriminates nothing.

**Effective discriminating weight = coverage 0.38 + level_fit 0.12 + quality 0.1 = 0.60 of 1.00.** 0.32 is dead and 0.08 is a constant offset.

This is the single most important finding in this dump. The six-signal hybrid is
advertised as the core of the ranker; for a button-driven cold-start learner —
which is the *default* path through the product — it is effectively a three-signal
ranker. The `semantic` loss is a **bug** (the label exists and is simply not
stored). The `collab` loss is inherent to cold start. The `modality` constant is
harmless but means the weight is misleading.

**Direct evidence for §11.1** (two conversations, same resulting role):

```
BUTTON  ("don't know" -> click Data Scientist)
        role=data-scientist  goal_text=''
        semantic component of top-5 candidates: [0.0, 0.0, 0.0, 0.0, 0.0]

TYPED   ("i want to be a data scientist")
        role=data-scientist  goal_text='i want to be a data scientist'
        semantic component of top-5 candidates: [0.2778, 0.1621, 0.4108, 0.4116, 0.5152]
```

Both arrive at the same role. The button path silently discards 0.18 of the
ranking weight. The audited run took the button path.


### 11.2 Six required skills are never brought to target — CONFIRMED

| Skill | Target | Reached after full path | Shortfall |
|---|---|---|---|
| ML Foundations | 0.95 | 0.836 | 0.019 |
| Python Fundamentals | 0.9 | 0.713 | 0.097 |
| SQL | 0.85 | 0.698 | 0.067 |
| Regression Models | 0.8 | 0.633 | 0.087 |
| Probability | 0.75 | 0.602 | 0.073 |
| Communication & Storytelling | 0.65 | 0.425 | 0.160 |

The planner stops at `COVERAGE_TARGET=0.82`, so ~18% of weighted
gap mass is left uncovered **by design**. Readiness still reports 0.91, which is
honest arithmetic but reads as 'nearly job-ready' while 6 of 17 required skills
sit below threshold. Worth checking whether that framing is acceptable.

### 11.3 Roadmap length — FLAG

**380 hours / 63.3 weeks / 26 items.** At the
learner's stated 6.0 h/week this is **1.2 years**,
ending 2027-11-24. Nothing is wrong with the arithmetic; the
issue is that pace is used only to *schedule*, never to *scope*. A 6 h/week learner
and a 20 h/week learner receive the identical 380-hour path.

### 11.4 Readiness per hour varies ~20x across selected items — FLAG

| Item | Hours | Readiness delta | Delta per hour |
|---|---|---|---|
| Dimensionality Reduction: PCA, t-SNE, UMAP | 10 | +0.0000 | **0.00000** |
| Python Data Structures | 20 | +0.0134 | **0.00067** |
| Project: Predictive Model End-to-End | 20 | +0.0138 | **0.00069** |
| Project: End-to-End EDA on Public Data | 14 | +0.0122 | **0.00087** |
| ... | | | |
| Storytelling with Data | 10 | +0.0455 | 0.00455 |
| Ensemble Methods & Gradient Boosting | 12 | +0.0550 | 0.00458 |
| Assessment: ML Fundamentals Quiz | 2 | +0.0107 | 0.00535 |

The low-value tail is mostly late items hitting already-saturated skills (noisy-OR
diminishing returns) plus prerequisite fills, which are not selected for gain at all.
Expected behaviour, but it is where a shorter path would cut.

### 11.5 Redundancy — CLEAN

Chosen items covering zero outstanding gap: **0**. Prerequisite
fills that teach nothing new toward the goal: counted separately as scaffolding
(7 items). No duplicate-topic stacking detected: noisy-OR simulation
collapses the marginal value of a second course on a covered skill.

### 11.6 Prerequisite fills carry no explanation attribution — CONFIRMED

All **7** filler items have empty `reason_components` and empty
`covers`, because they were never scored by the ranker. Their `Why this?` therefore
cannot cite the arithmetic — it falls back to a generic headline. A learner asking
'why am I doing Linear Algebra?' gets no mention of the item it unlocks, even
though the graph knows exactly what that is.

### 11.7 Ordering, prerequisites, relevance — CLEAN

- prerequisite violations in final order: **0**
- items unrelated to the goal: **0** (every chosen item covers >0 weighted gap)
- prerequisite chains: max depth observed in path = **7**, catalog max is 9
- generic vs personalised: the path *is* role-driven, but with `semantic` dead
  (11.1) two learners who pick the same role button get identical paths regardless
  of how they described themselves. **Personalisation here comes from history and
  role only — not from free text.**

### 11.8 Scoring anomalies — NONE DETECTED

Coverage is peak-normalised per step so scores are comparable within a step but
**not across steps**. Final scores range 0.2270–0.5122. No NaN, no negatives.

## 12. RAW CONFIGURATION

```python
# app/ml/recommender.py
WEIGHTS = {"coverage": 0.38, "semantic": 0.18, "collab": 0.14, "level_fit": 0.12, "quality": 0.1, "modality": 0.08}   # sum = 1.0
PRIOR_RATING    = 4.6
PRIOR_COUNT     = 50000.0
CF_SHRINKAGE    = 12.0      # similarity damping: co / (co + 12)
LEVEL_TOLERANCE = 0.85
PREREQ_PENALTY  = 0.12

level_fit = exp(-(item.level - learner_level)**2 / (2 * LEVEL_TOLERANCE**2))
if missing_prereqs: score *= max(0.4, 1 - PREREQ_PENALTY * len(missing_prereqs))

# app/ml/planner.py
COVERAGE_TARGET = 0.82
MAX_SELECTED    = 22
COST_EXPONENT   = 0.5
MIN_PHASES, MAX_PHASES = 3, 5
KIND_BONUS      = {"course": 1.0, "project": 1.3, "assessment": 1.15}
MIN_PROJECTS    = 2
_LATE_CATEGORIES = {'Career'}

efficiency = (gain * score * KIND_BONUS[kind]) / hours ** COST_EXPONENT
_simulate_gain: contribution = min(0.92, weight * depth * 0.85); noisy-OR combine
                depth = {1: 0.85, 2: 1.0, 3: 1.15}[item.level]

# app/ml/profiler.py  (mastery + forgetting)
RECENCY_HALFLIFE_MONTHS  = 24.0
RECENCY_FLOOR            = 0.35
DEFAULT_COMPLETION_SCORE = 0.85
MAX_SINGLE_CONTRIBUTION  = 0.92
LEVEL_DEPTH_FACTOR       = {"1": 0.85, "2": 1.0, "3": 1.15}
DECLARED_WEIGHT          = 0.7

recency_factor(m) = RECENCY_FLOOR + (1 - RECENCY_FLOOR) * 0.5 ** (m / 24.0)
contribution      = min(0.92, weight * depth * recency * score * kind_factor)
                    kind_factor = 1.1 for project|assessment else 1.0
mastery[s]        = 1 - prod(1 - contribution_i)          # noisy-OR
confidence[s]     = 1 - exp(-sum(weight * recency))
implied_level     = min(3, 0.6*declared + 1.6*min(1, strong/18) + 0.4)

# app/ml/gap.py
MET_RATIO        = 0.9
GOAL_SKILL_FLOOR = 0.55
weighted_gap = max(0, target - mastery) * target
readiness    = sum(min(mastery[s], target[s])) / sum(target[s])

# app/ml/graph.py
prerequisite_closure: BFS over Item.prereqs, skipping anything in `known`
topological_order   : Kahn, sort_key = (career_stage, level, depth, -priority, id)
                      raises ValueError on a cycle

# scheduling
n_phases = max(3, min(5, round(total_hours / 45) or 3))
weeks    = round(hours / hours_per_week, 1)
ends     = cursor + timedelta(days=max(7, round(weeks * 7)))
```

**NOT AVAILABLE:** soft/optional prerequisite type; per-skill prerequisite edges
(edges are item-level only); learned ranking weights (all six are hand-set);
time-on-task signals; any A/B or real-learner outcome data.
