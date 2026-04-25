# ARC-AGI-3 Baseline Notebook Inspection

Date: 2026-04-25

## Purpose

Inspect the official/sample baseline notebooks and available logs before changing any agent code. The goal is to understand the submission wrapper, agent API, current baseline options, and what framework files still need deeper inspection.

## K-12 summary

We have three starter robots:

1. A random robot that presses buttons randomly.
2. A heuristic/exploration robot that tries to explore more deliberately.
3. A learning robot that tries to learn which actions change the screen.

Before building a better robot, we first check how these robots are plugged into the game, how they decide actions, and whether their notebook wrappers run correctly.

## Files inspected

Baseline notebooks:

- `x_competition_files/C_code/C1_arc3-sample-submission-random-agent_silver_medal.ipynb`
- `x_competition_files/C_code/C2_arc3-sample-submission-stochastic-goose_gold _medal.ipynb`
- `x_competition_files/C_code/C3_arc3-sample-submission-just-explore_bronze_medal.ipynb`

Baseline logs:

- `x_competition_files/C_code/C12_arc3-sample-submission-random-agent.log`
- `x_competition_files/C_code/C21_arc3-sample-submission-stochastic-goose.log`
- `x_competition_files/C_code/C31_arc3-sample-submission-just-explore.log`

Framework/reference files searched:

- `x_competition_files/B_data/B2_files/README.md`
- `x_competition_files/B_data/B2_files/llms.txt`
- Expected but not directly found as standalone files in the indexed repo:
  - `x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/agent.py`
  - `x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/swarm.py`
  - `x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/main.py`

## Common notebook pattern

All three sample notebooks use the same high-level submission structure:

1. Install `arc-agi` from local competition wheels.
2. In Kaggle competition rerun mode, wait for the gateway endpoint.
3. Copy the official `ARC-AGI-3-Agents` package into `/kaggle/working`.
4. Inject the selected custom agent into `agents/templates/`.
5. Patch `agents/__init__.py` to avoid eager imports of optional dependencies.
6. Write a `.env` pointing to the Kaggle gateway.
7. Run `python main.py --agent <agent_name>`.
8. In non-rerun mode, write a dummy `submission.parquet` so the notebook commits cleanly.

## Random agent baseline

Path:

```text
x_competition_files/C_code/C1_arc3-sample-submission-random-agent_silver_medal.ipynb
```

Observed behavior:

- Defines `MyAgent(Agent)`.
- Uses `MAX_ACTIONS = float('inf')`.
- `is_done(...)` returns true when `latest_frame.state is GameState.WIN`.
- If state is `NOT_PLAYED` or `GAME_OVER`, it returns `GameAction.RESET`.
- Otherwise it randomly selects a non-reset `GameAction`.
- If the selected action is complex, it assigns random coordinates:
  - `x`: random integer from 0 to 63
  - `y`: random integer from 0 to 63

Practical interpretation:

- This is the cleanest P0 baseline.
- It is simple, submission-safe, and easy to edit.
- Do not assume the filename label `silver_medal` means it is currently validated as strong; the actual code is random.

## Just-explore baseline

Path:

```text
x_competition_files/C_code/C3_arc3-sample-submission-just-explore_bronze_medal.ipynb
```

Observed behavior:

- Copies an external Kaggle dataset/package into `/kaggle/working`.
- Exposes a `HeuristicAgent` through `agents/__init__.py`.
- Runs:

```bash
python main.py --agent heuristicagent
```

Practical interpretation:

- This is likely a useful heuristic/exploration reference.
- The core logic is not fully visible from the wrapper alone.
- We should inspect the copied `HeuristicAgent` implementation if it exists in the repo or can be exported from the Kaggle dataset.

## StochasticGoose baseline

Path:

```text
x_competition_files/C_code/C2_arc3-sample-submission-stochastic-goose_gold _medal.ipynb
```

Observed behavior:

- Writes a large custom `my_agent.py`.
- Uses PyTorch.
- Defines a CNN-style `ActionModel`.
- Converts the 64x64 grid into one-hot color channels.
- Predicts a combined action space:
  - simple action logits
  - coordinate logits across a 64x64 grid
