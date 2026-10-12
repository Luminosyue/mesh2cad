#!/usr/bin/env python3
"""Stage one P3 part, run Dora SES, map sharp edges to edge_score, visualize.

SpatialLM originally consumes xyzrgb. This pipeline replaces color with
(normal, edge_score) so each sampled point is:

    [x, y, z, nx, ny, nz, edge_score]

edge_score = exp(-d_i / sigma), d_i = distance to the nearest Dora sharp edge.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cad-spatial")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_STL = ROOT / "ours3/cadfit_xpart45_routea_v1/input_stl/PART_005.stl"
DEFAULT_OUT = ROOT / "cad_spatial_dataset"
EXISTING_DORA = ROOT / "ours3/dora_ses_xpart45_v1"
VIEW = np.array([[0.82, -0.38, 0.0], [0.22, 0.30, 0.86]], dtype=float)
EDGE_CMAP = LinearSegmentedColormap.from_list(
    "edge_score",
    ["#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"],
)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_json_default) + "\n", encoding="utf-8")


def _json_default(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return str(obj)


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    mesh = trimesh.Trimesh(vertices=np.asarray(mesh.vertices), faces=np.asarray(mesh.faces), process=False)
    if len(mesh.face_adjacency) == 0:
        mesh.merge_vertices()
        mesh.update_faces(mesh.unique_faces())
        mesh.remove_unreferenced_vertices()
    return mesh


def stage_part(stl_path: Path, out_root: Path, part_id: str, source: str) -> tuple[trimesh.Trimesh, Path]:
    mesh = load_mesh(stl_path)
    staged = out_root / source / "P3" / f"{part_id}.obj"
    staged.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(staged)
    part_dir = out_root / part_id
    part_dir.mkdir(parents=True, exist_ok=True)
    mesh_path = part_dir / "mesh.obj"
    shutil.copy2(staged, mesh_path)
    return mesh, mesh_path


def dora_ses_edges(mesh: trimesh.Trimesh, threshold_deg: float) -> tuple[np.ndarray, np.ndarray]:
    """Dora SES criterion: select mesh edges whose face-normal angle exceeds threshold."""
    if len(mesh.face_adjacency) == 0:
        raise RuntimeError("mesh has no face adjacency; cannot run Dora SES")
    angles_deg = np.degrees(np.asarray(mesh.face_adjacency_angles, dtype=np.float64))
    keep = angles_deg > float(threshold_deg)
    pairs = np.asarray(mesh.face_adjacency_edges, dtype=np.int64)[keep]
    dihedral = angles_deg[keep].astype(np.float32)
    if len(pairs) == 0:
        return np.zeros((0, 2), dtype=np.int64), np.zeros((0,), dtype=np.float32)
    ordered = np.sort(pairs, axis=1)
    _, uniq_idx = np.unique(ordered, axis=0, return_index=True)
    uniq_idx = np.sort(uniq_idx)
    return ordered[uniq_idx], dihedral[uniq_idx]


def chain_sharp_edges(edge_idx: np.ndarray, vertices: np.ndarray) -> list[dict]:
    """Walk Dora mesh edges into polylines: edge_001, edge_002, ..."""
    adj: dict[int, list[int]] = defaultdict(list)
    undirected = set()
    for a, b in edge_idx.tolist():
        a, b = int(a), int(b)
        key = (a, b) if a < b else (b, a)
        if key in undirected:
            continue
        undirected.add(key)
        adj[a].append(b)
        adj[b].append(a)

    visited_e: set[tuple[int, int]] = set()
    chains: list[list[int]] = []

    def walk(start: int, nxt: int) -> list[int]:
        path = [start, nxt]
        visited_e.add((min(start, nxt), max(start, nxt)))
        prev, cur = start, nxt
        while True:
            cands = [n for n in adj[cur] if (min(cur, n), max(cur, n)) not in visited_e]
            if not cands:
                break
            # prefer continuation away from prev
            nxt = cands[0]
            visited_e.add((min(cur, nxt), max(cur, nxt)))
            path.append(nxt)
            prev, cur = cur, nxt
            if cur == path[0]:
                break
        return path

    endpoints = [v for v, nbrs in adj.items() if len(nbrs) == 1]
    for v in sorted(endpoints):
        for n in adj[v]:
            key = (min(v, n), max(v, n))
            if key not in visited_e:
                chains.append(walk(v, n))

    for v, nbrs in adj.items():
        for n in nbrs:
            key = (min(v, n), max(v, n))
            if key not in visited_e:
                chains.append(walk(v, n))

    records = []
    for i, vids in enumerate(chains, start=1):
        pts = vertices[np.asarray(vids, dtype=np.int64)]
        segs = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
        records.append(
            {
                "edge_id": f"edge_{i:03d}",
                "vertex_indices": [int(v) for v in vids],
                "points": pts.astype(np.float32),
                "length": float(segs.sum()) if len(segs) else 0.0,
                "closed": bool(len(vids) > 2 and vids[0] == vids[-1]),
            }
        )
    return records


def densify_polylines(chains: list[dict], spacing: float) -> np.ndarray:
    pts = []
    for ch in chains:
        poly = np.asarray(ch["points"], dtype=np.float64)
        if len(poly) == 0:
            continue
        pts.append(poly[0])
        for a, b in zip(poly[:-1], poly[1:]):
            seg = b - a
            length = float(np.linalg.norm(seg))
            if length < 1e-12:
                continue
            n = max(int(np.floor(length / max(spacing, 1e-8))), 1)
            for k in range(1, n + 1):
                t = k / n
                pts.append(a + t * seg)
    if not pts:
        return np.zeros((0, 3), dtype=np.float32)
    arr = np.asarray(pts, dtype=np.float32)
    # unique at a small grid to drop exact duplicates
    key = np.round(arr / max(spacing * 0.25, 1e-8), 0)
    _, idx = np.unique(key, axis=0, return_index=True)
    return arr[np.sort(idx)]


def point_to_segment_distance(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """d_i = min distance from each point to any sharp-edge segment."""
    if len(a) == 0:
        return np.full(len(points), np.inf, dtype=np.float64)
    p = np.asarray(points, dtype=np.float64)
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ab = b - a
    ab_len2 = np.sum(ab * ab, axis=1)
    ab_len2 = np.maximum(ab_len2, 1e-18)
    dmin = np.full(len(p), np.inf, dtype=np.float64)
    chunk = 512
    for i0 in range(0, len(a), chunk):
        i1 = min(i0 + chunk, len(a))
        ab_c = ab[i0:i1]
        a_c = a[i0:i1]
        ap = p[:, None, :] - a_c[None, :, :]
        t = np.sum(ap * ab_c[None, :, :], axis=2) / ab_len2[None, i0:i1]
        t = np.clip(t, 0.0, 1.0)
        closest = a_c[None, :, :] + t[:, :, None] * ab_c[None, :, :]
        dist = np.linalg.norm(p[:, None, :] - closest, axis=2)
        dmin = np.minimum(dmin, dist.min(axis=1))
    return dmin


def sample_surface(mesh: trimesh.Trimesh, n_points: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    points, face_idx = mesh.sample(n_points, return_index=True)
    rng = np.random.default_rng(seed)
    # trimesh.sample is not seeded; resample faces area-weighted with a seed
    areas = mesh.area_faces
    probs = areas / (areas.sum() + 1e-18)
    face_idx = rng.choice(len(mesh.faces), size=n_points, replace=True, p=probs)
    faces = mesh.faces[face_idx]
    tri = mesh.vertices[faces]
    u = rng.random(n_points)
    v = rng.random(n_points)
    mask = u + v > 1.0
    u[mask] = 1.0 - u[mask]
    v[mask] = 1.0 - v[mask]
    w = 1.0 - u - v
    points = (w[:, None] * tri[:, 0] + u[:, None] * tri[:, 1] + v[:, None] * tri[:, 2]).astype(np.float32)
    normals = mesh.face_normals[face_idx].astype(np.float32)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, np.maximum(norms, 1e-8))
    return points, normals


def project(pts: np.ndarray) -> np.ndarray:
    return np.asarray(pts, dtype=float) @ VIEW.T


def frame_limits(p2: np.ndarray, pad: float = 0.58) -> tuple[tuple[float, float], tuple[float, float]]:
    c = p2.mean(axis=0)
    r = max(float(np.ptp(p2, axis=0).max()) * pad, 1e-8)
    return (c[0] - r, c[0] + r), (c[1] - r, c[1] + r)


def subsample_faces(faces: np.ndarray, n: int = 7000) -> np.ndarray:
    if len(faces) <= n:
        return faces
    rng = np.random.default_rng(7)
    return faces[rng.choice(len(faces), n, replace=False)]


def draw_mesh(ax, verts, faces, color, alpha, xlim, ylim):
    p2 = project(verts)
    polys = [p2[f] for f in subsample_faces(faces)]
    ax.add_collection(
        PolyCollection(
            polys,
            facecolors=(*color, alpha),
            edgecolors=(0.30, 0.32, 0.36, 0.10),
            linewidths=0.04,
        )
    )
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


def save_fig(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def visualize(
    part_dir: Path,
    part_id: str,
    mesh: trimesh.Trimesh,
    chains: list[dict],
    points: np.ndarray,
    scores: np.ndarray,
    threshold_deg: float | None = None,
) -> dict[str, str]:
    vis = part_dir / "vis"
    vis.mkdir(parents=True, exist_ok=True)
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    p2 = project(verts)
    xlim, ylim = frame_limits(p2)
    th_tag = f"  th={threshold_deg:g}°" if threshold_deg is not None else ""

    fig, ax = plt.subplots(figsize=(6.4, 5.4), dpi=160)
    draw_mesh(ax, verts, faces, (0.55, 0.60, 0.66), 0.92, xlim, ylim)
    ax.set_title(f"{part_id}  source mesh", fontsize=11)
    save_fig(fig, vis / "01_mesh.png")

    fig, ax = plt.subplots(figsize=(6.4, 5.4), dpi=160)
    draw_mesh(ax, verts, faces, (0.82, 0.84, 0.86), 0.22, xlim, ylim)
    n_edges = 0
    for ch in chains:
        pts = np.asarray(ch["points"], dtype=float)
        if len(pts) < 2:
            continue
        q = project(pts)
        ax.plot(q[:, 0], q[:, 1], color="#c0392b", lw=0.95, alpha=0.88, solid_capstyle="round")
        n_edges += 1
    ax.set_title(f"{part_id}  Dora SES sharp edges  n={n_edges}{th_tag}", fontsize=11)
    save_fig(fig, vis / "02_dora_edges.png")

    q = project(points)
    fig, ax = plt.subplots(figsize=(6.8, 5.4), dpi=160)
    draw_mesh(ax, verts, faces, (0.88, 0.89, 0.91), 0.12, xlim, ylim)
    sc = ax.scatter(
        q[:, 0],
        q[:, 1],
        c=scores,
        cmap=EDGE_CMAP,
        vmin=0.0,
        vmax=1.0,
        s=7.5,
        linewidths=0,
        zorder=3,
    )
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("edge_score", fontsize=9)
    ax.set_title(f"{part_id}  edge_score  red=sharp  blue=surface{th_tag}", fontsize=11)
    save_fig(fig, vis / "03_edge_score.png")

    fig, axes = plt.subplots(1, 3, figsize=(15.6, 5.0), dpi=150)
    draw_mesh(axes[0], verts, faces, (0.55, 0.60, 0.66), 0.92, xlim, ylim)
    axes[0].set_title("1. mesh")
    draw_mesh(axes[1], verts, faces, (0.82, 0.84, 0.86), 0.22, xlim, ylim)
    for ch in chains:
        pts = np.asarray(ch["points"], dtype=float)
        if len(pts) < 2:
            continue
        qe = project(pts)
        axes[1].plot(qe[:, 0], qe[:, 1], color="#c0392b", lw=0.9, alpha=0.88)
    axes[1].set_title(f"2. Dora sharp edges{th_tag}")
    draw_mesh(axes[2], verts, faces, (0.88, 0.89, 0.91), 0.12, xlim, ylim)
    sc = axes[2].scatter(q[:, 0], q[:, 1], c=scores, cmap=EDGE_CMAP, vmin=0, vmax=1, s=5.5, linewidths=0, zorder=3)
    fig.colorbar(sc, ax=axes[2], fraction=0.046, pad=0.02)
    axes[2].set_title("3. edge_score")
    fig.suptitle(f"{part_id}  SpatialLM CAD front-end  (no LLM)", fontsize=12, y=1.02)
    save_fig(fig, vis / "panel.png")

    colors = EDGE_CMAP(np.clip(scores, 0, 1))[:, :3]
    cloud = trimesh.points.PointCloud(points, colors=(colors * 255).astype(np.uint8))
    cloud.export(vis / "edge_score.ply")

    return {
        "mesh": str(vis / "01_mesh.png"),
        "dora_edges": str(vis / "02_dora_edges.png"),
        "edge_score": str(vis / "03_edge_score.png"),
        "panel": str(vis / "panel.png"),
        "edge_score_ply": str(vis / "edge_score.ply"),
    }


def visualize_rings(
    part_dir: Path,
    part_id: str,
    mesh: trimesh.Trimesh,
    chains: list[dict],
    edge_stats: dict,
    surface: dict,
) -> dict[str, str]:
    """Highlight closed / circular CAD rings (outer rim / inner hole / shaft)."""
    vis = part_dir / "vis"
    vis.mkdir(parents=True, exist_ok=True)
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    p2 = project(verts)
    xlim, ylim = frame_limits(p2)

    ring_ids = {r["edge_id"] for r in edge_stats.get("rings", [])}
    closed_ids = {ch["edge_id"] for ch in chains if ch.get("closed")}
    clusters = edge_stats.get("radius_clusters", []) or []
    peaks = edge_stats.get("radius_peaks_from_edges", []) or []
    cmap = plt.cm.tab10

    # assign each chain to nearest radius cluster/peak by mean radial distance
    axis = np.asarray(surface.get("pca_axis", [0, 0, 1]), dtype=np.float64)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    center = verts.mean(axis=0)
    ref_radii = [c["radius_mean"] for c in clusters] or [p["radius_mean"] for p in peaks]

    def chain_radius(ch: dict) -> float | None:
        pts = np.asarray(ch["points"], dtype=np.float64)
        if len(pts) == 0:
            return None
        rel = pts - center
        radial = rel - (rel @ axis)[:, None] * axis[None, :]
        return float(np.linalg.norm(radial, axis=1).mean())

    id_to_cluster: dict[str, int] = {}
    for ch in chains:
        if ch["edge_id"] in ring_ids:
            for i, cl in enumerate(clusters):
                if ch["edge_id"] in cl.get("members", []):
                    id_to_cluster[ch["edge_id"]] = i
                    break
            continue
        if not ref_radii:
            continue
        r = chain_radius(ch)
        if r is None:
            continue
        # match to a radius group within 8%
        best_i, best_d = None, 1e9
        for i, rr in enumerate(ref_radii):
            d = abs(r - rr) / max(rr, 1e-8)
            if d < best_d:
                best_d, best_i = d, i
        if best_i is not None and best_d < 0.08:
            id_to_cluster[ch["edge_id"]] = best_i

    fig, ax = plt.subplots(figsize=(6.8, 5.6), dpi=160)
    draw_mesh(ax, verts, faces, (0.84, 0.86, 0.88), 0.18, xlim, ylim)
    for ch in chains:
        pts = np.asarray(ch["points"], dtype=float)
        if len(pts) < 2:
            continue
        q = project(pts)
        if ch["edge_id"] in id_to_cluster:
            ci = id_to_cluster[ch["edge_id"]]
            ax.plot(q[:, 0], q[:, 1], color=cmap(ci % 10), lw=1.55, alpha=0.95, solid_capstyle="round")
        else:
            ax.plot(q[:, 0], q[:, 1], color="#bbbbbb", lw=0.55, alpha=0.4)

    n_rings = len(ring_ids)
    n_groups = len(clusters) if clusters else len(peaks)
    ax.set_title(
        f"{part_id}  CAD rings  closed={len(closed_ids)}  circular={n_rings}  radius_groups={n_groups}",
        fontsize=10,
    )
    legend_src = clusters if clusters else peaks
    if legend_src:
        labels = [f"r≈{cl['radius_mean']:.3f} (n={cl.get('count', 0)})" for cl in legend_src[:5]]
        ax.text(
            0.02,
            0.02,
            "\n".join(labels),
            transform=ax.transAxes,
            fontsize=8,
            va="bottom",
            ha="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.75, edgecolor="#ddd"),
        )
    save_fig(fig, vis / "04_cad_rings.png")
    return {"cad_rings": str(vis / "04_cad_rings.png")}


def score_distribution(scores: np.ndarray) -> dict:
    s = np.asarray(scores, dtype=np.float64)
    return {
        "n": int(len(s)),
        "min": float(s.min()) if len(s) else 0.0,
        "max": float(s.max()) if len(s) else 0.0,
        "mean": float(s.mean()) if len(s) else 0.0,
        "median": float(np.median(s)) if len(s) else 0.0,
        "frac_lt_0_1": float(np.mean(s < 0.1)) if len(s) else 0.0,
        "frac_lt_0_2": float(np.mean(s < 0.2)) if len(s) else 0.0,
        "frac_ge_0_5": float(np.mean(s >= 0.5)) if len(s) else 0.0,
        "frac_ge_0_8": float(np.mean(s >= 0.8)) if len(s) else 0.0,
        "frac_ge_0_9": float(np.mean(s >= 0.9)) if len(s) else 0.0,
        "ideal_check": {
            "want_frac_lt_0_1_near_0_9": True,
            "want_frac_ge_0_8_in_0_05_0_10": True,
            "pass_lt_0_1": bool(len(s) and np.mean(s < 0.1) >= 0.80),
            "pass_ge_0_8": bool(len(s) and 0.03 <= np.mean(s >= 0.8) <= 0.10),
        },
    }


THRESHOLD_CANDIDATES = (15, 25, 35, 45)
EDGE_FRAC_TARGET = 0.02
EDGE_FRAC_LO = 0.01
EDGE_FRAC_HI = 0.04


def mesh_dihedral_angles(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray]:
    """All face-adjacency edges and their dihedral angles in degrees."""
    if len(mesh.face_adjacency) == 0:
        raise RuntimeError("mesh has no face adjacency; cannot run Dora SES")
    angles = np.degrees(np.asarray(mesh.face_adjacency_angles, dtype=np.float64))
    pairs = np.asarray(mesh.face_adjacency_edges, dtype=np.int64)
    return pairs, angles


def select_threshold_by_edge_fraction(
    angles_deg: np.ndarray,
    candidates: tuple[int, ...] = THRESHOLD_CANDIDATES,
    target: float = EDGE_FRAC_TARGET,
    lo: float = EDGE_FRAC_LO,
    hi: float = EDGE_FRAC_HI,
) -> tuple[float, list[dict]]:
    """Pick θ in candidates so #{edges>θ}/#{adj} ≈ 2% (prefer band 1%–4%)."""
    n = max(len(angles_deg), 1)
    rows = []
    for th in candidates:
        n_keep = int(np.sum(angles_deg > float(th)))
        frac = n_keep / n
        rows.append(
            {
                "threshold_deg": float(th),
                "n_edges": n_keep,
                "edge_frac": float(frac),
                "in_band": bool(lo <= frac <= hi),
                "abs_err_to_target": float(abs(frac - target)),
            }
        )
    in_band = [r for r in rows if r["in_band"]]
    pool = in_band if in_band else rows
    # tie-break: closer to 2%, then prefer mid candidates (25/35)
    best = min(
        pool,
        key=lambda r: (r["abs_err_to_target"], abs(r["threshold_deg"] - 25.0)),
    )
    return float(best["threshold_deg"]), rows


