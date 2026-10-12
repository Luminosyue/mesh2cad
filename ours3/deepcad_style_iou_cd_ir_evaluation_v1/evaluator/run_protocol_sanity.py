from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

from deepcad_style_cd_v1 import chamfer_squared_symmetric, deterministic_cd
from deepcad_style_invalid_classifier_v1 import classify_prediction
from solid_iou_v1 import solid_iou


def mesh_box(x=1.0, y=1.0, z=1.0, center=(0, 0, 0)):
    m = trimesh.creation.box((x, y, z))
    m.apply_translation(center)
    return m


def main(out_path):
    results = {}
    unit = cq.Workplane("XY").box(1, 1, 1)
    results["iou_gt_gt"] = solid_iou(unit, unit)
    results["iou_disjoint"] = solid_iou(unit, cq.Workplane("XY").box(1, 1, 1).translate((2, 0, 0)))
    results["iou_half_overlap"] = solid_iou(unit, cq.Workplane("XY").box(1, 1, 1).translate((0.5, 0, 0)))

    a, b = mesh_box(), mesh_box(center=(0.2, 0, 0))
    results["cd_identical"] = chamfer_squared_symmetric(np.zeros((2000, 3)), np.zeros((2000, 3)))
    results["cd_translated"] = chamfer_squared_symmetric(a.vertices[:200], b.vertices[:200])
    cd1 = deterministic_cd(a, b, "toy_case")
    cd2 = deterministic_cd(a, b, "toy_case")
    results["cd_deterministic"] = {"first": cd1, "second": cd2, "equal": cd1 == cd2}

    valid = cq.Workplane("XY").box(1, 1, 1).val()
    invalid_cases = {}
    for name, kwargs in {
        "valid": dict(native_program_valid=True, cad_exec_success=True, shape=valid, surface_sampling_success=True),
        "empty_shape": dict(native_program_valid=True, cad_exec_success=True, shape=None, surface_sampling_success=True),
        "exec_failure": dict(native_program_valid=True, cad_exec_success=False, shape=None, surface_sampling_success=False),
        "sampling_failure": dict(native_program_valid=True, cad_exec_success=True, shape=valid, surface_sampling_success=False),
    }.items():
        invalid_cases[name] = classify_prediction(**kwargs)
    results["ir_cases"] = invalid_cases

    checks = {
        "iou_gt_gt": abs(results["iou_gt_gt"]["iou"] - 1.0) < 1e-9,
        "iou_disjoint": abs(results["iou_disjoint"]["iou"]) < 1e-9,
        "iou_half_overlap": abs(results["iou_half_overlap"]["iou"] - (1 / 3)) < 1e-6,
        "cd_identical": results["cd_identical"] == 0.0,
        "cd_deterministic": results["cd_deterministic"]["equal"],
        "ir_valid": invalid_cases["valid"][0] is False,
        "ir_empty": invalid_cases["empty_shape"][0] is True,
        "ir_exec": invalid_cases["exec_failure"][0] is True,
        "ir_sampling": invalid_cases["sampling_failure"][0] is True,
    }
    results["checks"] = checks
    results["all_pass"] = all(checks.values())
    Path(out_path).write_text(json.dumps(results, indent=2))
    print(json.dumps({"all_pass": results["all_pass"], "checks": checks}, indent=2))
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
