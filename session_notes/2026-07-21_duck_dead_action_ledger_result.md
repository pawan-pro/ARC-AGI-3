# Duck Dead-Action Ledger Result

Date: 2026-07-21  
Experiment: EXP-DUCK-010  
Active public baseline: EXP-DUCK-009, score `0.92`

## Question

Can Duck safely remember actions that did nothing and avoid trying them again?

The proposed ledger used two tests after two observed no-effect attempts:

1. **Exact-state rule:** same level, same visible board, and same exact action.
2. **Structural rule:** same level and same action/object shape. Mouse objects are described by color, connected size, bounding box, rectangle status, and number of matching twins.

This experiment only replayed stored logs. It did not change the solver or spend Kaggle GPU time.

## Evidence

| Stored run | Actions reviewed | Exact no-effect | Exact candidates | Exact unsafe | Structural candidates | Structural unsafe |
|---|---:|---:|---:|---:|---:|---:|
| Duck baseline (`0.84`) | 682 | 12 | 1 | 1 | 0 | 0 |
| EXP-DUCK-009 full evaluation (`0.92`) | 1,118 | 69 | 4 | 2 | 5 | 0 |

All five safe structural candidates were repeated clicks in `sc25` at `MOUSE(row=19, col=14)`. Blocking them would save only five of 1,118 actions, or about `0.45%`.

The exact-state rule was not safe. Two of its four proposed blocks in the full evaluation later changed the board. The baseline's only proposed exact block also changed the board. This means the visible screen is not the complete game state; animation, timing, or hidden state can make an apparently identical retry behave differently.

The larger pattern is more important:

- 1,117 of 1,118 full-evaluation actions did not increase level, score, or reward.
- Many of those actions still changed pixels, so a simple no-change detector calls them "effective" even when they do not solve anything.
- `tr87` had a 37-action `ACTION1` streak with no progress.
- `r11l` had repeated 60-click streaks with no progress.
- `tn36` had a 69-click streak that solved one level, followed by 61 and 28-click streaks with no progress.

## K-12 Explanation

Imagine a student is trying to open a combination lock.

The dead-action ledger watches whether the lock looks different after each move. That works for a button that truly does nothing. But some moves spin a dial or animate the screen without bringing the student closer to opening the lock. The screen changed, but the puzzle was not solved.

It is also unsafe to say, "This same move failed twice, so never try it again." The game may have a hidden timer or hidden memory. In our logs, some apparently identical third attempts did produce a visible change.

So the ledger is a useful notebook for observation, but it is not yet a good steering wheel for the solver.

## Decision

Do not add either veto to the live Duck notebook.

The generic rule offers too little saving and carries real regression risk. Keep the analyzer as a reusable trace diagnostic.

## Next Controlled Experiment

Use `tn36` as the next paired-trace case:

- baseline trace: `0` levels;
- EXP-DUCK-009 trace: `1` level;
- compare the successful first 69 clicks with the failed baseline sequences;
- identify the visual rule or click-order invariant that caused level progress;
- test a small `tn36` level-1 helper in isolation before another full evaluation.

This follows the successful ft09 pattern: learn a mechanic from evidence, build one narrow tool, validate it alone, and only then run the two-hour full notebook.

## Reproduction

```bash
python experiments/duck_harness_repro/test_dead_action_ledger.py

python experiments/duck_harness_repro/dead_action_ledger.py \
  artifacts/kaggle/duck_public_repro_terminal_run/latest \
  --output experiments/duck_harness_repro/dead_action_ledger_baseline.json

python experiments/duck_harness_repro/dead_action_ledger.py \
  artifacts/kaggle/duck_full_eval_ft09_overlap/latest \
  --output experiments/duck_harness_repro/dead_action_ledger_full_eval.json
```
