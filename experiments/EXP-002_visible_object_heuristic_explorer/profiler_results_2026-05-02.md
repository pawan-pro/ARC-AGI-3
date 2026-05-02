# EXP-002 Profiler Results — 2026-05-02

## Result

The EXP-002 profiler notebook completed successfully on the 25 public demo tasks.

Key outputs:

- n_games: 25
- n_probe_rows: 184
- coarse family counts:
  - keyboard_click: 11
  - click: 8
  - keyboard: 6
- one_step_progress_games: none

## Task-family implication

The public tasks are not one homogeneous environment. A single random policy is inefficient. The next scoring notebook should route by action family:

1. keyboard_click: movement plus object-centered click policy
2. click: object-centered click search policy
3. keyboard: movement-only exploration and no-op suppression

## Responsive-game findings

Movement-responsive games:

- sk48-d8078629
- m0r0-492f87ba
- bp35-0a0ad940
- cn04-2fe56bfb
- dc22-fdcac232
- tu93-0768757b
- ka59-38d34dbb
- wa30-ee6fef47
- sp80-589a99af
- ar25-0c556536
- cd82-fb555c5d
- re86-8af5384d
- ls20-9607627b
- tr87-cd924810
- g50t-5849a774

Click-responsive games:

- tn36-ef4dde99
- bp35-0a0ad940
- cn04-2fe56bfb
- dc22-fdcac232
- ka59-38d34dbb
- vc33-5430563c
- lf52-271a04aa
- r11l-495a7899
- sp80-589a99af
- sb26-7fbdac44
- cd82-fb555c5d
- s5i5-18d95033
- su15-1944f8ab

## Important caution

The profiler used one-step probes. No game showed one-step level progress, which is expected. These games require multi-step exploration and planning.

## EXP-002 scoring-notebook design decision

Do not build a task-specific ls20 solver. Build a routed policy:

- If click-only: click candidate object centers repeatedly with novelty/no-op suppression.
- If keyboard-only: use directional movement exploration toward small components, avoid no-op loops.
- If keyboard_click: combine movement toward components with occasional object-centered clicks.
- Avoid ACTION7/undo by default.
- Preserve EXP-001 random visible-pixel fallback when uncertain.

## Next implementation

Create or update:

- notebooks/01_exploration/exp002_visible_object_heuristic_explorer.ipynb

Validation gate before submission:

- local score >= 0.21238458620043624
- local levels >= 7 / 183
- no runtime failure
- submission.parquet created

If local score falls below EXP-001, do not submit.
