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

## Scoring / task-coverage clarification

Kaggle competition scoring is not a random single-task assignment. The agent is evaluated across all available competition environments. Locally, the public demo set contains 25 task IDs; the hidden/public leaderboard set is aggregated similarly through the competition runner.

Implication: do not hard-code only ls20. Use ls20 as one observed example of a broader family: movement + objects + affordances + goal/reference matching.

## Useful evidence from ls20 visual inspection

The public demo for task ls20 shows a maze-like game where the blue/orange player can move through corridors and interact with multiple element types. A human can solve this by planning movement paths and understanding object roles, not by random clicking.

User-observed ls20 level mechanics:

- The blue/orange block is the controllable player.
- Up/down/left/right actions move the player.
- The black/blue block is the goal block.
- The goal condition depends on matching the goal block orientation to the orientation shown in the bottom-left reference icon.
- The gray plus sign changes the orientation of the goal block when touched by the player.
- Yellow blocks increase remaining time/energy, shown by the yellow bar, and disappear after being consumed.

Implication for EXP-002: random visible pixels are not enough. We need element discovery, affordance testing, state tracking, and a simple planner.

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

## EXP-002 updated hypothesis

A small heuristic explorer should beat EXP-001 if it first learns the role of visible elements, then plans toward the goal.

The high-level loop should be:

1. Parse frame into objects.
2. Identify controllable player by testing directional actions.
3. Identify consumables by touching small objects and watching whether a resource bar increases.
4. Identify state-changing objects by touching them and watching whether another object changes orientation/color/shape.
5. Identify goal/reference relationship by comparing target-like object to UI/reference icon.
6. Optimize path: collect useful resource/time blocks only when beneficial, then trigger orientation-changing object as needed, then enter the goal.

## EXP-002 first implementation scope

Do not try to fully solve ls20 immediately. First implement generic mechanics that can help multiple games:

1. Object parser: connected components by color, excluding background and huge static regions.
2. Player detector: object/blob whose centroid moves after ACTION1/ACTION2/ACTION3/ACTION4.
3. No-op detector: suppress moves that do not change the frame or player position.
4. Target candidates: small non-background blobs, plus unusual UI-like or goal-like objects.
5. Short-horizon greedy planner: move toward nearest useful candidate with directional actions.
6. Affordance log: record whether touching each candidate caused level progress, frame change, score proxy, resource-bar increase, or object disappearance.

## Profiler-first decision

Before submitting a new heuristic agent, create and run a profiler notebook over all 25 public demo tasks.

Profiler notebook created:

- notebooks/02_analysis/exp002_task_profiler_and_replay_analysis.ipynb

Purpose:

- list games, titles, tags, and action spaces,
- save initial frame color histograms,
- save connected components and candidate objects,
- run one-step probes for simple actions,
- click candidate object centers where ACTION6 is available,
- infer coarse task families and hints,
- save CSV/JSON artifacts for later EXP-002 agent design.

Expected profiler artifacts:

- /kaggle/working/exp002_profiler_artifacts/game_metadata.csv
- /kaggle/working/exp002_profiler_artifacts/action_space_by_game.csv
- /kaggle/working/exp002_profiler_artifacts/initial_frame_color_histograms.csv
- /kaggle/working/exp002_profiler_artifacts/initial_connected_components.csv
- /kaggle/working/exp002_profiler_artifacts/initial_target_candidates.csv
- /kaggle/working/exp002_profiler_artifacts/probe_action_effects.csv
- /kaggle/working/exp002_profiler_artifacts/task_family_summary.csv
- /kaggle/working/exp002_profiler_artifacts/profiler_summary.json
- /kaggle/working/exp002_profiler_artifacts/artifact_manifest.csv

## EXP-002 proposed files

- notebooks/02_analysis/exp002_task_profiler_and_replay_analysis.ipynb
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

1. Run notebooks/02_analysis/exp002_task_profiler_and_replay_analysis.ipynb in Kaggle with internet disabled and ARC-AGI-3 competition data attached.
2. Download/share profiler artifacts.
3. Analyze task families and probe effects.
4. Use findings to finish/adjust notebooks/01_exploration/exp002_visible_object_heuristic_explorer.ipynb.
5. Run local validation and compare with EXP-001.

## Research note

This is the transition from random exploration to adaptive game understanding. The key research artifact is not just score, but a replay/log showing the agent identifies elements, tests them, and updates object roles from observed effects.
