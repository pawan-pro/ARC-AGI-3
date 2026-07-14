# ft09 Level-4 Candidate Truth Table

Date: 2026-07-14

Source run:

```text
artifacts/kaggle/duck_ft09_level4_isolated/latest/
```

Helper reconstruction script:

```text
experiments/duck_harness_repro/ft09_level4_truth_table.py
```

## Setup

The replay prefix reached level 4 at action 48. At that moment the 18 sampled normal cell centers were all blue:

```text
bbbbbbbbbbbbbbbbbb
```

Special clue masks at level-4 start:

```text
special (24, 22), center O
gWg
gOg
gWg

special (24, 38), center b
gWg
gbg
ggW

special (40, 30), center O
Wgg
gOg
WWW
```

Cell center string order:

```text
(16,14) (16,22) (16,30) (16,38) (16,46)
(24,14) (24,30) (24,46)
(32,14) (32,22) (32,30) (32,38) (32,46)
(40,22) (40,38)
(48,22) (48,30) (48,38)
```

Color cycle:

```text
b -> R -> O -> b
```

## Candidate Trace

| Candidate | Actions | Completed? | Changed pixels | Before centers | Target centers | After centers |
|---|---:|---|---:|---|---|---|
| `level4:gray_is_center+blue_wins` | 12 planned / 12 executed, actions 49-60 | yes | 440 | `bbbbbbbbbbbbbbbbbb` | `ObbRbObbObbbROObbb` | `ObbRbObbObbbROObbb` |
| `level4:white_cycles_from_center+parity` | 15 planned / 15 executed, actions 61-75 | yes | 550 | `ObbRbObbObbbROObbb` | `RbbRORbORbRbRRRbbb` | `RbbRORbORbRbRRRbbb` |
| `level4:white_is_center+majority` | 30 planned / 30 executed, actions 76-105 | yes | 1100 | `RbbRORbORbRbRRRbbb` | `bObbRbbRbObbbbbOOO` | `bObbRbbRbObbbbbOOO` |
| `level4:gray_is_center+majority` | 23 planned / 15 executed, actions 106-120 | no, stopped mid-candidate | 550 | `bObbRbbRbObbbbbOOO` | `ObbRbObbObObROObbb` | `ObbRbObbObObbbbOOO` |

## Interpretation

This is a useful negative result, but it also exposes an experimental bug.

The helper did not exhaust all 8 planned candidates. It was stopped at action 120 by the zero-token stall guard:

```text
max_consecutive_zero_token_actions = 120
```

Because the diagnostic replay and helper actions are all zero-token actions, the stall guard counted the 48 replay actions plus 72 helper actions and stopped the run partway through candidate 4.

K-12 version: the helper was still trying candidate 4 when the safety timer said, "you have clicked enough without talking," and ended the run.

## What We Learned

The click executor is working:

- every completed candidate reached its intended target center colors exactly
- clicks changed the board consistently
- no action-coordinate mismatch appeared in the reconstructed trace

The failed part is not low-level clicking. It is the rule that chooses target layouts from the clue masks.

The current candidates are too guessy:

- candidate 1 sets only a few cells and fails
- candidate 2 changes to a different color layout and fails
- candidate 3 makes a large transformation and fails
- candidate 4 was interrupted before completion

## Next Run

For the next diagnostic, do not change the LLM or prompt. Change the instrumentation:

1. Disable or raise the zero-token stall cap during deterministic replay/helper actions.
2. Log `candidate_name`, `planned_actions`, `executed_actions`, `before_centers`, `target_centers`, and `after_centers` into `solver_note` or a small JSON artifact.
3. Run all 8 candidates to true exhaustion.
4. If all 8 fail, inspect the level-4 visual mapping directly rather than adding more candidate guesses.

Recommended next variant:

```text
EXP-DUCK-006: ft09 level-4 fully instrumented candidate exhaustion
```
