#!/usr/bin/env python3
"""V4: Point2CAD intersection polylines → tolerant corners → trimmed edges → OCC B-Rep.

Reuses frozen V3 clipped meshes + official topology curves. Does not re-run Dora / fitting.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

VIEW = np.array([[0.82, -0.38, 0.0], [0.22, 0.30, 0.86]], dtype=float)
EPS_CANDIDATES = (1e-4, 3e-4, 1e-3)


def dump_json(path: Path, obj: Any) -> None:
    def _default(x: Any) -> Any:
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, (np.floating,)):
            return float(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        return str(x)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=_default) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def bbox_diag(pts: np.ndarray) -> float:
    if len(pts) == 0:
        return 1.0
    return float(np.linalg.norm(np.ptp(pts, axis=0)))


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else np.asarray(v, dtype=float)


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def unnormalize_points(pts: np.ndarray, tf: dict) -> np.ndarray:
    mean = np.asarray(tf["mean"], dtype=float)
    r = np.asarray(tf["R"], dtype=float)
    scale = float(tf["scale"])
    return (np.linalg.inv(r) @ (np.asarray(pts, dtype=float).reshape(-1, 3) * scale).T).T + mean


def unnormalize_dir(v: np.ndarray, tf: dict) -> np.ndarray:
    r = np.asarray(tf["R"], dtype=float)
    return unit(np.linalg.inv(r) @ np.asarray(v, dtype=float).reshape(3))


def split_surfaces_by_color(clipped: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    fc = np.asarray(clipped.visual.face_colors)[:, :3]
    order = []
    seen = set()
    for row in fc:
        k = tuple(int(x) for x in row)
        if k not in seen:
            seen.add(k)
            order.append(k)
    out = []
    faces = np.asarray(clipped.faces)
    verts = np.asarray(clipped.vertices, dtype=float)
    for k in order:
        mask = np.all(fc == np.array(k)[None, :], axis=1)
        idx = np.where(mask)[0]
        if len(idx) < 1:
            continue
        sub = trimesh.Trimesh(vertices=verts, faces=faces[idx], process=False)
        sub.remove_unreferenced_vertices()
        out.append(sub)
    return out


def weld_polyline_graph(points: np.ndarray, lines: np.ndarray, weld: float) -> tuple[np.ndarray, list[tuple[int, int]]]:
    from scipy.spatial import cKDTree

    pts = np.asarray(points, dtype=float)
    if len(pts) == 0:
        return pts, []
    tree = cKDTree(pts)
    parent = list(range(len(pts)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in tree.query_pairs(weld):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a
    roots = {}
    new_of = [0] * len(pts)
    kept = []
    for i in range(len(pts)):
        r = find(i)
        if r not in roots:
            roots[r] = len(kept)
            kept.append(pts[r])
        new_of[i] = roots[r]
    welded = np.asarray(kept, dtype=float)
    edges = []
    seen = set()
    for a, b in np.asarray(lines, dtype=int):
        ua, ub = new_of[int(a)], new_of[int(b)]
        if ua == ub:
            continue
        ek = (ua, ub) if ua < ub else (ub, ua)
        if ek in seen:
            continue
        seen.add(ek)
        edges.append((ua, ub))
    return welded, edges


def polyline_components(points: np.ndarray, lines) -> list[np.ndarray]:
    adj: dict[int, list[int]] = defaultdict(list)
    for a, b in lines:
        if a == b:
            continue
        adj[int(a)].append(int(b))
        adj[int(b)].append(int(a))
    if not adj:
        return [points] if len(points) >= 2 else []
    visited_e: set[tuple[int, int]] = set()

    def ek(u: int, v: int) -> tuple[int, int]:
        return (u, v) if u < v else (v, u)

    def walk(start: int, nxt: int) -> list[int]:
        seq = [start, nxt]
        visited_e.add(ek(start, nxt))
        cur = nxt
        while True:
            nbs = [x for x in adj[cur] if ek(cur, x) not in visited_e]
            if not nbs:
                break
            chosen = nbs[0]
            visited_e.add(ek(cur, chosen))
            seq.append(chosen)
            cur = chosen
            if cur == start:
                break
        return seq

    chains = []
    deg1 = [i for i in adj if len(adj[i]) == 1]
    for s in deg1:
        for t in adj[s]:
            if ek(s, t) in visited_e:
                continue
            chains.append(walk(s, t))
    for u in list(adj.keys()):
        for v in adj[u]:
            if ek(u, v) in visited_e:
                continue
            chains.append(walk(u, v))
    out = []
    for seq in chains:
        pts = points[np.asarray(seq, dtype=int)]
        if len(pts) >= 2:
            out.append(pts)
    return out


def load_curves_world(topo: dict, weld: float) -> list[dict[str, Any]]:
    curves = []
    for i, c in enumerate(topo.get("curves") or []):
        pts = np.asarray(c.get("pv_points_world") or c.get("pv_points") or [], dtype=float)
        lines = np.asarray(c.get("pv_lines") or [], dtype=int)
        if len(pts) < 2:
            continue
        if len(lines):
            wpts, wedges = weld_polyline_graph(pts, lines, weld)
            comps = polyline_components(wpts, wedges)
        else:
            comps = [pts]
        curves.append(
            {
                "raw_id": i,
                "curve_id": f"RAW_{i:02d}",
                "points": pts,
                "components": comps,
                "n_components": len(comps),
            }
        )
    return curves


def assign_surface_pairs(curves: list[dict], surfaces: list[trimesh.Trimesh]) -> None:
    from scipy.spatial import cKDTree

    trees = []
    for s in surfaces:
        v = np.asarray(s.vertices, dtype=float)
        trees.append(cKDTree(v) if len(v) else None)
    for c in curves:
        pts = c["points"]
        sample = pts[np.linspace(0, len(pts) - 1, min(64, len(pts)), dtype=int)]
        dists = []
        for t in trees:
            if t is None:
                dists.append(1e9)
            else:
                dists.append(float(t.query(sample)[0].mean()))
        order = np.argsort(dists)
        a = int(order[0])
        b = int(order[1]) if len(order) > 1 else a
        c["surface_pair"] = (min(a, b), max(a, b))
        c["surface_dist"] = [float(dists[a]), float(dists[b])]


def recover_corners(curves: list[dict], diag: float, eps_frac: float) -> tuple[list[dict], int, dict]:
    """Official-curve point clouds, distance < eps, cluster. Prefer pairs sharing one surface."""
    from scipy.spatial import cKDTree

    eps = eps_frac * diag
    cands = []
    pair_stats = []
    for i, a in enumerate(curves):
        for j, b in enumerate(curves):
            if j <= i:
                continue
            sa, sb = set(a.get("surface_pair") or []), set(b.get("surface_pair") or [])
            share = sa & sb
            prefer = len(share) == 1
            lim = eps if prefer else 0.45 * eps
            tree = cKDTree(b["points"])
            d, idx = tree.query(a["points"])
            close = np.where(d < lim)[0]
            n_close = int(len(close))
            min_d = float(d.min()) if len(d) else 1e9
            pair_stats.append({"i": i, "j": j, "prefer": prefer, "min_d": min_d, "n_close": n_close})
            if n_close == 0:
                # fallback: shared-surface min-dist still under the scan ceiling
                if prefer and min_d < max(eps, 1e-3 * diag):
                    k = int(np.argmin(d))
                    mid = 0.5 * (a["points"][k] + b["points"][int(idx[k])])
                    cands.append({"xyz": mid, "dist": min_d, "curves": (i, j), "shared_surface": True})
                continue
            for k in close:
                pa = a["points"][int(k)]
                pb = b["points"][int(idx[int(k)])]
                cands.append(
                    {
                        "xyz": 0.5 * (pa + pb),
                        "dist": float(d[int(k)]),
                        "curves": (i, j),
                        "shared_surface": prefer,
                    }
                )
    n_cand = len(cands)
    if not cands:
        return [], n_cand, {"pairs": pair_stats, "eps": eps}

    xyzs = np.asarray([c["xyz"] for c in cands], dtype=float)
    parent = list(range(len(cands)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = cKDTree(xyzs)
    for p, q in tree.query_pairs(2.0 * eps):
        ra, rb = find(p), find(q)
        if ra != rb:
            parent[rb] = ra
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(cands)):
        groups[find(i)].append(i)

    merged = []
    for ids in groups.values():
        cluster = [cands[k] for k in ids]
        pts = np.asarray([c["xyz"] for c in cluster], dtype=float)
        diam = float(np.linalg.norm(pts.max(0) - pts.min(0)))
        if diam > 12.0 * eps and len(pts) > 4:
            # elongated near-miss: keep the tightest local minimum only
            best = min(cluster, key=lambda x: x["dist"])
            pts = np.asarray([best["xyz"]], dtype=float)
            cluster = [best]
            diam = 0.0
        xyz = np.mean(pts, axis=0)
        merged.append(
            {
                "vertex_id": f"VERTEX_{len(merged):03d}",
                "xyz": xyz.tolist(),
                "n_candidates": len(cluster),
                "mean_pair_dist": float(np.mean([x["dist"] for x in cluster])),
                "diameter": diam,
                "curve_ids": sorted({k for x in cluster for k in x["curves"]}),
                "shared_surface": bool(any(x["shared_surface"] for x in cluster)),
            }
        )
    return merged, n_cand, {"pairs": pair_stats, "eps": eps}


def pick_eps(curves, diag: float) -> tuple[float, list[dict], int, dict]:
    scored = []
    for frac in EPS_CANDIDATES:
        corners, ncand, extra = recover_corners(curves, diag, frac)
        n = len(corners)
        fat = sum(1 for c in corners if c.get("diameter", 0) > 8 * frac * diag)
        score = 8.0 * n - 6.0 * fat
        if len(curves) >= 2 and n == 0:
            score -= 25.0
        if n > 16:
            score -= 2.0 * (n - 16)
        # prefer 3e-4 when scores are close (stable CAD corners, not explosion)
        if frac == 3e-4:
            score += 1.5
        scored.append((score, frac, corners, ncand, extra))
    scored.sort(key=lambda x: -x[0])
    _, frac, corners, ncand, extra = scored[0]
    extra = dict(extra)
    extra["scan"] = [{"eps_frac": s[1], "n_corners": len(s[2]), "n_cand": s[3], "score": s[0]} for s in scored]
    return frac, corners, ncand, extra


def merge_close_corners(corners: list[dict], eps: float) -> list[dict]:
    if len(corners) < 2:
        return corners
    from scipy.spatial import cKDTree

    xyzs = np.asarray([c["xyz"] for c in corners], dtype=float)
    parent = list(range(len(corners)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = cKDTree(xyzs)
    for i, j in tree.query_pairs(4.0 * eps):
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(corners)):
        groups[find(i)].append(i)
    merged = []
    for ids in groups.values():
        cluster = [corners[k] for k in ids]
        pts = np.asarray([c["xyz"] for c in cluster], dtype=float)
        curve_ids = sorted({cid for c in cluster for cid in (c.get("curve_ids") or [])})
        merged.append(
            {
                "vertex_id": f"VERTEX_{len(merged):03d}",
                "xyz": np.mean(pts, axis=0).tolist(),
                "n_candidates": int(sum(c.get("n_candidates") or 1 for c in cluster)),
                "mean_pair_dist": float(np.mean([c.get("mean_pair_dist") or 0.0 for c in cluster])),
                "diameter": float(np.linalg.norm(pts.max(0) - pts.min(0))),
                "curve_ids": curve_ids,
                "shared_surface": bool(any(c.get("shared_surface") for c in cluster)),
            }
        )
    return merged


def arclength_params(pts: np.ndarray) -> np.ndarray:
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(s[-1]) if s[-1] > 1e-12 else 1.0
    return s / total


def project_point_on_polyline(pts: np.ndarray, p: np.ndarray) -> tuple[float, float, np.ndarray]:
    best = (1e9, 0.0, pts[0])
    params = arclength_params(pts)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        ab = b - a
        den = float(np.dot(ab, ab)) + 1e-18
        t = float(np.clip(np.dot(p - a, ab) / den, 0.0, 1.0))
        q = a + t * ab
        d = float(np.linalg.norm(p - q))
        tp = (1 - t) * params[i] + t * params[i + 1]
        if d < best[0]:
            best = (d, tp, q)
    return best


def downsample_poly(pts: np.ndarray, n: int) -> np.ndarray:
    if len(pts) <= n:
        return pts
    idx = np.linspace(0, len(pts) - 1, n, dtype=int)
    return pts[idx]


def _slice_poly(pts: np.ndarray, t0: float, t1: float, p0: np.ndarray, p1: np.ndarray) -> np.ndarray:
    params = arclength_params(pts)
    mask = (params >= t0 - 1e-9) & (params <= t1 + 1e-9)
    sub = pts[mask]
    if len(sub) < 2:
        return np.vstack([p0, p1])
    return np.vstack([p0, sub, p1])


def trim_edges(curves: list[dict], corners: list[dict], diag: float, eps: float) -> list[dict]:
    edges = []
    snap = 3.0 * eps
    for ci, c in enumerate(curves):
        comps = c.get("components") or [c["points"]]
        lengths = [float(np.linalg.norm(np.diff(pl, axis=0), axis=1).sum()) if len(pl) > 1 else 0.0 for pl in comps]
        max_len = max(lengths) if lengths else 0.0
        for j, pts in enumerate(comps):
            length = lengths[j]
            closed_comp = float(np.linalg.norm(pts[0] - pts[-1])) < max(snap, 0.01 * max(length, 1e-9)) and len(pts) > 8
            hits = []
            snap_hit = max(snap, 8.0 * eps)
            for v in corners:
                if v.get("endpoint"):
                    continue
                d, t, q = project_point_on_polyline(pts, np.asarray(v["xyz"], dtype=float))
                if d < snap_hit:
                    hits.append((t, v["vertex_id"], np.asarray(v["xyz"], dtype=float), d))
            vlookup = {v["vertex_id"]: np.asarray(v["xyz"], dtype=float) for v in corners if not v.get("endpoint")}
            for t_end, p_end, tag in ((0.0, pts[0], "START"), (1.0, pts[-1], "END")):
                near = None
                best_d = 1e9
                q_near = p_end
                for v in corners:
                    if v.get("endpoint"):
                        continue
                    dd = float(np.linalg.norm(np.asarray(v["xyz"]) - p_end))
                    if dd < snap_hit and dd < best_d:
                        near = v["vertex_id"]
                        best_d = dd
                        q_near = np.asarray(v["xyz"], dtype=float)
                has_real_so_far = any(not str(h[1]).startswith("ENDPOINT_") for h in hits)
                if near is None and not closed_comp and (has_real_so_far or length >= 0.15 * max(max_len, 1e-9)):
                    vid = f"ENDPOINT_{c['curve_id']}_{j:02d}_{tag}"
                    corners.append(
                        {
                            "vertex_id": vid,
                            "xyz": np.asarray(p_end, dtype=float).tolist(),
                            "n_candidates": 0,
                            "endpoint": True,
                            "curve_ids": [ci],
                        }
                    )
                    near = vid
                    q_near = p_end
                if near is not None:
                    hits.append((t_end, near, q_near, 0.0))
            has_real = any(not str(h[1]).startswith("ENDPOINT_") for h in hits)
            if not has_real and not closed_comp:
                continue
            hits.sort(key=lambda x: x[0])
            uniq = []
            for h in hits:
                if not uniq or abs(h[0] - uniq[-1][0]) > 0.015:
                    uniq.append(h)
                elif h[3] < uniq[-1][3]:
                    uniq[-1] = h
            if closed_comp and len(uniq) < 2:
                edges.append(
                    {
                        "edge_id": f"EDGE_{len(edges):03d}",
                        "raw_curve": c["curve_id"],
                        "v_start": uniq[0][1] if uniq else None,
                        "v_end": uniq[0][1] if uniq else None,
                        "closed": True,
                        "surfaces": list(c.get("surface_pair") or []),
                        "points": downsample_poly(pts, 80),
                        "length": length,
                    }
                )
                continue
            if len(uniq) < 2:
                continue
            for a, b in zip(uniq, uniq[1:]):
                if b[0] - a[0] < 0.02:
                    continue
                sub = _slice_poly(pts, a[0], b[0], a[2], b[2])
                edges.append(
                    {
                        "edge_id": f"EDGE_{len(edges):03d}",
                        "raw_curve": c["curve_id"],
                        "v_start": a[1],
                        "v_end": b[1],
                        "closed": False,
                        "surfaces": list(c.get("surface_pair") or []),
                        "points": downsample_poly(sub, 80),
                        "length": float(np.linalg.norm(np.diff(sub, axis=0), axis=1).sum()),
                    }
                )
            if closed_comp and uniq[0][1] != uniq[-1][1]:
                a, b = uniq[-1], uniq[0]
                params = arclength_params(pts)
                sub = np.vstack([pts[params >= a[0] - 1e-9], pts[params <= b[0] + 1e-9]])
                if len(sub) >= 2:
                    edges.append(
                        {
                            "edge_id": f"EDGE_{len(edges):03d}",
                            "raw_curve": c["curve_id"],
                            "v_start": a[1],
                            "v_end": b[1],
                            "closed": False,
                            "surfaces": list(c.get("surface_pair") or []),
                            "points": downsample_poly(sub, 80),
                            "length": float(np.linalg.norm(np.diff(sub, axis=0), axis=1).sum()),
                        }
                    )
    return edges


def classify_edges_from_wires(edges: list[dict], wires: list[dict]) -> dict[str, int]:
    closed = [w for w in wires if w.get("closed")]
    deg = Counter()
    for e in edges:
        n = sum(1 for w in closed if e["edge_id"] in (w.get("edge_ids") or []))
        if n <= 0:
            # fall back to intended surface-pair incidence if no closed face yet
            n_surf = len(set(e.get("surfaces") or []))
            label = {0: "ZERO", 1: "FREE", 2: "MANIFOLD"}.get(n_surf, "NONMANIFOLD")
            e["face_degree"] = n_surf
            e["class"] = label
            e["face_degree_from_wires"] = 0
            deg[label] += 1
        else:
            label = {1: "FREE", 2: "MANIFOLD"}.get(n, "NONMANIFOLD")
            e["face_degree"] = n
            e["face_degree_from_wires"] = n
            e["class"] = label
            deg[label] += 1
    return {
        "ZERO_EDGES": int(deg["ZERO"]),
        "FREE_EDGES": int(deg["FREE"]),
        "MANIFOLD_EDGES": int(deg["MANIFOLD"]),
        "NONMANIFOLD_EDGES": int(deg["NONMANIFOLD"]),
    }


def recover_wires(n_surf: int, edges: list[dict]) -> list[dict]:
    wires = []
    for si in range(n_surf):
        local = [e for e in edges if si in (e.get("surfaces") or [])]
        if not local:
            continue
        closed_loops = [e for e in local if e.get("closed")]
        open_e = [e for e in local if not e.get("closed")]
        # a lone closed intersection is a complete wire only if it is the only edge
        if len(local) == 1:
            for e in closed_loops:
                wires.append(
                    {
                        "wire_id": f"WIRE_{len(wires):03d}",
                        "surface": si,
                        "edge_ids": [e["edge_id"]],
                        "vertex_ids": [e.get("v_start"), e.get("v_end")],
                        "closed": True,
                        "kind": "closed_loop_edge",
                    }
                )
        if not open_e:
            continue
        adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for e in open_e:
            if e.get("v_start") and e.get("v_end") and e["v_start"] != e["v_end"]:
                adj[e["v_start"]].append((e["v_end"], e["edge_id"]))
                adj[e["v_end"]].append((e["v_start"], e["edge_id"]))
        used = set()

        def unused_from(v: str) -> list[tuple[str, str]]:
            return [(w, eid) for w, eid in adj[v] if eid not in used]

        # cycles: start at any vertex that still has unused edges
        for start in list(adj.keys()):
            while unused_from(start):
                nxt, eid0 = unused_from(start)[0]
                seq_e = [eid0]
                seq_v = [start, nxt]
                used.add(eid0)
                cur = nxt
                found = False
                for _ in range(len(open_e) + 2):
                    nbs = unused_from(cur)
                    if not nbs:
                        break
                    # prefer returning to start if possible
                    back = [(w, e) for w, e in nbs if w == start]
                    v2, e2 = (back[0] if back else nbs[0])
                    seq_e.append(e2)
                    seq_v.append(v2)
                    used.add(e2)
                    cur = v2
                    if cur == start:
                        found = True
                        break
                real_vs = [v for v in seq_v[:-1] if v and not str(v).startswith("ENDPOINT_")]
                if found and len(seq_e) >= 2 and len(set(real_vs)) >= 2:
                    wires.append(
                        {
                            "wire_id": f"WIRE_{len(wires):03d}",
                            "surface": si,
                            "edge_ids": seq_e,
                            "vertex_ids": seq_v[:-1],
                            "closed": True,
                            "kind": "cycle",
                        }
                    )
                else:
                    wires.append(
                        {
                            "wire_id": f"WIRE_{len(wires):03d}",
                            "surface": si,
                            "edge_ids": seq_e,
                            "vertex_ids": seq_v,
                            "closed": False,
                            "kind": "open_walk",
                        }
                    )
        leftover = [e for e in open_e if e["edge_id"] not in used]
        if leftover:
            wires.append(
                {
                    "wire_id": f"WIRE_{len(wires):03d}",
                    "surface": si,
                    "edge_ids": [e["edge_id"] for e in leftover],
                    "vertex_ids": [leftover[0].get("v_start"), leftover[-1].get("v_end")],
                    "closed": False,
                    "kind": "leftover",
                }
            )
    return wires


def load_surface_models(fits: list[dict], tf: dict | None, meshes: list[trimesh.Trimesh]) -> list[dict]:
    models = []
    for i, mesh in enumerate(meshes):
        info = fits[i] if i < len(fits) else {}
        typ = str(info.get("type") or "open_spline")
        params = info.get("params")
        model: dict[str, Any] = {"type": typ, "mesh": mesh}
        pts = np.asarray(mesh.vertices, dtype=float)
        c = pts.mean(0)
        _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
        model["origin"] = c.tolist()
        model["normal"] = unit(vt[-1]).tolist()
        if typ == "plane" and params is not None and tf is not None:
            n = np.asarray(params[0], dtype=float).reshape(-1)[:3]
            d = float(np.asarray(params[1]).reshape(-1)[0])
            r = np.asarray(tf["R"], dtype=float)
            n_w = unit(r.T @ n)
            mean = np.asarray(tf["mean"], dtype=float)
            scale = float(tf["scale"])
            # n·p = d in normalized space → n_w·p_w = n_w·mean + d*scale
            origin = mean + n_w * (d * scale)
            model["origin"] = origin.tolist()
            model["normal"] = n_w.tolist()
        elif typ == "cylinder" and params is not None and tf is not None:
            axis, center, radius = params
            model["axis"] = unnormalize_dir(np.asarray(axis, dtype=float), tf).tolist()
            model["center"] = unnormalize_points(np.asarray(center, dtype=float).reshape(1, 3), tf)[0].tolist()
            model["radius"] = float(radius) * float(tf["scale"])
        elif typ == "cone" and params is not None and tf is not None:
            apex, axis, theta = params
            model["apex"] = unnormalize_points(np.asarray(apex, dtype=float).reshape(1, 3), tf)[0].tolist()
            model["axis"] = unnormalize_dir(np.asarray(axis, dtype=float), tf).tolist()
            model["theta"] = float(theta)
        elif typ == "sphere" and params is not None and tf is not None:
            center, radius = params
            model["center"] = unnormalize_points(np.asarray(center, dtype=float).reshape(1, 3), tf)[0].tolist()
            model["radius"] = float(radius) * float(tf["scale"])
        models.append(model)
    return models


def occ_bspline_edge(pts: np.ndarray, closed: bool = False):
    from OCP.GeomAPI import GeomAPI_PointsToBSpline
    from OCP.TColgp import TColgp_Array1OfPnt
    from OCP.gp import gp_Pnt
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

    pl = np.asarray(pts, dtype=float)
    if closed and np.linalg.norm(pl[0] - pl[-1]) > 1e-12:
        pl = np.vstack([pl, pl[0]])
    if len(pl) > 80:
        pl = pl[np.linspace(0, len(pl) - 1, 80, dtype=int)]
    arr = TColgp_Array1OfPnt(1, len(pl))
    for i, p in enumerate(pl, 1):
        arr.SetValue(i, gp_Pnt(float(p[0]), float(p[1]), float(p[2])))
    crv = GeomAPI_PointsToBSpline(arr).Curve()
    return BRepBuilderAPI_MakeEdge(crv).Edge(), crv


def try_analytic_edge(sa: dict, sb: dict, pts: np.ndarray, diag: float):
    from OCP.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt
    from OCP.Geom import Geom_CylindricalSurface, Geom_ConicalSurface, Geom_Plane, Geom_TrimmedCurve
    from OCP.GeomAPI import GeomAPI_IntSS, GeomAPI_ProjectPointOnCurve
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

    def as_geom(s: dict):
        if s["type"] == "plane":
            o = np.asarray(s["origin"], dtype=float)
            n = unit(np.asarray(s["normal"], dtype=float))
            return Geom_Plane(gp_Pln(gp_Pnt(float(o[0]), float(o[1]), float(o[2])), gp_Dir(float(n[0]), float(n[1]), float(n[2]))))
        if s["type"] == "cylinder":
            c = np.asarray(s["center"], dtype=float)
            a = unit(np.asarray(s["axis"], dtype=float))
            ax = gp_Ax3(gp_Pnt(float(c[0]), float(c[1]), float(c[2])), gp_Dir(float(a[0]), float(a[1]), float(a[2])))
            return Geom_CylindricalSurface(ax, float(s["radius"]))
        if s["type"] == "cone":
            apex = np.asarray(s["apex"], dtype=float)
            axis = unit(np.asarray(s["axis"], dtype=float))
            theta = float(s["theta"])
            sample = pts[np.linspace(0, len(pts) - 1, min(8, len(pts)), dtype=int)]
            hs = [(np.dot(p - apex, axis), p) for p in sample]
            h_use = max((abs(h) for h, _ in hs), default=0.0)
            if h_use < 1e-9:
                return None
            sign = 1.0 if sum(h for h, _ in hs) >= 0 else -1.0
            origin = apex + axis * (sign * 0.5 * h_use)
            radius = abs(0.5 * h_use * np.tan(theta))
            if radius < 1e-12:
                return None
            ax = gp_Ax3(gp_Pnt(float(origin[0]), float(origin[1]), float(origin[2])), gp_Dir(float(sign * axis[0]), float(sign * axis[1]), float(sign * axis[2])))
            return Geom_ConicalSurface(ax, radius, theta)
        return None

    ga, gb = as_geom(sa), as_geom(sb)
    if ga is None or gb is None:
        return None
    try:
        inter = GeomAPI_IntSS(ga, gb, 1e-7)
        if not inter.IsDone() or inter.NbLines() < 1:
            return None
        sample = pts[np.linspace(0, len(pts) - 1, min(12, len(pts)), dtype=int)]
        best = None
        for k in range(1, inter.NbLines() + 1):
            crv = inter.Line(k)
            dists, ts = [], []
            for p in sample:
                proj = GeomAPI_ProjectPointOnCurve(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), crv)
                if proj.NbPoints() < 1:
                    continue
                dists.append(proj.LowerDistance())
                ts.append(proj.LowerDistanceParameter())
            if not dists:
                continue
            score = float(np.mean(dists))
            if best is None or score < best[0]:
                best = (score, crv, ts)
        if best is None or best[0] > 0.02 * diag:
            return None
        tmin, tmax = float(min(best[2])), float(max(best[2]))
        if abs(tmax - tmin) < 1e-9:
            return None
        trim = Geom_TrimmedCurve(best[1], tmin, tmax)
        return BRepBuilderAPI_MakeEdge(trim).Edge()
    except Exception:
        return None


def _geom_from_model(s: dict):
    from OCP.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt
    from OCP.Geom import Geom_CylindricalSurface, Geom_ConicalSurface, Geom_Plane

    if s["type"] == "plane":
        o = np.asarray(s["origin"], dtype=float)
        n = unit(np.asarray(s["normal"], dtype=float))
        return Geom_Plane(gp_Pln(gp_Pnt(float(o[0]), float(o[1]), float(o[2])), gp_Dir(float(n[0]), float(n[1]), float(n[2]))))
    if s["type"] == "cylinder":
        c = np.asarray(s["center"], dtype=float)
        a = unit(np.asarray(s["axis"], dtype=float))
        ax = gp_Ax3(gp_Pnt(float(c[0]), float(c[1]), float(c[2])), gp_Dir(float(a[0]), float(a[1]), float(a[2])))
        return Geom_CylindricalSurface(ax, float(s["radius"]))
    if s["type"] == "cone":
        apex = np.asarray(s["apex"], dtype=float)
        axis = unit(np.asarray(s["axis"], dtype=float))
        theta = float(s["theta"])
        origin = apex + axis * 0.05
        radius = abs(0.05 * np.tan(theta)) if abs(theta) > 1e-6 else 0.05
        ax = gp_Ax3(gp_Pnt(float(origin[0]), float(origin[1]), float(origin[2])), gp_Dir(float(axis[0]), float(axis[1]), float(axis[2])))
        return Geom_ConicalSurface(ax, max(radius, 1e-6), theta)
    return None


def bspline_surface_from_mesh(mesh: trimesh.Trimesh):
    from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.gp import gp_Pnt

    pts = np.asarray(mesh.vertices, dtype=float)
    if len(pts) < 16:
        return None
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    uv = (pts - c) @ vt[:2].T
    nu = nv = 8
    umin, vmin = uv.min(0)
    umax, vmax = uv.max(0)
    grid = np.zeros((nu, nv, 3))
    cnt = np.zeros((nu, nv))
    iu = np.clip(((uv[:, 0] - umin) / max(umax - umin, 1e-12) * (nu - 1)).astype(int), 0, nu - 1)
    iv = np.clip(((uv[:, 1] - vmin) / max(vmax - vmin, 1e-12) * (nv - 1)).astype(int), 0, nv - 1)
    for p, i, j in zip(pts, iu, iv):
        grid[i, j] += p
        cnt[i, j] += 1
    for i in range(nu):
        for j in range(nv):
            if cnt[i, j] > 0:
                grid[i, j] /= cnt[i, j]
            else:
                u = umin + (umax - umin) * i / max(nu - 1, 1)
                v = vmin + (vmax - vmin) * j / max(nv - 1, 1)
                grid[i, j] = c + u * vt[0] + v * vt[1]
    arr = TColgp_Array2OfPnt(1, nu, 1, nv)
    for i in range(nu):
        for j in range(nv):
            p = grid[i, j]
            arr.SetValue(i + 1, j + 1, gp_Pnt(float(p[0]), float(p[1]), float(p[2])))
    try:
        return GeomAPI_PointsToBSplineSurface(arr).Surface()
    except Exception:
        return None


def build_occ(
    part_mesh: trimesh.Trimesh,
    surf_models: list[dict],
    edges: list[dict],
    wires: list[dict],
    vertices: list[dict],
    step_path: Path,
    eps: float,
) -> dict:
    verts = np.asarray(part_mesh.vertices, dtype=float)
    diag = max(bbox_diag(verts), 1e-12)
    try:
        from OCP.BRepBuilderAPI import (
            BRepBuilderAPI_MakeEdge,
            BRepBuilderAPI_MakeFace,
            BRepBuilderAPI_MakeSolid,
            BRepBuilderAPI_MakeVertex,
            BRepBuilderAPI_MakeWire,
            BRepBuilderAPI_Sewing,
        )
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepFill import BRepFill_Filling
        from OCP.GeomAbs import GeomAbs_C0
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        from OCP.ShapeFix import ShapeFix_Face, ShapeFix_Solid, ShapeFix_Wire
        from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
        from OCP.TopExp import TopExp, TopExp_Explorer
        from OCP.TopoDS import TopoDS, TopoDS_Compound
        from OCP.BRep import BRep_Builder
        from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
        from OCP.BRepLib import BRepLib
        from OCP.gp import gp_Pnt
        from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve
    except Exception as exc:
        return {"BREP_VALID": False, "CAD_NATIVE": False, "failure_class": "OCC_IMPORT_FAILURE", "error": str(exc)}

    vmap = {}
    for v in vertices:
        p = np.asarray(v["xyz"], dtype=float)
        vmap[v["vertex_id"]] = BRepBuilderAPI_MakeVertex(gp_Pnt(float(p[0]), float(p[1]), float(p[2]))).Vertex()

    master_edges = {}
    edge_source = {}
    for e in edges:
        pts = np.asarray(e["points"], dtype=float)
        if len(pts) < 2:
            continue
        if e.get("v_start") in vmap:
            pts[0] = np.asarray(next(v["xyz"] for v in vertices if v["vertex_id"] == e["v_start"]), dtype=float)
        if e.get("v_end") in vmap:
            pts[-1] = np.asarray(next(v["xyz"] for v in vertices if v["vertex_id"] == e["v_end"]), dtype=float)
        occ_e = None
        crv = None
        surfs = e.get("surfaces") or []
        if len(surfs) >= 2:
            occ_e = try_analytic_edge(surf_models[surfs[0]], surf_models[surfs[1]], pts, diag)
            if occ_e is not None:
                edge_source[e["edge_id"]] = "OCC_SURFACE_INTERSECTION"
        if occ_e is None:
            try:
                occ_e, crv = occ_bspline_edge(pts, closed=bool(e.get("closed")))
                edge_source[e["edge_id"]] = "P2C_POLYLINE_BSPLINE"
            except Exception:
                continue
        vs, ve = vmap.get(e.get("v_start")), vmap.get(e.get("v_end"))
        if crv is not None and vs is not None and ve is not None and not e.get("closed"):
            try:
                occ_e = BRepBuilderAPI_MakeEdge(crv, vs, ve).Edge()
            except Exception:
                pass
        master_edges[e["edge_id"]] = occ_e

    faces_out = []
    closed_wires_built = 0
    valid_faces = 0
    pcurve_ok = 0
    for w in wires:
        if not w.get("closed"):
            continue
        if w.get("kind") not in ("cycle", "closed_loop_edge"):
            continue
        ids = [eid for eid in w["edge_ids"] if eid in master_edges]
        if not ids:
            continue
        try:
            mw = BRepBuilderAPI_MakeWire()
            for eid in ids:
                mw.Add(master_edges[eid])
            if not mw.IsDone():
                continue
            wire = mw.Wire()
            fixer = ShapeFix_Wire()
            fixer.Load(wire)
            fixer.SetPrecision(max(eps, 1e-6))
            fixer.SetMaxTolerance(max(0.01 * diag, 20.0 * eps))
            try:
                fixer.FixConnected()
                fixer.FixClosed()
            except Exception:
                pass
            fixer.Perform()
            wire = fixer.Wire()
            closed_wires_built += 1
            si = int(w["surface"])
            model = surf_models[si]
            face = None
            geom = _geom_from_model(model)
            if geom is not None:
                try:
                    face = BRepBuilderAPI_MakeFace(geom, wire).Face()
                except Exception:
                    face = None
            if (face is None or face.IsNull()) and model["type"] in ("open_spline", "closed_spline"):
                try:
                    surf = bspline_surface_from_mesh(model["mesh"])
                    if surf is not None:
                        face = BRepBuilderAPI_MakeFace(surf, wire).Face()
                except Exception:
                    face = None
            if face is None or face.IsNull():
                try:
                    fill = BRepFill_Filling()
                    ex = TopExp_Explorer(wire, TopAbs_EDGE)
                    nadd = 0
                    while ex.More():
                        fill.Add(TopoDS.Edge_s(ex.Current()), GeomAbs_C0)
                        nadd += 1
                        ex.Next()
                    if nadd >= 1:
                        fill.Build()
                        if fill.IsDone():
                            face = fill.Face()
                except Exception:
                    face = None
            if face is None or face.IsNull():
                try:
                    face = BRepBuilderAPI_MakeFace(wire, True).Face()
                except Exception:
                    face = None
            if face is not None and not face.IsNull():
                try:
                    sff = ShapeFix_Face(face)
                    sff.SetPrecision(max(eps, 1e-6))
                    sff.Perform()
                    face = sff.Face()
                    BRepLib.BuildCurves3d_s(face)
                    pcurve_ok += 1
                except Exception:
                    pass
                faces_out.append(face)
                valid_faces += 1
        except Exception:
            continue

    if not faces_out:
        return {
            "BREP_VALID": False,
            "CAD_NATIVE": False,
            "failure_class": "NO_OCC_FACE",
            "VALID_TRIMMED_FACES": 0,
            "CLOSED_WIRES_BUILT": closed_wires_built,
            "MASTER_EDGES": len(master_edges),
            "EDGE_SOURCE": dict(Counter(edge_source.values())),
            "DUAL_PCURVE_FACES": pcurve_ok,
        }

    sew_tol = 0.002 * diag
    sewing = BRepBuilderAPI_Sewing(sew_tol)
    for f in faces_out:
        sewing.Add(f)
    sewing.Perform()
    sewn = sewing.SewedShape()
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    solids = 0
    closed_shells = 0
    shells = 0
    clean_solids = 0

    def count(shape, kind) -> int:
        e = TopExp_Explorer(shape, kind)
        n = 0
        while e.More():
            n += 1
            e.Next()
        return n

    def free_edges(shape) -> int:
        try:
            imap = TopTools_IndexedDataMapOfShapeListOfShape()
            TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, imap)
            return sum(1 for i in range(1, imap.Size() + 1) if imap.FindFromIndex(i).Size() < 2)
        except Exception:
            return -1

    try:
        ex = TopExp_Explorer(sewn, TopAbs_SHELL)
        added = 0
        while ex.More():
            sh = TopoDS.Shell_s(ex.Current())
            shells += 1
            n_faces = count(sh, TopAbs_FACE)
            n_free = free_edges(sh)
            is_closed = bool(sh.Closed()) and n_free == 0 and n_faces >= 4
            if is_closed:
                closed_shells += 1
                try:
                    ms = BRepBuilderAPI_MakeSolid(sh)
                    if ms.IsDone():
                        solid = ms.Solid()
                        try:
                            sfs = ShapeFix_Solid(solid)
                            sfs.Perform()
                            solid = sfs.Solid()
                        except Exception:
                            pass
                        ana = BRepCheck_Analyzer(solid)
                        builder.Add(compound, solid)
                        solids += 1
                        added += 1
                        if ana.IsValid() and n_free == 0:
                            clean_solids += 1
                    else:
                        builder.Add(compound, sh)
                        added += 1
                except Exception:
                    builder.Add(compound, sh)
                    added += 1
            else:
                builder.Add(compound, sh)
                added += 1
            ex.Next()
        if added == 0:
            builder.Add(compound, sewn)
    except Exception:
        builder.Add(compound, sewn)

    free = free_edges(compound)
    step_path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    ok = writer.Write(str(step_path)) == IFSelect_RetDone and step_path.is_file()
    ana = BRepCheck_Analyzer(compound)
    return {
        "BREP_VALID": bool(ok and ana.IsValid() and clean_solids > 0),
        "STEP_RELOAD_VALID": bool(ok),
        "CAD_NATIVE": True,
        "VALID_TRIMMED_FACES": valid_faces,
        "CLOSED_WIRES_BUILT": closed_wires_built,
        "SHELL_COUNT": shells if shells else count(compound, TopAbs_SHELL),
        "CLOSED_SHELLS": closed_shells,
        "SOLID_COUNT": solids,
        "CLEAN_PARAMETRIC_PART_SOLIDS": int(clean_solids),
        "FREE_EDGE_COUNT": free,
        "FACE_COUNT": count(compound, TopAbs_FACE),
        "MASTER_EDGES": len(master_edges),
        "EDGE_SOURCE": dict(Counter(edge_source.values())),
        "SEWING_TOLERANCE_NORMALIZED": sew_tol / diag,
        "STEP_PATH": str(step_path),
        "DUAL_PCURVE_FACES": pcurve_ok,
        "CAD_NATIVE_OPEN_SHELL": bool(solids == 0 and (shells or count(compound, TopAbs_SHELL)) > 0),
    }


def render_topo(mesh, edges, corners, path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection

    v = np.asarray(mesh.vertices, dtype=float)
    f = np.asarray(mesh.faces, dtype=int)
    if len(f) > 3500:
        f = f[np.linspace(0, len(f) - 1, 3500, dtype=int)]
    p2 = v @ VIEW.T
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=130)
    ax.add_collection(
        PolyCollection(
            [p2[tri] for tri in f],
            facecolors=(0.75, 0.76, 0.78, 0.25),
            edgecolors=(0.5, 0.5, 0.52, 0.08),
            linewidths=0.03,
        )
    )
    segs = []
    for e in edges:
        q = np.asarray(e["points"]) @ VIEW.T
        if len(q) >= 2:
            segs.append(q)
    if segs:
        ax.add_collection(LineCollection(segs, colors="#1d4ed8", linewidths=1.4, alpha=0.95))
    if corners:
        cxyz = np.asarray([c["xyz"] for c in corners], dtype=float) @ VIEW.T
        ax.scatter(cxyz[:, 0], cxyz[:, 1], s=28, c="#b91c1c", zorder=5)
    c = p2.mean(0)
    r = max(float(np.ptp(p2, axis=0).max()) * 0.58, 1e-8)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def process_part(pid: str, v3_part: Path, xpart_mesh: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(xpart_mesh)
    diag = max(bbox_diag(np.asarray(mesh.vertices, dtype=float)), 1e-12)
    p2c = v3_part / "point2cad"
    topo = load_json(p2c / "topo/topo_world.json") or load_json(p2c / "topo/topo.json") or {}
    fits_doc = load_json(p2c / "surface_fits.json") or {}
    tf = load_json(p2c / "p2c_normalize_transform.json")
    clipped_path = p2c / "clipped/mesh_world.ply"
    if not clipped_path.is_file():
        clipped_path = p2c / "clipped/mesh.ply"
    clipped = load_mesh(clipped_path)
    surfaces = split_surfaces_by_color(clipped)
    weld = max(1e-6, 1e-5 * diag)
    curves = load_curves_world(topo, weld)
    if surfaces and curves:
        assign_surface_pairs(curves, surfaces)
    else:
        for c in curves:
            c["surface_pair"] = (0, 0)
    frac, corners, n_cand, extra = pick_eps(curves, diag)
    eps = frac * diag
    corners = merge_close_corners(corners, eps)
    corner_work = [dict(v) for v in corners]
    edges = trim_edges(curves, corner_work, diag, eps)
    used_v = {e["v_start"] for e in edges} | {e["v_end"] for e in edges}
    vertices = [v for v in corner_work if v["vertex_id"] in used_v or not v.get("endpoint")]
    topo_corners = [v for v in vertices if not v.get("endpoint")]
    wires = recover_wires(len(surfaces), edges)
    deg = classify_edges_from_wires(edges, wires)
    n_closed = sum(1 for w in wires if w.get("closed"))
    n_open = sum(1 for w in wires if not w.get("closed"))
    with_face = [e for e in edges if e.get("face_degree", 0) > 0]
    inc_rate = float(sum(1 for e in with_face if e["face_degree"] == 2) / max(len(with_face), 1))
    v_inc = defaultdict(list)
    for e in edges:
        for vid in (e.get("v_start"), e.get("v_end")):
            if vid:
                v_inc[vid].append(e["edge_id"])
    dump_json(
        out_dir / "incidence_graph.json",
        {
            "vertices": [
                {
                    "vertex_id": v["vertex_id"],
                    "xyz": v["xyz"],
                    "endpoint": bool(v.get("endpoint")),
                    "incident_edges": v_inc.get(v["vertex_id"], []),
                }
                for v in vertices
            ],
            "edges": [
                {k: (e[k].tolist() if isinstance(e[k], np.ndarray) else e[k]) for k in e if k != "points"}
                | {"n_points": len(e["points"])}
                for e in edges
            ],
            "wires": wires,
            "surface_count": len(surfaces),
            "official_curves": [
                {"curve_id": c["curve_id"], "surface_pair": c.get("surface_pair"), "n_components": c.get("n_components")}
                for c in curves
            ],
        },
    )
    dump_json(out_dir / "corners.json", topo_corners)
    dump_json(out_dir / "trimmed_edges.json", [{k: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for k, vv in e.items() if k != "points"} for e in edges])
    dump_json(out_dir / "wires.json", wires)
    dump_json(out_dir / "corner_scan.json", extra)
    try:
        render_topo(mesh, edges, topo_corners, out_dir / "renders/01_corners_edges.png", f"{pid} corners={len(topo_corners)} edges={len(edges)}")
        closed_e = [e for e in edges if any(w.get("closed") and e["edge_id"] in w["edge_ids"] for w in wires)]
        render_topo(mesh, closed_e or edges, topo_corners, out_dir / "renders/02_trimmed_edges.png", f"{pid} closed-wire edges")
    except Exception:
        pass
    surf_models = load_surface_models(fits_doc.get("fits") or [], tf, surfaces)
    s3 = build_occ(mesh, surf_models, edges, wires, vertices, out_dir / f"{pid}.step", eps)
    dump_json(out_dir / "brep.json", s3)
    qa = {}
    try:
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import routeb_edge_curve_recovery_v2 as v2

        if (out_dir / f"{pid}.step").is_file():
            qa = v2.geometry_qa(mesh, out_dir / f"{pid}.step")
    except Exception as exc:
        qa = {"GEOMETRY_QA_FAIL": True, "error": str(exc)}
    dump_json(out_dir / "qa.json", qa)
    row = {
        "part": pid,
        "POINT2CAD_SURFACES_REUSED": True,
        "POINT2CAD_INTERSECTIONS_REUSED": True,
        "bbox_diagonal": diag,
        "eps_frac": frac,
        "eps_abs": eps,
        "n_surfaces": len(surfaces),
        "RAW_INTERSECTION_CURVES": len(curves),
        "OFFICIAL_CURVE_COMPONENTS": int(sum(c.get("n_components") or 0 for c in curves)),
        "CORNER_CANDIDATES": n_cand,
        "MERGED_TOPO_CORNERS": len(topo_corners),
        "RAW_INTERSECTION_EDGES": len(curves),
        "TRIMMED_TOPO_EDGES": len(edges),
        **deg,
        "FACE_EDGE_INCIDENCE_VALID_RATE": inc_rate,
        "WIRE_COUNT": len(wires),
        "CLOSED_WIRES": n_closed,
        "OPEN_WIRES": n_open,
        **s3,
        "qa": qa,
    }
    dump_json(out_dir / "part_gate.json", {k: v for k, v in row.items() if k != "qa"})
    return row
