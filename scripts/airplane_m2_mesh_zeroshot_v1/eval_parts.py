#!/usr/bin/env python3
"""Mesh-reference metrics for airplane B0/M2 predictions (no GT DSL)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[2]
OUT_ROOT = REPO / "ours3" / "airplane_m2_mesh_zeroshot_v1"


def sample_mesh(mesh: trimesh.Trimesh, n: int = 8192, seed: int = 0) -> np.ndarray:
    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=seed)
    return np.asarray(pts, dtype=np.float64)


def chamfer_hausdorff(a: np.ndarray, b: np.ndarray) -> dict:
    from scipy.spatial import cKDTree

    da, _ = cKDTree(b).query(a, k=1)
    db, _ = cKDTree(a).query(b, k=1)
    return {
        "chamfer": float(0.5 * (da.mean() + db.mean())),
        "hausdorff_95": float(max(np.percentile(da, 95), np.percentile(db, 95))),
        "coverage_02": float(np.mean(db < 0.02)),
        "fp_occupancy_02": float(np.mean(da < 0.02)),  # pred points near GT
    }


def bbox_err(pred: trimesh.Trimesh, ref: trimesh.Trimesh) -> dict:
    pe = pred.extents
    re = ref.extents
    return {
        "bbox_extent_l1": float(np.abs(pe - re).sum()),
        "bbox_extent_rel": float(np.abs(pe - re).sum() / (re.sum() + 1e-8)),
        "bbox_diag_pred": float(np.linalg.norm(pe)),
        "bbox_diag_ref": float(np.linalg.norm(re)),
    }


def eval_one(part_id: str, arm: str) -> dict:
    pdir = OUT_ROOT / "parts" / part_id
    ddir = OUT_ROOT / "decode" / arm.lower() / part_id
    row = json.loads((ddir / "row.json").read_text())
    tf = json.loads((pdir / "transform.json").read_text())
    mesh_c = trimesh.load(pdir / "mesh_canonical.obj", force="mesh", process=False)

    out = {
        "part_id": part_id,
        "arm": arm,
        "parsed": row.get("parsed"),
        "step_ok": row.get("step_ok"),
        "stop_reason": row.get("stop_reason"),
        "prediction_tokens": row.get("prediction_tokens"),
        "n_curve_tokens": row.get("n_curve_tokens"),
        "n_extrude": row.get("n_extrude"),
        "n_cut": row.get("n_cut"),
        "n_union": row.get("n_union"),
        "fail_type": None,
    }
    stl = row.get("stl")
    if not row.get("step_ok") or not stl or not Path(stl).is_file():
        out["fail_type"] = "step_invalid_or_missing"
        out["geometry"] = None
        return out

    try:
        pred = trimesh.load(stl, force="mesh", process=False)
        if not isinstance(pred, trimesh.Trimesh) or len(pred.faces) == 0:
            out["fail_type"] = "empty_pred_mesh"
            out["geometry"] = None
            return out
    except Exception as exc:
        out["fail_type"] = f"load_pred:{exc}"
        out["geometry"] = None
        return out

    # metrics in canonical frame (same as training / surface)
    ref_pts = sample_mesh(mesh_c, 8192, seed=0)
    pred_pts = sample_mesh(pred, 8192, seed=0)
    geo = chamfer_hausdorff(pred_pts, ref_pts)
    diag = float(tf["target_diagonal"])
    geo["chamfer_rel"] = geo["chamfer"] / diag
    geo["hausdorff_95_rel"] = geo["hausdorff_95"] / diag
    geo.update(bbox_err(pred, mesh_c))
    # under/over geometry by volume if both watertight-ish
    try:
        rv, pv = float(mesh_c.volume), float(pred.volume)
        geo["volume_ref"] = rv
        geo["volume_pred"] = pv
        geo["volume_ratio"] = pv / (abs(rv) + 1e-12)
    except Exception:
        pass
    out["geometry"] = geo
    out["fail_type"] = None

    # denormalize STEP to airplane coords for assembly (mesh copy)
    s = float(tf["scale"])
    t = np.asarray(tf["translation"], dtype=np.float64)
    pred_src = pred.copy()
    pred_src.vertices = (np.asarray(pred_src.vertices) - t) / s
    pred_src.export(ddir / "pred_source.stl")
    # also try write OBJ
    pred_src.export(ddir / "pred_source.obj")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", default=["B0", "M2"])
    ap.add_argument("--parts", nargs="+", default=None)
    args = ap.parse_args()
    parts_root = OUT_ROOT / "parts"
    parts = args.parts or sorted(p.name for p in parts_root.iterdir() if p.is_dir())

    all_rows = {}
    for arm in args.arms:
        rows = [eval_one(p, arm) for p in parts]
        all_rows[arm] = rows
        outp = OUT_ROOT / "metrics" / f"{arm.lower()}.json"
        outp.parent.mkdir(parents=True, exist_ok=True)
        # summary
        ok = [r for r in rows if r.get("geometry")]
        summary = {
            "arm": arm,
            "n": len(rows),
            "step_valid_rate": sum(1 for r in rows if r.get("step_ok")) / max(len(rows), 1),
            "parse_rate": sum(1 for r in rows if r.get("parsed")) / max(len(rows), 1),
            "mean_chamfer_rel": float(np.mean([r["geometry"]["chamfer_rel"] for r in ok]))
            if ok
            else None,
            "mean_hausdorff95_rel": float(
                np.mean([r["geometry"]["hausdorff_95_rel"] for r in ok])
            )
            if ok
            else None,
            "mean_coverage_02": float(np.mean([r["geometry"]["coverage_02"] for r in ok]))
            if ok
            else None,
            "samples": rows,
        }
        outp.write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps({k: v for k, v in summary.items() if k != "samples"}, indent=2))

    # paired table
    lines = [
        "# Airplane mesh-derived curve zero-shot (canary / stress)",
        "",
        "Not a formal main result — M2 trained on B-Rep oracle curves; airplane uses mesh-fitted curves.",
        "",
        "| part | role | K | B0 STEP | M2 STEP | B0 Chamfer_rel | M2 Chamfer_rel | B0 cov | M2 cov |",
        "|---|---|---:|:---:|:---:|---:|---:|---:|---:|",
    ]
    roles = json.loads((OUT_ROOT / "prepare_manifest.json").read_text()) if (OUT_ROOT / "prepare_manifest.json").is_file() else {"parts": []}
    role_map = {p["part_id"]: p.get("role") for p in roles.get("parts", [])}
    for p in parts:
        b0 = next(r for r in all_rows["B0"] if r["part_id"] == p)
        m2 = next(r for r in all_rows["M2"] if r["part_id"] == p)
        bg = b0.get("geometry") or {}
        mg = m2.get("geometry") or {}
        lines.append(
            f"| {p} | {role_map.get(p,'')} | {b0.get('n_curve_tokens')} | "
            f"{'Y' if b0.get('step_ok') else 'N'} | {'Y' if m2.get('step_ok') else 'N'} | "
            f"{bg.get('chamfer_rel', float('nan')):.4f} | {mg.get('chamfer_rel', float('nan')):.4f} | "
            f"{bg.get('coverage_02', float('nan')):.3f} | {mg.get('coverage_02', float('nan')):.3f} |"
        )
    md = OUT_ROOT / "TABLE_CANARY.md"
    md.write_text("\n".join(lines) + "\n")
    print(md.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
