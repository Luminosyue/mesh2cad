"""Build one sample: frozen CAD target + canonical mesh + surface + two edge GTs."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

from .constants import (
    DEFAULT_SEED,
    EDGE_CHANNELS,
    EXPERIMENT,
    NUM_EDGE_POINTS,
    NUM_SURFACE_POINTS,
    SHARP_ANGLE_DEG,
    SURFACE_CHANNELS,
)
from .edge_sample import sample_edge_cloud
from .mesh_edges import detect_sharp_edges, segment_face_pair_normals
from .occ import sharp_segment_mask, tessellate_step
from .surface import sample_surface_uniform


def _sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")


def load_frozen_transform(sample_dir: Path) -> tuple[float, np.ndarray]:
    tf_path = sample_dir / "coordinate_transform.json"
    if not tf_path.is_file():
        raise FileNotFoundError(f"missing frozen transform: {tf_path}")
    tf = json.loads(tf_path.read_text(encoding="utf-8"))
    return float(tf["scale"]), np.asarray(tf["translation"], dtype=np.float64)


def apply_canonical(points: np.ndarray, scale: float, translation: np.ndarray) -> np.ndarray:
    return np.asarray(points, dtype=np.float64) * scale + translation


def freeze_cad_target(sample_dir: Path, out_dir: Path) -> dict:
    """Copy the existing DeepCAD sequence. Never re-derive it from mesh/points."""
    dsl = sample_dir / "program_canonical.dsl"
    src_dsl = sample_dir / "program.dsl"
    source_json = sample_dir / "source.json"
    tf = sample_dir / "coordinate_transform.json"
    step = sample_dir / "model.step"
    missing = [p.name for p in (dsl, source_json, tf, step) if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"{sample_dir.name}: missing {missing}")

    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dsl, out_dir / "cad_target.dsl")
    shutil.copy2(tf, out_dir / "coordinate_transform.json")
    shutil.copy2(source_json, out_dir / "source.json")
    if src_dsl.is_file():
        shutil.copy2(src_dsl, out_dir / "program.dsl")

    return {
        "sample_id": sample_dir.name,
        "cad_target_path": str(out_dir / "cad_target.dsl"),
        "cad_target_sha256": _sha256_text(dsl),
        "program_dsl_sha256": _sha256_text(src_dsl) if src_dsl.is_file() else None,
        "source_json_sha256": _sha256_text(source_json),
        "coordinate_transform_sha256": _sha256_text(tf),
        "train_cad_target": str(dsl),
        "model_step": str(step),
        "note": "CAD sequence is copied from program_canonical.dsl; input modality must not change it.",
    }


def _pack_features(xyz: np.ndarray, normals: np.ndarray) -> np.ndarray:
    feats = np.concatenate([xyz, normals], axis=1).astype(np.float32)
    if feats.shape[1] != SURFACE_CHANNELS:
        raise ValueError(f"expected {SURFACE_CHANNELS} channels, got {feats.shape}")
    return feats


def build_one(
    sample_dir: Path,
    out_root: Path,
    *,
    num_surface: int = NUM_SURFACE_POINTS,
    num_edge: int = NUM_EDGE_POINTS,
    sharp_angle_deg: float = SHARP_ANGLE_DEG,
    seed: int = DEFAULT_SEED,
    overwrite: bool = False,
) -> dict:
    sample_dir = Path(sample_dir)
    out_dir = Path(out_root) / sample_dir.name
    meta_path = out_dir / "metadata.json"
    if meta_path.is_file() and not overwrite:
        return json.loads(meta_path.read_text(encoding="utf-8"))

    cad = freeze_cad_target(sample_dir, out_dir)
    scale, translation = load_frozen_transform(sample_dir)

    tess = tessellate_step(Path(cad["model_step"]))
    vertices, faces = tess["vertices"], tess["faces"]

    import trimesh

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.export(out_dir / "mesh.obj")
    mesh.export(out_dir / "mesh.stl")

    points, normals, face_idx = sample_surface_uniform(vertices, faces, num_surface, seed)
    surface = _pack_features(apply_canonical(points, scale, translation), normals)
    np.save(out_dir / "surface_points.npy", surface)
    np.save(out_dir / "surface_face_index.npy", face_idx)
    np.save(out_dir / "surface_points_source.npy", points.astype(np.float32))

    # --- Mesh detected sharp edges (practical pipeline) ---
    # Zero sharp is allowed: surface_valid stays True, edge_valid becomes False.
    sharp = detect_sharp_edges(
        vertices,
        faces,
        tess["face_adjacency"],
        tess["face_adjacency_edges"],
        sharp_angle_deg,
    )
    mesh_edge_valid = int(sharp["num_segments"]) > 0
    if mesh_edge_valid:
        sharp_normals = segment_face_pair_normals(vertices, faces, sharp["face_pairs"])
        det_pts, det_n, det_seg, det_stats = sample_edge_cloud(
            sharp["v0"], sharp["v1"], sharp_normals, num_edge, seed + 1
        )
        edge_detected = _pack_features(apply_canonical(det_pts, scale, translation), det_n)
        dih_min = float(sharp["dihedral_deg"].min())
        dih_max = float(sharp["dihedral_deg"].max())
    else:
        edge_detected = np.zeros((num_edge, EDGE_CHANNELS), dtype=np.float32)
        det_seg = np.full((num_edge,), -1, dtype=np.int32)
        det_stats = {
            "num_segments": 0,
            "total_length": 0.0,
            "num_points": int(num_edge),
            "points_per_segment_min": 0,
            "points_per_segment_max": 0,
            "degenerate_normal_count": int(num_edge),
            "empty_padded": True,
        }
        dih_min = None
        dih_max = None
        sharp = {
            **sharp,
            "v0": np.zeros((0, 3), dtype=np.float64),
            "v1": np.zeros((0, 3), dtype=np.float64),
            "vertex_indices": np.zeros((0, 2), dtype=np.int32),
            "dihedral_deg": np.zeros((0,), dtype=np.float64),
            "face_pairs": np.zeros((0, 2), dtype=np.int32),
            "num_segments": 0,
        }
    np.save(out_dir / "edge_points_detected.npy", edge_detected)
    np.save(out_dir / "edge_segment_index_detected.npy", det_seg)
    np.savez_compressed(
        out_dir / "mesh_sharp_edges.npz",
        v0=sharp["v0"].astype(np.float32),
        v1=sharp["v1"].astype(np.float32),
        vertex_indices=sharp["vertex_indices"],
        dihedral_deg=sharp["dihedral_deg"].astype(np.float32),
        face_pairs=sharp["face_pairs"],
    )

    # --- B-Rep GT: ALL topo edges vs SHARP structural edges (same θ_sharp) ---
    brep = tess["brep"]
    if brep["num_segments"] == 0:
        # Extremely rare: no topo edges at all. Still keep surface-valid pack.
        all_pts = np.zeros((num_edge, 3), dtype=np.float64)
        all_n = np.zeros((num_edge, 3), dtype=np.float64)
        all_seg = np.full((num_edge,), -1, dtype=np.int32)
        all_stats = {
            "num_segments": 0,
            "total_length": 0.0,
            "num_points": int(num_edge),
            "points_per_segment_min": 0,
            "points_per_segment_max": 0,
            "degenerate_normal_count": int(num_edge),
            "empty_padded": True,
        }
        edge_gt_all = np.zeros((num_edge, EDGE_CHANNELS), dtype=np.float32)
    else:
        all_pts, all_n, all_seg, all_stats = sample_edge_cloud(
            brep["v0"], brep["v1"], brep["segment_normals"], num_edge, seed + 2
        )
        edge_gt_all = _pack_features(apply_canonical(all_pts, scale, translation), all_n)
    np.save(out_dir / "edge_points_gt_all.npy", edge_gt_all)
    np.save(out_dir / "edge_segment_index_gt_all.npy", all_seg)

    keep = sharp_segment_mask(brep["segment_dihedral_deg"], sharp_angle_deg)
    n_sharp_topo = int(
        sum(1 for e in brep["edges"] if float(e["dihedral_deg"]) > float(sharp_angle_deg))
    )
    brep_edge_valid = bool(np.any(keep))
    if brep_edge_valid:
        gt_pts, gt_n, gt_seg, gt_stats = sample_edge_cloud(
            brep["v0"][keep],
            brep["v1"][keep],
            brep["segment_normals"][keep],
            num_edge,
            seed + 3,
        )
        edge_gt_sharp = _pack_features(apply_canonical(gt_pts, scale, translation), gt_n)
    else:
        edge_gt_sharp = np.zeros((num_edge, EDGE_CHANNELS), dtype=np.float32)
        gt_seg = np.full((num_edge,), -1, dtype=np.int32)
        gt_stats = {
            "num_segments": 0,
            "total_length": 0.0,
            "num_points": int(num_edge),
            "points_per_segment_min": 0,
            "points_per_segment_max": 0,
            "degenerate_normal_count": int(num_edge),
            "empty_padded": True,
        }
    np.save(out_dir / "edge_points_gt_sharp.npy", edge_gt_sharp)
    np.save(out_dir / "edge_segment_index_gt_sharp.npy", gt_seg)
    # Alias: old name must NOT mean "all TopoDS_Edge". Method-1 oracle = sharp.
    np.save(out_dir / "edge_points_gt.npy", edge_gt_sharp)
    np.save(out_dir / "edge_segment_index_gt.npy", gt_seg)

    edge_valid = bool(brep_edge_valid)  # Method-1 oracle availability
    surface_valid = True

    edge_records = []
    for e in brep["edges"]:
        rec = {k: v for k, v in e.items() if k != "polyline"}
        rec["is_sharp"] = bool(float(e["dihedral_deg"]) > float(sharp_angle_deg))
        edge_records.append(rec)

    np.savez_compressed(
        out_dir / "brep_edges.npz",
        v0=brep["v0"].astype(np.float32),
        v1=brep["v1"].astype(np.float32),
        segment_normals=brep["segment_normals"].astype(np.float32),
        segment_dihedral_deg=brep["segment_dihedral_deg"].astype(np.float32),
        sharp_mask=keep.astype(np.bool_),
        num_topo_edges=np.asarray([brep["num_topo_edges"]]),
        curve_types=np.asarray([e["curve_type"] for e in brep["edges"]]),
        lengths=np.asarray([e["length"] for e in brep["edges"]], dtype=np.float32),
        dihedral_deg=np.asarray([e["dihedral_deg"] for e in brep["edges"]], dtype=np.float32),
    )
    _write_json(
        out_dir / "brep_edges.json",
        {
            "num_topo_edges": brep["num_topo_edges"],
            "num_topo_edges_sharp": n_sharp_topo,
            "num_segments_all": brep["num_segments"],
            "num_segments_sharp": int(keep.sum()),
            "skipped_degenerate": brep["skipped_degenerate"],
            "sharp_angle_deg": float(sharp_angle_deg),
            "sharp_predicate": "dihedral_deg > sharp_angle_deg (same as mesh detected)",
            "edge_valid": edge_valid,
            "edges": edge_records,
        },
    )

    _write_json(out_dir / "tessellation.json", tess["params"])

    s_xyz = surface[:, :3]
    metadata = {
        "experiment": EXPERIMENT,
        "sample_id": sample_dir.name,
        "cad_target": cad,
        "surface_valid": surface_valid,
        "edge_valid": edge_valid,
        "mesh_edge_valid": mesh_edge_valid,
        "num_sharp_edges": int(n_sharp_topo),
        "num_sharp_segments": int(keep.sum()),
        "edge_valid": edge_valid,  # True iff sharp segments exist for Method-1 sampling
        "edge_token_fallback": ["<EDGE_START>", "<NO_EDGE>", "<EDGE_END>"] if not edge_valid else None,
        "surface_shape": list(surface.shape),
        "surface_channels": SURFACE_CHANNELS,
        "edge_channels": EDGE_CHANNELS,
        "num_surface_points": int(surface.shape[0]),
        "num_edge_points": int(num_edge),
        "surface_has_edge_score": False,
        "sharp_angle_deg": float(sharp_angle_deg),
        "sharp_predicate": "dihedral_deg > sharp_angle_deg",
        "seed": int(seed),
        "tessellation": tess["params"],
        "mesh": {
            "vertices": int(len(vertices)),
            "faces": int(len(faces)),
            "adjacency": int(len(tess["face_adjacency"])),
        },
        "mesh_sharp_edge": {
            "num_segments": int(sharp["num_segments"]),
            "dihedral_min": dih_min,
            "dihedral_max": dih_max,
            **det_stats,
        },
        "brep_gt_edge_all": {
            "num_topo_edges": brep["num_topo_edges"],
            "skipped_degenerate": brep["skipped_degenerate"],
            **all_stats,
        },
        "brep_gt_edge_sharp": {
            "num_topo_edges_sharp": n_sharp_topo,
            "num_segments_sharp": int(keep.sum()),
            "sharp_angle_deg": float(sharp_angle_deg),
            **gt_stats,
        },
        # Back-compat key: now means SHARP oracle, not all topo edges.
        "brep_gt_edge": {
            "semantics": "sharp structural B-Rep edges (alias of brep_gt_edge_sharp)",
            "num_topo_edges_all": brep["num_topo_edges"],
            "num_topo_edges_sharp": n_sharp_topo,
            "skipped_degenerate": brep["skipped_degenerate"],
            **gt_stats,
        },
        "canonical": {
            "scale": scale,
            "translation": translation.tolist(),
            "source": "train/coordinate_transform.json (frozen with CAD target)",
        },
        "surface_bbox_min": s_xyz.min(axis=0).tolist(),
        "surface_bbox_max": s_xyz.max(axis=0).tolist(),
        "files": {
            "surface": "surface_points.npy",
            "edge_gt_all": "edge_points_gt_all.npy",
            "edge_gt_sharp": "edge_points_gt_sharp.npy",
            "edge_gt": "edge_points_gt.npy (= edge_points_gt_sharp.npy alias)",
            "edge_detected": "edge_points_detected.npy",
            "cad_target": "cad_target.dsl",
            "mesh": "mesh.obj",
        },
        "ablation_inputs": {
            "baseline": "surface_points.npy",
            "edge_score": "do not use this pack; 7ch lives in train/",
            "method1_oracle": ["surface_points.npy", "edge_points_gt_sharp.npy"],
            "method1_detected": ["surface_points.npy", "edge_points_detected.npy"],
            "method1_no_edge_token": ["<EDGE_START>", "<NO_EDGE>", "<EDGE_END>"],
            "method2_curve": "later; CAD target stays cad_target.dsl",
            "audit_all_topo_edges": "edge_points_gt_all.npy",
        },
    }
    _write_json(meta_path, metadata)
    return metadata
