# 2026-05-09 Long-horizon discovery run plan

## Purpose

Use one very long local run to discover which actions and action sequences lead to actual level progress.

This is not primarily a Kaggle submission candidate. It is a data-generation / discovery experiment.

## K-12 summary

Instead of asking the robot to win efficiently, we let it play for a very long time and watch carefully. When it finally makes progress, we write down what it did right before that progress. Then we can teach the next robot to try those useful patterns earlier.

## Motivation

EXP-003F_5000 showed that increasing `MAX_MOVES` from `1000` to `5000` improved local score and level count:

```text
EXP-003F_1000 score: 0.481950521305291 | levels: 7 / 183 | actions: 25,000
EXP-003F_5000 score: 0.5105754965839018 | levels: 9 / 183 | actions: 125,000
```

This suggests some levels are reachable by longer stochastic exploration. The next research question is:

```text
Which actions, in which games, right before which level_delta events, actually caused progress?
```

## Proposed experiment

Create a long-horizon discovery experiment:

```text
EXP-004_long_horizon_discovery
```

Recommended initial local settings:

```text
MAX_MOVES = 10000 or 20000 per environment
SEED = 42 initially
Base policy = EXP-003C / EXP-003F fallback + sparse prior
No new throttle logic
Do not submit to Kaggle
```

## Key instrumentation requirement

The experiment must log every progress event with enough context to reconstruct what happened.

For every `level_delta > 0`, save:

```text
game_id
step
level_before
level_after
action at progress step
policy at progress step
action data / click coordinate if complex
state_before
state_after
frame_changed
diff_pixels
last 10 actions
last 25 actions
last 50 actions
last 100 actions
number of resets before progress
time/actions since previous level_delta
action counts before progress
policy counts before progress
recent no-op rate
recent game-over rate
```

## Required artifacts

```text
exp004_progress_events.csv
exp004_progress_windows.json
exp004_action_counts.json
exp004_policy_counts.json
exp004_policy_action_counts.json
exp004_scorecard_summary.json
exp004_scorecard_by_environment.csv
exp004_run_results.csv
exp004_run_details.json
exp004_effect_summary_by_game.csv
exp004_action_diagnostics_by_game.csv
artifact_manifest.csv
```

## Analysis targets

After the run, analyze:

1. Which games produced new level deltas beyond the 1000/5000 move runs.
2. Which actions most often appear in the last 10/25/50 steps before level progress.
3. Whether level progress is caused by a single action or by repeated action patterns.
4. Whether ACTION6 is a true causal action or only common because it is sampled often.
5. Whether progress is concentrated in single-action games or mixed-action games.
6. Whether resets are helping or hurting discovery.

## Important warning

Long-horizon runs can overstate progress because they use many more actions.

This experiment should not be treated as a submission baseline unless it is later compressed into a more efficient policy.

## Expected output of the research step

The useful output is not only the score. The useful output is a table like:

```text
game_id | level_delta_step | progress_action | likely_precondition_actions | repeat_pattern | actions_since_start | notes
```

This table can drive a later policy experiment.

## Candidate follow-up

If the long-horizon run identifies repeatable progress windows, create:

```text
EXP-004B_progress_replay_prior
```

Possible policy idea:

```text
If a game resembles a previously observed progress pattern, bias toward the actions that appeared in the pre-progress window, but only for a short budget.
```

## Validation gate

Do not submit the long-horizon discovery run directly unless explicitly intended as a public probe.

Submit only a compressed follow-up if it improves either:

```text
local score at 25k actions
levels at 25k actions
action efficiency
public Kaggle score
```

## Next step

Implement `EXP-004_long_horizon_discovery` as a standalone notebook/source file with progress-event logging before running another policy tweak.
