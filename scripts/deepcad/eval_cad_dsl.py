#!/usr/bin/env python3
"""Evaluate predicted CAD DSL: op accuracy + geometry (step 6)."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, extract_dsl_code, parse_dsl  # noqa: E402

TOP_LEVEL_OPS = ("Extrude", "ExtrudePolygon", "Box", "Cut", "Union", "Revolve", "Cylinder")


def _extract_ops(dsl_text: str) -> list[str]:
    try:
        program = parse_dsl(extract_dsl_code(dsl_text))
    except Exception:
        return []
    ops = []
    for node in program.assignments.values():
        if isinstance(node, dict) and "op" in node:
            ops.append(node["op"])
    return ops


def _op_sequence_accuracy(gt_ops: list[str], pred_ops: list[str]) -> dict:
    gt_set = Counter(gt_ops)
    pred_set = Counter(pred_ops)
    all_ops = set(gt_set) | set(pred_set)
    per_op = {}
    correct = 0
    total = 0
    for op in all_ops:
        g = gt_set.get(op, 0)
        p = pred_set.get(op, 0)
        match = min(g, p)
        per_op[op] = {"gt": g, "pred": p, "matched": match}
        correct += match
        total += max(g, p)
    return {
        "exact_sequence_match": gt_ops == pred_ops,
        " multiset_f1": 2 * correct / (sum(gt_set.values()) + sum(pred_set.values()))
        if (sum(gt_set.values()) + sum(pred_set.values())) > 0
        else 0.0,
        "per_op": per_op,
        "gt_ops": gt_ops,
        "pred_ops": pred_ops,
    }


def _sample_surface(mesh, n: int, seed: int) -> np.ndarray:
    import trimesh

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    rng = np.random.default_rng(seed)
    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=int(rng.integers(1 << 30)))
    return np.asarray(pts, dtype=np.float64)


def _geometry_metrics(gt_mesh: Path, pred_stl: Path, n: int = 50_000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(gt_mesh), force="mesh")
    pred = trimesh.load(str(pred_stl), force="mesh")
    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    a = _sample_surface(ref, n, seed)
    b = _sample_surface(pred, n, seed + 1)
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]
    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff_95_norm": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "step_valid": True,
    }


def eval_prediction(
    gt_dsl_path: Path,
    pred_text: str,
    gt_mesh: Path,
    seed: int = 0,
) -> dict:
    gt_text = gt_dsl_path.read_text(encoding="utf-8")
    gt_ops = _extract_ops(gt_text)
    pred_ops = _extract_ops(pred_text)
    result = {"op_metrics": _op_sequence_accuracy(gt_ops, pred_ops)}

    try:
        code = extract_dsl_code(pred_text)
        with tempfile.TemporaryDirectory(prefix="cad_eval_") as tmp:
            stl = Path(tmp) / "pred.stl"
            step = Path(tmp) / "pred.step"
            execute_dsl(code, step, stl)
            result["geometry"] = _geometry_metrics(gt_mesh, stl, seed=seed)
    except Exception as exc:
        result["geometry"] = {"step_valid": False, "error": str(exc)}
    return result


def eval_directory(predictions_dir: Path, train_dir: Path, out_path: Path | None) -> dict:
    rows = []
    for pred_file in sorted(predictions_dir.glob("*.txt")):
        sid = pred_file.stem
        sample_dir = train_dir / sid
        gt_dsl = sample_dir / "program.dsl"
        gt_mesh = sample_dir / "model.obj"
        if not gt_dsl.exists() or not gt_mesh.exists():
            continue
        pred_text = pred_file.read_text(encoding="utf-8")
        row = {"sample_id": sid, **eval_prediction(gt_dsl, pred_text, gt_mesh)}
        rows.append(row)

    step_valid = sum(1 for r in rows if r.get("geometry", {}).get("step_valid"))
    chamfers = [r["geometry"]["chamfer_norm"] for r in rows if r.get("geometry", {}).get("step_valid")]
    summary = {
        "n_samples": len(rows),
        "step_valid_rate": step_valid / len(rows) if rows else 0.0,
        "mean_chamfer_norm": float(np.mean(chamfers)) if chamfers else None,
        "mean_hausdorff_95_norm": float(
            np.mean([r["geometry"]["hausdorff_95_norm"] for r in rows if r.get("geometry", {}).get("step_valid")])
        )
        if chamfers
        else None,
        "samples": rows,
    }

    print(json.dumps({k: v for k, v in summary.items() if k != "samples"}, indent=2))
    if out_path:
        out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate CAD DSL predictions")
    parser.add_argument("--predictions-dir", type=Path, required=True, help="Dir of <sample_id>.txt predictions")
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    eval_directory(args.predictions_dir, args.train_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
