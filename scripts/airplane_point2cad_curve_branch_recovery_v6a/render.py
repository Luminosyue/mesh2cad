"""V6A visualization renders."""
from __future__ import annotations

from pathlib import Path

import numpy as np

VIEW = np.array([[0.72, -0.36, 0.59], [0.68, 0.42, -0.60], [-0.15, 0.83, 0.53]])


def _plot_polylines(mesh, polylines, colors, path: Path, title: str, points=None, point_colors=None, point_sizes=None):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection

    v = np.asarray(mesh.vertices, float)
    f = np.asarray(mesh.faces, int)
    if len(f) > 3500:
        f = f[np.linspace(0, len(f) - 1, 3500, dtype=int)]
    p2 = v @ VIEW.T
    p2 = p2[:, :2]
    fig, ax = plt.subplots(figsize=(6.0, 5.0), dpi=120)
    ax.add_collection(
        PolyCollection(
            [p2[tri] for tri in f],
            facecolors=(0.75, 0.76, 0.78, 0.22),
            edgecolors=(0.5, 0.5, 0.52, 0.07),
            linewidths=0.03,
        )
    )
    segs = []
    cols = []
    for i, pl in enumerate(polylines):
        q = np.asarray(pl, float) @ VIEW.T
        q = q[:, :2]
        if len(q) >= 2:
            segs.append(q)
            if isinstance(colors, list):
                cols.append(colors[i % len(colors)])
            else:
                cols.append(colors)
    if segs:
        ax.add_collection(LineCollection(segs, colors=cols, linewidths=1.4, alpha=0.95))
    if points is not None and len(points):
        c = np.asarray(points, float) @ VIEW.T
        c = c[:, :2]
        ax.scatter(c[:, 0], c[:, 1], s=point_sizes or 24, c=point_colors or "#dc2626", zorder=5)
    ctr = p2.mean(0)
    r = max(float(np.ptp(p2, 0).max()) * 0.58, 1e-8)
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_v6a(mesh, out: Path, frags, branch_doc, before_topo, after_topo, occ, title_prefix: str):
    palette = ["#1d4ed8", "#b45309", "#0f766e", "#7c3aed", "#be123c", "#365314", "#0891b2", "#ca8a04"]
    out.mkdir(parents=True, exist_ok=True)
    raw_lines = [f["points"] for f in frags]
    raw_colors = [palette[i % len(palette)] for i in range(len(frags))]
    _plot_polylines(mesh, raw_lines, raw_colors, out / "01_raw_fragments.png", f"{title_prefix} raw fragments n={len(frags)}")

    branch_lines = []
    branch_colors = []
    for i, b in enumerate(branch_doc["branches"]):
        branch_lines.append(b["points"])
        branch_colors.append(palette[i % len(palette)])
    _plot_polylines(
        mesh,
        branch_lines,
        branch_colors,
        out / "02_recovered_branches.png",
        f"{title_prefix} recovered branches n={len(branch_lines)}",
    )

    # endpoint degree on after edges
    graph = after_topo["graph"]
    adj = graph["adj"]
    deg_pts, deg_cols, deg_sizes = [], [], []
    for si in range(len(adj)):
        for vid, nbrs in adj[si].items():
            deg = len({e for _, e in nbrs})
            vrec = next((v for v in after_topo["verts"] if v["vertex_id"] == vid), None)
            if not vrec:
                continue
            deg_pts.append(vrec["xyz"])
            if deg == 1:
                deg_cols.append("#dc2626")
                deg_sizes.append(36)
            elif deg == 2:
                deg_cols.append("#16a34a")
                deg_sizes.append(28)
            else:
                deg_cols.append("#9333ea")
                deg_sizes.append(44)
    _plot_polylines(
        mesh,
        [e["points"] for e in after_topo["edges"] if not e.get("closed")],
        "#64748b",
        out / "03_endpoint_degree.png",
        f"{title_prefix} endpoint degree d1={graph['ENDPOINT_GRAPH_DEGREE1']}",
        points=deg_pts,
        point_colors=deg_cols,
        point_sizes=deg_sizes,
    )

    acc_lines = []
    rej_lines = []
    for c in branch_doc["accepted_connections"]:
        fi = next(f for f in frags if f["fragment_id"] == c["fragment_i"])
        fj = next(f for f in frags if f["fragment_id"] == c["fragment_j"])
        pa = fi["start_xyz"] if c["endpoint_i"] == "s" else fi["end_xyz"]
        pb = fj["start_xyz"] if c["endpoint_j"] == "s" else fj["end_xyz"]
        acc_lines.append(np.vstack([pa, pb]))
    for c in branch_doc["rejected_connections"][:40]:
        fi = next((f for f in frags if f["fragment_id"] == c["fragment_i"]), None)
        fj = next((f for f in frags if f["fragment_id"] == c["fragment_j"]), None)
        if not fi or not fj:
            continue
        pa = fi["start_xyz"] if c["endpoint_i"] == "s" else fi["end_xyz"]
        pb = fj["start_xyz"] if c["endpoint_j"] == "s" else fj["end_xyz"]
        rej_lines.append(np.vstack([pa, pb]))
    _plot_polylines(
        mesh,
        acc_lines or [np.zeros((2, 3))],
        "#16a34a",
        out / "04_accepted_continuations.png",
        f"{title_prefix} accepted n={len(acc_lines)}",
    )
    _plot_polylines(
        mesh,
        rej_lines or [np.zeros((2, 3))],
        "#dc2626",
        out / "05_rejected_continuations.png",
        f"{title_prefix} rejected sample n={len(rej_lines)}",
    )

    closed_eids = {eid for w in after_topo["wires"] if w.get("closed") for eid in w["edge_ids"]}
    _plot_polylines(
        mesh,
        [e["points"] for e in after_topo["edges"] if e["edge_id"] in closed_eids],
        "#0f766e",
        out / "06_closed_wires_faces.png",
        f"{title_prefix} closed wires={after_topo['n_closed']} faces={occ.get('VALID_TRIMMED_FACES')}",
    )
    _plot_polylines(
        mesh,
        [e["points"] for e in after_topo["edges"]],
        "#1d4ed8",
        out / "07_final_brep_edges.png",
        f"{title_prefix} shell={occ.get('CLOSED_SHELLS')} solid={occ.get('CLEAN_PARAMETRIC_PART_SOLIDS')}",
    )
