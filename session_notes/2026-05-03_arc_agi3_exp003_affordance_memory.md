# 2026-05-03 ARC-AGI-3 session — EXP-003 affordance memory, logging scaffold, and progress-prior candidate

## Objective

Begin the next durable generalization stage after EXP-002C failed to improve the public leaderboard. The goal was to move beyond seed luck and public-demo overfit toward agents that learn from their own interactions: action effects, object effects, no-ops, game-over risk, and progress signals.

## K-12 summary

Yesterday we found that lucky random seeds can help on practice games but do not necessarily help on the real scoreboard. Today we started teaching the robot to keep notes while it plays.

The first attempt made the robot too eager to click things that changed the picture, so it got worse. Then we made the robot only write notes while playing normally, and it matched the baseline exactly. Finally, we gave the robot a very small action preference based on real progress signals. That produced the best local score so far, but it has now been submitted and we are waiting for the Kaggle result.

## Starting state

Confirmed public baseline before this session:

- EXP-001 public score: `0.11`
- EXP-001 local score: `0.21238458620043624`
- EXP-001 local levels: `7 / 183`

Yesterday's EXP-002C result:

- EXP-002C local score: `0.21261630408032173`
- EXP-002C local levels: `9 / 183`
- EXP-002C public score: `0.11`

Interpretation: EXP-002C improved local practice games but not the Kaggle public score. It was likely public-demo/game-id seed overfit. EXP-001 remains the current confirmed public baseline.

## Key strategic shift

The session moved from:

```text
seed tricks / public-demo tuning
```

toward:

```text
safe logging -> progress-aware priors -> affordance learning -> goal inference -> planning
```

The core lesson is that local scoring is useful for filtering bad ideas, but Kaggle public scoring is the only validation source for real competition progress.

## EXP-003 — affordance-memory explorer

Created and ran:

- `experiments/EXP-003_affordance_memory_explorer/README.md`
- `notebooks/01_exploration/exp003_affordance_memory_explorer.ipynb`

Design:

- Keep EXP-001 fallback as main behavior.
- Add `15%` memory-biased object/component clicks.
- Record object/action/effect memory.
- Track frame change, diff pixels, level delta, state changes, no-ops, policy counts, and action counts.

Local result:

- score: `0.0644204640`
- levels: `7 / 183`
- actions: `25,000`
- memory bias probability: `0.15`

Status:

- Failed local gate.
- Not submitted.

Interpretation:

EXP-003 preserved the number of completed levels but sharply reduced score. The memory policy incorrectly treated frame changes as useful progress. It clicked too many objects that changed pixels but did not advance levels.

Main lesson:

```text
frame change != useful progress
```

Progress signals must be ranked more carefully:

1. `level_delta > 0`
2. `WIN` / positive state change
3. avoiding `GAME_OVER`
4. no-op avoidance
5. frame change only as weak evidence

## EXP-003A — affordance log-only ablation

Created and ran:

- `experiments/EXP-003A_affordance_log_only/README.md`
- `notebooks/01_exploration/exp003a_affordance_log_only.ipynb`

Design:

- Keep EXP-001 policy exactly unchanged.
- Add logging only.
- No memory-biased actions.
- No object-center override.
- No no-op suppression.
- ACTION7 kept, same as EXP-001.

Local result:

- score: `0.21238458620043624`
- levels: `7 / 183`
- actions: `25,000`

Status:

- Passed diagnostic gate.
- Not submitted because it is policy-equivalent to EXP-001.

Interpretation:

EXP-003A reproduced EXP-001 exactly while generating logs. This proves the instrumentation is policy-neutral and safe. The failure in EXP-003 came from using weak memory as policy guidance, not from logging itself.

Important artifact insight:

- EXP-003A action distribution matched EXP-001-style balanced random exploration.
- Logging can now be used as a research scaffold.

## EXP-003B — progress-weighted action prior

Created and ran:

- `experiments/EXP-003B_progress_weighted_action_prior/README.md`
- `notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb`

Design:

- Keep EXP-001 random visible-pixel fallback as default.
- Use only `10%` online progress-weighted action prior.
- No public game-id hard-coding.
- No per-game seed schedule.
- No object/component targeting.
- Utility prioritizes real progress:
  - level delta / WIN: strong positive
  - GAME_OVER: strong negative
  - no-op: negative
  - frame change: weak positive only

Local result:

- score: `0.48491096178440257`
- levels: `6 / 183`
- actions: `25,000`
- prior probability: `0.10`
- min prior observations: `8`
- fallback actions: `23,294`
- progress-prior actions: `1,411`
- resets: `295`

Status:

- Strongest local score so far.
- Submitted to Kaggle for scoring.
- Awaiting public score.

Important interpretation:

EXP-003B completed fewer levels than EXP-001 (`6` vs `7`) but more than doubled local score (`0.4849` vs `0.2124`). This suggests ARC-AGI-3 scoring is sensitive to action efficiency, level weighting, and the quality of completed progress, not just raw level count.

K-12 version:

```text
The robot finished fewer rooms, but it finished the important rooms better, so the practice scoreboard gave it more points.
```

Caution:

This must be validated by Kaggle. Local score can still be misleading. EXP-003B is a strong local candidate, not yet a confirmed public baseline.

## EXP-003B action distribution

EXP-003B changed the action distribution substantially compared with EXP-003A / EXP-001:

