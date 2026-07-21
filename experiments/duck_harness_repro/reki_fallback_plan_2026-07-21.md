# EXP-DUCK-011: Fallback-Only Reki Saliency

Date: 2026-07-21

## Why this differs from EXP-DUCK-010

EXP-DUCK-010 tested whether structural memory should veto ordinary Duck actions. That is unsafe because Duck may intentionally click several similar objects.

The linked Reki notebook uses dead signatures inside a larger exploration system. EXP-DUCK-011 therefore changes the boundary:

- the LLM keeps every action it requests;
- structural memory may influence only a separate fallback;
- the fallback starts only after the existing 90-action no-level-progress threshold;
- every fallback action is tagged in the event log;
- the fallback is limited to 24 clicks per level.

## Target Games

```text
sc25-635fd71a
tn36-ef4dde99
```

`sc25` contains repeated inert clicks. `tn36` is the safety case because one stored run solved a level through a long intentional click sequence.

## Fallback Logic

1. Segment the current grid into non-background, same-color connected components.
2. Rank components using Reki's small-object and rare-color saliency score.
3. Skip an exact coordinate that already failed on the same visible state.
4. Mark a structural class dead after two no-effect observations.
5. Permanently protect a class for the current level once any click on it changes the board or advances the level.
6. Reset structural memory after a level transition.

The structural signature is:

```text
(color, pixel count, rectangle flag, number of twins)
```

## K-12 Explanation

Duck remains the student solving the puzzle. The fallback is a small emergency tray of buttons to try only after the student has been stuck for a long time.

The tray puts small, unusual-looking buttons first. If two buttons of one type do absolutely nothing, it moves that type to the back of the tray. It never grabs the pencil away from the student and never rejects the student's own answer.

## Success Gate

- The notebook runs only the two named games.
- Fallback actions appear as `fallback_policy=reki_saliency_deadsig` in event logs.
- No LLM-requested action is vetoed.
- A known `tn36` level completion is preserved if the LLM reaches it before fallback.
- Promotion requires level progress or a clearly reusable mechanic trace, not merely changed pixels.

## Runtime

The earlier four-game controlled-stall benchmark took about 42 minutes. This two-game run should be checked after approximately 45-60 minutes because model startup and the slowest concurrent game dominate elapsed time.

## Launch

- Version: `1`
- Launched: `2026-07-21 16:26 IST`
- Status after upload: `KernelWorkerStatus.RUNNING`
- Kernel: `jatalepawan/arc-agi-3-duck-fallback-only-reki-saliency`
- URL: <https://www.kaggle.com/code/jatalepawan/arc-agi-3-duck-fallback-only-reki-saliency>
- First useful check window: approximately `17:11-17:26 IST`

## Commands

```bash
python experiments/duck_harness_repro/build_reki_fallback_notebook.py
python scripts/kaggle_kernel_run.py --variant reki-fallback info
python scripts/kaggle_kernel_run.py --variant reki-fallback push
python scripts/kaggle_kernel_run.py --variant reki-fallback status
python scripts/kaggle_kernel_run.py --variant reki-fallback output
python scripts/kaggle_kernel_run.py --variant reki-fallback summarize
```
