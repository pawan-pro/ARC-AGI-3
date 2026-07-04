# 2026-07-04 Session Notes — Duck Public Notebook Reproduction Run

## Session context

We started the 2026-07-04 ARC Prize 2026 / ARC-AGI-3 session with the goal of reproducing the public Tufa Labs Duck harness notebook before building on top of it.

This follows the 2026-07-02 review of the Tufa Labs Milestone 1 winning approach, where the main conclusion was:

```text
Do not blindly tune BFS further. First reproduce and inspect the Duck harness in isolation, then port only the most evidence-backed ideas into our clean baseline.
```

## What was done

### 1. Created a public Duck reproduction notebook

Generated a clean reproduction notebook from the uploaded Tufa Labs public notebook:

```text
Input notebook:
/mnt/data/tufa-labs-duck-harness-june-30-milestone-winner.ipynb

Output notebook shared to user:
/mnt/data/arc3_20260704_duck_public_repro_workbench.ipynb
```

Notebook role:

```text
Duck-Repro-A: exact public notebook reproduction base
```

Operating rule added to the notebook:

```text
Run unchanged first.
Record diagnostics/runtime/output.
Only then modify the customization hook.
```

The generated notebook adds:

- a 2026-07-04 session intro,
- Kaggle input preflight checks,
- a reproducibility manifest cell,
- a safe customization hook,
- instructions for post-run diagnostics and next variants.

### 2. Required Kaggle inputs documented

The notebook was prepared for a Kaggle environment with:

```text
Competition input:
arc-prize-2026-arc-agi-3

Public datasets:
jeroencottaar/taaf-kaggle-source-share
driessmit1/arc3-vllm-h100-wheelhouse-v3
driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
```

Recommended run settings:

```text
GPU: RTX Pro 6000
Internet: off
Mode: Save & Run / Commit
Expected artifact: /kaggle/working/diagnostics.html
```

### 3. User started the Kaggle run

The user reported the run was still going after about 1.5 hours and shared benchmark output.

Key harness configuration from the log:

```text
benchmark.label : duck-harness-kaggle
benchmark.solver: HarnessSolver(
    label='duck-harness',
    model='local',
    analyzer_timeout=900.0,
    max_actions_per_game=None,
    max_runtime_s_per_game=7920.0,
    concurrency=28,
    start_local_server=False
)
benchmark.passes: 1
benchmark.games : 25
```

Important runtime interpretation:

```text
concurrency=28 and games=25 means the benchmark runs the 25 games concurrently.
The printed total wallclock in diagnostics is likely aggregate game-job wallclock, not direct Kaggle GPU quota consumed.
```

Therefore, the large printed values such as:

```text
total wallclock: 85878.0s
```

should not be interpreted as 23.85 Kaggle GPU-hours consumed. Dividing by roughly 25 concurrent game jobs gives a much more realistic per-game average runtime:

```text
85878 / 25 ≈ 3435 seconds ≈ 57 minutes average per game-run
```

This is compatible with the user's observed live runtime of about 1.5 hours.

## Run progress observed

The user shared repeated diagnostics snapshots while the run was still in progress.

Score progression:

| Snapshot | Mean score | Total actions | Total tokens | Generated tokens/sec | Printed total wallclock |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.11 | 242 | 131,666 | 218.27 | 11,707.3s |
| 2 | 0.11 | 475 | 220,895 | 183.18 | 25,738.4s |
| 3 | 0.11 | 677 | 319,978 | 176.91 | 39,738.0s |
| 4 | 0.38 | 883 | 421,500 | 174.81 | 52,844.4s |
| 5 | 0.56 | 1,083 | 537,665 | 178.41 | 67,524.8s |
| 6 | 0.58 | 1,276 | 688,578 | 190.41 | 85,878.0s |

The key positive sign is that the run was not stuck: the mean score improved over time:

```text
0.11 -> 0.38 -> 0.56 -> 0.58
```

The run was still marked:

```text
ended: in progress
```

## Per-game progress at latest snapshot

Latest snapshot:

```text
benchmark: duck-harness-kaggle-duck-public-repro-20260704
solver:    duck-harness
games:     25
passes:    1
runs:      25 (won: 0)
started:   2026-07-04 16:48:59
ended:     in progress
mean score:    0.58
median score:  0.00
total actions: 1276
total tokens:  688578
generated tokens/sec: 190.41
total wallclock: 85878.0s
```

Games with level progress in the latest snapshot:

| Game | Score | Levels | Actions | Tokens |
|---|---:|---:|---:|---:|
| ka59-38d34dbb | 1.94 | 1.0 / 7 | 53 | 28,354 |
| lf52-271a04aa | 1.82 | 1.0 / 10 | 41 | 28,363 |
| lp85-305b61c3 | 2.78 | 1.0 / 8 | 9 | 25,359 |
| sb26-7fbdac44 | 2.78 | 1.0 / 8 | 59 | 28,493 |
| su15-1944f8ab | 0.37 | 1.0 / 9 | 55 | 29,067 |
| tn36-ef4dde99 | 3.57 | 1.0 / 7 | 19 | 26,706 |
| tu93-0768757b | 0.12 | 1.0 / 9 | 86 | 28,610 |
| vc33-5430563c | 1.22 | 1.0 / 7 | 21 | 25,094 |

