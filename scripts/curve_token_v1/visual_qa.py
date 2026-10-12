#!/usr/bin/env python3
"""Visual QA: overlay the original B-Rep edge, the curve rebuilt from the saved
parameters, and the stored sampled points.

Three layers per figure so position, direction, arc range, radius, ellipse
orientation and B-spline shape can all be inspected by eye:

  1. original B-Rep edge   -- dense evaluation of the OCC curve (grey, thick)
  2. rebuilt curve         -- from curves.json parameters only (coloured, dashed)
  3. sampled curve points  -- from curve_samples.npz (dots + tangent quivers)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_curve_token_v1")

import matplotlib
import mpl_toolkits

# A stale system mpl_toolkits (/usr/lib/python3/dist-packages) shadows the one
# shipped with the installed matplotlib, which breaks projection="3d". Point the
# namespace package at matplotlib's own sibling instead of touching site-packages.
_sibling = Path(matplotlib.__file__).resolve().parents[1] / "mpl_toolkits"
if _sibling.is_dir() and str(_sibling) not in mpl_toolkits.__path__:
    mpl_toolkits.__path__.insert(0, str(_sibling))

matplotlib.use("Agg")
from mpl_toolkits.mplot3d import Axes3D  # noqa: E402,F401  (registers the 3d projection)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .config import SPLITS, STEP_FILENAME, VISUAL_QA_DIR, cad_dir, split_dir  # noqa: E402
from .curve_eval import UnsupportedCurve, evaluate  # noqa: E402
from .occ_curve_v1 import eval_point, load_step_shape, make_adaptor, rebuild_occ_curve  # noqa: E402

TYPE_COLOR = {
    "LINE": "#1f77b4",
    "CIRCLE": "#d62728",
    "ELLIPSE": "#9467bd",
    "BSPLINE": "#2ca02c",
    "BEZIER": "#ff7f0e",
}
N_DENSE = 120


def _rebuilt_points(ctype: str, params: dict, us: np.ndarray, u0: float, u1: float):
    """Prefer the OCC-free evaluator; fall back to the kernel rebuild."""
    try:
        return evaluate(ctype, params, us), "numpy"
    except (UnsupportedCurve, Exception):  # noqa: BLE001
        pass
    try:
        geom = rebuild_occ_curve(ctype, params)
        from .occ_curve_v1 import pnt_to_np

        periodic = bool(params.get("is_periodic", False)) or ctype in ("CIRCLE", "ELLIPSE")
        lo, hi = float(geom.FirstParameter()), float(geom.LastParameter())
        out = []
        for u in us:
            uu = float(u) if periodic else float(np.clip(u, lo, hi))
            out.append(pnt_to_np(geom.Value(uu)))
        return np.asarray(out), "occ"
    except Exception:  # noqa: BLE001
        return None, "failed"


def _equal_aspect(ax, pts: np.ndarray) -> None:
    if pts.size == 0:
        return
    mn, mx = pts.min(axis=0), pts.max(axis=0)
    c = 0.5 * (mn + mx)
    r = float(max(mx - mn).max() if (mx - mn).size else 1.0) * 0.55 or 1.0
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)


def render_cad(split: str, cad_id: str, out_dir: Path, max_zoom_panels: int = 6) -> dict:
    d = cad_dir(split, cad_id)
    data = json.loads((d / "curves.json").read_text(encoding="utf-8"))
    npz = np.load(d / "curve_samples.npz", allow_pickle=False)
    xyz = npz["curve_xyz"].astype(np.float64)
    tan = npz["curve_tangent"].astype(np.float64)
    mask = npz["curve_mask"]

    shape = load_step_shape(SPLITS[split]["step_root"] / cad_id / STEP_FILENAME)
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp
    from OCP.TopoDS import TopoDS
    from OCP.TopTools import TopTools_IndexedMapOfShape

    emap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, emap)

    records = data["curves"]
    layers = []
    for i, rec in enumerate(records):
        ad = make_adaptor(TopoDS.Edge_s(emap.FindKey(rec["edge_id"] + 1)))
        u0, u1 = float(rec["u_start"]), float(rec["u_end"])
        us = np.linspace(u0, u1, N_DENSE)
        occ_pts = np.array([eval_point(ad, float(u)) for u in us])
        reb, how = _rebuilt_points(rec["curve_type"], rec.get("world_parameters", {}), us, u0, u1)
        layers.append(
            {
                "rec": rec,
                "occ": occ_pts,
                "reb": reb,
                "how": how,
                "samp": xyz[i][mask[i]],
                "tan": tan[i][mask[i]],
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    all_pts = np.concatenate([l["occ"] for l in layers], axis=0)

    # ---------------- whole-object overlay ----------------
    fig = plt.figure(figsize=(19, 6.4))
    for k, (elev, azim, title) in enumerate(
        [(24, -60, "view 1"), (24, 30, "view 2"), (78, -60, "top view")]
    ):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d")
        for l in layers:
            ct = l["rec"]["curve_type"]
            col = TYPE_COLOR.get(ct, "#7f7f7f")
            ax.plot(*l["occ"].T, color="0.55", lw=4.0, alpha=0.55, solid_capstyle="round")
            if l["reb"] is not None:
                ax.plot(*l["reb"].T, color=col, lw=1.5, ls="--")
            if l["samp"].size:
                ax.scatter(*l["samp"].T, color=col, s=3.5, depthshade=False)
        _equal_aspect(ax, all_pts)
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("x", fontsize=8)
        ax.set_ylabel("y", fontsize=8)
        ax.tick_params(labelsize=6)

    counts = data["curve_type_counts"]
    handles = [
        plt.Line2D([], [], color="0.55", lw=4, label="original B-Rep edge (OCC)"),
        plt.Line2D([], [], color="k", lw=1.5, ls="--", label="rebuilt from saved parameters"),
        plt.Line2D([], [], color="k", marker="o", ls="", ms=3, label="sampled curve points (npz)"),
    ] + [
        plt.Line2D([], [], color=TYPE_COLOR.get(ct, "#7f7f7f"), lw=3, label=f"{ct} x{n}")
        for ct, n in sorted(counts.items())
    ]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(handles), 7), fontsize=8, frameon=False)
    fig.suptitle(
        f"{split}/{cad_id}  --  {data['num_curves']} curves, "
        f"{data['num_faces']} faces, {data['num_vertices']} vertices",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    overview = out_dir / f"{cad_id}_overview.png"
    fig.savefig(overview, dpi=130)
    plt.close(fig)

    # ---------------- per-curve zoom panels ----------------
    # one panel per curve type, preferring the longest instance of each so
    # arc range / radius / orientation are actually legible
    picks: list[dict] = []
    by_type: dict[str, list[dict]] = {}
    for l in layers:
        by_type.setdefault(l["rec"]["curve_type"], []).append(l)
    for ct in ("BSPLINE", "ELLIPSE", "CIRCLE", "BEZIER", "LINE"):
        for l in sorted(by_type.get(ct, []), key=lambda x: -x["rec"]["length"])[:2]:
            picks.append(l)
    picks = picks[:max_zoom_panels]

    zoom = None
    if picks:
        cols = min(3, len(picks))
        rows = int(np.ceil(len(picks) / cols))
        fig = plt.figure(figsize=(6.0 * cols, 5.4 * rows))
        for k, l in enumerate(picks):
            rec = l["rec"]
            ax = fig.add_subplot(rows, cols, k + 1, projection="3d")
            ax.plot(*l["occ"].T, color="0.55", lw=6, alpha=0.6, label="B-Rep edge (OCC)")
            if l["reb"] is not None:
                ax.plot(
                    *l["reb"].T,
                    color=TYPE_COLOR.get(rec["curve_type"], "k"),
                    lw=1.8,
                    ls="--",
                    label=f"rebuilt ({l['how']})",
                )
            if l["samp"].size:
                ax.scatter(*l["samp"].T, color="k", s=14, depthshade=False, label="sampled points")
                step = max(1, len(l["samp"]) // 12)
                span = float(np.linalg.norm(l["occ"].max(0) - l["occ"].min(0))) or 1.0
                ax.quiver(
                    *l["samp"][::step].T,
                    *l["tan"][::step].T,
                    length=0.10 * span,
                    color="#ff7f0e",
                    lw=1.0,
                    normalize=True,
                )
            sp = np.asarray(rec["start_point"])
            ep = np.asarray(rec["end_point"])
            ax.scatter(*sp, color="lime", s=70, marker="^", depthshade=False, label="start")
            ax.scatter(*ep, color="red", s=70, marker="v", depthshade=False, label="end")

            p = rec.get("world_parameters", {})
            info = [f"edge {rec['edge_id']}  {rec['curve_type']}",
                    f"u=[{rec['u_start']:.4f}, {rec['u_end']:.4f}]  len={rec['length']:.4f}",
                    f"closed={rec['is_closed']}  faces={rec['face_ids']}"]
            if rec["curve_type"] == "CIRCLE":
                info.append(f"r={p['radius']:.5f}")
                info.append(f"arc={np.degrees(rec['u_end'] - rec['u_start']):.2f} deg")
            elif rec["curve_type"] == "ELLIPSE":
                info.append(f"ra={p['major_radius']:.5f}  rb={p['minor_radius']:.5f}")
                info.append(f"arc={np.degrees(rec['u_end'] - rec['u_start']):.2f} deg")
            elif rec["curve_type"] in ("BSPLINE", "BEZIER"):
                info.append(
                    f"deg={p['degree']}  cp={p['num_control_points']}  knots={p['num_knots']}"
                )
                info.append(f"rational={p['is_rational']}  periodic={p['is_periodic']}")
                cp = np.asarray(p["control_points"], dtype=np.float64)
                ax.plot(*cp.T, color="#8c564b", lw=0.8, ls=":", marker=".", ms=3,
                        alpha=0.8, label="control polygon")
            err = rec["extraction"]["recon_max_err"]
            if err is not None:
                info.append(f"recon max err = {err:.2e}")
            ax.set_title("\n".join(info), fontsize=8, loc="left")
            _equal_aspect(ax, l["occ"])
            ax.tick_params(labelsize=6)
            if k == 0:
                ax.legend(fontsize=6, loc="upper right")
        fig.suptitle(f"{split}/{cad_id}  --  per-curve reconstruction check", fontsize=13)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        zoom = out_dir / f"{cad_id}_curves.png"
        fig.savefig(zoom, dpi=130)
        plt.close(fig)

    return {
        "cad_id": cad_id,
        "split": split,
        "overview": str(overview),
        "zoom": str(zoom) if zoom else None,
        "num_curves": data["num_curves"],
        "type_counts": counts,
        "rebuild_backends": sorted({l["how"] for l in layers}),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Visual QA for Track B curves")
    ap.add_argument("--split", default="deepcad_train")
    ap.add_argument("--cad-id", action="append", default=None)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--tag", default="canary")
    args = ap.parse_args()

    out_dir = VISUAL_QA_DIR / args.tag
    ids = args.cad_id
    if not ids:
        root = split_dir(args.split)
        ids = [d.name for d in sorted(root.iterdir()) if (d / "curves.json").is_file()][: args.limit]

    infos = []
    for cid in ids:
        try:
            infos.append(render_cad(args.split, cid, out_dir))
            print(f"[visual_qa] {cid} ok")
        except Exception as exc:  # noqa: BLE001
            print(f"[visual_qa] {cid} FAILED: {type(exc).__name__}: {exc}")
    (out_dir / "index.json").write_text(json.dumps(infos, indent=2), encoding="utf-8")
    print(f"-> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
