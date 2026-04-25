# ARC-AGI-3 Practical Rules Constraints

## Purpose

This file converts the ARC-AGI-3 competition rules into practical project constraints for development, experimentation, collaboration, submission, and reproducibility.

## 1. Submission discipline

- Maximum Kaggle submissions per day: 5.
- Maximum final submissions for judging: 2.
- Every Kaggle submission should be treated as an experiment artifact.
- Each submission should be linked to:
  - branch or commit
  - notebook path
  - agent name/version
  - experiment notes
  - logs or recordings
  - public leaderboard score
  - change summary versus previous submission

## 2. Team and collaboration constraints

- Maximum team size: 8.
- Use only one official Kaggle account/team identity.
- Do not use proxy accounts or duplicate accounts.
- Do not privately share competition code or data with anyone outside the official Kaggle team.
- If interns, researchers, or collaborators work on private competition materials, they should be handled as official team members or kept away from private solution code/data.
- Public sharing should be done through Kaggle forums/notebooks or other fully public open-source-compatible channels.

## 3. Reference-material handling

- Keep `x_competition_files/` as the official/reference-material zone.
- Do not casually modify files inside `x_competition_files/`.
- Working code, experiments, notebooks, logs, and notes should live outside `x_competition_files/`.
- Any derived work should clearly reference the source document, notebook, log, or leaderboard snapshot used.

## 4. External data, tools, and models

- Prefer official competition files first.
- External data/models/tools should be:
  - publicly available
  - equally accessible to competitors
  - reasonably low-cost or minimal-cost
  - legally usable under their licenses
  - compatible with Kaggle notebook execution constraints
- Avoid private datasets, paid APIs, or closed/proprietary services in the final submission path.
- Document every dependency and data/model source used.

## 5. Kaggle notebook constraints

- Submissions must be made through Kaggle notebooks.
- Internet must be disabled for the submitted notebook.
- Runtime must stay within the competition notebook limit.
- The submission file is generated automatically if the agent takes action on the games.
- Maintain at least one clean baseline notebook that is known to submit successfully.

## 6. Reproducibility requirements

Maintain enough information to reproduce every meaningful result:

- exact notebook/file path
- branch and commit hash
- dependency list
- environment notes
- model/data provenance
- experiment configuration
- logs/recordings
- local evaluation result, if available
- Kaggle public leaderboard result, if submitted

Avoid claiming improvement unless it is supported by logs, local evaluation, or Kaggle submission results.

## 7. Winner/open-source obligations

If the team becomes prize-eligible, expect to provide open-source/reproducible materials, including:

- final model/software code
- inference code
- training or tuning code, if applicable
- documentation
- dependency and environment details
- architecture/methodology explanation
- preprocessing details
- hyperparameters/configuration
- instructions for reproducing the submitted result

Do not build the final system around components that cannot be disclosed, licensed, or reproduced.

## 8. Leaderboard and final-submission implications

- Public leaderboard is useful for iteration but should not be overfit.
- Private leaderboard determines final standing.
- Ties may favor earlier submissions, so stable strong submissions should not be delayed until the final hours.
- Keep diverse final-candidate submissions when possible, such as:
  - robust conservative agent
  - higher-upside experimental agent

## 9. Milestone planning

Important dates:

- Milestone 1: 2026-06-30
- Milestone 2: 2026-09-30
- Entry/team merger deadline: 2026-10-26
- Final submission deadline: 2026-11-02
- Winners announcement: 2026-12-04

Operational implications:

- Prepare a public/open-source-ready notebook before Milestone 1.
- Prepare a stronger public/open-source-ready notebook before Milestone 2.
- Preserve clean baselines and experiment artifacts throughout the competition.

## 10. Project workflow checklist

For each experiment:

1. Define the hypothesis.
2. Create or update the branch/notebook.
3. Run locally or in Kaggle as appropriate.
4. Save logs and recordings.
5. Record score/result.
6. Compare against the clean baseline.
7. Update session notes.
8. Decide whether the change graduates, is archived, or needs follow-up.

## Current operating rule

The project should prioritize reproducibility, clean baselines, and measurable progress over speculative rewrites.
