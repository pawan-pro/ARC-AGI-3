# 2026-05-10 EXP-004 100k long-horizon result analysis

## Purpose

Analyze the `EXP-004_long_horizon_discovery` run with `MAX_MOVES = 100000` per environment.

This is a discovery / data-generation result, not a submission baseline.

## Run setup

```text
EXP_ID = EXP-004
MAX_MOVES = 100000 per environment
Total environments = 25
Total action budget = 2,500,000
SEED = 42
PRIOR_PROB = 0.05
MIN_PRIOR_OBS = 12
No ACTION6 throttle
Base behavior = EXP-003C-style fallback + sparse progress prior
```

## Result

```text
Local score: 0.5105933166837525
Levels completed: 22 / 183
Progress events logged: 22
Environments completed: 0 / 25
Total actions: 2,500,000
```

## Comparison

```text
EXP-003B:       0.4849109618 | 6 / 183  | 25,000 actions | public 0.12
EXP-003C/003F:  0.4819505213 | 7 / 183  | 25,000 actions | public tie 0.12
EXP-003F_5000:  0.5105754966 | 9 / 183  | 125,000 actions
EXP-004_10k:    0.5105769385 | 10 / 183 | 250,000 actions
EXP-004_100k:   0.5105933167 | 22 / 183 | 2,500,000 actions
```

The 100k run discovers many more levels but produces almost no raw score gain over the 10k run. This confirms severe action-efficiency decay.

## Efficiency view

Approximate levels per 1,000 actions:

```text
EXP-003C/003F 1000-move: 7 / 25    = 0.280 levels per 1k actions
EXP-003F_5000:            9 / 125   = 0.072 levels per 1k actions
EXP-004_10k:             10 / 250   = 0.040 levels per 1k actions
EXP-004_100k:            22 / 2500  = 0.0088 levels per 1k actions
```

K-12 version: the robot found more treasures when it played much longer, but it took so many extra steps that the scoreboard barely rewarded it.

## Global action counts

```text
ACTION1: 305,138
ACTION2: 303,194
ACTION3: 326,798
ACTION4: 329,396
ACTION5: 170,986
ACTION6: 867,651
ACTION7: 167,640
RESET: 29,197
```

## Global policy counts

```text
fallback: 2,450,106
progress_prior_guardrailed: 20,697
reset: 29,197
```

ACTION6 remains overwhelmingly fallback-driven:

```text
fallback ACTION6: 867,613
prior ACTION6: 38
```

## Progress events discovered

```text
sk48-d8078629  | step 44,785 | 0 -> 1 | ACTION4
tn36-ef4dde99  | step 39     | 0 -> 1 | ACTION6
m0r0-492f87ba  | step 449    | 0 -> 1 | ACTION3
cn04-2fe56bfb  | step 28,315 | 0 -> 1 | ACTION4
lp85-305b61c3  | step 320    | 0 -> 1 | ACTION6
lp85-305b61c3  | step 30,743 | 1 -> 2 | ACTION6
lp85-305b61c3  | step 49,427 | 2 -> 3 | ACTION6
lp85-305b61c3  | step 80,557 | 3 -> 4 | ACTION6
lp85-305b61c3  | step 92,910 | 4 -> 5 | ACTION6
ka59-38d34dbb  | step 96,909 | 0 -> 1 | ACTION3
vc33-5430563c  | step 74     | 0 -> 1 | ACTION6
vc33-5430563c  | step 27,451 | 1 -> 2 | ACTION6
r11l-495a7899  | step 15     | 0 -> 1 | ACTION6
sp80-589a99af  | step 349    | 0 -> 1 | ACTION5
sp80-589a99af  | step 22,259 | 1 -> 2 | ACTION5
ar25-0c556536  | step 8,883  | 0 -> 1 | ACTION3
ar25-0c556536  | step 97,591 | 1 -> 2 | ACTION2
cd82-fb555c5d  | step 44     | 0 -> 1 | ACTION5
cd82-fb555c5d  | step 1,796  | 1 -> 2 | ACTION5
s5i5-18d95033  | step 23,041 | 0 -> 1 | ACTION6
ft09-0d8bbf25  | step 2,779  | 0 -> 1 | ACTION6
tr87-cd924810  | step 10,039 | 0 -> 1 | ACTION2
```

## Progress-action summary

```text
ACTION6: 10 progress events
ACTION5: 4 progress events
ACTION3: 3 progress events
ACTION4: 2 progress events
ACTION2: 2 progress events
```

## Key discovery patterns

### 1. ACTION6 repeated-click games

Strong ACTION6 progress games:

```text
tn36
lp85
vc33
r11l
s5i5
ft09
```

The most important finding is `lp85`, which reached 5 levels through repeated ACTION6 over the long horizon. This suggests that in some games ACTION6 is not merely a risky click; it is the core level-progress mechanism.

Policy implication:

```text
Build a bounded ACTION6 coordinate-search policy for ACTION6-only / ACTION6-dominant games.
```

### 2. ACTION5 replay games

ACTION5 produced repeated progress in:

```text
cd82: 0 -> 1 and 1 -> 2
sp80: 0 -> 1 and 1 -> 2
```

Policy implication:

```text
If ACTION5 produces a level_delta, replay/probe ACTION5 again for a short budget after the level transition.
```

### 3. ACTION3 / ACTION2 mixed-action games

ACTION3 and ACTION2 produced late progress in mixed-action games:

```text
m0r0: ACTION3
ar25: ACTION3 then ACTION2
ka59: ACTION3
tr87: ACTION2
```

Policy implication:

```text
Reserve bounded probe budgets for ACTION3/ACTION2 in mixed keyboard-like games.
```

### 4. Very late discoveries matter but are inefficient

Several discoveries occurred only after large budgets:

```text
sk48 ACTION4 at step 44,785
cn04 ACTION4 at step 28,315
ka59 ACTION3 at step 96,909
ar25 ACTION2 at step 97,591
```

These are useful for learning patterns, but not directly usable at 25k unless compressed.

## Decision

```text
Do not submit EXP-004_100k.
Do not treat it as a new baseline.
Use it as discovery data for EXP-004B.
```

## Missing artifact note

This review is based on the pasted run log. For full reproducible analysis, attach the 100k `exp004_artifacts` bundle:

```text
exp004_scorecard_summary.json
exp004_scorecard_by_environment.csv
exp004_run_results.csv
exp004_progress_events.csv
exp004_progress_windows.json
exp004_progress_action_summary.csv
exp004_action_diagnostics_by_game.csv
exp004_action_counts.json
exp004_policy_counts.json
exp004_policy_action_counts.json
artifact_manifest.csv
```

## Recommended next experiment

```text
EXP-004B_progress_replay_prior
```

Goal:

```text
Compress long-horizon discoveries into a 25k-action policy.
```

Candidate modules:

1. Bounded ACTION6 coordinate search for ACTION6-dominant games.
2. ACTION5 post-progress replay for `cd82` and `sp80` style games.
3. ACTION3/ACTION2 probe budgets for mixed-action games.
4. Strict budget caps and fallback to stochastic baseline.

## Gate for EXP-004B

EXP-004B should be evaluated under the normal 25k-action local budget.

Success target:

```text
Beat 7 / 183 levels under 25k actions, or beat EXP-003B local score 0.4849109618.
```

Public submission only if the 25k local result is clearly competitive and artifacts are attached.
