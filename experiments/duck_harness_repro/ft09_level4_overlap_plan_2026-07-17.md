# ft09 Level-4 Overlap-Consistent Test Plan

Date: 2026-07-17

Experiment: `EXP-DUCK-008`

Notebook:

```text
notebooks/04_submission_builds/duck_public_repro_terminal_run/arc3_20260704_duck_public_repro_ft09_level4_overlap.ipynb
```

Kaggle kernel:

```text
jatalepawan/arc-agi-3-duck-ft09-level4-overlap
```

## Test

1. Replay the proven 48-action prefix to reach level 4.
2. Verify the exact three-clue board signature.
3. Apply only target `RORbRRRRRORRbRROOO`.
4. Stop immediately after success, failure, or all 21 planned clicks.

This is a zero-token mechanic test. It does not call the LLM for level 4 and
does not cycle through alternate candidates.

## Why This Target

White copies each clue's center color. Gray must be a different palette color.
Requiring overlapping clue neighborhoods to agree produces exactly one gray
assignment: red for all three clues.

K-12 version: three transparent clue cards overlap. Only red lets every shared
square tell the same story, so we test that one answer instead of guessing.

## Decision Gate

Positive:

```text
ft09 advances from 3/6 to at least 4/6
```

Negative:

```text
the prefix reaches level 4, all 21 clicks execute, and level 4 remains unsolved
```

Invalid:

```text
the replay does not reach level 4, or the clue signature does not match
```

The full evaluation notebook remains gated until this targeted run is positive.
