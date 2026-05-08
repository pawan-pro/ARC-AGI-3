# EXP-003E — soft ACTION6 throttle
# Controlled wrapper over EXP-003D.
# Same diagnostics and throttle mechanism, softer ACTION6 no-op threshold.
# Do not submit before artifact analysis.

from pathlib import Path

BASE = Path("notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py")
if not BASE.exists():
    # Kaggle notebook fallback when only this file is copied into /kaggle/working.
    BASE = Path("/kaggle/working/exp003d_policy_action_diagnostics_action6_throttle.py")

if not BASE.exists():
    raise FileNotFoundError(
        "EXP-003E is a controlled wrapper over EXP-003D, but the EXP-003D source file was not found. "
        "Please make sure `notebooks/01_exploration/exp003d_policy_action_diagnostics_action6_throttle.py` "
        "is present in the repo checkout or copy it to /kaggle/working/."
    )

source = BASE.read_text()

replacements = {
    'EXP_ID = "EXP-003D"': 'EXP_ID = "EXP-003E"',
    'ACTION6_BAD_NOOP_RATE = 0.45': 'ACTION6_BAD_NOOP_RATE = 0.70',
    'ART = WORK / "exp003d_artifacts"': 'ART = WORK / "exp003e_artifacts"',
    '"EXP-003C refinement with policy-action diagnostics and local ACTION6 fallback throttle"': '"EXP-003D softening with ACTION6_BAD_NOOP_RATE=0.70"',
}

for old, new in replacements.items():
    if old not in source:
        raise RuntimeError(f"Expected replacement target not found in EXP-003D source: {old}")
    source = source.replace(old, new)

# Rename artifact prefixes and visible labels after changing the directory.
source = source.replace("exp003d_", "exp003e_")
source = source.replace("EXP-003D — policy-action diagnostics and local ACTION6 throttle", "EXP-003E — soft ACTION6 throttle")
source = source.replace("Diagnostic-first refinement of EXP-003C", "Controlled softening of EXP-003D")
source = source.replace("# EXP-003D local fallback ACTION6 throttle.", "# EXP-003E local fallback ACTION6 throttle: softer no-op threshold.")

compiled = compile(source, "exp003e_soft_action6_throttle_generated_from_exp003d.py", "exec")
exec(compiled, globals(), globals())