def filter_edges_by_threshold(
    pairs: np.ndarray, angles_deg: np.ndarray, threshold_deg: float
) -> tuple[np.ndarray, np.ndarray]:
    keep = angles_deg > float(threshold_deg)
    edged = pairs[keep]
    dih = angles_deg[keep].astype(np.float32)
    if len(edged) == 0:
        return np.zeros((0, 2), dtype=np.int64), np.zeros((0,), dtype=np.float32)
    ordered = np.sort(edged, axis=1)
    _, uniq_idx = np.unique(ordered, axis=0, return_index=True)
    uniq_idx = np.sort(uniq_idx)
    return ordered[uniq_idx], dih[uniq_idx]


def adaptive_select_threshold_and_sigma(
    mesh: trimesh.Trimesh,
    points: np.ndarray,
    *,
    pairs: np.ndarray,
    angles_deg: np.ndarray,
    diag: float,
    candidates: tuple[int, ...] = THRESHOLD_CANDIDATES,
    fixed_threshold: float | None = None,
    fixed_sigma: float | None = None,
    max_refine: int = 4,
) -> dict:
    """
    1) choose θ from candidates with edge fraction ≈ 2% (1–4%)
    2) compute edge_score; refine σ first, then θ if needed
    3) return the best (θ, σ) seen, not necessarily the last iterate
    """
    if fixed_threshold is not None:
        threshold = float(fixed_threshold)
        cand_rows = [
            {
                "threshold_deg": float(fixed_threshold),
                "n_edges": int(np.sum(angles_deg > float(fixed_threshold))),
                "edge_frac": float(np.mean(angles_deg > float(fixed_threshold))),
                "in_band": bool(
                    EDGE_FRAC_LO
                    <= float(np.mean(angles_deg > float(fixed_threshold)))
                    <= EDGE_FRAC_HI
                ),
                "abs_err_to_target": float(
                    abs(float(np.mean(angles_deg > float(fixed_threshold))) - EDGE_FRAC_TARGET)
                ),
                "note": "user_fixed",
            }
        ]
        selection_mode = "user_fixed"
    else:
        threshold, cand_rows = select_threshold_by_edge_fraction(angles_deg, candidates)
        selection_mode = "edge_frac_target_2pct"

    sigma = float(fixed_sigma) if fixed_sigma is not None else 0.01 * diag
    sigma = max(sigma, 1e-8)
    sigma_locked = fixed_sigma is not None
    threshold_locked = fixed_threshold is not None

    history: list[dict] = []
    best: dict | None = None
    best_err = float("inf")

    def eval_state(th: float, sig: float, it: int, action: str) -> dict:
        nonlocal best, best_err
        e_idx, dih = filter_edges_by_threshold(pairs, angles_deg, th)
        if len(e_idx):
            a = np.asarray(mesh.vertices[e_idx[:, 0]], dtype=np.float64)
            b = np.asarray(mesh.vertices[e_idx[:, 1]], dtype=np.float64)
        else:
            a = np.zeros((0, 3), dtype=np.float64)
            b = np.zeros((0, 3), dtype=np.float64)
        d = point_to_segment_distance(points, a, b)
        scores = np.clip(np.exp(-d / max(sig, 1e-8)), 0.0, 1.0).astype(np.float32)
        stats = score_distribution(scores)
        edge_frac = float(len(e_idx) / max(len(angles_deg), 1))
        cold_ok = stats["frac_lt_0_1"] >= 0.80
        sharp_ok = 0.03 <= stats["frac_ge_0_8"] <= 0.10
        # soft objective around ideal surface field
        err = abs(stats["frac_lt_0_1"] - 0.85) + 2.0 * abs(stats["frac_ge_0_8"] - 0.06)
        # prefer staying near 2% edge fraction
        err += 0.5 * abs(edge_frac - EDGE_FRAC_TARGET)
        step = {
            "iter": it,
            "threshold_deg": float(th),
            "sigma": float(sig),
            "n_salient_edges": int(len(e_idx)),
            "edge_frac": edge_frac,
            "frac_lt_0_1": stats["frac_lt_0_1"],
            "frac_ge_0_8": stats["frac_ge_0_8"],
            "cold_ok": cold_ok,
            "sharp_ok": sharp_ok,
            "err": float(err),
            "action": action,
            "edge_idx": e_idx,
            "dihedral": dih,
            "v0": a,
            "v1": b,
            "edge_score": scores,
            "dist_stats": stats,
        }
        if err < best_err:
            best_err = err
            best = step
        return step

    for it in range(max_refine):
        step = eval_state(threshold, sigma, it, "evaluate")
        cold_ok, sharp_ok = step["cold_ok"], step["sharp_ok"]
        too_hot = (step["frac_lt_0_1"] < 0.80) or (step["frac_ge_0_8"] > 0.10)
        too_cold = step["frac_ge_0_8"] < 0.03

        if cold_ok and sharp_ok:
            step["action"] = "accept"
            history.append({k: v for k, v in step.items() if k not in ("edge_idx", "dihedral", "v0", "v1", "edge_score", "dist_stats")})
            break

        action = "stop_no_move"
        if too_hot:
            # shrink σ first; if still hot / σ floored → raise θ
            if (not sigma_locked) and step["frac_lt_0_1"] < 0.80 and sigma > 0.004 * diag:
                sigma = max(sigma * 0.7, 0.004 * diag)
                action = "shrink_sigma_too_hot"
            elif not threshold_locked:
                higher = [c for c in candidates if c > threshold]
                if higher:
                    threshold = float(min(higher))
                    action = "raise_theta_too_hot"
                elif not sigma_locked:
                    sigma = max(sigma * 0.7, 0.003 * diag)
                    action = "shrink_sigma_floor"
            elif not sigma_locked:
                sigma = max(sigma * 0.7, 0.003 * diag)
                action = "shrink_sigma_floor"
        elif too_cold:
            # grow σ first; if still cold / σ capped → lower θ
            if (not sigma_locked) and sigma < 0.02 * diag:
                sigma = min(sigma * 1.35, 0.02 * diag)
                action = "grow_sigma_too_cold"
            elif not threshold_locked:
                lower = [c for c in candidates if c < threshold]
                if lower:
                    threshold = float(max(lower))
                    action = "lower_theta_too_cold"
                elif not sigma_locked:
                    sigma = min(sigma * 1.2, 0.025 * diag)
                    action = "grow_sigma_ceiling"
            elif not sigma_locked:
                sigma = min(sigma * 1.2, 0.025 * diag)
                action = "grow_sigma_ceiling"

        step["action"] = action
        history.append(
            {k: v for k, v in step.items() if k not in ("edge_idx", "dihedral", "v0", "v1", "edge_score", "dist_stats")}
        )
        if action == "stop_no_move":
            break

    assert best is not None
    # one final eval already stored in best
    angle_summary = {
        "n_adjacency": int(len(angles_deg)),
        "p50": float(np.percentile(angles_deg, 50)) if len(angles_deg) else 0.0,
        "p90": float(np.percentile(angles_deg, 90)) if len(angles_deg) else 0.0,
        "p95": float(np.percentile(angles_deg, 95)) if len(angles_deg) else 0.0,
        "p99": float(np.percentile(angles_deg, 99)) if len(angles_deg) else 0.0,
        "max": float(angles_deg.max()) if len(angles_deg) else 0.0,
    }

    return {
        "threshold_deg": float(best["threshold_deg"]),
        "sigma": float(best["sigma"]),
        "selection_mode": selection_mode,
        "candidates": cand_rows,
        "angle_summary": angle_summary,
        "refine_history": history,
        "edge_idx": best["edge_idx"],
        "dihedral": best["dihedral"],
        "v0": best["v0"],
        "v1": best["v1"],
        "edge_score": best["edge_score"],
        "dist_stats": best["dist_stats"],
        "accepted": bool(
            best["dist_stats"]["ideal_check"]["pass_lt_0_1"]
            and best["dist_stats"]["ideal_check"]["pass_ge_0_8"]
        ),
        "best_err": float(best["err"]),
    }


