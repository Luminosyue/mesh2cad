from __future__ import annotations

from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def _sorted_extents(verts: np.ndarray) -> tuple[float, float, float, float]:
    ext = np.sort(np.abs(verts.max(0) - verts.min(0)))
    major = float(ext[2])
    middle = float(ext[1])
    minor = float(ext[0])
    diag = float(np.linalg.norm(ext))
    return major, middle, minor, max(diag, 1e-12)


def _pca_axes(verts: np.ndarray) -> np.ndarray:
    c = verts.mean(0)
    _, _, vt = np.linalg.svd(verts - c, full_matrices=False)
    return vt


def _face_curvature(mesh: trimesh.Trimesh) -> np.ndarray:
    fn = np.asarray(mesh.face_normals, dtype=float)
    n = len(mesh.faces)
    curv = np.zeros(n, dtype=float)
    if not hasattr(mesh, "face_adjacency_angles") or len(mesh.face_adjacency_angles) == 0:
        return curv
    edges = np.asarray(mesh.face_adjacency_edges)
    angles = np.degrees(np.asarray(mesh.face_adjacency_angles, dtype=float))
    for e, ang in zip(edges, angles):
        curv[e[0]] = max(curv[e[0]], ang)
        curv[e[1]] = max(curv[e[1]], ang)
    return curv


def _local_thickness(mesh: trimesh.Trimesh, n_rays: int = 800) -> np.ndarray:
    verts = np.asarray(mesh.vertices, dtype=float)
    fn = np.asarray(mesh.vertex_normals, dtype=float)
    diag = max(float(np.linalg.norm(verts.max(0) - verts.min(0))), 1e-12)
    rng = np.random.default_rng(7)
    idx = rng.choice(len(verts), size=min(n_rays, len(verts)), replace=False)
    origins = verts[idx] - fn[idx] * (1e-4 * diag)
    directions = -fn[idx]
    norms = np.linalg.norm(directions, axis=1, keepdims=True)
    valid = norms[:, 0] > 1e-9
    origins = origins[valid]
    directions = directions[valid] / np.maximum(norms[valid], 1e-12)
    thickness = []
    try:
        locations, ray_ids, _ = mesh.ray.intersects_location(origins, directions, multiple_hits=False)
        if len(ray_ids):
            d = np.linalg.norm(locations - origins[ray_ids], axis=1)
            d = d[(d > 1e-6) & (d < 0.8 * diag)]
            if len(d):
                thickness = d.tolist()
    except Exception:
        thickness = []
    if len(thickness) < 20:
        tree = cKDTree(verts)
        for p, n in zip(origins[:400], directions[:400]):
            q = p + n * (0.002 * diag)
            d, j = tree.query(q, k=8)
            rel = verts[j] - p
            along = rel @ n
            ok = along > 1e-6
            if np.any(ok):
                thickness.append(float(np.min(along[ok])))
    if not thickness:
        return np.array([0.25 * diag])
    return np.asarray(thickness, dtype=float)


def _planarity(mesh: trimesh.Trimesh) -> float:
    fn = np.asarray(mesh.face_normals, dtype=float)
    if len(fn) == 0:
        return 0.0
    ref = fn.mean(0)
    ref_norm = np.linalg.norm(ref)
    if ref_norm < 1e-9:
        return 0.0
    ref = ref / ref_norm
    dots = np.abs(fn @ ref)
    return float(np.mean(dots > 0.95))


def _curvature_ratios(curv: np.ndarray) -> dict[str, float]:
    if len(curv) == 0:
        return {"LOW_CURVATURE_RATIO": 0.0, "MEDIUM_CURVATURE_RATIO": 0.0, "HIGH_CURVATURE_RATIO": 0.0}
    low = float(np.mean(curv < 15.0))
    med = float(np.mean((curv >= 15.0) & (curv < 45.0)))
    high = float(np.mean(curv >= 45.0))
    return {"LOW_CURVATURE_RATIO": low, "MEDIUM_CURVATURE_RATIO": med, "HIGH_CURVATURE_RATIO": high}


