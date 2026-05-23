# Experiment Tracker Addendum — 2026-05-23

This addendum records the scored EXP-005C and EXP-005D results and the resulting decision matrix. It should be read after `docs/experiment_tracker_2026-05-17_exp005a_exp005b_addendum.md`.

| ID | Date | Branch/Notebook | Agent | Change | Local Result | Kaggle Result | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| EXP-005C | 2026-05-21 | `notebooks/01_exploration/exp005c_level_transfer_from_exp005a.ipynb` | Level-to-level transfer + hidden hash | EXP-005A backbone plus direct replay and object-offset transfer from previous-level solutions; no EXP-005B broad scan | Visible notebook produced placeholder artifacts only | Public score: `0.10`; Version 12; succeeded | Completed / public regression | Transfer did not validate. Do not continue EXP-005C2 until scoring-time transfer diagnostics prove reliable benefit. |
| EXP-005D | 2026-05-22/23 | `notebooks/01_exploration/exp005d_deterministic_exp005a_control.ipynb` | Deterministic EXP-005A replay control | EXP-005A backbone with hidden-state hash and simple scan; wall-clock seed replaced by deterministic MD5 game/level seed; no broad scan; no transfer | Visible notebook produced placeholder artifacts only | Public score: `0.10`; Version 13; succeeded | Completed / deterministic control failed | Did not reproduce EXP-005A `0.17`. Investigate fallback stability and BFS/fallback attribution before adding planner features. |

Current validated best remains:

```text
EXP-005A / Version 9 public score: 0.17
```

Updated source-BFS ladder:

```text
EXP-005:  0.08  minimal source-BFS
EXP-005A: 0.17  hidden-state-aware BFS, current best
EXP-005B: 0.09  broader scan regression
EXP-005C: 0.10  transfer regression
EXP-005D: 0.10  deterministic replay control regression
```

Decision rule applied:

```text
If EXP-005D < 0.17:
    EXP-005A score may depend on stochastic fallback.
    Investigate fallback stability before planner feature work.
```

Actual decision:

```text
Do not promote EXP-005D.
Do not start EXP-005E gated scan yet.
Do not continue EXP-005C2 yet.
Keep EXP-005A V9 as current public baseline.
Create a scoring-time attribution diagnostic next.
```