All other games remained at zero levels in the latest snapshot.

## Runtime / quota interpretation

The user asked whether the runtime implied a problem, given the estimated Kaggle quota of about 30 GPU-hours/week.

Assessment:

```text
The runtime does not look abnormal for Duck.
This is a local multimodal/coding LLM harness, not a lightweight heuristic notebook.
A full 25-game public reproduction can reasonably take around 1.5 to 2.5 real GPU-hours.
```

Important distinction:

```text
Actual Kaggle GPU quota should be tied to real notebook job runtime, not the aggregate benchmark wallclock printed across concurrent game jobs.
```

Practical budget rule:

```text
Full 25-game Duck runs should be used sparingly.
After the first baseline reproduction, use targeted 3-8 game diagnostics rather than full runs for every change.
```

Suggested targeted games from observed progress:

```python
LIMIT_TO_GAME_IDS = [
    "ka59",
    "lf52",
    "lp85",
    "sb26",
    "su15",
    "tn36",
    "tu93",
    "vc33",
]
```

## Browser tab guidance

The user asked whether they could close the browser tab running the Kaggle notebook.

Guidance given:

```text
Safe to close the tab if the run was started via Save & Run / Commit and appears as an active Kaggle job.
Do not close if it is only an unsaved interactive cell execution unless interruption risk is acceptable.
```

Safer checklist:

```text
1. Confirm Save & Run / Commit was used.
2. Confirm the run appears under Kaggle active/running events or notebook versions.
3. Then closing the browser tab should be fine.
```

## What worked

- A clean Duck public reproduction workbench was created and shared.
- The Kaggle run started and produced diagnostics.
- The run showed increasing mean score over time, indicating the harness was alive and making progress.
- The run reached level 1 on multiple public games.
- Runtime behavior was explained as plausible given concurrency and local LLM inference.
- GPU budget risk was identified early.

## What failed / unresolved

- The run was still in progress at the time of this note.
- Final score, final diagnostics, and final artifact list are not yet known.
- No code improvements were attempted yet.
- No per-game comparison against our persistent-memory/gated-BFS baseline was completed yet.
- We still need to save final `diagnostics.html`, logs, and any generated files from Kaggle.

## Current best score/result

Project baseline context:

```text
P0 random baseline: 0.07 public
Best known selected project submission: ~0.38 public, Persistent Memory short/gated-BFS v1 — Version 1
Latest weak offline seed/sweep context: ~0.1916
```

Duck reproduction run context at latest shared snapshot:

```text
Duck-Repro-A latest in-progress mean score: 0.58
Median score: 0.00
Runs: 25
Won: 0
Total actions: 1276
Total tokens: 688,578
Status: in progress
```

Reference Tufa result from earlier review:

```text
Tufa Duck official Milestone 1 Kaggle score: 1.21%
Tufa public train mean: 1.6002 +/- 0.4475
```

## Files changed

Created and shared to user during this session:

```text
/mnt/data/arc3_20260704_duck_public_repro_workbench.ipynb
```

Created in repo by this commit:

```text
session_notes/2026-07-04_duck_public_repro_run.md
```

No project source code or scoring notebook was modified in the repo during this session.

## Next session plan

### Step 1 — Finish baseline artifact capture

When the Kaggle run completes, collect:

```text
/kaggle/working/diagnostics.html
/kaggle/working/git_status.txt
/kaggle/working/submission.parquet
full notebook output/log
any score/summary files emitted by the harness
```

Record:

```text
final mean score
final per-game scores
runtime
GPU type
whether Save & Run / Commit was used
whether run was competition rerun or public/offline benchmark mode
```

### Step 2 — Build per-game comparison

Create a table:

```text
game_id | our_baseline_score | duck_score | duck_level_progress | duck_action_count | reusable_idea
```

Start with games where Duck made progress:

```text
ka59, lf52, lp85, sb26, su15, tn36, tu93, vc33
```

### Step 3 — Avoid full reruns initially

Use targeted diagnostics in the customization hook before running another full 25-game job.

Targeted run candidate:

```python
LIMIT_TO_GAME_IDS = ["ka59", "lf52", "lp85", "sb26", "su15", "tn36", "tu93", "vc33"]
MAX_GAMES_FOR_DEBUG = None
```

### Step 4 — First build-on-top experiment

Recommended first actual improvement branch:

```text
EXP-DUCK-LITE-001: segmentation + trace diagnostics port
```

Goal:

```text
Do not modify the LLM solver first. First port the reusable perception/diagnostic ideas into our own offline workbench and compare against persistent-memory/gated-BFS.
```
