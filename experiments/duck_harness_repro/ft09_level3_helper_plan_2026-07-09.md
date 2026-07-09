# ft09 Level-3 Helper Plan - 2026-07-09

Source run:

```text
artifacts/kaggle/duck_controlled_stall_policy/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
```

## What Happened

The clean targeted run solved `ft09` levels 1 and 2, then stalled on level 3.

```text
actions_per_level = [29, 7, 90, 0, 0, 0]
```

Level 3 starts as a diamond-shaped red/orange toggle board. Normal cells toggle between red and orange when clicked. Four special cells do not toggle; they contain tiny 3x3 white/gray masks.

The model correctly noticed the mask structure, but then tried overlapping interpretations manually. That is exactly the kind of work code should do instead.

## Helper Strategy

Generate a small suite of candidate target boards from the four masks:

```text
1. white means orange, gray means red
2. white means the special cell's center color, gray means the other color
3. gray means the special cell's center color, white means the other color
```

For overlapping mask votes, try compact combination rules:

```text
orange wins
red wins
majority
parity
last writer wins
```

For each candidate target board:

```text
1. click only cells whose current color differs from the target
2. stop immediately if a level completes
3. if not solved, toggle to the next candidate by clicking the symmetric difference
4. after the candidate suite is exhausted, fall back to the LLM
```

This should replace 90 exploratory LLM actions with a small deterministic probe.

## Why This Is Safer Than Prompt Tuning

Prompt tuning would still ask the model to reason through overlapping masks repeatedly. The helper does the repetitive bookkeeping directly and lets the model handle the cases where the helper fails.

## Local Tooling Added

```text
experiments/duck_harness_repro/ft09_mask_helper.py
```

Run:

```bash
python experiments/duck_harness_repro/ft09_mask_helper.py \
  artifacts/kaggle/duck_controlled_stall_policy/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
```