def compute_surface_stats(mesh: trimesh.Trimesh) -> dict:
    """Lightweight CAD primitive hint from face normals vs PCA axis."""
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    normals = np.asarray(mesh.face_normals, dtype=np.float64)
    areas = np.asarray(mesh.area_faces, dtype=np.float64)
    total = float(areas.sum()) + 1e-18

    centered = verts - verts.mean(axis=0)
    cov = np.cov(centered.T)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)  # ascending
    evals = evals[order]
    evecs = evecs[:, order]
    # for wheel/disk, smallest variance ≈ cylinder axis
    axis = evecs[:, 0]
    axis = axis / (np.linalg.norm(axis) + 1e-12)

    n_dot = np.abs(normals @ axis)
    # planar: normals nearly parallel to axis (top/bottom faces)
    planar_mask = n_dot >= np.cos(np.radians(35.0))
    # cylindrical: normals nearly perpendicular to axis (side wall)
    cyl_mask = n_dot <= np.cos(np.radians(70.0))
    other_mask = ~(planar_mask | cyl_mask)

    planar_ratio = float(areas[planar_mask].sum() / total)
    cylindrical_ratio = float(areas[cyl_mask].sum() / total)
    other_ratio = float(areas[other_mask].sum() / total)
    # renormalize the two main classes for a simple CAD hint
    main = planar_ratio + cylindrical_ratio
    if main > 1e-8:
        planar_n = planar_ratio / main
        cyl_n = cylindrical_ratio / main
    else:
        planar_n, cyl_n = planar_ratio, cylindrical_ratio

    evals_n = evals / (evals.sum() + 1e-18)
    return {
        "planar_ratio": round(planar_n, 4),
        "cylindrical_ratio": round(cyl_n, 4),
        "other_ratio": round(other_ratio, 4),
        "planar_area_frac_raw": round(planar_ratio, 4),
        "cylindrical_area_frac_raw": round(cylindrical_ratio, 4),
        "pca_axis": axis.tolist(),
        "pca_variance_ratios": evals_n.tolist(),
        "likely_class": (
            "cylindrical"
            if cyl_n >= 0.55
            else ("planar" if planar_n >= 0.55 else "mixed")
        ),
    }


