# 2026-09-07 — Stability Repeat and Visual Dashboard Handoff

## Current verified baseline

- Current official best: `EXP-DUCK-038`, public score `1.12`.
- Previous official best: `EXP-DUCK-024`, public score `1.11`.
- The `1.306` / `1.31` value from EXP-DUCK-038 is the offline public-game mean
  and is not directly comparable with the competition leaderboard score.

## Stability repeat launched

The frozen EXP-DUCK-038 notebook was revalidated before launch:

- all 9 code cells compiled;
- notebook SHA-256 remained unchanged;
- AGI_8 repeated-no-effect directional guard remained present;
- AGI_9 analyzer yield remained 90 seconds;
- no competition submission call was present.

The exact artifact was pushed as Version 2 of the existing private Kaggle kernel:

```text
jatalepawan/arc3-duck-agi9-public-repro-20260903
```

Purpose: measure run-to-run stability without mixing in a new code change.
This is a private 25-public-game evaluation, not a competition submission.
Do not submit it for official scoring until the output is complete and validated.

## Tomorrow's primary action item — visual reasoning dashboard

Build a local replay dashboard from the downloaded EXP-DUCK-038 Version 1 artifacts.
The first useful version should provide:

1. game selector and per-game summary;
2. chronological action timeline with play, pause, previous, and next controls;
3. board image before and after each action;
4. highlighted pixel/object changes;
5. chosen action and button/click coordinates;
6. logged world-model/plan summary and Python/tool activity;
7. score, level, reward, elapsed time, token use, and remaining budget;
8. flags for repeated ineffective moves, game-over resets, and stalls.

Use logged model outputs and concise derived summaries. Do not describe the
dashboard as exposing a model's complete private chain of thought.

Potential starting artifacts already downloaded under the isolated experiment
output include `benchmark.json`, per-game event JSONL, viewer-data JSON, prompt
logs, diagnostic HTML, and generated game movies.

## Next experimental sequence

1. Validate Version 2 and compare its 25-game aggregate and per-game results
   against Version 1.
2. If the baseline is sufficiently stable, create controlled arms:
   - AGI_8 on / AGI_9 off;
   - AGI_8 off / AGI_9 on;
   - both off as the control, if safely recoverable.
3. Do not make another competition submission without explicit authorization
   after reviewing the completed candidate.
