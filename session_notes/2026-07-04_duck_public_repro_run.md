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
Expected artifacts:
- /kaggle/working/diagnostics.html
- /kaggle/working/benchmark.json
- /kaggle/working/summary.txt or equivalent summary output
- /kaggle/working/submission.parquet
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

should not be interpreted as 23.85 Kaggle GPU-hours consumed. Dividing by roughly 25 concurrent game jobs gives a more realistic per-game average runtime:

```text
85878 / 25 ≈ 3435 seconds ≈ 57 minutes average per game-run
```

This was compatible with the user's observed live runtime of about 1.5 hours.

## In-progress run observations

The user shared repeated diagnostics snapshots while the run was still in progress.

Score progression during the run:

| Snapshot | Mean score | Total actions | Total tokens | Generated tokens/sec | Printed total wallclock |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.11 | 242 | 131,666 | 218.27 | 11,707.3s |
| 2 | 0.11 | 475 | 220,895 | 183.18 | 25,738.4s |
| 3 | 0.11 | 677 | 319,978 | 176.91 | 39,738.0s |
| 4 | 0.38 | 883 | 421,500 | 174.81 | 52,844.4s |
| 5 | 0.56 | 1,083 | 537,665 | 178.41 | 67,524.8s |
| 6 | 0.58 | 1,276 | 688,578 | 190.41 | 85,878.0s |

The key positive sign was that the run was not stuck:

```text
0.11 -> 0.38 -> 0.56 -> 0.58
```

## Final Duck-Repro-A public benchmark result

The final uploaded diagnostics and summary show that the run completed successfully.

```text
benchmark: duck-harness-kaggle-duck-public-repro-20260704
solver:    duck-harness
games:     25
passes:    1
runs:      25 (won: 0)
started:   2026-07-04 16:48:59
ended:     2026-07-04 19:01:35
duration:  2h 12m 36s
mean score:    1.68
median score:  0.20
total actions: 3545
total tokens:  1576578
generated tokens/sec: 198.15 (job wallclock)
total wallclock: 198107.2s
```

Additional score views from the diagnostics PDFs:

| Scorer view | Mean |
|---|---:|
| Official ARC | 1.68 |
| Weighted `(1, 2, 2, ...)` | 3.61 |
| Raw levels beaten | 0.72 levels per game |

Interpretation:

```text
This is a successful reproduction of the public Duck harness on the 25 public games.
The result is in line with the Tufa reported public-train mean of about 1.6002 +/- 0.4475.
```

Important distinction:

```text
This is a public benchmark reproduction result, not yet the official Kaggle leaderboard result for our submitted notebook.
Kaggle submission scoring is awaited.
```

## Per-game final results

