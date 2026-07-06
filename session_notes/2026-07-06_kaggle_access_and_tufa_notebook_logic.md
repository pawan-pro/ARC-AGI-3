# 2026-07-06 Session Notes - Kaggle Access and Tufa Duck Notebook Logic

## Session context

This note records the follow-up discovery work after the Duck reproduction became the active project baseline.

Current project baseline remains:

```text
Submission: ARC-AGI-3 - Duck Public Notebook Reproduction Work - Version 1
Kaggle public score: 0.84
Status: Succeeded
Submission date: 2026-07-04 19:07:23
```

The goal of this session was to confirm what Codex can access directly:

```text
1. GitHub commits and session notes
2. Kaggle CLI and competition submissions
3. Our replicated Duck notebook
4. The Tufa/Jeroen milestone notebook
5. The Kaggle winning write-up and embedded images
6. A K-12 explanation of the winning notebook logic
```

## GitHub access

Repository identified:

```text
pawan-pro/ARC-AGI-3
```

Latest planning commits referenced:

```text
fc52360d32f0ab5d7800acb79c839ef10cd40a28
docs: record duck reproduction baseline in experiment tracker

1e78c290e43b9befce06270ad19b7e6160b318b5
docs: add 2026-07-06 duck strategy session note

4a1a6414d6ab2817c4680c1c544e0104feee67e5
docs: add codex prompt for duck replay trace scaffold
```

Important local finding:

```text
The local workspace initially contained only an unborn Git repo with no files and no remote.
Codex added origin as https://github.com/pawan-pro/ARC-AGI-3.git, fetched main, and checked out main from origin/main.
```

## Kaggle CLI access

Kaggle CLI is available and authenticated locally:

```text
kaggle 2.1.2
```

The account is entered in:

```text
arc-prize-2026-arc-agi-3
```

Competition submissions can be queried with:

```bash
kaggle competitions submissions arc-prize-2026-arc-agi-3
```

The latest Duck reproduction submission was visible in Kaggle submission history:

```text
ref: 54339875
fileName: submission.parquet
date: 2026-07-04 19:07:23.407000
description: Notebook ARC-AGI-3 - Duck Public Notebook Reproduction Work | Version 1
status: SubmissionStatus.COMPLETE
publicScore: 0.84
```

## Our replicated Duck notebook

Codex found and pulled our private Duck reproduction kernel:

```text
jatalepawan/arc-agi-3-duck-public-notebook-reproduction-work
```

Pulled locally to:

```text
/tmp/kaggle_duck_pull/arc-agi-3-duck-public-notebook-reproduction-work.ipynb
/tmp/kaggle_duck_pull/kernel-metadata.json
```

Metadata confirmed:

```text
title: ARC-AGI-3 - Duck Public Notebook Reproduction Work
is_private: true
enable_gpu: true
enable_internet: false
machine_shape: NvidiaRtxPro6000
competition_sources:
  - arc-prize-2026-arc-agi-3
dataset_sources:
  - driessmit1/arc3-vllm-h100-wheelhouse-v3
  - jeroencottaar/taaf-kaggle-source-share
  - driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
```

Practical result:

```text
Codex can pull, edit, push, monitor, read logs, and read the public score for Kaggle notebooks through the CLI.
```

Useful commands:

```bash
kaggle kernels pull jatalepawan/arc-agi-3-duck-public-notebook-reproduction-work -p <workdir> --metadata
kaggle kernels push -p <workdir>
kaggle kernels status jatalepawan/arc-agi-3-duck-public-notebook-reproduction-work
kaggle kernels logs jatalepawan/arc-agi-3-duck-public-notebook-reproduction-work
kaggle competitions submissions arc-prize-2026-arc-agi-3
```

Working caution:

```text
kaggle kernels push updates and runs the Kaggle notebook. For controlled experiments, first preserve the pulled notebook in Git, then push a clearly named version.
```

## Winning write-up and attached notebooks

Kaggle discussion accessed:

```text
https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion/717133
```

Authenticated CLI command used:

```bash
kaggle competitions topic-messages arc-prize-2026-arc-agi-3 717133 -n -1 -v
```

The discussion text describes the Tufa Labs Duck harness and links to Kaggle notebooks.

The exact write-up link:

```text
jeroencottaar/taaf-duck-harness-kaggle-share
```

returned 404 through the Kaggle API, but Kaggle search exposed the visible public replacement/readable notebook:

```text
jeroencottaar/tufa-labs-duck-harness-june-30-milestone-winner
```

Pulled locally to:

```text
/tmp/kaggle_tufa_milestone/tufa-labs-duck-harness-june-30-milestone-winner.ipynb
/tmp/kaggle_tufa_milestone/kernel-metadata.json
```

Metadata confirmed:

```text
title: Tufa Labs duck harness [June 30 milestone winner]
is_private: false
enable_gpu: true
enable_internet: false
machine_shape: NvidiaRtxPro6000
competition_sources:
  - arc-prize-2026-arc-agi-3
dataset_sources:
  - driessmit1/arc3-vllm-h100-wheelhouse-v3
  - jeroencottaar/taaf-kaggle-source-share
  - driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
```

The official/result wrapper notebook was also pulled:

```text
jeroencottaar/taaf-duck-harness-kaggle
```

