# 2026-07-06 Session Notes — Duck Baseline Strategy and Replay Plan

## Session context

We started the 2026-07-06 ARC Prize 2026 / ARC-AGI-3 session after the public Duck reproduction notebook produced a valid Kaggle submission score.

New Kaggle result reported by user:

```text
Submission: ARC-AGI-3 — Duck Public Notebook Reproduction Work - Version 1
Status: Succeeded
Public score: 0.84
```

This follows the 2026-07-04 public benchmark reproduction:

```text
Duck-Repro-A public benchmark official ARC mean: 1.68
Weighted scorer mean: 3.61
Raw levels beaten mean: 0.72
Duration: 2h 12m 36s
Games: 25
Passes: 1
Runs won: 0 / 25
Games with level progress: 14 / 25
Total completed levels: 18
Total actions: 3,545
Total tokens: 1,576,578
```

## Current score ladder

| Stage | Result | Decision |
|---|---:|---|
| P0 random baseline | 0.07 public | Valid control only |
| Historical FORGE / no-BFS range | 0.26–0.28 public | Superseded |
| Persistent-memory gated-BFS best observed | ~0.38 public | Keep as historical fallback; no longer active best architecture |
| Duck public notebook reproduction | 0.84 public | New strongest validated submission path |
| Duck public benchmark reproduction | 1.68 public-game mean | Strong local/public diagnostic artifact; not leaderboard score |
| Tufa reference | 1.21 official Milestone 1 score; ~1.6002 ± 0.4475 public-train mean | Reference target to replicate/beat |

Working conclusion:

```text
Duck is now the active baseline. The next objective is not random prompt hacking. The next objective is to understand the harness mechanics, replay solved games, identify reusable behavior, then run small controlled variants that can beat 0.84 and approach/exceed the Tufa 1.21 reference.
```

## User question / strategic issue

The user asked whether to manage the work in one chat or two chats:

```text
1. one chat to understand notebook code, logic, and brainstorm ideas;
2. another chat for implementation;
3. or push everything to git and take it up in Codex.
```

Recommended workflow:

```text
Use one ChatGPT project chat for research direction, interpretation, scorekeeping, and session notes.
Use Codex for implementation on a clean branch with copy-paste-ready prompts.
```

Rationale:

- Understanding and implementation are tightly linked, so splitting across two chats can create drift.
- Codex is better for repo edits, notebook surgery, and file-level changes.
- ChatGPT should remain the research notebook / project manager layer.
- Every implementation should land in a named branch/folder and produce artifacts.

## Conceptual understanding of Duck

User's understanding was mostly correct:

```text
We are using a local Qwen multimodal/coding LLM snapshot attached as a Kaggle dataset, served via vLLM.
The LLM sees the game screen, ASCII/grid state, segmentation/state variables, and prior history.
It uses a Python REPL to inspect the state, reason, test actions, and call action([...]).
It observes transitions and updates its hypothesis/world model.
It continues until it solves levels or gives up/timeouts.
Context is managed by keeping the system prompt pinned and evicting older non-system context; compact world-model notes help carry useful facts forward.
```

Important correction:

```text
The model is not downloaded live from Hugging Face during the Kaggle run. Internet is off. The Qwen model snapshot is attached as a Kaggle dataset and served locally via vLLM.
```

The submitted log confirmed:

```text
Model path: /kaggle/input/datasets/driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot
Served model name: vrfai/Qwen3.6-27B-FP8
vLLM version: 0.19.0
GPU: NVIDIA RTX PRO 6000 Blackwell Server Edition
max model len: 65536
reasoning parser: qwen3
tool call parser: qwen3_coder
enable prefix caching: true
```

## Replay viewer requirement

The user remembered a play button after a code block that showed the game being played by the selected logic.

Decision:

```text
Add a replay/movie viewer cell to the Duck reproduction notebook/workbench.
```

Purpose:

```text
Move from score tables to behavioral diagnosis:
- What did the LLM see?
- What did it try first?
- Which actions caused level progress?
- Where did it waste tokens/actions?
- Which mechanics were inferred correctly?
- Which games failed due to perception/objective/action misuse?
```

The diagnostics already supports this idea: every `(game, pass)` row has a movie/play-through artifact. The notebook should expose those movies directly through an interactive dropdown + play button.

