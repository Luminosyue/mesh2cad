#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

from common import CASES, ensure_dirs, sha256_file


PARAMS = [
    (0.05, 0.08),
    (0.02, 0.05),
    (0.01, 0.03),
    (0.005, 0.02),
    (0.002, 0.01),
]
TARGETS = {
    "case_a_flange": (20_000, 60_000),
    "case_b_bracket": (30_000, 100_000),
}


def load_build_model(path: Path):
    spec = importlib.util.spec_from_file_location("ground_truth_case", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.build_model


def solid_stats(obj) -> dict:
    shape = obj.val() if hasattr(obj, "val") else obj
    bb = shape.BoundingBox()
    return {
        "solid_count": len(shape.Solids()),
        "face_count": len(shape.Faces()),
        "volume": float(shape.Volume()),
        "bbox": [float(bb.xlen), float(bb.ylen), float(bb.zlen)],
        "shape_valid": bool(shape.isValid()),
    }


def mesh_stats(path: Path) -> dict:
    t0 = time.time()
    mesh = trimesh.load(path, force="mesh", process=True)
    verts = np.asarray(mesh.vertices)
    try:
        comps = len(mesh.split(only_watertight=False))
    except Exception:
        comps = -1
    return {
        "vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.faces)),
        "connected_component_count": int(comps),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume": float(mesh.volume),
        "surface_area": float(mesh.area),
        "bbox": [float(x) for x in mesh.extents],
        "nonfinite_vertex_count": int((~np.isfinite(verts)).any(axis=1).sum()) if len(verts) else 0,
        "load_seconds": time.time() - t0,
    }


def mesh_gate(stats: dict) -> bool:
    return (
        stats["connected_component_count"] == 1
        and stats["is_watertight"]
        and stats["is_winding_consistent"]
        and stats["is_volume"]
        and stats["volume"] > 0
        and stats["nonfinite_vertex_count"] == 0
    )


def choose_candidate(case_name: str, candidates: list[dict]) -> dict:
    lo, hi = TARGETS[case_name]
    valid = [c for c in candidates if c["mesh_gate"]]
    if not valid:
        raise RuntimeError(f"No valid watertight mesh candidate for {case_name}")
    in_range = [c for c in valid if lo <= c["triangle_count"] <= hi]
    if in_range:
        return max(in_range, key=lambda c: c["triangle_count"])
    under_ok = [c for c in valid if c["triangle_count"] >= 10_000 and c["triangle_count"] <= 150_000]
    if under_ok:
        return max(under_ok, key=lambda c: c["triangle_count"])
    not_huge = [c for c in valid if c["triangle_count"] <= 150_000]
    return max(not_huge or valid, key=lambda c: c["triangle_count"])


def export_case(case_name: str, label: str) -> dict:
    case_dir = Path("datasets/synthetic_high_mesh_two_case_v1") / case_name
    build_model = load_build_model(case_dir / "ground_truth.py")
    obj = build_model()
    gt_step = case_dir / "ground_truth.step"
    cq.exporters.export(obj, str(gt_step))
    reopened = cq.importers.importStep(str(gt_step))
    cad = solid_stats(reopened)
    if cad["solid_count"] != 1 or not cad["shape_valid"] or cad["volume"] <= 0:
        raise RuntimeError(f"CAD gate failed for {case_name}: {cad}")
    candidates = []
    for tol, ang in PARAMS:
        tmp = case_dir / f"input_high_mesh_tol_{tol:g}_ang_{ang:g}.stl"
        cq.exporters.export(obj, str(tmp), tolerance=tol, angularTolerance=ang)
        ms = mesh_stats(tmp)
        lo, hi = TARGETS[case_name]
        candidates.append({
            "case_name": case_name,
            "case_label": label,
            "selected_tolerance": tol,
            "selected_angular_tolerance": ang,
            "triangle_target_reached": lo <= ms["triangle_count"] <= hi,
            "mesh_gate": mesh_gate(ms),
            **ms,
        })
    chosen = choose_candidate(case_name, candidates)
    src = case_dir / f"input_high_mesh_tol_{chosen['selected_tolerance']:g}_ang_{chosen['selected_angular_tolerance']:g}.stl"
    dst = case_dir / "input_high_mesh.stl"
    if dst.exists():
        dst.unlink()
    os.replace(src, dst)
    for p in case_dir.glob("input_high_mesh_tol_*.stl"):
        p.unlink(missing_ok=True)
    audit = {
        **chosen,
        "stl_sha256": sha256_file(dst),
        "step_sha256": sha256_file(gt_step),
        "ground_truth_step_faces": cad["face_count"],
        "ground_truth_solid_count": cad["solid_count"],
        "ground_truth_volume": cad["volume"],
        "ground_truth_bbox": cad["bbox"],
        "ground_truth_shape_valid": cad["shape_valid"],
        "cad_gate": "PASS",
        "adjustments": [],
    }
    (case_dir / "mesh_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"{case_name.upper()}_CAD_GATE=PASS")
    print(f"{case_name.upper()}_TRIANGLES={audit['triangle_count']}")
    print(f"{case_name.upper()}_WATERTIGHT={audit['is_watertight']}")
    return audit


def main() -> int:
    argparse.ArgumentParser().parse_args()
    ensure_dirs()
    audits = {}
    for case_name, label in CASES:
        audits[case_name] = export_case(case_name, label)
    Path("artifacts/synthetic_high_mesh_two_case_v1").mkdir(parents=True, exist_ok=True)
    Path("artifacts/synthetic_high_mesh_two_case_v1/input_mesh_audits.json").write_text(json.dumps(audits, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
