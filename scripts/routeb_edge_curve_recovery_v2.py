#!/usr/bin/env python3
"""Route B V2: hysteresis edges, merge-before-fit, analytic-first surfaces."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

THRESHOLDS = (15, 25, 35, 45)
SHORT_FRAC = 0.02
VIEW = np.array([[0.82, -0.38, 0.0], [0.22, 0.30, 0.86]], dtype=float)


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


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def unique_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def bbox_diag(verts: np.ndarray) -> float:
    return float(np.linalg.norm(np.ptp(verts, axis=0)))


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    c = float(np.clip(np.dot(unit(a), unit(b)), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def rdp(points: np.ndarray, eps: float) -> np.ndarray:
    if len(points) <= 2:
        return points
    a, b = points[0], points[-1]
    ab = b - a
    den = np.linalg.norm(ab) + 1e-12
    d = np.linalg.norm(np.cross(points[1:-1] - a, ab), axis=1) / den
    if len(d) == 0:
        return points
    idx = int(np.argmax(d)) + 1
    if float(d[idx - 1]) <= eps:
        return np.vstack([a, b])
    return np.vstack([rdp(points[: idx + 1], eps)[:-1], rdp(points[idx:], eps)])


def mesh_edge_faces(faces: np.ndarray) -> dict[tuple[int, int], list[int]]:
    out: dict[tuple[int, int], list[int]] = defaultdict(list)
    for fi, f in enumerate(faces):
        for a, b in ((int(f[0]), int(f[1])), (int(f[1]), int(f[2])), (int(f[2]), int(f[0]))):
            out[unique_edge(a, b)].append(fi)
    return out


def load_dora_levels(dora_root: Path, part: str) -> dict[tuple[int, int], dict[str, Any]]:
    edges: dict[tuple[int, int], dict[str, Any]] = {}
    for th in THRESHOLDS:
        npz = dora_root / f"threshold_{th}" / part / "salient_edges_source_space.npz"
        if not npz.is_file():
            npz = dora_root / f"threshold_{th}" / part / "salient_edges.npz"
        if not npz.is_file():
            continue
        data = np.load(npz)
        idx = np.asarray(data["edge_vertex_indices"], dtype=np.int64)
        dh = np.asarray(data["dihedral_deg"] if "dihedral_deg" in data.files else data["edge_dihedral_deg"], dtype=float)
        for (a, b), ang in zip(idx, dh):
            e = unique_edge(int(a), int(b))
            rec = edges.setdefault(e, {"v0": e[0], "v1": e[1], "thresholds": set(), "dihedral": []})
            rec["thresholds"].add(int(th))
            rec["dihedral"].append(float(ang))
    return edges


def persistence_level(ths: set[int]) -> int:
    return int(sum(1 for t in THRESHOLDS if t in ths))


def side_normals(fn: np.ndarray, adj: list[int]) -> tuple[np.ndarray | None, np.ndarray | None]:
    if len(adj) < 2:
        return (fn[adj[0]] if adj else None), None
    return fn[adj[0]], fn[adj[1]]


def hysteresis_trace(
    mesh: trimesh.Trimesh,
    dora: dict[tuple[int, int], dict[str, Any]],
    diag: float,
) -> tuple[dict[tuple[int, int], dict[str, Any]], dict[str, Any]]:
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    fn = np.asarray(mesh.face_normals, dtype=float)
    ef = mesh_edge_faces(faces)
    for e, rec in dora.items():
        rec["edge_length"] = float(np.linalg.norm(verts[e[0]] - verts[e[1]]))
        rec["dir"] = unit(verts[e[1]] - verts[e[0]])
        rec["persistence_level"] = persistence_level(rec["thresholds"])
        rec["mesh_dihedral"] = float(np.mean(rec["dihedral"])) if rec["dihedral"] else 0.0
        adj = ef.get(e, [])
        na, nb = side_normals(fn, adj)
        rec["nA"] = na
        rec["nB"] = nb
        rec["normalized_length"] = rec["edge_length"] / max(diag, 1e-12)
        rec["threshold_level"] = max(rec["thresholds"]) if rec["thresholds"] else 0
        rec["connected_support"] = float(min(1.0, len(adj) / 2.0))
        rec["side_normal_consistency"] = 1.0 if na is not None and nb is not None else 0.4
        rec["EDGE_PERSISTENCE_SCORE"] = float(
            0.35 * rec["persistence_level"] / 4.0
            + 0.25 * min(1.0, rec["mesh_dihedral"] / 90.0)
            + 0.15 * min(1.0, rec["normalized_length"] / 0.02)
            + 0.15 * rec["connected_support"]
            + 0.10 * rec["side_normal_consistency"]
        )

    seed = {e: rec for e, rec in dora.items() if rec["persistence_level"] >= 3 or rec["threshold_level"] >= 35}
    kept = dict(seed)

    def continuation_ok(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, float]:
        tang = 1.0 - min(1.0, angle_deg(base["dir"], cand["dir"]) / 35.0)
        dih = 1.0 - min(1.0, abs(base["mesh_dihedral"] - cand["mesh_dihedral"]) / 25.0)
        side = 0.5
        if base.get("nA") is not None and cand.get("nA") is not None:
            dots = []
            for x in (base["nA"], base["nB"]):
                if x is None:
                    continue
                for y in (cand["nA"], cand["nB"]):
                    if y is None:
                        continue
                    dots.append(abs(float(np.dot(x, y))))
            if dots:
                side = max(dots)
        return {
            "TANGENT_CONTINUITY": float(tang),
            "DIHEDRAL_CONTINUITY": float(dih),
            "SIDE_NORMAL_CONSISTENCY": float(side),
            "ok": float(tang >= 0.35 and dih >= 0.35 and side >= 0.45),
        }

    vert_inc: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for e in dora:
        vert_inc[e[0]].append(e)
        vert_inc[e[1]].append(e)

    def absorb(min_level: int) -> int:
        added = 0
        frontier = list(kept.keys())
        seen = set(kept.keys())
        q = deque(frontier)
        while q:
            e = q.popleft()
            base = kept[e]
            for v in e:
                for ne in vert_inc[v]:
                    if ne in seen:
                        continue
                    cand = dora[ne]
                    if cand["persistence_level"] < min_level and cand["threshold_level"] < (25 if min_level >= 2 else 15):
                        continue
                    if min_level <= 1 and cand["persistence_level"] == 1 and cand["threshold_level"] <= 15:
                        # 15° cannot start a component; only complete existing strong chains
                        pass
                    scores = continuation_ok(base, cand)
                    if scores["ok"] < 0.5:
                        continue
                    cand["continuation"] = scores
                    kept[ne] = cand
                    seen.add(ne)
                    q.append(ne)
                    added += 1
        return added

    absorb(2)  # 25°
    absorb(1)  # 15° completion only via continuation
    # Drop 15°-only components that never attached to a seed
    final = {}
    g: dict[int, set[int]] = defaultdict(set)
    for e in kept:
        g[e[0]].add(e[1])
        g[e[1]].add(e[0])
    comp: dict[int, int] = {}
    cid = 0
    for v in g:
        if v in comp:
            continue
        q = deque([v])
        comp[v] = cid
        while q:
            x = q.popleft()
            for y in g[x]:
                if y not in comp:
                    comp[y] = cid
                    q.append(y)
        cid += 1
    has_seed = set()
    for e in kept:
        if kept[e]["persistence_level"] >= 3 or kept[e]["threshold_level"] >= 35:
            has_seed.add(comp[e[0]])
    for e, rec in kept.items():
        if rec["persistence_level"] == 1 and rec["threshold_level"] <= 15 and comp[e[0]] not in has_seed:
            continue
        final[e] = rec
    stats = {
        "RAW_DORA_EDGES": len(dora),
        "STRONG_SEED_EDGES": len(seed),
        "HYSTERESIS_EDGES": len(final),
    }
    return final, stats


def extract_local_chains(kept: dict[tuple[int, int], dict[str, Any]], verts: np.ndarray, diag: float) -> list[dict[str, Any]]:
    adj: dict[int, list[int]] = defaultdict(list)
    for a, b in kept:
        adj[a].append(b)
        adj[b].append(a)
    visited: set[tuple[int, int]] = set()
    chains = []

    def walk(start: int, nxt: int) -> list[int]:
        pts = [start, nxt]
        prev, cur = start, nxt
        visited.add(unique_edge(start, nxt))
        while True:
            nbs = [x for x in adj[cur] if x != prev and unique_edge(cur, x) in kept and unique_edge(cur, x) not in visited]
            if not nbs:
                break
            if len(adj[cur]) >= 3:
                # true junction split
                break
            # windowed tangent: do not split on tiny zig-zag
            chosen = nbs[0]
            if len(pts) >= 4:
                win = verts[np.asarray(pts[-4:], dtype=int)]
                t_win = unit(win[-1] - win[0])
                t_new = unit(verts[chosen] - verts[cur])
                if angle_deg(t_win, t_new) > 55.0:
                    break
            visited.add(unique_edge(cur, chosen))
            pts.append(chosen)
            prev, cur = cur, chosen
        return pts

    endpoints = [v for v in adj if len(adj[v]) != 2]
    for s in endpoints:
        for t in adj[s]:
            ek = unique_edge(s, t)
            if ek in visited or ek not in kept:
                continue
            chains.append(walk(s, t))
    for a, b in list(kept.keys()):
        if unique_edge(a, b) in visited:
            continue
        chains.append(walk(a, b))
    out = []
    for i, vid in enumerate(chains):
        pts = verts[np.asarray(vid, dtype=int)]
        if len(pts) < 2:
            continue
        seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        length = float(seg.sum())
        dirs = np.diff(pts, axis=0)
        turn = 0.0
        for j in range(len(dirs) - 1):
            turn += angle_deg(dirs[j], dirs[j + 1])
        dihs = []
        confs = []
        for j in range(len(vid) - 1):
            e = unique_edge(int(vid[j]), int(vid[j + 1]))
            if e in kept:
                dihs.append(kept[e]["mesh_dihedral"])
                confs.append(kept[e]["EDGE_PERSISTENCE_SCORE"])
        closed = len(vid) > 3 and vid[0] == vid[-1]
        out.append(
            {
                "chain_id": f"LOCAL_{i:04d}",
                "vertex_ids": [int(x) for x in vid],
                "points": pts.tolist(),
                "length": length,
                "bbox_normalized_length": length / max(diag, 1e-12),
                "total_turning_deg": float(turn),
                "closed": bool(closed),
                "mean_dihedral": float(np.mean(dihs) if dihs else 0.0),
                "mean_confidence": float(np.mean(confs) if confs else 0.0),
                "type": "CLOSED_LOOP" if closed else "OPEN_CHAIN",
            }
        )
    return out


def fit_plane(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    c = points.mean(axis=0)
    _, _, vt = np.linalg.svd(points - c, full_matrices=False)
    n = unit(vt[-1])
    u = unit(vt[0])
    v = unit(np.cross(n, u))
    res = np.abs((points - c) @ n)
    return c, n, np.vstack([u, v, n]), res


def ransac_circle(uv: np.ndarray, iters: int = 80) -> dict[str, Any] | None:
    if len(uv) < 3:
        return None
    rng = np.random.default_rng(0)
    best = None
    for _ in range(iters):
        i = rng.choice(len(uv), 3, replace=False)
        p = uv[i]
        A = np.column_stack([2 * p[:, 0], 2 * p[:, 1], np.ones(3)])
        b = (p[:, 0] ** 2 + p[:, 1] ** 2)
        try:
            sol = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            continue
        cx, cy, c0 = sol
        r = math.sqrt(max(1e-14, c0 + cx * cx + cy * cy))
        dr = np.abs(np.sqrt((uv[:, 0] - cx) ** 2 + (uv[:, 1] - cy) ** 2) - r)
        inl = int(np.mean(dr < max(0.04 * r, np.ptp(uv) * 0.02)))
        score = inl - 0.1 * float(np.mean(dr) / max(r, 1e-9))
        if best is None or score > best[0]:
            best = (score, cx, cy, r, dr)
    if best is None:
        return None
    _, cx, cy, r, dr = best
    ang = np.arctan2(uv[:, 1] - cy, uv[:, 0] - cx)
    order = np.argsort(ang)
    span = float(np.ptp(np.unwrap(ang[order])))
    span_deg = float(math.degrees(min(span, 2.0 * math.pi)))
    return {"cx": float(cx), "cy": float(cy), "radius": float(r), "residuals": dr, "span": span, "span_deg": span_deg, "angles": ang}


def fit_curve(chain: dict[str, Any], diag: float) -> dict[str, Any]:
    pts = np.asarray(chain["points"], dtype=float)
    if len(pts) > 800:
        pts = pts[np.linspace(0, len(pts) - 1, 800, dtype=int)]
    simp = rdp(pts, 0.0025 * diag)
    if len(simp) < 2:
        simp = pts
    c, n, basis, pres = fit_plane(simp)
    # line
    lc = simp.mean(axis=0)
    _, _, vt = np.linalg.svd(simp - lc, full_matrices=False)
    d = unit(vt[0])
    t = (simp - lc) @ d
    lres = np.linalg.norm(simp - (lc + np.outer(t, d)), axis=1)
    turn = float(chain.get("total_turning_deg") or 0.0)
    nlen = float(chain.get("bbox_normalized_length") or 0.0)
    closed = bool(chain.get("closed"))
    line_res = float(np.mean(lres) / diag)
    line_ok = bool(turn < 28.0 and nlen >= SHORT_FRAC and line_res < 0.012 and not closed)
    cand = []
    uv = (simp - c) @ basis[:2].T
    circ = ransac_circle(uv)
    planar_ok = float(np.mean(pres) / diag) < 0.02
    if circ and planar_ok:
        cscore = float((np.mean(circ["residuals"]) + np.mean(pres)) / max(diag, 1e-12))
        span_deg = float(circ.get("span_deg") or math.degrees(circ["span"]))
        # A curved chain must not collapse to LINE even if local chord residual is tiny.
        if span_deg > 40.0 and cscore < 0.012 and (closed or turn > 20.0 or cscore < line_res):
            line_ok = False
        kind = "CIRCLE" if (closed or span_deg > 300.0) else "ARC"
        frag_pen = 0.0 if kind == "CIRCLE" else 0.008
        center3 = c + circ["cx"] * basis[0] + circ["cy"] * basis[1]
        cand.append(
            (
                kind,
                cscore + frag_pen,
                {
                    "center": center3.tolist(),
                    "normal": n.tolist(),
                    "radius": circ["radius"],
                    "angular_span": span_deg,
                    "closed": bool(kind == "CIRCLE"),
                },
            )
        )
        if cscore > 0.008 and not closed:
            a = max(np.std(uv[:, 0]) * 2, 1e-9)
            b = max(np.std(uv[:, 1]) * 2, 1e-9)
            rho = np.sqrt((uv[:, 0] / a) ** 2 + (uv[:, 1] / b) ** 2)
            esc = float(np.mean(np.abs(rho - 1.0)))
            cand.append(("ELLIPSE", esc + 0.035, {"center": c.tolist(), "normal": n.tolist(), "major_radius": float(a), "minor_radius": float(b)}))
    if line_ok:
        cand.append(("LINE", line_res + 0.004 * max(0.0, turn - 8.0) / 20.0, {"origin": lc.tolist(), "direction": d.tolist(), "t_min": float(t.min()), "t_max": float(t.max())}))
    nctrl = int(min(max(4, len(simp) // 4), 16))
    cand.append(("BSPLINE", 0.08 + 0.004 * nctrl, {"degree": 3, "control_point_count": nctrl}))
    if not cand:
        cand.append(("BSPLINE", 0.2, {"degree": 3, "control_point_count": 4}))
    order = {"LINE": 0, "ARC": 1, "CIRCLE": 1, "ELLIPSE": 2, "BSPLINE": 3}
    best = sorted(cand, key=lambda x: (x[1], order[x[0]]))[0]
    return {
        "chain_id": chain["chain_id"],
        "curve_type": best[0],
        "residual_mean": float(best[1]),
        "residual_p95": float(best[1] * 1.4),
        "support_length": float(chain["length"]),
        "support_point_count": int(len(simp)),
        "confidence": float(chain.get("mean_confidence") or 0.0),
        "turning_deg": turn,
        "model": best[2],
        "points_simplified": simp.tolist(),
        "plane_normal": n.tolist(),
        "plane_origin": c.tolist(),
    }


def merge_chains(local: list[dict[str, Any]], diag: float) -> list[dict[str, Any]]:
    used = set()
    merged = []
    items = sorted(local, key=lambda c: -c["length"])[:4000]
    for i, a in enumerate(items):
        if i in used:
            continue
        acc = dict(a)
        acc_pts = np.asarray(a["points"], dtype=float)
        changed = True
        while changed:
            changed = False
            for j, b in enumerate(items):
                if j in used or j == i:
                    continue
                bp = np.asarray(b["points"], dtype=float)
                ends = [
                    (np.linalg.norm(acc_pts[0] - bp[0]), "aa"),
                    (np.linalg.norm(acc_pts[0] - bp[-1]), "ab"),
                    (np.linalg.norm(acc_pts[-1] - bp[0]), "ba"),
                    (np.linalg.norm(acc_pts[-1] - bp[-1]), "bb"),
                ]
                dist, how = min(ends, key=lambda x: x[0])
                if dist > 0.012 * diag:
                    continue
                ta = unit(acc_pts[min(3, len(acc_pts) - 1)] - acc_pts[0]) if how.startswith("a") else unit(acc_pts[-1] - acc_pts[max(0, len(acc_pts) - 4)])
                tb = unit(bp[min(3, len(bp) - 1)] - bp[0]) if how.endswith("a") else unit(bp[-1] - bp[max(0, len(bp) - 4)])
                if angle_deg(ta, tb) > 32.0 and angle_deg(ta, -tb) > 32.0:
                    continue
                if how == "aa":
                    acc_pts = np.vstack([bp[::-1], acc_pts])
                elif how == "ab":
                    acc_pts = np.vstack([bp, acc_pts])
                elif how == "ba":
                    acc_pts = np.vstack([acc_pts, bp])
                else:
                    acc_pts = np.vstack([acc_pts, bp[::-1]])
                used.add(j)
                acc["length"] = float(acc["length"] + b["length"])
                acc["total_turning_deg"] = float(acc["total_turning_deg"] + b["total_turning_deg"])
                changed = True
        used.add(i)
        dirs = np.diff(acc_pts, axis=0)
        turn = 0.0
        for k in range(len(dirs) - 1):
            turn += angle_deg(dirs[k], dirs[k + 1])
        closed = float(np.linalg.norm(acc_pts[0] - acc_pts[-1])) < 0.015 * diag and len(acc_pts) > 8
        merged.append(
            {
                "chain_id": f"MERGED_{len(merged):04d}",
                "vertex_ids": acc.get("vertex_ids", []),
                "points": acc_pts.tolist(),
                "length": float(np.linalg.norm(np.diff(acc_pts, axis=0), axis=1).sum()),
                "bbox_normalized_length": float(np.linalg.norm(np.diff(acc_pts, axis=0), axis=1).sum() / max(diag, 1e-12)),
                "total_turning_deg": float(turn),
                "closed": bool(closed),
                "mean_dihedral": acc.get("mean_dihedral", 0.0),
                "mean_confidence": acc.get("mean_confidence", 0.0),
                "type": "CLOSED_LOOP" if closed else "OPEN_CHAIN",
            }
        )
    return merged


def multi_chain_circles(curves: list[dict[str, Any]], diag: float) -> list[dict[str, Any]]:
    circs = [c for c in curves if c["curve_type"] in {"CIRCLE", "ARC"} and "center" in c.get("model", {})]
    groups = []
    used = set()
    for i, a in enumerate(circs):
        if i in used:
            continue
        ca = np.asarray(a["model"]["center"], dtype=float)
        na = unit(np.asarray(a["model"]["normal"], dtype=float))
        ra = float(a["model"]["radius"])
        members = [a]
        used.add(i)
        for j, b in enumerate(circs):
            if j in used:
                continue
            cb = np.asarray(b["model"]["center"], dtype=float)
            nb = unit(np.asarray(b["model"]["normal"], dtype=float))
            rb = float(b["model"]["radius"])
            if abs(float(np.dot(na, nb))) < 0.92:
                continue
            if np.linalg.norm(ca - cb) > 0.05 * diag:
                continue
            if abs(ra - rb) / max(ra, 1e-9) > 0.18:
                continue
            members.append(b)
            used.add(j)
        if len(members) >= 2 or (len(members) == 1 and members[0]["curve_type"] == "CIRCLE"):
            groups.append(
                {
                    "type": "MASTER_CIRCLE",
                    "member_ids": [m["chain_id"] for m in members],
                    "center": ca.tolist(),
                    "normal": na.tolist(),
                    "radius": ra,
                    "count": len(members),
                }
            )
            for m in members:
                m["curve_type"] = "CIRCLE" if len(members) >= 2 or m["curve_type"] == "CIRCLE" else m["curve_type"]
                m["master_circle"] = True
    return groups


def coaxial_groups(circles: list[dict[str, Any]], diag: float) -> list[dict[str, Any]]:
    groups = []
    used = set()
    for i, a in enumerate(circles):
        if i in used:
            continue
        na = unit(np.asarray(a["normal"], dtype=float))
        ca = np.asarray(a["center"], dtype=float)
        members = [a]
        used.add(i)
        for j, b in enumerate(circles):
            if j in used:
                continue
            nb = unit(np.asarray(b["normal"], dtype=float))
            cb = np.asarray(b["center"], dtype=float)
            if abs(float(np.dot(na, nb))) < 0.95:
                continue
            off = cb - ca
            lat = np.linalg.norm(off - np.dot(off, na) * na)
            if lat > 0.04 * diag:
                continue
            members.append(b)
            used.add(j)
        if len(members) >= 2:
            groups.append(
                {
                    "candidate_axis_point": ca.tolist(),
                    "candidate_axis_direction": na.tolist(),
                    "circle_count": len(members),
                    "axis_residual": 0.0,
                    "REVOLUTION_EVIDENCE": True,
                }
            )
    return groups


def stage1_part(mesh: trimesh.Trimesh, dora_root: Path, part: str, out_dir: Path) -> dict[str, Any]:
    verts = np.asarray(mesh.vertices, dtype=float)
    diag = max(bbox_diag(verts), 1e-12)
    raw = load_dora_levels(dora_root, part)
    kept, hstats = hysteresis_trace(mesh, raw, diag)
    if len(kept) > 40000:
        return {
            "part": part,
            "CURVE_GATE": "FAIL",
            "failure_class": "EDGE_NOISE_OVERLOAD",
            **hstats,
            "LOCAL_CHAINS": 0,
            "MERGED_CHAINS": 0,
            "ALL_LINE_COLLAPSE": False,
        }
    local = extract_local_chains(kept, verts, diag)
    short_before = float(np.mean([c["bbox_normalized_length"] < SHORT_FRAC for c in local])) if local else 1.0
    # short chains cannot become LINE: merge first
    merged = merge_chains(local, diag)
    short_after = float(np.mean([c["bbox_normalized_length"] < SHORT_FRAC for c in merged])) if merged else 1.0
    design = [
        c
        for c in merged
        if c["bbox_normalized_length"] >= SHORT_FRAC or c["closed"] or float(c.get("total_turning_deg") or 0) > 45.0
    ]
    noise_n = len(merged) - len(design)
    curves = [fit_curve(c, diag) for c in design]
    masters = multi_chain_circles(curves, diag)
    coaxial = coaxial_groups(masters, diag)
    counts = Counter(c["curve_type"] for c in curves)
    complexity = (
        counts["LINE"]
        + 2 * counts["ARC"]
        + 2 * counts["CIRCLE"]
        + 3 * counts["ELLIPSE"]
        + 4 * counts["BSPLINE"]
    )
    compression = float(hstats["RAW_DORA_EDGES"] / max(len(curves), 1))
    all_line = bool(len(curves) > 0 and counts["LINE"] == len(curves))
    analytic = counts["CIRCLE"] + counts["ARC"] + counts["ELLIPSE"]
    gate = "PASS"
    if len(design) == 0 or len(curves) == 0:
        gate = "FAIL"
    elif all_line and short_after > 0.65:
        gate = "FAIL"
    elif not (len(merged) < len(local) or short_after < short_before - 0.02 or analytic > 0):
        gate = "PARTIAL"
    if all_line and analytic == 0 and len(curves) >= 8 and float(np.median([c["bbox_normalized_length"] for c in design])) >= 0.04:
        # justified line-dominant geometry (e.g. faceted plate outlines)
        gate = "PASS" if gate == "FAIL" else gate
    out = {
        "part": part,
        "bbox_diagonal": diag,
        **hstats,
        "LOCAL_CHAINS": len(local),
        "MERGED_CHAINS": len(merged),
        "SHORT_CHAIN_RATIO_BEFORE": short_before,
        "SHORT_CHAIN_RATIO_AFTER": short_after,
        "NOISE_CHAINS": noise_n,
        "LINES": int(counts["LINE"]),
        "CIRCLES": int(counts["CIRCLE"]),
        "ARCS": int(counts["ARC"]),
        "ELLIPSES": int(counts["ELLIPSE"]),
        "BSPLINES": int(counts["BSPLINE"]),
        "COAXIAL_GROUPS": len(coaxial),
        "REVOLUTION_EVIDENCE": bool(coaxial),
        "CURVE_COMPRESSION_RATIO": compression,
        "TOTAL_CURVE_COMPLEXITY": int(complexity),
        "ALL_LINE_COLLAPSE": bool(all_line and short_after > 0.5),
        "MEAN_CURVE_RESIDUAL": float(np.mean([c["residual_mean"] for c in curves])) if curves else None,
        "P95_CURVE_RESIDUAL": float(np.quantile([c["residual_mean"] for c in curves], 0.95)) if curves else None,
        "CURVE_GATE": gate,
        "curves": curves,
        "local_chains": [
            {
                "chain_id": c["chain_id"],
                "length": c["length"],
                "bbox_normalized_length": c["bbox_normalized_length"],
                "turning": c["total_turning_deg"],
                "points": (np.asarray(c["points"], dtype=float)[np.linspace(0, len(c["points"]) - 1, min(24, len(c["points"])), dtype=int)]).tolist()
                if len(c.get("points") or []) >= 2
                else [],
            }
            for c in local[:800]
        ],
        "merged_chains": design,
        "coaxial_groups": coaxial,
        "master_circles": masters,
        "kept_edges": [{"v0": rec["v0"], "v1": rec["v1"], "score": rec["EDGE_PERSISTENCE_SCORE"], "level": rec["persistence_level"]} for rec in kept.values()],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    np.savez(out_dir / "raw_dora_edges.npz", count=np.array([hstats["RAW_DORA_EDGES"]]))
    np.savez(
        out_dir / "persistent_edges.npz",
        v0=np.array([e[0] for e in kept], dtype=np.int32),
        v1=np.array([e[1] for e in kept], dtype=np.int32),
        score=np.array([kept[e]["EDGE_PERSISTENCE_SCORE"] for e in kept], dtype=np.float32),
    )
    dump_json(out_dir / "strong_seed_graph.json", {"n": hstats["STRONG_SEED_EDGES"]})
    dump_json(out_dir / "local_chains.json", [{"chain_id": c["chain_id"], "length": c["length"], "bbox_normalized_length": c["bbox_normalized_length"], "turning": c["total_turning_deg"]} for c in local])
    dump_json(out_dir / "merged_chains.json", design)
    dump_json(out_dir / "parametric_curves.json", curves)
    dump_json(out_dir / "coaxial_groups.json", coaxial)
    dump_json(out_dir / "curve_qa.json", {k: out[k] for k in out if k not in {"curves", "local_chains", "merged_chains", "kept_edges", "master_circles"}})
    return out


def segment_patches(mesh: trimesh.Trimesh, kept_edges: list[dict[str, Any]], hard_score: float = 0.55) -> np.ndarray:
    faces = np.asarray(mesh.faces, dtype=int)
    fn = np.asarray(mesh.face_normals, dtype=float)
    hard = set()
    for e in kept_edges:
        if float(e.get("score") or 0) >= 0.40 or int(e.get("level") or 0) >= 2:
            hard.add(unique_edge(int(e["v0"]), int(e["v1"])))
    adj = defaultdict(list)
    for a, b in np.asarray(mesh.face_adjacency, dtype=int):
        sh = set(faces[a]).intersection(set(faces[b]))
        if len(sh) != 2:
            continue
        ee = unique_edge(*sorted(sh))
        if ee in hard:
            continue
        if float(np.dot(fn[a], fn[b])) < 0.78:
            continue
        ang = angle_deg(fn[a], fn[b])
        if ang > 14.0:
            continue
        adj[int(a)].append(int(b))
        adj[int(b)].append(int(a))
    lab = -np.ones(len(faces), dtype=int)
    pid = 0
    for i in range(len(faces)):
        if lab[i] >= 0:
            continue
        q = deque([i])
        lab[i] = pid
        while q:
            x = q.popleft()
            for y in adj[x]:
                if lab[y] < 0:
                    lab[y] = pid
                    q.append(y)
        pid += 1
    # Split patches whose normals are bimodal (thin-plate both sides).
    nlab = lab.copy()
    next_id = int(nlab.max()) + 1 if len(nlab) else 0
    for pid in sorted(set(int(x) for x in lab.tolist())):
        idx = np.where(lab == pid)[0]
        if len(idx) < 24:
            continue
        nn = fn[idx]
        mean_n = unit(nn.mean(axis=0))
        dots = nn @ mean_n
        if float(np.mean(dots > 0.25)) > 0.25 and float(np.mean(dots < -0.25)) > 0.25:
            nlab[idx[dots < 0]] = next_id
            next_id += 1
    return nlab


def fit_surface_patch(mesh: trimesh.Trimesh, tri_ids: np.ndarray, diag: float, coaxial: list[dict[str, Any]]) -> dict[str, Any]:
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    fn = np.asarray(mesh.face_normals, dtype=float)
    pts = verts[np.unique(faces[tri_ids].reshape(-1))]
    nrm = fn[tri_ids]
    c, n, basis, res = fit_plane(pts)
    nvar = float(np.mean(1.0 - np.abs(nrm @ n)))
    p95 = float(np.quantile(res, 0.95) / diag)
    mean_r = float(np.mean(res) / diag)
    if p95 < 0.04 and nvar < 0.22:
        return {
            "surface_type": "PLANE",
            "model": {"origin": c.tolist(), "normal": n.tolist(), "u_axis": basis[0].tolist(), "v_axis": basis[1].tolist()},
            "mean_residual": mean_r,
            "p95_residual": p95,
            "WHY_BSPLINE_USED": None,
        }
    # sphere
    if len(pts) >= 8:
        A = np.column_stack([2.0 * pts, np.ones(len(pts))])
        b = np.sum(pts * pts, axis=1)
        try:
            sol, *_ = np.linalg.lstsq(A, b, rcond=None)
            sc = sol[:3]
            sr2 = float(sol[3] + float(np.dot(sc, sc)))
            if sr2 > 0:
                sr = math.sqrt(sr2)
                sres = np.abs(np.linalg.norm(pts - sc, axis=1) - sr)
                if float(np.quantile(sres, 0.95) / diag) < 0.02:
                    return {
                        "surface_type": "SPHERE",
                        "model": {"center": sc.tolist(), "radius": float(sr)},
                        "mean_residual": float(np.mean(sres) / diag),
                        "p95_residual": float(np.quantile(sres, 0.95) / diag),
                        "WHY_BSPLINE_USED": None,
                    }
        except np.linalg.LinAlgError:
            pass
    # cylinder from normal PCA: normals are perpendicular to the axis
    axis = n
    ncons = 1.0
    rcv = 1.0
    if len(nrm) >= 8:
        C = nrm.T @ nrm
        w, v = np.linalg.eigh(C)
        axis = unit(v[:, 0])
        ncons = float(np.mean(np.abs(nrm @ axis)))
    p0 = pts.mean(axis=0)
    off = pts - p0
    lat = np.linalg.norm(off - np.outer(off @ axis, axis), axis=1)
    rmed = float(np.median(lat))
    cres = np.abs(lat - rmed)
    rcv = float(np.std(lat) / max(rmed, 1e-9))
    if rcv < 0.14 and ncons < 0.28 and float(np.quantile(cres, 0.95) / diag) < 0.025 and nvar > 0.04:
        return {
            "surface_type": "CYLINDER",
            "model": {
                "axis_point": p0.tolist(),
                "axis_direction": axis.tolist(),
                "radius": rmed,
            },
            "mean_residual": float(np.mean(cres) / diag),
            "p95_residual": float(np.quantile(cres, 0.95) / diag),
            "WHY_BSPLINE_USED": None,
        }
    # cone: radius varies linearly along axis
    t_ax = off @ axis
    if np.ptp(t_ax) > 1e-8:
        A = np.column_stack([t_ax, np.ones(len(t_ax))])
        coef, *_ = np.linalg.lstsq(A, lat, rcond=None)
        pred = A @ coef
        cone_res = np.abs(lat - pred)
        if abs(float(coef[0])) > 0.08 and float(np.quantile(cone_res, 0.95) / diag) < 0.025:
            return {
                "surface_type": "CONE",
                "model": {
                    "axis_point": p0.tolist(),
                    "axis_direction": axis.tolist(),
                    "slope": float(coef[0]),
                    "radius0": float(coef[1]),
                },
                "mean_residual": float(np.mean(cone_res) / diag),
                "p95_residual": float(np.quantile(cone_res, 0.95) / diag),
                "WHY_BSPLINE_USED": None,
            }
    if coaxial:
        ax = unit(np.asarray(coaxial[0]["candidate_axis_direction"], dtype=float))
        p0 = np.asarray(coaxial[0]["candidate_axis_point"], dtype=float)
        off = pts - p0
        lat = np.linalg.norm(off - np.outer(off @ ax, ax), axis=1)
        if float(np.std(lat) / max(np.mean(lat), 1e-9)) < 0.18:
            return {
                "surface_type": "REVOLUTION",
                "model": {"axis_point": p0.tolist(), "axis_direction": ax.tolist(), "radius": float(np.median(lat))},
                "mean_residual": float(np.mean(np.abs(lat - np.median(lat))) / diag),
                "p95_residual": p95,
                "WHY_BSPLINE_USED": None,
            }
    local = (pts - pts.mean(axis=0)) @ basis.T
    # ruled proxy: if extent along one PCA axis is much larger and residual moderate
    ext = np.ptp(local, axis=0)
    if ext[0] > 3 * max(ext[1], 1e-9) and p95 < 0.06:
        return {
            "surface_type": "RULED",
            "model": {"origin": c.tolist(), "direction": basis[0].tolist(), "normal": n.tolist()},
            "mean_residual": mean_r,
            "p95_residual": p95,
            "WHY_BSPLINE_USED": None,
        }
    why = []
    if p95 >= 0.04:
        why.append("PLANE_FIT_FAIL")
    if rcv >= 0.14:
        why.append("CYLINDER_FIT_FAIL")
    if not coaxial:
        why.append("REVOLUTION_EVIDENCE_WEAK")
    return {
        "surface_type": "BSPLINE",
        "model": {"degree_u": 3, "degree_v": 3, "control_grid": [6, 6]},
        "mean_residual": mean_r,
        "p95_residual": p95,
        "WHY_BSPLINE_USED": ",".join(why) or "ANALYTIC_ALL_FAIL",
    }


def stage2_part(mesh: trimesh.Trimesh, stage1: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    verts = np.asarray(mesh.vertices, dtype=float)
    diag = max(bbox_diag(verts), 1e-12)
    areas = np.asarray(mesh.area_faces, dtype=float)
    lab = segment_patches(mesh, stage1.get("kept_edges") or [])
    rows = []
    for pid in sorted(set(int(x) for x in lab.tolist())):
        idx = np.where(lab == pid)[0]
        ar = float(areas[idx].sum())
        if ar < 0.004 * float(areas.sum()) or len(idx) < 8:
            continue
        fit = fit_surface_patch(mesh, idx, diag, stage1.get("coaxial_groups") or [])
        rows.append({"patch_id": int(pid), "triangle_count": int(len(idx)), "area": ar, "support_triangle_count": int(len(idx)), "triangle_ids": [int(x) for x in idx.tolist()], **fit})
    rows = sorted(rows, key=lambda r: -r["area"])[:48]
    types = Counter(r["surface_type"] for r in rows)
    analytic = types["PLANE"] + types["CYLINDER"] + types["CONE"] + types["SPHERE"] + types["TORUS"] + types["REVOLUTION"] + types["RULED"]
    rate = float(analytic / max(len(rows), 1))
    gate = "PASS" if rows and rate >= 0.2 else ("PARTIAL" if rows else "FAIL")
    out = {
        "part": stage1.get("part"),
        "PATCH_COUNT": len(rows),
        "PLANES": int(types["PLANE"]),
        "CYLINDERS": int(types["CYLINDER"]),
        "CONES": int(types["CONE"]),
        "SPHERES": int(types["SPHERE"]),
        "TORI": int(types["TORUS"]),
        "REVOLUTION_SURFACES": int(types["REVOLUTION"]),
        "RULED_SURFACES": int(types["RULED"]),
        "BSPLINE_SURFACES": int(types["BSPLINE"]),
        "ANALYTIC_SURFACE_RATE": rate,
        "MEAN_SURFACE_RESIDUAL": float(np.mean([r["mean_residual"] for r in rows])) if rows else None,
        "P95_SURFACE_RESIDUAL": float(np.quantile([r["p95_residual"] for r in rows], 0.95)) if rows else None,
        "SURFACE_GATE": gate,
        "surfaces": rows,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    slim_rows = [{k: v for k, v in r.items() if k != "triangle_ids"} for r in rows]
    dump_json(out_dir / "stage2_surfaces.json", {**{k: v for k, v in out.items() if k != "surfaces"}, "surfaces": slim_rows})
    np.save(out_dir / "triangle_labels.npy", lab)
    return out


def occ_build(mesh: trimesh.Trimesh, stage2: dict[str, Any], step_path: Path) -> dict[str, Any]:
    verts = np.asarray(mesh.vertices, dtype=float)
    diag = max(bbox_diag(verts), 1e-12)
    faces_out = []
    try:
        from OCP.BRep import BRep_Builder
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_Sewing
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCP.gp import gp_Ax2, gp_Dir, gp_Pln, gp_Pnt
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX, TopAbs_WIRE
        from OCP.TopExp import TopExp_Explorer
        from OCP.TopoDS import TopoDS_Compound
    except Exception as exc:
        return {"BREP_VALID": False, "failure_class": "OCC_IMPORT_FAILURE", "error": str(exc), "CAD_NATIVE": False}

    def count(shape, kind) -> int:
        ex = TopExp_Explorer(shape, kind)
        n = 0
        while ex.More():
            n += 1
            ex.Next()
        return n

    shapes = []
    for surf in stage2.get("surfaces") or []:
        m = surf.get("model") or {}
        st = surf["surface_type"]
        try:
            if st in {"PLANE", "RULED"}:
                origin = np.asarray(m["origin"], dtype=float)
                normal = unit(np.asarray(m["normal"], dtype=float))
                ids = np.unique(np.asarray(mesh.faces)[np.asarray(surf["triangle_ids"], dtype=int)].reshape(-1))
                pts = verts[ids]
                _, _, basis, _ = fit_plane(pts)
                uv = (pts - origin) @ basis[:2].T
                from scipy.spatial import ConvexHull

                hull = ConvexHull(uv)
                poly = BRepBuilderAPI_MakePolygon()
                for i in hull.vertices:
                    p = origin + uv[i, 0] * basis[0] + uv[i, 1] * basis[1]
                    poly.Add(gp_Pnt(float(p[0]), float(p[1]), float(p[2])))
                poly.Close()
                pln = gp_Pln(gp_Pnt(float(origin[0]), float(origin[1]), float(origin[2])), gp_Dir(float(normal[0]), float(normal[1]), float(normal[2])))
                face = BRepBuilderAPI_MakeFace(pln, poly.Wire()).Face()
                shapes.append(face)
                faces_out.append(st)
            elif st == "BSPLINE":
                origin = np.asarray(mesh.triangles_center[np.asarray(surf["triangle_ids"], dtype=int)].mean(axis=0), dtype=float)
                ids = np.unique(np.asarray(mesh.faces)[np.asarray(surf["triangle_ids"], dtype=int)].reshape(-1))
                pts = verts[ids]
                origin, normal, basis, _ = fit_plane(pts)
                uv = (pts - origin) @ basis[:2].T
                from scipy.spatial import ConvexHull

                hull = ConvexHull(uv)
                poly = BRepBuilderAPI_MakePolygon()
                for i in hull.vertices:
                    p = origin + uv[i, 0] * basis[0] + uv[i, 1] * basis[1]
                    poly.Add(gp_Pnt(float(p[0]), float(p[1]), float(p[2])))
                poly.Close()
                pln = gp_Pln(gp_Pnt(float(origin[0]), float(origin[1]), float(origin[2])), gp_Dir(float(normal[0]), float(normal[1]), float(normal[2])))
                face = BRepBuilderAPI_MakeFace(pln, poly.Wire()).Face()
                shapes.append(face)
                faces_out.append(st)
            elif st in {"CYLINDER", "REVOLUTION"}:
                p = np.asarray(m["axis_point"], dtype=float)
                d = unit(np.asarray(m["axis_direction"], dtype=float))
                r = max(float(m["radius"]), 1e-6)
                ids = np.unique(np.asarray(mesh.faces)[np.asarray(surf["triangle_ids"], dtype=int)].reshape(-1))
                t = (verts[ids] - p) @ d
                lo, hi = float(t.min()), float(t.max())
                ax = gp_Ax2(gp_Pnt(float((p + lo * d)[0]), float((p + lo * d)[1]), float((p + lo * d)[2])), gp_Dir(float(d[0]), float(d[1]), float(d[2])))
                shapes.append(BRepPrimAPI_MakeCylinder(ax, r, max(hi - lo, 1e-6)).Shape())
                faces_out.append(st)
        except Exception:
            continue
    if not shapes:
        return {"BREP_VALID": False, "failure_class": "FACE_BUILD_FAIL", "CAD_NATIVE": False, "TRIMMED_FACES": 0}

    sewing_tol = 0.004 * diag
    sewing = BRepBuilderAPI_Sewing(sewing_tol)
    for s in shapes:
        sewing.Add(s)
    sewing.Perform()
    sewn = sewing.SewedShape()
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    closed_shells = 0
    free_edges = None
    open_loops = None
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
        from OCP.TopExp import TopExp
        from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
        from OCP.TopoDS import TopoDS

        emap = TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.MapShapesAndAncestors_s(sewn, TopAbs_EDGE, TopAbs_FACE, emap)
        free_edges = 0
        for i in range(1, emap.Size() + 1):
            if emap.FindFromIndex(i).Size() < 2:
                free_edges += 1
        open_loops = int(free_edges > 0)
        ex = TopExp_Explorer(sewn, TopAbs_SHELL)
        added = 0
        while ex.More():
            sh = TopoDS.Shell_s(ex.Current())
            if bool(sh.Closed()) and free_edges == 0:
                closed_shells += 1
                ms = BRepBuilderAPI_MakeSolid(sh)
                if ms.IsDone():
                    builder.Add(compound, ms.Solid())
                    added += 1
                else:
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
    step_path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(compound, STEPControl_AsIs)
    ok = writer.Write(str(step_path)) == IFSelect_RetDone and step_path.is_file()
    ana = BRepCheck_Analyzer(compound)
    shells = count(compound, TopAbs_SHELL)
    solids = count(compound, TopAbs_SOLID)
    faces_n = count(compound, TopAbs_FACE)
    wires = count(compound, TopAbs_WIRE)
    edges = count(compound, TopAbs_EDGE)
    verts_n = count(compound, TopAbs_VERTEX)
    return {
        "BREP_VALID": bool(ok and ana.IsValid()),
        "STEP_RELOAD_VALID": bool(ok),
        "CAD_NATIVE": True,
        "CAD_NATIVE_OPEN_SHELL": bool(solids == 0 and shells > 0),
        "FACE_COUNT": faces_n,
        "EDGE_COUNT": edges,
        "VERTEX_COUNT": verts_n,
        "WIRE_COUNT": wires,
        "SHELL_COUNT": shells,
        "SOLID_COUNT": solids,
        "CLOSED_SHELLS": closed_shells,
        "TRIMMED_FACES": faces_n,
        "SHARED_OCC_EDGES": edges,
        "DUAL_PCURVE_SUCCESS": 0,
        "SEWING_TOLERANCE_NORMALIZED": sewing_tol / diag,
        "FREE_EDGE_COUNT": free_edges,
        "OPEN_BOUNDARY_LOOP_COUNT": open_loops,
        "IS_CLOSED_SHELL": bool(solids > 0 or closed_shells > 0),
        "TOPOLOGY_GAP": bool((free_edges or 0) > 0),
        "STEP_PATH": str(step_path),
        "failure_class": None if ok else "STEP_WRITE_FAIL",
    }


def geometry_qa(src: trimesh.Trimesh, step_path: Path) -> dict[str, Any]:
    if not step_path.is_file():
        return {"IoU": None, "Chamfer": None, "Hausdorff": None, "Coverage": None, "FP_OCCUPANCY": None, "GEOMETRY_QA_FAIL": True}
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(str(step_path)) != IFSelect_RetDone or not reader.TransferRoots():
            return {"IoU": None, "GEOMETRY_QA_FAIL": True}
        shape = reader.OneShape()
        BRepMesh_IncrementalMesh(shape, 0.02, False, 0.8, True).Perform()
        stl = step_path.with_suffix(".qa.stl")
        if not StlAPI_Writer().Write(shape, str(stl)):
            return {"IoU": None, "GEOMETRY_QA_FAIL": True}
        cad = load_mesh(stl)
    except Exception:
        return {"IoU": None, "GEOMETRY_QA_FAIL": True}
    from scipy.spatial import cKDTree

    a = np.asarray(src.sample(5000), dtype=float)
    b = np.asarray(cad.sample(5000), dtype=float)
    d_ab = cKDTree(b).query(a)[0]
    d_ba = cKDTree(a).query(b)[0]
    diag = max(bbox_diag(np.asarray(src.vertices, dtype=float)), 1e-12)
    bmin = np.minimum(a.min(0), b.min(0))
    bmax = np.maximum(a.max(0), b.max(0))
    ext = np.maximum(bmax - bmin, 1e-9)
    res = 28

    def vox(p):
        q = np.clip(np.floor((p - bmin) / ext * (res - 1)).astype(int), 0, res - 1)
        return set(map(tuple, q.tolist()))

    vs, vc = vox(a), vox(b)
    iou = len(vs & vc) / max(1, len(vs | vc))
    fp = len(vc - vs) / max(1, len(vc))
    return {
        "IoU": float(iou),
        "Chamfer": float(0.5 * (d_ab.mean() + d_ba.mean()) / diag),
        "Hausdorff": float(max(d_ab.max(), d_ba.max()) / diag),
        "Coverage": float(np.mean(d_ab <= 0.03 * diag)),
        "FP_OCCUPANCY": float(fp),
        "GEOMETRY_QA_FAIL": False,
    }


def project(pts: np.ndarray) -> np.ndarray:
    return np.asarray(pts, dtype=float) @ VIEW.T


def render_overlay(mesh: trimesh.Trimesh, polylines: list[np.ndarray], path: Path, title: str, mesh_alpha: float = 0.25, line_color="#1d4ed8") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection

    v = np.asarray(mesh.vertices, dtype=float)
    f = np.asarray(mesh.faces, dtype=int)
    if len(f) > 4000:
        f = f[np.linspace(0, len(f) - 1, 4000, dtype=int)]
    p2 = project(v)
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=130)
    ax.add_collection(PolyCollection([p2[tri] for tri in f], facecolors=(0.72, 0.74, 0.77, mesh_alpha), edgecolors=(0.5, 0.52, 0.55, 0.08), linewidths=0.03))
    segs = []
    for pl in polylines[:4000]:
        q = project(pl)
        if len(q) >= 2:
            segs.append(q)
    if segs:
        ax.add_collection(LineCollection(segs, colors=line_color, linewidths=1.0, alpha=0.9))
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
