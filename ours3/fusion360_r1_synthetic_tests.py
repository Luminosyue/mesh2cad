#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np

PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = PROJECT / "ours3/fusion360_reconstruction_expansion_v1"
sys.path.insert(0, str(PROJECT / "scripts/fusion360"))
sys.path.insert(0, str(PROJECT / "scripts"))

from fusion360_to_dsl import convert_file  # noqa: E402
from edge_aware_cad_planner_v1.cad_dsl import execute_dsl  # noqa: E402


def p(x, y, z=0.0):
    return {"type": "Point3D", "x": x, "y": y, "z": z}


def v(x, y, z):
    return {"type": "Vector3D", "x": x, "y": y, "z": z, "length": float(np.linalg.norm([x, y, z]))}


def rect_loop(cx, cy, w, h):
    xs = [cx - w / 2, cx + w / 2]
    ys = [cy - h / 2, cy + h / 2]
    pts = [p(xs[0], ys[0]), p(xs[1], ys[0]), p(xs[1], ys[1]), p(xs[0], ys[1])]
    return {
        "is_outer": True,
        "profile_curves": [
            {"type": "Line3D", "start_point": pts[0], "end_point": pts[1]},
            {"type": "Line3D", "start_point": pts[1], "end_point": pts[2]},
            {"type": "Line3D", "start_point": pts[2], "end_point": pts[3]},
            {"type": "Line3D", "start_point": pts[3], "end_point": pts[0]},
        ],
    }


def make_case(name, origin, x_axis, y_axis, z_axis, center, size, height, op="NewBodyFeatureOperation"):
    return {
        "metadata": {"synthetic": name},
        "timeline": [{"index": 0, "entity": "e0"}],
        "entities": {
            "s0": {
                "type": "Sketch",
                "transform": {"origin": p(*origin), "x_axis": v(*x_axis), "y_axis": v(*y_axis), "z_axis": v(*z_axis)},
                "profiles": {"p0": {"loops": [rect_loop(center[0], center[1], size[0], size[1])]}}
            },
            "e0": {
                "type": "ExtrudeFeature",
                "operation": op,
                "extent_type": "OneSideFeatureExtentType",
                "start_extent": {"type": "ProfilePlaneStartDefinition"},
                "extent_one": {"distance": {"value": height}, "taper_angle": {"value": 0.0}},
                "profiles": [{"sketch": "s0", "profile": "p0"}],
            },
        },
        "properties": {},
        "sequence": [],
    }


def expected_origin(origin, x_axis, y_axis, center):
    return (np.asarray(origin, dtype=float) + center[0] * np.asarray(x_axis, dtype=float) + center[1] * np.asarray(y_axis, dtype=float)).tolist()


