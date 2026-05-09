# 2026-05-09 ARC-AGI-3 session start

## Objective

Start the 2026-05-09 ARC-AGI-3 session from the 2026-05-08 closeout state, ingest the newly attached EXP-003C artifacts, and decide the next controlled step.

## K-12 summary

Yesterday we learned that ACTION6 is a risky button: it sometimes helps, but it also causes many no-ops and game-over events. Today the missing EXP-003C result files were attached, so we can compare EXP-003C, EXP-003D, and EXP-003E properly before building another experiment.

## Current baseline

Public baseline remains:

```text
EXP-003B public score: 0.12
EXP-003B local score: 0.48491096178440257
EXP-003B local levels: 6 / 183
```

Do not overwrite or demote EXP-003B unless a later experiment beats it by validated local and/or public evidence.

## Previous session closeout recap

From the 2026-05-08 closeout:

```text
EXP-003C score: 0.4819505213 | levels: 7 / 183 | ACTION6: 8,667 | RESET: 288
EXP-003D score: 0.4809739507 | levels: 6 / 183 | ACTION6: 7,876 | RESET: 304
EXP-003E score: 0.4818242866 | levels: 7 / 183 | ACTION6: 8,086 | RESET: 303
```

Decision at closeout:

```text
Do not submit EXP-003C, EXP-003D, or EXP-003E.
Keep EXP-003B as the public baseline.
```

## Newly attached EXP-003C artifacts

The user attached the EXP-003C artifact bundle that was missing/full-limited during the prior session:

```text
artifact_manifest (6).csv
exp003c_scorecard_summary (1).json
exp003c_scorecard_by_environment (1).csv
exp003c_scorecard_by_tag (1).csv
exp003c_run_results (1).csv
exp003c_run_details (1).json
exp003c_action_counts (1).json
exp003c_policy_counts (1).json
exp003c_effect_summary_by_game (1).csv
exp003c_action_prior_by_game (1).json
```

This satisfies the artifact-handling rule recorded on 2026-05-08.

## EXP-003C artifact confirmation

Scorecard summary:

```text
EXP-003C local score: 0.481950521305291
Levels: 7 / 183
Actions: 25,000
Environments completed: 0 / 25
```

Policy counts:

```text
fallback: 24,296
progress_prior_guardrailed: 416
reset: 288
```

Action counts:

```text
ACTION1: 3,007
ACTION2: 3,032
ACTION3: 3,298
ACTION4: 3,345
ACTION5: 1,697
ACTION6: 8,667
ACTION7: 1,666
RESET: 288
```

## Interpretation

EXP-003C remains a useful near-tie diagnostic:

- It is only slightly below EXP-003B local score.
- It improves level count from `6 / 183` to `7 / 183`.
- It sharply reduces progress-prior usage compared with EXP-003B.
- It does not solve ACTION6 overuse.
- ACTION6 is still too central and too risky to ban globally.

The attached artifacts confirm the previous provisional conclusion, now with reproducibility support.

## Linear issue

Created Linear issue:

```text
KAG-14 — 2026-05-09 ARC-AGI-3 session: artifact comparison and EXP-003F planning
```

Status:

```text
In Progress
```

## Next session plan

P0 — Baseline protection:

- Keep EXP-003B as public baseline.
- Do not submit EXP-003C/D/E.

P1 — Artifact comparison:

- Build or run an offline comparison notebook for EXP-003C, EXP-003D, and EXP-003E.
- Compare per-game levels, resets, ACTION6 count, no-op rate, game-over rate, and utility.
- Identify games where ACTION6 helped versus games where ACTION6 mostly harmed.

P2 — Candidate EXP-003F:

Use EXP-003E diagnostics but disable no-op-based ACTION6 throttle.

Proposed EXP-003F rule:

```text
Throttle ACTION6 only when local ACTION6 GAME_OVER rate is bad
and no recent ACTION6 level_delta occurred.
```

Rationale:

- EXP-003D showed no-op throttling was too blunt.
- EXP-003E softened no-op throttling and recovered 7 levels, but still did not beat EXP-003B.
- GAME_OVER-only throttling may reduce damaging ACTION6 behavior without suppressing useful exploration as aggressively.

## Validation gate for EXP-003F

Submit EXP-003F only if one of these holds:

1. It beats EXP-003B local score `0.48491096178440257`; or
2. It is very close to EXP-003B, preserves `7 / 183` levels, and shows clearly safer ACTION6 game-over/reset behavior.

Minimum artifacts required before analysis:

```text
artifact_manifest.csv
*_scorecard_summary.json
*_scorecard_by_environment.csv
*_scorecard_by_tag.csv
*_run_results.csv
*_run_details.json
*_action_counts.json
*_policy_counts.json
*_policy_action_counts.json
*_effect_summary_by_game.csv
*_action_diagnostics_by_game.csv
*_action_prior_by_game.json
*_action6_throttle_counts.json, if applicable
*_action6_throttle_by_game.csv, if applicable
```

## Current recommendation

Do not jump directly to submission. First compare EXP-003C/D/E artifacts side-by-side, then implement EXP-003F only if the artifact comparison supports GAME_OVER-only throttling.
