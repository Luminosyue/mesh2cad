#!/usr/bin/env python3
"""Per-part Dora-sample → curve-input viz under DeepCAD/train/<id>/viz_dora_curve_v1/.

Reads existing Dora packs only. Does not regenerate Dora, STEP, or train.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_viz_deepcad_dora_curve_v1")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts")]
from dora_fitted_curve_dataset_v1 import (  # noqa: E402
    FIT_TOL_REL,
    MIN_REL_LEN,
    circlefit,
    ellipsefit,
    extract_chains,
    graph_from_dora,
    linefit,
    sample_fit,
    splinefit,
)
from viz_cad_spatial_dora_train_v1 import (  # noqa: E402
    CMAP,
    MAX_FACES,
    MAX_POINTS,
    apply_canonical,
    draw_edges,
    draw_mesh,
    load_mesh,
    normalize_verts,
    project_pts,
    subsample,
)

TRAIN = ROOT / "cad_spatial_dataset" / "DeepCAD" / "train"
FITTED = ROOT / "ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad"
VIZ_NAME = "viz_dora_curve_v1"
COL_CHAIN = "#dc2626"
COL_FIT = "#2563eb"


def list_ids() -> list[str]:
    out = []
    for d in sorted(TRAIN.iterdir()):
        if not d.is_dir():
            continue
        if (d / "dora" / "salient_edges.npz").is_file() and (d / "features_canonical.npy").is_file() and (d / "model.obj").is_file():
            out.append(d.name)
    return out


def fit_chains(chains, diag: float):
    sampled = []
    types = []
    n_skip = 0
    for ch in chains:
        p = ch["points"]
        rel = ch["length"] / max(diag, 1e-12)
        if len(p) < 2 or rel < MIN_REL_LEN or float(np.ptp(p, 0).max()) < MIN_REL_LEN * diag:
            n_skip += 1
            continue
        f = linefit(p)
        if f["rms"] / diag > FIT_TOL_REL and len(p) >= 4:
            f = circlefit(p, ch["closed_loop"])
        if (f is None or f["rms"] / diag > FIT_TOL_REL) and len(p) >= 6:
            f = ellipsefit(p, ch["closed_loop"])
        if f is None or f["rms"] / diag > FIT_TOL_REL:
            f = splinefit(p, ch["closed_loop"], diag)
        if f is None:
            n_skip += 1
            continue
        xyz, _, _, _ = sample_fit(f)
        sampled.append(np.asarray(xyz, float))
        types.append(f["type"])
    return sampled, types, n_skip


def load_fitted_from_v1(sid: str):
    p = FITTED / f"deepcad__{sid}" / "dora" / "fitted_curves.json"
    if not p.is_file():
        return None
    curves = json.loads(p.read_text())["curves"]
    out, types = [], []
    for f in curves:
        q = dict(f)
        for k in ("origin", "direction", "center", "normal", "x_axis", "y_axis", "major_axis", "minor_axis"):
            if k in q:
                q[k] = np.asarray(q[k], float)
        if q.get("type") == "BSPLINE":
            q["tck"] = [np.asarray(q["tck"][0]), np.asarray(q["tck"][1]), int(q["tck"][2])]
        xyz, _, _, _ = sample_fit(q)
        out.append(np.asarray(xyz, float))
        types.append(f["type"])
    return out, types


def render_one(sid: str, overwrite: bool = False) -> dict:
    d = TRAIN / sid
    dest = d / VIZ_NAME
    board = dest / "board.png"
    if board.is_file() and not overwrite:
        return {"sample_id": sid, "status": "skip_exists", "board": str(board)}
    dest.mkdir(exist_ok=True)
    tf = json.loads((d / "coordinate_transform.json").read_text())
    s, t = float(tf["scale"]), np.asarray(tf["translation"], float)
    mesh = load_mesh(d / "model.obj")
    verts = apply_canonical(np.asarray(mesh.vertices, float), s, t)
    faces = np.asarray(mesh.faces, int)
    feat = np.load(d / "features_canonical.npy").astype(float)
    z = np.load(d / "dora" / "salient_edges.npz")
    edge_pts = apply_canonical(np.load(d / "dora" / "edge_points.npy"), s, t)
    xyz0 = apply_canonical(z["edge_xyz0"], s, t)
    xyz1 = apply_canonical(z["edge_xyz1"], s, t)
    dih = np.asarray(z["dihedral_deg"], float)
    score = feat[:, 6]
    raw_xyz, adj, edges = graph_from_dora(z)
    chains = extract_chains(raw_xyz, adj, edges)
    for ch in chains:
        ch["points"] = apply_canonical(ch["points"], s, t)
    diag = float(np.linalg.norm(verts.max(0) - verts.min(0)))
    frozen = load_fitted_from_v1(sid)
    if frozen is not None:
        fits, ftypes = frozen
        fit_src = "train800_fitted_v1"
    else:
        fits, ftypes, _ = fit_chains(chains, diag)
        fit_src = "on_the_fly"
    _, center, scale = normalize_verts(verts)
    frac = float((score > 0.5).mean())
    fig, axes = plt.subplots(1, 4, figsize=(16.4, 4.35), dpi=120)
    draw_mesh(axes[0], verts, faces, center, scale, alpha=0.96)
    axes[0].set_title("① mesh", fontsize=10)

    draw_mesh(axes[1], verts, faces, center, scale, alpha=0.16)
    idx = subsample(len(feat), MAX_POINTS, 11)
    q = project_pts(feat[idx, :3], center, scale)
    axes[1].scatter(q[:, 0], q[:, 1], s=2.0, c=score[idx], cmap=CMAP, vmin=0, vmax=1, linewidths=0, alpha=0.8)
    axes[1].set_title(f"② Dora 8192×7  edge_score  >0.5={frac:.1%}", fontsize=9)

    draw_mesh(axes[2], verts, faces, center, scale, alpha=0.18)
    draw_edges(axes[2], xyz0, xyz1, dih, center, scale)
    show = edge_pts[subsample(len(edge_pts), MAX_POINTS, 13)]
    qe = project_pts(show, center, scale)
    axes[2].scatter(qe[:, 0], qe[:, 1], s=1.4, c="#dc2626", alpha=0.55, linewidths=0)
    axes[2].set_title(f"③ SES n={len(xyz0)}  edge_pts n={len(edge_pts)}", fontsize=9)

    draw_mesh(axes[3], verts, faces, center, scale, alpha=0.14)
    for ch in chains:
        p = project_pts(ch["points"], center, scale)
        if len(p) >= 2:
            axes[3].plot(p[:, 0], p[:, 1], color=COL_CHAIN, lw=1.15, alpha=0.9, solid_capstyle="round")
    for xyz in fits:
        p = project_pts(np.asarray(xyz, float), center, scale)
        if len(p) >= 2:
            axes[3].plot(p[:, 0], p[:, 1], color=COL_FIT, lw=1.55, alpha=0.92, solid_capstyle="round")
    axes[3].set_title(f"④ → curve  chains={len(chains)}  fitted={len(fits)}", fontsize=9)
    fig.suptitle(
        f"{sid}   Dora sample → curve input   (red=chain, blue=fitted)   src={fit_src}",
        fontsize=11,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(board, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(fig)
    stats = {
        "sample_id": sid,
        "n_verts": int(len(verts)),
        "n_faces": int(len(faces)),
        "n_points": int(len(feat)),
        "n_salient_edges": int(len(xyz0)),
        "n_edge_points": int(len(edge_pts)),
        "n_chains": int(len(chains)),
        "n_fitted": int(len(fits)),
        "fitted_types": {k: int(sum(t == k for t in ftypes)) for k in sorted(set(ftypes))},
        "fit_source": fit_src,
        "frac_edge_score_gt_0_5": frac,
        "board": str(board),
    }
    (dest / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    return {"sample_id": sid, "status": "ok", **{k: stats[k] for k in ("n_chains", "n_fitted", "fit_source", "board")}}


def _worker(sid: str) -> dict:
    os.environ.setdefault("MPLCONFIGDIR", f"/tmp/mplconfig_viz_dora_curve_{os.getpid()}")
    try:
        return render_one(sid, overwrite=os.environ.get("VIZ_OVERWRITE") == "1")
    except Exception as e:  # noqa: BLE001
        return {"sample_id": sid, "status": "error", "error": f"{type(e).__name__}: {e}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()
    ids = args.ids or list_ids()
    if args.limit:
        ids = ids[: args.limit]
    print(f"parts={len(ids)} workers={args.workers}", flush=True)
    if args.overwrite:
        os.environ["VIZ_OVERWRITE"] = "1"
    rows = []
    if args.workers <= 1 or len(ids) == 1:
        for i, sid in enumerate(ids, 1):
            r = render_one(sid, overwrite=args.overwrite)
            rows.append(r)
            print(f"{i}/{len(ids)} {sid} {r['status']}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_worker, sid): sid for sid in ids}
            n = 0
            for fut in as_completed(futs):
                n += 1
                r = fut.result()
                rows.append(r)
                if n % 50 == 0 or r["status"] == "error":
                    print(f"{n}/{len(ids)} {r['sample_id']} {r['status']}", flush=True)
    summary = {
        "n": len(rows),
        "ok": sum(x["status"] == "ok" for x in rows),
        "skip": sum(x["status"] == "skip_exists" for x in rows),
        "error": sum(x["status"] == "error" for x in rows),
        "errors": [x for x in rows if x["status"] == "error"],
        "viz_subdir": VIZ_NAME,
        "layout": "mesh | 8192 edge_score | SES+edge_points | chains(red)+fitted(blue) → C2",
    }
    (TRAIN / "_viz_dora_curve_v1_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("n", "ok", "skip", "error")}, indent=2))


if __name__ == "__main__":
    main()
