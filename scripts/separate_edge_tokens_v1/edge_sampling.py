#!/usr/bin/env python3
"""Turn stored Dora sharp-edge segments into a fixed-size edge point cloud.

The dataset already carries the segment representation produced by the Dora SES
pass (`dora/salient_edges.npz`: `edge_xyz0`, `edge_xyz1`, `edge_length`,
`dihedral_deg`), so no new edge detector is introduced here.

Sampling contract
-----------------
Points are distributed over segments proportionally to arc length,

    N_i  proportional to  L_i,      L_i = ||v1_i - v0_i||

and placed at cell centres along each segment. Mesh vertices are deliberately
not reused as sample locations: tessellation density must not decide edge token
density.

Normals follow the priority order fixed for V1:

    1. mean of the two adjacent face normals (renormalised)   -> "face_pair_mean"
    2. normal of the nearest sampled surface point            -> "nearest_surface"
    3. zero vector                                            -> "degenerate"

The fallback actually used is recorded per sample; feature semantics are never
silently changed.

Output lives in the same canonical frame as `features_canonical.npy`
(`p' = s * p + t` from `coordinate_transform.json`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DEFAULT_NUM_EDGE_POINTS = 1024
EDGE_CHANNELS = 6
SURFACE_CHANNELS = 6

NORMAL_SOURCE_FACE_PAIR = "face_pair_mean"
NORMAL_SOURCE_NEAREST_SURFACE = "nearest_surface"
NORMAL_SOURCE_DEGENERATE = "degenerate"


@dataclass
class EdgeCloud:
    """A fixed-size sharp-edge point cloud in canonical CAD coordinates."""

    features: np.ndarray  # (N, 6) float32 = [x, y, z, nx, ny, nz]
    segment_index: np.ndarray  # (N,) which sharp segment each point came from
    stats: dict = field(default_factory=dict)

    @property
    def points(self) -> np.ndarray:
        return self.features[:, :3]

    @property
    def normals(self) -> np.ndarray:
        return self.features[:, 3:6]


def load_sharp_segments(sample_dir: Path) -> dict:
    """Read `dora/salient_edges.npz`; endpoints are in mesh source space."""
    npz_path = Path(sample_dir) / "dora" / "salient_edges.npz"
    if not npz_path.is_file():
        raise FileNotFoundError(f"missing sharp-edge segments: {npz_path}")
    data = np.load(npz_path)
    v0 = np.asarray(data["edge_xyz0"], dtype=np.float64)
    v1 = np.asarray(data["edge_xyz1"], dtype=np.float64)
    lengths = np.linalg.norm(v1 - v0, axis=1)
    return {
        "v0": v0,
        "v1": v1,
        "length": lengths,
        "dihedral_deg": np.asarray(data["dihedral_deg"], dtype=np.float64),
        "vertex_indices": np.asarray(data["edge_vertex_indices"], dtype=np.int64),
        "num_segments": int(v0.shape[0]),
        "total_length": float(lengths.sum()),
    }


def _load_mesh(path: Path):
    """Mirror `scripts/build_cad_spatial_part.py::load_mesh` so indices line up."""
    import trimesh

    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    mesh = trimesh.Trimesh(
        vertices=np.asarray(mesh.vertices), faces=np.asarray(mesh.faces), process=False
    )
    if len(mesh.face_adjacency) == 0:
        mesh.merge_vertices()
        mesh.update_faces(mesh.unique_faces())
        mesh.remove_unreferenced_vertices()
    return mesh


def segment_normals_from_mesh(
    mesh, v0: np.ndarray, v1: np.ndarray, tol_scale: float = 1e-3
) -> tuple[np.ndarray, np.ndarray]:
    """Per-segment normal = normalised mean of the two adjacent face normals.

    Segments are matched to mesh adjacency edges by midpoint proximity rather
    than by stored vertex index, so a re-loaded mesh whose vertices were merged
    differently still resolves correctly.

    Returns (normals (E,3), matched mask (E,)).
    """
    from scipy.spatial import cKDTree

    normals = np.zeros((v0.shape[0], 3), dtype=np.float64)
    matched = np.zeros(v0.shape[0], dtype=bool)
    if v0.shape[0] == 0 or len(mesh.face_adjacency) == 0:
        return normals, matched

    adj_edges = np.asarray(mesh.face_adjacency_edges, dtype=np.int64)  # (A, 2)
    adj_faces = np.asarray(mesh.face_adjacency, dtype=np.int64)  # (A, 2)
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    face_normals = np.asarray(mesh.face_normals, dtype=np.float64)

    adj_mid = 0.5 * (verts[adj_edges[:, 0]] + verts[adj_edges[:, 1]])
    seg_mid = 0.5 * (v0 + v1)

    diag = float(np.linalg.norm(verts.max(axis=0) - verts.min(axis=0)))
    tol = max(diag * tol_scale, 1e-9)

    dist, idx = cKDTree(adj_mid).query(seg_mid, k=1)
    hit = dist <= tol
    if not np.any(hit):
        return normals, matched

    pair = adj_faces[idx[hit]]
    summed = face_normals[pair[:, 0]] + face_normals[pair[:, 1]]
    norm = np.linalg.norm(summed, axis=1, keepdims=True)
    # Opposing face normals (a knife-edge fold) sum to ~0 and carry no direction.
    usable = norm[:, 0] > 1e-8
    resolved = np.zeros_like(summed)
    resolved[usable] = summed[usable] / norm[usable]

    hit_idx = np.where(hit)[0]
    normals[hit_idx[usable]] = resolved[usable]
    matched[hit_idx[usable]] = True
    return normals, matched


def allocate_points_by_length(
    lengths: np.ndarray, num_points: int
) -> np.ndarray:
    """Largest-remainder allocation of `num_points` proportional to `lengths`."""
    n_seg = lengths.shape[0]
    if n_seg == 0 or num_points <= 0:
        return np.zeros(n_seg, dtype=np.int64)

    total = float(lengths.sum())
    if total <= 0:
        counts = np.zeros(n_seg, dtype=np.int64)
        counts[: min(n_seg, num_points)] = 1
        deficit = num_points - int(counts.sum())
        if deficit > 0 and n_seg > 0:
            counts[np.arange(deficit) % n_seg] += 1
        return counts

    exact = lengths / total * num_points
    counts = np.floor(exact).astype(np.int64)

    # Every sharp segment deserves at least one sample, even a very short one.
    counts = np.maximum(counts, 1)
    while int(counts.sum()) > num_points:
        # Trim from the segments that are most over-served relative to length.
        over = counts - exact
        order = np.argsort(-over)
        for j in order:
            if counts[j] > 1:
                counts[j] -= 1
                break
            if int(counts.sum()) <= num_points:
                break
        else:  # every segment already at 1 and still too many
            break

    remainder = exact - np.floor(exact)
    while int(counts.sum()) < num_points:
        deficit = num_points - int(counts.sum())
        order = np.argsort(-remainder)
        take = min(deficit, n_seg)
        counts[order[:take]] += 1
    return counts


def sample_points_on_segments(
    v0: np.ndarray, v1: np.ndarray, counts: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Uniform arc-length sampling at cell centres along each segment."""
    pts, seg_idx = [], []
    for i in range(v0.shape[0]):
        n = int(counts[i])
        if n <= 0:
            continue
        # (k + 0.5) / n keeps samples off the shared endpoints, so a chain of
        # segments does not pile duplicates at every junction.
        t = (np.arange(n, dtype=np.float64) + 0.5) / n
        pts.append(v0[i][None, :] + t[:, None] * (v1[i] - v0[i])[None, :])
        seg_idx.append(np.full(n, i, dtype=np.int64))
    if not pts:
        return np.zeros((0, 3), dtype=np.float64), np.zeros((0,), dtype=np.int64)
    return np.concatenate(pts, axis=0), np.concatenate(seg_idx, axis=0)


