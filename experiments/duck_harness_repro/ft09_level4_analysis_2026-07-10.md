# ft09 Level-4 Analysis - 2026-07-10

Source run:

```text
artifacts/kaggle/duck_ft09_helper/latest/artifacts/ft09-0d8bbf25_p0_events.jsonl
artifacts/kaggle/duck_ft09_helper/latest/transcripts/ft09-0d8bbf25_p0.txt
```

## Result Being Explained

The `ft09-helper` run solved level 3 and then stalled on level 4:

```text
ft09-helper actions_per_level = [9, 7, 32, 172, 0, 0]
level 3 solved by helper rule: white_is_center + parity
level 4 consumed 172 actions without progress
```

## Level-4 Structure

Level 4 is the same broad puzzle family as level 3, not a separate mechanic.

Evidence:

```text
only action: MOUSE
normal cells are clickable color blocks
clicking a normal cell changes its color
special cells contain small white/gray/color masks
progress requires reaching a target color pattern
```

The difference is that level 4 is harder:

```text
level 3: two-color toggle-like board
level 4: multi-color/cycling board
```

Observed click cycle from the replay:

```text
b -> R
R -> O
O -> b
```

So level 4 is not just "toggle red/orange"; it is a three-state color cycle.

## Board Signature

Initial level-4 board has:

```text
normal color cells: mostly b
special clue cells: masks centered around (24,22), (24,38), and (40,30)
palette / reference colors near right edge: b, R, O
```

Representative special masks:

```text
center (24,22), center color O:
ggWWgg
ggOOgg
ggWWgg

center (24,38), center color b:
ggWWgg
ggbbgg
ggggWW

center (40,30), center color O:
WWgggg
ggOOgg
WWWWWW
```

## Decision

Generalize the mask/toggle helper. Do not create a completely separate helper yet.

Reason:

```text
level 4 shares the same clue-mask and click-cell family as level 3.
the missing abstraction is not a new solver; it is generalized detection and color-cycle handling.
```

## Required Generalization

The next helper should stop hardcoding level-3 geometry and instead detect:

```text
1. clickable normal cell centers
2. special mask/clue cells
3. available color cycle, inferred by one safe probe or by palette/reference colors
4. candidate target colors from white/gray mask rules
5. shortest click count from current color to target color under the cycle
```

For level 4, candidate generation should support:

```text
white_is_center
gray_is_center
white_is_palette_color
gray_is_palette_color
majority / parity / color-wins / last-writer overlap rules
```

## Next Implementation

Create `EXP-DUCK-004`: generalized ft09 mask-cycle helper.

Acceptance gate:

```text
1. keep level 3 solved
2. improve level 4 from 0 progress
3. reduce level-4 waste below 172 actions if level 4 is not solved
```

