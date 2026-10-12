"""Geometry-to-CAD brief + light closed-feature circle candidates.

Input: cad_spatial_dataset/PART_xxx/{meta.json, features.npy, dora/sharp_edges.json}
Output: structured summary for LLM (not 8192 raw points).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _round(x: float, nd: int = 6) -> float:
    return float(round(float(x), nd))


def _unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def _plane_basis(axis: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    axis = _unit(axis)
    tmp = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, tmp)
    u = _unit(u)
    v = np.cross(axis, u)
    return u, v


def fit_circle_3d(pts: np.ndarray, axis_hint: np.ndarray | None = None) -> dict | None:
    """PCA plane + algebraic circle fit. Returns radius/center/confidence, not a wire."""
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) < 8:
        return None
    c0 = pts.mean(axis=0)
    centered = pts - c0
    cov = np.cov(centered.T)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)  # ascending: plane normal ≈ smallest variance
    evals = evals[order]
    evecs = evecs[:, order]
    normal = evecs[:, 0]
    if axis_hint is not None:
        ah = _unit(axis_hint)
        if abs(float(normal @ ah)) < 0.5:
            # prefer axis-aligned plane when PCA is ambiguous
            normal = ah
    normal = _unit(normal)
    planarity = float(1.0 - evals[0] / (evals.sum() + 1e-18))
    if planarity < 0.55:
        return None

    u, v = _plane_basis(normal)
    xy = np.stack([(pts - c0) @ u, (pts - c0) @ v], axis=1)
    x, y = xy[:, 0], xy[:, 1]
    A = np.stack([2 * x, 2 * y, np.ones_like(x)], axis=1)
    try:
        sol, *_ = np.linalg.lstsq(A, x * x + y * y, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cx, cy, c = sol
    r2 = float(c + cx * cx + cy * cy)
    if r2 <= 0:
        return None
    r = float(np.sqrt(r2))
    if r < 1e-8:
        return None
    resid = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    rmse = float(np.sqrt(np.mean((resid - r) ** 2)))
    circ = float(1.0 - min(rmse / r, 1.0))
    if circ < 0.80:
        return None
    center = c0 + cx * u + cy * v
    # angular coverage heuristic
    angles = np.arctan2(y - cy, x - cx)
    ang_sorted = np.sort(angles)
    gaps = np.diff(ang_sorted)
    wrap = float(ang_sorted[0] + 2 * np.pi - ang_sorted[-1])
    max_gap = float(max(gaps.max() if len(gaps) else 0.0, wrap))
    coverage = float(1.0 - max_gap / (2 * np.pi))
    confidence = float(np.clip(0.55 * circ + 0.35 * coverage + 0.10 * planarity, 0.0, 1.0))
    return {
        "type": "circle",
        "radius": _round(r),
        "center": [_round(x) for x in center.tolist()],
        "normal": [_round(x) for x in normal.tolist()],
        "circularity": _round(circ, 4),
        "coverage": _round(coverage, 4),
        "planarity": _round(planarity, 4),
        "n_points": int(len(pts)),
        "confidence": _round(confidence, 4),
    }


def _load_dora_edge_points(part_dir: Path) -> np.ndarray:
    """Flatten Dora sharp-edge polylines into points (still no wire construction)."""
    path = part_dir / "dora" / "sharp_edges.json"
    if not path.is_file():
        return np.zeros((0, 3), dtype=np.float64)
    data = _load_json(path)
    if not isinstance(data, list):
        return np.zeros((0, 3), dtype=np.float64)
    pts = []
    for ch in data:
        arr = np.asarray(ch.get("points") or [], dtype=np.float64)
        if len(arr):
            pts.append(arr)
    if not pts:
        return np.zeros((0, 3), dtype=np.float64)
    return np.vstack(pts)


def light_closed_feature_candidates(
    part_dir: Path,
    meta: dict,
    *,
    edge_score_thr: float = 0.3,
    eps_frac: float = 0.03,
    min_samples: int = 12,
) -> list[dict]:
    """edge points → DBSCAN → PCA plane → circle fit → radius candidates (no BRep wire)."""
    chunks: list[np.ndarray] = []
    dora_pts = _load_dora_edge_points(part_dir)
    if len(dora_pts):
        chunks.append(dora_pts)

    features_path = part_dir / "features.npy"
    if features_path.is_file():
        feats = np.load(features_path)
        pts = feats[:, :3].astype(np.float64)
        scores = feats[:, 6].astype(np.float64)
        keep = scores >= float(edge_score_thr)
        edge_pts = pts[keep]
        if len(edge_pts) < min_samples:
            k = min(max(min_samples * 3, 64), len(pts))
            idx = np.argsort(-scores)[:k]
            edge_pts = pts[idx]
        if len(edge_pts):
            chunks.append(edge_pts)

    if not chunks:
        return []
    edge_pts = np.vstack(chunks)

    diag = float(meta.get("bbox_diagonal") or np.linalg.norm(np.asarray(meta.get("bbox", [1, 1, 1]), dtype=float)))
    eps = max(eps_frac * diag, 1e-5)
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(edge_pts)

    axis = None
    surf = meta.get("surface_stats") or {}
    if surf.get("pca_axis"):
        axis = np.asarray(surf["pca_axis"], dtype=np.float64)

    cands: list[dict] = []
    for lab in sorted(set(labels.tolist())):
        if lab < 0:
            continue
        cluster = edge_pts[labels == lab]
        fit = fit_circle_3d(cluster, axis_hint=axis)
        if fit is None:
            continue
        fit["cluster_id"] = int(lab)
        fit["source"] = "edge_score_dbscan_circle"
        cands.append(fit)

    # also promote existing radius clusters from Dora meta as soft candidates
    for i, cl in enumerate((meta.get("edge_stats") or {}).get("radius_clusters") or []):
        r = float(cl.get("radius_mean", 0.0))
        if r <= 0:
            continue
        count = int(cl.get("count", 0))
        src = str(cl.get("source", "meta_radius_cluster"))
        conf = 0.9 if src == "polyline_circle_fit" and count >= 2 else (0.75 if count >= 20 else 0.55)
        # skip near-duplicates of DBSCAN fits
        if any(abs(r - c["radius"]) / max(c["radius"], 1e-8) < 0.06 for c in cands):
            continue
        cands.append(
            {
                "type": "circle",
                "radius": _round(r),
                "center": None,
                "normal": [_round(x) for x in (axis.tolist() if axis is not None else [0, 1, 0])],
                "circularity": None,
                "coverage": None,
                "planarity": None,
                "n_points": count,
                "confidence": _round(conf, 4),
                "cluster_id": -(i + 1),
                "source": f"meta:{src}",
                "height_mean": cl.get("height_mean"),
            }
        )

    cands.sort(key=lambda c: (-float(c.get("confidence", 0.0)), -float(c.get("radius", 0.0))))
    # drop tiny noise radii relative to the dominant candidate
    if cands:
        r_max = max(float(c["radius"]) for c in cands)
        cands = [c for c in cands if float(c["radius"]) >= 0.25 * r_max or c.get("source", "").startswith("meta:")]
    return cands[:12]


def infer_part_type(meta: dict) -> str:
    surf = meta.get("surface_stats") or {}
    edge = meta.get("edge_stats") or {}
    likely = surf.get("likely_class", "mixed")
    rings = int(edge.get("circular_ring_count", 0))
    groups = int(edge.get("concentric_radius_groups", 0))
    if likely == "cylindrical" and (rings >= 1 or groups >= 1):
        return "mechanical wheel / cylindrical component"
    if likely == "planar":
        return "mechanical planar / plate component"
    if rings >= 3:
        return "mechanical ringed / revolved component"
    return "mechanical CAD component"


def detect_features(meta: dict, closed: list[dict]) -> list[str]:
    """Human-readable feature list. Do NOT invent holes when rings are weak."""
    surf = meta.get("surface_stats") or {}
    edge = meta.get("edge_stats") or {}
    feats: list[str] = []
    likely = surf.get("likely_class", "mixed")
    rings = int(edge.get("circular_ring_count", 0))
    groups = int(edge.get("concentric_radius_groups", 0))

    if likely == "cylindrical" or float(surf.get("cylindrical_ratio", 0)) >= 0.5:
        feats.append("cylindrical body")
    if float(surf.get("planar_ratio", 0)) >= 0.3:
        feats.append("planar faces (likely ends / flanges)")

    # outer rim if any circle candidate or ring
    outer_r = None
    if closed:
        outer_r = max(float(c["radius"]) for c in closed)
        feats.append(f"outer circular rim (r≈{outer_r:.4f})")
    elif rings >= 1 or groups >= 1:
        clusters = edge.get("radius_clusters") or []
        if clusters:
            outer_r = float(clusters[0]["radius_mean"])
            feats.append(f"outer circular rim (r≈{outer_r:.4f})")
        else:
            feats.append("outer circular rim")

    # hole only when evidence is strong
    allow_hole = rings >= 2 or (
        groups >= 2
        and len([c for c in closed if float(c.get("confidence", 0)) >= 0.75]) >= 2
    )
    if allow_hole and groups >= 2:
        clusters = edge.get("radius_clusters") or []
        if len(clusters) >= 2:
            inner = float(clusters[-1]["radius_mean"])
            feats.append(f"possible inner circular feature (r≈{inner:.4f}, optional)")
    else:
        feats.append("inner hole: NOT confirmed by Dora (do not invent Cut/hole)")

    return feats


def allowed_operations(meta: dict, closed: list[dict]) -> list[str]:
    edge = meta.get("edge_stats") or {}
    rings = int(edge.get("circular_ring_count", 0))
    groups = int(edge.get("concentric_radius_groups", 0))
    ops = ["Cylinder", "Sketch", "Extrude", "Revolve"]
    # Cut only when hole evidence is strong enough to avoid LLM hallucination
    if rings >= 2 or (
        groups >= 2 and len([c for c in closed if float(c.get("confidence", 0)) >= 0.8]) >= 2
    ):
        ops.append("Cut")
    return ops


def axis_extent(meta: dict) -> dict:
    """Height along PCA axis from bbox corners."""
    surf = meta.get("surface_stats") or {}
    axis = np.asarray(surf.get("pca_axis") or [0, 1, 0], dtype=np.float64)
    axis = _unit(axis)
    bmin = np.asarray(meta.get("bbox_min") or [0, 0, 0], dtype=np.float64)
    bmax = np.asarray(meta.get("bbox_max") or [1, 1, 1], dtype=np.float64)
    corners = np.array(
        [[x, y, z] for x in (bmin[0], bmax[0]) for y in (bmin[1], bmax[1]) for z in (bmin[2], bmax[2])],
        dtype=np.float64,
    )
    t = corners @ axis
    height = float(t.max() - t.min())
    center = 0.5 * (bmin + bmax)
    return {
        "axis": [_round(x) for x in axis.tolist()],
        "height": _round(height),
        "center": [_round(x) for x in center.tolist()],
        "t_min": _round(float(t.min())),
        "t_max": _round(float(t.max())),
    }


def build_geometry_summary(part_dir: Path | str) -> dict[str, Any]:
    part_dir = Path(part_dir)
    meta = _load_json(part_dir / "meta.json")
    closed = light_closed_feature_candidates(part_dir, meta)
    surf = meta.get("surface_stats") or {}
    edge = meta.get("edge_stats") or {}
    extent = axis_extent(meta)
    axis = extent["axis"]
    height = float(extent["height"])
    center = extent["center"]
    bottom_origin = [
        _round(center[0] - 0.5 * height * axis[0]),
        _round(center[1] - 0.5 * height * axis[1]),
        _round(center[2] - 0.5 * height * axis[2]),
    ]
    extent["bottom_origin"] = bottom_origin
    summary = {
        "part_id": meta.get("part_id") or part_dir.name,
        "part_type": infer_part_type(meta),
        "geometry": {
            "dominant_surface": surf.get("likely_class", "mixed"),
            "cylindrical_ratio": surf.get("cylindrical_ratio"),
            "planar_ratio": surf.get("planar_ratio"),
            "other_ratio": surf.get("other_ratio"),
            "pca_axis": surf.get("pca_axis"),
        },
        "bounding_box": {
            "min": meta.get("bbox_min"),
            "max": meta.get("bbox_max"),
            "size": meta.get("bbox"),
            "diagonal": meta.get("bbox_diagonal"),
        },
        "axis_extent": extent,
        "edge_information": {
            "sharp_edge_count": edge.get("sharp_edge_count", meta.get("sharp_edges")),
            "circular_ring_count": edge.get("circular_ring_count"),
            "concentric_radius_groups": edge.get("concentric_radius_groups"),
            "closed_curve_count": edge.get("closed_curve_count"),
            "radius_clusters": edge.get("radius_clusters", [])[:6],
        },
        "closed_feature_candidates": closed,
        "detected_features": detect_features(meta, closed),
        # Strategy / prefer-single-Cylinder lives in cad_feature_planner.py, not here.
        "allowed_operations_hint": allowed_operations(meta, closed),
        "units": "SOURCE_NATIVE",
        "source_meta": str(part_dir / "meta.json"),
    }
    return summary


def render_cad_brief(summary: dict[str, Any]) -> str:
    """Geometry evidence only (no CAD strategy / prefer-Cylinder policy)."""
    g = summary["geometry"]
    bb = summary["bounding_box"]
    e = summary["edge_information"]
    ax = summary["axis_extent"]
    lines = [
        f"Part id: {summary['part_id']}",
        f"Part type: {summary['part_type']}",
        "",
        "Geometry:",
        f"- dominant surface: {g.get('dominant_surface')}",
        f"- cylindrical ratio: {g.get('cylindrical_ratio')}",
        f"- planar ratio: {g.get('planar_ratio')}",
        "",
        "Bounding box:",
        f"- min: {bb.get('min')}",
        f"- max: {bb.get('max')}",
        f"- size: {bb.get('size')}",
        f"- diagonal: {bb.get('diagonal')}",
        "",
        "Axis extent (PCA):",
        f"- axis: {ax.get('axis')}",
        f"- height: {ax.get('height')}",
        f"- center: {ax.get('center')}",
        f"- suggested_cylinder_origin (BOTTOM): {ax.get('bottom_origin')}",
        "",
        "Edge information:",
        f"- sharp edge count: {e.get('sharp_edge_count')}",
        f"- circular ring count: {e.get('circular_ring_count')}",
        f"- concentric radius groups: {e.get('concentric_radius_groups')}",
        f"- closed curve count: {e.get('closed_curve_count')}",
    ]
    clusters = e.get("radius_clusters") or []
    if clusters:
        lines.append("- radius clusters:")
        for cl in clusters[:5]:
            lines.append(
                f"  - r={cl.get('radius_mean')} count={cl.get('count')} source={cl.get('source')}"
            )

    lines.append("")
    lines.append("Closed feature candidates (light circle fits, NOT BRep wires):")
    cands = summary.get("closed_feature_candidates") or []
    if not cands:
        lines.append("- (none)")
    else:
        for c in cands[:8]:
            lines.append(
                f"- type={c.get('type')} radius={c.get('radius')} "
                f"confidence={c.get('confidence')} source={c.get('source')}"
            )

    lines.append("")
    lines.append("Detected features:")
    for f in summary.get("detected_features") or []:
        lines.append(f"- {f}")

    lines.append("")
    lines.append(f"Units: {summary.get('units', 'SOURCE_NATIVE')}")
    return "\n".join(lines) + "\n"