Pulled locally to:

```text
/tmp/kaggle_taaf_duck_kaggle/taaf-duck-harness-kaggle.ipynb
/tmp/kaggle_taaf_duck_kaggle/kernel-metadata.json
```

Important distinction:

```text
The official/result wrapper notebook has only one markdown cell pointing users to the readable notebook.
The readable milestone notebook has 17 cells and is the useful file for understanding the flow.
```

## Winning write-up images

Codex can access the embedded Kaggle forum attachment images.

Seven image URLs were extracted from discussion 717133:

```text
duck_harness_pretty.png
viewer_thinking_figure.png
viewer_action_figure.png
context_eviction.gif
segmentation_decomposition.png
fig1_heatmap_levels.png
fig3_cumulative_score.png
```

Downloads tested successfully with HTTP 200.

Local scratch download path used:

```text
/tmp/kaggle_discussion_717133_images/
```

## K-12 explanation of the winning notebook

The winning notebook is best understood as a school bus driver for a smart game-playing student.

The notebook itself is not the brain. It mostly sets up the classroom, brings in the brain from attached files, starts the tools, runs the games, and saves the report card.

### Big idea

The Duck approach turns each ARC-AGI-3 game into something a coding LLM can inspect through Python.

Instead of saying:

```text
Look at this game screen and magically solve it.
```

it says:

```text
Here is the screen as data.
Here are the objects.
Here is the last move.
Here is what changed.
You may write Python to inspect it.
When ready, call an action.
```

So the LLM behaves less like a random player and more like a student using a notebook, scratch paper, and experiments.

### Notebook flow

1. Prepare the Kaggle room.

   The notebook checks whether it is running as a real Kaggle submission or just a normal notebook run. If it is a real submission, it keeps diagnostics small. If it is a normal run, it saves more debugging output.

2. Install the ARC game runtime.

   Kaggle has no internet during the run, so the notebook installs `arc-agi` from the competition files already mounted inside Kaggle.

3. Find the attached Duck source bundle.

   The real solver code is not typed directly in the notebook. It is attached as a Kaggle dataset. The notebook searches `/kaggle/input` for the TAAF/Duck bundle.

4. Make the solver code importable.

   The notebook adds the attached source folders to Python's path, so Python can import the Duck harness code.

5. Run setup commands.

   This is where the heavy machinery starts, including local model/runtime setup. The model is not downloaded live. It is mounted as a Kaggle dataset and served locally.

6. Load the benchmark.

   The notebook loads a saved benchmark object from `benchmark_initial.pkl`. This is like loading the game list, solver configuration, scoring setup, and run settings.

7. Leave a customization hook.

   There is a blank safe spot where someone can tweak the benchmark before running. In the shared notebook, this is mostly left alone.

8. Choose live vs offline games.

   If this is a real Kaggle rerun, it connects to the Kaggle competition gateway and plays the hidden/live competition games. If it is just a normal notebook run, it plays the bundled offline environment files.

9. Run one pass.

   The notebook sets:

   ```text
   bm.n_passes = 1
   ```

   Then the benchmark runs the Duck solver over the games.

10. Write outputs.

   The run writes results into `/kaggle/working`, including benchmark data, diagnostics, recordings, and submission output.

11. Show diagnostics.

   In non-submission mode, the notebook displays `diagnostics.html`, which helps humans inspect what happened.

### What Duck does while playing

For each game, Duck gives the LLM a Python workspace containing things like:

```text
current_frame
previous_frame
history
transitions
last_action
last_action_result
valid_actions
segmentation
```

Plain-English meanings:

```text
current_frame: what the game looks like now
previous_frame: what it looked like before
history: what actions were already tried
transitions: action to result records
valid_actions: buttons/mouse actions allowed
segmentation: object-like pieces found in the screen
```

The LLM can write Python to inspect the state and eventually call actions like:

```text
UP
DOWN
LEFT
RIGHT
SPACE
MOUSE
RESET
```

The LLM is also shown an image of the current board, so it gets both visual and code/data views.

### Why it works

The winning trick is not one magic rule. It is this loop:

```text
Look at game state.
Think with Python.
Try an action.
Observe what changed.
Update world model.
Repeat.
```

This is powerful because ARC-AGI-3 games often require discovering the rules of a tiny world. Duck lets the LLM experiment and remember useful facts.

### Why context management matters

The LLM can play for a long time, but its memory window is limited. Duck keeps the system prompt pinned and removes older less-important messages when context gets too large.

K-12 version:

```text
The student keeps the teacher's instructions, keeps the newest observations, and throws away old scratch paper when the desk gets too full.
```

### Important caveat

The visible Kaggle notebook is mostly infrastructure. The actual solver behavior, prompts, tools, and model interaction live in the attached TAAF/Duck source dataset.

Therefore, the safest next step is not prompt tuning. The safest next step is:

```text
1. Add replay/trace tools.
2. Watch what the LLM actually did.
3. Identify which solved-game behaviors are reusable.
4. Only then try one controlled solver variant.
```

## Recommended next action

Proceed with the already-planned observational Codex branch:

```text
exp/duck-replay-trace-review-2026-07-06
```

Implementation prompt:

```text
codex_prompts/2026-07-06_duck_replay_trace_review.md
```

Do not change solver behavior yet.
