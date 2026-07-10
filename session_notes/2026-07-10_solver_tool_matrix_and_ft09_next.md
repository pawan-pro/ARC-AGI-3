# 2026-07-10 Session - Solver Tool Matrix and ft09 Next Step

## Starting Point

The `ft09-helper` Kaggle run completed and improved `ft09` from 2 solved levels to 3 solved levels.

```text
baseline ft09:       2/6, actions_per_level = [42, 21, 19, 0, 0, 0], tokens = 70,043
stall ft09:          2/6, actions_per_level = [29, 7, 90, 0, 0, 0], tokens = 71,628
ft09-helper ft09:    3/6, actions_per_level = [9, 7, 32, 172, 0, 0], tokens = 100,578
```

The helper solved level 3 with:

```text
ft09_helper = white_is_center + parity
helper_actions = 32
```

## Strategic Clarification

The goal is not to hardcode one puzzle. The goal is to build a solver tool matrix:

```text
LLM recognizes puzzle family.
Helper tool executes exact bookkeeping/clicking.
Stall guard stops waste.
LLM resumes if no helper applies.
```

The `ft09` helper generalizes only when the board has the same family signature:

```text
two-color toggle cells
special cells containing local white/gray masks
single-cell mouse toggle action
level progress after a target pattern is reached
```

## Current Interpretation

`ft09` level 3 was not blocked by raw model intelligence. The model had the right intuition, but it spent too many actions trying mask interpretations manually. The deterministic helper converted that repeated reasoning into candidate target boards and solved the level.

This supports the broader architecture:

```text
Use LLM for recognition and hypothesis.
Use tools for exhaustive exact candidate tests.
```

## Next Recommended Experiment

Inspect `ft09` level 4 from:

```text
artifacts/kaggle/duck_ft09_helper/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
artifacts/kaggle/duck_ft09_helper/latest/transcripts/ft09-0d8bbf25_p0.txt
```

Question to answer:

```text
Is level 4 another mask/toggle level with different geometry, or a different mechanic?
```

If level 4 is same-family:

```text
Generalize ft09 helper from hardcoded level-3 coordinates to detected cell centers and detected special masks.
```

If level 4 is different:

```text
Add a second helper rather than stretching the level-3 helper beyond its applicability.
```

