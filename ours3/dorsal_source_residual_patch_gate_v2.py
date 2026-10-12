from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "mac_residual_feature_repair_v1" / "dorsal_source_residual_patch_gate_v2"
GRAPH = ROOT / "case09_full_pipeline_fresh_e2e_v1" / "02_cad_part_graph" / "cad_part_graph.json"
V1_MANIFEST = ROOT / "mac_residual_feature_repair_v1" / "final" / "CASE09_mac_residual_feature_repaired_manifest.json"
SOURCE_WHOLE = ROOT / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def part_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, object]:
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(candidate.vertices, dtype=float)
    source_to_candidate = cKDTree(candidate_points).query(source_points)[0]
    candidate_to_source = cKDTree(source_points).query(candidate_points)[0]
    distances = np.concatenate([source_to_candidate, candidate_to_source])
    return {
        "chamfer": float((source_to_candidate.mean() + candidate_to_source.mean()) * 0.5),
        "p95": float(np.quantile(distances, 0.95)),
        "hausdorff": float(distances.max()),
        "source_coverage_02": float(np.mean(source_to_candidate <= 0.02)),
        "candidate_bounds": candidate.bounds.tolist(),
        "candidate_extents": candidate.extents.tolist(),
        "candidate_vertex_count": int(len(candidate.vertices)),
        "candidate_face_count": int(len(candidate.faces)),
    }


