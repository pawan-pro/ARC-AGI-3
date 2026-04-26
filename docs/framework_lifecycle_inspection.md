# ARC-AGI-3 Framework Lifecycle Inspection

Date: 2026-04-26

## Purpose

Document the runtime lifecycle of the ARC-AGI-3 agent framework before modifying or building new agents.

This note is based on the selected upstream framework files copied into this repo under:

```text
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/
```

## K-12 summary

Think of the framework as a game referee and a robot player.

- `main.py` starts the match.
- `Swarm` creates one robot for each game.
- Each `Agent` looks at the latest screen.
- The agent chooses one move.
- The environment returns a new screen.
- The agent stores that screen in memory.
- The loop repeats until the game is won, the agent says it is done, or the move limit is reached.
- The recorder writes down what happened.
- The scorecard is closed at the end.

## Files verified

The following lifecycle files were verified as present and readable in the repo:

```text
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/main.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/agent.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/swarm.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/recorder.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/tracing.py
x_competition_files/B_data/B2_files/ARC-AGI-3-Agents/agents/__init__.py
```

Important caveat:

`agents/__init__.py` imports template agents that are not all copied into this repo yet. That is acceptable for lifecycle inspection, but not enough to run the full upstream package from this reference folder without copying the template files as well.

## High-level lifecycle

```text
main.py
  -> loads .env / .env.example
  -> parses CLI args
  -> fetches available game IDs from /api/games
  -> creates Swarm(agent, ROOT_URL, games, tags)
  -> starts Swarm in a thread

Swarm.main()
  -> opens scorecard
  -> creates one Agent instance per game
  -> starts one thread per Agent
  -> waits for all agents to finish
  -> closes scorecard
  -> calls cleanup(scorecard)

Agent.main()
  -> starts timer
  -> loops while not is_done(...) and action_counter <= MAX_ACTIONS
  -> reads latest environment observation
  -> converts raw observation to FrameData
  -> calls choose_action(frames, latest_frame)
  -> submits the returned GameAction
  -> receives next FrameData
  -> appends frame to frames memory and recorder
  -> increments action_counter
  -> cleanup()
```

## 1. `main.py`

Role:

`main.py` is the command-line entrypoint.

Key responsibilities:

- Loads `.env.example` first and then `.env` with override enabled.
- Builds `ROOT_URL` from `SCHEME`, `HOST`, and `PORT` environment variables.
- Parses CLI args:
  - `--agent`
  - `--game`
  - `--tags`
- Gets the available game list from:

```text
{ROOT_URL}/api/games
```

- Optionally filters games by prefix if `--game` is provided.
- Initializes AgentOps tracing if configured.
- Creates a `Swarm`.
- Runs the swarm in a daemon thread.
- Installs a SIGINT cleanup handler.

Practical implication:

For Kaggle submission notebooks, the key command remains:

```bash
python main.py --agent <agent_name>
```

or for a subset of games:

```bash
python main.py --agent <agent_name> --game <game_prefix>
```

Important detail:

`main.py` imports `AVAILABLE_AGENTS` from `agents`. Therefore, any custom agent must be registered or exposed through `agents/__init__.py`, unless the notebook patches `agents/__init__.py` the way the sample notebooks do.

## 2. `agents/__init__.py`

Role:

`agents/__init__.py` builds the agent registry used by `main.py`.

Key responsibilities:

- Imports base classes and available template agents.
- Builds:

```python
AVAILABLE_AGENTS: dict[str, Type[Agent]]
```

- Uses lowercase class names as agent keys.
- Adds playback recording files as valid agent names.
- Adds `reasoningagent` explicitly.

Practical implication:

If we create `MyAgent`, the easiest submission-safe pattern is the sample-notebook pattern:

1. Copy/write `my_agent.py` into `agents/templates/`.
2. Patch `agents/__init__.py` so it imports only required classes.
3. Add something like:

```python
from .templates.my_agent import MyAgent
AVAILABLE_AGENTS = {"myagent": MyAgent}
```

This avoids eager imports of LLM/template dependencies that may not be available or needed.

## 3. `Swarm`

Role:

`Swarm` orchestrates many agents playing many ARC-AGI-3 games.

Key responsibilities:

- Receives:
  - agent name
  - root URL
  - game list
  - optional tags
- Looks up the agent class from `AVAILABLE_AGENTS`.
- Creates an `Arcade()` object.
- Opens a scorecard.
- Creates one agent instance per game:

