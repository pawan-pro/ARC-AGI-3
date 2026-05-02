# 2026-05-02 ARC-AGI-3 session — EXP-002 planning, profiling, ablations, and strategy

## Objective

Start from the validated EXP-001 Kaggle result and design the next path toward a medal-level ARC-AGI-3 agent. The session began with a goal of improving the EXP-001 baseline and ended with a clearer experimental roadmap: preserve EXP-001 as the current public baseline, submit EXP-002C as a controlled seed-schedule test, and move next toward genuine affordance-memory and planning.

## K-12 summary

Yesterday's robot learned to touch things it could see. Today we learned that making the robot too careful made it worse. We also learned that different random seeds behave very differently. The best short-term trick was to keep the same simple robot but use a slightly different random seed for two public games.

The deeper goal is still not random luck. The real next robot should learn:

- what it controls,
- what objects do,
- what helps or hurts,
- where the goal might be,
- and how to make a short plan.

## Current validated state

- EXP-000 public score: 0.07
- EXP-001 public score: 0.11
- EXP-001 notebook: notebook338b6b3c9c, Version 2, Succeeded
- EXP-001 local score: 0.21238458620043624
- EXP-001 local levels: 7 / 183
- EXP-001 remains the best confirmed Kaggle/public baseline until EXP-002C score returns.

## EXP-001 interpretation

EXP-001 improved the public score from 0.07 to 0.11. This validated that visible-pixel random clicking is better than pure random action selection, but the policy remains weak and action-inefficient.

The local-to-public gap is material:

- local score: 0.2124
- public score: 0.11

Therefore, local validation is directional only. Public Kaggle submissions remain the source of truth for real competition progress.

## Scoring / task-coverage clarification

A key clarification from the ARC-AGI Toolkit and competition documentation was that scoring is not based on one random assigned task. The agent is evaluated across all available competition environments. Locally, the public demo set contains 25 task IDs; in Kaggle competition mode, the submission is scored across the available evaluation environments through the competition runner.

Implication:

- do not build only an ls20 solver;
- use ls20 as one example of a broader game family;
- build reusable skills: movement detection, object parsing, affordance learning, goal inference, and planning.

## Public task-family profiling

We created and ran:

- notebooks/02_analysis/exp002_task_profiler_and_replay_analysis.ipynb

Profiler outputs showed:

- total games: 25
- probe rows: 184
- coarse family counts:
  - keyboard_click: 11
  - click: 8
  - keyboard: 6
- movement-responsive games: 15
- click-responsive games: 13
- one-step-progress games: 0

Interpretation:

No public game was solved by one obvious action. The agent needs multi-step interaction and memory. The correct policy class is not one fixed random action distribution; it should route by game family and eventually learn object effects.

## Useful evidence from ls20 visual inspection

The public demo for task ls20 shows a maze-like game where the blue/orange player can move through corridors and interact with multiple element types. A human can solve this by planning movement paths and understanding object roles, not by random clicking.

User-observed ls20 mechanics:

- The blue/orange block is the controllable player.
- Up/down/left/right actions move the player.
- The black/blue block is the goal block.
- The goal condition depends on matching the goal block orientation to the orientation shown in the bottom-left reference icon.
- The gray plus sign changes the orientation of the goal block when touched by the player.
- Yellow blocks increase remaining time/energy, shown by the yellow bar, and disappear after being consumed.

Insight:

Yellow blocks are not the final goal. They are resource/time pickups discovered by effect: touching them made them disappear and increased the yellow bar. This is the kind of affordance learning the agent must eventually perform.

## Engine/action knowledge

Known action conventions from ARCEngine documentation:

- ACTION1 = up
- ACTION2 = down
- ACTION3 = left
- ACTION4 = right
- ACTION5 = spacebar
- ACTION6 = click with x,y coordinates
- ACTION7 = undo

This means future agents should stop treating all actions as opaque random labels. At minimum, movement actions should be directional and ACTION7 should be treated carefully. However, the no-undo ablation showed that simply removing ACTION7 changed stochastic behavior and hurt local score badly.

## EXP-002 hypothesis and result

Initial EXP-002 hypothesis:

A small heuristic explorer should beat EXP-001 if it first learns visible structure and avoids waste.

Implemented EXP-002 features:

