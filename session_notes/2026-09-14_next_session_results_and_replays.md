# Next session: official score and deeper replay comparison

User deferred further comparison work to the next session.

1. Check existing official submission 56228748 for exact notebook Version 3; last verified PENDING. Do not submit a duplicate.
2. Compare original and corrected ft09 and re86 trajectories in depth: earliest action divergence, level transitions, repeated no-effect actions, available timing and sampling configuration. Separate observed differences from causal hypotheses.
3. Decide the next controlled experiment together after reviewing the evidence. An unchanged private repeat was discussed but has NOT been launched; do not assume it exists or launch automatically from this handoff.

Offline comparison: original mean 7.2913, 37 levels, 3179 actions; corrected mean 5.8809, 32 levels, 3731 actions. Eight games improved, twelve regressed, five were unchanged in score. Offline results are not leaderboard scores.

Replay download retry succeeded: both ft09 and re86 event files exist under experiments/EXP-DUCK-039_qwen38_anim_reproduction/output_v3/artifacts; original files are under output_v1/artifacts. Deeper replay analysis is not yet done.

The readable comparison artifact is unfinished: comparison/artifact.json exists, but HTML packaging failed because manifest.version was absent. Do not claim report.html is delivered or validated. Resume packaging or choose a user-approved simpler artifact next session.