```python
self.agent_class(
    card_id=self.card_id,
    game_id=g,
    agent_name=self.agent_name,
    ROOT_URL=self.ROOT_URL,
    record=True,
    arc_env=self._arc.make(g, scorecard_id=self.card_id),
    tags=self.tags,
)
```

- Starts one thread per agent.
- Waits for all agent threads to finish.
- Closes the scorecard.
- Calls cleanup on all agents.

Practical implication:

A single submission run can create multiple agent instances, one per available game. Agent state should be instance-local, not stored as shared global state unless explicitly intended.

## 4. `Agent.__init__`

Role:

Initializes one agent instance for one game.

Key fields:

```python
self.ROOT_URL = ROOT_URL
self.card_id = card_id
self.game_id = game_id
self.guid = ""
self.agent_name = agent_name
self.tags = tags or []
self.frames = [FrameData(levels_completed=0)]
self._cleanup = True
self.arc_env = arc_env
```

Important default:

```python
MAX_ACTIONS: int = 80
```

Practical implication:

Every agent starts with a placeholder frame:

```python
FrameData(levels_completed=0)
```

The real current observation is passed to `choose_action` from `arc_env.observation_space`, not necessarily from `self.frames[-1]` at the first call.

## 5. `Agent.main`

Role:

This is the core action loop for one game.

Loop condition:

```python
while (
    not self.is_done(self.frames, self.frames[-1])
    and self.action_counter <= self.MAX_ACTIONS
):
```

Inside each loop:

```python
action = self.choose_action(
    self.frames,
    self._convert_raw_frame_data(
        self.arc_env.observation_space if self.arc_env else None
    ),
)

if frame := self.take_action(action):
    self.append_frame(frame)

self.action_counter += 1
```

Practical implication:

`choose_action` receives two views of state:

1. `frames`: the stored frame history after previous actions.
2. `latest_frame`: the latest observation converted directly from the environment.

These can be different early in the episode because `self.frames` starts with a placeholder frame.

## 6. `is_done(frames, latest_frame)`

Role:

Custom agent hook deciding whether the agent should stop.

Signature:

```python
def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
```

Framework rule:

- The framework calls `is_done(self.frames, self.frames[-1])` in the loop condition.
- If it returns `True`, no new action is selected.

Practical implication:

Our baseline should usually stop when:

```python
latest_frame.state is GameState.WIN
```

For safety, future agents may also stop on repeated loops, obvious no-progress patterns, or near-runtime limits.

## 7. `choose_action(frames, latest_frame)`

Role:

Custom agent hook selecting the next action.

Signature:

```python
def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
```

Framework expectation:

- Must return a valid `GameAction`.
- Complex actions must have their required action data filled in before return.
- The action is passed directly to `take_action`.

Practical implication:

The agent should inspect:

```python
latest_frame.state
latest_frame.frame
latest_frame.levels_completed
latest_frame.available_actions
```

The safest initial policy remains:

```python
if latest_frame.state in [GameState.NOT_PLAYED, GameState.GAME_OVER]:
    return GameAction.RESET
```

Then select from `available_actions` where possible rather than assuming all actions are legal.

## 8. `take_action(action)` and `do_action_request(action)`

Role:

Submits the selected action to the environment and receives the next frame.

Flow:

```python
take_action(action)
  -> do_action_request(action)
      -> data = action.action_data.model_dump()
      -> raw = self.arc_env.step(action, data=data, reasoning=data["reasoning"] if present else {})
      -> _convert_raw_frame_data(raw)
  -> FrameData.model_validate(frame_data)
  -> returns FrameData or None
```

Practical implication:

Agent authors do not call `arc_env.step` directly. They return a `GameAction`; the framework submits it.

If action data is malformed, validation or environment execution may fail. Therefore, coordinate actions must be populated carefully.

## 9. `_convert_raw_frame_data(raw)`

Role:

Converts raw environment output into the pydantic-style `FrameData` used by agents.

Fields copied:

```python
game_id
frame
state
levels_completed
win_levels
guid
full_reset
available_actions
```

Practical implication:

The framework has already migrated from old `score` naming to:

```python
levels_completed
```

Agent code should use `levels_completed`, not `score`.

## 10. `append_frame(frame)`

Role:

Stores a new frame after a successful action.

Behavior:

```python
self.frames.append(frame)
if frame.guid:
    self.guid = frame.guid
if hasattr(self, "recorder") and not self.is_playback:
    self.recorder.record(json.loads(frame.model_dump_json()))
```

Practical implication:

`frames` is an unbounded list by default. Long-running agents or agents with high `MAX_ACTIONS` may want to override `append_frame` to keep only the most recent N frames.

The StochasticGoose notebook does this with a sliding-window override.

## 11. `Recorder`

Role:

Writes gameplay events to JSONL files.

Filename pattern:

```text
<prefix>.<guid>.recording.jsonl
```

Each event contains:

```json
{
  "timestamp": "<UTC ISO timestamp>",
  "data": {...}
}
```

The recordings directory is controlled by:

```text
RECORDINGS_DIR
```

Practical implication:

Recordings are crucial experiment artifacts. For local/offline evaluation, save them under a structured folder such as:

```text
logs/raw/
logs/parsed/
logs/summaries/
```

## 12. Scorecard lifecycle

Scorecard flow:

```text
Swarm.main()
  -> open_scorecard()
  -> create/run agents
  -> close_scorecard(card_id)
  -> log final scorecard
  -> cleanup(scorecard)
```

`Swarm.open_scorecard` calls:

```python
self._arc.open_scorecard(tags=self.tags)
```

`Swarm.close_scorecard` calls:

```python
self._arc.close_scorecard(card_id)
```

Practical implication:

Scores are attached at the swarm/environment level, not produced manually by our agent. Our job is to make the agent act effectively and preserve logs/recordings.

## 13. `MAX_ACTIONS`

Default:

```python
MAX_ACTIONS: int = 80
```

Loop condition uses:

```python
self.action_counter <= self.MAX_ACTIONS
```

Cleanup logs whether the agent reached the move cap:

```python
if self.action_counter >= self.MAX_ACTIONS:
    logger.info("Exiting: agent reached MAX_ACTIONS ...")
```

Practical implication:

Because the condition is `<=`, an agent may effectively get one more loop than expected depending on counter state. We should test this during baseline reproduction rather than assume exact action count.

For serious submissions, `MAX_ACTIONS` should be treated as an efficiency/risk control, not simply set to infinity.

## 14. `cleanup`

There are two cleanup levels.

### Agent cleanup

`Agent.cleanup(scorecard=None)`:

- Runs only once due to `_cleanup` guard.
- Records scorecard data for that game if scorecard is provided.
- Logs the recording filename.
- Logs whether the agent ended due to `MAX_ACTIONS` or normal finish.

### Swarm cleanup

`Swarm.cleanup(scorecard=None)`:

- Calls cleanup on every agent.
- Closes session if present.

### Main cleanup

`main.py` also installs a SIGINT handler that:

- Closes the scorecard if still open.
- Logs existing scorecard report.
- Calls `swarm.cleanup(scorecard)`.
- Exits process.

Practical implication:

The framework is designed to preserve scorecard/recording artifacts even if interrupted, but we should still avoid unnecessary forced exits in Kaggle notebooks.

## 15. Key design implications for our agents

### P0 baseline

Start with a clean random agent that:

- Uses the official `Agent` interface.
- Returns `RESET` for `NOT_PLAYED` or `GAME_OVER`.
- Stops on `GameState.WIN`.
- Uses `available_actions` where possible.
- Sets coordinate action data correctly for complex actions.
- Keeps the notebook submission-safe.

### P1 robust submission

Add guardrails:

- Avoid immediate repeat loops.
- Track no-change actions.
- Prefer actions that cause visible frame changes.
- Cap or summarize frame history.
- Log action reason and simple state summaries.

### P2 leaderboard improvement

Add adaptive exploration:

- Learn which actions are available and useful per game.
- Track state/action/effect tuples.
- Detect level changes using `levels_completed`.
- Reset local memory on level transition.

### P3 medal-level research bet

Hybrid approach:

- Heuristic exploration first.
- Online action-effect learning second.
- Memory and hypothesis testing third.
- Planning/search when environment dynamics become predictable.

## 16. Open questions for next development step

1. What is the exact action-data schema for each `GameAction`, especially coordinate actions?
2. How should `available_actions` be interpreted: raw ints, enums, or both?
3. How many games are exposed during local/offline evaluation versus Kaggle rerun?
4. What does a real recording JSONL look like for each baseline?
5. What is the exact public leaderboard score for each sample baseline if submitted today?
6. Should P0 keep `MAX_ACTIONS = 80`, increase it, or make it configurable?

## Next step

Create a clean P0 baseline plan and working copy outside `x_competition_files`:

```text
experiments/000_baseline_reproduction/README.md
notebooks/00_baselines/p0_random_agent_clean.ipynb
```

Do not modify the copied upstream reference files directly.