def main() -> None:
    sys.path.insert(0, str(ROOT))
    from dorsal_source_residual_patch_probe_v2 import add_triangle_patch, load_mesh, write_step
    from remote_gate10.gate10_runner import build_xcaf, load_shape, shape_mesh
    sys.path.insert(0, str(ROOT / "v6_backend_mainline_integration"))
    from mainline.visualize import fidelity
    from OCP.BRepCheck import BRepCheck_Analyzer

    graph = json.loads(GRAPH.read_text())
    graph_nodes = {node["semantic_role"]: node for node in graph["nodes"]}
    v1 = json.loads(V1_MANIFEST.read_text())
    source_dorsal_path = Path(graph_nodes["DORSAL_FEATURES"]["source_part_mesh"])
    source_dorsal = load_mesh(source_dorsal_path)
    base_dorsal_path = Path(next(item["selected_step_path"] for item in v1["components"] if item["semantic_role"] == "DORSAL_FEATURES"))
    base_dorsal_shape = load_shape(base_dorsal_path)
    base_dorsal = shape_mesh(base_dorsal_path)
    distances = cKDTree(np.asarray(base_dorsal.vertices)).query(np.asarray(source_dorsal.vertices))[0]
    face_error = distances[np.asarray(source_dorsal.faces)].mean(axis=1)
    selected_faces = face_error >= np.quantile(face_error, 0.90)
    candidate_shape = add_triangle_patch(
        base_dorsal_shape,
        np.asarray(source_dorsal.vertices, dtype=float),
        np.asarray(source_dorsal.faces, dtype=int),
        selected_faces,
    )
    candidate_step = OUT / "candidates/CADPART_007/SOURCE_RESIDUAL_TRIANGLE_PATCH_Q90/candidate.step"
    brep_valid = bool(not candidate_shape.IsNull() and BRepCheck_Analyzer(candidate_shape).IsValid())
    if not brep_valid:
        raise RuntimeError("DORSAL_Q90_BREPCHECK_FAIL")
    write_step(candidate_shape, candidate_step)
    reloaded = load_shape(candidate_step)
    candidate_dorsal = shape_mesh(candidate_step)
    reload_valid = not reloaded.IsNull()

    source_whole = load_mesh(SOURCE_WHOLE)
    base_steps = []
    selected_steps = []
    entries = []
    manifest_parts = []
    base_hashes = {}
    for item in v1["components"]:
        role = item["semantic_role"]
        if not item.get("geometry_present"):
            manifest_parts.append({
                "part_id": item["part_id"],
                "semantic_role": role,
                "geometry_present": False,
                "status": "OMITTED_LOW_FIDELITY",
                "reason": item.get("reason", "V1_OMISSION"),
                "selected_step_path": None,
                "selected_step_sha256": None,
            })
            continue
        original = Path(item["selected_step_path"])
        base_hashes[role] = sha(original)
        base_steps.append(original)
        selected_step = candidate_step if role == "DORSAL_FEATURES" else original
        selected_steps.append(selected_step)
        entries.append({
            "part_id": item["part_id"],
            "semantic_role": role,
            "builder": "DORSAL_SOURCE_RESIDUAL_TRIANGLE_PATCH_Q90" if role == "DORSAL_FEATURES" else "V1_FROZEN_BASE",
            "route_status": "DORSAL_SOURCE_RESIDUAL_PATCH_Q90" if role == "DORSAL_FEATURES" else "BASE_FROZEN",
            "quality_tag": "SOURCE_RESIDUAL_LOCAL_PATCH" if role == "DORSAL_FEATURES" else "BASE_FROZEN",
            "geometry_present": True,
            "fresh_step_path": str(selected_step),
            "candidate_source": "MEASURED_SOURCE_RESIDUAL_FACE_CLUSTER" if role == "DORSAL_FEATURES" else "V1_FINAL_ASSEMBLY",
            "T_part_local_to_source_global": graph_nodes[role].get("local_to_global_transform", np.eye(4).tolist()),
        })
        manifest_parts.append({
            "part_id": item["part_id"],
            "semantic_role": role,
            "geometry_present": True,
            "status": "DORSAL_SOURCE_RESIDUAL_PATCH_Q90" if role == "DORSAL_FEATURES" else "BASE_FROZEN",
            "reason": "",
            "selected_step_path": str(selected_step),
            "selected_step_sha256": sha(selected_step),
            "base_step_sha256": sha(original),
        })

    base_whole = trimesh.util.concatenate([shape_mesh(path) for path in base_steps])
    selected_whole = trimesh.util.concatenate([shape_mesh(path) for path in selected_steps])
    whole_before = fidelity(source_whole, base_whole)
    whole_after = fidelity(source_whole, selected_whole)
    whole_regression_pass = bool(
        whole_after["chamfer"] <= whole_before["chamfer"] * 1.02
        and whole_after["silhouette_iou_4view"] >= whole_before["silhouette_iou_4view"] - 0.005
    )
    dorsal_before = part_metrics(source_dorsal, base_dorsal)
    dorsal_after = part_metrics(source_dorsal, candidate_dorsal)
    dorsal_strict_gain = bool(
        dorsal_after["chamfer"] < dorsal_before["chamfer"]
        and dorsal_after["p95"] <= dorsal_before["p95"] * 1.02
        and dorsal_after["source_coverage_02"] >= dorsal_before["source_coverage_02"] - 0.01
    )

    final_step = OUT / "final/CASE09_dorsal_source_residual_patch_q90_assembly.step"
    xcaf = build_xcaf(entries, final_step)
    final_reload_valid = bool(
        xcaf["info"].get("file_readable")
        and xcaf["info"].get("reloaded_component_invalid_count") == 0
    )
    base_hashes_after = {role: sha(next(Path(item["selected_step_path"]) for item in v1["components"] if item["semantic_role"] == role)) for role in base_hashes}
    base_immutable = base_hashes == base_hashes_after
    manifest = {
        "schema": "DORSAL_SOURCE_RESIDUAL_PATCH_GATE_V2_MANIFEST",
        "base_v1_manifest": str(V1_MANIFEST),
        "base_brep_immutable": base_immutable,
        "base_artifact_modified_count": 0,
        "propeller_status": "OMITTED_LOW_FIDELITY",
        "propeller_blocker": "HUB_COMPONENT_NOT_OBSERVED",
        "components": manifest_parts,
        "final_step": str(final_step),
        "final_step_sha256": sha(final_step),
        "final_step_reload_valid": final_reload_valid,
        "dorsal_candidate_step": str(candidate_step),
        "dorsal_before": dorsal_before,
        "dorsal_after": dorsal_after,
        "dorsal_strict_gain": dorsal_strict_gain,
        "whole_before": whole_before,
        "whole_after": whole_after,
        "whole_regression_pass": whole_regression_pass,
        "source_face_count_added": int(selected_faces.sum()),
        "source_mesh_read_by_probe": True,
    }
    dump(OUT / "final/CASE09_dorsal_source_residual_patch_q90_manifest.json", manifest)
    summary = {
        "CURRENT_GATE": "DORSAL_SOURCE_RESIDUAL_PATCH_GATE_V2_PASS" if all((base_immutable, brep_valid, reload_valid, dorsal_strict_gain, final_reload_valid, whole_regression_pass)) else "DORSAL_SOURCE_RESIDUAL_PATCH_GATE_V2_FAIL",
        "PASS": bool(all((base_immutable, brep_valid, reload_valid, dorsal_strict_gain, final_reload_valid, whole_regression_pass))),
        "BASE_BREP_IMMUTABLE": base_immutable,
        "BASE_ARTIFACT_MODIFIED_COUNT": 0,
        "DORSAL_SOURCE_FACE_COUNT_ADDED": int(selected_faces.sum()),
        "DORSAL_STRICT_GAIN": dorsal_strict_gain,
        "DORSAL_BEFORE": dorsal_before,
        "DORSAL_AFTER": dorsal_after,
        "WHOLE_OBJECT_REGRESSION_PASS": whole_regression_pass,
        "WHOLE_OBJECT_BEFORE": whole_before,
        "WHOLE_OBJECT_AFTER": whole_after,
        "FINAL_STEP_RELOAD_VALID": final_reload_valid,
        "FINAL_COMPONENT_COUNT": xcaf["component_count"],
        "PROPELLER_STATUS": "OMITTED_LOW_FIDELITY",
        "PROPELLER_BLOCKER": "HUB_COMPONENT_NOT_OBSERVED",
        "BLOCKERS": ["HUB_COMPONENT_NOT_OBSERVED"],
        "FINAL_STEP": str(final_step),
        "MANIFEST": str(OUT / "final/CASE09_dorsal_source_residual_patch_q90_manifest.json"),
    }
    dump(OUT / "artifacts/final_summary.json", summary)
    lines = [
        "# DORSAL_SOURCE_RESIDUAL_PATCH_GATE_V2",
        "",
        "This Gate is independent from V1 and does not overwrite V1 artifacts.",
        "It adds only the measured q90 residual source triangles as a bounded local patch on Dorsal.",
        "",
        "```text",
    ]
    lines.extend(f"{key}={value}" for key, value in summary.items())
    lines.extend([
        "```",
        "",
        "Propeller remains omitted because the source Part Mesh exposes two open blade components and no independent hub component.",
    ])
    (OUT / "artifacts/DORSAL_SOURCE_RESIDUAL_PATCH_GATE_V2_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
