# 2026-05-10 EXP-004 long-horizon result analysis

## Purpose

Analyze the first `EXP-004_long_horizon_discovery` run and extract button/action logic that can inform a compressed follow-up policy.

## Run setup

```text
EXP_ID = EXP-004
MAX_MOVES = 10000 per environment
Total actions = 250000
SEED = 42
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
No ACTION6 throttle
Base behavior = EXP-003C-style fallback + sparse progress prior
```

## Result

```text
Local score: 0.5105769384937995
Levels completed: 10 / 183
Progress events logged: 10
Environments completed: 0 / 25
Actions: 250000
```

This is the best local raw level count so far, but it uses 10x the standard 25k-action budget.

## Comparison

```text
EXP-003B:       0.4849109618 | 6 / 183  | 25,000 actions | public 0.12
EXP-003C/003F:  0.4819505213 | 7 / 183  | 25,000 actions | public tie 0.12
EXP-003F_5000:  0.5105754966 | 9 / 183  | 125,000 actions
EXP-004:        0.5105769385 | 10 / 183 | 250,000 actions
```

EXP-004 improved level count versus EXP-003F_5000 but produced almost no raw score gain, confirming that the extra level came at high action cost.

## Global action / policy counts

Action counts:

```text
ACTION1: 30,702
ACTION2: 30,020
ACTION3: 31,956
ACTION4: 33,515
ACTION5: 17,166
ACTION6: 86,814
ACTION7: 16,727
RESET: 3,100
```

Policy counts:

```text
fallback: 244,182
progress_prior_guardrailed: 2,718
reset: 3,100
```

Policy-action counts show ACTION6 remains overwhelmingly fallback-driven:

```text
fallback ACTION6: 86,776
prior ACTION6: 38
```

## Progress events discovered

```text
tn36-ef4dde99 | step 39   | 0 -> 1 | ACTION6 | click {x=38, y=53}
m0r0-492f87ba | step 449  | 0 -> 1 | ACTION3
lp85-305b61c3 | step 320  | 0 -> 1 | ACTION6 | click {x=4, y=33}
vc33-5430563c | step 74   | 0 -> 1 | ACTION6 | click {x=60, y=33}
r11l-495a7899 | step 15   | 0 -> 1 | ACTION6 | click {x=42, y=22}
sp80-589a99af | step 349  | 0 -> 1 | ACTION5
ar25-0c556536 | step 8883 | 0 -> 1 | ACTION3
cd82-fb555c5d | step 44   | 0 -> 1 | ACTION5
cd82-fb555c5d | step 1796 | 1 -> 2 | ACTION5
ft09-0d8bbf25 | step 2779 | 0 -> 1 | ACTION6 | click {x=38, y=56}
```

Progress-action summary:

```text
ACTION6: 5 events / 5 levels
ACTION5: 3 events / 3 levels
ACTION3: 2 events / 2 levels
```

## Button / action logic findings

### 1. Pure or near-pure ACTION6 click games

The following games show strong evidence that repeated ACTION6 click exploration is the progress mechanism:

```text
tn36-ef4dde99
lp85-305b61c3
vc33-5430563c
r11l-495a7899
ft09-0d8bbf25
```

In these games, the last 10 actions before progress were all ACTION6. For tn36, lp85, vc33, r11l, and ft09, the progress action was ACTION6 with a specific click coordinate.

Candidate rule:

```text
If the action space is ACTION6-only or ACTION6-dominant and ACTION6 is not no-op, run a bounded ACTION6 coordinate-search policy before reverting to random.
```

Important: coordinate choice matters. The immediate progress coordinates were:

```text
tn36: (38, 53)
lp85: (4, 33)
vc33: (60, 33)
r11l: (42, 22)
ft09: (38, 56)
```

This suggests a future policy should test structured coordinate scans, not only repeat ACTION6 randomly.

### 2. ACTION5 progress games

ACTION5 caused three progress events:

```text
sp80-589a99af: ACTION5 at step 349
cd82-fb555c5d: ACTION5 at step 44
cd82-fb555c5d: ACTION5 at step 1796
```

For `cd82`, ACTION5 is especially strong because it caused both level 0 -> 1 and 1 -> 2.

Candidate rule:

```text
For cd82-like mixed-action games, if ACTION5 produces level progress, temporarily bias ACTION5 again after reset/level change.
```

### 3. ACTION3 progress games

ACTION3 caused two progress events:

```text
m0r0-492f87ba: ACTION3 at step 449
ar25-0c556536: ACTION3 at step 8883
```

`ar25` is especially important because it took 8883 steps and 91 resets before progress. It is a long-tail discovery case.

Candidate rule:

```text
For games with mixed keyboard-like actions where ACTION3 has low no-op and occasional progress, reserve budget for repeated ACTION3 probes instead of relying entirely on random fallback.
```

## Efficiency warning

EXP-004 reached 10 levels, but at 250k actions.

Approximate levels per 1,000 actions:

```text
EXP-003C/003F 1000-move: 7 / 25 = 0.28 levels per 1k actions
EXP-003F_5000: 9 / 125 = 0.072 levels per 1k actions
EXP-004: 10 / 250 = 0.04 levels per 1k actions
```

So EXP-004 is valuable for discovery, not for direct submission.

## Policy implications for EXP-004B

Recommended next policy experiment:

```text
EXP-004B_progress_replay_prior
```

Use progress windows to compress long-run discoveries into a shorter policy.

Candidate modules:

1. `ACTION6_coordinate_search_policy`
   - apply only in ACTION6-only or ACTION6-dominant games;
   - scan/click structured coordinate candidates;
   - cap budget tightly.

2. `progress_action_replay_policy`
   - if ACTION5 or ACTION3 caused progress in the current game, replay that action pattern for a short budget after level transitions.

3. `post_level_progress_reprobe`
   - after a `level_delta`, bias the same progress action for a limited number of steps, especially for `cd82` where ACTION5 produced two levels.

4. `discovery_to_compression_gate`
   - all replay policies must be bounded and fallback-safe;
   - target 25k-action local score/levels, not 250k-action raw score.

## Do not do next

Do not submit EXP-004 directly. Do not treat EXP-004 as a new baseline. Do not add another blind ACTION6 throttle.

## Next step

Implement a compact analysis/replay plan:

```text
EXP-004B_progress_replay_prior
```

Initial target:

```text
Improve 25k-action level count above 7 without increasing action budget.
```
