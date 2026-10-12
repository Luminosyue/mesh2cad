#!/usr/bin/env python3
"""Curve-fitting baseline: observed edge points -> predicted parametric curve.

This is the *input* side of Track B, not the ground truth. Exact GT always comes
from the CAD kernel; this module exists only to establish the benchmark

    Observed Edge Points -> Predicted Curve -> Exact B-Rep Curve GT

so a future Curve Encoder can be compared against classical fitting. Nothing here
feeds back into the dataset.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .config import FITTING_DIR, SPLITS, cad_dir, split_dir
from .curve_eval import evaluate


# ------------------------------------------------------------- primitives ----
def fit_line(pts: np.ndarray) -> dict:
    """Total least squares line through the point set."""
    c = pts.mean(axis=0)
    q = pts - c
    _, _, vh = np.linalg.svd(q, full_matrices=False)
    d = vh[0]
    d = d / np.linalg.norm(d)
    ts = q @ d
    # anchor the origin at the first sample so the fit is comparable to a
    # B-Rep edge whose parameterisation starts at its start vertex
    if ts[-1] < ts[0]:
        d = -d
        ts = -ts
    origin = c + ts.min() * d
    resid = np.linalg.norm(q - np.outer(ts, d), axis=1)
    return {
        "curve_type": "LINE",
        "origin": origin.tolist(),
        "direction": d.tolist(),
        "u_start": 0.0,
        "u_end": float(ts.max() - ts.min()),
        "rms_residual": float(np.sqrt((resid**2).mean())),
        "max_residual": float(resid.max()),
    }


def _fit_plane(pts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    c = pts.mean(axis=0)
    _, _, vh = np.linalg.svd(pts - c, full_matrices=False)
    e1, e2, n = vh[0], vh[1], vh[2]
    return c, e1 / np.linalg.norm(e1), e2 / np.linalg.norm(e2), n / np.linalg.norm(n)


def fit_circle(pts: np.ndarray) -> dict:
    """Plane fit by PCA, then an algebraic (Kasa) circle fit in the plane."""
    c0, e1, e2, n = _fit_plane(pts)
    q = pts - c0
    x, y = q @ e1, q @ e2
    A = np.column_stack([x, y, np.ones_like(x)])
    b = x**2 + y**2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = 0.5 * sol[0], 0.5 * sol[1]
    r2 = sol[2] + cx**2 + cy**2
    if not np.isfinite(r2) or r2 <= 0:
        return {"curve_type": "CIRCLE", "ok": False, "reason": "non-positive radius"}
    r = float(np.sqrt(r2))
    center = c0 + cx * e1 + cy * e2

    # keep x_axis pointing at the first observed sample so the angular origin is
    # reproducible rather than an arbitrary PCA axis
    v0 = pts[0] - center
    v0 -= np.dot(v0, n) * n
    nv = np.linalg.norm(v0)
    x_axis = v0 / nv if nv > 1e-12 else e1
    y_axis = np.cross(n, x_axis)

    radial = np.linalg.norm(pts - center, axis=1)
    out_of_plane = np.abs((pts - center) @ n)
    resid = np.sqrt((radial - r) ** 2 + out_of_plane**2)
    ang = np.arctan2((pts - center) @ y_axis, (pts - center) @ x_axis)
    return {
        "curve_type": "CIRCLE",
        "ok": True,
        "center": center.tolist(),
        "normal": n.tolist(),
        "x_axis": x_axis.tolist(),
        "y_axis": y_axis.tolist(),
        "radius": r,
        "u_start": float(ang.min()),
        "u_end": float(ang.max()),
        "rms_residual": float(np.sqrt((resid**2).mean())),
        "max_residual": float(resid.max()),
    }


def fit_ellipse(pts: np.ndarray) -> dict:
    """Plane fit by PCA, then a general conic fit constrained to ellipses."""
    c0, e1, e2, n = _fit_plane(pts)
    q = pts - c0
    x, y = q @ e1, q @ e2
    scale = float(max(np.abs(x).max(), np.abs(y).max(), 1e-12))
    x, y = x / scale, y / scale

    D = np.column_stack([x**2, x * y, y**2, x, y, np.ones_like(x)])
    _, _, vh = np.linalg.svd(D, full_matrices=False)
    a, b, c, d, e, f = vh[-1]

    m = np.array([[a, b / 2], [b / 2, c]])
    disc = b**2 - 4 * a * c
    if disc >= 0:
        return {"curve_type": "ELLIPSE", "ok": False, "reason": "conic is not an ellipse"}
    try:
        cen2 = np.linalg.solve(2 * m, np.array([-d, -e]))
    except np.linalg.LinAlgError:
        return {"curve_type": "ELLIPSE", "ok": False, "reason": "singular conic"}

    const = a * cen2[0] ** 2 + b * cen2[0] * cen2[1] + c * cen2[1] ** 2 + d * cen2[0] + e * cen2[1] + f
    if abs(const) < 1e-300:
        return {"curve_type": "ELLIPSE", "ok": False, "reason": "degenerate conic"}
    evals, evecs = np.linalg.eigh(m / -const)
    if np.any(evals <= 0):
        return {"curve_type": "ELLIPSE", "ok": False, "reason": "non-positive eigenvalues"}
    radii = 1.0 / np.sqrt(evals)
    order = np.argsort(radii)[::-1]
    ra, rb = float(radii[order[0]] * scale), float(radii[order[1]] * scale)
    ax_maj2, ax_min2 = evecs[:, order[0]], evecs[:, order[1]]

    center = c0 + (cen2[0] * scale) * e1 + (cen2[1] * scale) * e2
    major = ax_maj2[0] * e1 + ax_maj2[1] * e2
    major /= np.linalg.norm(major)
    minor = np.cross(n, major)

    params = {"center": center, "major_axis": major, "minor_axis": minor,
              "major_radius": ra, "minor_radius": rb}
    rel = pts - center
    u = np.arctan2(rel @ minor / max(rb, 1e-300), rel @ major / max(ra, 1e-300))
    pred = evaluate("ELLIPSE", {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                                for k, v in params.items()} | {"normal": n.tolist()}, u)
    resid = np.linalg.norm(pred - pts, axis=1)
    return {
        "curve_type": "ELLIPSE",
        "ok": True,
        "center": center.tolist(),
        "normal": n.tolist(),
        "major_axis": major.tolist(),
        "minor_axis": minor.tolist(),
        "major_radius": ra,
        "minor_radius": rb,
        "u_start": float(u.min()),
        "u_end": float(u.max()),
        "rms_residual": float(np.sqrt((resid**2).mean())),
        "max_residual": float(resid.max()),
    }


def fit_bspline(pts: np.ndarray, tol: float, degree_max: int = 8) -> dict:
    """Approximating B-spline through the observed points (OCC GeomAPI)."""
    from OCP.GeomAbs import GeomAbs_C2
    from OCP.GeomAPI import GeomAPI_PointsToBSpline
    from OCP.TColgp import TColgp_Array1OfPnt
    from OCP.gp import gp_Pnt

    n = pts.shape[0]
    arr = TColgp_Array1OfPnt(1, n)
    for i in range(n):
        arr.SetValue(i + 1, gp_Pnt(*[float(v) for v in pts[i]]))
    try:
        approx = GeomAPI_PointsToBSpline(
            arr, 3, int(max(3, min(8, degree_max))), GeomAbs_C2, float(tol)
        )
        if not approx.IsDone():
            return {"curve_type": "BSPLINE", "ok": False, "reason": "approximation did not converge"}
        bs = approx.Curve()
    except Exception as exc:  # noqa: BLE001
        return {"curve_type": "BSPLINE", "ok": False, "reason": f"{type(exc).__name__}: {exc}"}

    from .occ_curve_v1 import pnt_to_np

    npoles = int(bs.NbPoles())
    resid = []
    u0, u1 = float(bs.FirstParameter()), float(bs.LastParameter())
    from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve

    for p in pts:
        proj = GeomAPI_ProjectPointOnCurve(gp_Pnt(*[float(v) for v in p]), bs)
        resid.append(float(proj.LowerDistance()) if proj.NbPoints() else float("nan"))
    resid_a = np.asarray(resid, dtype=np.float64)
    return {
        "curve_type": "BSPLINE",
        "ok": True,
        "degree": int(bs.Degree()),
        "num_control_points": npoles,
        "num_knots": int(bs.NbKnots()),
        "u_start": u0,
        "u_end": u1,
        "control_points": [pnt_to_np(bs.Pole(i)).tolist() for i in range(1, npoles + 1)],
        "rms_residual": float(np.sqrt(np.nanmean(resid_a**2))),
        "max_residual": float(np.nanmax(resid_a)),
    }


# ------------------------------------------------------------- benchmark -----
def benchmark_cad(split: str, cad_id: str, noise_rel: float = 0.0, seed: int = 0) -> dict:
    """Fit every GT curve from its own sampled points and score against exact GT."""
    d = cad_dir(split, cad_id)
    data = json.loads((d / "curves.json").read_text(encoding="utf-8"))
    npz = np.load(d / "curve_samples.npz", allow_pickle=False)
    xyz = npz["curve_xyz"].astype(np.float64)
    mask = npz["curve_mask"]
    diag = float(data["source_diagonal"])
    rng = np.random.default_rng(seed)

    rows: list[dict] = []
    for i, rec in enumerate(data["curves"]):
        ctype = rec["curve_type"]
        pts = xyz[i][mask[i]]
        if pts.shape[0] < 4:
            rows.append({"edge_id": rec["edge_id"], "curve_type": ctype, "ok": False,
                         "reason": "too few observed points"})
            continue
        if noise_rel > 0:
            pts = pts + rng.normal(scale=noise_rel * diag, size=pts.shape)

        gt = rec["world_parameters"]
        row: dict = {"edge_id": rec["edge_id"], "curve_type": ctype, "gt_length": rec["length"]}
        if ctype == "LINE":
            f = fit_line(pts)
            row.update(
                ok=True,
                fit_type="LINE",
                direction_angle_err_deg=_ang(f["direction"], gt["direction"]),
                # a line's origin is gauge-dependent, so score endpoint recovery instead
                endpoint_err=min(
                    np.linalg.norm(np.asarray(f["origin"]) - np.asarray(rec["start_point"])),
                    np.linalg.norm(np.asarray(f["origin"]) - np.asarray(rec["end_point"])),
                ),
                length_rel_err=abs(f["u_end"] - rec["length"]) / max(rec["length"], 1e-12),
                rms_residual=f["rms_residual"],
            )
        elif ctype == "CIRCLE":
            f = fit_circle(pts)
            if not f.get("ok"):
                row.update(ok=False, fit_type="CIRCLE", reason=f.get("reason"))
            else:
                row.update(
                    ok=True,
                    fit_type="CIRCLE",
                    center_err=float(np.linalg.norm(np.asarray(f["center"]) - np.asarray(gt["center"]))),
                    radius_err=abs(f["radius"] - gt["radius"]),
                    radius_rel_err=abs(f["radius"] - gt["radius"]) / max(gt["radius"], 1e-12),
                    normal_angle_err_deg=_ax_ang(f["normal"], gt["normal"]),
                    rms_residual=f["rms_residual"],
                )
        elif ctype == "ELLIPSE":
            f = fit_ellipse(pts)
            if not f.get("ok"):
                row.update(ok=False, fit_type="ELLIPSE", reason=f.get("reason"))
            else:
                row.update(
                    ok=True,
                    fit_type="ELLIPSE",
                    center_err=float(np.linalg.norm(np.asarray(f["center"]) - np.asarray(gt["center"]))),
                    major_radius_err=abs(f["major_radius"] - gt["major_radius"]),
                    minor_radius_err=abs(f["minor_radius"] - gt["minor_radius"]),
                    normal_angle_err_deg=_ax_ang(f["normal"], gt["normal"]),
                    major_axis_angle_err_deg=_ax_ang(f["major_axis"], gt["major_axis"]),
                    rms_residual=f["rms_residual"],
                )
        else:
            f = fit_bspline(pts, tol=1e-4 * diag)
            if not f.get("ok"):
                row.update(ok=False, fit_type="BSPLINE", reason=f.get("reason"))
            else:
                row.update(
                    ok=True,
                    fit_type="BSPLINE",
                    gt_degree=gt.get("degree"),
                    gt_num_control_points=gt.get("num_control_points"),
                    fit_degree=f["degree"],
                    fit_num_control_points=f["num_control_points"],
                    rms_residual=f["rms_residual"],
                    max_residual=f["max_residual"],
                )
        rows.append(row)
    return {"split": split, "cad_id": cad_id, "source_diagonal": diag,
            "noise_rel": noise_rel, "rows": rows}


def _ang(a, b) -> float:
    a = np.asarray(a, float) / np.linalg.norm(a)
    b = np.asarray(b, float) / np.linalg.norm(b)
    ang = np.degrees(np.arccos(np.clip(abs(float(a @ b)), -1, 1)))
    return float(ang)


def _ax_ang(a, b) -> float:
    return _ang(a, b)


def summarize(reports: list[dict]) -> dict:
    per_type: dict[str, dict] = {}
    for rep in reports:
        diag = rep["source_diagonal"]
        for row in rep["rows"]:
            ct = row["curve_type"]
            bucket = per_type.setdefault(ct, {"n": 0, "n_ok": 0, "metrics": {}})
            bucket["n"] += 1
            if not row.get("ok"):
                continue
            bucket["n_ok"] += 1
            for k, v in row.items():
                if not isinstance(v, float) or k in ("gt_length",):
                    continue
                key = f"{k}_rel" if k.endswith(("_err", "residual")) and not k.endswith("_rel_err") and not k.endswith("_deg") else k
                val = v / diag if key.endswith("_rel") and diag > 0 else v
                bucket["metrics"].setdefault(key, []).append(val)

    out: dict = {}
    for ct, b in per_type.items():
        m = {}
        for k, vals in b["metrics"].items():
            a = np.asarray(vals, dtype=np.float64)
            a = a[np.isfinite(a)]
            if not a.size:
                continue
            m[k] = {
                "mean": float(a.mean()),
                "median": float(np.median(a)),
                "p95": float(np.percentile(a, 95)),
                "max": float(a.max()),
            }
        out[ct] = {
            "n_curves": b["n"],
            "n_fitted": b["n_ok"],
            "fit_success_rate_pct": 100.0 * b["n_ok"] / max(b["n"], 1),
            "metrics": m,
        }
    return out


def write_report(summary: dict, reports: list[dict], tag: str) -> tuple[Path, Path]:
    FITTING_DIR.mkdir(parents=True, exist_ok=True)
    jpath = FITTING_DIR / f"fitting_baseline_{tag}.json"
    mpath = FITTING_DIR / f"fitting_baseline_{tag}.md"
    jpath.write_text(
        json.dumps({"summary": summary, "per_cad": reports}, indent=2), encoding="utf-8"
    )
    lines = [
        f"# Curve fitting baseline ({tag})",
        "",
        "Benchmark direction: **observed edge points -> predicted curve -> exact B-Rep GT**.",
        "Errors ending in `_rel` are normalised by the object's bbox diagonal.",
        "This baseline never contributes to the ground truth; it only measures how much",
        "a classical fitter recovers, as the reference a Curve Encoder must beat.",
        "",
    ]
    for ct, b in sorted(summary.items()):
        lines += [
            f"## {ct}",
            "",
            f"- curves: {b['n_curves']}, fitted: {b['n_fitted']} ({b['fit_success_rate_pct']:.2f}%)",
            "",
            "| metric | mean | median | P95 | max |",
            "|---|---|---|---|---|",
        ]
        for k, v in sorted(b["metrics"].items()):
            lines.append(
                f"| {k} | {v['mean']:.4e} | {v['median']:.4e} | {v['p95']:.4e} | {v['max']:.4e} |"
            )
        lines.append("")
    mpath.write_text("\n".join(lines), encoding="utf-8")
    return jpath, mpath


def main() -> int:
    ap = argparse.ArgumentParser(description="Curve fitting baseline (edge points -> curve)")
    ap.add_argument("--split", default="deepcad_train")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--noise-rel", type=float, default=0.0)
    ap.add_argument("--tag", default="canary")
    args = ap.parse_args()

    root = split_dir(args.split)
    ids = [d.name for d in sorted(root.iterdir()) if (d / "curves.json").is_file()]
    ids = ids[: args.limit]
    reports = [benchmark_cad(args.split, cid, args.noise_rel) for cid in ids]
    summary = summarize(reports)
    jp, mp = write_report(summary, reports, args.tag)
    print(json.dumps({k: {"n": v["n_curves"], "ok%": round(v["fit_success_rate_pct"], 2)}
                      for k, v in summary.items()}, indent=2))
    print(f"-> {jp}\n-> {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
