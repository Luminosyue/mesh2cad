#!/usr/bin/env python3
"""Canonical grid audit: 4×4 / 6×6 / 8×8 UV-grid → cubic BSpline vs GT surface.

For each BSpline patch in freeform_surface_pack_v1:
  1. Rebuild raw Geom_BSplineSurface from surface_raw.npz
  2. Dense-sample GT on a fine UV grid
  3. For each N in {4,6,8}:
       - sample N×N points on the raw surface (UV-grid poles)
       - treat them as cubic clamped BSpline control points
       - dense-sample the reconstructed surface
       - report Chamfer / Hausdorff95 / NormalConsistency

Also reports a bilinear densify baseline (interpolation lower bound).

Output:
  freeform_surface_pack_v1/canonical_grid_audit.{json,md}
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
    build_bspline_from_poles,
    chamfer_l1,
    flatten_grid,
    hausdorff95,
    load_raw_bspline,
    normal_consistency,
    sample_surface_uv_grid,
)
from freeform_surface_pack_v1.constants import CANONICAL_DEGREE  # noqa: E402

DEFAULT_PACK = ROOT / "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1"
GRID_SIZES = (4, 6, 8)
DENSE_N = 32  # 32×32 = 1024 eval points


def bilinear_densify(grid: np.ndarray, out_u: int, out_v: int) -> np.ndarray:
    """Bilinear upsample of an (nu,nv,3) sample grid — interpolation lower bound."""
    nu, nv, _ = grid.shape
    us = np.linspace(0, nu - 1, out_u)
    vs = np.linspace(0, nv - 1, out_v)
    out = np.zeros((out_u, out_v, 3), dtype=np.float64)
    for i, u in enumerate(us):
        u0 = int(np.floor(u))
        u1 = min(u0 + 1, nu - 1)
        tu = u - u0
        for j, v in enumerate(vs):
            v0 = int(np.floor(v))
            v1 = min(v0 + 1, nv - 1)
            tv = v - v0
            p00 = grid[u0, v0]
            p10 = grid[u1, v0]
            p01 = grid[u0, v1]
            p11 = grid[u1, v1]
            out[i, j] = (
                (1 - tu) * (1 - tv) * p00
                + tu * (1 - tv) * p10
                + (1 - tu) * tv * p01
                + tu * tv * p11
            )
    return out


def audit_one(sample_dir: Path) -> dict | None:
    raw_path = sample_dir / "surface_raw.npz"
    if not raw_path.is_file():
        return None
    try:
        surf, bounds, raw = load_raw_bspline(raw_path)
    except Exception as exc:  # noqa: BLE001
        return {"sample_id": sample_dir.name, "error": f"{type(exc).__name__}: {exc}"}

    gt = sample_surface_uv_grid(surf, bounds, DENSE_N, DENSE_N, with_normals=True)
    gt_pts = flatten_grid(gt["points"])
    gt_n = flatten_grid(gt["normals"])
    diag = float(np.linalg.norm(gt_pts.max(0) - gt_pts.min(0)))
    if diag <= 1e-12:
        return {"sample_id": sample_dir.name, "error": "degenerate_bbox"}

    raw_poles = np.asarray(raw["poles"])
    result = {
        "sample_id": sample_dir.name,
        "raw_poles": list(raw_poles.shape[:2]),
        "raw_degree": [
            int(np.asarray(raw["degree_u"]).reshape(-1)[0]),
            int(np.asarray(raw["degree_v"]).reshape(-1)[0]),
        ],
        "bbox_diag": diag,
        "grids": {},
    }

    for n in GRID_SIZES:
        # UV-grid samples from GT surface (= current pack's canonical construction)
        samp = sample_surface_uv_grid(surf, bounds, n, n, with_normals=True)
        poles = samp["points"]  # (n,n,3)

        # A) treat as cubic BSpline control points
        try:
            recon = build_bspline_from_poles(
                poles, degree_u=CANONICAL_DEGREE, degree_v=CANONICAL_DEGREE
            )
            # recon lives in unit knot domain [0,1]^2
            unit_bounds = np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float64)
            pred = sample_surface_uv_grid(
                recon, unit_bounds, DENSE_N, DENSE_N, with_normals=True
            )
            pred_pts = flatten_grid(pred["points"])
            pred_n = flatten_grid(pred["normals"])
            cd = chamfer_l1(pred_pts, gt_pts)
            hd = hausdorff95(pred_pts, gt_pts)
            nc = normal_consistency(pred_pts, pred_n, gt_pts, gt_n)
            bsp = {
                "chamfer": cd,
                "chamfer_rel": cd / diag,
                "hausdorff95": hd,
                "hausdorff95_rel": hd / diag,
                "normal_consistency": nc,
            }
        except Exception as exc:  # noqa: BLE001
            bsp = {"error": f"{type(exc).__name__}: {exc}"}

        # B) bilinear densify of UV samples (interpolation floor)
        bi = bilinear_densify(poles, DENSE_N, DENSE_N)
        bi_pts = flatten_grid(bi)
        cd_bi = chamfer_l1(bi_pts, gt_pts)
        hd_bi = hausdorff95(bi_pts, gt_pts)
        result["grids"][f"{n}x{n}"] = {
            "bspline_ctrl": bsp,
            "bilinear_interp": {
                "chamfer": cd_bi,
                "chamfer_rel": cd_bi / diag,
                "hausdorff95": hd_bi,
                "hausdorff95_rel": hd_bi / diag,
            },
        }
    return result


def summarize(rows: list[dict]) -> dict:
    ok = [r for r in rows if "grids" in r]
    table = []
    for n in GRID_SIZES:
        key = f"{n}x{n}"
        cds, hds, ncs, cds_bi = [], [], [], []
        for r in ok:
            g = r["grids"][key]
            if "error" not in g["bspline_ctrl"]:
                cds.append(g["bspline_ctrl"]["chamfer_rel"])
                hds.append(g["bspline_ctrl"]["hausdorff95_rel"])
                ncs.append(g["bspline_ctrl"]["normal_consistency"])
            cds_bi.append(g["bilinear_interp"]["chamfer_rel"])
        table.append(
            {
                "canonical_grid": key,
                "n_ok": len(cds),
                "bspline_ctrl_chamfer_rel_median": float(np.median(cds)) if cds else None,
                "bspline_ctrl_hausdorff95_rel_median": float(np.median(hds)) if hds else None,
                "bspline_ctrl_normal_consistency_median": float(np.median(ncs)) if ncs else None,
                "bilinear_chamfer_rel_median": float(np.median(cds_bi)) if cds_bi else None,
            }
        )
    # Recommendation: pick smallest grid whose bspline chamfer is within 1.25x of 8x8
    by = {t["canonical_grid"]: t for t in table}
    ref = by["8x8"]["bspline_ctrl_chamfer_rel_median"]
    recommend = "8x8"
    if ref is not None:
        for cand in ("4x4", "6x6", "8x8"):
            v = by[cand]["bspline_ctrl_chamfer_rel_median"]
            if v is not None and v <= 1.25 * ref + 1e-12:
                recommend = cand
                break
    return {
        "n_samples": len(ok),
        "n_failed": len(rows) - len(ok),
        "table": table,
        "recommend_canonical_grid": recommend,
        "note": (
            "bspline_ctrl = UV-grid samples used as cubic clamped BSpline poles "
            "(matches current pack decoder target semantics). "
            "bilinear_interp = densify UV samples by bilinear interpolation "
            "(representation lower bound)."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument(
        "--out-json",
        type=Path,
        default=None,
    )
    ap.add_argument("--out-md", type=Path, default=None)
    args = ap.parse_args()

    man = json.loads((args.pack_dir / "manifest.json").read_text(encoding="utf-8"))
    ids = [s["sample_id"] for s in man["samples"]]
    if args.limit is not None:
        ids = ids[: args.limit]

    rows = []
    for i, sid in enumerate(ids):
        r = audit_one(args.pack_dir / "samples" / sid)
        if r is None:
            continue
        rows.append(r)
        if (i + 1) % 50 == 0 or i == 0 or i + 1 == len(ids):
            status = "ok" if "grids" in r else f"FAIL {r.get('error')}"
            print(f"[{i + 1}/{len(ids)}] {sid} {status}", flush=True)

    summary = summarize(rows)
    out = {
        "experiment": "canonical_grid_audit",
        "pack_dir": str(args.pack_dir),
        "dense_eval": f"{DENSE_N}x{DENSE_N}",
        "grid_sizes": list(GRID_SIZES),
        "summary": summary,
        "samples": rows,
    }
    out_json = args.out_json or (args.pack_dir / "canonical_grid_audit.json")
    out_md = args.out_md or (args.pack_dir / "canonical_grid_audit.md")
    out_json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Canonical grid audit (4×4 / 6×6 / 8×8)",
        "",
        f"- n_samples = **{summary['n_samples']}**",
        f"- n_failed = **{summary['n_failed']}**",
        f"- recommend_canonical_grid = **{summary['recommend_canonical_grid']}**",
        "",
        summary["note"],
        "",
        "| Canonical grid | GT refit Chamfer (rel, median) | Hausdorff95 (rel, median) | Normal consistency ↑ | Bilinear Chamfer (rel) |",
        "|---|---:|---:|---:|---:|",
    ]
    for t in summary["table"]:
        lines.append(
            f"| {t['canonical_grid']} | "
            f"{t['bspline_ctrl_chamfer_rel_median']:.6g} | "
            f"{t['bspline_ctrl_hausdorff95_rel_median']:.6g} | "
            f"{t['bspline_ctrl_normal_consistency_median']:.4f} | "
            f"{t['bilinear_chamfer_rel_median']:.6g} |"
        )
    lines += [
        "",
        f"**Recommendation:** use `{summary['recommend_canonical_grid']}` "
        "as the first reconstruction target (capacity bottleneck).",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
