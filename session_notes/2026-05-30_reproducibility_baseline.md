# ARC-AGI-3 Session Notes — 2026-05-30

## Session Objective

Establish a reproducible ARC-AGI-3 baseline before introducing architectural modifications or instrumentation.

Primary goals:

* determine whether public Kaggle notebook scores can be replicated reliably,
* analyze yesterday’s lower-than-expected replication behavior,
* decide whether optimization or reproducibility should be prioritized.

---

# Prior Context Incorporated (Yesterday’s Run Analysis)

## Yesterday’s Observed Issue

A previously replicated/public notebook produced a significantly lower score than expected during your rerun.

Observed situation:

| Notebook Type             | Expected Public Score | Your Earlier Replication |
| ------------------------- | --------------------- | ------------------------ |
| Public ARC-AGI-3 notebook | ~0.39–0.46 range      | materially lower         |

This became the key investigation topic for today.

---

# Analysis Performed on Yesterday’s Score Gap

We analyzed several possible explanations for the replication discrepancy.

## Hypotheses considered

### 1. Kaggle runtime variance

Possible differences:

* H100 vs P100 vs T4
* runtime throttling
* queue truncation
* hidden timeout effects

Assessment:

* plausible contributor.

---

### 2. Hidden nondeterminism

Potential causes:

* stochastic exploration
* random action ordering
* unstable BFS branching
* environment timing sensitivity

Assessment:

* highly plausible.

---

### 3. Notebook version drift

Potential causes:

* copied notebook not identical to scored version
* hidden edits between versions
* dependency/environment drift

Assessment:

* plausible.

---

### 4. Silent failures

Potential causes:

* hidden exceptions
* partial model loading
* incomplete execution paths
* skipped branches due to runtime

Assessment:

* possible.

---

### 5. BFS instability

Potential causes:

* action explosion
* timeout-sensitive search
* branching-factor instability
* inconsistent trigger discovery

Assessment:

* likely important.

---

# Key Strategic Conclusion Reached

We concluded:

```text id="b9g8y2"
Optimization before reproducibility is premature.
```

The correct workflow became:

1. replicate scores first
2. freeze stable baseline
3. instrument
4. analyze bottlenecks
5. optimize later

This became the core decision of today’s session.

---

# Work Completed Today

## 1. Evaluated strategy direction

Discussed whether to:

* immediately modify public notebooks,
* add instrumentation,
* or first validate reproducibility.

Decision:

* prioritize replication before optimization.

---

# 2. Reviewed public ARC-AGI-3 notebook lineage

Analyzed the following notebook chain:

| Notebook                    | Public Score |
| --------------------------- | ------------ |
| FORGE ARC-AGI-3 Agent       | 0.39         |
| FORGE v16 Trigger-aware BFS | 0.35         |
| Ash's ARC-AGI-3 Agent       | 0.42         |
| [ARC26-3] Agent v15         | 0.46         |

Observed progression:

* increasing use of:

  * BFS search,
  * trigger-aware exploration,
  * transfer heuristics,
  * source-code inspection,
  * hybrid fallback logic.

---

# 3. Analyzed “CPU-bound BFS + GPU fallback” architecture

Reviewed notebook description claiming:

* BFS planner as primary solver
* CNN fallback policy
* transfer learning between levels
* hidden-state retries
* action filtering

Technical interpretation:

* BFS/search dominates solution quality.
* GPU affects fallback smoothness only.
* H100 likely improves throughput marginally.

Conclusion:

* search instrumentation is more important than CNN redesign.

---

# 4. Evaluated proposed instrumentation patch

Reviewed large instrumentation-enhanced `my_agent.py`.

Decision:

* DO NOT replace full file directly.

Reason:

* pasted version omitted critical original logic:

  * init pipeline,
  * helper methods,
  * inference code,
  * replay/memory,
  * environment setup.

Recommended approach:

* incremental instrumentation merge only.

---

# 5. Designed safe instrumentation plan

Prepared minimal-risk instrumentation strategy.

## Planned instrumentation

* run registry
* state hashing
* BFS/CNN usage tracking
* per-level metrics
* reward accumulation
* stochastic divergence tracking
* run summaries