| Game | State | Score | Levels | Actions | Tokens |
|---|---|---:|---:|---:|---:|
| ar25-0c556536 | gave_up | 0.43 | 1 / 8 | 156 | 66,225 |
| bp35-0a0ad940 | gave_up | 0.03 | 1 / 9 | 197 | 65,505 |
| cd82-fb555c5d | gave_up | 0.00 | 0 / 6 | 243 | 64,967 |
| cn04-2fe56bfb | gave_up | 0.00 | 0 / 6 | 515 | 64,179 |
| dc22-fdcac232 | gave_up | 0.00 | 0 / 6 | 247 | 65,466 |
| ft09-0d8bbf25 | gave_up | 14.21 | 2 / 6 | 63 | 50,154 / note 63,676 |
| g50t-5849a774 | gave_up | 0.00 | 0 / 7 | 72 | 65,736 / note 67,954 |
| ka59-38d34dbb | gave_up | 1.94 | 1 / 7 | 166 | 60,092 / note 66,945 |
| lf52-271a04aa | gave_up | 1.82 | 1 / 10 | 83 | 66,622 |
| lp85-305b61c3 | gave_up | 2.78 | 1 / 8 | 89 | 67,084 |
| ls20-9607627b | gave_up | 0.00 | 0 / 7 | 70 | 65,910 / note 66,744 |
| m0r0-492f87ba | gave_up | 0.00 | 0 / 6 | 238 | 61,789 / note 65,002 |
| r11l-495a7899 | gave_up | 0.00 | 0 / 6 | 154 | 65,106 |
| re86-8af5384d | gave_up | 0.21 | 1 / 8 | 99 | 64,036 / note 67,070 |
| s5i5-18d95033 | gave_up | 0.00 | 0 / 8 | 65 | 65,531 / note 66,034 |
| sb26-7fbdac44 | gave_up | 2.78 | 1 / 8 | 195 | 64,391 / note 65,807 |
| sc25-635fd71a | gave_up | 3.48 | 2 / 6 | 131 | 66,266 |
| sk48-d8078629 | gave_up | 0.00 | 0 / 8 | 37 | 62,075 / note 67,205 |
| sp80-589a99af | gave_up | 0.20 | 1 / 6 | 208 | 65,583 / note 65,744 |
| su15-1944f8ab | gave_up | 0.37 | 1 / 9 | 67 | 44,506 / note 67,095 |
| tn36-ef4dde99 | gave_up | 10.71 | 2 / 7 | 45 | 66,681 |
| tr87-cd924810 | gave_up | 0.00 | 0 / 6 | 104 | 59,236 |
| tu93-0768757b | gave_up | 1.94 | 2 / 9 | 121 | 58,943 |
| vc33-5430563c | gave_up | 1.22 | 1 / 7 | 64 | 63,688 / note 64,552 |
| wa30-ee6fef47 | gave_up | 0.00 | 0 / 9 | 116 | 66,807 |

Summary counts from the final table:

```text
Games with level progress: 14 / 25
Total completed levels: 18
Games with 2 levels completed: ft09, sc25, tn36, tu93
Best score: ft09 = 14.21
Second-best score: tn36 = 10.71
Median official ARC score: 0.20
```

## Runtime / quota interpretation after completion

Real job duration:

```text
2h 12m 36s ≈ 2.21 GPU-hours if Kaggle bills by notebook runtime
```

If the weekly GPU budget is about 30 hours:

```text
2.21 / 30 ≈ 7.4% of weekly GPU quota
```

Decision:

```text
Full 25-game Duck runs are affordable but expensive.
Use full runs only for baseline/release candidates.
Use targeted 3-8 game diagnostics for development.
```

The diagnostics explicitly warn that games run in parallel and wallclock per game is not simply total wallclock divided by number of games. Therefore, `total wallclock: 198107.2s` should not be treated as consumed Kaggle GPU time.

## Analysis / interpretation

### What worked

- The public Duck notebook reproduced successfully in our Kaggle setup.
- The final public benchmark score was `1.68`, aligned with the Tufa public-train reference mean.
- The harness completed one pass over all 25 public games.
- The run generated useful diagnostics, including score-vs-token curves, score-vs-wallclock curves, per-game plots, and per-pass per-game result table.
- Duck solved early levels on 14 of 25 games and completed 18 total levels.
- The strongest games were `ft09`, `tn36`, `sc25`, and `tu93`.

### What failed / limitations

- No full game was won: `runs won = 0 / 25`.
- All runs ended in `gave_up` state.
- The public benchmark is much stronger than our current heuristic baseline, but it is still low in absolute terms.
- Token use is heavy: `1,576,578` total generated tokens for one 25-game pass.
- Many games consumed around 60k-67k tokens with zero levels completed.
- Weak / zero-score games remain important failure-analysis targets: `cd82`, `cn04`, `dc22`, `g50t`, `ls20`, `m0r0`, `r11l`, `s5i5`, `sk48`, `tr87`, `wa30`.
- Official Kaggle submission score is still awaited and must be recorded separately when available.

### Strategic conclusion

This session confirms that the Duck direction is materially above our current gated-BFS line on public-game reproduction:

