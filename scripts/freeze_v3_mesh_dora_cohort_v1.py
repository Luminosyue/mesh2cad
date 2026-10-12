#!/usr/bin/env python3
"""Freeze the original V3 1000-CAD Mesh+Dora cohort without model-result reads."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
V3_DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
OUT = ROOT / "ours3/dora_fitted_curve_dataset_v1"
SPLITS = {
    "train800": V3_DATA / "v3_1k_train.json",
    "decode_dev50": V3_DATA / "v3_decode_dev_50.json",
    "pilot150": V3_DATA / "v3_pilot_eval_150.json",
}
REQUIRED = (
    "model_obj", "model_step", "program_dsl", "dora_salient_edges",
    "dora_edge_points", "features_7d",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def obj_vertices(path: Path) -> np.ndarray:
    vertices = []
    with path.open(errors="ignore") as handle:
        for line in handle:
            if line.startswith("v "):
                vertices.append([float(item) for item in line.split()[1:4]])
    return np.asarray(vertices, dtype=np.float64)


def source_id(cad_id: str) -> tuple[str, str]:
    if cad_id.startswith("deepcad__"):
        return "DeepCAD", cad_id[len("deepcad__"):]
    if cad_id.startswith("fusion360__"):
        return "Fusion360", cad_id[len("fusion360__"):]
    raise ValueError(f"unknown cad_id prefix: {cad_id}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if any((OUT / name).exists() for name in (
        "V3_MESH_DORA_COHORT_V1.jsonl", "V3_MESH_DORA_COHORT_V1_FREEZE.json"
    )):
        raise RuntimeError(f"refusing to overwrite an existing freeze in {OUT}")
    records = []
    split_counts = Counter()
    dataset_counts = Counter()
    adaptive_accept = 0
    all_high_score = 0
    edge_alignment_max = 0.0
    for split, manifest_path in SPLITS.items():
        manifest = json.loads(manifest_path.read_text())
        for source_record in manifest["records"]:
            cad_id = source_record["cad_id"]
            dataset, sid = source_id(cad_id)
            cad_dir = ROOT / "cad_spatial_dataset" / dataset / "train" / sid
            paths = {
                "model_obj": cad_dir / "model.obj",
                "model_step": cad_dir / "model.step",
                "program_dsl": cad_dir / "program_canonical.dsl",
                "dora_salient_edges": cad_dir / "dora/salient_edges.npz",
                "dora_edge_points": cad_dir / "dora/edge_points.npy",
                "features_7d": cad_dir / "features_canonical.npy",
            }
            missing = [name for name, path in paths.items() if not path.is_file()]
            if missing:
                raise RuntimeError(f"{cad_id}: missing {missing}")
            topology_mesh = cad_dir / "mesh.obj"
            features = np.load(paths["features_7d"], mmap_mode="r", allow_pickle=False)
            if features.shape != (8192, 7) or not np.isfinite(features).all():
                raise RuntimeError(f"{cad_id}: bad features {features.shape}")
            all_high_score += int(bool(np.all(features[:, 6] > 0.5)))
            dora = np.load(paths["dora_salient_edges"], allow_pickle=False)
            model_vertices = obj_vertices(paths["model_obj"])
            edge_indices = np.asarray(dora["edge_vertex_indices"], dtype=np.int64)
            dora_points = np.concatenate([dora["edge_xyz0"], dora["edge_xyz1"]], axis=0)
            model_bounds = np.stack([model_vertices.min(0), model_vertices.max(0)])
            bbox_diag = float(np.linalg.norm(model_bounds[1] - model_bounds[0]))
            endpoint_outside = float(np.maximum(model_bounds[0] - dora_points, 0).max(initial=0.0))
            endpoint_outside = max(endpoint_outside, float(np.maximum(dora_points - model_bounds[1], 0).max(initial=0.0)))
            if endpoint_outside > max(1e-6 * bbox_diag, 1e-7):
                raise RuntimeError(f"{cad_id}: Dora endpoints outside model coordinate frame {endpoint_outside}")
            topology_available = topology_mesh.is_file()
            max_err = 0.0
            if topology_available:
                topology_vertices = obj_vertices(topology_mesh)
                if edge_indices.size and (edge_indices.min() < 0 or edge_indices.max() >= len(topology_vertices)):
                    raise RuntimeError(f"{cad_id}: Dora edge index outside Dora topology mesh")
                err = np.concatenate([
                    np.linalg.norm(topology_vertices[edge_indices[:, 0]] - dora["edge_xyz0"], axis=1),
                    np.linalg.norm(topology_vertices[edge_indices[:, 1]] - dora["edge_xyz1"], axis=1),
                ])
                max_err = float(err.max())
                diag = float(np.linalg.norm(topology_vertices.max(0) - topology_vertices.min(0)))
                if max_err > max(1e-6 * diag, 1e-7):
                    raise RuntimeError(f"{cad_id}: Dora/topology vertex mismatch {max_err}")
                edge_alignment_max = max(edge_alignment_max, max_err)
                topology_bounds = np.stack([topology_vertices.min(0), topology_vertices.max(0)])
                bbox_err = float(np.max(np.abs(model_bounds - topology_bounds)))
            else:
                bbox_err = None
            meta_path = cad_dir / "meta.json"
            adaptive = {}
            if meta_path.is_file():
                adaptive = json.loads(meta_path.read_text()).get("spatial", {}).get("adaptive", {})
                adaptive_accept += int(bool(adaptive.get("accepted", False)))
            record = {
                "cad_id": cad_id,
                "source_id": sid,
                "dataset": dataset,
                "split": split,
                "assets": {
                    name: {"path": str(path), "sha256": sha256(path), "size": path.stat().st_size}
                    for name, path in paths.items()
                },
                "features_shape": list(features.shape),
                "dora_mesh_edges": int(len(edge_indices)),
                "dora_topology_mesh": (
                    {"path": str(topology_mesh), "sha256": sha256(topology_mesh)} if topology_available else None
                ),
                "dora_topology_vertex_max_error": max_err,
                "dora_endpoint_model_bbox_outside_error": endpoint_outside,
                "model_dora_mesh_bbox_max_error": bbox_err,
                "adaptive_accepted": bool(adaptive.get("accepted", False)),
            }
            records.append(record)
            split_counts[split] += 1
            dataset_counts[dataset] += 1

    if len(records) != 1000 or split_counts != Counter({"train800": 800, "decode_dev50": 50, "pilot150": 150}):
        raise RuntimeError(f"cohort count mismatch: {len(records)} {split_counts}")
    if len({row["cad_id"] for row in records}) != 1000:
        raise RuntimeError("duplicate CAD IDs in V3 cohort")

    cohort = OUT / "V3_MESH_DORA_COHORT_V1.jsonl"
    with cohort.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    builder = ROOT / "scripts/build_cad_spatial_part.py"
    review = {
        "CURRENT_STATUS": "DORA_DISTRIBUTION_REVIEW_REQUIRED",
        "SURFACE_7CH_REVIEW_REQUIRED": True,
        "EDGE_SCORE_ALL_GT_0_5_CAD_COUNT": all_high_score,
        "ADAPTIVE_ACCEPTED_COUNT": adaptive_accept,
        "COHORT_COUNT": 1000,
        "SALIENT_GEOMETRY_HARD_FAIL": False,
        "CONFIRMATION": (
            "adaptive.accepted is metadata only; salient edge geometry is persisted from "
            "edge_idx/v0/v1. Sigma controls edge_score values and acceptance diagnostics; "
            "there is no branch that discards or rewrites salient_edges.npz based on accepted."
        ),
        "BUILDER_PATH": str(builder),
        "BUILDER_SHA256": sha256(builder),
        "EVIDENCE_LINES": {
            "adaptive_result_unpack": "1047-1054",
            "salient_geometry_write": "1056-1065",
            "edge_score_write": "1087-1091",
        },
    }
    write_json(OUT / "DORA_EDGE_SCORE_REVIEW.json", review)
    freeze = {
        "CURRENT_GATE": "V3_MESH_DORA_COHORT_V1_FREEZE_PASS",
        "V3_COHORT_MAPPING": "PASS",
        "REQUIRED_ASSET_COVERAGE": "1000/1000",
        "FEATURE_8192X7_SCHEMA": "PASS",
        "DORA_POINT_EDGE_ALIGNMENT": "PASS",
        "DORA_TOPOLOGY_VERTEX_MAX_ERROR": edge_alignment_max,
        "DORA_VERTEX_INDEX_CONTRACT": "graph uses edge_vertex_indices plus NPZ endpoint coordinates; optional dora_topology_mesh validates indices when retained",
        "COUNTS_BY_SPLIT": dict(split_counts),
        "COUNTS_BY_DATASET": dict(dataset_counts),
        "COHORT_JSONL": str(cohort),
        "COHORT_SHA256": sha256(cohort),
        "PILOT150_METADATA_ONLY_READ": True,
        "DECODE_DEV50_MODEL_RESULTS_READ": False,
        "PILOT150_MODEL_RESULTS_READ": False,
        "ANCHOR_EVAL100_READ": False,
        "OFFICIAL_TEST_READ": False,
        "TRAINING_STARTED": False,
    }
    write_json(OUT / "V3_MESH_DORA_COHORT_V1_FREEZE.json", freeze)
    manifest = {}
    for path in sorted(OUT.iterdir()):
        if path.is_file():
            manifest[path.name] = {"size": path.stat().st_size, "sha256": sha256(path)}
    write_json(OUT / "FILE_SHA256_MANIFEST.json", manifest)
    print(json.dumps(freeze, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
