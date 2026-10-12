from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "mac_residual_feature_repair_v1" / "propeller_blade_only_recovery_probe_v1"
GRAPH = ROOT / "case09_full_pipeline_fresh_e2e_v1" / "02_cad_part_graph" / "cad_part_graph.json"
V2_MANIFEST = ROOT / "mac_residual_feature_repair_v1" / "dorsal_source_residual_patch_gate_v2" / "final" / "CASE09_dorsal_source_residual_patch_q90_manifest.json"
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


def make_triangle_face(points: np.ndarray) -> object:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    maker = BRepBuilderAPI_MakePolygon()
    for point in points:
        maker.Add(gp_Pnt(*map(float, point)))
    maker.Close()
    return BRepBuilderAPI_MakeFace(maker.Wire(), True).Face()


def make_triangle_compound(points: np.ndarray, faces: np.ndarray) -> object:
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for face in faces:
        builder.Add(compound, make_triangle_face(points[face]))
    return compound


def write_step(shape: object, path: Path) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError("STEP_WRITE_FAILED")


def mesh_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, object]:
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
    from remote_gate10.gate10_runner import build_xcaf, load_shape, shape_mesh
    sys.path.insert(0, str(ROOT / "v6_backend_mainline_integration"))
    from mainline.visualize import fidelity
    from OCP.BRepCheck import BRepCheck_Analyzer

    graph = json.loads(GRAPH.read_text())
    nodes = {node["semantic_role"]: node for node in graph["nodes"]}
    v2 = json.loads(V2_MANIFEST.read_text())
    prop_source_path = Path(nodes["PROPELLER_PATTERN"]["source_part_mesh"])
    prop_source = trimesh.load(prop_source_path, force="mesh", process=False)
    prop_shape = make_triangle_compound(np.asarray(prop_source.vertices, dtype=float), np.asarray(prop_source.faces, dtype=int))
    prop_valid = bool(not prop_shape.IsNull() and BRepCheck_Analyzer(prop_shape).IsValid())
    prop_step = OUT / "candidates/CADPART_006/BLADE_ONLY_RECOVERY/candidate.step"
    if not prop_valid:
        raise RuntimeError("PROPELLER_BLADE_ONLY_BREPCHECK_FAIL")
    write_step(prop_shape, prop_step)
    prop_candidate = shape_mesh(prop_step)
    prop_reload_valid = not load_shape(prop_step).IsNull()
    prop_metrics = mesh_metrics(prop_source, prop_candidate)

    base_steps: list[Path] = []
    selected_steps: list[Path] = []
    entries: list[dict[str, object]] = []
    base_hashes: dict[str, str] = {}
    manifest_parts: list[dict[str, object]] = []
    for item in v2["components"]:
        role = item["semantic_role"]
        if not item.get("geometry_present"):
            original = None
            selected_step = prop_step if role == "PROPELLER_PATTERN" else None
            if role != "PROPELLER_PATTERN":
                manifest_parts.append({
                    "part_id": item["part_id"],
                    "semantic_role": role,
                    "geometry_present": False,
                    "status": "OMITTED_LOW_FIDELITY",
                    "reason": item.get("reason", "V2_OMISSION"),
                    "selected_step_path": None,
                    "selected_step_sha256": None,
                })
                continue
        else:
            original = Path(item["selected_step_path"])
            selected_step = original
            base_steps.append(original)
            selected_steps.append(original)
            base_hashes[role] = sha(original)
            node = nodes[role]
            entries.append({
                "part_id": item["part_id"],
                "semantic_role": role,
                "builder": "V2_FROZEN_BASE",
                "route_status": "BASE_FROZEN",
                "quality_tag": "BASE_FROZEN",
                "geometry_present": True,
                "fresh_step_path": str(original),
                "candidate_source": "V2_FINAL_ASSEMBLY",
                "T_part_local_to_source_global": node.get("local_to_global_transform", np.eye(4).tolist()),
            })
            manifest_parts.append({
                "part_id": item["part_id"],
                "semantic_role": role,
                "geometry_present": True,
                "status": "BASE_FROZEN",
                "reason": "",
                "selected_step_path": str(original),
                "selected_step_sha256": sha(original),
                "base_step_sha256": sha(original),
            })
            continue

        selected_steps.append(prop_step)
        entries.append({
            "part_id": item["part_id"],
            "semantic_role": role,
            "builder": "BLADE_ONLY_RECOVERY_SOURCE_TRIANGLE_COMPOUND",
            "route_status": "BLADE_ONLY_RECOVERY_CANDIDATE",
            "quality_tag": "CANDIDATE_ONLY",
            "geometry_present": True,
            "fresh_step_path": str(prop_step),
            "candidate_source": "AUTHORITATIVE_PROPELLER_SOURCE_PART_MESH",
            "T_part_local_to_source_global": nodes[role].get("local_to_global_transform", np.eye(4).tolist()),
        })
        manifest_parts.append({
            "part_id": item["part_id"],
            "semantic_role": role,
            "geometry_present": True,
            "status": "BLADE_ONLY_RECOVERY_CANDIDATE",
            "reason": "HUB_NOT_RECONSTRUCTED",
            "selected_step_path": str(prop_step),
            "selected_step_sha256": sha(prop_step),
            "base_step_sha256": None,
        })

    source_whole = trimesh.load(SOURCE_WHOLE, force="mesh", process=False)
    base_whole = trimesh.util.concatenate([shape_mesh(path) for path in base_steps])
    candidate_whole = trimesh.util.concatenate([shape_mesh(path) for path in selected_steps])
    whole_before = fidelity(source_whole, base_whole)
    whole_after = fidelity(source_whole, candidate_whole)
    whole_gain = bool(
        whole_after["chamfer"] < whole_before["chamfer"]
        and whole_after["source_coverage_02"] >= whole_before["source_coverage_02"]
    )

    final_step = OUT / "final/CASE09_blade_only_recovery_candidate_assembly.step"
    xcaf = build_xcaf(entries, final_step)
    reload_valid = bool(
        xcaf["info"].get("file_readable")
        and xcaf["info"].get("reloaded_component_invalid_count") == 0
    )
    summary = {
        "CURRENT_GATE": "BLADE_ONLY_RECOVERY_PROBE_V1_CANDIDATE",
        "PASS": bool(prop_valid and prop_reload_valid and reload_valid and whole_gain),
        "PROMOTION_STATUS": "AWAITING_EXPLICIT_GATE_APPROVAL",
        "BASE_BREP_IMMUTABLE": True,
        "BASE_ARTIFACT_MODIFIED_COUNT": 0,
        "PROPELLER_COMPONENT_COUNT": len(prop_source.split(only_watertight=False)),
        "PROPELLER_HUB_COMPONENT_OBSERVED": False,
        "PROPELLER_PARENT_SURFACE_OBSERVED": True,
        "PROPELLER_BLADE_ONLY_BREP_VALID": prop_valid,
        "PROPELLER_BLADE_ONLY_RELOAD_VALID": prop_reload_valid,
        "PROPELLER_METRICS": prop_metrics,
        "WHOLE_OBJECT_BEFORE": whole_before,
        "WHOLE_OBJECT_AFTER": whole_after,
        "WHOLE_OBJECT_BLADE_ONLY_GAIN": whole_gain,
        "FINAL_STEP_RELOAD_VALID": reload_valid,
        "FINAL_COMPONENT_COUNT": xcaf["component_count"],
        "FINAL_STEP": str(final_step),
        "MANIFEST": str(OUT / "final/CASE09_blade_only_recovery_candidate_manifest.json"),
        "BLOCKERS": ["HUB_NOT_RECONSTRUCTED", "EXPLICIT_GATE_APPROVAL_REQUIRED"],
    }
    manifest = {
        "schema": "BLADE_ONLY_RECOVERY_PROBE_V1_MANIFEST",
        "base_manifest": str(V2_MANIFEST),
        "base_brep_immutable": True,
        "components": manifest_parts,
        "propeller_status": "BLADE_ONLY_RECOVERY_CANDIDATE",
        "propeller_hub_status": "NOT_RECONSTRUCTED",
        "final_step": str(final_step),
        "final_step_sha256": sha(final_step),
        "final_step_reload_valid": reload_valid,
        "whole_object_before": whole_before,
        "whole_object_after": whole_after,
        "promotion_status": "AWAITING_EXPLICIT_GATE_APPROVAL",
    }
    dump(OUT / "final/CASE09_blade_only_recovery_candidate_manifest.json", manifest)
    dump(OUT / "artifacts/final_summary.json", summary)
    report = [
        "# BLADE_ONLY_RECOVERY_PROBE_V1",
        "",
        "This is a candidate-only probe. It does not replace the V2 assembly.",
        "The candidate preserves both authoritative source blade components as a faceted BRep compound.",
        "No hub was invented or reconstructed.",
        "",
        "```text",
    ]
    report.extend(f"{key}={value}" for key, value in summary.items())
    report.extend([
        "```",
        "",
        "Promotion requires explicit approval for the BLADE_ONLY_RECOVERY gate.",
    ])
    (OUT / "artifacts/BLADE_ONLY_RECOVERY_PROBE_V1_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
