#!/usr/bin/env python3
"""Coordinate contract audit: Point input ↔ GT DSL ↔ GT STEP/mesh.

Checks whether SpatialLM CAD preprocessing (target_diagonal scale +
PositiveShift) is applied only to the point cloud while program.dsl labels
remain in DeepCAD-normalized space — a silent desync.

Usage:
  /data/miniconda3/envs/cadfit-env/bin/python scripts/deepcad/coordinate_contract_audit.py \\
      --n 20 --seed 0
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "deepcad"))

TARGET_DIAGONAL = 6.0
NUM_BINS = 1280
TOL_MATCH = 5e-3  # bbox half-extent relative / absolute mix
DIAG_TOL = 2e-2


def _bbox(pts: np.ndarray) -> dict:
    pts = np.asarray(pts, dtype=np.float64)
    mn = pts.min(0)
    mx = pts.max(0)
    extent = mx - mn
    diag = float(np.linalg.norm(extent))
    return {
        "min": mn.tolist(),
        "max": mx.tolist(),
        "extent": extent.tolist(),
        "center": ((mn + mx) / 2).tolist(),
        "diagonal": diag,
    }


def _mesh_bbox(path: Path) -> dict | None:
    if not path.exists():
        return None
    import trimesh

    m = trimesh.load(str(path), force="mesh")
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)
    if m is None or len(getattr(m, "vertices", [])) == 0:
        return None
    return _bbox(np.asarray(m.vertices, dtype=np.float64))


def _dsl_exec_bbox(dsl_path: Path) -> dict | None:
    """Execute GT DSL → temp STL → bbox (same path as training label geometry)."""
    from dsl_to_occ import run_dsl_to_occ

    with tempfile.TemporaryDirectory(prefix="coord_audit_") as td:
        td = Path(td)
        step = td / "tmp.step"
        stl = td / "tmp.stl"
        try:
            rep = run_dsl_to_occ(dsl_path, step, stl)
        except Exception as e:
            return {"error": f"exec_failed: {e}"}
        if not stl.exists():
            return {"error": f"no_stl: {rep}"}
        bb = _mesh_bbox(stl)
        if bb is None:
            return {"error": "empty_mesh"}
        return bb


def _spatiallm_preprocess_bbox(points: np.ndarray, target_diagonal: float = TARGET_DIAGONAL):
    """Mirror SpatialLMPlugin._load_cad_npy / preprocess_cad_point_cloud (no GridSample needed for bbox)."""
    coord = points.astype(np.float64).copy()
    extent = coord.max(0) - coord.min(0)
    diagonal = float(np.linalg.norm(extent))
    scale = float(target_diagonal / diagonal) if target_diagonal > 0 and diagonal > 0 else 1.0
    coord_scaled = coord * scale
    # PositiveShift
    shift = coord_scaled.min(0).copy()
    coord_shifted = coord_scaled - shift
    return {
        "scale": scale,
        "translation_positive_shift": shift.tolist(),
        "rotation": [0.0, 0.0, 0.0],
        "bbox_after_scale": _bbox(coord_scaled),
        "bbox_after_positive_shift": _bbox(coord_shifted),
        "target_diagonal": target_diagonal,
        "input_diagonal": diagonal,
    }


def _bbox_close(a: dict | None, b: dict | None, atol: float = TOL_MATCH, rtol: float = 0.02) -> bool:
    if not a or not b or "diagonal" not in a or "diagonal" not in b:
        return False
    if a.get("error") or b.get("error"):
        return False
    da, db = a["diagonal"], b["diagonal"]
    if abs(da - db) > max(atol, rtol * max(da, db, 1e-9)):
        return False
    ca, cb = np.asarray(a["center"]), np.asarray(b["center"])
    return bool(np.allclose(ca, cb, atol=max(atol, rtol * max(da, db, 1e-9))))


def _rel_diag_err(a: dict | None, b: dict | None) -> float | None:
    if not a or not b or "diagonal" not in a or "diagonal" not in b:
        return None
    if a.get("error") or b.get("error"):
        return None
    da, db = a["diagonal"], b["diagonal"]
    return abs(da - db) / max(da, db, 1e-12)


def audit_one(sample_dir: Path, target_diagonal: float = TARGET_DIAGONAL) -> dict:
    sid = sample_dir.name
    feats_path = sample_dir / "features.npy"
    dsl_path = sample_dir / "program.dsl"
    obj_path = sample_dir / "model.obj"
    stl_path = sample_dir / "model.stl"
    step_path = sample_dir / "model.step"

    feats = np.load(feats_path)
    xyz = feats[:, :3]

    feat_bb = _bbox(xyz)
    mesh_bb = _mesh_bbox(obj_path) or _mesh_bbox(stl_path)
    # STEP bbox via existing mesh derived from STEP (model.obj); also try re-read stl
    step_bb = _mesh_bbox(stl_path) or mesh_bb

    dsl_bb = _dsl_exec_bbox(dsl_path)
    prep = _spatiallm_preprocess_bbox(xyz, target_diagonal=target_diagonal)

    # Also run full SpatialLM path (with GridSample) if importable — xyz after sample
    encoder_bb = None
    try:
        from spatiallm_cad_frontend import preprocess_cad_point_cloud

        normals = feats[:, 3:6]
        edge = feats[:, 6] if feats.shape[1] >= 7 else np.zeros(len(feats))
        part = preprocess_cad_point_cloud(
            xyz, normals, edge, num_bins=NUM_BINS, target_diagonal=target_diagonal
        )
        # tensor columns: grid(3) | xyz(3) | ...
        enc_xyz = part.tensor[0, :, 3:6].numpy()
        encoder_bb = _bbox(enc_xyz)
        prep["frontend_scale"] = part.scale
        prep["frontend_stats"] = part.stats
    except Exception as e:
        prep["frontend_error"] = str(e)

    # Label is raw DSL — no scale/shift applied in create_spatiallm_cad_dataset / cad_mode
    label_synced = False

    features_vs_mesh = _bbox_close(feat_bb, mesh_bb)
    features_vs_dsl = _bbox_close(feat_bb, dsl_bb)
    mesh_vs_dsl = _bbox_close(mesh_bb, dsl_bb)
    # After preprocess, diagonal should be ~ target_diagonal, NOT feat diagonal
    prep_diag = prep["bbox_after_positive_shift"]["diagonal"]
    scale_applied_to_input = abs(prep["scale"] - 1.0) > 1e-3
    scale_applied_to_label = False  # by construction of dataset

    contract_ok = (
        features_vs_mesh
        and features_vs_dsl
        and mesh_vs_dsl
        and (not scale_applied_to_input or label_synced)
        and abs(prep_diag - target_diagonal) < DIAG_TOL * target_diagonal
        # last: preprocess reaches target diag (expected); failure is label sync
    )

    # Primary verdict the user cares about:
    desync = scale_applied_to_input and not label_synced

    return {
        "sample_id": sid,
        "raw_step_bbox": step_bb,  # from model.stl built from STEP
        "raw_mesh_bbox": mesh_bb,
        "features_npy_bbox": feat_bb,
        "spatiallm_preprocess": {
            "scale_factor": prep["scale"],
            "translation": prep["translation_positive_shift"],
            "rotation": prep["rotation"],
            "bbox_after_scale": prep["bbox_after_scale"],
            "bbox_after_positive_shift": prep["bbox_after_positive_shift"],
            "encoder_xyz_bbox": encoder_bb,
            "target_diagonal": target_diagonal,
        },
        "gt_dsl_execute_bbox": dsl_bb,
        "checks": {
            "features_vs_mesh": features_vs_mesh,
            "features_vs_dsl_exec": features_vs_dsl,
            "mesh_vs_dsl_exec": mesh_vs_dsl,
            "rel_err_features_mesh_diag": _rel_diag_err(feat_bb, mesh_bb),
            "rel_err_features_dsl_diag": _rel_diag_err(feat_bb, dsl_bb),
            "scale_applied_to_point_input": scale_applied_to_input,
            "scale_applied_to_dsl_label": scale_applied_to_label,
            "positive_shift_applied_to_point_input": True,
            "positive_shift_applied_to_dsl_label": False,
            "rotation_applied": False,
            "input_label_desync": desync,
            "preprocess_diagonal": prep_diag,
            "features_diagonal": feat_bb["diagonal"],
            "dsl_diagonal": dsl_bb.get("diagonal") if dsl_bb else None,
        },
        "verdict": "FAIL_DESYNC" if desync else ("PASS" if contract_ok else "FAIL_OTHER"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Coordinate contract audit")
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
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--target-diagonal", type=float, default=TARGET_DIAGONAL)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "ours3/deepcad_train100_val_decode/coordinate_contract_audit.json",
    )
    args = parser.parse_args()

    if args.manifest.exists():
        ids = [
            sid.replace("/", "_")
            for sid in json.loads(args.manifest.read_text())["sample_ids"]
        ]
    else:
        ids = [p.name for p in sorted(args.train_dir.iterdir()) if p.is_dir()]

    complete = []
    for sid in ids:
        d = args.train_dir / sid
        if (d / "features.npy").exists() and (d / "program.dsl").exists() and (
            (d / "model.obj").exists() or (d / "model.stl").exists()
        ):
            complete.append(d)

    rng = random.Random(args.seed)
    rng.shuffle(complete)
    sample_dirs = complete[: args.n]

    rows = []
    for d in sample_dirs:
        print(f"auditing {d.name} ...", flush=True)
        rows.append(audit_one(d, target_diagonal=args.target_diagonal))

    n_desync = sum(1 for r in rows if r["checks"]["input_label_desync"])
    n_feat_mesh = sum(1 for r in rows if r["checks"]["features_vs_mesh"])
    n_feat_dsl = sum(1 for r in rows if r["checks"]["features_vs_dsl_exec"])
    scales = [r["spatiallm_preprocess"]["scale_factor"] for r in rows]
    feat_diags = [r["features_npy_bbox"]["diagonal"] for r in rows]
    prep_diags = [r["checks"]["preprocess_diagonal"] for r in rows]

    summary = {
        "n": len(rows),
        "n_input_label_desync": n_desync,
        "n_features_match_mesh": n_feat_mesh,
        "n_features_match_dsl_exec": n_feat_dsl,
        "scale_factor_min": float(min(scales)) if scales else None,
        "scale_factor_max": float(max(scales)) if scales else None,
        "scale_factor_mean": float(np.mean(scales)) if scales else None,
        "features_diagonal_min": float(min(feat_diags)) if feat_diags else None,
        "features_diagonal_max": float(max(feat_diags)) if feat_diags else None,
        "preprocess_diagonal_mean": float(np.mean(prep_diags)) if prep_diags else None,
        "target_diagonal": args.target_diagonal,
        "contract_verdict": (
            "FAIL: point input scaled+shifted; DSL label NOT synced"
            if n_desync == len(rows) and len(rows) > 0
            else (
                "PASS"
                if n_desync == 0 and n_feat_mesh == len(rows) and n_feat_dsl == len(rows)
                else "MIXED"
            )
        ),
        "explanation": {
            "on_disk_chain": (
                "DeepCAD cad.normalize() → DSL/STEP/mesh/features share DeepCAD unit-cube space "
                "(features ≈ mesh ≈ DSL-exec). This layer is OK."
            ),
            "training_desync": (
                "SpatialLMPlugin._load_cad_npy scales xyz by (cad_target_diagonal / bbox_diagonal) "
                f"then PositiveShift (coord -= min). Labels from create_spatiallm_cad_dataset "
                "are raw program.dsl with NO inverse transform. cad_mode transformations dict "
                "hardcodes scaling=1.0 and never rewrites DSL. Absolute scale of features is "
                "erased to ~constant diagonal; model must emit original DeepCAD numbers."
            ),
            "code_refs": [
                "SpatialLM/spatiallm/tuner/data/mm_plugin.py::_load_cad_npy",
                "scripts/spatiallm_cad_frontend.py::preprocess_cad_point_cloud",
                "scripts/deepcad/create_spatiallm_cad_dataset.py::_load_dsl_label",
            ],
        },
    }

    out = {"summary": summary, "per_sample": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    # human markdown
    md = args.out.with_suffix(".md")
    lines = [
        "# Coordinate contract audit",
        "",
        f"**Verdict:** `{summary['contract_verdict']}`",
        "",
        f"- n={summary['n']}, desync={summary['n_input_label_desync']}/{summary['n']}",
        f"- features↔mesh match: {summary['n_features_match_mesh']}/{summary['n']}",
        f"- features↔DSL-exec match: {summary['n_features_match_dsl_exec']}/{summary['n']}",
        f"- scale_factor range: [{summary['scale_factor_min']:.3f}, {summary['scale_factor_max']:.3f}] "
        f"(mean {summary['scale_factor_mean']:.3f})",
        f"- features diagonal range: [{summary['features_diagonal_min']:.3f}, {summary['features_diagonal_max']:.3f}]",
        f"- preprocess diagonal mean: {summary['preprocess_diagonal_mean']:.3f} (target={summary['target_diagonal']})",
        "",
        "## Per-sample",
        "",
        "| sample_id | feat_diag | dsl_diag | scale | shift | preprocess_diag | desync | feat≈mesh | feat≈dsl |",
        "|---|---:|---:|---:|---|---:|:---:|:---:|:---:|",
    ]
    for r in rows:
        c = r["checks"]
        sh = r["spatiallm_preprocess"]["translation"]
        shift_s = f"({sh[0]:.3f},{sh[1]:.3f},{sh[2]:.3f})"
        dsl_d = c["dsl_diagonal"]
        dsl_s = f"{dsl_d:.4f}" if dsl_d is not None else "ERR"
        lines.append(
            f"| {r['sample_id']} | {c['features_diagonal']:.4f} | {dsl_s} | "
            f"{r['spatiallm_preprocess']['scale_factor']:.3f} | `{shift_s}` | "
            f"{c['preprocess_diagonal']:.3f} | "
            f"{'Y' if c['input_label_desync'] else 'n'} | "
            f"{'Y' if c['features_vs_mesh'] else 'n'} | "
            f"{'Y' if c['features_vs_dsl_exec'] else 'n'} |"
        )
    lines.extend(
        [
            "",
            "## Explanation",
            "",
            summary["explanation"]["on_disk_chain"],
            "",
            summary["explanation"]["training_desync"],
            "",
            "Code:",
            "",
            *[f"- `{p}`" for p in summary["explanation"]["code_refs"]],
            "",
        ]
    )
    md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"\nwrote {args.out}\nwrote {md}")
    return 0 if summary["contract_verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