def _section_metrics(mesh: trimesh.Trimesh, axis: np.ndarray, positions: list[float]) -> dict[str, float]:
    verts = np.asarray(mesh.vertices, dtype=float)
    c = verts.mean(0)
    axis = axis / max(np.linalg.norm(axis), 1e-12)
    proj = (verts - c) @ axis
    pmin, pmax = float(proj.min()), float(proj.max())
    span = max(pmax - pmin, 1e-12)
    areas, perims, centroids = [], [], []
    u, v = np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])
    if abs(np.dot(axis, u)) > 0.9:
        u = np.array([0.0, 1.0, 0.0])
    u = u - axis * np.dot(u, axis)
    u = u / max(np.linalg.norm(u), 1e-12)
    v = np.cross(axis, u)
    for t in positions:
        plane = pmin + t * span
        band = np.abs(proj - plane) <= 0.03 * span
        if int(band.sum()) < 12:
            continue
        pts = verts[band]
        uv = np.column_stack([(pts - c) @ u, (pts - c) @ v])
        rng = np.ptp(uv, axis=0)
        area = float(rng[0] * rng[1])
        perim = float(2 * (rng[0] + rng[1]))
        areas.append(area)
        perims.append(perim)
        centroids.append(uv.mean(0))
    if len(areas) < 3:
        return {"SECTION_AREA_CV": 1.0, "SECTION_SHAPE_VARIATION": 1.0, "SECTION_CENTROID_DRIFT": 1.0, "EXTRUSION_EVIDENCE": 0.0}
    areas = np.asarray(areas, dtype=float)
    perims = np.asarray(perims, dtype=float)
    cents = np.asarray(centroids, dtype=float)
    area_cv = float(np.std(areas) / max(np.mean(areas), 1e-12))
    shape_var = float(np.std(perims / np.maximum(areas, 1e-12)) / max(np.mean(perims / np.maximum(areas, 1e-12)), 1e-12))
    drift = float(np.linalg.norm(cents - cents.mean(0), axis=1).mean() / max(np.ptp(cents), 1e-12))
    extrusion = float(max(0.0, 1.0 - area_cv) * max(0.0, 1.0 - drift))
    return {
        "SECTION_AREA_CV": area_cv,
        "SECTION_SHAPE_VARIATION": shape_var,
        "SECTION_CENTROID_DRIFT": drift,
        "EXTRUSION_EVIDENCE": extrusion,
    }


def _revolution_score(mesh: trimesh.Trimesh, axes: np.ndarray) -> tuple[float, list[float]]:
    verts = np.asarray(mesh.vertices, dtype=float)
    c = verts.mean(0)
    best_score = 0.0
    best_axis = axes[0].tolist()
    for ax in axes:
        axn = ax / max(np.linalg.norm(ax), 1e-12)
        rel = verts - c
        along = rel @ axn
        perp = rel - np.outer(along, axn)
        radii = np.linalg.norm(perp, axis=1)
        if len(radii) < 20:
            continue
        bins = np.linspace(along.min(), along.max(), 8)
        circular = []
        for i in range(len(bins) - 1):
            m = (along >= bins[i]) & (along < bins[i + 1])
            if int(m.sum()) < 8:
                continue
            r = radii[m]
            cv = float(np.std(r) / max(np.mean(r), 1e-12))
            circular.append(max(0.0, 1.0 - cv))
        if circular:
            score = float(np.mean(circular))
            if score > best_score:
                best_score = score
                best_axis = axn.tolist()
    return best_score, best_axis


def _freeform_score(curv_ratios: dict[str, float], extrusion: float, revolution: float, thickness_ratio: float) -> float:
    curved = 0.55 * curv_ratios["HIGH_CURVATURE_RATIO"] + 0.35 * curv_ratios["MEDIUM_CURVATURE_RATIO"]
    thin = max(0.0, 1.0 - 4.0 * thickness_ratio)
    non_prismatic = max(0.0, 1.0 - extrusion) * max(0.0, 1.0 - revolution)
    return float(np.clip(0.4 * curved + 0.35 * thin + 0.25 * non_prismatic, 0.0, 1.0))


def _regime_label(thickness_ratio: float, extrusion: float, revolution: float, freeform: float, planar: float) -> str:
    if revolution > 0.55 and thickness_ratio > 0.08:
        return "ROTATIONAL"
    if extrusion > 0.55 and freeform < 0.45:
        return "EXTRUSION_LIKE"
    if thickness_ratio < 0.12 or freeform > 0.55:
        return "THIN_FREEFORM"
    if planar > 0.65:
        return "PLANAR_DOMINANT"
    return "VOLUMETRIC_MIXED"


