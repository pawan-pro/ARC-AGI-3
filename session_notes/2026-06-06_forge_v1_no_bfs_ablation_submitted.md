# 2026-06-06 Session Notes — FORGE V1 No-BFS Ablation Submitted

## Session context

We continued from the validated FORGE V1 instrumented baseline.

Latest validated result:

```text
FORGE-V1 instrumented notebook — Version 1
Public score: 0.26
Status: Succeeded
```

This matched the clean FORGE V1 reproduction score of approximately `0.26`, which confirmed that the instrumentation itself was behaviorally safe.

Prior invalid regression:

```text
FORGE ARC-AGI-3 Agent V2: 0.10
Cause: accidental random-only fallback path replaced the original CNN fallback.
```

Therefore, the V2 result is not a valid instrumentation result and should not be used as the baseline.

## What was done today

### 1. Interpreted the validated instrumented FORGE V1 score

The instrumented notebook scored:

```text
0.26
```

Interpretation:

- Instrumentation did not degrade performance.
- FORGE V1 instrumented is now a validated diagnostic baseline.
- The current reliable reproduced baseline remains `0.26`.

### 2. Decided next controlled ablation

We selected the next experiment:

```text
FORGE V1 no-BFS ablation
```

Purpose:

```text
Measure whether BFS is helping, neutral, or hurting the current public score.
```

Reason:

The current public score gap remains unresolved:

```text
Historical FORGE / public references: 0.35–0.46
Current reproduced stable range: approximately 0.20–0.26
```

Since scoring-time JSON artifacts are usually not exposed by Kaggle, controlled score-delta ablations are now the cleanest way to estimate module contribution.

### 3. Created no-BFS notebook artifact

Created downloadable notebook:

```text
forge-arc-agi-3-agent-v1-no-bfs-ablation.ipynb
```

The ablation disables:

- BFS initialization.
- BFS solve attempts.
- BFS replay.
- CLTI replay injection from BFS solutions.

The ablation preserves:

- original CNN fallback path.
- replay learning.
- action-effect memory.
- heuristic fallback behavior.
- submission wrapper.

### 4. User action

The user ran the no-BFS ablation notebook and submitted it to Kaggle for scoring.

Current state:

```text
FORGE V1 no-BFS ablation: submitted for scoring
Public score: pending
```

## Decision matrix for no-BFS score

| No-BFS public score | Interpretation | Next action |
|---:|---|---|
| Near 0.25–0.26 | BFS contributes little under current evaluation; focus on CNN/fallback/exploration. | Try no-CLTI or shorter-BFS ablation next. |
| Higher than 0.26 | BFS is hurting current score; add gating, reduce timeouts, or route BFS selectively. | Build gated-BFS experiment. |
| Much lower than 0.26, especially below 0.20 | BFS is important; optimize BFS/action pruning rather than remove it. | Build BFS profiling / pruning experiment. |
| Kaggle Error | Ablation broke wrapper or policy path. | Inspect log, restore baseline. |

## What worked

- Validated that FORGE V1 instrumentation is safe.
- Established FORGE V1 instrumented as the diagnostic baseline.
- Created a controlled no-BFS ablation rather than making speculative architecture changes.
- Preserved the CNN fallback path in the ablation.
- User ran and submitted the ablation for scoring.

## What failed / unresolved

- Public score for no-BFS ablation is pending.
- Scoring-time JSON diagnostics are still unavailable / not expected to be exposed.
- GitHub still needs the full notebook bodies pushed from local or via a reliable large-file workflow; previous connector attempts struggled with full `.ipynb` replacement.

## Current best score/result

Reliable reproduced baseline:

```text
FORGE V1 instrumented: 0.26
```

Pending experiment:

```text
FORGE V1 no-BFS ablation: score pending
```

## Files / artifacts

Generated notebook artifact:

```text
forge-arc-agi-3-agent-v1-no-bfs-ablation.ipynb
```

Created GitHub session note:

```text
session_notes/2026-06-06_forge_v1_no_bfs_ablation_submitted.md
```

## Next session plan

1. Record no-BFS public score.
2. Compare no-BFS score against validated baseline `0.26`.
3. Decide whether BFS is helpful, neutral, or harmful.
4. If no-BFS is near baseline, test no-CLTI or shorter-BFS next.
5. If no-BFS improves, design gated-BFS experiment.
6. If no-BFS drops materially, design BFS profiling/action-pruning experiment.
