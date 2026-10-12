from __future__ import annotations

from typing import Any

import numpy as np
import trimesh

from .geometry_features import extract_geometry_features, face_regime_labels
from .router import compute_router_scores


def _face_adjacency(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray]:
    if hasattr(mesh, "face_adjacency") and len(mesh.face_adjacency) > 0:
        return np.asarray(mesh.face_adjacency), np.asarray(mesh.face_adjacency_angles)
    mesh.fix_normals()
    return np.asarray(mesh.face_adjacency), np.asarray(mesh.face_adjacency_angles)


def _connected_components(n: int, adj: np.ndarray, labels: np.ndarray) -> np.ndarray:
    parent = np.arange(n)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for f0, f1 in adj:
        if labels[f0] == labels[f1]:
            union(int(f0), int(f1))
    return np.array([find(i) for i in range(n)])


def decompose_mesh(mesh: trimesh.Trimesh, min_area_ratio: float = 0.08, features: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    labels = face_regime_labels(mesh)
    areas = np.asarray(mesh.area_faces, dtype=float)
    total_area = float(areas.sum()) + 1e-12
    adj, angles = _face_adjacency(mesh)
    if len(adj) == 0:
        radial = _radial_split(mesh, features or {}, areas, total_area, min_area_ratio)
        return _finalize_regions(mesh, radial, angles) if radial else []
    comp = _connected_components(len(mesh.faces), adj, labels)
    uniq = np.unique(comp)
    regions = []
    for cid in uniq:
        mask = comp == cid
        area_ratio = float(areas[mask].sum() / total_area)
        sub = mesh.submesh([np.where(mask)[0]], append=True, repair=False)
        if sub is None or len(sub.faces) < 12:
            continue
        regions.append({"face_mask": mask, "area_ratio": area_ratio, "mesh": sub})
    regions.sort(key=lambda r: r["area_ratio"], reverse=True)

    def merge_into(dst, src):
        dst["face_mask"] = dst["face_mask"] | src["face_mask"]
        dst["area_ratio"] = float(areas[dst["face_mask"]].sum() / total_area)
        dst["mesh"] = mesh.submesh([np.where(dst["face_mask"])[0]], append=True, repair=False)

    kept = []
    for r in regions:
        if r["area_ratio"] < min_area_ratio and kept:
            merge_into(kept[0], r)
        else:
            kept.append(r)
    regions = [r for r in kept if r["area_ratio"] >= min_area_ratio and r["mesh"] is not None]
    if len(regions) <= 1:
        regions = _radial_split(mesh, features or {}, areas, total_area, min_area_ratio)
    if not regions or len(regions) <= 1:
        return []
    return _finalize_regions(mesh, regions, angles)


def _radial_split(mesh: trimesh.Trimesh, features: dict[str, Any], areas: np.ndarray, total_area: float, min_area_ratio: float) -> list[dict[str, Any]]:
    axis = np.asarray(features.get("REVOLUTION_AXIS") or [0, 0, 1], dtype=float)
    if np.linalg.norm(axis) < 1e-9:
        return []
    axis = axis / np.linalg.norm(axis)
    verts = np.asarray(mesh.vertices, dtype=float)
    c = verts.mean(0)
    cents = verts[mesh.faces].mean(axis=1)
    rel = cents - c
    radii = np.linalg.norm(rel - np.outer(rel @ axis, axis), axis=1)
    if radii.std() / max(radii.mean(), 1e-12) < 0.15:
        return []
    av = float(features.get("area_volume_ratio") or 0.0)
    if av < 80.0:
        return []
    thr = float(np.median(radii))
    masks = [radii <= thr, radii > thr]
    out = []
    for mask in masks:
        ar = float(areas[mask].sum() / total_area)
        if ar < min_area_ratio:
            return []
        sub = mesh.submesh([np.where(mask)[0]], append=True, repair=False)
        if sub is None or len(sub.faces) < 12:
            return []
        out.append({"face_mask": mask, "area_ratio": ar, "mesh": sub})
    return out if len(out) == 2 else []


def _finalize_regions(mesh: trimesh.Trimesh, regions: list[dict[str, Any]], angles: np.ndarray) -> list[dict[str, Any]]:
    out = []
    hom_before = _homogeneity(mesh)
    for i, r in enumerate(regions):
        feats = extract_geometry_features(r["mesh"], f"REGION_{i:03d}")
        route = compute_router_scores(feats, r["mesh"])
        if route["selected_route"] == "MIXED_STRUCTURE":
            route["selected_route"] = "THIN_FREEFORM" if route["ROUTEB_SCORE"] >= route["CADFIT_SCORE"] else "REGULAR_CADFIT"
            route["selected_backend"] = "DORA_POINT2CAD" if route["selected_route"] == "THIN_FREEFORM" else "CADFIT"
            route["reason_codes"] = list(route.get("reason_codes", [])) + ["MAX_DECOMPOSITION_DEPTH"]
        out.append(
            {
                "region_id": f"REGION_{i:03d}",
                "face_mask": r["face_mask"],
                "area_ratio": r["area_ratio"],
                "mesh": r["mesh"],
                "features": feats,
                "routing": route,
                "HOMOGENEITY_BEFORE": hom_before,
            }
        )
    hom_after = float(np.mean([_homogeneity(r["mesh"]) for r in out]))
    for r in out:
        r["HOMOGENEITY_AFTER"] = hom_after
        r["boundary_compatibility"] = float(1.0 - np.mean(np.degrees(angles))) if len(angles) else 0.0
    return out


def _homogeneity(mesh: trimesh.Trimesh) -> float:
    labels = face_regime_labels(mesh)
    areas = np.asarray(mesh.area_faces, dtype=float)
    total = float(areas.sum()) + 1e-12
    shares = [float(areas[labels == lab].sum() / total) for lab in np.unique(labels)]
    return float(max(shares) if shares else 0.0)