## Recommended experiment sequence

### P0 — Protect baselines

- Keep old gated-BFS best score as historical fallback.
- Do not overwrite or discard deterministic baseline artifacts.
- Treat Duck `0.84` as the new active Kaggle baseline.

### P1 — Understand the notebook and harness

Create a notebook-reading map:

```text
1. Kaggle/TAAF setup and dataset path mapping
2. vLLM wheelhouse installation
3. Qwen model server startup
4. environment variable setup
5. benchmark object construction
6. solver/harness configuration
7. action/state interface
8. diagnostics generation
9. benchmark.json / diagnostics.html artifacts
10. movie/replay output location
```

Deliverable:

```text
experiments/duck_harness_repro/notebook_logic_map.md
```

### P2 — Add replay viewer

Add a safe post-run notebook cell that:

- loads `/kaggle/working/benchmark.json`,
- lists games sorted by score and levels,
- finds the corresponding movie/play-through HTML files,
- provides a dropdown for game selection,
- adds a play button,
- displays movie HTML inline,
- falls back to manual `GAME_ID` mode if widgets are unavailable.

Deliverable:

```text
notebooks or experiments/duck_harness_repro/duck_replay_viewer_cell.py
```

### P3 — Trace review before changes

Review strongest progress games first:

```text
ft09, tn36, sc25, tu93, lp85, sb26, ka59, lf52, vc33
```

Review zero-score failure games separately:

```text
cd82, cn04, dc22, g50t, ls20, m0r0, r11l, s5i5, sk48, tr87, wa30
```

Deliverable:

```text
experiments/duck_harness_repro/per_game_duck_trace_review.md
experiments/duck_harness_repro/duck_vs_gated_bfs_comparison.csv
```

### P4 — Only then run controlled variants

Do not immediately rewrite prompts/model/harness. First variant candidates after trace review:

| Variant | Description | Risk | Why test |
|---|---|---:|---|
| EXP-DUCK-002 | Targeted replay/trace diagnostics only | Low | Learn mechanics and failure modes |
| EXP-DUCK-003 | Shorter token cap / earlier give-up policy | Medium | Reduce wasted tokens on doomed games |
| EXP-DUCK-004 | World-model compaction / better carryover | Medium | Help cross-level generalization |
| EXP-DUCK-005 | Segmentation/object summary compaction | Medium | Reduce context pollution and improve perception |
| EXP-DUCK-006 | Gated-BFS fallback when LLM stalls | Medium/High | Combine action-cheap search with LLM reasoning |

Initial recommendation:

```text
Run EXP-DUCK-002 first. No solver changes. Add viewer + trace extraction + notebook logic map.
```

## Codex implementation plan

Use a new branch:

```text
exp/duck-replay-trace-review-2026-07-06
```

Codex should make a minimal, artifact-focused patch:

```text
1. Add replay viewer cell/script.
2. Add notebook logic map markdown.
3. Add per-game trace review template.
4. Add duck-vs-baseline comparison CSV template.
5. Update experiment tracker if needed.
6. Do not change solver behavior yet.
```

Validation rule:

```text
No claim of improvement until a Kaggle public score or public-game benchmark diagnostic supports it.
```

## Files changed in this ChatGPT/GitHub update

Updated:

```text
docs/experiment_tracker.md
```

Created:

```text
session_notes/2026-07-06_duck_baseline_strategy_and_replay_plan.md
codex_prompts/2026-07-06_duck_replay_trace_review.md
```

## Current best score/result

```text
Current best Kaggle public score: 0.84
Submission: ARC-AGI-3 — Duck Public Notebook Reproduction Work - Version 1
Architecture: Tufa Duck public notebook reproduction / Qwen3.6-27B-FP8 via local vLLM
Status: Succeeded
```

## Next session plan

1. Open the Duck notebook in repo/Kaggle context.
2. Add and test replay viewer cell.
3. Map notebook logic top-to-bottom.
4. Watch movies for `ft09`, `tn36`, `sc25`, `tu93`, `lp85`, `sb26`, `ka59`, `lf52`, `vc33`.
5. Create per-game trace notes.
6. Compare Duck behavior vs old gated-BFS on same games.
7. Choose exactly one controlled improvement variant.
8. Submit only after local/public diagnostic evidence.
