#!/usr/bin/env python3
"""Decode + evaluate CAD SpatialLM on a ShareGPT split (train100 val/train).

Metrics:
  - exact DSL match
  - op recall / multiset F1
  - predicted_op_count / gt_op_count  (under-generation detector)
  - STEP valid rate (DSL → OCC → STEP)
  - Chamfer / Hausdorff95 / volume error vs GT mesh
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "SpatialLM"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

from decode_overfit10 import (  # noqa: E402
    CAD_INSTRUCTION,
    _build_tensor,
    _load_model,
    _normalize_dsl,
    _op_tokens,
    generate_dsl,
)


def _exec_step(code: str, out_dir: Path) -> dict:
    from edge_aware_cad_planner_v1.cad_dsl import parse_dsl

    out_dir.mkdir(parents=True, exist_ok=True)
    dsl_path = out_dir / "pred.dsl"
    step = out_dir / "pred.step"
    stl = out_dir / "pred.stl"
    dsl_path.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")
    try:
        parse_dsl(code)
    except Exception as exc:
        return {"parsed": False, "step_ok": False, "error": f"parse: {exc}"}

    try:
        from edge_aware_cad_planner_v1.cad_dsl import execute_dsl

        execute_dsl(code, step, stl)
    except Exception:
        py = Path("/data/miniconda3/envs/cadfit-env/bin/python")
        script = ROOT / "scripts/deepcad/dsl_to_occ.py"
        proc = subprocess.run(
            [str(py), str(script), "--dsl", str(dsl_path), "--step", str(step), "--stl", str(stl)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return {
                "parsed": True,
                "step_ok": False,
                "error": (proc.stderr or proc.stdout)[-400:],
            }
    ok = step.exists() and step.stat().st_size > 0
    return {"parsed": True, "step_ok": ok, "step": str(step), "stl": str(stl) if stl.exists() else None}


def _geom(gt_mesh: Path, pred_stl: Path, n: int = 20000, seed: int = 0) -> dict:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(gt_mesh), force="mesh")
    pred = trimesh.load(str(pred_stl), force="mesh")
    if isinstance(ref, trimesh.Scene):
        ref = ref.dump(concatenate=True)
    if isinstance(pred, trimesh.Scene):
        pred = pred.dump(concatenate=True)
    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    if diag < 1e-12:
        return {"error": "zero_diag"}
    rng = np.random.default_rng(seed)
    a, _ = trimesh.sample.sample_surface(ref, n, seed=int(rng.integers(1 << 30)))
    b, _ = trimesh.sample.sample_surface(pred, n, seed=int(rng.integers(1 << 30)))
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]
    ref_vol = float(abs(ref.volume)) if ref.is_volume else None
    pred_vol = float(abs(pred.volume)) if pred.is_volume else None
    vol_err = None
    if ref_vol and ref_vol > 0 and pred_vol is not None:
        vol_err = abs(pred_vol - ref_vol) / ref_vol
    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff_95_norm": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "volume_error": vol_err,
    }


SOLID_OPS = frozenset({"Extrude", "ExtrudePolygon", "Box", "Cylinder", "Revolve"})


def _op_multiset(dsl_text: str) -> list[str]:
    """Ordered list of op names for multiset F1."""
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

    try:
        prog = parse_dsl(extract_dsl_code(dsl_text))
        return [
            v["op"]
            for name, v in prog.assignments.items()
            if name != "result" and isinstance(v, dict) and "op" in v
        ]
    except Exception:
        return []


def _solid_op_count(dsl_text: str) -> int:
    """Count solid construction ops (Extrude/ExtrudePolygon/Box/...)."""
    return sum(1 for op in _op_multiset(dsl_text) if op in SOLID_OPS)


def _f1_multiset(gt: list[str], pred: list[str]) -> float:
    from collections import Counter

    if not gt and not pred:
        return 1.0
    cg, cp = Counter(gt), Counter(pred)
    tp = sum((cg & cp).values())
    if tp == 0:
        return 0.0
    prec = tp / max(sum(cp.values()), 1)
    rec = tp / max(sum(cg.values()), 1)
    return 2 * prec * rec / max(prec + rec, 1e-12)


def _op_bucket(op_count: int) -> str:
    if op_count <= 1:
        return "1-op"
    if op_count == 2:
        return "2-op"
    if op_count == 3:
        return "3-op"
    return "4+-op"


def _stratified_metrics(rows: list[dict]) -> dict[str, Any]:
    """Primary 1K eval metrics by GT op bucket."""
    buckets = {"1-op": [], "2-op": [], "3-op": [], "4+-op": [], "all": rows}
    for r in rows:
        if "gt_op_count" not in r:
            continue
        buckets[_op_bucket(r["gt_op_count"])].append(r)

    def _summ(sub: list[dict]) -> dict[str, Any]:
        if not sub:
            return {}
        ratios = [
            r["predicted_op_count_over_gt_op_count"]
            for r in sub
            if r.get("predicted_op_count_over_gt_op_count") is not None
        ]
        return {
            "n": len(sub),
            "mean_gt_op_count": float(np.mean([r["gt_op_count"] for r in sub])),
            "mean_predicted_op_count": float(np.mean([r["predicted_op_count"] for r in sub])),
            "mean_pred_gt_op_ratio": float(np.mean(ratios)) if ratios else None,
            "under_generation_rate": sum(1 for r in sub if r.get("under_generation"))
            / len(sub),
            "mean_op_recall": float(np.mean([r["op_recall"] for r in sub])),
            "mean_op_f1": float(np.mean([r["op_f1"] for r in sub])),
            "eos_rate": sum(1 for r in sub if r.get("stop_reason") == "EOS") / len(sub),
            "max_length_rate": sum(1 for r in sub if r.get("stop_reason") == "MAX_LENGTH")
            / len(sub),
            "step_valid_rate": sum(1 for r in sub if r.get("step_ok")) / len(sub),
            "mean_chamfer_norm": float(
                np.mean(
                    [
                        r["geometry"]["chamfer_norm"]
                        for r in sub
                        if "chamfer_norm" in r.get("geometry", {})
                    ]
                )
            )
            if any("chamfer_norm" in r.get("geometry", {}) for r in sub)
            else None,
        }

    return {k: _summ(v) for k, v in buckets.items() if v}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--split-json", type=Path, required=True, help="ShareGPT json (val preferred)")
    ap.add_argument(
        "--variant",
        choices=("ours", "baseline", "edge_zero", "edge_shuffle", "edge_real"),
        required=True,
        help="6ch baseline or 7ch ablation (zero/shuffle/real=ours)",
    )
    ap.add_argument("--media-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD")
    ap.add_argument("--train-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD/train")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float32"))
    ap.add_argument("--max-new-tokens", type=int, default=4096)
    args = ap.parse_args()

    use_edge = args.variant in ("ours", "edge_zero", "edge_shuffle", "edge_real")
    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)

    model, tokenizer, preprocess_fn = _load_model(
        args.checkpoint, use_edge, getattr(torch, args.dtype), "cuda"
    )

    rows = []
    exact_n = 0
    for rec in records:
        sid = rec["id"]
        gt = rec["conversations"][1]["value"]
        feats = args.media_dir / rec["point_clouds"][0]
        sample_out = args.out / sid
        sample_out.mkdir(parents=True, exist_ok=True)

        tensor = _build_tensor(feats, preprocess_fn, use_edge)
        pred, gen_meta = generate_dsl(
            model, tokenizer, tensor, max_new_tokens=args.max_new_tokens, return_meta=True
        )
        (sample_out / "pred.txt").write_text(pred, encoding="utf-8")
        (sample_out / "generation_meta.json").write_text(
            json.dumps(gen_meta, indent=2) + "\n", encoding="utf-8"
        )
        (sample_out / "gt.dsl").write_text(gt, encoding="utf-8")

        exact = _normalize_dsl(pred) == _normalize_dsl(gt)
        exact_n += int(exact)
        gt_ops, pred_ops = _op_tokens(gt), _op_tokens(pred)
        op_recall = len(gt_ops & pred_ops) / len(gt_ops) if gt_ops else 0.0
        gt_ms, pred_ms = _op_multiset(gt), _op_multiset(pred)
        op_f1 = _f1_multiset(gt_ms, pred_ms)
        gt_op_count = _solid_op_count(gt)
        predicted_op_count = _solid_op_count(pred)
        op_count_ratio = (
            predicted_op_count / gt_op_count if gt_op_count > 0 else None
        )

        from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code
        from cad_canonical import load_transform_json, transform_dsl

        try:
            code = extract_dsl_code(pred)
        except Exception:
            code = pred
        (sample_out / "pred_canonical.dsl").write_text(
            code if code.endswith("\n") else code + "\n", encoding="utf-8"
        )

        # Pred is in canonical space; invert T for source-space STEP / geom vs model.obj
        tf_path = args.train_dir / sid / "coordinate_transform.json"
        code_source = code
        if tf_path.exists():
            try:
                tf = load_transform_json(tf_path)
                code_source = transform_dsl(code, tf, inverse=True)
                (sample_out / "pred_source.dsl").write_text(code_source, encoding="utf-8")
            except Exception as exc:
                (sample_out / "inverse_transform_error.txt").write_text(str(exc), encoding="utf-8")

        exec_rec = _exec_step(code_source, sample_out)

        geom = {}
        gt_mesh = args.train_dir / sid / "model.obj"
        if exec_rec.get("step_ok") and exec_rec.get("stl") and gt_mesh.exists():
            try:
                geom = _geom(gt_mesh, Path(exec_rec["stl"]))
            except Exception as exc:
                geom = {"error": str(exc)}

        row = {
            "sample_id": sid,
            "exact_match": exact,
            "gt_ops": sorted(gt_ops),
            "pred_ops": sorted(pred_ops),
            "op_recall": op_recall,
            "op_f1": op_f1,
            "gt_op_count": gt_op_count,
            "predicted_op_count": predicted_op_count,
            "predicted_op_count_over_gt_op_count": op_count_ratio,
            "under_generation": (
                predicted_op_count < gt_op_count if gt_op_count > 0 else False
            ),
            **gen_meta,
            **exec_rec,
            "geometry": geom,
        }
        rows.append(row)
        ratio_s = f"{op_count_ratio:.2f}" if op_count_ratio is not None else "n/a"
        print(
            f"{sid}: exact={exact} parsed={row.get('parsed')} step={row.get('step_ok')} "
            f"op_recall={op_recall:.2f} op_f1={op_f1:.2f} "
            f"pred/gt_ops={predicted_op_count}/{gt_op_count}={ratio_s} "
            f"chamfer={geom.get('chamfer_norm')}"
        )

    chamfers = [r["geometry"]["chamfer_norm"] for r in rows if "chamfer_norm" in r.get("geometry", {})]
    haus = [r["geometry"]["hausdorff_95_norm"] for r in rows if "hausdorff_95_norm" in r.get("geometry", {})]
    vols = [r["geometry"]["volume_error"] for r in rows if r.get("geometry", {}).get("volume_error") is not None]
    ratios = [
        r["predicted_op_count_over_gt_op_count"]
        for r in rows
        if r.get("predicted_op_count_over_gt_op_count") is not None
    ]
    stratified = _stratified_metrics(rows)
    stop_counts = Counter(r.get("stop_reason") for r in rows if r.get("stop_reason"))
    report = {
        "checkpoint": str(args.checkpoint),
        "variant": args.variant,
        "split": str(args.split_json),
        "max_new_tokens": args.max_new_tokens,
        "n_samples": len(rows),
        "exact_match_n": exact_n,
        "exact_match_rate": exact_n / max(len(rows), 1),
        "mean_op_recall": float(np.mean([r["op_recall"] for r in rows])) if rows else 0.0,
        "mean_op_f1": float(np.mean([r["op_f1"] for r in rows])) if rows else 0.0,
        "mean_gt_op_count": float(np.mean([r["gt_op_count"] for r in rows])) if rows else 0.0,
        "mean_predicted_op_count": float(np.mean([r["predicted_op_count"] for r in rows]))
        if rows
        else 0.0,
        "mean_predicted_op_count_over_gt_op_count": float(np.mean(ratios)) if ratios else None,
        "under_generation_rate": sum(1 for r in rows if r.get("under_generation"))
        / max(len(rows), 1),
        "stop_reason_counts": dict(stop_counts),
        "eos_rate": stop_counts.get("EOS", 0) / max(len(rows), 1),
        "max_length_rate": stop_counts.get("MAX_LENGTH", 0) / max(len(rows), 1),
        "stratified": stratified,
        "dsl_parse_valid_rate": sum(1 for r in rows if r.get("parsed")) / max(len(rows), 1),
        "step_valid_rate": sum(1 for r in rows if r.get("step_ok")) / max(len(rows), 1),
        "mean_chamfer_norm": float(np.mean(chamfers)) if chamfers else None,
        "mean_hausdorff_95_norm": float(np.mean(haus)) if haus else None,
        "mean_volume_error": float(np.mean(vols)) if vols else None,
        "samples": rows,
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
