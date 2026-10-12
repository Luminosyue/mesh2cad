import numpy as np
from PIL import Image, ImageDraw
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


def _raster(vertices, faces, source_bounds, size=192):
    masks = []
    lo, hi = np.asarray(source_bounds[0]), np.asarray(source_bounds[1])
    for a, b in ((0, 1), (0, 2), (1, 2)):
        image = Image.new("1", (size, size), 0)
        draw = ImageDraw.Draw(image)
        sx = (size - 9) / max(hi[a] - lo[a], 1e-9)
        sy = (size - 9) / max(hi[b] - lo[b], 1e-9)
        scale = min(sx, sy)
        ox = (size - (hi[a] - lo[a]) * scale) / 2
        oy = (size - (hi[b] - lo[b]) * scale) / 2
        xy = np.c_[ox + (vertices[:, a] - lo[a]) * scale, size - (oy + (vertices[:, b] - lo[b]) * scale)]
        for face in faces:
            if max(face) < len(xy):
                draw.polygon([tuple(xy[index]) for index in face], fill=1)
        masks.append(np.asarray(image, dtype=bool))
    return masks


def silhouette_iou(source_points, candidate_points, source_faces=None, candidate_faces=None):
    if source_faces is None or candidate_faces is None:
        source_faces = np.zeros((0, 3), dtype=int)
        candidate_faces = np.zeros((0, 3), dtype=int)
    bounds = [source_points.min(0), source_points.max(0)]
    source_masks = _raster(source_points, source_faces, bounds)
    candidate_masks = _raster(candidate_points, candidate_faces, bounds)
    views = []
    for a, b in zip(source_masks, candidate_masks):
        union = np.logical_or(a, b).sum()
        views.append(float(np.logical_and(a, b).sum() / max(union, 1)))
    return {"views": views, "mean": float(np.mean(views)), "min": float(np.min(views))}


def section_profile_error(source_points, candidate_points):
    if len(source_points) == 0 or len(candidate_points) == 0:
        return 1.0
    center = source_points.mean(0)
    axis = np.linalg.svd(source_points - center, full_matrices=False)[2][0]
    source_coordinate = (source_points - center) @ axis
    candidate_coordinate = (candidate_points - center) @ axis
    errors = []
    for station in np.linspace(np.quantile(source_coordinate, 0.12), np.quantile(source_coordinate, 0.88), 7):
        width = 0.06 * (source_coordinate.max() - source_coordinate.min())
        source_section = source_points[np.abs(source_coordinate - station) < width]
        candidate_section = candidate_points[np.abs(candidate_coordinate - station) < width]
        if len(source_section) > 10 and len(candidate_section) > 3:
            source_widths = np.sort(np.ptp(source_section, axis=0))[-2:]
            candidate_widths = np.sort(np.ptp(candidate_section, axis=0))[-2:]
            errors.append(float(np.mean(np.abs(source_widths - candidate_widths) / np.maximum(source_widths, 1e-9))))
    return float(np.mean(errors)) if errors else 1.0


def geometry_qa(occ_valid, explosion, bbox_ratio, parameter_provenance_complete):
    passed = bool(occ_valid and not explosion and bbox_ratio < 25.0 and parameter_provenance_complete)
    return {"occ_valid": bool(occ_valid), "geometry_explosion": bool(explosion), "bbox_diagonal_ratio": float(bbox_ratio), "parameter_provenance_complete": bool(parameter_provenance_complete), "pass": passed}


def nativeness_qa(face_count, analytic_face_count, edge_count, triangle_like_face_count=0):
    analytic_ratio = analytic_face_count / max(face_count, 1)
    fragmentation = triangle_like_face_count / max(face_count, 1)
    score = float(np.clip(0.55 * analytic_ratio + 0.25 * (1.0 - fragmentation) + 0.20 * min(1.0, 80 / max(face_count, 1)), 0, 1))
    return {"face_count": int(face_count), "edge_count": int(edge_count), "analytic_face_count": int(analytic_face_count), "analytic_face_ratio": float(analytic_ratio), "triangle_like_fragmentation_ratio": float(fragmentation), "score": score, "pass": bool(score >= 0.45)}