```text
Latest weak offline gated-BFS context: ~0.1916
Best known selected project public baseline: ~0.38
Duck-Repro-A public benchmark: 1.68
```

Approximate ratio:

```text
1.68 / 0.38 ≈ 4.4x best observed selected baseline
1.68 / 0.1916 ≈ 8.8x latest weak offline context
```

Research interpretation:

```text
Duck is token-expensive but adapts better than action-search heuristics.
The main gap is not just action efficiency. It is early-level rule discovery through LLM + Python REPL + multimodal/segmentation context.
```

## Browser tab guidance recorded

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

## Current best score/result

Project baseline context:

```text
P0 random baseline: 0.07 public
Best known selected project submission before Duck: ~0.38 public, Persistent Memory short/gated-BFS v1 — Version 1
Latest weak offline seed/sweep context: ~0.1916
```

Duck reproduction context:

```text
Duck-Repro-A public benchmark mean score: 1.68
Weighted scorer mean: 3.61
Raw levels beaten mean: 0.72
Median official ARC score: 0.20
Runs: 25
Won: 0
Games with progress: 14 / 25
Total completed levels: 18
Total actions: 3,545
Total tokens: 1,576,578
Duration: 2h 12m 36s
```

Submission status:

```text
Official Kaggle submission score: awaited
```

Reference Tufa result from earlier review:

```text
Tufa Duck official Milestone 1 Kaggle score: 1.21%
Tufa public train mean: 1.6002 +/- 0.4475
```

## Files / artifacts referenced

Created and shared to user during this session:

```text
/mnt/data/arc3_20260704_duck_public_repro_workbench.ipynb
```

Uploaded by user after run completion:

```text
/mnt/data/summary (6).txt
/mnt/data/diagnostics.html
/mnt/data/benchmark.json
/mnt/data/taaf_setup_env.json
/mnt/data/ar25-0c556536_p0.log
/mnt/data/wa30-ee6fef47_p0_events.jsonl
/mnt/data/duck-harness-kaggle-duck-public-repro-20260704.pdf
/mnt/data/duck-harness-kaggle-duck-public-repro-20260704 2.pdf
/mnt/data/duck-harness-kaggle-duck-public-repro-20260704 3.pdf
```

Repo session note updated:

```text
session_notes/2026-07-04_duck_public_repro_run.md
```

No project source code or scoring notebook was modified in the repo during this update.

## Next session plan

### Step 1 — Record official Kaggle score when available

When Kaggle submission scoring completes, append:

```text
submission name / version
public score
private score if visible / applicable
rank if visible
whether selected
submission runtime if shown
```

### Step 2 — Build per-game comparison

Create a table:

```text
game_id | our_baseline_score | duck_score | duck_level_progress | duck_action_count | reusable_idea
```

Start with Duck's strongest progress games:

```text
ft09, tn36, sc25, tu93, lp85, sb26, ka59, lf52, vc33
```

### Step 3 — Avoid full reruns initially

Use targeted diagnostics in the customization hook before running another full 25-game job.

Targeted run candidate:

```python
LIMIT_TO_GAME_IDS = ["ft09", "tn36", "sc25", "tu93", "lp85", "sb26", "ka59", "lf52", "vc33"]
MAX_GAMES_FOR_DEBUG = None
```

### Step 4 — First build-on-top experiment

Recommended first actual improvement branch:

```text
EXP-DUCK-LITE-001: segmentation + trace diagnostics port
```

Goal:

```text
Do not modify the LLM solver first.
First port the reusable perception/diagnostic ideas into our own offline workbench and compare against persistent-memory/gated-BFS.
```

### Step 5 — Failure analysis targets

Inspect zero-score games separately:

```text
cd82, cn04, dc22, g50t, ls20, m0r0, r11l, s5i5, sk48, tr87, wa30
```

Purpose:

```text
Determine whether failures are caused by perception, wrong objective hypothesis, mouse/action misuse, excessive token burn, or insufficient memory/context compaction.
```