- ACTION1: `3,140`
- ACTION2: `3,022`
- ACTION3: `3,247`
- ACTION4: `3,356`
- ACTION5: `1,700`
- ACTION6: `8,613`
- ACTION7: `1,627`
- RESET: `295`

This shows the online prior shifted behavior strongly toward `ACTION6` while still preserving mostly random fallback behavior.

## What worked today

- EXP-003A validated a safe logging scaffold.
- EXP-003B produced the strongest local score so far.
- The project now has a clean way to collect effect logs without damaging baseline behavior.
- The experiments clarified that frame-change-only memory is harmful, but progress-weighted priors can be valuable.
- The experiment tracker was updated after each meaningful result.

## What failed / what we learned

- EXP-003 object/component memory failed because it overvalued frame changes.
- A small amount of policy bias can strongly alter the action distribution.
- More levels completed does not always mean higher score.
- Public Kaggle score remains the source of truth.
- We should avoid broad heuristic changes and keep testing one controlled idea at a time.

## Current best result

Confirmed public baseline:

- EXP-001 public score: `0.11`

Best local score:

- EXP-003B local score: `0.48491096178440257`
- EXP-003B local levels: `6 / 183`

Pending:

- EXP-003B Kaggle public score

## Files created / changed today

EXP-003:

- `experiments/EXP-003_affordance_memory_explorer/README.md`
- `notebooks/01_exploration/exp003_affordance_memory_explorer.ipynb`

EXP-003A:

- `experiments/EXP-003A_affordance_log_only/README.md`
- `notebooks/01_exploration/exp003a_affordance_log_only.ipynb`

EXP-003B:

- `experiments/EXP-003B_progress_weighted_action_prior/README.md`
- `notebooks/01_exploration/exp003b_progress_weighted_action_prior.ipynb`

Tracker:

- `docs/experiment_tracker.md`

Session note:

- `session_notes/2026-05-03_arc_agi3_exp003_affordance_memory.md`

## Commit highlights

- `6e11c2c4ed6a20674b1125d5ac48faedb8e1f844` — experiments: add EXP-003 affordance memory README
- `c57befe434975c7649ea2ade383135c2fcf469d0` — experiments: add EXP-003 affordance memory notebook
- `a8f82a2ba969e3871c08225920dd4bda16f08bb1` — experiments: record EXP-003 local regression
- `efa8ef36cf0ec1ad750cd750e44b9fd3330b0198` — experiments: add EXP-003A log-only README
- `da485dd52d008e098f433fd526fb76fbc06e348b` — experiments: add EXP-003A affordance log-only notebook
- `c0c70bbfb30074a55117e9e2d2b2b2a81709da43` — experiments: record EXP-003A log-only reproduction
- `a88b1c85a9aabf8a510dcd93794dbbefef84cf5a` — experiments: add EXP-003B progress-weighted prior README
- `9170626cb828ce67b68b28323e923125ad943aa4` — experiments: add EXP-003B progress-weighted action prior notebook
- `e7e901df385ffadbf0f241aaa7046cf29618648c` — experiments: record EXP-003B strong local score candidate

## Overall medal/top-position strategy update

The most promising path remains hybrid, not pure random, pure RL, or pure LLM.

Near-term stack:

1. Keep EXP-001 as clean public baseline until Kaggle confirms a better notebook.
2. Use EXP-003A-style logging as the safe analysis scaffold.
3. Use EXP-003B-style progress-weighted priors as the first promising online learning layer.
4. Add stricter state-aware rules only after each ablation passes.

Medium-term stack:

1. Action-effect memory.
2. Object-effect memory, but only after progress signals are separated from visual changes.
3. Game-family classifiers from action space and early probes.
4. No-op and GAME_OVER risk modeling.
5. Short-horizon planning based on learned affordances.

Long-term medal bet:

1. Object parsing.
2. Affordance learning.
3. Goal/reference inference, especially for ls20-like games.
4. Symbolic or graph search planning: BFS, A*, beam search, and later MCTS-style rollout selection where feasible.
5. Replay mining to learn action priors by task family.
6. Possibly offline packaged models or LLM/VLM-assisted analysis outside the scoring notebook, but not as the first-line Kaggle runtime agent.

Research narrative:

```text
random visible interaction -> safe logging -> online progress priors -> affordance discovery -> goal inference -> symbolic planning
```

This is a clean paper-track story because each experiment is measurable, reproducible, and explains a failure mode.

## Next session plan

1. Ingest EXP-003B Kaggle public result.
2. If EXP-003B public score > `0.11`:
   - mark EXP-003B as new public baseline,
   - analyze which public/hidden task families likely improved,
   - prepare EXP-003C as a refinement rather than a rewrite.
3. If EXP-003B public score <= `0.11`:
   - keep EXP-001 as public baseline,
   - use EXP-003B as local-overfit/evaluation-mismatch evidence,
   - inspect why local score rose despite fewer levels.
4. Next candidate experiment after result:
   - EXP-003C: stricter progress prior with lower GAME_OVER exposure and reduced repeated ACTION6 loops.
5. Continue to avoid submitting notebooks that fail local validation unless the experiment is deliberately diagnostic.

## Fallback plan

If EXP-003B does not improve Kaggle:

- return to EXP-003A logging scaffold,
- create an offline analyzer that identifies exactly where level deltas occurred,
- design action priors only after actual `level_delta` events, not weak utility,
- test with lower prior probabilities such as `0.03` or `0.05`,
- evaluate per-family rather than per-game hard-coding.
