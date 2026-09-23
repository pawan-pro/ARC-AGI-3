# Next ARC session: results and attribution

User asked to be reminded of this agenda when the next session starts.

1. Check the corrected Qwen 3.8 Version 3 run and any validated official submission. Do not confuse offline scores with leaderboard scores. Score follow-up is configured in the task.
2. Once the corrected baseline runs cleanly, plan controlled ablations to explain the offline improvement; do not launch ablations until discussed next session.
3. Repeat the unchanged baseline to measure variance, then disable speculative decoding, vary GPU-memory settings separately, and compare quantization only if compatible weights and hardware permit.
4. A model-only comparison requires matching harness and serving settings; current Qwen 3.6 versus 3.8 results confound model and runtime changes.
5. Use a fixed small game set first, log scores, levels, latency, tokens where instrumentation is valid, and action counts. Compare equal-time and equal-action budgets; neither alone fully isolates reasoning quality. Confirm promising results across all 25 public games.
6. Review saved replay trajectories to select hypotheses. More tokens or moves do not guarantee better scores.

Latest verified state: Kaggle accepted Version 3 after correcting patch-cell order and explicit teardown dispatch. No new official score was verified during this session. Version 1 offline mean was 7.2913; last confirmed official best was 1.12.
