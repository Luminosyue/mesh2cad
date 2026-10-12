#!/usr/bin/env python3
"""3D overlay + funnel + type table for DORA_FITTED_CURVE_DATASET_V1.

Read-only on train800_build_v1. Writes an isolated report under
ours3/dora_fitted_curve_overlay_report_v1.

Layers (one highlighted curve / one GT edge):
  gray  Mesh
  red   Dora ordered chain
  blue  Fitted continuous curve
  green GT B-Rep curve
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig_dora_overlay_v1")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyBboxPatch
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts")]
from curve_token_v1.curve_eval import UnsupportedCurve, evaluate  # noqa: E402
from dora_fitted_curve_dataset_v1 import (  # noqa: E402
    extract_chains,
    graph_from_dora,
    sample_fit,
)

BASE = ROOT / "ours3/dora_fitted_curve_dataset_v1/train800_build_v1"
COHORT = ROOT / "ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl"
OUT = ROOT / "ours3/dora_fitted_curve_overlay_report_v1"

FIT_TYPES = ("LINE", "CIRCLE", "ARC", "ELLIPSE", "BSPLINE")
CLS = ("MATCHED_1_TO_1", "FRAGMENTED", "PARTIAL", "MERGED", "UNMATCHED")
N_GT = 64
MAX_FACES = 14000
FRAME = 0.86
MESH_COLOR = np.array([0.62, 0.66, 0.70])
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))
COL_MESH = (0.55, 0.58, 0.62)
COL_DORA = "#dc2626"
COL_FIT = "#2563eb"
COL_GT = "#16a34a"
NEAR_DIST = 0.02  # relative to bbox diag; looser than match threshold, for GT-side mining
NEAR_COV = 0.35


def dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def farr(f: dict) -> dict:
    q = dict(f)
    for k in ("origin", "direction", "center", "normal", "x_axis", "y_axis", "major_axis", "minor_axis"):
        if k in q:
            q[k] = np.asarray(q[k], float)
    if q.get("type") == "BSPLINE":
        q["tck"] = [np.asarray(q["tck"][0]), np.asarray(q["tck"][1]), int(q["tck"][2])]
    return q


def gt_family(typ: str) -> str:
    return "BSPLINE" if typ == "BEZIER" else typ


def sample_gt(rec: dict) -> np.ndarray | None:
    typ = gt_family(rec["curve_type"])
    params = rec.get("world_parameters") or {}
    u0, u1 = float(rec["u_start"]), float(rec["u_end"])
    us = np.linspace(u0, u1, N_GT)
    try:
        return np.asarray(evaluate(typ, params, us), float)
    except (UnsupportedCurve, Exception):
        sp = np.asarray(rec.get("start_point", []), float)
        ep = np.asarray(rec.get("end_point", []), float)
        if sp.size == 3 and ep.size == 3:
            t = np.linspace(0, 1, N_GT)[:, None]
            return (1.0 - t) * sp + t * ep
        return None


def pair_pts(a: np.ndarray, b: np.ndarray, diag: float) -> dict:
    if len(a) == 0 or len(b) == 0:
        return {
            "d2g_mean_rel": 1.0,
            "g2d_mean_rel": 1.0,
            "coverage_d2g": 0.0,
            "coverage_g2d": 0.0,
        }
    ia = cKDTree(b).query(a)[1]
    ib = cKDTree(a).query(b)[1]
    da = np.linalg.norm(a - b[ia], axis=1)
    db = np.linalg.norm(b - a[ib], axis=1)
    tol = 0.008 * diag
    return {
        "d2g_mean_rel": float(da.mean() / max(diag, 1e-12)),
        "g2d_mean_rel": float(db.mean() / max(diag, 1e-12)),
        "coverage_d2g": float((da <= tol).mean()),
        "coverage_g2d": float((db <= tol).mean()),
    }


def near(m: dict) -> bool:
    return (m["d2g_mean_rel"] <= NEAR_DIST and m["coverage_d2g"] >= NEAR_COV) or (
        m["g2d_mean_rel"] <= NEAR_DIST and m["coverage_g2d"] >= 0.20
    )


def load_mesh(path: Path):
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    verts = np.asarray(mesh.vertices, float)
    faces = np.asarray(mesh.faces, np.int64)
    return verts, faces


def pca_eye(pts: np.ndarray) -> np.ndarray:
    x = pts - pts.mean(0)
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    longest, mid, shortest = vt[0], vt[1], vt[2]
    if shortest[2] < 0:
        shortest = -shortest
    eye = 0.45 * longest + 0.70 * mid + 1.05 * shortest
    n = float(np.linalg.norm(eye)) or 1.0
    return eye / n


def orbit_eye(azim_deg: float, elev_deg: float = 28.0) -> np.ndarray:
    az, el = np.deg2rad(azim_deg), np.deg2rad(elev_deg)
    return np.array([np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), np.sin(el)], float)


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right = right / float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def blank_ax(ax):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)


def project(pts, center, scale, eye):
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.18):
    blank_ax(ax)
    if len(faces) == 0:
        q = project(verts[:: max(1, len(verts) // 4000)], center, scale, eye)
        ax.scatter(q[:, 0], q[:, 1], s=1.2, c=[COL_MESH], linewidths=0, alpha=0.35)
        return
    idx = np.arange(len(faces))
    if len(idx) > MAX_FACES:
        idx = np.random.default_rng(7).choice(idx, MAX_FACES, replace=False)
    tris = verts[faces[idx]]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    n = n / nn
    shade = 0.30 + 0.70 * np.clip(n @ WORLD_LIGHT, 0.0, 1.0)
    fc = np.clip(MESH_COLOR.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(eye)
    x = (tris - center) / scale
    order = np.argsort(x.mean(1) @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.22, 0.24, 0.26, 0.10),
            linewidths=0.04,
        )
    )


def draw_poly(ax, pts, center, scale, eye, color, lw, ls="-", alpha=0.95, zorder=5):
    if pts is None or len(pts) < 2:
        return
    q = project(np.asarray(pts, float), center, scale, eye)
    ax.plot(q[:, 0], q[:, 1], color=color, lw=lw, ls=ls, alpha=alpha, zorder=zorder, solid_capstyle="round")


def load_cad_geom(cad: str, assets: dict):
    cdir = BASE / "cad" / cad
    verts, faces = load_mesh(Path(assets["model_obj"]["path"]))
    diag = float(np.linalg.norm(verts.max(0) - verts.min(0)))
    z = np.load(Path(assets["dora_salient_edges"]["path"]))
    xyz, adj, edges = graph_from_dora(z)
    chains = extract_chains(xyz, adj, edges)
    fits = json.loads((cdir / "dora/fitted_curves.json").read_text())["curves"]
    gts = json.loads((cdir / "gt_brep_curves.json").read_text())["curves"]
    corr = json.loads((cdir / "correspondence.json").read_text())["records"]
    chain_pts = {ch["chain_id"]: ch["points"] for ch in chains}
    fit_xyz = []
    for f in fits:
        p, _, _, _ = sample_fit(farr(f))
        fit_xyz.append(np.asarray(p, float))
    gt_xyz = []
    for g in gts:
        gt_xyz.append(sample_gt(g))
    return {
        "verts": verts,
        "faces": faces,
        "diag": max(diag, 1e-12),
        "chain_pts": chain_pts,
        "fits": fits,
        "fit_xyz": fit_xyz,
        "gts": gts,
        "gt_xyz": gt_xyz,
        "corr": corr,
    }


def frames_aligned(verts: np.ndarray, pts: np.ndarray, diag: float) -> bool:
    if pts is None or len(pts) == 0:
        return False
    lo, hi = verts.min(0), verts.max(0)
    pad = 0.25 * diag
    return bool(np.all(pts.min(0) >= lo - pad) and np.all(pts.max(0) <= hi + pad))


def overlay_panel(ax, geom, eye, focus_pts, dora_list, fit_list, gt_pts, title: str):
    verts = geom["verts"]
    used = []
    for p in dora_list + fit_list + ([gt_pts] if gt_pts is not None else []):
        if p is not None and len(p):
            used.append(np.asarray(p, float))
    if focus_pts is not None and len(focus_pts):
        used.append(np.asarray(focus_pts, float))
    cloud = np.concatenate(used, 0) if used else verts
    center = cloud.mean(0)
    scale = float(np.abs(cloud - center).max()) * 1.65 or 1.0
    draw_mesh(ax, verts, geom["faces"], center, scale, eye, alpha=0.16)
    draw_poly(ax, gt_pts, center, scale, eye, COL_GT, 3.6, "-", 0.90, 6)
    for p in fit_list:
        draw_poly(ax, p, center, scale, eye, COL_FIT, 2.3, "-", 0.95, 7)
    for p in dora_list:
        draw_poly(ax, p, center, scale, eye, COL_DORA, 1.55, "-", 0.95, 8)
    ax.set_title(title, fontsize=10, pad=6)


def render_case(path: Path, geom, title: str, subtitle: str, metrics_lines: list[str],
                dora_list, fit_list, gt_pts):
    focus = []
    for p in dora_list + fit_list + ([gt_pts] if gt_pts is not None else []):
        if p is not None and len(p):
            focus.append(np.asarray(p, float))
    focus_pts = np.concatenate(focus, 0) if focus else geom["verts"]
    fig = plt.figure(figsize=(13.6, 6.4), dpi=140)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.12, 1.12, 0.86], wspace=0.08)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[0, 2])
    overlay_panel(ax0, geom, pca_eye(focus_pts), focus_pts, dora_list, fit_list, gt_pts, "PCA 3D overlay")
    overlay_panel(ax1, geom, orbit_eye(48), focus_pts, dora_list, fit_list, gt_pts, "orbit 48°")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis("off")
    ax2.add_patch(FancyBboxPatch((0.04, 0.04), 0.92, 0.92, boxstyle="round,pad=0.02",
                                 facecolor="#f8fafc", edgecolor="#cbd5e1", lw=0.8))
    legend = [
        ("Mesh", COL_MESH),
        ("Dora chain", COL_DORA),
        ("Fitted curve", COL_FIT),
        ("GT B-Rep curve", COL_GT),
    ]
    y = 0.90
    ax2.text(0.08, y, title, fontsize=11, fontweight="bold", va="top", wrap=True)
    y -= 0.10
    ax2.text(0.08, y, subtitle, fontsize=8.5, color="#334155", va="top")
    y -= 0.10
    for name, col in legend:
        ax2.plot([0.10, 0.22], [y, y], color=col, lw=3.2)
        ax2.text(0.25, y, name, fontsize=9, va="center", color="#0f172a")
        y -= 0.055
    y -= 0.02
    for line in metrics_lines:
        ax2.text(0.08, y, line, fontsize=8.2, family="monospace", va="top", color="#0f172a")
        y -= 0.048
        if y < 0.08:
            break
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.12)
    plt.close(fig)


def pick(rows, n, keyfn):
    rows = sorted(rows, key=lambda r: hashlib.sha256(keyfn(r).encode()).hexdigest())
    return rows[:n]


def gt_attach(geom, gid: int) -> list[int]:
    gp = geom["gt_xyz"][gid]
    if gp is None:
        return []
    out = []
    for i, fp in enumerate(geom["fit_xyz"]):
        if not frames_aligned(geom["verts"], gp, geom["diag"]):
            return []
        if not frames_aligned(geom["verts"], fp, geom["diag"]):
            continue
        m = pair_pts(fp, gp, geom["diag"])
        if near(m):
            out.append(i)
    return out


def scan_index(cohort: dict):
    table = {t: {c: 0 for c in CLS} for t in FIT_TYPES}
    table = {t: {**table[t], "TOTAL_FITTED": 0} for t in FIT_TYPES}
    funnel = Counter()
    matched_line, matched_circle = [], []
    fitted_ell_unmatched, fitted_bs_unmatched, fitted_bs_partial = [], [], []
    gt_ell_frag, gt_bs_frag, gt_bs_partial = [], [], []
    bs_close_unmatched = []
    gt_ell_n = gt_bs_n = 0

    cad_dirs = sorted((BASE / "cad").iterdir())
    for k, cdir in enumerate(cad_dirs, 1):
        cad = cdir.name
        fits = json.loads((cdir / "dora/fitted_curves.json").read_text())["curves"]
        corr = json.loads((cdir / "correspondence.json").read_text())["records"]
        gts = json.loads((cdir / "gt_brep_curves.json").read_text())["curves"]
        gtby = {int(g["edge_id"]): g for g in gts}
        funnel["TOTAL_DORA_CURVES"] += len(fits)
        for rec, f in zip(corr, fits):
            typ = f["type"]
            cls = rec["classification"]
            table[typ]["TOTAL_FITTED"] += 1
            table[typ][cls] += 1
            funnel[cls] += 1
            m = rec.get("metrics") or {}
            gt = gtby.get(rec.get("gt_curve_id"))
            gt_type = None if gt is None else gt_family(gt["curve_type"])
            row = {
                "cad_id": cad,
                "dora_curve_index": int(rec["dora_curve_index"]),
                "chain_id": int(f["chain_id"]),
                "fitted_type": typ,
                "gt_curve_id": rec.get("gt_curve_id"),
                "gt_type": gt_type,
                "classification": cls,
                "metrics": m,
                "curve_length": f.get("curve_length"),
            }
            if cls == "MATCHED_1_TO_1" and typ == "LINE" and gt_type == "LINE":
                matched_line.append(row)
            if cls == "MATCHED_1_TO_1" and typ in ("CIRCLE", "ARC") and gt_type == "CIRCLE":
                matched_circle.append(row)
            if typ == "ELLIPSE" and cls != "MATCHED_1_TO_1":
                fitted_ell_unmatched.append(row)
            if typ == "BSPLINE" and cls == "UNMATCHED":
                fitted_bs_unmatched.append(row)
            if typ == "BSPLINE" and cls == "PARTIAL":
                fitted_bs_partial.append(row)
        if k % 100 == 0:
            print(f"index {k}/{len(cad_dirs)}", flush=True)

    # GT-side fragmentation: load geometry only for CADs that have rare GT types.
    rare_cads = []
    for cdir in cad_dirs:
        gts = json.loads((cdir / "gt_brep_curves.json").read_text())["curves"]
        fam = [gt_family(g["curve_type"]) for g in gts]
        if "ELLIPSE" in fam or "BSPLINE" in fam:
            rare_cads.append(cdir.name)
    print(f"GT-side scan on {len(rare_cads)} CADs with ELLIPSE/BSPLINE", flush=True)
    for n, cad in enumerate(rare_cads, 1):
        geom = load_cad_geom(cad, cohort[cad]["assets"])
        for gi, g in enumerate(geom["gts"]):
            fam = gt_family(g["curve_type"])
            if fam not in ("ELLIPSE", "BSPLINE"):
                continue
            if fam == "ELLIPSE":
                gt_ell_n += 1
            else:
                gt_bs_n += 1
            gp = geom["gt_xyz"][gi]
            if gp is None or not frames_aligned(geom["verts"], gp, geom["diag"]):
                continue
            attached = []
            mets = []
            for i, fp in enumerate(geom["fit_xyz"]):
                m = pair_pts(fp, gp, geom["diag"])
                if near(m):
                    attached.append(i)
                    mets.append(m)
            if not attached:
                continue
            union = None
            for i in attached:
                union = geom["fit_xyz"][i] if union is None else np.vstack([union, geom["fit_xyz"][i]])
            cov = pair_pts(union, gp, geom["diag"])
            rec = {
                "cad_id": cad,
                "gt_curve_id": int(g["edge_id"]),
                "gt_index": gi,
                "gt_type": fam,
                "n_dora": len(attached),
                "dora_indices": attached,
                "fitted_types": [geom["fits"][i]["type"] for i in attached],
                "coverage_d2g": cov["coverage_d2g"],
                "coverage_g2d": cov["coverage_g2d"],
                "d2g_mean_rel": cov["d2g_mean_rel"],
                "g2d_mean_rel": cov["g2d_mean_rel"],
                "rel_extent": float(np.ptp(gp, axis=0).max() / geom["diag"]),
            }
            if fam == "ELLIPSE" and len(attached) >= 2:
                gt_ell_frag.append(rec)
            if fam == "BSPLINE" and len(attached) >= 2:
                gt_bs_frag.append(rec)
            if fam == "BSPLINE" and len(attached) == 1 and cov["coverage_g2d"] < 0.85:
                rec["dora_curve_index"] = attached[0]
                rec["fitted_type"] = geom["fits"][attached[0]]["type"]
                gt_bs_partial.append(rec)
        corr_by_i = {int(c["dora_curve_index"]): c for c in geom["corr"]}
        gt_bs_idx = [gi for gi, g in enumerate(geom["gts"]) if gt_family(g["curve_type"]) == "BSPLINE"]
        for i, f in enumerate(geom["fits"]):
            if f["type"] != "BSPLINE":
                continue
            rec = corr_by_i.get(i, {})
            if rec.get("classification") == "MATCHED_1_TO_1":
                continue
            best = None
            for gi in gt_bs_idx:
                gp = geom["gt_xyz"][gi]
                if gp is None or not frames_aligned(geom["verts"], gp, geom["diag"]):
                    continue
                m = pair_pts(geom["fit_xyz"][i], gp, geom["diag"])
                if best is None or m["d2g_mean_rel"] < best[0]["d2g_mean_rel"]:
                    best = (m, gi, geom["gts"][gi])
            if best is None:
                continue
            m, gi, g = best
            bs_close_unmatched.append({
                "cad_id": cad,
                "dora_curve_index": i,
                "chain_id": int(f["chain_id"]),
                "fitted_type": "BSPLINE",
                "gt_curve_id": int(g["edge_id"]),
                "gt_type": "BSPLINE",
                "classification": rec.get("classification", "UNMATCHED"),
                "metrics": m,
                "curve_length": f.get("curve_length"),
                "score": -(min(m["coverage_d2g"], m["coverage_g2d"]) - max(m["d2g_mean_rel"], m["g2d_mean_rel"])),
            })
        if n % 20 == 0:
            print(f"  rare {n}/{len(rare_cads)}", flush=True)

    return {
        "table": table,
        "funnel": dict(funnel),
        "matched_line": matched_line,
        "matched_circle": matched_circle,
        "fitted_ell_unmatched": fitted_ell_unmatched,
        "fitted_bs_unmatched": fitted_bs_unmatched,
        "fitted_bs_partial": fitted_bs_partial,
        "gt_ell_frag": gt_ell_frag,
        "gt_bs_frag": gt_bs_frag,
        "gt_bs_partial": gt_bs_partial,
        "bs_close_unmatched": bs_close_unmatched,
        "gt_ellipse_count": gt_ell_n,
        "gt_bspline_count": gt_bs_n,
    }


def unique_cads(rows, n):
    seen = set()
    out = []
    for r in rows:
        if r["cad_id"] in seen:
            continue
        out.append(r)
        seen.add(r["cad_id"])
        if len(out) >= n:
            break
    return out


def choose_success(rows):
    ranked = []
    for r in rows:
        m = r["metrics"]
        if not m:
            continue
        if min(m.get("coverage_d2g", 0), m.get("coverage_g2d", 0)) < 0.99:
            continue
        if max(m.get("d2g_mean_rel", 1), m.get("g2d_mean_rel", 1)) > 0.003:
            continue
        ranked.append(r)
    ranked = sorted(
        ranked,
        key=lambda r: (
            0 if r["cad_id"].startswith("deepcad") else 1,
            -float(r.get("curve_length") or 0),
            hashlib.sha256(f"{r['cad_id']}:{r['dora_curve_index']}".encode()).hexdigest(),
        ),
    )
    return unique_cads(ranked, 4)


def choose_frag(rows, n=3):
    rows = [r for r in rows if 2 <= r["n_dora"] <= 8]
    rows = sorted(
        rows,
        key=lambda r: (-float(r.get("rel_extent") or 0), -r["n_dora"], -r["coverage_g2d"], r["cad_id"]),
    )
    return unique_cads(rows, n)


def render_success(cohort, row, outp, kind: str):
    geom = load_cad_geom(row["cad_id"], cohort[row["cad_id"]]["assets"])
    i = row["dora_curve_index"]
    f = geom["fits"][i]
    gid = row["gt_curve_id"]
    gidx = next(j for j, g in enumerate(geom["gts"]) if int(g["edge_id"]) == int(gid))
    dora = [geom["chain_pts"][int(f["chain_id"])]]
    fit = [geom["fit_xyz"][i]]
    gt = geom["gt_xyz"][gidx]
    m = row["metrics"]
    title = f"MATCHED_1_TO_1\nDora → {f['type']} fitting → GT {row['gt_type']}"
    sub = f"{row['cad_id']}   dora[{i}] chain {f['chain_id']}   GT edge {gid}"
    lines = [
        f"classification: MATCHED_1_TO_1",
        f"GT type:        {row['gt_type']}",
        f"Fitted type:    {f['type']}",
        f"Dora → GT cov:  {m.get('coverage_d2g', 0):.1%}",
        f"GT → Dora cov:  {m.get('coverage_g2d', 0):.1%}",
        f"distance d2g:   {m.get('d2g_mean_rel', 0):.4f}",
        f"distance g2d:   {m.get('g2d_mean_rel', 0):.4f}",
        f"tangent sim:    {m.get('tangent_compatibility', 0):.3f}",
        "three polylines almost coincide",
        "Mesh → Dora → fit → GT works",
    ]
    render_case(outp, geom, title.replace("\n", "  "), sub, lines, dora, fit, gt)
    return {"kind": kind, "file": outp.name, **row}


def render_gt_side(cohort, rec, outp, kind: str, headline: str):
    geom = load_cad_geom(rec["cad_id"], cohort[rec["cad_id"]]["assets"])
    dora, fit = [], []
    types = []
    for i in rec["dora_indices"]:
        f = geom["fits"][i]
        dora.append(geom["chain_pts"][int(f["chain_id"])])
        fit.append(geom["fit_xyz"][i])
        types.append(f["type"])
    gt = geom["gt_xyz"][rec["gt_index"]]
    cls = "FRAGMENTED" if rec["n_dora"] >= 2 else "PARTIAL"
    title = f"{headline}\n{cls}   GT {rec['gt_type']} ← {rec['n_dora']} Dora pieces"
    sub = f"{rec['cad_id']}   GT edge {rec['gt_curve_id']}"
    lines = [
        f"GT type:        {rec['gt_type']}",
        f"Fitted types:   {', '.join(types)}",
        f"classification: {cls}",
        f"Dora fragments: {rec['n_dora']}",
        f"Dora → GT cov:  {rec['coverage_d2g']:.1%}",
        f"GT → Dora cov:  {rec['coverage_g2d']:.1%}",
        f"distance d2g:   {rec['d2g_mean_rel']:.4f}",
        f"distance g2d:   {rec['g2d_mean_rel']:.4f}",
        "C2 never saw a complete curve" if cls == "FRAGMENTED" else "Dora only covers part of GT",
        "root: Dora / chaining, not C2",
    ]
    render_case(outp, geom, title.replace("\n", "  "), sub, lines, dora, fit, gt)
    return {"kind": kind, "file": outp.name, **rec}


def render_fitted_bs(cohort, row, outp, kind: str, headline: str):
    geom = load_cad_geom(row["cad_id"], cohort[row["cad_id"]]["assets"])
    i = row["dora_curve_index"]
    f = geom["fits"][i]
    dora = [geom["chain_pts"][int(f["chain_id"])]]
    fit = [geom["fit_xyz"][i]]
    gt, gtyp, m_use = None, row.get("gt_type"), row.get("metrics") or {}
    # search nearest GT BSPLINE in-frame (correspondence nearest may be a LINE)
    best = None
    for gi, g in enumerate(geom["gts"]):
        if gt_family(g["curve_type"]) != "BSPLINE":
            continue
        gp = geom["gt_xyz"][gi]
        if gp is None or not frames_aligned(geom["verts"], gp, geom["diag"]):
            continue
        m = pair_pts(geom["fit_xyz"][i], gp, geom["diag"])
        if best is None or m["d2g_mean_rel"] < best[0]["d2g_mean_rel"]:
            best = (m, gi, g)
    if best is not None:
        m_use, gi, g = best
        gt = geom["gt_xyz"][gi]
        gtyp = "BSPLINE"
        row = {**row, "gt_curve_id": int(g["edge_id"]), "gt_type": "BSPLINE", "metrics": m_use}
    elif row.get("gt_curve_id") is not None:
        gidx = next((j for j, g in enumerate(geom["gts"]) if int(g["edge_id"]) == int(row["gt_curve_id"])), None)
        if gidx is not None:
            gt = geom["gt_xyz"][gidx]
    title = f"{headline}\n{row['classification']}   fitted {f['type']} vs GT {gtyp}"
    sub = f"{row['cad_id']}   dora[{i}]   GT edge {row.get('gt_curve_id')}"
    visually_close = (
        m_use
        and max(m_use.get("d2g_mean_rel", 1), m_use.get("g2d_mean_rel", 1)) <= 0.012
        and min(m_use.get("coverage_d2g", 0), m_use.get("coverage_g2d", 0)) >= 0.70
    )
    note = (
        "fit ≈ GT but program says UNMATCHED → metric / threshold"
        if visually_close and row["classification"] == "UNMATCHED"
        else "Dora observable coverage is incomplete"
        if row["classification"] == "PARTIAL"
        else "fitted BSpline did not pass 1-to-1 match"
    )
    lines = [
        f"GT type:        {gtyp}",
        f"Fitted type:    {f['type']}",
        f"classification: {row['classification']}",
        f"Dora → GT cov:  {m_use.get('coverage_d2g', 0):.1%}",
        f"GT → Dora cov:  {m_use.get('coverage_g2d', 0):.1%}",
        f"distance d2g:   {m_use.get('d2g_mean_rel', 0):.4f}",
        f"distance g2d:   {m_use.get('g2d_mean_rel', 0):.4f}",
        f"visually close: {visually_close}",
        note,
    ]
    render_case(outp, geom, title.replace("\n", "  "), sub, lines, dora, fit, gt)
    return {"kind": kind, "file": outp.name, "visually_close": visually_close, **row}


def draw_funnel(counts: dict, path: Path):
    total = counts["TOTAL_DORA_CURVES"]
    parts = [
        ("MATCHED_1_TO_1", counts.get("MATCHED_1_TO_1", 0), "#16a34a"),
        ("FRAGMENTED", counts.get("FRAGMENTED", 0), "#f59e0b"),
        ("PARTIAL", counts.get("PARTIAL", 0), "#38bdf8"),
        ("MERGED", counts.get("MERGED", 0), "#a78bfa"),
        ("UNMATCHED", counts.get("UNMATCHED", 0), "#ef4444"),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 7.2), dpi=140)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.28, 0.86), 0.44, 0.10, boxstyle="round,pad=0.01",
                                facecolor="#e2e8f0", edgecolor="#64748b"))
    ax.text(0.50, 0.91, f"Dora fitted curves\n{total:,}", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.annotate("", xy=(0.50, 0.78), xytext=(0.50, 0.86),
                arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.4))
    y = 0.68
    for name, n, col in parts:
        w = 0.22 + 0.42 * (n / max(total, 1))
        ax.add_patch(FancyBboxPatch((0.38, y), w, 0.09, boxstyle="round,pad=0.01",
                                    facecolor=col, edgecolor="white", alpha=0.90))
        ax.text(0.36, y + 0.045, name, ha="right", va="center", fontsize=11, color="#0f172a", fontweight="bold")
        ax.text(0.38 + w / 2, y + 0.045, f"{n:,}   ({n / total:.1%})",
                ha="center", va="center", fontsize=11, color="white", fontweight="bold")
        y -= 0.125
    ax.set_title("Where fitted curves are lost  (strict 1-to-1 funnel)", fontsize=14, pad=8)
    ax.text(
        0.50,
        0.04,
        "Mass loss is unmatched + partial + merged.\nNext step: split this funnel by curve type, not more training data.",
        ha="center",
        va="center",
        fontsize=9,
        color="#334155",
    )
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)


def draw_type_table(table: dict, path: Path):
    cols = ["Type", "Fitted", "Matched", "Fragmented", "Partial", "Merged", "Unmatched"]
    keys = ["TOTAL_FITTED", "MATCHED_1_TO_1", "FRAGMENTED", "PARTIAL", "MERGED", "UNMATCHED"]
    cell = [cols]
    totals = Counter()
    for t in FIT_TYPES:
        row = [t] + [str(int(table[t][k])) for k in keys]
        cell.append(row)
        for k in keys:
            totals[k] += table[t][k]
    cell.append(["ALL"] + [str(int(totals[k])) for k in keys])
    fig, ax = plt.subplots(figsize=(11.2, 3.8), dpi=140)
    ax.axis("off")
    ax.set_title("Type-conditioned correspondence  (Dora fitted → GT B-Rep)", fontsize=13, pad=8)
    tbl = ax.table(cellText=cell[1:], colLabels=cell[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.15, 1.55)
    for (r, c), cell_obj in tbl.get_celld().items():
        cell_obj.set_edgecolor("#cbd5e1")
        if r == 0:
            cell_obj.set_facecolor("#0f172a")
            cell_obj.set_text_props(color="white", fontweight="bold")
        elif r == len(cell) - 1:
            cell_obj.set_facecolor("#e2e8f0")
            cell_obj.set_text_props(fontweight="bold")
        elif cell[r][0] in ("ELLIPSE", "BSPLINE"):
            cell_obj.set_facecolor("#fef3c7")
        else:
            cell_obj.set_facecolor("white")
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.15)
    plt.close(fig)


def stitch_gallery(figdir: Path, selected: list, path: Path):
    from PIL import Image, ImageDraw, ImageFont

    order = [
        "success_LINE",
        "success_CIRCLE",
        "ellipse_FRAGMENTED",
        "bspline_UNMATCHED",
        "bspline_PARTIAL",
        "bspline_FRAGMENTED",
    ]
    by = defaultdict(list)
    for rec in selected:
        by[rec["kind"]].append(rec)
    cells = []
    for kind in order:
        if by[kind]:
            cells.append(figdir / by[kind][0]["file"])
    extra = [figdir / "funnel.png", figdir / "type_table.png"]
    cells = [p for p in cells if p.exists()] + extra
    if not cells:
        return
    imgs = [Image.open(p).convert("RGB") for p in cells]
    w = 720
    scaled = []
    for im in imgs:
        h = int(im.height * w / im.width)
        scaled.append(im.resize((w, h), Image.Resampling.LANCZOS))
    cols = 2
    rows = int(np.ceil(len(scaled) / cols))
    row_h = [0] * rows
    for i, im in enumerate(scaled):
        row_h[i // cols] = max(row_h[i // cols], im.height)
    canvas = Image.new("RGB", (cols * w + 24, sum(row_h) + 18 * (rows + 1) + 48), "white")
    draw = ImageDraw.Draw(canvas)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 22) if Path(font_path).is_file() else ImageFont.load_default()
    draw.text((16, 12), "Dora fitted curve overlay  —  success / ellipse / BSpline / funnel", fill=(15, 23, 42), font=font)
    y = 52
    i = 0
    for r in range(rows):
        x = 12
        h = row_h[r]
        for _ in range(cols):
            if i >= len(scaled):
                break
            canvas.paste(scaled[i], (x, y))
            x += w
            i += 1
        y += h + 12
    canvas.save(path)


def json_safe(x):
    if isinstance(x, dict):
        return {k: json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_safe(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x


def main():
    if (OUT / "REPORT_FREEZE.json").exists():
        (OUT / "REPORT_FREEZE.json").unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    for old in (OUT / "figures").glob("*.png"):
        old.unlink()
    cohort = {}
    for line in COHORT.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            cohort[row["cad_id"]] = row
    print("scanning correspondence index", flush=True)
    idx = scan_index(cohort)
    dump(OUT / "TYPE_CONDITIONED_TABLE.json", {"columns": ["TOTAL_FITTED", *CLS], "table": idx["table"]})
    dump(OUT / "FUNNEL.json", idx["funnel"])
    dump(
        OUT / "GT_SIDE_MINING.json",
        {
            "gt_ellipse_count": idx["gt_ellipse_count"],
            "gt_bspline_count": idx["gt_bspline_count"],
            "gt_ellipse_fragmented_cases": len(idx["gt_ell_frag"]),
            "gt_bspline_fragmented_cases": len(idx["gt_bs_frag"]),
            "gt_bspline_partial_cases": len(idx["gt_bs_partial"]),
            "bspline_close_unmatched_vs_gt_bspline": len(idx["bs_close_unmatched"]),
            "note": "GT-side attach uses looser near-threshold; classification FRAGMENTED here means >=2 Dora pieces cover one GT edge.",
        },
    )
    draw_funnel(idx["funnel"], OUT / "figures" / "funnel.png")
    draw_type_table(idx["table"], OUT / "figures" / "type_table.png")

    selected = []
    figdir = OUT / "figures"

    lines = choose_success(idx["matched_line"])
    for n, r in enumerate(lines[:2]):
        selected.append(render_success(cohort, r, figdir / f"success_LINE_{n}_{r['cad_id']}.png", "success_LINE"))
    circ = choose_success(idx["matched_circle"])
    for n, r in enumerate(circ[:2]):
        selected.append(render_success(cohort, r, figdir / f"success_CIRCLE_{n}_{r['cad_id']}.png", "success_CIRCLE"))

    for n, r in enumerate(choose_frag(idx["gt_ell_frag"], 3)):
        selected.append(
            render_gt_side(cohort, r, figdir / f"ellipse_FRAGMENTED_{n}_{r['cad_id']}.png", "ellipse_FRAGMENTED",
                           "GT Ellipse  vs  Dora fragmentation")
        )
    # fitted ellipse that never 1-to-1 matched, if any remaining visual
    ell_fit = pick(idx["fitted_ell_unmatched"], 1, lambda r: f"{r['cad_id']}:{r['dora_curve_index']}")
    if ell_fit:
        # reuse success renderer path via fitted-bs style
        row = ell_fit[0]
        geom = load_cad_geom(row["cad_id"], cohort[row["cad_id"]]["assets"])
        i = row["dora_curve_index"]
        f = geom["fits"][i]
        best = None
        for gi, g in enumerate(geom["gts"]):
            if gt_family(g["curve_type"]) != "ELLIPSE":
                continue
            gp = geom["gt_xyz"][gi]
            if gp is None or not frames_aligned(geom["verts"], gp, geom["diag"]):
                continue
            m = pair_pts(geom["fit_xyz"][i], gp, geom["diag"])
            if best is None or m["d2g_mean_rel"] < best[0]["d2g_mean_rel"]:
                best = (m, gi, g)
        dora = [geom["chain_pts"][int(f["chain_id"])]]
        fit = [geom["fit_xyz"][i]]
        gt = None
        m_use = row.get("metrics") or {}
        gtyp = row.get("gt_type")
        if best is not None:
            m_use, gi, g = best
            gt = geom["gt_xyz"][gi]
            gtyp = "ELLIPSE"
        lines_m = [
            f"GT type:        {gtyp}",
            f"Fitted type:    {f['type']}",
            f"classification: {row['classification']}",
            f"Dora → GT cov:  {m_use.get('coverage_d2g', 0):.1%}",
            f"GT → Dora cov:  {m_use.get('coverage_g2d', 0):.1%}",
            f"distance d2g:   {m_use.get('d2g_mean_rel', 0):.4f}",
            f"distance g2d:   {m_use.get('g2d_mean_rel', 0):.4f}",
            "fitted ELLIPSE never entered MATCHED_1_TO_1",
        ]
        render_case(
            figdir / f"ellipse_fitted_UNMATCHED_{row['cad_id']}.png",
            geom,
            f"Fitted ELLIPSE  {row['classification']}",
            f"{row['cad_id']}   dora[{i}]",
            lines_m,
            dora,
            fit,
            gt,
        )
        selected.append({"kind": "ellipse_fitted_UNMATCHED", "file": f"ellipse_fitted_UNMATCHED_{row['cad_id']}.png", **row})

    close_bs = sorted(idx["bs_close_unmatched"], key=lambda r: r["score"])
    a_rows = unique_cads(close_bs, 2) or unique_cads(idx["fitted_bs_unmatched"], 2)
    for n, r in enumerate(a_rows):
        selected.append(
            render_fitted_bs(
                cohort, r, figdir / f"bspline_UNMATCHED_{n}_{r['cad_id']}.png",
                "bspline_UNMATCHED", "BSpline case A  fit vs match",
            )
        )

    for n, r in enumerate(idx["fitted_bs_partial"][:2]):
        selected.append(
            render_fitted_bs(
                cohort, r, figdir / f"bspline_PARTIAL_fitted_{n}_{r['cad_id']}.png",
                "bspline_PARTIAL", "BSpline case B  Dora only part of GT",
            )
        )
    bs_part = unique_cads(sorted(idx["gt_bs_partial"], key=lambda r: r["coverage_g2d"]), 2)
    for n, r in enumerate(bs_part):
        selected.append(
            render_gt_side(
                cohort, r, figdir / f"bspline_PARTIAL_gt_{n}_{r['cad_id']}.png",
                "bspline_PARTIAL_gt", "BSpline case B  GT-side partial",
            )
        )
    for n, r in enumerate(choose_frag(idx["gt_bs_frag"], 3)):
        selected.append(
            render_gt_side(
                cohort, r, figdir / f"bspline_FRAGMENTED_{n}_{r['cad_id']}.png",
                "bspline_FRAGMENTED", "BSpline case C  Dora chopped GT",
            )
        )

    dump(OUT / "SELECTED_CASES.json", json_safe(selected))
    stitch_gallery(figdir, selected, figdir / "gallery_board.png")
    dump(
        OUT / "REPORT_FREEZE.json",
        {
            "CURRENT_GATE": "DORA_FITTED_CURVE_OVERLAY_REPORT_V1",
            "SOURCE": str(BASE),
            "V1_MODIFIED": False,
            "TRAINING_STARTED": False,
            "n_figures": len(list(figdir.glob("*.png"))),
            "n_selected": len(selected),
        },
    )
    print(json.dumps({"out": str(OUT), "figures": sorted(p.name for p in figdir.glob('*.png'))}, indent=2))


if __name__ == "__main__":
    main()
