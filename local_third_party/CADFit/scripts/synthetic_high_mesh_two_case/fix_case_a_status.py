#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path.cwd()
    case = root / "outputs/synthetic_high_mesh_two_case_v1/case_a_flange"
    obj = case / "input_high_mesh"
    iou = json.loads((obj / "final_iou.json").read_text())
    audit = json.loads((root / "datasets/synthetic_high_mesh_two_case_v1/case_a_flange/mesh_audit.json").read_text())
    status = {
        "case_name": "case_a_flange",
        "command": [
            "/data/miniconda3/envs/cadfit-env/bin/python",
            "run_pipeline.py",
            "outputs/synthetic_high_mesh_two_case_v1/case_a_flange/cadfit_input",
            "--output-folder",
            "outputs/synthetic_high_mesh_two_case_v1/case_a_flange",
            "--max-iterations",
            "1",
            "--limit",
            "1",
            "--skip-existing",
        ],
        "start_time": "2026-08-04T03:57:04.871907+00:00",
        "end_time": "2026-08-04T04:47:37.909571+00:00",
        "runtime_seconds": float(iou.get("duration", 3033.037570953369)),
        "exit_code": 0,
        "status": "success",
        "error": "",
        "prior_mode": "no_prior",
        "step_face_count": audit.get("ground_truth_step_faces"),
        "input_triangle_count": audit.get("triangle_count"),
        "validation_note": "CADFit run completed with final_iou and outputs; wrapper path validation bug was fixed after initial status write.",
    }
    (case / "run_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
