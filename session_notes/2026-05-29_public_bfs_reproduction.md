# ARC-AGI-3 Session Notes — 2026-05-29

## Objective

Analyze public ARC-AGI-3 leaderboard notebooks and identify a reproducible baseline before attempting architectural modifications or fine-tuning.

Primary goal:
- Reproduce public ~0.42–0.46 leaderboard agent behavior reliably.
- Establish a stable experimentation baseline.

---

# Public Leaderboard Context

| Team | Public Score |
|---|---|
| Tufa Labs | 1.18 |
| Redfield Rentals | 0.68 |
| Barada Sahu | 0.66 |
| Kevin E R MILLE | 0.66 |
| SVG | 0.65 |
| Matthew Philip Poetker | 0.64 |

Reviewed public notebooks:
- Ash's ARC-AGI-3 Agent — Public 0.42
- Revised BFS/CNN hybrid derivative — ~0.46

---

# Key Technical Findings

## Core Insight

The public agent is primarily:

- a CPU-bound BFS/search planner
- with a lightweight CNN fallback

The score is NOT primarily coming from large-scale neural learning.

---

# Architecture Breakdown

## 1. BFS Planner

Main solving mechanism:
- deep-copy game states
- replay actions
- breadth-first exploration
- deduplicate via state hashing

Key file/class:
- `BFSSolver`

Important components:
- `_state_hash`
- `_scan_actions`
- `_probe_hidden_fields`
- `_try_transfer`

---

## 2. Hidden-State Recovery

Important discovery:
- some ARC-AGI-3 games contain hidden scalar state
- pixel hashing alone is insufficient

Notebook dynamically probes:
- `game.__dict__`

Then retries BFS with:
- frame hash + hidden scalar variables

---

## 3. Action Pruning

Large performance optimization:
- only retain actions that visibly change state

Especially important for:
- ACTION6 click-space pruning

This significantly reduces branching factor.

---

## 4. Transfer Between Levels

The notebook:
- replays previous-level solutions
- computes centroid offsets
- shifts click coordinates

This exploits level similarity.

---

## 5. CNN Fallback

CNN is secondary.

Used when:
- BFS fails
- search becomes too expensive

Features:
- one-hot color channels
- edge maps
- rarity maps
- temporal diffs
- lightweight episodic memory

---

# Important Observations

## Why the notebook works

Main reasons:
1. Simulator introspection
2. Action pruning
3. Efficient state hashing
4. Solution transfer
5. Replay-based memory optimization

---

## Why it stalls near 0.42–0.46

Current limitations:
- BFS depth cap (~30)
- primitive action search only
- weak hidden-state modeling
- limited generalization
- no macro-actions
- no learned world model

---

# Strategic Direction

## P0 — Reproduction

Goal:
- reproduce public notebook score exactly

Tasks:
- verify runtime consistency
- log BFS solve rates
- instrument search depth
- measure branching factor

---

## P1 — Robust Baseline

Planned additions:
- local evaluation harness
- structured logging
- replay inspection
- deterministic seeds
- submission-safe fallback mode

---

## P2 — Leaderboard Improvement

Primary experiments:
- macro-actions
- novelty search
- prioritized BFS
- object-level hashing
- best-first search

---

## P3 — Research Bet

Longer-term ideas:
- learned world model
- MCTS hybrid
- latent planning
- object-centric state abstraction

---

# Current Status

Submission:
- public BFS/CNN hybrid submitted for scoring

Awaiting:
- Kaggle public score
- runtime diagnostics

---

# Files Reviewed

- `my_agent.py`
- BFS solver implementation
- CNN fallback implementation
- Kaggle submission wrapper

---

# Next Session Plan

1. Confirm reproducible score
2. Build instrumentation layer
3. Add trajectory logging
4. Measure:
   - solved levels
   - BFS depth
   - action branching
5. Begin macro-action experiment branch
