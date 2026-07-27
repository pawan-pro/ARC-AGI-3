# 2026-07-27 Duck tu93 Level-3 Route and Visual Review

## Baseline decision

EXP-DUCK-026 completed at public score `0.86`, so EXP-DUCK-024 remains the
active public baseline at `1.11`.

The isolated tu93 levels 1-2 calculator remains valid, but it did not activate
in the EXP-DUCK-026 full run because normal Duck had already completed both
levels.

## Visual review

A local comparison page was generated at:

```text
artifacts/kaggle/duck_calculator_visual_review/index.html
```

It contains playable replays and final-board stills for:

1. tn36 before the calculator in EXP-DUCK-009;
2. tn36 with the postlude in the `1.11` EXP-DUCK-024 notebook;
3. the isolated two-level tu93 calculator proof;
4. the EXP-DUCK-026 tu93 state where normal Duck reached level 3 and the
   postlude correctly skipped.

## Official tu93 level-3 analysis

The exact competition source was downloaded from:

```text
environment_files/tu93/0768757b/tu93.py
```

It was executed locally with the official `arcengine==0.9.3` runtime under
Python 3.12. A breadth-first search explored the true movement, collision,
enemy, and 35-step-budget rules.

The clean level-3 board has CRC32:

```text
0x936EEEB5
```

The search reached level 4 in 19 actions:

```text
UP, UP, RIGHT, UP,
LEFT, LEFT, UP, LEFT, LEFT,
DOWN, RIGHT, DOWN,
LEFT, LEFT, LEFT,
DOWN, RIGHT, DOWN, RIGHT
```

This is genuinely new progress beyond the previously validated levels 1-2.

## EXP-DUCK-027 gate

The isolated notebook replays all three exact-board routes:

```text
level 1: 18 actions
level 2: 10 actions
level 3: 19 actions
total:   47 actions
tokens:  0
```

Kaggle Version 1:

```text
jatalepawan/arc-agi-3-duck-tu93-level-3-route
```

Do not run a full evaluation or create a competition submission unless Kaggle
confirms exactly `3/9` levels, 47 actions, zero analysis events, and all three
success notes.
