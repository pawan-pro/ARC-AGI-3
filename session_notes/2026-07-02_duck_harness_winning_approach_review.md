# 2026-07-02 Session Notes — Tufa Duck Harness Winning Approach Review

## Session context

We started this ARC Prize 2026 / ARC-AGI-3 session by reviewing the latest project state and the new Tufa Labs Milestone 1 write-up shared in the Kaggle discussion:

```text
Tufa Labs’ Winning Solution for ARC-AGI-3 Milestone 1
Kaggle discussion: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133
Uploaded notebook: tufa-labs-duck-harness-june-30-milestone-winner.ipynb
Uploaded pasted discussion text: Pasted text.txt
```

The main strategic update is that the Milestone 1 winning direction is not just a stronger hand-written search policy. It is an LLM coding-agent harness that turns ARC-AGI-3 gameplay into an iterative inspect-reason-code-act loop.

K-12 summary:

```text
Our current agent is like a robot that tries buttons, remembers some good/bad moves, and searches ahead.
The winning Duck agent is more like giving a clever programmer a game screen, a debugger, object maps, and a Python notebook.
It can inspect what changed, write code, form a theory, test the theory, then act.
```

## Current project state entering the review

Known project score ladder from prior sessions:

| Experiment / submission | Score / status | Decision |
|---|---:|---|
| P0 random baseline | 0.07 public | Validated submission plumbing; not competitive |
| FORGE V1 instrumented | 0.26 public | Historical validated baseline |
| FORGE V1 no-BFS ablation | 0.28 public | Useful historical ablation |
| Persistent Memory BFS exact replication | 0.30 public | Older baseline |
| Persistent Memory short/gated-BFS v1 — Version 1 | 0.38 public | Best observed; keep selected |
| Persistent Memory short/gated-BFS v1 — Version 2 | 0.20 public | Weak rerun / high variance |
| Persistent Memory short/gated-BFS v2 — Version 1 | 0.19 public | Rejected |
| Persistent Memory gated-BFS v2 / wider budget | 0.18 public | Rejected |
| Persistent Memory v1 + loop/no-change pruning | 0.24 public | Rejected |
| Latest offline seed/sweep context | about 0.1916 offline | Weak; not a promotion candidate |

Latest pasted local/offline result from the project context:

```text
Finished: 25/25
Overall score: 0.19161491783449486
Run dir: /kaggle/working/runs-20260701-142957-pm-gated-v1-seed-sweep-e
```

Working conclusion before reading the Tufa approach:

```text
Our current deterministic/search-heavy line is useful as a clean baseline, but it is probably capped unless we add stronger perception, hypothesis testing, and adaptive reasoning.
```

## What was reviewed today

### 1. Tufa Labs / Duck write-up

The shared Kaggle discussion describes Tufa Labs' winning Milestone 1 solution, called the Duck, successor to Stochastic Goose.

Key reported result from the write-up:

```text
Official Kaggle Milestone 1 score: 1.21%
Initially observed / later retracted score: 1.30%
Public train-set mean: 1.6002 +/- 0.4475
Same submission observed as low as 0.77% on Kaggle
Evaluation: 25 public games x 20 tries
```

Important interpretation:

```text
This is not human-level performance. It is still very low in absolute terms.
But it is materially above our current baseline trajectory and, more importantly, points to a higher-ceiling architecture.
```

### 2. Uploaded Duck notebook

The session also considered the uploaded notebook:

```text
tufa-labs-duck-harness-june-30-milestone-winner.ipynb
```

This notebook should be treated as an external reference artifact for the next reproduction experiment. It should not be mixed into our clean baseline agent until it has been reproduced and inspected in a separate branch/folder.

### 3. Visual examples from the write-up

The images showed the core agent loop:

```text
LLM -> Python sandbox -> action list -> ARC-AGI-3 environment -> updated state -> Python sandbox / LLM again
```

The examples also showed:

- a pinned system prompt,
- context management / eviction,
- segmentation into connected components,
- Python inspection of ASCII board regions,
- heatmaps of per-game progress,
- cumulative score distribution showing sparse high-scoring attempts.

## Winning approach summary

The Duck harness exposes the game to the LLM through a Python REPL. The LLM can inspect current game state, previous game state, history, transitions, segmentation, and valid actions. It can then call a function such as `action([...])` to execute one or more environment actions.

Main components:

| Component | What it does | Why it matters |
|---|---|---|
| Qwen 3.6 27B FP8 | Open-source multimodal/coding model | Fits competition GPU constraints better than frontier API models |
| Python REPL | Lets model inspect state and execute code | Turns gameplay into a coding/debugging problem |
| `current_frame.ascii` | Text representation of board | Enables precise grid/corridor inspection |
| `current_frame.segmentation` | Connected-component decomposition | Gives object-level structure instead of raw pixels only |
| `history` / `transitions` | Prior action-state records | Supports learning mechanics from evidence |
| `action(actions)` | Executes one or more moves | Allows batched, programmatic control |
| World model note | Compact natural-language memory | Helps preserve learned mechanics across turns/levels |
| Context eviction | Removes older non-system context | Lets the agent keep playing longer without context overflow |
| Multimodal frame input | Lets model see current board image | Helps visual grounding, though still imperfect |
| Diagnostics/viewer | Records traces and score behavior | Makes failure analysis practical |

## How Duck differs from our approach