def _nearly_closed(pts: np.ndarray, length: float, gap_tol: float) -> bool:
    if len(pts) < 4:
        return False
    gap = float(np.linalg.norm(pts[0] - pts[-1]))
    return gap <= max(gap_tol, 0.05 * max(length, 1e-8))


def _circle_fit_stats(pts: np.ndarray, axis: np.ndarray, max_radius: float | None = None) -> dict | None:
    """Project polyline to plane ⟂ axis; fit circle → radius hint for rings."""
    if len(pts) < 6:
        return None
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    # build plane basis
    tmp = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, tmp)
    u /= np.linalg.norm(u) + 1e-12
    v = np.cross(axis, u)
    c0 = pts.mean(axis=0)
    xy = np.stack([(pts - c0) @ u, (pts - c0) @ v], axis=1)
    # algebraic circle fit
    x, y = xy[:, 0], xy[:, 1]
    A = np.stack([2 * x, 2 * y, np.ones_like(x)], axis=1)
    try:
        sol, *_ = np.linalg.lstsq(A, x * x + y * y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cx, cy, c = sol
    r2 = c + cx * cx + cy * cy
    if r2 <= 0:
        return None
    r = float(np.sqrt(r2))
    if max_radius is not None and (r <= 1e-8 or r > max_radius):
        return None
    resid = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    rmse = float(np.sqrt(np.mean((resid - r) ** 2)))
    if r < 1e-8 or rmse / r > 0.12:
        return None
    center3 = c0 + cx * u + cy * v
    height = float(np.mean((pts - center3) @ axis))
    return {
        "radius": r,
        "rmse": rmse,
        "center": center3.tolist(),
        "axis_height": height,
        "circularity": float(1.0 - min(rmse / r, 1.0)),
    }


def compute_edge_stats(
    chains: list[dict],
    mesh: trimesh.Trimesh,
    surface: dict,
    med_edge_len: float,
    edge_xyz0: np.ndarray | None = None,
    edge_xyz1: np.ndarray | None = None,
) -> dict:
    axis = np.asarray(surface.get("pca_axis", [0, 0, 1]), dtype=np.float64)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    extent = np.asarray(mesh.bounds[1] - mesh.bounds[0], dtype=np.float64)
    max_radius = float(0.75 * np.linalg.norm(extent))
    gap_tol = max(3.5 * med_edge_len, 1e-5)
    closed = 0
    rings = []
    for ch in chains:
        pts = np.asarray(ch["points"], dtype=np.float64)
        length = float(ch["length"])
        is_closed = bool(ch.get("closed")) or _nearly_closed(pts, length, gap_tol)
        if is_closed:
            closed += 1
        # fit circle on closed OR long-enough arcs (fragmented rings still count)
        if len(pts) >= 6 and length >= 8.0 * max(med_edge_len, 1e-6):
            fit = _circle_fit_stats(pts, axis, max_radius=max_radius)
            if fit is not None and fit["circularity"] >= 0.85:
                # require the arc to cover enough angle: chord/length heuristic
                span = float(np.linalg.norm(pts[-1] - pts[0]))
                arc_frac = 1.0 - min(span / max(length, 1e-8), 1.0)
                if is_closed or arc_frac >= 0.35 or fit["circularity"] >= 0.95:
                    rings.append(
                        {
                            "edge_id": ch["edge_id"],
                            "radius": round(fit["radius"], 6),
                            "circularity": round(fit["circularity"], 4),
                            "axis_height": round(fit["axis_height"], 6),
                            "length": round(length, 6),
                            "closed": bool(is_closed),
                        }
                    )

    # backup: cluster mesh-edge midpoints by radius around PCA axis
    radius_peaks = []
    if edge_xyz0 is not None and edge_xyz1 is not None and len(edge_xyz0):
        mids = 0.5 * (np.asarray(edge_xyz0, dtype=np.float64) + np.asarray(edge_xyz1, dtype=np.float64))
        center = np.asarray(mesh.vertices, dtype=np.float64).mean(axis=0)
        rel = mids - center
        # remove axis component → radial distance in plane ⟂ axis
        axial = (rel @ axis)[:, None] * axis[None, :]
        radial_vec = rel - axial
        radii = np.linalg.norm(radial_vec, axis=1)
        heights = rel @ axis
        if len(radii):
            r_max = float(radii.max()) + 1e-8
            n_bins = 24
            hist, edges = np.histogram(radii, bins=n_bins, range=(0.0, r_max))
            # peak bins with enough edges
            thr = max(int(0.04 * len(radii)), 6)
            for i, c in enumerate(hist):
                if c < thr:
                    continue
                # local maximum
                left = hist[i - 1] if i > 0 else -1
                right = hist[i + 1] if i + 1 < len(hist) else -1
                if c >= left and c >= right:
                    lo, hi = edges[i], edges[i + 1]
                    mask = (radii >= lo) & (radii < hi)
                    radius_peaks.append(
                        {
                            "radius_mean": round(float(radii[mask].mean()), 6),
                            "count": int(mask.sum()),
                            "height_mean": round(float(heights[mask].mean()), 6),
                            "source": "edge_midpoint_histogram",
                        }
                    )
            # also split dominant radius band by axial height → top/bottom rims
            if len(radii) >= 12:
                r_med = float(np.median(radii))
                band = np.abs(radii - r_med) / max(r_med, 1e-8) < 0.12
                if band.sum() >= 12:
                    h = heights[band]
                    h_hist, h_edges = np.histogram(h, bins=12)
                    h_thr = max(int(0.08 * band.sum()), 4)
                    for i, c in enumerate(h_hist):
                        if c < h_thr:
                            continue
                        left = h_hist[i - 1] if i > 0 else -1
                        right = h_hist[i + 1] if i + 1 < len(h_hist) else -1
                        if c >= left and c >= right:
                            lo, hi = h_edges[i], h_edges[i + 1]
                            m2 = band & (heights >= lo) & (heights < hi)
                            radius_peaks.append(
                                {
                                    "radius_mean": round(float(radii[m2].mean()), 6),
                                    "count": int(m2.sum()),
                                    "height_mean": round(float(heights[m2].mean()), 6),
                                    "source": "radius_height_peak",
                                }
                            )
            # dedupe nearby peaks
            dedup = []
            for p in sorted(radius_peaks, key=lambda x: -x["count"]):
                if any(
                    abs(p["radius_mean"] - q["radius_mean"]) / max(q["radius_mean"], 1e-8) < 0.05
                    and abs(p["height_mean"] - q.get("height_mean", 0.0)) < 0.02 * max_radius
                    for q in dedup
                ):
                    continue
                dedup.append(p)
            radius_peaks = sorted(dedup, key=lambda x: (-x["radius_mean"], x.get("height_mean", 0.0)))

    rings = sorted(rings, key=lambda r: r["radius"], reverse=True)
    # cluster fitted ring radii
    radius_clusters = []
    for r in rings:
        placed = False
        for cl in radius_clusters:
            if abs(r["radius"] - cl["radius_mean"]) / max(cl["radius_mean"], 1e-8) < 0.08:
                cl["members"].append(r["edge_id"])
                cl["radii"].append(r["radius"])
                cl["radius_mean"] = float(np.mean(cl["radii"]))
                placed = True
                break
        if not placed:
            radius_clusters.append(
                {
                    "radius_mean": r["radius"],
                    "radii": [r["radius"]],
                    "members": [r["edge_id"]],
                }
            )
    for cl in radius_clusters:
        cl["radius_mean"] = round(cl["radius_mean"], 6)
        cl.pop("radii", None)
        cl["count"] = len(cl["members"])
        cl["source"] = "polyline_circle_fit"
    radius_clusters = sorted(radius_clusters, key=lambda c: -c["radius_mean"])

    # prefer midpoint peaks when they give more concentric groups, or merge in
    if radius_peaks:
        if not radius_clusters or len(radius_peaks) >= len(radius_clusters):
            # keep polyline clusters that are scale-valid, then add unmatched peaks
            kept = [cl for cl in radius_clusters if cl["radius_mean"] <= max_radius]
            for p in radius_peaks:
                if any(abs(p["radius_mean"] - cl["radius_mean"]) / max(cl["radius_mean"], 1e-8) < 0.08 for cl in kept):
                    continue
                kept.append(
                    {
                        "radius_mean": p["radius_mean"],
                        "count": p["count"],
                        "members": [],
                        "source": p["source"],
                        "height_mean": p["height_mean"],
                    }
                )
            radius_clusters = sorted(kept, key=lambda c: -c["radius_mean"])

    return {
        "sharp_edge_count": int(len(chains)),
        "closed_curve_count": int(closed),
        "circular_ring_count": int(len(rings)),
        "concentric_radius_groups": int(len(radius_clusters)),
        "rings": rings[:24],
        "radius_clusters": radius_clusters[:12],
        "radius_peaks_from_edges": radius_peaks[:12],
    }


def annotate_closed_chains(chains: list[dict], med_edge_len: float) -> list[dict]:
    gap_tol = max(2.5 * med_edge_len, 1e-5)
    out = []
    for ch in chains:
        pts = np.asarray(ch["points"], dtype=np.float64)
        closed = bool(ch.get("closed")) or _nearly_closed(pts, float(ch["length"]), gap_tol)
        out.append({**ch, "closed": closed})
    return out


def maybe_compare_existing_dora(part_id: str, edge_xyz0: np.ndarray, edge_xyz1: np.ndarray) -> dict:
    npz = EXISTING_DORA / "threshold_45" / part_id / "salient_edges_source_space.npz"
    if not npz.is_file():
        return {"compared": False}
    data = np.load(npz)
    ref0 = np.asarray(data["edge_xyz0"], dtype=np.float64)
    ref1 = np.asarray(data["edge_xyz1"], dtype=np.float64)
    return {
        "compared": True,
        "existing_npz": str(npz),
        "existing_n_edges": int(len(ref0)),
        "ours_n_edges": int(len(edge_xyz0)),
        "count_match": int(len(ref0) == len(edge_xyz0)),
    }


def run(args: argparse.Namespace) -> int:
    stl_path = Path(args.mesh)
    part_id = args.part_id or stl_path.stem.upper()
    if not part_id.startswith("PART_"):
        part_id = stl_path.stem
    out_root = Path(args.output)
    out_root.mkdir(parents=True, exist_ok=True)

    mesh, mesh_path = stage_part(stl_path, out_root, part_id, args.source)
    part_dir = out_root / part_id
    dora_dir = part_dir / "dora"
    dora_dir.mkdir(parents=True, exist_ok=True)

    pairs, angles_deg = mesh_dihedral_angles(mesh)
    bbox = mesh.bounds
    extent = bbox[1] - bbox[0]
    diag = float(np.linalg.norm(extent))

    points, normals = sample_surface(mesh, args.num_points, args.seed)

    # adaptive + no --threshold → auto θ; otherwise lock θ (σ still refinable unless --sigma)
    if args.adaptive and args.threshold is None:
        fixed_th = None
        fixed_sigma = args.sigma
        max_refine = int(args.max_refine)
    elif args.adaptive:
        fixed_th = float(args.threshold)
        fixed_sigma = args.sigma
        max_refine = int(args.max_refine)
    else:
        fixed_th = float(args.threshold) if args.threshold is not None else 25.0
        fixed_sigma = float(args.sigma) if args.sigma is not None else 0.01 * diag
        max_refine = 1

    adapt = adaptive_select_threshold_and_sigma(
        mesh,
        points,
        pairs=pairs,
        angles_deg=angles_deg,
        diag=diag,
        candidates=tuple(int(x) for x in args.threshold_candidates),
        fixed_threshold=fixed_th,
        fixed_sigma=fixed_sigma,
        max_refine=max_refine,
    )

    threshold = adapt["threshold_deg"]
    sigma = adapt["sigma"]
    edge_idx = adapt["edge_idx"]
    dihedral = adapt["dihedral"]
    v0 = adapt["v0"]
    v1 = adapt["v1"]
    edge_score = adapt["edge_score"]
    dist_stats = adapt["dist_stats"]

    edge_len = np.linalg.norm(v1 - v0, axis=1) if len(edge_idx) else np.zeros((0,))
    np.savez(
        dora_dir / "salient_edges.npz",
        edge_vertex_indices=edge_idx.astype(np.int32),
        edge_xyz0=np.asarray(v0, dtype=np.float32),
        edge_xyz1=np.asarray(v1, dtype=np.float32),
        dihedral_deg=dihedral.astype(np.float32),
        edge_length=edge_len.astype(np.float32),
        source=np.array(["DORA_SES"] * len(edge_idx)),
    )

    chains = chain_sharp_edges(edge_idx, np.asarray(mesh.vertices))
    med_len = float(np.median(edge_len)) if len(edge_len) else 1e-3
    spacing = med_len * float(args.edge_spacing_factor)
    chains = annotate_closed_chains(chains, med_len)
    edge_points = densify_polylines(chains, spacing=max(spacing, 1e-6))
    np.save(dora_dir / "edge_points.npy", edge_points)
    write_json(
        dora_dir / "sharp_edges.json",
        [
            {
                "edge_id": ch["edge_id"],
                "vertex_indices": ch["vertex_indices"],
                "points": np.asarray(ch["points"], dtype=float).round(6).tolist(),
                "length": ch["length"],
                "closed": ch["closed"],
            }
            for ch in chains
        ],
    )

    np.save(part_dir / "points.npy", points.astype(np.float32))
    np.save(part_dir / "normals.npy", normals.astype(np.float32))
    np.save(part_dir / "edge_score.npy", edge_score.astype(np.float32))
    features = np.concatenate([points, normals, edge_score[:, None]], axis=1).astype(np.float32)
    np.save(part_dir / "features.npy", features)

    surface = compute_surface_stats(mesh)
    edge_stats = compute_edge_stats(
        chains, mesh, surface, med_len, edge_xyz0=np.asarray(v0), edge_xyz1=np.asarray(v1)
    )
    vis_paths: dict = {}
    if not getattr(args, "no_vis", False):
        vis_paths = visualize(part_dir, part_id, mesh, chains, points, edge_score, threshold_deg=threshold)
        vis_paths.update(visualize_rings(part_dir, part_id, mesh, chains, edge_stats, surface))
    compare = maybe_compare_existing_dora(part_id, np.asarray(v0), np.asarray(v1))

    meta = {
        "part_id": part_id,
        "source": args.source,
        "mesh": str(mesh_path),
        "input_mesh": str(stl_path),
        "bbox": [float(extent[0]), float(extent[1]), float(extent[2])],
        "bbox_min": bbox[0].tolist(),
        "bbox_max": bbox[1].tolist(),
        "bbox_diagonal": diag,
        "sharp_edges": int(len(chains)),
        "sharp_mesh_edges": int(len(edge_idx)),
        "num_edge_points": int(len(edge_points)),
        "edge_spacing": spacing,
        "edge_spacing_factor": float(args.edge_spacing_factor),
        "num_points": int(len(points)),
        "threshold_deg": float(threshold),
        "sigma": sigma,
        "sigma_rule": "adaptive" if args.sigma is None else "user",
        "adaptive": {
            "enabled": bool(args.adaptive),
            "selection_mode": adapt["selection_mode"],
            "edge_frac_target": EDGE_FRAC_TARGET,
            "edge_frac_band": [EDGE_FRAC_LO, EDGE_FRAC_HI],
            "candidates": adapt["candidates"],
            "angle_summary": adapt["angle_summary"],
            "refine_history": adapt["refine_history"],
            "accepted": adapt["accepted"],
        },
        "edge_score_distribution": dist_stats,
        "edge_score_mean": dist_stats["mean"],
        "edge_score_p90": float(np.percentile(edge_score, 90)),
        "frac_score_gt_0_5": dist_stats["frac_ge_0_5"],
        "frac_score_gt_0_8": dist_stats["frac_ge_0_8"],
        "surface_stats": surface,
        "edge_stats": {
            "sharp_edge_count": edge_stats["sharp_edge_count"],
            "closed_curve_count": edge_stats["closed_curve_count"],
            "circular_ring_count": edge_stats["circular_ring_count"],
            "concentric_radius_groups": edge_stats["concentric_radius_groups"],
            "radius_clusters": edge_stats["radius_clusters"],
            "radius_peaks_from_edges": edge_stats.get("radius_peaks_from_edges", []),
            "rings": edge_stats["rings"],
        },
        "feature_layout": ["x", "y", "z", "nx", "ny", "nz", "edge_score"],
        "dora_compare": compare,
        "vis": vis_paths,
    }
    write_json(part_dir / "meta.json", meta)

    print(f"staged: {out_root / args.source / 'P3' / (part_id + '.obj')}")
    print(f"dataset: {part_dir}")
    print(
        f"adaptive: mode={adapt['selection_mode']}  θ={threshold:g}°  "
        f"σ={sigma:.6f}  accepted={adapt['accepted']}"
    )
    for row in adapt["candidates"]:
        mark = " <--" if abs(row["threshold_deg"] - threshold) < 1e-6 else ""
        print(
            f"  cand θ={row['threshold_deg']:g}  "
            f"edge_frac={row['edge_frac']*100:.2f}%  n={row['n_edges']}{mark}"
        )
    for step in adapt["refine_history"]:
        print(
            f"  refine[{step['iter']}]: θ={step['threshold_deg']:g} σ={step['sigma']:.5f} "
            f"<0.1={step['frac_lt_0_1']:.3f} >=0.8={step['frac_ge_0_8']:.3f} "
            f"→ {step['action']}"
        )
    print(f"sharp polylines: {len(chains)}  mesh edges: {len(edge_idx)}  edge points: {len(edge_points)}")
    print(
        f"samples: {len(points)}  "
        f"<0.1={dist_stats['frac_lt_0_1']:.3f}  >=0.8={dist_stats['frac_ge_0_8']:.3f}"
    )
    print(
        f"surface: {surface['likely_class']}  "
        f"planar={surface['planar_ratio']:.2f}  cyl={surface['cylindrical_ratio']:.2f}"
    )
    print(
        f"edges: closed={edge_stats['closed_curve_count']}  "
        f"rings={edge_stats['circular_ring_count']}  "
        f"radius_groups={edge_stats['concentric_radius_groups']}"
    )
    if vis_paths:
        print(f"panel: {vis_paths.get('panel', 'skipped')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SpatialLM CAD part dataset from one P3 mesh.")
    parser.add_argument("--mesh", type=Path, default=DEFAULT_STL, help="Single part mesh (STL/OBJ)")
    parser.add_argument("--part-id", type=str, default=None)
    parser.add_argument("--source", type=str, default="tank")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Lock Dora SES threshold (degrees). Default: adaptive pick from candidates.",
    )
    parser.add_argument(
        "--threshold-candidates",
        type=int,
        nargs="+",
        default=list(THRESHOLD_CANDIDATES),
        help="Candidate thresholds for adaptive selection",
    )
    parser.add_argument(
        "--adaptive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-select θ≈2%% edge fraction, then refine θ/σ by edge_score distribution",
    )
    parser.add_argument("--max-refine", type=int, default=4, help="Max adaptive refine iterations")
    parser.add_argument(
        "--edge-spacing-factor",
        type=float,
        default=0.15,
        help="edge_points spacing = median(mesh_edge_len) * factor (smaller = denser)",
    )
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument(
        "--sigma",
        type=float,
        default=None,
        help="Lock edge_score sigma. Default: start 0.01*bbox_diagonal then adaptive refine",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--no-vis", action="store_true", help="Skip PNG/PLY visualization outputs")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())