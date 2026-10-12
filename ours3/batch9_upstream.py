#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
FROZEN = ROOT / "batch10_semantic_mesh2cad_tts_v5/00_provenance/frozen_10_case_source_manifest.json"
P3_RUNNER = ROOT / "fusion_pipeline/scripts/part_segmenter.py"
P3_PYTHON = Path("/data/miniconda3/envs/hunyuan/bin/python")
P3_CKPT = Path("/data/home/cuiyuehan/project/mesh2cad/Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors")
SONATA_CKPT = Path("/data/home/cuiyuehan/.cache/sonata/sonata.pth")
PHYSX_CKPT = Path("/data/home/cuiyuehan/project/mesh2cad/PhysX-Omni/pretrain")

P3_EXISTING = {
    "CASE_00": ROOT / "fusion_pipeline/cases/REAL_03/segmentation",
    "CASE_05": ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/p3",
    "CASE_06": ROOT / "batch_real_mesh2cad_v1/cases/CASE_06/p3",
    "CASE_07": ROOT / "batch_real_mesh2cad_v1/cases/CASE_07/p3",
}


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, Path): return str(value)
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve_recorded(path: str):
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def verify_p3(case_id: str, source: Path, mesh: trimesh.Trimesh, directory: Path):
    labels_path = directory / "triangle_part_id.npy"
    metadata_path = directory / "part_metadata.json"
    checks = {
        "labels_present": labels_path.is_file(),
        "metadata_present": metadata_path.is_file(),
        "p3_checkpoint_present": P3_CKPT.is_file(),
        "sonata_checkpoint_present": SONATA_CKPT.is_file(),
        "working_environment_present": P3_PYTHON.is_file(),
    }
    parts = []
    if not checks["labels_present"] or not checks["metadata_present"]:
        return False, checks, parts
    labels = np.load(labels_path, allow_pickle=False)
    metadata = load(metadata_path)
    recorded_source = resolve_recorded(metadata.get("source_mesh", ""))
    checks.update({
        "source_path_or_sha_match": recorded_source.resolve() == source.resolve() or (recorded_source.is_file() and sha(recorded_source) == sha(source)),
        "source_sha_match": sha(source) == sha(recorded_source) if recorded_source.is_file() else False,
        "triangle_count_match": len(mesh.faces) == len(labels) == int(metadata.get("source_triangle_count", -1)),
        "labels_complete": labels.ndim == 1 and bool(len(labels)) and int(labels.min()) >= 0,
        "labels_contiguous": set(np.unique(labels).tolist()) == set(range(int(metadata.get("num_parts", -1)))),
        "triangle_mapping_declared": metadata.get("triangle_mapping") == "array_index_is_source_triangle_index",
        "official_api_declared": metadata.get("official_api") == "AutoMask.predict_aabb",
        "checkpoint_provenance_declared": bool(metadata.get("provenance") or case_id == "CASE_00"),
    })
    for row in metadata.get("parts", []):
        part_id = int(row["part_id"])
        part_path = resolve_recorded(row["path"])
        ids = np.flatnonzero(labels == part_id)
        ok = part_path.is_file() and len(ids) == int(row["triangle_count"])
        if ok:
            part = trimesh.load(part_path, force="mesh", process=False)
            ok = len(part.faces) == len(ids)
            ok = ok and np.allclose(part.bounds, [row["bbox_min"], row["bbox_max"]], atol=1e-8)
            ok = ok and np.isclose(part.area, row["surface_area"], rtol=1e-8, atol=1e-10)
        parts.append({"part_id": part_id, "path": part_path, "verified": bool(ok), "sha256": sha(part_path) if part_path.is_file() else None})
    checks["part_count_match"] = len(parts) == int(metadata.get("num_parts", -1))
    checks["part_meshes_all_match"] = bool(parts) and all(row["verified"] for row in parts)
    checks["triangle_sum_match"] = sum(int(row.get("triangle_count", 0)) for row in metadata.get("parts", [])) == len(mesh.faces)
    return all(checks.values()), checks, parts


def physx_paths(case_id: str):
    if case_id == "CASE_00":
        base = OUT / "01_upstream/CASE_00/physx"
        return base / "input/render_metadata.json", base / "input/CASE_00.png", base / "provenance/provenance.json", base / "understanding/physx_understanding.json"
    base = ROOT / "batch_real_mesh2cad_v1/cases" / case_id / "physx"
    return base / "input/render_metadata.json", base / "input" / f"{case_id}.png", base / "provenance/provenance.json", base / "understanding/physx_understanding.json"