def extract_geometry_features(mesh: trimesh.Trimesh, part_id: str = "") -> dict[str, Any]:
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    major, middle, minor, diag = _sorted_extents(verts)
    thickness_ratio = minor / max(major, 1e-12)
    secondary_ratio = middle / max(major, 1e-12)
    thickness_raw = _local_thickness(mesh)
    thickness_norm = thickness_raw / diag
    curv = _face_curvature(mesh)
    curv_ratios = _curvature_ratios(curv)
    planar = _planarity(mesh)
    axes = _pca_axes(verts)
    positions = [0.1 * i for i in range(1, 10)]
    sec_best = {"EXTRUSION_EVIDENCE": 0.0, "SECTION_AREA_CV": 1.0, "SECTION_SHAPE_VARIATION": 1.0, "SECTION_CENTROID_DRIFT": 1.0}
    for ax in axes:
        sm = _section_metrics(mesh, ax, positions)
        if sm["EXTRUSION_EVIDENCE"] > sec_best["EXTRUSION_EVIDENCE"]:
            sec_best = sm
    revolution, rev_axis = _revolution_score(mesh, axes)
    freeform = _freeform_score(curv_ratios, sec_best["EXTRUSION_EVIDENCE"], revolution, thickness_ratio)
    regime = _regime_label(thickness_ratio, sec_best["EXTRUSION_EVIDENCE"], revolution, freeform, planar)
    vol = float(mesh.volume) if mesh.is_watertight else 0.0
    area = float(mesh.area)
    return {
        "part_id": part_id,
        "vertices": int(len(verts)),
        "triangles": int(len(faces)),
        "bbox_extent_x": float(verts[:, 0].max() - verts[:, 0].min()),
        "bbox_extent_y": float(verts[:, 1].max() - verts[:, 1].min()),
        "bbox_extent_z": float(verts[:, 2].max() - verts[:, 2].min()),
        "bbox_diagonal": diag,
        "major_extent": major,
        "middle_extent": middle,
        "minor_extent": minor,
        "THICKNESS_RATIO": float(thickness_ratio),
        "SECONDARY_RATIO": float(secondary_ratio),
        "surface_area": area,
        "volume": vol,
        "area_volume_ratio": float(area / max(vol, 1e-12)) if vol > 0 else float("inf"),
        "THICKNESS_MEAN": float(thickness_norm.mean()),
        "THICKNESS_P50": float(np.median(thickness_norm)),
        "THICKNESS_P95": float(np.percentile(thickness_norm, 95)),
        "THICKNESS_STD": float(thickness_norm.std()),
        "PLANAR_SUPPORT_RATIO": float(planar),
        **curv_ratios,
        **sec_best,
        "REVOLUTION_SCORE": float(revolution),
        "REVOLUTION_AXIS": rev_axis,
        "FREEFORM_SCORE": float(freeform),
        "GEOMETRY_REGIME": regime,
    }


def face_regime_labels(mesh: trimesh.Trimesh) -> np.ndarray:
    curv = _face_curvature(mesh)
    fn = np.asarray(mesh.face_normals, dtype=float)
    ref = fn.mean(0)
    ref = ref / max(np.linalg.norm(ref), 1e-12)
    planar_face = np.abs(fn @ ref) > 0.92
    labels = np.zeros(len(mesh.faces), dtype=int)
    labels[planar_face & (curv < 20)] = 0
    labels[(curv >= 20) & (curv < 45)] = 1
    labels[curv >= 45] = 2
    labels[planar_face & (curv >= 20)] = 1
    return labels


def mixed_structure_score(mesh: trimesh.Trimesh, features: dict[str, Any]) -> tuple[float, int, float]:
    labels = face_regime_labels(mesh)
    areas = np.asarray(mesh.area_faces, dtype=float)
    total = float(areas.sum()) + 1e-12
    regime_areas = {}
    for lab in np.unique(labels):
        regime_areas[int(lab)] = float(areas[labels == lab].sum() / total)
    significant = [a for a in regime_areas.values() if a > 0.12]
    regime_count = len(significant)
    entropy = 0.0
    for a in significant:
        entropy -= a * np.log(max(a, 1e-12))
    entropy /= max(np.log(max(regime_count, 2)), 1e-12)
    curv = _face_curvature(mesh)
    boundary = float(np.mean(curv > 35.0))
    score = float(np.clip(0.45 * min(1.0, (regime_count - 1) / 2.0) + 0.35 * entropy + 0.20 * boundary, 0.0, 1.0))
    av = features.get("area_volume_ratio") or 0.0
    thin_shell = av > 80.0
    if thin_shell and features["REVOLUTION_SCORE"] > 0.50:
        score = max(score, 0.64)
        regime_count = max(regime_count, 2)
    if features["EXTRUSION_EVIDENCE"] > 0.45 and features["REVOLUTION_SCORE"] > 0.50 and thin_shell:
        score = max(score, 0.72)
        regime_count = max(regime_count, 2)
    return score, regime_count, float(entropy)