def _fit_to_size(
    points: np.ndarray,
    normals: np.ndarray,
    seg_idx: np.ndarray,
    num_points: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Force exactly `num_points` rows without disturbing spatial coverage."""
    n = points.shape[0]
    if n == num_points:
        return points, normals, seg_idx
    if n > num_points:
        keep = rng.choice(n, size=num_points, replace=False)
        keep.sort()
        return points[keep], normals[keep], seg_idx[keep]
    if n == 0:
        raise ValueError("cannot pad an empty edge cloud")
    extra = rng.choice(n, size=num_points - n, replace=True)
    return (
        np.concatenate([points, points[extra]], axis=0),
        np.concatenate([normals, normals[extra]], axis=0),
        np.concatenate([seg_idx, seg_idx[extra]], axis=0),
    )


def build_edge_cloud(
    sample_dir: Path,
    num_edge_points: int = DEFAULT_NUM_EDGE_POINTS,
    seed: int = 0,
    surface_features: np.ndarray | None = None,
) -> EdgeCloud:
    """Sample a canonical-space (num_edge_points, 6) sharp-edge cloud.

    `surface_features` is the canonical (N, >=6) surface array; it supplies the
    canonical transform check and the nearest-surface normal fallback.
    """
    sample_dir = Path(sample_dir)
    rng = np.random.default_rng(seed)

    seg = load_sharp_segments(sample_dir)
    v0, v1, lengths = seg["v0"], seg["v1"], seg["length"]
    if seg["num_segments"] == 0:
        raise ValueError(f"{sample_dir.name}: zero sharp-edge segments")

    mesh_path = sample_dir / "model.stl"
    seg_normals = np.zeros((seg["num_segments"], 3), dtype=np.float64)
    matched = np.zeros(seg["num_segments"], dtype=bool)
    mesh_error = None
    if mesh_path.is_file():
        try:
            mesh = _load_mesh(mesh_path)
            seg_normals, matched = segment_normals_from_mesh(mesh, v0, v1)
        except Exception as exc:  # noqa: BLE001 - recorded, never silenced
            mesh_error = f"{type(exc).__name__}: {exc}"
    else:
        mesh_error = f"missing mesh {mesh_path}"

    counts = allocate_points_by_length(lengths, num_edge_points)
    points_src, seg_idx = sample_points_on_segments(v0, v1, counts)
    normals = seg_normals[seg_idx]

    # Canonical transform: identical T as features_canonical.npy / program_canonical.dsl
    tf_path = sample_dir / "coordinate_transform.json"
    tf = json.loads(tf_path.read_text(encoding="utf-8"))
    scale = float(tf["scale"])
    translation = np.asarray(tf["translation"], dtype=np.float64)
    points_canon = points_src * scale + translation

    # Normals are direction-only: a uniform positive scale leaves them unchanged.
    normal_source = np.where(matched[seg_idx], NORMAL_SOURCE_FACE_PAIR, "")
    unresolved = ~matched[seg_idx]
    n_nearest = 0
    n_degenerate = 0
    if np.any(unresolved):
        if surface_features is not None and surface_features.shape[0] > 0:
            from scipy.spatial import cKDTree

            tree = cKDTree(np.asarray(surface_features[:, :3], dtype=np.float64))
            _, nn = tree.query(points_canon[unresolved], k=1)
            normals[unresolved] = np.asarray(
                surface_features[nn, 3:6], dtype=np.float64
            )
            normal_source[unresolved] = NORMAL_SOURCE_NEAREST_SURFACE
            n_nearest = int(unresolved.sum())
        else:
            normal_source[unresolved] = NORMAL_SOURCE_DEGENERATE
            n_degenerate = int(unresolved.sum())

    norm = np.linalg.norm(normals, axis=1, keepdims=True)
    bad = norm[:, 0] <= 1e-8
    normals = np.divide(normals, norm, out=np.zeros_like(normals), where=norm > 1e-8)
    if np.any(bad):
        normal_source[bad] = NORMAL_SOURCE_DEGENERATE
        n_degenerate = int(bad.sum())

    points_canon, normals, seg_idx = _fit_to_size(
        points_canon, normals, seg_idx, num_edge_points, rng
    )

    features = np.concatenate([points_canon, normals], axis=1).astype(np.float32)

    stats = {
        "num_segments": seg["num_segments"],
        "total_edge_length_source": seg["total_length"],
        "total_edge_length_canonical": float(seg["total_length"] * scale),
        "num_edge_points": int(features.shape[0]),
        "points_per_segment_min": int(counts.min()),
        "points_per_segment_max": int(counts.max()),
        "points_per_segment_mean": float(counts.mean()),
        "normal_face_pair_frac": float(matched[seg_idx].mean()) if len(seg_idx) else 0.0,
        "normal_nearest_surface_count": n_nearest,
        "normal_degenerate_count": n_degenerate,
        "mesh_error": mesh_error,
        "canonical_scale": scale,
        "canonical_translation": translation.tolist(),
        "dihedral_deg_min": float(seg["dihedral_deg"].min()),
        "dihedral_deg_max": float(seg["dihedral_deg"].max()),
        "edge_bbox_min": features[:, :3].min(axis=0).tolist(),
        "edge_bbox_max": features[:, :3].max(axis=0).tolist(),
    }
    return EdgeCloud(features=features, segment_index=seg_idx, stats=stats)