- Stores experience in a replay buffer.
- Trains online while playing.
- Resets buffer/model when level/score changes.

Practical interpretation:

- This is the most interesting P2/P3 candidate.
- It tries to learn action effects online, which is aligned with interactive ARC-AGI-3.
- It is also harder to debug and may have runtime/memory risks.
- Its internal time guard should be reviewed against the Kaggle 6-hour limit before using it as a serious submission base.

## Log inspection

The logs mainly confirm notebook execution, not true game performance.

Confirmed from logs:

- Local wheel install path is used.
- `arc-agi` and `arcengine` install successfully.
- `pillow` is upgraded to `12.1.1`.
- Dependency warnings appear for unrelated packages such as `dopamine-rl` and `gradio`.
- Notebooks complete in non-competition mode.
- Dummy `submission.parquet` is written when not in rerun mode.

Not confirmed by logs:

- Actual competition score.
- Game-level win rate.
- Action efficiency.
- Which games were solved.
- Whether the `bronze/silver/gold` labels are current or validated.

## Framework notes from `B_data/B2_files`

The available `README.md` and `llms.txt` describe the upstream `ARC-AGI-3-Agents` framework. They state that the core framework lives in `agents/` and includes:

- `agent.py`: base `Agent` class and utilities.
- `swarm.py`: orchestration for running many agents in parallel.
- `recorder.py`: JSONL gameplay recording utilities.
- `structs.py`: typed data structures such as `FrameData` and `GameAction`.

The README also notes important API changes:

- `score` changed to `levels_completed`.
- `win_score` changed to `win_levels`.
- `available_actions` was added to `FrameData`.
- `ACTION7` was added as a possible `GameAction`.

## Important current gap

The exact standalone files requested for lifecycle inspection were not found directly under the expected path in the indexed repo:

```text
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/agent.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/swarm.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/main.py
```

What we could verify instead:

- The sample notebooks copy `/kaggle/input/competitions/arc-prize-2026-arc-agi-3/ARC-AGI-3-Agents` during Kaggle rerun.
- The repo currently exposes framework documentation in `B_data/B2_files/README.md` and `B_data/B2_files/llms.txt`.
- The actual framework source may be inside the Kaggle competition dataset, not fully expanded into this GitHub repo.

## Working hypothesis on lifecycle

Based on the wrappers and framework docs, the likely lifecycle is:

1. `main.py` loads the selected agent class from `AVAILABLE_AGENTS`.
2. The agent receives frames from the gateway/environment.
3. The base `Agent` stores frames and invokes the custom agent hooks.
4. `is_done(frames, latest_frame)` decides whether the agent should stop.
5. `choose_action(frames, latest_frame)` returns a `GameAction`.
6. Complex actions require attached coordinate/action data.
7. Recorder utilities may write JSONL gameplay traces when enabled.
8. `Swarm` likely orchestrates multiple games/agents or parallel execution.

This remains a hypothesis until the actual `agent.py`, `swarm.py`, and `main.py` source files are inspected.

## Baseline ranking for project workflow

| Level | Candidate | Reason |
|---|---|---|
| P0 | Random agent | Cleanest minimal submission baseline |
| P1 | Just-explore | Useful heuristic/exploration reference |
| P2 | StochasticGoose | Online action-effect learning candidate |
| P3 | Hybrid | Combine heuristic exploration, memory, and action-effect learning |

## Recommended next actions

1. Locate or export the full `ARC-AGI-3-Agents` source tree into the repo, especially:
   - `agents/agent.py`
   - `agents/swarm.py`
   - `agents/recorder.py`
   - `agents/structs.py`
   - `main.py`
2. Keep the imported source under a clearly marked reference path, for example:

```text
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/
```

3. Do not modify the reference copy directly.
4. After source inspection, create:

```text
docs/framework_lifecycle_inspection.md
```

5. Then create a clean P0 baseline branch/notebook copied outside `x_competition_files/`.
