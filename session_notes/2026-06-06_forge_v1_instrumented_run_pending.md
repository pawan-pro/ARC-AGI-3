# 2026-06-06 Session Notes — FORGE V1 Instrumented Run Pending

## Session context

We continued ARC-AGI-3 work from the FORGE V1 instrumentation phase.

The clean reproduced FORGE V1 baseline was approximately:

```text
FORGE ARC-AGI-3 Agent V1 reproduction: 0.26
```

A prior instrumented attempt, FORGE V2, scored:

```text
FORGE ARC-AGI-3 Agent V2: 0.10
```

That 0.10 run was diagnosed as invalid because the notebook accidentally replaced the original CNN fallback path with a random-only fallback block.

## What was done today

### 1. Prepared the corrected instrumented FORGE V1 notebook

The user uploaded/downloaded the corrected instrumented notebook artifact:

```text
forge-arc-agi-3-agent-v1-instrumented-clean.ipynb
```

Purpose:

```text
Verify that instrumentation can be added without materially changing FORGE V1 behavior.
```

Instrumentation intent:

- Preserve the original FORGE V1 policy path.
- Preserve BFS logic.
- Preserve CNN fallback.
- Preserve replay learning.
- Preserve action-effect memory.
- Preserve transfer heuristics.
- Add observability around runtime and solver use.

Expected diagnostics:

```text
/kaggle/working/forge_v1_instrumentation.jsonl
/kaggle/working/forge_v1_run_summary.json
```

### 2. Discussed visible notebook output versus scoring output

We clarified that the visible Kaggle notebook run can confirm only:

- pip install succeeded.
- `my_agent.py` was written.
- notebook syntax/build did not crash.
- dummy fallback submission was produced in non-rerun mode.

It cannot confirm the real ARC-AGI-3 public score because actual scoring only happens under:

```python
if os.getenv("KAGGLE_IS_COMPETITION_RERUN"):
    ...
    python main.py --agent myagent
```

Decision:

```text
Submit the notebook for scoring once the visible notebook run finishes.
```

### 3. User submitted for scoring

The user reported that the corrected instrumented notebook was uploaded to Kaggle, run, and submitted for scoring.

Current state:

```text
FORGE V1 instrumented notebook: submitted for scoring
Public score: pending
```

## Decision matrix for the score

### Case A — Score near clean baseline

Expected range:

```text
0.24–0.27
```

Decision:

```text
Instrumentation is safe enough. Use this as the diagnostic baseline.
```

Next step:

- Inspect logs if available.
- If JSON is not exposed, proceed with controlled score-delta ablations.

### Case B — Score collapses

Threshold:

```text
<= 0.15
```

Decision:

```text
Instrumentation still disturbed runtime or policy behavior.
```

Next step:

- Revert to clean FORGE V1.
- Re-patch with lighter instrumentation.
- Confirm CNN fallback is not bypassed.

### Case C — Score improves materially

Threshold:

```text
> 0.30
```

Decision:

```text
Likely variance or instrumentation changed timing favorably. Do not overclaim improvement from one run.
```

Next step:

- Repeat once if compute allows.
- Freeze as candidate only if repeated.

### Case D — Kaggle Error

Decision:

```text
Notebook invalid or environment setup broken.
```

Next step:

- Inspect build log.
- Check `my_agent.py` generation.
- Check imports, indentation, and submission wrapper.

### Case E — Score near 0.25 but no JSON output

Decision:

```text
Instrumentation is behaviorally safe, but Kaggle still does not expose scoring-time JSON artifacts.
```

Next step:

- Use stdout logs if exposed.
- Otherwise use controlled score-delta ablations.

## What worked

- Corrected our approach after diagnosing the V2 random-only fallback regression.
- Preserved the correct FORGE V1 policy intent in the uploaded instrumented notebook.
- Confirmed that scoring submission is necessary; visible notebook output is insufficient.
- Submitted the instrumented notebook for scoring.

## What failed / unresolved

- Scoring result is pending.
- GitHub still has a placeholder notebook file at:

```text
notebooks/01_exploration/forge-arc-agi-3-agent-v1-instrumented.ipynb
```

- Full notebook replacement through the connector remains unresolved.
- It is still unknown whether Kaggle will expose scoring-time JSON artifacts.

## Current best score/result

Current usable reproduced baseline:

```text
FORGE ARC-AGI-3 Agent V1 reproduction: 0.26
```

Invalid regression:

```text
FORGE ARC-AGI-3 Agent V2: 0.10
Reason: random-only fallback path
```

Current pending experiment:

```text
FORGE V1 instrumented notebook
Submission: submitted for scoring
Score: pending
```

## Files changed

Created:

```text
session_notes/2026-06-06_forge_v1_instrumented_run_pending.md
```

## Next session plan

1. Record the Kaggle public score for the real instrumented FORGE V1 notebook.
2. Check whether any JSON artifacts are exposed.
3. Compare score against the clean V1 baseline of 0.26.
4. If score is near baseline, use the instrumented notebook as the diagnostic baseline.
5. If no scoring-time JSON appears, shift to controlled score-delta ablations.
6. First recommended ablation after validation: `V1 no-BFS`, to estimate BFS contribution.