tests = [
    ("translated_primitive", (10, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (2, 3), (4, 6), 1),
    ("rotated_primitive", (0, 0, 0), (0, 1, 0), (-1, 0, 0), (0, 0, 1), (2, 3), (4, 6), 1),
    ("translated_rotated_primitive", (10, 5, 1), (0, 1, 0), (0, 0, 1), (1, 0, 0), (2, 3), (4, 6), 2),
    ("nested_transform_composed_frame", (5, 6, 7), (0, 0, -1), (1, 0, 0), (0, -1, 0), (-4, 2), (3, 5), 1.5),
    ("non_default_extrusion_axis", (0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), (1, 4), (2, 8), 3),
    ("sketch_on_non_xy_plane", (0, 9, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), (0, 5), (4, 10), 0.5),
]

results = []
with tempfile.TemporaryDirectory(prefix="f360_r1_synth_") as tmp:
    tmp = Path(tmp)
    for name, origin, x_axis, y_axis, z_axis, center, size, height in tests:
        source = make_case(name, origin, x_axis, y_axis, z_axis, center, size, height)
        src_path = tmp / f"{name}.json"
        dsl_path = tmp / f"{name}.dsl"
        src_path.write_text(json.dumps(source), encoding="utf-8")
        rep = convert_file(src_path, dsl_path)
        dsl = dsl_path.read_text()
        expect = np.asarray(expected_origin(origin, x_axis, y_axis, center), dtype=float)
        origin_ok = f"origin=({expect[0]:.6f}".rstrip("0").rstrip(".") in dsl or all(abs(x) < 1e-6 for x in expect)
        step = tmp / f"{name}.step"
        stl = tmp / f"{name}.stl"
        exec_report = execute_dsl(dsl, step, stl)
        import trimesh
        mesh = trimesh.load(str(stl), force="mesh", process=True)
        if isinstance(mesh, trimesh.Scene):
            mesh = mesh.dump(concatenate=True)
        bbox_center = np.asarray(mesh.bounds).mean(axis=0)
        expected_bbox_center = expect + np.asarray(z_axis, dtype=float) * height * 0.5
        bbox_center_error = float(np.linalg.norm(bbox_center - expected_bbox_center))
        results.append({
            "name": name,
            "conversion_pass": True,
            "dsl_execute_pass": Path(step).exists() and Path(stl).exists(),
            "expected_origin": expect.tolist(),
            "dsl": dsl,
            "bbox_center": bbox_center.tolist(),
            "expected_bbox_center": expected_bbox_center.tolist(),
            "bbox_center_error": bbox_center_error,
            "pass": bbox_center_error < 1e-5,
            "conversion_report": rep,
            "execute_report": exec_report,
        })

# Boolean under different transforms: verify two bodies execute and retain both placement offsets.
with tempfile.TemporaryDirectory(prefix="f360_r1_bool_") as tmp:
    tmp = Path(tmp)
    data = make_case("boolean_operands_under_different_transforms", (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (2, 0), (2, 2), 1)
    data["timeline"].append({"index": 1, "entity": "e1"})
    data["entities"]["s1"] = {
        "type": "Sketch",
        "transform": {"origin": p(10, 0, 0), "x_axis": v(1, 0, 0), "y_axis": v(0, 1, 0), "z_axis": v(0, 0, 1)},
        "profiles": {"p1": {"loops": [rect_loop(3, 0, 2, 2)]}},
    }
    data["entities"]["e1"] = {
        "type": "ExtrudeFeature",
        "operation": "JoinFeatureOperation",
        "extent_type": "OneSideFeatureExtentType",
        "start_extent": {"type": "ProfilePlaneStartDefinition"},
        "extent_one": {"distance": {"value": 1}, "taper_angle": {"value": 0.0}},
        "profiles": [{"sketch": "s1", "profile": "p1"}],
    }
    src_path = tmp / "boolean.json"
    dsl_path = tmp / "boolean.dsl"
    src_path.write_text(json.dumps(data), encoding="utf-8")
    rep = convert_file(src_path, dsl_path)
    dsl = dsl_path.read_text()
    step = tmp / "boolean.step"
    stl = tmp / "boolean.stl"
    execute_dsl(dsl, step, stl)
    results.append({
        "name": "boolean_operands_under_different_transforms",
        "conversion_pass": True,
        "dsl_execute_pass": step.exists() and stl.exists(),
        "expected_origins": [[2, 0, 0], [13, 0, 0]],
        "dsl": dsl,
        "pass": "origin=(2" in dsl and "origin=(13" in dsl and step.exists(),
        "conversion_report": rep,
    })

summary = {
    "TEST_N": len(results),
    "PASS_N": sum(1 for r in results if r["pass"]),
    "FAIL_N": sum(1 for r in results if not r["pass"]),
    "tests": results,
}
(OUT / "FUSION360_R1_PLACEMENT_SYNTHETIC_TESTS.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print(json.dumps({"TEST_N": summary["TEST_N"], "PASS_N": summary["PASS_N"], "FAIL_N": summary["FAIL_N"]}, indent=2))
raise SystemExit(0 if summary["FAIL_N"] == 0 else 1)
