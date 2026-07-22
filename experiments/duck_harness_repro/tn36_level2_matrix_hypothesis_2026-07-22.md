# tn36 Level-2 Matrix Hypothesis - 2026-07-22

## Observation

After the validated seven-action level-1 helper, level 2 presents two 6x4 matrices:

- lower-left matrix on a gray field: read-only target;
- lower-right matrix on a white field: clickable editable copy.

Each cell is a three-pixel horizontal or vertical marker. Gray (`1`) and black (`5`)
are the two states. A separate 69-pixel blue object at `(58, 46)` is submit.

Initial target:

```text
BBBB
wwww
wwww
wwww
wwww
wwww
```

Initial editable matrix:

```text
wwww
wwww
wwww
wwww
wwww
wwww
```

## Trace evidence

Duck's first four level-2 actions clicked editable centers `(33,39)`, `(33,44)`,
`(33,49)`, and `(33,54)`. After those actions the editable matrix exactly matched
the target. Duck then clicked `(36,8)` instead of submit and spent another 252 actions
toggling, resetting, and probing without level progress.

## Controlled hypothesis

Copy every mismatched target cell to the editable matrix, then click submit. For the
observed board this is exactly five actions. The helper is gated by board dimensions,
panel backgrounds, all 48 triomino marker footprints, marker colors, and the exact
submit-component area/bounding box.

## Promotion gate

Run only tn36 with the validated seven-action level-1 helper followed by this
five-action level-2 plan. Accept only if action 12 advances to level 3 with zero model
tokens. Signature mismatch or failure must stop the isolated run, not invoke the LLM.