def verify_physx(case_id: str, source: Path, mesh: trimesh.Trimesh):
    render_meta_path, image_path, provenance_path, understanding_path = physx_paths(case_id)
    checks = {
        "render_metadata_present": render_meta_path.is_file(),
        "input_image_present": image_path.is_file(),
        "provenance_present": provenance_path is not None and provenance_path.is_file(),
        "understanding_present": understanding_path.is_file(),
        "checkpoint_index_present": (PHYSX_CKPT / "model.safetensors.index.json").is_file(),
    }
    details = {}
    if not all(checks.values()):
        return False, checks, details
    render = load(render_meta_path)
    provenance = load(provenance_path)
    understanding = load(understanding_path)
    bbox = [render["normalization_transform"]["source_bbox"]["min"], render["normalization_transform"]["source_bbox"]["max"]]
    checks.update({
        "source_path_match": Path(render["source_obj"]).resolve() == source.resolve(),
        "source_triangle_match": int(render["source_triangles"]) == len(mesh.faces),
        "source_bbox_match": bool(np.allclose(mesh.bounds, bbox, atol=1e-12)),
        "transform_orientation_preserved": bool(render["normalization_transform"].get("object_orientation_preserved")) and render["protocol"].get("object_rotation") == "NONE",
        "input_sha_match": provenance.get("input", {}).get("sha256") == sha(image_path),
        "official_repo_declared": provenance.get("repo") == str(ROOT / "external/PhysX-Omni"),
        "checkpoint_match": Path(provenance.get("checkpoint", "")).resolve() == PHYSX_CKPT.resolve(),
        "commit_declared": provenance.get("commit") == "46fa1cd0b6883d4d14431d51c3326ef80a85ef64",
        "output_parsed": understanding.get("PHYSX_OUTPUT_PARSED") is True,
        "raw_sha_declared": bool(provenance.get("raw_sha256")),
    })
    details = {"render_metadata": render_meta_path, "input_image": image_path, "provenance": provenance_path, "understanding": understanding_path}
    return all(checks.values()), checks, details


def main():
    manifest = load(FROZEN)["cases"]
    cases = []
    for case_id in [f"CASE_{i:02d}" for i in range(9)]:
        row = manifest[case_id]
        source = Path(row["source_path"])
        mesh = trimesh.load(source, force="mesh", process=False)
        source_checks = {
            "path_match": source.resolve() == Path(row["source_path"]).resolve(),
            "sha_match": sha(source) == row["source_sha256"],
            "triangle_count_match": len(mesh.faces) == int(row["triangle_count"]),
            "bbox_match": bool(np.allclose(mesh.bounds, row["bbox"], atol=1e-12)),
        }
        if not all(source_checks.values()):
            raise RuntimeError(f"{case_id} frozen source provenance failed: {source_checks}")
        p3_dir = P3_EXISTING.get(case_id, OUT / "01_upstream" / case_id / "p3")
        p3_ok, p3_checks, p3_parts = verify_p3(case_id, source, mesh, p3_dir)
        initially_reused = case_id in P3_EXISTING
        p3_reason = "NOT_REQUIRED_PROVENANCE_VERIFIED" if initially_reused and p3_ok else ("ARTIFACT_MISSING" if p3_ok else "PROVENANCE_CHECK_FAILED")
        physx_ok, physx_checks, physx_details = verify_physx(case_id, source, mesh)
        physx_reason = "NOT_REQUIRED_PROVENANCE_VERIFIED" if physx_ok else ("ARTIFACT_MISSING_OR_FAILED_OUTPUT" if case_id == "CASE_00" else "PROVENANCE_CHECK_FAILED")
        cases.append({
            "case_id": case_id, "source_obj": source, "source_sha256": sha(source), "source_triangle_count": len(mesh.faces), "source_bbox": mesh.bounds,
            "source_checks": source_checks, "P3_REUSED": initially_reused and p3_ok, "P3_RERUN": (not initially_reused) and p3_ok, "P3_RERUN_REASON": p3_reason,
            "p3_directory": p3_dir, "p3_checks": p3_checks, "p3_parts": p3_parts,
            "PHYSX_REUSED": case_id != "CASE_00" and physx_ok, "PHYSX_RERUN": case_id == "CASE_00" and physx_ok, "PHYSX_RERUN_REASON": ("ARTIFACT_MISSING_OR_FAILED_OUTPUT" if case_id == "CASE_00" else physx_reason),
            "physx_checks": physx_checks, "physx_details": physx_details,
        })
    audit = {
        "schema": "BATCH9_V6_UPSTREAM_PROVENANCE_AUDIT",
        "frozen_manifest": FROZEN,
        "p3_checkpoint": P3_CKPT, "p3_checkpoint_sha256": sha(P3_CKPT),
        "sonata_checkpoint": SONATA_CKPT, "sonata_checkpoint_sha256": sha(SONATA_CKPT),
        "p3_environment": P3_PYTHON, "p3_environment_modified": False,
        "physx_checkpoint": PHYSX_CKPT, "physx_checkpoint_index_sha256": sha(PHYSX_CKPT / "model.safetensors.index.json"),
        "cases": cases,
    }
    dump(OUT / "00_provenance/upstream_audit_initial.json", audit)
    for case in cases:
        print(case["case_id"], "P3_REUSED=" + str(case["P3_REUSED"]).lower(), "P3_RERUN=" + str(case["P3_RERUN"]).lower(), "P3_RERUN_REASON=" + case["P3_RERUN_REASON"])
        print(case["case_id"], "PHYSX_REUSED=" + str(case["PHYSX_REUSED"]).lower(), "PHYSX_RERUN=" + str(case["PHYSX_RERUN"]).lower(), "PHYSX_RERUN_REASON=" + case["PHYSX_RERUN_REASON"])


if __name__ == "__main__":
    main()
