import numpy as np
from scipy.spatial import cKDTree


def _mask(points, axes, bins=220):
    p = points[:, axes]
    lo, hi = p.min(0), p.max(0)
    span = np.maximum(hi - lo, 1e-12)
    ij = np.clip(((p - lo) / span * (bins - 1)).astype(int), 0, bins - 1)
    mask = np.zeros((bins, bins), dtype=bool)
    mask[ij[:, 0], ij[:, 1]] = True
    for _ in range(3):
        mask |= np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
    return mask, lo, span


def _mask_in_frame(points, axes, lo, span, bins=220):
    p = points[:, axes]
    ij = np.clip(((p - lo) / np.maximum(span, 1e-12) * (bins - 1)).astype(int), 0, bins - 1)
    mask = np.zeros((bins, bins), dtype=bool)
    inside = np.all((p >= lo) & (p <= lo + span), axis=1)
    ij = ij[inside]
    if len(ij):
        mask[ij[:, 0], ij[:, 1]] = True
    for _ in range(3):
        mask |= np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
    return mask


def silhouette_iou(source_points, candidate_points):
    views = []
    for axes in ((0, 1), (0, 2), (1, 2)):
        a, lo, span = _mask(source_points, axes)
        b = _mask_in_frame(candidate_points, axes, lo, span)
        union = np.logical_or(a, b).sum()
        views.append(float(np.logical_and(a, b).sum() / max(union, 1)))
    return {"views": views, "mean": float(np.mean(views)), "min": float(np.min(views))}


def section_profile_error(source_points, candidate_points):
    if len(source_points) == 0 or len(candidate_points) == 0:
        return 1.0
    span = np.ptp(source_points, axis=0)
    axis = int(np.argmax(span))
    lo, hi = source_points[:, axis].min(), source_points[:, axis].max()
    errors = []
    diag = float(np.linalg.norm(span))
    for t in np.linspace(lo, hi, 7)[1:-1]:
        width = max((hi - lo) * 0.035, 1e-6)
        s = source_points[np.abs(source_points[:, axis] - t) <= width]
        c = candidate_points[np.abs(candidate_points[:, axis] - t) <= width]
        if len(s) < 5 or len(c) < 5:
            continue
        keep = [i for i in range(3) if i != axis]
        a, b = s[:, keep], c[:, keep]
        e = (cKDTree(a).query(b)[0].mean() + cKDTree(b).query(a)[0].mean()) / 2
        errors.append(float(e / max(diag, 1e-12)))
    return float(np.mean(errors)) if errors else 1.0


def geometry_qa(occ_valid, explosion, bbox_ratio, parameter_provenance_complete):
    passed = bool(occ_valid and not explosion and bbox_ratio < 25.0 and parameter_provenance_complete)
    return {
        "occ_valid": bool(occ_valid),
        "geometry_explosion": bool(explosion),
        "bbox_diagonal_ratio": float(bbox_ratio),
        "parameter_provenance_complete": bool(parameter_provenance_complete),
        "pass": passed,
    }


def nativeness_qa(face_count, analytic_face_count, edge_count, triangle_like_face_count=0):
    analytic_ratio = analytic_face_count / max(face_count, 1)
    fragmentation = triangle_like_face_count / max(face_count, 1)
    score = float(np.clip(0.55 * analytic_ratio + 0.25 * (1.0 - fragmentation) + 0.20 * min(1.0, 80 / max(face_count, 1)), 0, 1))
    return {
        "face_count": int(face_count),
        "edge_count": int(edge_count),
        "analytic_face_count": int(analytic_face_count),
        "analytic_face_ratio": float(analytic_ratio),
        "triangle_like_fragmentation_ratio": float(fragmentation),
        "score": score,
        "pass": bool(score >= 0.45),
    }
