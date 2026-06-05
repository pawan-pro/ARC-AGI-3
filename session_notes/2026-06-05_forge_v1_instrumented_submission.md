# 2026-06-05 Session Notes — FORGE V1 Instrumented Submission

## Session context

We resumed ARC-AGI-3 work from the reproducibility and instrumentation phase.

Recent reproducibility results showed that public notebook scores did not replicate cleanly:

```text
FORGE ARC-AGI-3 Agent V1 reproduction: 0.26
FORGE ARC-AGI-3 Agent V2 instrumented/broken fallback: 0.10
[0.35] FORGE v16 Trigger-aware BFS reproduction: 0.23
baseline_v19_public: 0.20
```

The key diagnosis from the V2 result was that the submitted V2 notebook had accidentally replaced the real CNN fallback path with a random-only fallback block, causing a true behavioral regression rather than a valid instrumentation result.

## What was done

### 1. Analyzed FORGE V2 regression

The FORGE ARC-AGI-3 Agent Version 2 submission scored:

```text
Public score: 0.10
Status: Succeeded
```

The notebook log showed normal notebook execution and `my_agent.py` creation, so the low score was not caused by a notebook build crash.

Root cause identified:

```text
The fallback path had been replaced by random movement selection.
```

This bypassed the original FORGE CNN fallback, replay learning, click heatmap sampling, action-effect memory, heuristic click logic, and training loop.

Conclusion:

```text
Do not treat V2 as a valid instrumented FORGE result.
Revert to the clean FORGE V1 logic before adding instrumentation.
```

### 2. Patched uploaded FORGE V1 notebook locally

The user uploaded the FORGE ARC-AGI-3 Agent notebook corresponding to the usable V1 baseline lineage.

A new instrumented notebook was generated locally:

```text
forge-arc-agi-3-agent-v1-instrumented-clean.ipynb
```

Instrumentation goal:

```text
Add observability without changing policy behavior.
```

The patch was intended to preserve:

- BFS search logic.
- CNN fallback policy.
- Replay learning.
- Action-effect memory.
- Reward function behavior.
- Transfer heuristics.
- Heuristic fallback logic.

Diagnostics added included:

- BFS attempts.
- BFS solved/failed counts.
- Transfer success counts.
- Hidden-state retry counts.
- Warm-up unlock counts.
- Explored states.
- Unique states.
- Queue pressure.
- Level-entry logs.
- BFS action counts.
- CNN action counts.
- Undo/reset/train counts.
- Pretrained weight loading status.
- Run summary JSON/log outputs.

Expected Kaggle diagnostic outputs:

```text
/kaggle/working/forge_v1_instrumentation.jsonl
/kaggle/working/forge_v1_run_summary.json
```

### 3. GitHub status

The ARC repo is accessible:

```text
pawan-pro/ARC-AGI-3
```

A placeholder notebook file was created earlier on `main`:

```text
notebooks/01_exploration/forge-arc-agi-3-agent-v1-instrumented.ipynb
```

Commit:

```text
7db9510cd450438226bac77348f388c90b066bce
Add instrumented FORGE ARC-AGI-3 V1 notebook
```

Issue:

```text
The file currently contains only a placeholder payload, not the real notebook body.
```

The GitHub connector write for the full notebook replacement was blocked, so the full instrumented notebook still needs to be committed manually from the local downloaded file.

Required local Git fix:

```bash
git checkout main
git pull origin main
cp ~/Downloads/forge-arc-agi-3-agent-v1-instrumented-clean.ipynb \
  notebooks/01_exploration/forge-arc-agi-3-agent-v1-instrumented.ipynb
git add notebooks/01_exploration/forge-arc-agi-3-agent-v1-instrumented.ipynb
git commit -m "Replace placeholder with instrumented FORGE ARC-AGI-3 V1 notebook"
git push origin main
```

### 4. Kaggle action

The user downloaded the real instrumented notebook and uploaded it to Kaggle manually.

The user then ran and submitted the real instrumented notebook for scoring.

Current Kaggle state:

```text
FORGE V1 instrumented notebook: submitted for scoring
Public score: pending
```

## What worked

- Identified why FORGE V2 collapsed to 0.10.
- Avoided treating the broken V2 as a valid instrumentation result.
- Generated a real instrumented FORGE V1 notebook locally.
- Preserved the intended policy path in the generated instrumented notebook.
- User uploaded and submitted the real instrumented notebook to Kaggle.
- ARC GitHub repo is accessible.
- Session note committed to GitHub.

## What failed / unresolved

- GitHub currently contains only a placeholder notebook at the intended instrumented notebook path.
- Full notebook replacement via the connector was blocked.
- The full instrumented notebook still needs to be pushed from local Git.
- Kaggle score for the real instrumented notebook is pending.
- It is not yet known whether instrumentation affects runtime enough to change the public score.

## Current best score/result

Current usable reproduced baseline:

```text
FORGE ARC-AGI-3 Agent V1 reproduction: 0.26
```

Invalid / diagnostic regression:

```text
FORGE ARC-AGI-3 Agent V2: 0.10
Reason: random-only fallback regression
```

Historical public references remain:

```text
[ARC26-3] Agent v15: 0.46
Ash's ARC-AGI-3 Agent: 0.42
FORGE ARC-AGI-3 Agent: 0.39
FORGE v16 Trigger-aware BFS: 0.35
```

## Files changed

Created on GitHub:

```text
session_notes/2026-06-05_forge_v1_instrumented_submission.md
```

Existing placeholder file on GitHub:

```text
notebooks/01_exploration/forge-arc-agi-3-agent-v1-instrumented.ipynb
```

Local real notebook artifact used by the user:

```text
forge-arc-agi-3-agent-v1-instrumented-clean.ipynb
```

## Next session plan

1. Wait for Kaggle score for the real instrumented FORGE V1 notebook.
2. Download/upload the Kaggle log and output artifacts.
3. Compare score against the clean V1 baseline score of 0.26.
4. If score remains close to 0.26, treat instrumentation as safe and inspect metrics.
5. If score collapses, inspect whether instrumentation altered runtime or policy flow.
6. Replace the GitHub placeholder notebook with the real notebook from local Git.
7. Only after instrumentation is validated, proceed to targeted changes such as BFS action pruning or runtime profiling.
