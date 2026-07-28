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
