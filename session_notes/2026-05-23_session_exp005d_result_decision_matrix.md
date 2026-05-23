# 2026-05-23 Session Notes — EXP-005D Result and Decision Matrix

## Context

This note records the EXP-005D public result in the full ARC-AGI-3 experiment sequence and translates it into the next decision.

Current best before EXP-005D:

```text
EXP-005A — BFS Diagnostics + Hidden-State Hash
Version: 9
Public score: 0.17
Status: current best public baseline
```

Recent regressions:

```text
EXP-005B — Stronger Effective-Action Scan
Version: 10
Public score: 0.09

EXP-005C — Level-to-Level Transfer from EXP-005A
Version: 12
Public score: 0.10
```

EXP-005D was created as a control experiment, not a feature-stacking attempt.

Goal:

```text
Test whether EXP-005A's 0.17 result is reproducible when wall-clock stochastic seeding is removed.
```

## Result

```text
EXP-005D — Deterministic EXP-005A Replay Control
Version: 13
Status: Succeeded
Public score: 0.10
Best score remained: EXP-005A / V9 public score 0.17
```

The downloaded EXP-005D artifacts are visible-notebook placeholders only:

```text
exp005d_bfs_events.jsonl:
  status: placeholder_only
  reason: KAGGLE_IS_COMPETITION_RERUN was not set, so main.py --agent myagent did not run.

exp005d_run_summary.json:
  status: placeholder_only
  mode: non_rerun_notebook_mode
```

Therefore, the artifacts do not explain scoring-time BFS behavior. The public score is the reliable validation signal.

## Experiment Arc

| Experiment | Public score | Interpretation |
|---|---:|---|
| EXP-000 | 0.07 | Clean random baseline and submission mechanics. |
| EXP-001 | 0.11 | Visible-pixel clicking improved over pure random. |
| EXP-002C | 0.11 | Local seed schedule did not generalize publicly. |
| EXP-003B | 0.12 | First real public improvement from online progress prior. |
| EXP-003F V6 | 0.12 | Public tie, not a new baseline. |
| EXP-005 | 0.08 | Minimal source-BFS scaffold regressed. |
| EXP-005A | 0.17 | Hidden-state-aware hashing validated source-BFS direction. |
| EXP-005B | 0.09 | Broad action scan likely increased branching/search cost. |
| EXP-005C | 0.10 | Level transfer likely added fragility or overhead. |
| EXP-005D | 0.10 | Deterministic replay did not reproduce EXP-005A. |

## Interpretation

EXP-005D preserved the important EXP-005A planner components:

- source-BFS backbone,
- hidden scalar probing,
- frame plus hidden-field state hashing,
- EXP-005A simple stride-2 effective-action scan,
- no EXP-005B broad scan,
- no EXP-005C transfer.

The major behavioral change was seeding:

```text
EXP-005A: wall-clock/randomized agent seed path
EXP-005D: deterministic MD5-based game/level seed path
```

The score drop from `0.17` to `0.10` suggests that EXP-005A's public result may have depended materially on stochastic fallback trajectories. If BFS replay alone were carrying most of the result, EXP-005D should have stayed close to `0.17`.

This does not prove that BFS failed in EXP-005D. It proves that the deterministic control did not preserve the useful behavior observed in EXP-005A.

## Decision Matrix

Planned rule from the 2026-05-22 note:

| EXP-005D outcome | Decision |
|---|---|
| `≈ 0.17` | EXP-005A is stable enough. Use deterministic EXP-005D as clean baseline and plan EXP-005E gated scan. |
| `< 0.17` | EXP-005A may depend on stochastic fallback. Investigate fallback stability before planner feature work. |
| `> 0.17` | Deterministic seeding helped. Promote EXP-005D as new baseline. |

Actual outcome:

```text
EXP-005D = 0.10 < 0.17
```

Decision:

```text
Keep EXP-005A V9 as current best.
Do not promote EXP-005D.
Do not continue EXP-005C2.
Do not start EXP-005E gated scan yet.
Investigate fallback stability and BFS/fallback attribution first.
```

## Next Experiment Recommendation

Create an attribution diagnostic before any new planner feature:

```text
EXP-005A/005D attribution diagnostic
```

Minimum requirements:

1. Preserve EXP-005A behavior as closely as possible.
2. Add explicit scoring-time diagnostics for:
   - source path found or missing,
   - game class load success or failure,
   - scan effective action count,
   - hidden fields detected,
   - BFS solve status,
   - solution length,
   - BFS replay action count,
   - fallback action count,
   - explicit fallback reason.
3. Save real competition-rerun artifacts, not only visible-notebook placeholders.
4. Avoid broad scan, transfer, or fallback replacement until the `0.17 -> 0.10` drop is isolated.

## Working Hypothesis

```text
EXP-005A = source-BFS + hidden-hash + beneficial stochastic fallback.
EXP-005D = source-BFS + hidden-hash + deterministic fallback.
The deterministic fallback trajectory lost useful accidental progress.
```

This hypothesis should be treated as likely but unproven until scoring-time BFS/fallback attribution logs are available.
