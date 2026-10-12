#!/usr/bin/env python3
"""CANONICAL_4X4_FIT_GATE — true LSQ cubic 4×4 fit vs original Fusion360 BSpline.

Correct pipeline (NOT UV-samples-as-poles):
  Original BSpline
    → dense UV samples (default 32×32)
    → map UV → [0,1]^2
    → LSQ fit degree=3, 4×4 poles, clamped uniform knots
    → re-evaluate cubic BSpline
    → Chamfer / Hausdorff vs original dense samples

If PASS (median CD_rel < 1e-3 and fit_success_rate high), rewrite
`canonical_surface.npz` with fitted poles and freeze 4×4 for Exp1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from freeform_patch_reconstruction_v1.geom import (  # noqa: E402
    chamfer_l1,
    flatten_grid,
    hausdorff95,
    load_raw_bspline,
    sample_surface_uv_grid,
)
from freeform_surface_pack_v1.canonical_fit import (  # noqa: E402
    evaluate_fitted_grid,
    fit_cubic_grid_lsq,
    map_uv_to_unit,
)

DEFAULT_PACK = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"
DENSE_N = 32
GRID_N = 4
DEGREE = 3
# Gate thresholds
MEDIAN_CD_REL_MAX = 1e-3
FIT_SUCCESS_RATE_MIN = 0.95


def fit_one(sample_dir: Path, *, write: bool) -> dict:
    raw_path = sample_dir / "surface_raw.npz"
    surf, bounds, raw = load_raw_bspline(raw_path)
    dense = sample_surface_uv_grid(surf, bounds, DENSE_N, DENSE_N, with_normals=False)
    gt_pts = flatten_grid(dense["points"])
    # Build (u,v) list in original param domain
    us, vs = dense["us"], dense["vs"]
    uv = np.array([(u, v) for u in us for v in vs], dtype=np.float64)
    uv_unit = map_uv_to_unit(uv, bounds)

    diag = float(np.linalg.norm(gt_pts.max(0) - gt_pts.min(0)))
    if diag <= 1e-12 or not np.isfinite(gt_pts).all():
        return {"sample_id": sample_dir.name, "ok": False, "error": "degenerate_gt"}

    try:
        fit = fit_cubic_grid_lsq(uv_unit, gt_pts, n_u=GRID_N, n_v=GRID_N, degree=DEGREE)
    except Exception as exc:  # noqa: BLE001
        return {"sample_id": sample_dir.name, "ok": False, "error": f"fit:{type(exc).__name__}: {exc}"}

    if not np.isfinite(fit["poles"]).all():
        return {"sample_id": sample_dir.name, "ok": False, "error": "nan_poles"}

    pred_pts = evaluate_fitted_grid(fit["poles"], degree=DEGREE, nu_eval=DENSE_N, nv_eval=DENSE_N)
    cd = chamfer_l1(pred_pts, gt_pts)
    hd = hausdorff95(pred_pts, gt_pts)
    row = {
        "sample_id": sample_dir.name,
        "ok": True,
        "bbox_diag": diag,
        "chamfer": cd,
        "chamfer_rel": cd / diag,
        "hausdorff95": hd,
        "hausdorff95_rel": hd / diag,
        "fit_point_rmse": fit["point_rmse"],
        "fit_point_rmse_rel": fit["point_rmse"] / diag,
        "raw_poles": list(np.asarray(raw["poles"]).shape[:2]),
        "raw_degree": [
            int(np.asarray(raw["degree_u"]).reshape(-1)[0]),
            int(np.asarray(raw["degree_v"]).reshape(-1)[0]),
        ],
    }

    if write:
        np.savez_compressed(
            sample_dir / "canonical_surface.npz",
            degree_u=np.asarray([DEGREE], dtype=np.int32),
            degree_v=np.asarray([DEGREE], dtype=np.int32),
            poles=fit["poles"].astype(np.float64),
            weights=fit["weights"].astype(np.float64),
            u_knots=fit["u_knots"],
            v_knots=fit["v_knots"],
            u_multiplicities=fit["u_multiplicities"],
            v_multiplicities=fit["v_multiplicities"],
            uv_bounds=np.asarray(bounds, dtype=np.float64),  # original surface UV
            uv_domain=fit["uv_domain"],  # fitted param domain [0,1]^2
            representation=np.asarray(["lsq_cubic_clamped_open_4x4"]),
            fit_point_rmse=np.asarray([fit["point_rmse"]], dtype=np.float64),
            chamfer_rel=np.asarray([row["chamfer_rel"]], dtype=np.float64),
            hausdorff95_rel=np.asarray([row["hausdorff95_rel"]], dtype=np.float64),
        )
        # Keep a sidecar for the old UV-sample-as-poles artifact if present name differs
        meta_path = sample_dir / "surface_meta.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["canonical"] = {
                "degree": DEGREE,
                "grid": [GRID_N, GRID_N],
                "representation": "lsq_cubic_clamped_open_4x4",
                "chamfer_rel": row["chamfer_rel"],
                "hausdorff95_rel": row["hausdorff95_rel"],
            }
            meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--write", action="store_true", help="Rewrite canonical_surface.npz with LSQ poles")
    ap.add_argument("--dry-run", action="store_true", help="Audit only, do not write")
    args = ap.parse_args()
    write = args.write and not args.dry_run

    man = json.loads((args.pack_dir / "manifest.json").read_text(encoding="utf-8"))
    ids = [s["sample_id"] for s in man["samples"]]
    if args.limit is not None:
        ids = ids[: args.limit]

    rows = []
    for i, sid in enumerate(ids):
        row = fit_one(args.pack_dir / "samples" / sid, write=write)
        rows.append(row)
        if (i + 1) % 50 == 0 or i == 0 or i + 1 == len(ids):
            if row.get("ok"):
                print(
                    f"[{i + 1}/{len(ids)}] {sid} cd_rel={row['chamfer_rel']:.3e} "
                    f"hd_rel={row['hausdorff95_rel']:.3e}",
                    flush=True,
                )
            else:
                print(f"[{i + 1}/{len(ids)}] FAIL {sid}: {row.get('error')}", flush=True)

    ok = [r for r in rows if r.get("ok")]
    fail = [r for r in rows if not r.get("ok")]
    cds = np.array([r["chamfer_rel"] for r in ok], dtype=np.float64)
    hds = np.array([r["hausdorff95_rel"] for r in ok], dtype=np.float64)

    summary = {
        "gate": "CANONICAL_4X4_FIT_GATE",
        "CANONICAL_GRID": f"{GRID_N}x{GRID_N}",
        "DEGREE_U": DEGREE,
        "DEGREE_V": DEGREE,
        "DENSE_SAMPLES": f"{DENSE_N}x{DENSE_N}",
        "representation": "lsq_cubic_clamped_open (NOT uv-sample-as-poles)",
        "n_requested": len(ids),
        "n_ok": len(ok),
        "n_failed": len(fail),
        "FIT_SUCCESS_RATE": len(ok) / max(len(ids), 1),
        "MEDIAN_CHAMFER_REL": float(np.median(cds)) if len(cds) else None,
        "P95_CHAMFER_REL": float(np.percentile(cds, 95)) if len(cds) else None,
        "MEDIAN_HAUSDORFF_REL": float(np.median(hds)) if len(hds) else None,
        "P95_HAUSDORFF_REL": float(np.percentile(hds, 95)) if len(hds) else None,
        "MEAN_CHAMFER_REL": float(np.mean(cds)) if len(cds) else None,
        "wrote_canonical_npz": write,
        "failures_head": fail[:30],
        "thresholds": {
            "MEDIAN_CHAMFER_REL_MAX": MEDIAN_CD_REL_MAX,
            "FIT_SUCCESS_RATE_MIN": FIT_SUCCESS_RATE_MIN,
        },
    }
    passed = (
        summary["FIT_SUCCESS_RATE"] >= FIT_SUCCESS_RATE_MIN
        and summary["MEDIAN_CHAMFER_REL"] is not None
        and summary["MEDIAN_CHAMFER_REL"] < MEDIAN_CD_REL_MAX
    )
    summary["CURRENT_GATE"] = (
        "CANONICAL_4X4_FIT_GATE_PASS" if passed else "CANONICAL_4X4_FIT_GATE_FAIL"
    )

    out_json = args.pack_dir / "canonical_4x4_fit_gate.json"
    out_md = args.pack_dir / "canonical_4x4_fit_gate.md"
    payload = {**summary, "samples": rows}
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# CANONICAL_4X4_FIT_GATE",
        "",
        f"- CURRENT_GATE = **{summary['CURRENT_GATE']}**",
        f"- CANONICAL_GRID = **{summary['CANONICAL_GRID']}**",
        f"- DEGREE_U/V = **{DEGREE}/{DEGREE}**",
        f"- representation = `{summary['representation']}`",
        f"- FIT_SUCCESS_RATE = **{summary['FIT_SUCCESS_RATE']:.4f}** ({len(ok)}/{len(ids)})",
        f"- MEDIAN_CHAMFER_REL = **{summary['MEDIAN_CHAMFER_REL']:.6g}**",
        f"- P95_CHAMFER_REL = **{summary['P95_CHAMFER_REL']:.6g}**",
        f"- MEDIAN_HAUSDORFF_REL = **{summary['MEDIAN_HAUSDORFF_REL']:.6g}**",
        f"- P95_HAUSDORFF_REL = **{summary['P95_HAUSDORFF_REL']:.6g}**",
        f"- wrote_canonical_npz = **{write}**",
        "",
        "Pass rule: `FIT_SUCCESS_RATE >= 0.95` and `MEDIAN_CHAMFER_REL < 1e-3`.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in summary if k != "failures_head"}, indent=2))
    print(f"wrote {out_md}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
