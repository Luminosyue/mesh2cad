"""Fragment extraction and geometric features for V6A."""
from __future__ import annotations

import hashlib
import itertools
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4
import routeb_point2cad_wire_closure_v5 as v5


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def poly_len(pts: np.ndarray) -> float:
    if len(pts) < 2:
        return 0.0
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def endpoint_curvature(pts: np.ndarray, which: str, k: int = 6) -> float | None:
    if len(pts) < 4:
        return None
    k = min(k, len(pts) - 2)
    if which == "s":
        seg = pts[: k + 2]
    else:
        seg = pts[-(k + 2) :]
    if len(seg) < 3:
        return None
    tangents = np.diff(seg, axis=0)
    tangents = tangents / (np.linalg.norm(tangents, axis=1, keepdims=True) + 1e-12)
    angles = []
    for i in range(len(tangents) - 1):
        dot = float(np.clip(np.dot(tangents[i], tangents[i + 1]), -1.0, 1.0))
        angles.append(np.arccos(dot))
    return float(np.mean(angles)) if angles else None


def mesh_uv_frame(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pts = np.asarray(mesh.vertices, dtype=float)
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c, full_matrices=False)
    return c, vt[0], vt[1]


def project_uv(pts: np.ndarray, c: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    d = np.asarray(pts, dtype=float) - c
    return np.stack([d @ u, d @ v], axis=1)


def xpart_support_bridge(p0: np.ndarray, p1: np.ndarray, xpart: trimesh.Trimesh, diag: float, n: int = 12) -> dict:
    from scipy.spatial import cKDTree

    t = np.linspace(0.0, 1.0, n)
    bridge = np.asarray([p0 * (1 - ti) + p1 * ti for ti in t], dtype=float)
    xv = np.asarray(xpart.vertices, dtype=float)
    tree = cKDTree(xv)
    d = tree.query(bridge)[0]
    thr = 0.03 * diag
    return {
        "support_fraction": float(np.mean(d < thr)),
        "support_p95": float(np.percentile(d, 95)),
        "mean_dist": float(np.mean(d)),
    }


def extract_fragments(topo: dict, pair_map: dict, diag: float) -> list[dict]:
    curves = v5.extract_official_curves(topo, diag)
    id_map = {m["curve_id"]: (m["surface_a"], m["surface_b"]) for m in pair_map.get("mapping") or []}
    frags = []
    for c in curves:
        sa, sb = id_map.get(c["curve_id"], (None, None))
        if sa is None:
            continue
        for comp in c["components"]:
            pl = np.asarray(comp["points"], dtype=float)
            if comp.get("closed") and poly_len(pl) < 0.02 * diag:
                continue
            if (not comp.get("closed")) and poly_len(pl) < 0.004 * diag:
                continue
            fid = f"{c['curve_id']}_C{comp['comp_id']:02d}"
            frags.append(
                {
                    "fragment_id": fid,
                    "curve_id": c["curve_id"],
                    "comp_id": comp["comp_id"],
                    "surface_a": int(sa),
                    "surface_b": int(sb),
                    "surface_pair": (int(sa), int(sb)),
                    "points": pl,
                    "length": float(comp["length"]),
                    "closed": bool(comp.get("closed")),
                    "start_xyz": pl[0].tolist(),
                    "end_xyz": pl[-1].tolist(),
                    "start_tangent": v5.robust_tangent(pl, "s").tolist(),
                    "end_tangent": v5.robust_tangent(pl, "e").tolist(),
                    "start_curvature": endpoint_curvature(pl, "s"),
                    "end_curvature": endpoint_curvature(pl, "e"),
                    "bbox": [pl.min(0).tolist(), pl.max(0).tolist()],
                }
            )
    return frags


def attach_fragment_features(
    frags: list[dict],
    surfaces: list[trimesh.Trimesh],
    xpart: trimesh.Trimesh,
    diag: float,
) -> None:
    from scipy.spatial import cKDTree

    xv = np.asarray(xpart.vertices, dtype=float)
    xtree = cKDTree(xv)
    uv_frames = [mesh_uv_frame(s) for s in surfaces]
    for f in frags:
        pts = np.asarray(f["points"], dtype=float)
        d = xtree.query(pts[np.linspace(0, len(pts) - 1, min(32, len(pts)), dtype=int)])[0]
        f["distance_to_XPart"] = float(np.mean(d))
        f["support_fraction"] = float(np.mean(d < 0.03 * diag))
        sa, sb = f["surface_pair"]
        uv_a = project_uv(pts, *uv_frames[sa])
        uv_b = project_uv(pts, *uv_frames[sb])
        f["surface_A_uv"] = {"min": uv_a.min(0).tolist(), "max": uv_a.max(0).tolist(), "start": uv_a[0].tolist(), "end": uv_a[-1].tolist()}
        f["surface_B_uv"] = {"min": uv_b.min(0).tolist(), "max": uv_b.max(0).tolist(), "start": uv_b[0].tolist(), "end": uv_b[-1].tolist()}


def connection_oriented_tangent(fi: dict, fj: dict, ea: str, eb: str, reverse_b: bool) -> tuple[float, float]:
    ta = v5.leave_tangent(np.asarray(fi["points"]), ea)
    tb = v5.leave_tangent(np.asarray(fj["points"]), eb)
    if reverse_b:
        tb = -tb
    dot = float(np.dot(ta, -tb))
    angle = float(np.degrees(np.arccos(np.clip(abs(dot), -1.0, 1.0))))
    return dot, angle


GAP_CANDIDATES = [1e-4, 3e-4, 1e-3, 3e-3, 5e-3]


def connection_evidence_ok(rec: dict, gap_thr: float) -> bool:
    ng = rec["normalized_gap"]
    geom_close = ng <= gap_thr
    tangent_ok = rec["tangent_dot"] >= 0.65
    uv_ok = (rec["uv_ratio_A"] <= 0.35 and rec["uv_ratio_B"] <= 0.35) or ng <= 1e-3
    support_ok = rec["support_fraction"] >= 0.35 or ng <= 5e-4
    return bool(geom_close and tangent_ok and uv_ok and support_ok)


def select_gap_threshold(candidates: list[dict]) -> float:
    """Pick the smallest conservative normalized gap with at least one multi-evidence pass."""
    for thr in GAP_CANDIDATES:
        if any(connection_evidence_ok(c, thr) for c in candidates):
            return thr
    return 3e-3


def score_connection(fi: dict, fj: dict, ea: str, eb: str, surfaces: list[trimesh.Trimesh], xpart: trimesh.Trimesh, diag: float, gap_thr: float = 3e-3) -> dict:
    pa = np.asarray(fi["start_xyz"] if ea == "s" else fi["end_xyz"], dtype=float)
    pb = np.asarray(fj["start_xyz"] if eb == "s" else fj["end_xyz"], dtype=float)
    gap = float(np.linalg.norm(pa - pb))
    ng = gap / max(diag, 1e-12)
    d_fwd, ang_fwd = connection_oriented_tangent(fi, fj, ea, eb, False)
    d_rev, ang_rev = connection_oriented_tangent(fi, fj, ea, eb, True)
    reverse_b = d_rev > d_fwd
    tangent_dot = max(d_fwd, d_rev)
    tangent_angle = min(ang_fwd, ang_rev)
    sa, sb = fi["surface_pair"]
    uva_s = fi["surface_A_uv"]["start" if ea == "s" else "end"]
    uva_e = fi["surface_A_uv"]["end" if ea == "s" else "start"]
    uvb_s = fj["surface_A_uv"]["start" if eb == "s" else "end"]
    uva_b_s = fi["surface_B_uv"]["start" if ea == "s" else "end"]
    uvb_b_s = fj["surface_B_uv"]["start" if eb == "s" else "end"]
    uv_gap_a = float(np.linalg.norm(np.asarray(uva_s) - np.asarray(uvb_s)))
    uv_gap_b = float(np.linalg.norm(np.asarray(uva_b_s) - np.asarray(uvb_b_s)))
    ext_a = max(float(np.linalg.norm(np.asarray(fi["surface_A_uv"]["max"]) - np.asarray(fi["surface_A_uv"]["min"]))), 1e-9)
    ext_b = max(float(np.linalg.norm(np.asarray(fi["surface_B_uv"]["max"]) - np.asarray(fi["surface_B_uv"]["min"]))), 1e-9)
    uv_ratio_a = uv_gap_a / ext_a
    uv_ratio_b = uv_gap_b / ext_b
    bridge = xpart_support_bridge(pa, pb, xpart, diag)
    curv_i = fi["start_curvature"] if ea == "s" else fi["end_curvature"]
    curv_j = fj["start_curvature"] if eb == "s" else fj["end_curvature"]
    curv_diff = None if curv_i is None or curv_j is None else float(abs(curv_i - curv_j))
    accepted = connection_evidence_ok(
        {
            "normalized_gap": ng,
            "tangent_dot": tangent_dot,
            "uv_ratio_A": uv_ratio_a,
            "uv_ratio_B": uv_ratio_b,
            "support_fraction": bridge["support_fraction"],
        },
        gap_thr,
    )
    geom_close = ng <= gap_thr
    reason = []
    if not geom_close:
        reason.append("GAP_TOO_LARGE")
    if tangent_dot < 0.65:
        reason.append("TANGENT_DISCONTINUITY")
    if not ((uv_ratio_a <= 0.35 and uv_ratio_b <= 0.35) or ng <= 1e-3):
        reason.append("UV_DISCONTINUITY")
    if not (bridge["support_fraction"] >= 0.35 or ng <= 5e-4):
        reason.append("XPART_UNSUPPORTED")
    return {
        "fragment_i": fi["fragment_id"],
        "fragment_j": fj["fragment_id"],
        "endpoint_i": ea,
        "endpoint_j": eb,
        "endpoint_gap": gap,
        "normalized_gap": ng,
        "tangent_dot": tangent_dot,
        "tangent_angle_deg": tangent_angle,
        "reverse_b": reverse_b,
        "curvature_difference": curv_diff,
        "uv_gap_A": uv_gap_a,
        "uv_gap_B": uv_gap_b,
        "uv_ratio_A": uv_ratio_a,
        "uv_ratio_B": uv_ratio_b,
        "support_fraction": bridge["support_fraction"],
        "support_p95": bridge["support_p95"],
        "accepted": accepted,
        "reason_rejected": reason if not accepted else [],
        "cost": ng + 0.2 * (1.0 - tangent_dot) + 0.1 * max(uv_ratio_a, uv_ratio_b) + 0.2 * (1.0 - bridge["support_fraction"]),
    }


def histograms(candidates: list[dict]) -> dict:
    def hist(vals, bins=(1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 1.0)):
        out = {}
        arr = np.asarray(vals, float)
        for i in range(len(bins) - 1):
            out[f"{bins[i]:.0e}_{bins[i+1]:.0e}"] = int(np.sum((arr >= bins[i]) & (arr < bins[i + 1])))
        return out

    return {
        "endpoint_gap": hist([c["normalized_gap"] for c in candidates]),
        "tangent_angle": hist([c["tangent_angle_deg"] / 90.0 for c in candidates], (0, 0.2, 0.4, 0.6, 0.8, 1.01)),
        "uv_ratio": hist([max(c["uv_ratio_A"], c["uv_ratio_B"]) for c in candidates], (0, 0.1, 0.2, 0.35, 0.5, 1.01)),
        "support_fraction": hist([c["support_fraction"] for c in candidates], (0, 0.2, 0.35, 0.5, 0.75, 1.01)),
    }
