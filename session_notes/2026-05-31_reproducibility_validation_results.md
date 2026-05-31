# ARC-AGI-3 Session Notes — 2026-05-31

## Session Objective

Validate whether previously reported public leaderboard scores can be reproduced without architectural changes, then prepare a safe instrumentation-only branch for deeper diagnostics before attempting algorithmic modifications.

Primary focus:

* Reproduce prior FORGE/Baseline behavior faithfully
* Avoid premature architecture rewrites
* Add observability before optimization
* Preserve a clean submission-safe baseline

---

# 1. Kaggle Results Reviewed Today

## Submitted Notebooks + Scores

| Notebook                            | Public Score | Status    |
| ----------------------------------- | -----------: | --------- |
| `[0.35]FORGE v16 Trigger-aware BFS` |         0.23 | Succeeded |
| `FORGE ARC-AGI-3 Agent`             |         0.26 | Succeeded |
| `baseline_v19_public`               |         0.20 | Succeeded |
| `forge_public_v1`                   | Kaggle Error | Failed    |

---

# 2. Key Observations

## A. Strong Reproducibility Drift

The reproduced public scores are materially below the originally reported notebook scores.

### Original vs Current

| Notebook                       | Historical Reported | Current Reproduction |
| ------------------------------ | ------------------: | -------------------: |
| FORGE v16 Trigger-aware BFS    |                0.35 |                 0.23 |
| FORGE ARC-AGI-3 Agent          |                0.39 |                 0.26 |
| baseline_v19_public / v15-like |                0.46 |                 0.20 |

### Interpretation

This strongly suggests at least one of:

* hidden environment/version drift
* nondeterministic exploration sensitivity
* dependency/runtime drift
* changed game distribution
* action-budget sensitivity
* timing/runtime variance
* hidden seed effects
* pretrained weight mismatch
* evaluation pool shift

Current evidence does **not** support assuming the architecture itself is broken.

---

## B. v10 Lineage Still Appears Strongest

The evidence still points toward the v10/v16 lineage being the most reliable base:

### Important retained components

* action dedup
* counter A*
* transfer heuristics
* BFS-first solving
* hidden-state retry
* dynamic action scanning

These historically correlated with the best observed scores.

---

## C. Large Regressions Came From Removing Proven Components

The earlier analysis remains consistent:

### Likely regressors

* removing dedup
* removing counter A*
* aggressive pruning
* over-compressed exploration
* weaker BFS diversity
* unstable replay behavior

This aligns with the earlier v15 regression observations.

---

# 3. Strategic Decision Made

## Decision

Do NOT immediately redesign the agent.

Instead:

### Phase 1

Reproduce faithfully.

### Phase 2

Instrument deeply.

### Phase 3

Only then optimize.

This is now the working methodology.

---

# 4. New Experimental Branch Created

## FORGE v18

Created as:

### “v10 + proven fixes only”

No speculative architecture rewrite.

---

# 5. v18 Functional Additions

## Added

### 1. CLTI Replay Injection

Cross-Level Transfer Injection:

* BFS solutions from earlier levels injected into CNN replay memory
* Intended to help L1 adaptation

### 2. Warm-Up Unlock Logic

Addresses locked initial-state games:

* tries directional warm-up moves
* rescans action space after unlock

Designed for sc25-style environments.

### 3. Hidden-State Retry Retained

Dynamic scalar-field probing maintained.

### 4. Solution Transfer Retained

Previous-level replay + object-relative click transfer retained.

### 5. Dedup Retained

Important proven feature from earlier successful versions.

---

# 6. Instrumentation Upgrade Added

A second pass added instrumentation-only modifications.

## Added Diagnostics

### Runtime Metrics

* BFS timing
* explored states
* unique states
* retry timing
* queue pressure

### Solver Diagnostics

* unlock detection logs
* transfer success/failure logs
* hidden-field retry logs
* action-scan counts

