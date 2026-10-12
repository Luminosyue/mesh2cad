#!/usr/bin/env python3
"""Quality audit for DeepCAD spatial dataset (step 3).

Reports:
  1. DSL operation / profile distribution
  2. STEP generation success rate
  3. DSL re-execution consistency vs DeepCAD reference mesh
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))
sys.path.insert(0, str(ROOT / "DeepCAD"))

REQUIRED = ("features.npy", "program.dsl", "model.step", "model.obj", "meta.json")

V1_OPS = {"Sketch", "Circle", "Rectangle", "Box", "Extrude", "ExtrudePolygon", "Cut", "Union", "Cylinder", "Revolve"}


def _sample_ids_from_manifest(manifest: Path) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [sid.replace("/", "_") for sid in data.get("sample_ids", [])]


def _iter_sample_dirs(train_dir: Path, manifest: Path | None) -> list[Path]:
    if manifest is not None:
        ids = _sample_ids_from_manifest(manifest)
        return [train_dir / sid for sid in ids if (train_dir / sid).is_dir()]
    return sorted(p for p in train_dir.iterdir() if p.is_dir())


def _parse_dsl_ops(dsl_text: str) -> tuple[Counter, Counter]:
    ops: Counter = Counter()
    profile_kinds: Counter = Counter()
    try:
        tree = ast.parse(dsl_text, mode="exec")
    except SyntaxError:
        return ops, profile_kinds
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in V1_OPS:
                ops[name] += 1
            if name == "Extrude" and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Name):
                    profile_kinds[arg0.func.id] += 1
            if name == "Box":
                profile_kinds["Rectangle"] += 1
            if name == "ExtrudePolygon":
                profile_kinds["Polygon"] += 1
    return ops, profile_kinds


def _check_artifacts(sample_dir: Path) -> dict:
    missing = [name for name in REQUIRED if not (sample_dir / name).exists()]
    meta = {}
    if (sample_dir / "meta.json").exists():
        meta = json.loads((sample_dir / "meta.json").read_text(encoding="utf-8"))
    occ = meta.get("occ") or {}
    step_ok = bool(occ.get("ok")) and (sample_dir / "model.step").exists()
    dsl_fallback = bool(occ.get("dsl_error"))
    return {
        "complete": len(missing) == 0,
        "missing": missing,
        "step_ok": step_ok,
        "dsl_fallback": dsl_fallback,
        "meta": meta,
    }


def _sample_surface(mesh, n: int, seed: int) -> np.ndarray:
    import trimesh

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    rng = np.random.default_rng(seed)
    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=int(rng.integers(1 << 30)))
    return np.asarray(pts, dtype=np.float64)


def _compare_meshes(ref_path: Path, pred_path: Path, n: int = 50_000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(ref_path), force="mesh")
    pred = trimesh.load(str(pred_path), force="mesh")
    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    if diag < 1e-12:
        return {"error": "zero bbox diagonal"}

    a = _sample_surface(ref, n, seed)
    b = _sample_surface(pred, n, seed + 1)
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]

    ref_vol = float(abs(ref.volume))
    pred_vol = float(abs(pred.volume))
    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff_95_norm": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "volume_ratio": pred_vol / ref_vol if ref_vol > 0 else None,
        "ref_vertices": int(len(ref.vertices)),
        "pred_vertices": int(len(pred.vertices)),
        "ref_faces": int(len(ref.faces)),
        "pred_faces": int(len(pred.faces)),
    }


def _build_reference_mesh(source_json: Path, out_stl: Path) -> bool:
    from deepcad_occ_builder import export_deepcad_json

    try:
        export_deepcad_json(source_json, out_stl.with_suffix(".step"), out_stl)
        return out_stl.exists()
    except Exception:
        return False


def _reexecute_dsl(dsl_path: Path, out_stl: Path) -> bool:
    from edge_aware_cad_planner_v1.cad_dsl import execute_dsl

    try:
        code = dsl_path.read_text(encoding="utf-8")
        step = out_stl.with_suffix(".step")
        execute_dsl(code, step, out_stl)
        return out_stl.exists()
    except Exception:
        return False


def audit_sample(sample_dir: Path, check_consistency: bool, seed: int) -> dict:
    rec = {"sample_id": sample_dir.name, **_check_artifacts(sample_dir)}
    if not (sample_dir / "program.dsl").exists():
        return rec

    dsl_text = (sample_dir / "program.dsl").read_text(encoding="utf-8")
    ops, profiles = _parse_dsl_ops(dsl_text)
    rec["ops"] = dict(ops)
    rec["profiles"] = dict(profiles)
    rec["n_extrude"] = ops.get("Extrude", 0) + ops.get("ExtrudePolygon", 0) + ops.get("Box", 0)
    rec["has_cut"] = ops.get("Cut", 0) > 0
    rec["has_union"] = ops.get("Union", 0) > 0

    if not check_consistency:
        return rec

    source_json = sample_dir / "source.json"
    if not source_json.exists():
        rec["consistency"] = {"skipped": "no source.json"}
        return rec

    with tempfile.TemporaryDirectory(prefix="deepcad_audit_") as tmp:
        tmp_path = Path(tmp)
        ref_stl = tmp_path / "ref.stl"
        dsl_stl = tmp_path / "dsl.stl"

        if not _build_reference_mesh(source_json, ref_stl):
            rec["consistency"] = {"error": "reference mesh build failed"}
            return rec
        if not _reexecute_dsl(sample_dir / "program.dsl", dsl_stl):
            rec["consistency"] = {"error": "DSL re-execution failed"}
            return rec

        metrics = _compare_meshes(ref_stl, dsl_stl, seed=seed)
        rec["consistency"] = metrics
    return rec


def _pct(n: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{100.0 * n / total:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit DeepCAD spatial dataset quality")
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/manifest_train100.json",
    )
    parser.add_argument("--no-consistency", action="store_true", help="Skip Chamfer/volume checks")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=None, help="Write JSON report here")
    args = parser.parse_args()

    sample_dirs = _iter_sample_dirs(args.train_dir, args.manifest)
    records = [
        audit_sample(d, check_consistency=not args.no_consistency, seed=args.seed + i)
        for i, d in enumerate(sample_dirs)
    ]

    total = len(records)
    complete = sum(1 for r in records if r.get("complete"))
    step_ok = sum(1 for r in records if r.get("step_ok"))
    dsl_fallback = sum(1 for r in records if r.get("dsl_fallback"))

    op_totals: Counter = Counter()
    profile_totals: Counter = Counter()
    has_extrude = has_cut = has_union = has_box = 0
    for r in records:
        for k, v in (r.get("ops") or {}).items():
            op_totals[k] += v
        for k, v in (r.get("profiles") or {}).items():
            profile_totals[k] += v
        if r.get("n_extrude", 0) > 0:
            has_extrude += 1
        if r.get("has_cut"):
            has_cut += 1
        if r.get("has_union"):
            has_union += 1
        if (r.get("ops") or {}).get("Box", 0) > 0:
            has_box += 1

    consistency_ok = []
    chamfers = []
    for r in records:
        c = r.get("consistency") or {}
        if "chamfer_norm" in c:
            consistency_ok.append(r["sample_id"])
            chamfers.append(c["chamfer_norm"])

    report = {
        "total_samples": total,
        "complete_artifacts": complete,
        "step_ok": step_ok,
        "dsl_occ_fallback": dsl_fallback,
        "distribution": {
            "samples_with_extrude": {"count": has_extrude, "pct": _pct(has_extrude, total)},
            "samples_with_cut": {"count": has_cut, "pct": _pct(has_cut, total)},
            "samples_with_union": {"count": has_union, "pct": _pct(has_union, total)},
            "samples_with_box_rectangle": {"count": has_box, "pct": _pct(has_box, total)},
            "op_counts": dict(op_totals),
            "profile_counts": dict(profile_totals),
        },
        "consistency": {
            "checked": len(consistency_ok),
            "mean_chamfer_norm": float(np.mean(chamfers)) if chamfers else None,
            "median_chamfer_norm": float(np.median(chamfers)) if chamfers else None,
            "p95_chamfer_norm": float(np.percentile(chamfers, 95)) if chamfers else None,
            "fail_chamfer_gt_0.05": sum(1 for c in chamfers if c > 0.05),
        },
        "samples": records,
    }

    print("=== DeepCAD Dataset Audit ===")
    print(f"Samples:           {total}")
    print(f"Complete:          {complete}/{total} ({_pct(complete, total)})")
    print(f"STEP ok:           {step_ok}/{total} ({_pct(step_ok, total)})")
    print(f"OCC fallback used: {dsl_fallback}/{total}")
    print()
    print("--- DSL distribution (sample-level) ---")
    print(f"Extrude/Box/Polygon: {_pct(has_extrude, total)}")
    print(f"Cut:                 {_pct(has_cut, total)}")
    print(f"Union:               {_pct(has_union, total)}")
    print(f"Box (Rectangle):     {_pct(has_box, total)}")
    print()
    print("--- Op totals ---")
    for op, cnt in op_totals.most_common():
        print(f"  {op}: {cnt}")
    print()
    if chamfers:
        print("--- DSL vs DeepCAD consistency ---")
        print(f"Checked:             {len(chamfers)}")
        print(f"Mean Chamfer (norm): {report['consistency']['mean_chamfer_norm']:.5f}")
        print(f"Median:              {report['consistency']['median_chamfer_norm']:.5f}")
        print(f"P95:                 {report['consistency']['p95_chamfer_norm']:.5f}")
        print(f"Chamfer > 0.05:      {report['consistency']['fail_chamfer_gt_0.05']}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\nReport written to {args.out}")

    if step_ok < 0.9 * total:
        print("\nWARNING: STEP success rate below 90% — fix DSL runtime before training.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
