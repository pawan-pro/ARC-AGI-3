# Solver Tool Matrix Strategy

Date: 2026-07-10

## Core Idea

Duck should not solve every puzzle cell by free-form reasoning. The LLM should recognize the puzzle family, then use a small deterministic helper when the board matches that family.

This is the current working model:

```text
LLM = scout / manager
helper tools = calculators / hands
stall policy = safety brake
```

The LLM still matters because it can inspect unfamiliar boards, infer a likely mechanic, and decide what to try next. The fixed helpers matter because they can do repetitive bookkeeping and exact clicking much more reliably than an LLM thinking through every cell.

## Tool Matrix

| Puzzle pattern | Helper/tool | Applicability check | LLM role |
|---|---|---|---|
| Toggle grid | Compute cells to toggle | Board has clickable cells that flip between two states | Identify cells, colors, and whether toggling is the mechanic |
| Mask/clue cells | Decode local masks into candidate target boards | Board has special cells containing tiny local patterns | Recognize clue cells and decide whether candidates are plausible |
| Maze/path | BFS / shortest-path search | Board has avatar, walls, target, and movement actions | Identify player, blockers, goals, and action mapping |
| Palette/fill | Map source colors to target regions | Board has palette-like controls and fillable regions | Infer color mapping and finish/submit behavior |
| Object matching | Compare repeated shapes/hashes | Board has repeated objects or templates | Decide which object relation is likely relevant |
| Submit/finish | Safe submit/finish probe | Board has a stable completed-looking state and a candidate finish control | Decide when enough evidence supports submitting |
| Stall loop | Stop after no level progress | Actions continue but score/level does not move | Preserve time and tokens for other games or fallback paths |

## What ft09 Proved

The `ft09` helper is the first successful instance of this pattern.

Before the helper:

```text
stall run: ft09 = 2/6 levels, actions_per_level = [29, 7, 90, 0, 0, 0]
```

After the helper:

```text
ft09-helper run: ft09 = 3/6 levels, actions_per_level = [9, 7, 32, 172, 0, 0]
winning level-3 helper rule: white_is_center + parity
```

This does not mean the exact `ft09` mask helper is universal. It means the tool-matrix approach is valid when the helper has a good applicability check.

## Generalization Rule

A helper should be treated as general only across levels/games that match its preconditions.

Good:

```text
If the board has two-color toggle cells plus special 3x3 mask cells, try the mask/toggle helper.
```

Bad:

```text
Always run the ft09 helper on every game.
```

## Next Work

1. Implement `EXP-DUCK-004`: generalized ft09 mask-cycle helper.
2. Detect cell centers and special mask cells instead of hardcoding level-3 coordinates.
3. Support multi-color cycles such as `b -> R -> O -> b`, not only two-color toggles.
4. Keep controlled stall as a safety brake, not as a scoring strategy.

## 2026-07-10 Level-4 Decision

`ft09` level 4 is the same broad mask/toggle family, not a separate mechanic.

The reason is simple:

```text
normal cells are still clicked
clicks still change cell colors
special cells still contain white/gray clue masks
progress still appears to require matching a target color pattern
```

The new difficulty is that level 4 is a multi-color cycle:

```text
b -> R -> O -> b
```

So the next step is to generalize the existing helper rather than create an unrelated second helper.
