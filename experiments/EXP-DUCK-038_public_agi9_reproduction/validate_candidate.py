#!/usr/bin/env python3
"""Static, non-executing validation for the exact public AGI_9 notebook copy."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "lb-1-17-arc-agi-3-qwen3-6-duck-full-code.ipynb"
UPSTREAM_METADATA = ROOT / "upstream-kernel-metadata.json"
RUN_METADATA = ROOT / "kernel-metadata.json"
EXPECTED_NOTEBOOK_SHA256 = "015443fd998f5bac097211fcd8372a30c1ae3abdc4883b11be3535301a42d870"
EXPECTED_UPSTREAM_ID = "yw8837/lb-1-17-arc-agi-3-qwen3-6-duck-full-code"
EXPECTED_DATASETS = {
    "driessmit1/arc3-vllm-h100-wheelhouse-v3",
    "jeroencottaar/taaf-kaggle-source",
    "driessmit1/vrfai-qwen3-6-27b-fp8-hf-snapshot",
}


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def require_once(text: str, needle: str) -> None:
    count = text.count(needle)
    assert count == 1, f"expected exactly one {needle!r}; found {count}"


def main() -> None:
    notebook_bytes = NOTEBOOK.read_bytes()
    actual_hash = hashlib.sha256(notebook_bytes).hexdigest()
    assert actual_hash == EXPECTED_NOTEBOOK_SHA256, (actual_hash, EXPECTED_NOTEBOOK_SHA256)

    notebook = json.loads(notebook_bytes)
    upstream = json.loads(UPSTREAM_METADATA.read_text(encoding="utf-8"))
    run = json.loads(RUN_METADATA.read_text(encoding="utf-8"))

    assert upstream["id"] == EXPECTED_UPSTREAM_ID
    assert set(upstream["dataset_sources"]) == EXPECTED_DATASETS
    assert set(run["dataset_sources"]) == EXPECTED_DATASETS
    assert run["is_private"] is True
    assert run["enable_gpu"] is True
    assert run["enable_internet"] is False
    assert run["competition_sources"] == ["arc-prize-2026-arc-agi-3"]
    assert run["kernel_sources"] == []
    assert run["code_file"] == NOTEBOOK.name

    code_cells = [source_text(cell) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    assert len(code_cells) == 9
    code = "\n".join(code_cells)

    # Compile every code cell without executing downloaded code. Top-level await is intentional.
    for index, cell_code in enumerate(code_cells):
        try:
            compile(cell_code, f"{NOTEBOOK.name}:cell-{index}", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        except SyntaxError as exc:
            raise AssertionError(f"code cell {index} does not compile: {exc}") from exc

    require_once(code, "AGI_8 patch: repeated-no-effect batch guard active on exact AGI_1 runtime")
    require_once(code, "_LOCAL_ANALYZER_YIELD_SECONDS = 90.0")
    require_once(code, "assert bm.solver.concurrency == 28")
    require_once(code, "assert bm.solver.max_runtime_s_per_game == 7920")
    require_once(code, 'frozenset({"UP", "DOWN", "LEFT", "RIGHT"})')
    assert "KAGGLE_IS_COMPETITION_RERUN" in code
    assert "vrfai-qwen3-6-27b-fp8-hf-snapshot" in code
    assert "jeroencottaar/taaf-kaggle-source" in code
    assert "kaggle competitions submit" not in code.lower()
    assert "/api/v1/competitions/submissions" not in code.lower()

    print(
        json.dumps(
            {
                "status": "pass",
                "notebook_sha256": actual_hash,
                "code_cells_compiled": len(code_cells),
                "upstream_id": upstream["id"],
                "private_run_id": run["id"],
                "guard": "repeat-no-effect direction within batch",
                "analyzer_yield_seconds": 90,
                "competition_submission_call_found": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
