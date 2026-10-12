"""Build one Method-B clean pack from a STEP file."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

from .constants import (
    DEFAULT_SEED,
    EXPERIMENT,
    NOISE_SIGMAS,
    NUM_EDGE_POINTS,
    NUM_SURFACE_POINTS,
    PRIMARY_CURVE_TYPES,
    SHARP_ANGLE_DEG,
    SURFACE_CHANNELS,
    TARGET_DIAGONAL,
)
from .tessellate import tessellate_step

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from geometry_pack_v1.edge_sample import sample_edge_cloud  # noqa: E402
from geometry_pack_v1.mesh_edges import detect_sharp_edges, segment_face_pair_normals  # noqa: E402
from geometry_pack_v1.surface import sample_surface_uniform  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False, default=str) + "\n", encoding="utf-8")


def _apply_canonical(points: np.ndarray, scale: float, translation: np.ndarray) -> np.ndarray:
    return np.asarray(points, dtype=np.float64) * float(scale) + translation


def _pack_xyz_normal(xyz: np.ndarray, normals: np.ndarray) -> np.ndarray:
    feats = np.concatenate([xyz, normals], axis=1).astype(np.float32)
    if feats.shape[1] != SURFACE_CHANNELS:
        raise ValueError(f"expected {SURFACE_CHANNELS} channels, got {feats.shape}")
    return feats


def _export_noisy_meshes(out_dir: Path, vertices: np.ndarray, faces: np.ndarray, seed: int) -> dict:
    import trimesh

    clean = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    clean.export(out_dir / "mesh_clean.obj")
    rng = np.random.default_rng(int(seed) + 17)
    diag = float(np.linalg.norm(vertices.max(axis=0) - vertices.min(axis=0)))
    scale = max(diag, 1e-9)
    written = {"mesh_clean.obj": True}
    for tag, rel_sigma in NOISE_SIGMAS.items():
        eps = rng.normal(0.0, float(rel_sigma) * scale, size=vertices.shape)
        noisy = trimesh.Trimesh(vertices=vertices + eps, faces=faces, process=False)
        name = f"mesh_noise_{tag}.obj"
        noisy.export(out_dir / name)
        written[name] = True
    return {"noise_relative_to_bbox_diag": True, "sigmas": dict(NOISE_SIGMAS), "files": written}


def _compact_curve(rec: dict) -> dict | None:
    """Jerry-facing compact curve params (world frame)."""
    ctype = rec.get("curve_type")
    wp = rec.get("world_parameters") or {}
    if ctype == "LINE":
        return {
            "type": "line",
            "direction": wp.get("direction"),
            "length": rec.get("length"),
            "origin": wp.get("origin"),
        }
    if ctype == "CIRCLE":
        return {
            "type": "circle",
            "center": wp.get("center"),
            "radius": wp.get("radius"),
            "normal": wp.get("normal"),
        }
    if ctype == "ELLIPSE":
        return {
            "type": "ellipse",
            "center": wp.get("center"),
            "major_radius": wp.get("major_radius"),
            "minor_radius": wp.get("minor_radius"),
            "normal": wp.get("normal"),
            "major_axis": wp.get("major_axis"),
            "minor_axis": wp.get("minor_axis"),
        }
    if ctype == "BSPLINE":
        return {
            "type": "bspline",
            "degree": wp.get("degree"),
            "control_points": wp.get("control_points"),
        }
    return None


def _extract_curves(shape, cad_id: str, dataset: str):
    from curve_token_v1.canonicalize_curves import canonicalize_curves, from_bbox
    from curve_token_v1.config import CURVE_TYPE_IDS, SCHEMA_VERSION
    from curve_token_v1.extract_brep_curves import extract_curves_from_shape

    data = extract_curves_from_shape(shape, cad_id=cad_id)
    records = data["curves"]
    if not records:
        raise RuntimeError("no usable curves")
    nz = from_bbox(data["source_bbox_min"], data["source_bbox_max"], TARGET_DIAGONAL)
    data = canonicalize_curves(data, nz)
    type_counts: dict[str, int] = {}
    for r in records:
        type_counts[r["curve_type"]] = type_counts.get(r["curve_type"], 0) + 1
    curves_json = {
        "schema_version": SCHEMA_VERSION,
        "cad_id": cad_id,
        "dataset": dataset,
        "method": "B_parametric_curve_token",
        "num_curves": data["num_curves"],
        "num_topo_edges": data["num_topo_edges"],
        "num_vertices": data["num_vertices"],
        "num_faces": data["num_faces"],
        "num_skipped_edges": data["num_skipped_edges"],
        "curve_type_counts": type_counts,
        "curve_type_ids": CURVE_TYPE_IDS,
        "source_bbox_min": data["source_bbox_min"],
        "source_bbox_max": data["source_bbox_max"],
        "source_diagonal": data["source_diagonal"],
        "curves": records,
    }
    compact = {
        "cad_id": cad_id,
        "dataset": dataset,
        "curves": [c for c in (_compact_curve(r) for r in records) if c is not None],
    }
    return curves_json, nz, compact, type_counts


def build_one(
    *,
    step_path: Path,
    out_dir: Path,
    sample_id: str,
    dataset: str,
    seed: int = DEFAULT_SEED,
    overwrite: bool = False,
    annotation_path: Path | None = None,
) -> dict:
    t0 = time.time()
    step_path = Path(step_path)
    out_dir = Path(out_dir)
    meta_path = out_dir / "metadata.json"
    if meta_path.is_file() and not overwrite:
        return json.loads(meta_path.read_text(encoding="utf-8"))

    tess = tessellate_step(step_path)
    shape = tess["shape"]
    vertices, faces = tess["vertices"], tess["faces"]
    params = tess["params"]

    out_dir.mkdir(parents=True, exist_ok=True)
    noise_info = _export_noisy_meshes(out_dir, vertices, faces, seed)

    # Normalization from B-Rep bbox (CADFS has no Track-A transform).
    from curve_token_v1.canonicalize_curves import from_bbox

    mn = vertices.min(axis=0)
    mx = vertices.max(axis=0)
    # Prefer B-Rep bbox via curve extractor; fall back to mesh bbox if needed.
    try:
        curves_json, nz, compact, type_counts = _extract_curves(shape, sample_id, dataset)
    except Exception as exc:  # noqa: BLE001
        return {
            "sample_id": sample_id,
            "dataset": dataset,
            "ok": False,
            "qa_pass": False,
            "error": f"curve_extract_failed: {exc}",
            "elapsed_sec": time.time() - t0,
        }

    scale, translation = float(nz.scale), nz.t

    points, normals, face_idx = sample_surface_uniform(vertices, faces, NUM_SURFACE_POINTS, seed)
    surface = _pack_xyz_normal(_apply_canonical(points, scale, translation), normals)
    np.save(out_dir / "surface_points.npy", surface)
    np.save(out_dir / "surface_face_index.npy", face_idx.astype(np.int32))

    sharp = detect_sharp_edges(
        vertices,
        faces,
        tess["face_adjacency"],
        tess["face_adjacency_edges"],
        SHARP_ANGLE_DEG,
    )
    # sharp_edges.npy: M×3 segment midpoints (world / source frame, then canonical).
    if sharp["num_segments"] > 0:
        mids = 0.5 * (sharp["v0"] + sharp["v1"])
        sharp_xyz = _apply_canonical(mids, scale, translation).astype(np.float32)
        sharp_normals = segment_face_pair_normals(vertices, faces, sharp["face_pairs"])
        edge_pts, _, _, edge_stats = sample_edge_cloud(
            sharp["v0"], sharp["v1"], sharp_normals, NUM_EDGE_POINTS, seed + 1
        )
        edge_xyz = _apply_canonical(edge_pts, scale, translation).astype(np.float32)
        edge_valid = True
    else:
        sharp_xyz = np.zeros((0, 3), dtype=np.float32)
        edge_xyz = np.zeros((NUM_EDGE_POINTS, 3), dtype=np.float32)
        edge_stats = {"num_segments": 0, "empty_padded": True}
        edge_valid = False

    np.save(out_dir / "sharp_edges.npy", sharp_xyz)
    np.save(out_dir / "edge_points.npy", edge_xyz)
    np.savez_compressed(
        out_dir / "mesh_sharp_edges.npz",
        v0=sharp["v0"].astype(np.float32),
        v1=sharp["v1"].astype(np.float32),
        vertex_indices=sharp["vertex_indices"].astype(np.int32),
        dihedral_deg=sharp["dihedral_deg"].astype(np.float32),
        face_pairs=sharp["face_pairs"].astype(np.int32),
    )

    _write_json(out_dir / "curves.json", curves_json)
    _write_json(out_dir / "curves_compact.json", compact)
    _write_json(out_dir / "normalization.json", nz.to_json())
    _write_json(out_dir / "tessellation.json", params)

    if annotation_path is not None and Path(annotation_path).is_file():
        (out_dir / "text_annotation.txt").write_text(
            Path(annotation_path).read_text(encoding="utf-8", errors="replace"),
            encoding="utf-8",
        )

    primary = sum(int(type_counts.get(t, 0)) for t in PRIMARY_CURVE_TYPES)
    non_line = primary - int(type_counts.get("LINE", 0))
    qa = {
        "qa_pass": bool(primary > 0 and surface.shape == (NUM_SURFACE_POINTS, SURFACE_CHANNELS)),
        "num_curves": int(curves_json["num_curves"]),
        "curve_type_counts": type_counts,
        "primary_curve_count": int(primary),
        "non_line_curve_count": int(non_line),
        "num_sharp_segments": int(sharp["num_segments"]),
        "edge_valid": bool(edge_valid),
        "surface_shape": list(surface.shape),
        "edge_points_shape": list(edge_xyz.shape),
        "sharp_edges_shape": list(sharp_xyz.shape),
        "has_annotation": bool(annotation_path and Path(annotation_path).is_file()),
        "fail_reasons": [],
    }
    if primary <= 0:
        qa["fail_reasons"].append("no_primary_curves")
        qa["qa_pass"] = False
    if surface.shape != (NUM_SURFACE_POINTS, SURFACE_CHANNELS):
        qa["fail_reasons"].append("bad_surface_shape")
        qa["qa_pass"] = False
    if not edge_valid:
        qa["fail_reasons"].append("zero_sharp_edges")
        # still pass for Method B curve GT; flag only
        qa["edge_valid"] = False

    meta = {
        "experiment": EXPERIMENT,
        "sample_id": sample_id,
        "dataset": dataset,
        "ok": True,
        "qa_pass": qa["qa_pass"],
        "source_step": str(step_path),
        "source_step_sha256": _sha256(step_path),
        "tessellation": params,
        "num_surface_points": NUM_SURFACE_POINTS,
        "num_edge_points": NUM_EDGE_POINTS,
        "sharp_angle_deg": SHARP_ANGLE_DEG,
        "noise": noise_info,
        "curve_type_counts": type_counts,
        "edge_sample_stats": edge_stats,
        "normalization_source": nz.source,
        "elapsed_sec": time.time() - t0,
        # unused mesh bbox kept for debug; norm uses B-Rep bbox via nz
        "mesh_bbox_min": mn.tolist(),
        "mesh_bbox_max": mx.tolist(),
    }
    _write_json(out_dir / "qa.json", qa)
    _write_json(meta_path, meta)
    return meta
