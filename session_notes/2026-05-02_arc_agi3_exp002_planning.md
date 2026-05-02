# 2026-05-02 ARC-AGI-3 EXP-002 planning

## Objective

Start from the validated EXP-001 Kaggle result and design the next small, testable improvement.

## Current state

- EXP-000 public score: 0.07
- EXP-001 public score: 0.11
- EXP-001 notebook: notebook338b6b3c9c, Version 2, Succeeded
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183
- EXP-001 public result is now the best validated Kaggle baseline.

## Interpretation

EXP-001 improved the public score from 0.07 to 0.11. This validates that visible-pixel random clicking is better than pure random action selection, but it remains a weak exploratory policy.

The local-to-public gap is material:

- local score: 0.2124
- public score: 0.11

So local validation should be treated as directional only. Public Kaggle submissions remain the real validation source.

## Useful evidence from ls20 visual inspection

The public demo for task ls20 shows a maze-like game where the blue/orange player can move through corridors and collect yellow target blocks. A human can solve this by planning movement paths, not by random clicking.

Implication for EXP-002: random visible pixels are not enough. We need simple state tracking and movement/object heuristics.

## Engine/action knowledge

Known action conventions from ARCEngine documentation:

- ACTION1 = up
- ACTION2 = down
- ACTION3 = left
- ACTION4 = right
- ACTION5 = spacebar
- ACTION6 = click with x,y coordinates
- ACTION7 = undo

This suggests EXP-002 should stop treating action IDs as opaque random tokens. At minimum, movement actions should be interpreted as directional actions.

## EXP-002 hypothesis

A small heuristic explorer should beat EXP-001 if it:

1. detects the likely player/object blob,
2. detects non-background target objects,
3. uses directional actions to reduce distance to targets,
4. avoids repeated no-op movements,
5. avoids ACTION7 unless explicitly useful,
6. uses ACTION6 click only when a clickable object is likely.

## EXP-002 proposed files

- notebooks/01_exploration/exp002_visible_object_heuristic_explorer.ipynb
- experiments/EXP-002_visible_object_heuristic_explorer/README.md
- experiments/EXP-002_visible_object_heuristic_explorer/results_2026-05-02.md after validation

## Validation target

Before submission:

- local score >= 0.2124
- local levels >= 7 / 183
- submission.parquet created
- no runtime failure

Official success criterion:

- public score > 0.11

## Fallback plan

If EXP-002 local score is below EXP-001, do not submit. Keep EXP-001 as the Kaggle baseline and run ablations.

## Next implementation plan

1. Create EXP-002 notebook as a copy-independent experiment, not an edit to EXP-001.
2. Add frame parser:
   - count colors,
   - identify background colors by large area,
   - identify small colored blobs as possible player/targets.
3. Add movement policy:
   - prefer ACTION1/ACTION2/ACTION3/ACTION4 toward nearest target-like blob,
   - if frame does not change after a movement, suppress that action briefly.
4. Keep random fallback for unknown states.
5. Run local validation and compare with EXP-001.
