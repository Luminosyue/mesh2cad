#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    out = Path("artifacts/synthetic_high_mesh_two_case_v1/cadfit_command_audit.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    help_run = subprocess.run([sys.executable, "run_pipeline.py", "--help"], capture_output=True, text=True)
    text = "\n".join([
        "# CADFit Command Audit",
        "",
        "SKETCH_PRIOR_ENABLED=false",
        "PRIOR_MODE=no_prior",
        "",
        "CADFit entry: `run_pipeline.py`",
        "",
        "Input requirement: non-recursive folder containing one or more `.stl` files.",
        "This demo creates a per-case isolated input folder containing only `input_high_mesh.stl`.",
        "",
        "Output option: `--output-folder <case_output_dir>`",
        "Iteration option: `--max-iterations 1`",
        "Skip existing: `--skip-existing`",
        "Single file behavior: use input folder with one STL plus `--limit 1`.",
        "Inner workers: set `CADFIT_INNER_WORKERS=1` in subprocess environment.",
        "Sketch prior: not enabled; no `--filter-sketches` flag is passed.",
        "",
        "Actual command template:",
        "```bash",
        "CADFIT_INNER_WORKERS=1 python run_pipeline.py <isolated_input_dir> --output-folder <case_output_dir> --max-iterations 1 --limit 1 --skip-existing",
        "```",
        "",
        "Observed help/stdout excerpt:",
        "```text",
        (help_run.stdout + help_run.stderr)[-4000:],
        "```",
    ])
    out.write_text(text, encoding="utf-8")
    print("CADFIT_COMMAND_AUDIT=" + str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
