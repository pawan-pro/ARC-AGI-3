# Qwen 3.8 reproduction result

Version 1 completed; benchmark.json, score.json and kernel log are in output_v1.
Validated 25 expected unique public games, finite scores and real actions in every
game. All 25 ended as gave_up; none crashed or were cancelled.

- Offline mean: 7.291313041679922.
- Levels completed: 37.
- Actions: 3,179.
- Previous Qwen offline means: 1.306 and 1.204.
- Last verified official leaderboard best: 1.12 (separate evaluation).

Submission is held for review. After saving scores, serving_teardown.py reported
shutdown_ok=false and one surviving GPU process, then raised
RuntimeError: vLLM teardown did not reach the bounded terminal gate.
Gameplay validation passed, but clean runtime termination was not established.
No submission or retry was performed by these monitoring checks.
