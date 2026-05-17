# Experiment Tracker Addendum — 2026-05-17

This addendum records the EXP-005/EXP-005A result and the EXP-005B follow-up plan without rewriting the main `docs/experiment_tracker.md` table.

| ID | Date | Branch/Notebook | Agent | Change | Local Result | Kaggle Result | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| EXP-005 | 2026-05-15/16 | `notebooks/01_exploration/exp005_minimal_source_bfs_baseline.ipynb` | Minimal source-BFS + visible-pixel fallback | First clean source-code BFS reproduction: source lookup, direct game instantiation, effective-action scan, bounded BFS, online replay, simple fallback | Not locally validated beyond commit-mode mechanics | Public score: `0.08`; Version 8; succeeded | Completed / public regression / scaffold retained | Proved the notebook can score, but regressed versus EXP-003B `0.12`. Use as source-BFS scaffold, not baseline. |
| EXP-005A | 2026-05-16/17 | `notebooks/01_exploration/exp005a_bfs_diagnostics_hidden_hash.ipynb` | BFS diagnostics + hidden-state hash | Added hidden scalar probing, frame+hidden-field BFS state hash, and JSON diagnostic artifacts | Not locally validated beyond commit-mode mechanics | Public score: `0.17`; Version 9; succeeded | Completed / new public baseline | New best public score. Validates planner/BFS direction and hidden-state-aware hashing. Next: improve effective-action scanning rather than fallback recovery. |
| EXP-005B | 2026-05-17 | `notebooks/01_exploration/exp005b_stronger_effective_action_scan.ipynb` | Stronger effective-action scan + hidden hash | EXP-005A base plus connected-component/object-based click candidates and richer per-method scan JSON diagnostics | Pending | Pending | Created / awaiting validation | Goal is planner growth toward `0.4+`, not public-score recovery via EXP-003B fallback. |

Current validated best after this addendum:

```text
EXP-005A / Version 9 public score: 0.17
Previous best: EXP-003B / V6 public score: 0.12
```

Next target:

```text
EXP-005B — stronger effective-action scan
```

Primary diagnostics to inspect after EXP-005B:

- Source load success rate.
- `scan.generated_by_method`.
- `scan.effective_by_method`.
- `scan.unique_effects`.
- `scan.deduped`.
- Hidden fields detected.
- BFS solved-level count.
- BFS replay count.
