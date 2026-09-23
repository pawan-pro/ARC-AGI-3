# Shutdown-only derivative

## Version 3 correction — 2026-09-11

Version 2 failed before gameplay: the inserted patch cell ran before BUNDLE_DIR was defined. Moved it immediately after bundle discovery, before solver setup. Also corrected teardown dispatch: the upstream command contains an environment-variable path, so literal absolute-path replacement could not reliably select the patched helper. Dispatch now uses the interpreter and patched helper as an explicit argument list with shell=False and check=True.

Verified dependency order, compiled every code cell, executed the real patch against the downloaded source and passed its self-tests, and checked the actual dispatch AST resolves to the patched helper. Full GPU execution remains pending. Kaggle accepted Version 3; submit only Version 3 after runtime validation and duplicate checking. Version 2 must not be submitted.

Kaggle accepted Version 2 on 2026-09-09. Official submission is not yet made.

Version 1 saved an offline mean of 7.291313041679922 over 25 games, 37 levels. Its final CPU ownership scan was empty, but NVIDIA still listed a historical PID without process details. This suggests delayed driver cleanup; it does not prove cleanup eventually succeeded.

The derivative adds up to 10 seconds of GPU-drain polling (plus bounded query latency), preserves the survivor and artifact gates, and makes teardown subprocess failures fatal instead of ignored. The subprocess timeout is 60 seconds. Model, gameplay, scorer, and attached inputs are unchanged.

Local validation: all code cells compile; upstream teardown self-tests pass; simulated delayed cleanup clears; simulated persistent survivor remains blocked; exact notebook diff verified. GPU execution remains to be validated on Kaggle.

Next: download Version 2 outputs separately, verify shutdown_ok and all 25 expected games with finite scores and real actions, reject crashed/cancelled games, check duplicate submissions, then submit exact Version 2 once through the code-competition workflow. Keep offline and official scores separate. Do not submit Version 1.