| Dimension | Our current approach | Tufa Duck approach |
|---|---|---|
| Agent type | Hand-written heuristic/search agent | LLM coding-agent harness |
| Main intelligence | Action priors, BFS, memory, loop avoidance | LLM reasoning + Python inspection + hypothesis testing |
| Perception | Limited state/action parsing and handcrafted features | Image + ASCII + segmentation graph |
| Memory | Persistent action/statistical memory | Natural-language world model + transitions/history |
| Planning | Search over possible moves | Model writes code, tests mechanics, then acts |
| Adaptation | Mostly parameterized heuristics | In-context rule discovery and world-model updates |
| Diagnostics | Notebook logs, summary CSV, recordings | Full transcripts, trace exports, viewer/diagnostics infrastructure |
| Main failure mode | Stuck loops, wasted action budget, weak exploration | Hallucinated goals, over-printing grids, context pollution, visual misreads |
| Ceiling | Likely capped without reasoning layer | Higher ceiling as models and harness improve |

Key strategic distinction:

```text
We were mostly trying to manually design a better player.
Tufa turned the game into a live programming/debugging problem and let the model act as the player.
```

## What worked / useful insights

- Our clean baseline discipline remains valuable.
- The current best selected project result around `0.38` should remain protected as the known best submission.
- The persistent-memory/gated-BFS line remains useful as a cheap deterministic/fallback policy.
- The Tufa release gives a concrete architecture to reproduce and inspect rather than speculate from scratch.
- Segmentation/object graphs look immediately reusable even before adding a full LLM harness.
- World-model memory is a clearer abstraction than only storing action statistics.
- Diagnostics are now clearly a first-class research artifact, not a side effect.

## What failed / limitations in our current line

- Latest offline seed/sweep result around `0.1916` remains weak.
- The best observed `0.38` public result is not yet stable/reproducible.
- Pure BFS/seed/pruning changes may be near diminishing returns.
- Our agent does not yet form explicit hypotheses such as: "UP moves the orange/blue block, not the player."
- Our logs are less useful for interpreting object mechanics compared with a REPL + segmentation + transcript design.

## Updated research interpretation

The competition is moving toward adaptive tool-using agents, not only handcrafted action policies.

Paper-track framing that emerged today:

```text
Start with deterministic exploration and memory.
Measure its ceiling and instability.
Then move toward tool-using agents with structured perception, compact world-model memory, and in-context hypothesis testing.
Study how much performance comes from search, perception, memory, model reasoning, and diagnostics.
```

This is a stronger research narrative than only tuning BFS hyperparameters.

## Updated plan by priority

### P0 baseline

Keep the current best persistent-memory/gated-BFS submission unchanged as the safety baseline.

Do not overwrite the selected `0.38` submission unless a new candidate is validated by logs/local evaluation and Kaggle score.

### P1 robust submission

Port non-LLM improvements first:

```text
- connected-component segmentation
- compact per-game memory / world-model field
- action-effect trace logs
- no full-board dumping by default
- loop/no-change pruning with evidence
- HTML/CSV diagnostics for per-game failure modes
```

Goal:

```text
Recover or improve the 0.38 behavior with better reproducibility and better diagnostics.
```

### P2 leaderboard improvement

Create a clean reproduction experiment for Duck:

```text
EXP-DUCK-001: reproduce and inspect Tufa Duck harness
```

Tasks:

```text
1. Create a separate branch/folder.
2. Save the uploaded Tufa notebook as a reference artifact.
3. Run the notebook unchanged if possible.
4. Export diagnostics and per-game score tables.
5. Compare Duck vs our gated-BFS on all 25 public games.
6. Identify games where Duck succeeds and our agent fails.
7. Identify components that can be ported safely.
```

Target comparison table:

```text
game_id | our_score | duck_score | duck_success_pattern | reusable_idea
```

### P3 medal-level research bet

Build a Duck-lite harness after reproduction:

```text
- Kaggle-compatible open model
- Python REPL/action interface
- segmentation-first state representation
- compact world-model memory
- action batching
- output limits
- fallback to our deterministic BFS/exploration agent when LLM is uncertain or times out
```

### P4 paper-track narrative

Position the project as a study of:

```text
adaptive reasoning + tool use + structured perception + memory under hidden interactive games
```

## Recommended next experiment

```text
EXP-DUCK-001: Tufa Duck Harness Reproduction and Delta Analysis
```

Proposed branch:

```text
exp/duck-harness-repro-2026-07-02
```

Proposed folder:

```text
experiments/duck_harness_repro/
```

Proposed artifacts:

```text
experiments/duck_harness_repro/README.md
experiments/duck_harness_repro/source_notes.md
experiments/duck_harness_repro/per_game_comparison.csv
experiments/duck_harness_repro/diagnostics_summary.md
```

Validation requirement:

```text
Do not claim improvement from Duck or Duck-lite until we have either:
1. local/offline public-game evaluation logs, or
2. Kaggle submission score, or
3. reproducible diagnostics showing better game-level progress.
```

## Files changed in this session

```text
session_notes/2026-07-02_duck_harness_winning_approach_review.md
```

No agent code or scoring notebooks were changed in this session.

## Current best score/result

```text
P0 random baseline: 0.07 public
Best known selected project submission: ~0.38 public, Persistent Memory short/gated-BFS v1 — Version 1
Latest weak offline seed/sweep context: ~0.1916
Tufa Duck reference: 1.21% official Milestone 1 Kaggle score; 1.6002 +/- 0.4475 public train mean
```

## Next-session starting point

Start the next session from this principle:

```text
Do not blindly tune BFS further. First reproduce and inspect the Duck harness in isolation, then port only the most evidence-backed ideas into our clean baseline.
```

Concrete next prompt:

```text
Create EXP-DUCK-001 in a new branch. Add a clean reproduction folder for the Tufa Duck harness, preserve our current best baseline, run or prepare the uploaded notebook as an external benchmark artifact, and produce a per-game Duck-vs-our-baseline comparison plan.
```