- task-family routing,
- connected-component object detection,
- object-center click policy,
- directional movement toward candidate objects,
- no-op suppression,
- ACTION7 avoidance,
- EXP-001-style fallback.

Result:

- EXP-002 local score: 0.14996300324361506
- levels: 5 / 183
- actions: 25,000
- status: failed local gate / not submitted

Interpretation:

Conceptually useful but too restrictive. It harmed random discovery. This confirmed that we should not combine many heuristic changes at once.

## EXP-002A no-undo ablation

Purpose:

Test the smallest possible change: keep EXP-001 visible-pixel random behavior but remove ACTION7 / undo.

Result:

- EXP-002A local score: 0.03613655104588648
- levels: 6 / 183
- actions: 25,000
- status: failed local gate / not submitted

Interpretation:

Removing ACTION7 looked safe but strongly regressed score. The action sequence and random exploration dynamics are fragile. This result also suggests that even apparently bad actions may occasionally help or alter trajectories in ways that matter.

## EXP-002B seed sweep

Purpose:

Before adding more heuristics, measure stochastic variance under the exact EXP-001 policy.

Notebook:

- notebooks/02_analysis/exp002b_exp001_seed_sweep.ipynb

Seeds tested:

- 0, 1, 2, 3, 4, 5, 10, 42, 100, 123

Printed results:

- seed 42: score 0.21238458620043624, levels 7 / 183
- seed 10: score 0.20182443586033266, levels 6 / 183
- seed 1: score 0.1893783602920196, levels 4 / 183
- many seeds were near zero

Conclusion:

Seed 42 remains the best sampled global seed, but random exploration has high variance. The strongest local performance is fragile and seed-dependent.

Implementation note:

The original seed sweep notebook errored during final artifact export due to a pandas query issue. The notebook was fixed in commit:

- 2349d5cb11e19df2fbaa34193337bac81f511fed
- analysis: fix EXP-002B best seed export

## EXP-002C per-game seed schedule

Purpose:

Keep the EXP-001 policy unchanged but use a per-game seed schedule for public demo tasks where another seed completed an extra level.

Notebook:

- notebooks/01_exploration/exp002c_per_game_seed_schedule.ipynb

Seed schedule:

- default seed: 42
- vc33 -> seed 10
- r11l -> seed 10
- all other games -> seed 42

Local result:

- EXP-002C local score: 0.21261630408032173
- levels: 9 / 183
- actions: 25,000
- seed usage: seed 42 for 23 games, seed 10 for 2 games
- submission.parquet created: yes

Interpretation:

EXP-002C passed the local validation gate by a very small score margin and improved level count from 7 to 9. It was submitted for Kaggle scoring and the result is pending.

Important caution:

This may overfit public demo game IDs. If the public/hidden Kaggle tasks do not include those exact game prefixes or behave differently, the improvement may not generalize. Treat the submission as a controlled public-overfit test, not as durable intelligence progress.

## What worked today

- The task profiler established the 25 public tasks split into keyboard_click, click, and keyboard families.
- We clarified that scoring is across all available environments, not one random task.
- The ls20 manual analysis produced a concrete affordance-learning example: yellow as time/resource, plus as orientation switch, black/blue block as goal, bottom-left as reference icon.
- EXP-002 and EXP-002A failed locally, which prevented bad submissions.
- EXP-002B showed that seed variance is large and seed 42 remains strong.
- EXP-002C produced a local improvement and was submitted for public scoring.
- The experiment tracker was updated after each meaningful result.

## What failed / what we learned

- Broad heuristics hurt performance when added all at once.
- Removing ACTION7 / undo hurt performance badly.
- Object-center targeting and no-op suppression are not automatically beneficial without better state understanding.
- EXP-001's local score is highly stochastic and fragile.
- Local improvements can be public-demo overfit and must be treated carefully.

## Current best result

Confirmed public baseline:

- EXP-001 public score: 0.11

Best local result:

- EXP-002C local score: 0.21261630408032173
- EXP-002C local levels: 9 / 183

Pending:

- EXP-002C Kaggle public score

## Files created / changed today

Analysis / profiler:

- notebooks/02_analysis/exp002_task_profiler_and_replay_analysis.ipynb
- experiments/EXP-002_visible_object_heuristic_explorer/profiler_results_2026-05-02.md

Heuristic scoring attempt:

