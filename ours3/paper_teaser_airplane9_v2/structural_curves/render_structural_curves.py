#!/usr/bin/env python3
"""Mesh-derived structural curves figure: extract -> chain -> fit -> filter on a real wing mesh."""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from scipy.interpolate import splev, splprep

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
RENDERER = ROOT / "paper_teaser_demo_v2/scripts/render_smooth_brep.py"
ROUTEB = ROOT / "airplane_routeb_geometry_v2"
OUT = Path(__file__).resolve().parent

PART = sys.argv[1] if len(sys.argv) > 1 else "PART_004"
FEATURE_DEG = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
MIN_LEN_FRAC = 0.04
ORANGE = "#f06a1d"

spec = importlib.util.spec_from_file_location("render_smooth_brep", RENDERER)
R = importlib.util.module_from_spec(spec)
sys.modules["render_smooth_brep"] = R
spec.loader.exec_module(R)
R.W = R.H = 1400


def feature_edges(mesh: trimesh.Trimesh):
    sharp = mesh.face_adjacency_edges[np.degrees(mesh.face_adjacency_angles) > FEATURE_DEG]
    edges_sorted = np.sort(mesh.edges, axis=1)
    uniq, counts = np.unique(edges_sorted, axis=0, return_counts=True)
    boundary = uniq[counts == 1]
    return np.unique(np.sort(np.vstack([sharp, boundary]), axis=1), axis=0), len(sharp), len(boundary)


def chain_edges(edges):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    used, chains = set(), []
    starts = [v for v in adj if len(adj[v]) != 2] + list(adj)
    for s in starts:
        for n in adj[s]:
            if (min(s, n), max(s, n)) in used:
                continue
            path, prev, cur = [s], s, n
            used.add((min(s, n), max(s, n)))
            while True:
                path.append(cur)
                if len(adj[cur]) != 2 or cur == s:
                    break
                nxt = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
                key = (min(cur, nxt), max(cur, nxt))
                if key in used:
                    break
                used.add(key)
                prev, cur = cur, nxt
            chains.append(path)
    return chains


def fit_curve(pts, diag):
    if len(pts) < 4:
        return pts
    _, keep = np.unique(np.round(pts / (diag * 1e-5)), axis=0, return_index=True)
    pts = pts[np.sort(keep)]
    if len(pts) < 4:
        return pts
    try:
        tck, _ = splprep(pts.T, s=len(pts) * (diag * 0.003) ** 2, k=3)
    except Exception:
        return pts
    return np.stack(splev(np.linspace(0, 1, 200), tck), axis=1)


def polyline_len(p):
    return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


def visible_runs(sx, sy, z, zbuf, eps):
    xi = np.clip(np.round(sx).astype(int), 0, R.W - 1)
    yi = np.clip(np.round(sy).astype(int), 0, R.H - 1)
    return z >= zbuf[yi, xi] - eps


def main():
    src = ROUTEB / f"{PART}/source/complete_{PART.lower()}.obj"
    mesh = trimesh.load(src, force="mesh", process=True)
    mesh.merge_vertices()
    v, f = np.asarray(mesh.vertices, float), np.asarray(mesh.faces, np.int64)
    diag = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))

    edges, n_sharp, n_boundary = feature_edges(mesh)
    raw_chains = [v[c] for c in chain_edges(edges)]
    kept = [c for c in raw_chains if polyline_len(c) >= MIN_LEN_FRAC * diag]
    fitted = [fit_curve(c, diag) for c in kept]

    center, span = R.frame_of(v)
    half = R.projected_half(v, center, span)
    img, zbuf = R.blank()
    corners = R.smooth_corner_normals(v, f, feature_deg=FEATURE_DEG)
    R.paint_surface(img, zbuf, v, f, corners, R.MESH_COLOR, center, span, half)

    wire_edges = mesh.edges_unique
    ws = R.project(v, center, span, half)
    pad = 0.06 * max(np.ptp(ws[0]), np.ptp(ws[1]))
    xlim = (ws[0].min() - pad, ws[0].max() + pad)
    ylim = (ws[1].max() + pad, ws[1].min() - pad)
    aspect = (xlim[1] - xlim[0]) / (ylim[0] - ylim[1])
    fig, axes = plt.subplots(1, 2, figsize=(2 * 6 * aspect, 6.8), facecolor="white")
    ax = axes[0]
    ax.imshow(img)
    for a, b in wire_edges[:: max(len(wire_edges) // 6000, 1)]:
        ax.plot([ws[0][a], ws[0][b]], [ws[1][a], ws[1][b]], color="#8d99a3", lw=0.25, alpha=0.5)
    eps = 0.01
    for c in kept:
        sx, sy, z = R.project(c, center, span, half)
        vis = visible_runs(sx, sy, z, zbuf, eps)
        xs = np.where(vis, sx, np.nan)
        ys = np.where(vis, sy, np.nan)
        ax.plot(xs, ys, color=ORANGE, lw=2.6, ls=(0, (4, 2.5)), solid_capstyle="round")
    ax.set_title("Observed mesh with structural edge chains", fontsize=14, color="#14222b")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")

    ax = axes[1]
    ax.set_facecolor("white")
    for c in fitted:
        sx, sy, _ = R.project(c, center, span, half)
        ax.plot(sx, sy, color=ORANGE, lw=2.2)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Retained curves (fitted)", fontsize=14, color="#14222b")
    fig.suptitle(f"Mesh-derived structural curves | {PART} (wing)  extract - chain - fit - filter", fontsize=13, color="#14222b")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.02, wspace=0.02)
    stem = OUT / f"{PART}_structural_curves"
    fig.savefig(f"{stem}.png", dpi=180, facecolor="white")
    fig.savefig(f"{stem}.pdf", facecolor="white")
    plt.close(fig)

    for name, draw_mesh in (("mesh_with_chains", True), ("retained_curves", False)):
        fig, ax = plt.subplots(figsize=(7 * aspect, 7), facecolor="white")
        if draw_mesh:
            ax.imshow(img)
            for a, b in wire_edges[:: max(len(wire_edges) // 6000, 1)]:
                ax.plot([ws[0][a], ws[0][b]], [ws[1][a], ws[1][b]], color="#8d99a3", lw=0.25, alpha=0.5)
            for c in kept:
                sx, sy, z = R.project(c, center, span, half)
                vis = visible_runs(sx, sy, z, zbuf, eps)
                ax.plot(np.where(vis, sx, np.nan), np.where(vis, sy, np.nan), color=ORANGE, lw=2.6, ls=(0, (4, 2.5)))
        else:
            for c in fitted:
                sx, sy, _ = R.project(c, center, span, half)
                ax.plot(sx, sy, color=ORANGE, lw=2.2)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")
        ax.axis("off")
        fig.subplots_adjust(0, 0, 1, 1)
        fig.savefig(OUT / f"{PART}_{name}.png", dpi=200, facecolor="white", transparent=not draw_mesh)
        plt.close(fig)

    stats = {
        "part": PART, "source_mesh": str(src), "feature_deg": FEATURE_DEG, "min_len_frac": MIN_LEN_FRAC,
        "sharp_edges": int(n_sharp), "boundary_edges": int(n_boundary), "raw_chains": len(raw_chains),
        "retained_chains": len(kept), "routeb_cached_chains": len(json.load(open(ROUTEB / f"{PART}/curves/merged_chains.json"))),
    }
    (OUT / f"{PART}_structural_curves.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