### CNN Diagnostics

* replay buffer growth
* training invocation frequency
* epsilon decay visibility
* AEM memory stats

### Stability Metrics

* unproductive-action counters
* undo trigger visibility
* checkpoint tracking

---

# 7. Important Engineering Principle Established

## New Rule

Separate:

### Functional changes

from

### Observability changes

This is critical for ARC experimentation.

Without instrumentation:

* leaderboard movements become uninterpretable
* regressions cannot be localized
* hidden bottlenecks remain invisible

---

# 8. Current Experimental Structure

## P0 — Clean Reproduction

* original notebooks
* no modifications
* establish reproducibility baseline

## P1 — Instrumented Baseline

* v18 instrumentation branch
* same core logic
* deeper visibility

## P2 — Targeted Improvements

After diagnostics:

* BFS queue shaping
* adaptive state hashing
* trigger discovery refinement
* better transfer heuristics

## P3 — Research-Level Bets

Later only:

* planning/search hybrids
* latent state inference
* learned exploration priors
* meta-controller policies

---

# 9. Current Hypotheses

## Most Plausible Current Bottlenecks

### Hypothesis A

BFS solving fewer levels than historical runs.

### Hypothesis B

State hashing collapsing valid states.

### Hypothesis C

Exploration variance causing unstable public scores.

### Hypothesis D

Some notebooks historically benefited from accidental runtime characteristics.

### Hypothesis E

Transfer logic succeeds on some hidden distributions but fails on current evaluation slices.

---

# 10. Files/Artifacts Worked On

## Main Artifact

`my_agent.py`

### Major Sections Updated

* BFSSolver
* hidden-state probing
* warm-up unlock
* transfer logic
* CNN replay injection
* instrumentation logging

---

# 11. Current Best Known Results

| Agent                       | Best Known Historical Public |
| --------------------------- | ---------------------------: |
| baseline_v19 lineage        |                         0.46 |
| FORGE ARC-AGI-3 Agent       |                         0.39 |
| FORGE v16 Trigger-aware BFS |                         0.35 |

## Current Reproduced Range

~0.20–0.26

---

# 12. Most Important Outcome of Today

The project is now transitioning from:

* “trying random modifications”

to:

* controlled experimental science

This is a major methodological improvement.

---

# 13. Next Session Plan

## Immediate Priority

### A. Analyze v18 Instrumentation Output

Inspect:

* BFS solve counts
* timeout distributions
* retry frequency
* unlock frequency
* transfer success rate
* replay statistics

### B. Build Evaluation Ledger

Track per-run:

* notebook hash
* seed behavior
* runtime
* solve counts
* public score
* Kaggle logs

### C. Add Per-Level Outcome Tracking

Need:

* solved levels
* solve source (BFS/CNN/transfer)
* action counts
* timeout reasons

### D. Preserve Clean Baselines

Keep:

* untouched reproduction notebooks
* instrumented branch separate

---

# 14. Recommended Next Engineering Step

Highest-value next addition:

## Structured JSON Logging

Per level:

* game id
* solver used
* states explored
* retries
* action count
* solve success
* elapsed time

This will enable:

* offline analytics
* clustering failures
* identifying systematic bottlenecks
* reproducible comparisons across runs

---

# Session Summary (Compact)

## What Was Done

* Reviewed reproduced Kaggle scores
* Identified major score drift
* Built v18 based on proven v10 lineage
* Added instrumentation-only diagnostics
* Preserved clean experimental methodology

## What Worked

* Stable submissions
* BFS + transfer architecture intact
* Instrumentation integrated successfully

## What Failed

* Public score reproduction significantly below historical values
* One notebook failed with Kaggle error

## Current Best Historical Score

0.46

## Current Reproduced Range

0.20–0.26

## Files Changed

* `my_agent.py`

## Next Step

Analyze v18 instrumentation logs before making further algorithmic changes.