Constraint:

* no behavioral modifications.

Goal:

* diagnose:

  * nondeterminism,
  * timeout-heavy games,
  * BFS dead zones,
  * transfer failures,
  * state collapse.

---

# 6. Established experiment structure

Recommended maintaining separate notebook tracks:

| Track                   | Purpose                 |
| ----------------------- | ----------------------- |
| `baseline_exact`        | untouched replication   |
| `baseline_instrumented` | diagnostics only        |
| `experimental_search`   | algorithm modifications |

---

# 7. Kaggle submissions launched

Submitted exact-copy replications of:

| Notebook                            | Public Score |
| ----------------------------------- | ------------ |
| `[ARC26-3] Agent v15`               | 0.46         |
| `Ash's ARC-AGI-3 Agent`             | 0.42         |
| `FORGE ARC-AGI-3 Agent`             | 0.39         |
| `[0.35]FORGE v16 Trigger-aware BFS` | 0.35         |

Important:

* submissions intentionally kept near-original.
* goal is reproducibility isolation.

---

# Current Hypotheses

## Hypothesis A — Scores replicate

If scores reproduce closely:

* environment is reasonably stable,
* notebook behavior is mostly reproducible,
* optimization work becomes meaningful.

Then next step:

* instrumentation-only branch.

---

## Hypothesis B — Scores fail again

Likely causes become:

* runtime nondeterminism,
* hidden stochasticity,
* dependency drift,
* timeout sensitivity,
* hardware variance,
* unstable BFS expansion.

Then next phase becomes:

* forensic reproducibility debugging.

---

# Current Best Baseline Status

| Notebook  | Status    |
| --------- | --------- |
| Agent v15 | submitted |
| Ash Agent | submitted |
| FORGE     | submitted |
| FORGE v16 | submitted |

Scores pending.

---

# What Worked

* avoided premature optimization
* avoided destabilizing baseline
* identified reproducibility as primary blocker
* established clean experiment hierarchy
* isolated likely true performance drivers
* prevented unsafe full-file overwrite

---

# What Failed / Risks Identified

* replication variance remains unresolved

* public notebooks may rely on:

  * fragile timing,
  * hidden runtime behavior,
  * undocumented assumptions,
  * stochastic exploration effects.

* instrumentation patch as pasted was unsafe as a full replacement.

---

# Files / Artifacts Affected

## Kaggle notebooks submitted

* `[ARC26-3] Agent v15`
* `Ash's ARC-AGI-3 Agent`
* `FORGE ARC-AGI-3 Agent`
* `[0.35]FORGE v16 Trigger-aware BFS`

## Planned future artifacts

* `baseline_instrumented`
* `run_metrics.json`
* `search_diagnostics.md`
* `reproducibility_matrix.csv`

---

# Current Strategic Position

Current phase:

```text id="5w5b7u"
P0 = reproducibility validation
```

NOT yet:

* architecture redesign,
* search expansion,
* learned planning,
* leaderboard chasing.

---

# Next Session Plan

## Immediate

Wait for Kaggle scores.

---

## If scores replicate

Next actions:

1. freeze clean baselines
2. clone instrumented branch
3. add logging-only instrumentation
4. analyze:

   * BFS solve rates
   * branching factors
   * retry counts
   * timeout patterns
   * transfer success

---

## If scores do NOT replicate

Next actions:

1. compare runtime logs
2. compare hardware/runtime
3. inspect hidden notebook differences
4. verify package parity
5. inspect timeout behavior
6. test deterministic seeding
7. analyze stochastic BFS divergence

---

# Research Notes

Most likely future leverage points:

## P1 Robust Submission

* runtime stabilization
* deterministic execution
* search pruning
* replay reuse

## P2 Leaderboard Improvement

* smarter action filtering
* trigger-aware branching
* object-relative transfer
* adaptive BFS depth

## P3 Medal-Level Research Bet

* learned search priors
* latent state abstraction
* hybrid symbolic/neural planning
* adaptive exploration policies

## P4 Paper-Track Narrative

* adaptive planning in hidden interactive environments
* dynamic state abstraction
* transfer-aware search
* exploration-efficiency analysis