- experiments/EXP-002_visible_object_heuristic_explorer/README.md
- notebooks/01_exploration/exp002_visible_object_heuristic_explorer.ipynb

Ablations:

- experiments/EXP-002A_exp001_no_undo_ablation/README.md
- notebooks/01_exploration/exp002a_exp001_no_undo_ablation.ipynb
- experiments/EXP-002B_exp001_seed_sweep/README.md
- notebooks/02_analysis/exp002b_exp001_seed_sweep.ipynb
- experiments/EXP-002C_per_game_seed_schedule/README.md
- notebooks/01_exploration/exp002c_per_game_seed_schedule.ipynb

Trackers / notes:

- docs/experiment_tracker.md
- session_notes/2026-05-02_arc_agi3_exp002_planning.md

## Commit highlights from today

- d703c9967ea132e5e9d496d80686fce882088ce6 — analysis: add EXP-002 task profiler notebook
- adf3da47db056d76cc1d7a9c56e665ec0e6cd48e — session notes: add EXP-002 profiler notebook plan
- c1bf121c2da06b93876467ec940866d7913ced6e — experiments: add EXP-002 routed heuristic scoring notebook
- 50651ec85f9cfad9a394880d28eb1b3156928131 — experiments: record EXP-002 local regression
- 3d3c8579ccc12823a74698483aff726032031d97 — experiments: add EXP-002A no-undo ablation notebook
- 72d1572dce2cf420908ba51788da4dc3586d42bb — experiments: record EXP-002A no-undo regression
- 38e237345578a279d8ee18b1eb154de989ba6b9f — analysis: add EXP-002B EXP-001 seed sweep notebook
- 2349d5cb11e19df2fbaa34193337bac81f511fed — analysis: fix EXP-002B best seed export
- 828bf6644b0e6c2c224eb267609563d3f0c7856d — experiments: add EXP-002C per-game seed schedule notebook
- c9ac40ebc80b63d608751f9f7cc51d8d87febf93 — experiments: record EXP-002B seed sweep and EXP-002C local pass

## Overall medal/top-position strategy

The path to a medal should not be pure random search, pure LLM, or immediate reinforcement learning. The strongest path is likely a hybrid stack:

1. Clean baselines and reproducible scoring notebooks.
2. Profiling and replay analysis for all public tasks.
3. Object parsing from frames.
4. Action-effect memory: what changed after each interaction.
5. Affordance learning: consumable, switch, obstacle, goal-like, reference-like.
6. Short-horizon planning: move/click toward useful objects and avoid no-ops.
7. Symbolic planning for games with explicit conditions, like orientation/reference matching in ls20.
8. Search over action plans where local simulation allows it: BFS, A*, beam search, MCTS-like rollouts.
9. Replay mining and offline imitation/action-prior learning.
10. Later, possibly RL or offline packaged VLM/LLM assistance, but only after strong logs and object abstractions exist.

Near-term target:

- Beat public score 0.11 with a reproducible agent.

Medium-term target:

- Build EXP-003 affordance-memory explorer that improves behavior across task families without public game-id overfit.

Long-term medal bet:

- Combine object/affordance memory, symbolic planning, and replay-mined action priors into a robust adaptive agent. The paper-track narrative should emphasize transition from stochastic interaction to self-supervised game-rule discovery.

## Next session plan

1. Ingest EXP-002C Kaggle public score when available.
2. If EXP-002C public score > 0.11:
   - mark EXP-002C as temporary public baseline,
   - note overfit risk,
   - proceed to EXP-003 affordance-memory explorer.
3. If EXP-002C public score <= 0.11:
   - keep EXP-001 as official public baseline,
   - treat EXP-002C as local/public-demo overfit evidence,
   - proceed to EXP-003 anyway, focused on generalization.
4. Start EXP-003 with one narrowly scoped improvement:
   - record object/action/effect memory,
   - classify object disappearance and bar/resource changes,
   - preserve EXP-001 fallback behavior.
5. Avoid broad heuristic combinations until each component passes ablation testing.

## Fallback plan

If EXP-003 underperforms locally:

- revert to EXP-001 as stable baseline,
- keep EXP-002C only as local overfit/seed-sensitivity evidence,
- run one ablation at a time:
  - click-only candidate cycling,
  - keyboard-only no-op memory,
  - keyboard-click movement/click ratio,
  - per-tag seed schedule rather than per-game seed schedule.
