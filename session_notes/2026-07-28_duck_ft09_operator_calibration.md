# EXP-DUCK-032: ft09 Operator Calibration

## Goal

Explain why EXP-DUCK-031 executed perfectly but failed to solve level 5, then
form a new target only after passing closed-book calibration on solved levels.

## Reconstructed Training Evidence

The accepted targets from levels 1-4 were reconstructed from their initial
boards, observed click cycles, and level-completion traces:

```text
level 1: 8 target cells, 1 clue
level 2: 13 target cells, 2 clues
level 3: 23 target cells, 4 clues
level 4: 18 target cells, 3 clues
```

All four levels teach the same relational meanings:

```text
pixel mark 0: same as the clue center
pixel mark 2: different from the clue center
```

## Closed-Book Calibration

Each solved level was hidden in turn. The model learned from the other three
levels and predicted the hidden accepted target.

```text
held-out level 1: 1 target, exact
held-out level 2: 1 target, exact
held-out level 3: 1 target, exact
held-out level 4: 1 target, exact
```

Level 4 required the calibrated global palette because its accepted red state
was present in earlier levels but absent from its untouched board.

## EXP-DUCK-031 Diagnosis

The rejected learner made two concrete mistakes:

1. It allowed the learned white/light-gray roles to reverse.
2. It classified three magenta cross cells as clues rather than fixed
   obstacles.

That produced the rejected 18-click target.

## New Level-5 Objective

After applying the calibrated roles and separating obstacles:

```text
normal cells: 27
true clues: 8
fixed obstacles: 3
uncovered cells retained unchanged: 1
unknown mark-3 interpretations: 2
actionable target signatures: 1
planned clicks: 9
cells different from rejected target: 27/27
```

The two surviving meanings of the new dark-gray mark produce the same target,
so the semantic uncertainty cannot change an action.

## Gate

```text
focused tests: 5/5
structural checks: 12/12
private isolated Kaggle run: APPROVED
full evaluation: NOT YET
competition submission: NO
```

The isolated run must advance from level 5 to level 6 with all nine predicted
effects intact. No full evaluation should be built unless that causal gate
passes.

## Kaggle Launch

Private kernel Version 1 was pushed successfully:

```text
jatalepawan/arc-agi-3-duck-ft09-level-5-calibrated
status after push: RUNNING
GPU: enabled
internet: disabled
competition submission: NO
```

The shared GPU environment may take about two hours to initialize. The result
will be downloaded and validated after the kernel reaches a terminal state.

## Live Result

```text
levels completed: 4/6
actions per level: [9, 7, 32, 21, 9, 0]
total actions: 78
tokens: 0
level-5 helper actions: 9
correct observed effects: 9/9
final target mismatches: 0
level-5 progress: 0
```

The calibrated helper activated with the expected 27 normal cells, 8 clues,
3 magenta cells, 2 action-equivalent unknown-mark models, and 1 unchanged
uncovered cell. It executed the exact nine-click plan. Every selected green
cell became purple as predicted, and the final board matched the frozen
target. The game remained on level 5.

## Interpretation

Closed-book calibration on levels 1-4 was necessary but not sufficient for
level 5. Level 5 introduces a new mechanic that cannot be explained by either
complementary coloring of the 27 normal cells:

```text
EXP-DUCK-031: 18-click complement rejected
EXP-DUCK-032: 9-click complement rejected
```

The control and effect models are sound. The objective model is still
incomplete.

## Decision

```text
structural validation: PASS
causal level-gain gate: FAIL
full evaluation: NO
competition submission: NO
```

## Next Gate: EXP-DUCK-033

Do not test another normal-cell target. The next controlled experiment should
start from clean level-5 boards and probe the centers of the three magenta
cells separately:

```text
(14, 24)
(30, 24)
(46, 40)
```

Each arm should record whether one click is a no-op, changes the special cell,
changes neighboring cells, unlocks normal cells, causes game over, or advances
the level. This is a mechanic-identification experiment, not a scoring run.
