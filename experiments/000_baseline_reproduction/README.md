# EXP-000 — P0 Baseline Reproduction

Date opened: 2026-04-26
Status: Planned
Priority: P0

## Objective

Create and validate a clean ARC-AGI-3 baseline agent outside `x_competition_files/`.

This experiment should reproduce the simplest working submission pattern before any architecture changes are attempted.

## K-12 summary

Before building a smarter robot, first make sure our simplest robot can enter the game, press legal buttons, finish the run, and produce a valid Kaggle submission.

## Source references

Reference files:

```text
x_competition_files/C_code/C1_arc3-sample-submission-random-agent_silver_medal.ipynb
x_competition_files/C_code/C12_arc3-sample-submission-random-agent.log
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/main.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/agent.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/swarm.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/recorder.py
```

Documentation:

```text
docs/rules_constraints.md
docs/baseline_notebook_inspection.md
docs/framework_lifecycle_inspection.md
```

## Planned working artifact

Notebook to create next:

```text
notebooks/00_baselines/p0_random_agent_clean.ipynb
```

Optional extracted agent file after notebook stabilizes:

```text
src/arc_agi3/agents/p0_random_agent.py
```

## Baseline behavior

The P0 agent should:

1. Inherit from the official `Agent` base class.
2. Implement:

```python
def is_done(self, frames, latest_frame):
    ...


def choose_action(self, frames, latest_frame):
    ...
```

3. Stop when `latest_frame.state is GameState.WIN`.
4. Return `GameAction.RESET` when state is `NOT_PLAYED` or `GAME_OVER`.
5. Prefer `latest_frame.available_actions` when selecting actions.
6. Fall back to valid non-reset actions if `available_actions` is missing or malformed.
7. Correctly populate action data for coordinate/complex actions.
8. Produce a valid notebook commit and submission artifact.

## Hypothesis

A clean minimal random baseline gives us a reproducible control submission and helps verify:

- Kaggle notebook wrapper correctness.
- Gateway connection behavior.
- Action schema.
- Recording/logging behavior.
- Valid submission generation.

This experiment is not expected to be strong; it is expected to be reliable.

## Success criteria

Minimum success:

- Notebook runs end-to-end in non-competition mode.
- Dummy `submission.parquet` is created when not in Kaggle rerun mode.
- Notebook has no syntax/import errors.

Competition-mode success:

- Notebook connects to gateway.
- Agent takes actions on at least one game.
- Submission is accepted by Kaggle.
- Public leaderboard score is recorded.

Artifact success:

- Logs are saved.
- Score/result is added to `docs/experiment_tracker.md`.
- Session notes mention exact notebook path, commit, and score.

## Validation steps

### Local/repo validation

1. Confirm notebook exists:

```bash
ls notebooks/00_baselines/p0_random_agent_clean.ipynb
```

2. Confirm no accidental edits to reference files:

```bash
git status -- x_competition_files
```

3. Confirm experiment tracker updated after run:

```bash
grep "EXP-000" docs/experiment_tracker.md
```

### Kaggle validation

1. Upload or create notebook on Kaggle.
2. Attach official ARC-AGI-3 competition data.
3. Disable internet.
4. Commit notebook.
5. Confirm notebook completes.
6. Submit if the run is valid.
7. Record score and logs.

## Risks

| Risk | Mitigation |
|---|---|
| `available_actions` format differs between wrapper and gateway | Accept both raw ints and enum-like values |
| Complex action schema unclear | Inspect `GameAction` behavior in sample notebooks before changing logic |
| Full upstream `agents/__init__.py` imports missing templates | Patch `agents/__init__.py` in notebook to expose only the P0 agent |
| Random agent wastes actions | This is acceptable for P0; later experiments improve exploration |
| `MAX_ACTIONS` action count ambiguity | Keep default initially; document observed action counts from logs |

## Fallback plan

If the clean notebook fails:

1. Revert to the known sample random-agent notebook wrapper.
2. Change only the minimum required agent registration code.
3. Avoid improving policy until submission mechanics are validated.

## Planned experiment tracker row

```markdown
| EXP-000 | 2026-04-26 | notebooks/00_baselines/p0_random_agent_clean.ipynb | P0RandomAgent | Clean random baseline reproduction | TBD | TBD | Planned | Validate submission mechanics before improvements |
```

## Next action

Create:

```text
notebooks/00_baselines/p0_random_agent_clean.ipynb
```

The first version should be a clean copy/adaptation of the inspected random-agent sample notebook, not a new architecture.
