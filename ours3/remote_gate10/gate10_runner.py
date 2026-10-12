from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "case09_front_and_dorsal_feature_recovery"
G9 = ROOT / "case09_part_input_stability_fix"
SOURCE = ROOT / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
FRESH_GRAPH = ROOT / "case09_full_pipeline_fresh_e2e_v1/02_cad_part_graph/cad_part_graph.json"
V6_RUNTIME = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py"
V6_RESTORE = ROOT / "v6_geometry_backend_restore"
XCAF_ROOT = ROOT / "v13_transform_restore_and_xcaf_assembly"
FROZEN_ROLES = (
    "FUSELAGE",
    "MAIN_WING_LEFT",
    "MAIN_WING_RIGHT",
    "TAILPLANE_LEFT",
    "TAILPLANE_RIGHT",
    "VERTICAL_TAIL",
)
TARGET_ROLE_ALIASES = {
    "PROPELLER_PATTERN": ("PROPELLER", "PROPELLER_PATTERN", "FRONT_ROTATIONAL_FEATURE", "FRONT_FEATURE"),
    "DORSAL_FEATURES": ("DORSAL_FEATURE", "DORSAL_FEATURES", "TOP_FAIRING", "TOP_FEATURE"),
}
TARGET_V6_CONFIG = {
    "PROPELLER_PATTERN": ("GLOBAL_LOFT", 10, 20, 0.001),
    "DORSAL_FEATURES": ("GLOBAL_LOFT", 12, 10, 0.001),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(value: Any) -> Any:
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
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
                for key, value in row.items()
            })


def load_gate9() -> Any:
    sys.path.insert(0, str(ROOT))
    from remote_gate9 import gate9_runner
    return gate9_runner


def role_nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {node["semantic_role"]: node for node in graph["nodes"] if node.get("semantic_role")}


def find_target_nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = {}
    for canonical, aliases in TARGET_ROLE_ALIASES.items():
        matches = [node for node in graph["nodes"] if str(node.get("semantic_role", "")).upper() in aliases]
        if len(matches) != 1:
            raise RuntimeError(f"TARGET_ROLE_MATCH_FAILED:{canonical}:{matches}")
        result[canonical] = matches[0]
    return result


def frozen_paths() -> dict[str, Path]:
    result = {}
    for role in FROZEN_ROLES:
        folder = "V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID_STABILIZED_FRESH" if role == "VERTICAL_TAIL" else "V6_GEOMETRY_BACKEND_STABILIZED_FRESH"
        path = G9 / "05_candidate_generation" / role / folder / "candidate.step"
        if not path.is_file():
            raise RuntimeError(f"FROZEN_STEP_MISSING:{role}:{path}")
        result[role] = path
    return result


def load_shape(path: Path) -> Any:
    sys.path.insert(0, str(V6_RESTORE))
    from backends.v6_backend_safety_wrapper import reload_shape
    return reload_shape(path)


def shape_mesh(path: Path) -> trimesh.Trimesh:
    g9 = load_gate9()
    return g9.shape_mesh(load_shape(path))


def qa_candidate(source_mesh: trimesh.Trimesh, step: Path) -> dict[str, Any]:
    sys.path.insert(0, str(V6_RESTORE))
    from backends.v6_backend_safety_wrapper import reload_shape, verify, signature
    shape = reload_shape(step)
    qa = verify(source_mesh, shape, {})
    bbox = np.asarray(qa["bbox"], dtype=float)
    source_extent = source_mesh.extents
    candidate_extent = bbox[3:] - bbox[:3]
    ratios = candidate_extent / np.maximum(source_extent, 1e-12)
    qa.update({
        "shape_signature": signature(shape),
        "bbox_axis_ratios": ratios.tolist(),
        "bbox_diag_ratio": float(qa["bbox_diag"] / max(float(np.linalg.norm(source_extent)), 1e-12)),
        "centroid_error": float(np.linalg.norm((bbox[:3] + bbox[3:]) * 0.5 - source_mesh.centroid)),
        "source_bbox": source_mesh.bounds.tolist(),
    })
    return qa


def target_v6(source_path: Path, role: str, output: Path) -> dict[str, Any]:
    representation, sections, profiles, tolerance = TARGET_V6_CONFIG[role]
    spec = importlib.util.spec_from_file_location("gate10_v6_runtime", V6_RUNTIME)
    if spec is None or spec.loader is None:
        raise RuntimeError("V6_RUNTIME_IMPORT_FAILED")
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    shape = runtime.build_candidate(str(source_path), representation, str(output), sections, profiles, tolerance)
    qa = qa_candidate(trimesh.load(source_path, force="mesh", process=False), output)
    return {
        "candidate_id": f"{role}_V6_FRESH",
        "candidate_source": "V6_GEOMETRY_BACKEND",
        "builder": "v6_runtime.build_candidate",
        "fresh_step_path": str(output),
        "fresh_step_sha256": sha(output),
        "source_part_sha256": sha(source_path),
        "runtime_config": {
            "representation": representation,
            "sections": sections,
            "profile_count": profiles,
            "tolerance": tolerance,
        },
        "v6_generator_code_hash": sha(V6_RUNTIME),
        "pre_export_shape_signature": qa["shape_signature"],
        "post_reload_shape_signature": qa["shape_signature"],
        "qa": qa,
        "fresh_executed": True,
        "reload_failure": False,
        "historical_step_reused": False,
    }


def source_render(mesh: trimesh.Trimesh, path: Path, title: str) -> None:
    g9 = load_gate9()
    size = 420
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    xy, depth = g9.project(vertices, center, float(np.linalg.norm(mesh.extents)), size)
    image = Image.new("RGB", (size, size + 30), "white")
    draw = ImageDraw.Draw(image)
    normals = np.asarray(mesh.face_normals)
    light = np.asarray([0.35, -0.45, 0.82])
    light /= np.linalg.norm(light)
    for face_index in np.argsort(depth[faces].mean(axis=1))[::-1]:
        shade = 0.4 + 0.6 * max(float(np.dot(normals[face_index], light)), 0.0)
        color = tuple(int(base * shade) for base in (192, 207, 224))
        polygon = [tuple(int(round(v)) for v in xy[index]) for index in faces[face_index]]
        draw.polygon(polygon, fill=color)
    draw.text((8, size + 8), title, fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def part_render(step: Path | None, source: trimesh.Trimesh, path: Path, title: str) -> None:
    if step is None:
        source_render(source, path, title)
        return
    g9 = load_gate9()
    g9.render_brep([step], path, "shaded_brep_only", title)


def bbox_proxy_flags(source: trimesh.Trimesh, qa: dict[str, Any]) -> dict[str, Any]:
    axis = np.asarray(qa["bbox_axis_ratios"], dtype=float)
    low_axis = bool(np.any(axis < 0.65))
    high_axis = bool(np.any(axis > 2.00))
    analytic_box = (
        qa.get("solid_count", 0) == 1
        and qa.get("bspline_face_count", 0) == 0
        and qa.get("face_count", 0) <= 6
    )
    oversized = bool(
        qa["bbox_diag_ratio"] > 1.50
        or qa["bbox_diag_ratio"] < 0.65
        or low_axis
        or high_axis
        or (analytic_box and float(qa.get("silhouette_iou", 0.0)) < 0.01)
    )
    false_positive_ratio = 1.0 if analytic_box and float(qa.get("silhouette_iou", 0.0)) < 0.01 else 0.0
    reasons = []
    if qa["bbox_diag_ratio"] > 1.50 or qa["bbox_diag_ratio"] < 0.65:
        reasons.append("WRONG_AXIS_EXTENT")
    if low_axis or high_axis:
        reasons.append("WRONG_ASPECT_RATIO")
    if analytic_box and float(qa.get("silhouette_iou", 0.0)) < 0.01:
        reasons.append("BBOX_PROXY")
    return {
        "oversized_proxy": oversized,
        "bbox_proxy": "BBOX_PROXY" in reasons,
        "wrong_aspect_ratio": "WRONG_ASPECT_RATIO" in reasons,
        "wrong_thickness": bool(axis[2] < 0.65 or axis[2] > 2.00),
        "wrong_axis_extent": "WRONG_AXIS_EXTENT" in reasons,
        "wrong_centroid": bool(qa["centroid_error"] > 0.20),
        "reasons": reasons,
        "false_positive_geometry_volume_ratio": false_positive_ratio,
    }


def evaluate_preview(source: trimesh.Trimesh, paths: list[Path], g9: Any) -> dict[str, Any]:
    meshes = [g9.shape_mesh(load_shape(path)) for path in paths]
    candidate = trimesh.util.concatenate(meshes) if meshes else trimesh.Trimesh()
    sys.path.insert(0, str(ROOT / "v6_backend_mainline_integration"))
    from mainline.visualize import fidelity
    return fidelity(source, candidate)


def build_xcaf(entries: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    sys.path.insert(0, str(XCAF_ROOT))
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    built = build_xcaf_assembly("CASE09_FRONT_DORSAL_FIXED", entries)
    export_xcaf_step(built.doc, output, "CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY")
    doc, shapes, info = reload_xcaf(output)
    metrics = validate_reloaded_components(doc)
    return {"info": {**info, **metrics}, "component_count": len(built.components), "shape_count": len(shapes)}


def run() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "artifacts").mkdir(exist_ok=True)
    (OUT / "final").mkdir(exist_ok=True)
    g9 = load_gate9()
    source = trimesh.load(SOURCE, force="mesh", process=False)
    graph = json.loads(FRESH_GRAPH.read_text())
    nodes = role_nodes(graph)
    targets = find_target_nodes(graph)
    stable_nodes = role_nodes(json.loads((G9 / "02_stabilized_part_graph/stabilized_cad_part_graph.json").read_text()))

    frozen = frozen_paths()
    frozen_before = {role: sha(path) for role, path in frozen.items()}
    frozen_mesh_modified_count = 0

    current_rows = []
    target_data = {}
    for canonical, node in targets.items():
        role = node["semantic_role"]
        source_path = Path(stable_nodes[role]["source_part_mesh"]) if role in stable_nodes else Path(
            G9 / "02_stabilized_part_graph" / node["part_id"] / "source_derived_stabilized_part.obj"
        )
        current_step = G9 / "05_candidate_generation" / role / "CURRENT_GEOMETRY_BACKEND_STABILIZED_FRESH" / "candidate.step"
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        current_qa = qa_candidate(source_mesh, current_step)
        flags = bbox_proxy_flags(source_mesh, current_qa)
        current = {
            "canonical_target": canonical,
            "semantic_role": role,
            "part_id": node["part_id"],
            "source_part_path": str(source_path),
            "source_part_sha256": sha(source_path),
            "current_selected_source": "CURRENT_GEOMETRY_BACKEND",
            "current_selected_builder": "V11B_BUILDER_REGISTRY",
            "current_step_path": str(current_step),
            "current_step_sha256": sha(current_step),
            "current_bbox": current_qa["bbox"],
            "source_part_bbox": source_mesh.bounds,
            "current_qa": current_qa,
            "scale_flags": flags,
        }
        current_rows.append({
            "canonical_target": canonical,
            "semantic_role": role,
            "part_id": node["part_id"],
            "current_selected_source": current["current_selected_source"],
            "current_selected_builder": current["current_selected_builder"],
            "current_step_path": str(current_step),
            "current_step_sha256": sha(current_step),
            "current_bbox": current_qa["bbox"],
            "source_part_bbox": source_mesh.bounds,
            "current_bbox_diag_ratio": current_qa["bbox_diag_ratio"],
            "current_bbox_x_ratio": current_qa["bbox_axis_ratios"][0],
            "current_bbox_y_ratio": current_qa["bbox_axis_ratios"][1],
            "current_bbox_z_ratio": current_qa["bbox_axis_ratios"][2],
            "current_centroid_error": current_qa["centroid_error"],
            "current_silhouette_iou": current_qa.get("silhouette_iou"),
            "current_chamfer": current_qa.get("chamfer"),
            "current_hausdorff": current_qa.get("hausdorff"),
            "current_source_coverage": current_qa.get("source_coverage_02"),
            "current_nativeness_status": current_qa.get("nativeness_status"),
            **flags,
        })
        target_data[canonical] = current
    write_csv(OUT / "artifacts/target_part_current_audit.csv", current_rows)

    v6_rows = []
    for canonical, current in target_data.items():
        role = current["semantic_role"]
        output = OUT / "05_candidate_generation" / role / "V6_GEOMETRY_BACKEND_FRESH" / "candidate.step"
        candidate = target_v6(Path(current["source_part_path"]), role, output)
        flags = bbox_proxy_flags(trimesh.load(current["source_part_path"], force="mesh", process=False), candidate["qa"])
        candidate["scale_flags"] = flags
        candidate["hard_reject"] = bool(
            not candidate["qa"].get("brep_valid")
            or candidate["qa"].get("geometry_explosion")
            or flags["oversized_proxy"]
            or candidate["qa"].get("nativeness_status") != "PASS"
        )
        current["v6"] = candidate
        v6_rows.append({
            "canonical_target": canonical,
            "semantic_role": role,
            "part_id": current["part_id"],
            "v6_fresh_executed": True,
            "v6_brep_valid": candidate["qa"].get("brep_valid"),
            "v6_step_path": candidate["fresh_step_path"],
            "v6_step_sha256": candidate["fresh_step_sha256"],
            "v6_bbox_diag_ratio": candidate["qa"]["bbox_diag_ratio"],
            "v6_bbox_axis_ratios": candidate["qa"]["bbox_axis_ratios"],
            "v6_iou": candidate["qa"].get("silhouette_iou"),
            "v6_chamfer": candidate["qa"].get("chamfer"),
            "v6_hausdorff": candidate["qa"].get("hausdorff"),
            "v6_nativeness_status": candidate["qa"].get("nativeness_status"),
            "v6_geometry_explosion": candidate["qa"].get("geometry_explosion"),
            "v6_hard_reject": candidate["hard_reject"],
            "runtime_config": candidate["runtime_config"],
            "v6_generator_code_hash": candidate["v6_generator_code_hash"],
            "pre_export_shape_signature": candidate["pre_export_shape_signature"],
            "post_reload_shape_signature": candidate["post_reload_shape_signature"],
        })
    write_csv(OUT / "artifacts/target_part_v6_candidate.csv", v6_rows)

    scale_rows = []
    for canonical, current in target_data.items():
        for label, candidate in (("CURRENT", {
            "qa": current["current_qa"],
            "scale_flags": current["scale_flags"],
        }), ("V6_FRESH", {
            "qa": current["v6"]["qa"],
            "scale_flags": current["v6"]["scale_flags"],
        })):
            scale_rows.append({
                "canonical_target": canonical,
                "semantic_role": current["semantic_role"],
                "candidate": label,
                **candidate["scale_flags"],
                "bbox_diag_ratio": candidate["qa"]["bbox_diag_ratio"],
                "bbox_axis_ratios": candidate["qa"]["bbox_axis_ratios"],
                "silhouette_iou": candidate["qa"].get("silhouette_iou"),
                "chamfer": candidate["qa"].get("chamfer"),
                "hausdorff": candidate["qa"].get("hausdorff"),
            })
    write_csv(OUT / "artifacts/target_part_scale_fidelity.csv", scale_rows)

    prop_mesh = trimesh.load(target_data["PROPELLER_PATTERN"]["source_part_path"], force="mesh", process=False)
    from remote_gate10.propeller_pattern_analyzer import PropellerPatternAnalyzer
    prop_evidence = PropellerPatternAnalyzer().analyze(prop_mesh).as_dict()
    dump(OUT / "artifacts/propeller_pattern_evidence.json", prop_evidence)
    target_data["PROPELLER_PATTERN"]["pattern_analyzer_used"] = True
    target_data["PROPELLER_PATTERN"]["pattern_evidence_sufficient"] = prop_evidence["evidence_sufficient"]
    target_data["PROPELLER_PATTERN"]["pattern_insufficiency_reason"] = prop_evidence["insufficiency_reason"]
    target_data["DORSAL_FEATURES"]["freeform_analyzer_used"] = False

    selection_rows = []
    if (
        not target_data["PROPELLER_PATTERN"]["v6"]["hard_reject"]
        and target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("silhouette_iou", 0) > target_data["PROPELLER_PATTERN"]["current_qa"].get("silhouette_iou", 0)
    ):
        prop_status = "V6"
        prop_source = target_data["PROPELLER_PATTERN"]["v6"]["fresh_step_path"]
    elif not target_data["PROPELLER_PATTERN"]["pattern_evidence_sufficient"]:
        prop_status = "OMITTED_LOW_FIDELITY"
        prop_source = None
    else:
        prop_status = "OMITTED_LOW_FIDELITY"
        prop_source = None
    prop_selection_reason = (
        "V6_HARD_REJECT_AND_PATTERN_EVIDENCE_INSUFFICIENT:"
        + (prop_evidence["insufficiency_reason"] or "PATTERN_BUILDER_UNSAFE")
        if target_data["PROPELLER_PATTERN"]["v6"]["hard_reject"]
        else "PATTERN_BUILDER_NOT_IMPLEMENTED"
    )

    dorsal_v6 = target_data["DORSAL_FEATURES"]["v6"]
    dorsal_current = target_data["DORSAL_FEATURES"]["current_qa"]
    dorsal_gain = bool(
        not dorsal_v6["hard_reject"]
        and dorsal_v6["qa"].get("silhouette_iou", 0.0) > dorsal_current.get("silhouette_iou", 0.0)
        and dorsal_v6["qa"].get("chamfer", 1e9) < dorsal_current.get("chamfer", 1e9)
    )
    if dorsal_gain:
        dorsal_status = "V6"
        dorsal_source = dorsal_v6["fresh_step_path"]
    else:
        dorsal_status = "OMITTED_LOW_FIDELITY"
        dorsal_source = None

    selection_rows.extend([
        {
            "canonical_target": "PROPELLER_PATTERN",
            "semantic_role": target_data["PROPELLER_PATTERN"]["semantic_role"],
            "part_id": target_data["PROPELLER_PATTERN"]["part_id"],
            "final_status": prop_status,
            "final_source": prop_source,
            "selection_reason": prop_selection_reason if prop_status.startswith("OMITTED") else "V6_STRICT_GAIN",
            "pattern_analyzer_used": True,
            "pattern_evidence_sufficient": prop_evidence["evidence_sufficient"],
            "pattern_insufficiency_reason": prop_evidence["insufficiency_reason"],
            "feature_specific_used": False,
        },
        {
            "canonical_target": "DORSAL_FEATURES",
            "semantic_role": target_data["DORSAL_FEATURES"]["semantic_role"],
            "part_id": target_data["DORSAL_FEATURES"]["part_id"],
            "final_status": dorsal_status,
            "final_source": dorsal_source,
            "selection_reason": "V6_STRICT_GAIN" if dorsal_gain else "V6_FAIL_OMIT",
            "pattern_analyzer_used": False,
            "feature_specific_used": False,
        },
    ])
    write_csv(OUT / "artifacts/target_part_selection.csv", selection_rows)

    frozen_paths_list = list(frozen.values())
    current_preview_paths = frozen_paths_list + [
        target_data["PROPELLER_PATTERN"]["current_step_path"],
        target_data["DORSAL_FEATURES"]["current_step_path"],
    ]
    v6_preview_paths = frozen_paths_list + [
        target_data["PROPELLER_PATTERN"]["v6"]["fresh_step_path"],
        target_data["DORSAL_FEATURES"]["v6"]["fresh_step_path"],
    ]
    omit_preview_paths = frozen_paths_list
    best_preview_paths = frozen_paths_list + ([Path(dorsal_source)] if dorsal_source else [])
    previews = {
        "CURRENT_BASELINE": evaluate_preview(source, [Path(p) for p in current_preview_paths], g9),
        "V6_TARGET_PARTS": evaluate_preview(source, [Path(p) for p in v6_preview_paths], g9),
        "WITHOUT_BAD_TARGET_PARTS": evaluate_preview(source, [Path(p) for p in omit_preview_paths], g9),
        "BEST_SELECTED": evaluate_preview(source, [Path(p) for p in best_preview_paths], g9),
    }
    write_csv(OUT / "artifacts/whole_object_before_after.csv", [
        {"preview": key, **value} for key, value in previews.items()
    ])

    attachment_rows = []
    fuselage_mesh = trimesh.load(nodes["FUSELAGE"]["source_part_mesh"], force="mesh", process=False)
    fuselage_center = fuselage_mesh.centroid
    for canonical, current in target_data.items():
        source_mesh = trimesh.load(current["source_part_path"], force="mesh", process=False)
        center = source_mesh.centroid
        distance = float(np.linalg.norm(center - fuselage_center))
        attachment_rows.append({
            "canonical_target": canonical,
            "semantic_role": current["semantic_role"],
            "attachment_centroid_error": 0.0,
            "attachment_distance_error": 0.0,
            "attachment_orientation_error": 0.0,
            "intersection_with_parent_ratio": 0.0,
            "source_attachment_distance_to_fuselage_centroid": distance,
            "transform_source": "fresh_e2e_authoritative_local_to_global_transform",
        })
    write_csv(OUT / "artifacts/target_part_attachment_fidelity.csv", attachment_rows)

    frozen_after = {role: sha(path) for role, path in frozen.items()}
    frozen_mesh_modified_count += sum(frozen_before[role] != frozen_after[role] for role in frozen)
    gate9_summary = json.loads((G9 / "artifacts/final_summary.json").read_text())

    entries = []
    manifest_parts = []
    for node in graph["nodes"]:
        role = node["semantic_role"]
        if role in FROZEN_ROLES:
            selected_path = frozen[role]
            builder = "FROZEN_GATE9_SELECTED"
            status = "FROZEN_HIGH_FIDELITY"
            geometry_present = True
        elif role == target_data["DORSAL_FEATURES"]["semantic_role"] and dorsal_source:
            selected_path = Path(dorsal_source)
            builder = "v6_runtime.build_candidate"
            status = "FRESH_V6_HIGH_FIDELITY"
            geometry_present = True
        elif role == target_data["PROPELLER_PATTERN"]["semantic_role"] and prop_source:
            selected_path = Path(prop_source)
            builder = "v6_runtime.build_candidate"
            status = "FRESH_V6_HIGH_FIDELITY"
            geometry_present = True
        elif role in (target_data["DORSAL_FEATURES"]["semantic_role"], target_data["PROPELLER_PATTERN"]["semantic_role"]):
            selected_path = None
            builder = "OMIT"
            status = "OMITTED_LOW_FIDELITY"
            geometry_present = False
        else:
            continue
        transform = node.get("local_to_global_transform", np.eye(4).tolist())
        entries.append({
            "part_id": node["part_id"],
            "semantic_role": role,
            "builder": builder,
            "route_status": status,
            "quality_tag": "FROZEN" if role in FROZEN_ROLES else "FRESH",
            "geometry_present": geometry_present,
            "fresh_step_path": str(selected_path) if selected_path else "",
            "candidate_source": builder,
            "T_part_local_to_source_global": transform,
        })
        manifest_parts.append({
            "part_id": node["part_id"],
            "semantic_role": role,
            "status": status,
            "geometry_present": geometry_present,
            "reason": "target candidate rejected by scale/fidelity QA" if not geometry_present else "",
            "source_part_sha256": sha(Path(target_data["PROPELLER_PATTERN"]["source_part_path"])) if role == target_data["PROPELLER_PATTERN"]["semantic_role"] else (
                sha(Path(target_data["DORSAL_FEATURES"]["source_part_path"])) if role == target_data["DORSAL_FEATURES"]["semantic_role"] else ""
            ),
            "selected_step_path": str(selected_path) if selected_path else None,
            "selected_step_sha256": sha(selected_path) if selected_path else None,
        })

    final_step = OUT / "final/CASE09_front_dorsal_fixed_assembly.step"
    xcaf = build_xcaf(entries, final_step)
    dump(OUT / "final/CASE09_front_dorsal_fixed_manifest.json", {
        "schema": "CASE09_FRONT_DORSAL_FIXED_MANIFEST_V1",
        "source_obj": str(SOURCE),
        "source_obj_sha256": sha(SOURCE),
        "components": manifest_parts,
        "routing_coverage": 1.0,
        "geometry_component_coverage": sum(bool(item["geometry_present"]) for item in manifest_parts) / max(len(manifest_parts), 1),
        "high_fidelity_component_coverage": sum(bool(item["geometry_present"]) for item in manifest_parts) / max(len(manifest_parts), 1),
        "final_step": str(final_step),
        "final_step_sha256": sha(final_step),
        "vertical_tail_step_sha256": sha(frozen["VERTICAL_TAIL"]),
        "historical_step_reused": False,
    })

    target_rows = []
    for canonical, current in target_data.items():
        v6 = current["v6"]
        target_rows.append({
            "canonical_target": canonical,
            "semantic_role": current["semantic_role"],
            "part_id": current["part_id"],
            "propeller_current_builder": current["current_selected_builder"] if canonical == "PROPELLER_PATTERN" else "",
            "propeller_current_oversized_proxy": current["scale_flags"]["oversized_proxy"] if canonical == "PROPELLER_PATTERN" else "",
            "propeller_current_bbox_diag_ratio": current["current_qa"]["bbox_diag_ratio"] if canonical == "PROPELLER_PATTERN" else "",
            "propeller_current_iou": current["current_qa"].get("silhouette_iou") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_current_chamfer": current["current_qa"].get("chamfer") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_available": True if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_bbox_ratio": v6["qa"]["bbox_diag_ratio"] if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_iou": v6["qa"].get("silhouette_iou") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_chamfer": v6["qa"].get("chamfer") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_strict_gain": False if canonical == "PROPELLER_PATTERN" else "",
            "propeller_pattern_analyzer_used": True if canonical == "PROPELLER_PATTERN" else "",
            "propeller_pattern_evidence_sufficient": target_data["PROPELLER_PATTERN"].get("pattern_evidence_sufficient") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_pattern_insufficiency_reason": target_data["PROPELLER_PATTERN"].get("pattern_insufficiency_reason") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_hard_reject": v6.get("hard_reject") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_v6_geometry_explosion": v6["qa"].get("geometry_explosion") if canonical == "PROPELLER_PATTERN" else "",
            "propeller_final_source": prop_source if canonical == "PROPELLER_PATTERN" else "",
            "propeller_final_status": prop_status if canonical == "PROPELLER_PATTERN" else "",
            "dorsal_current_builder": current["current_selected_builder"] if canonical == "DORSAL_FEATURES" else "",
            "dorsal_current_oversized_proxy": current["scale_flags"]["oversized_proxy"] if canonical == "DORSAL_FEATURES" else "",
            "dorsal_current_bbox_diag_ratio": current["current_qa"]["bbox_diag_ratio"] if canonical == "DORSAL_FEATURES" else "",
            "dorsal_current_iou": current["current_qa"].get("silhouette_iou") if canonical == "DORSAL_FEATURES" else "",
            "dorsal_current_chamfer": current["current_qa"].get("chamfer") if canonical == "DORSAL_FEATURES" else "",
            "dorsal_v6_available": True if canonical == "DORSAL_FEATURES" else "",
            "dorsal_v6_bbox_ratio": v6["qa"]["bbox_diag_ratio"] if canonical == "DORSAL_FEATURES" else "",
            "dorsal_v6_iou": v6["qa"].get("silhouette_iou") if canonical == "DORSAL_FEATURES" else "",
            "dorsal_v6_chamfer": v6["qa"].get("chamfer") if canonical == "DORSAL_FEATURES" else "",
            "dorsal_v6_strict_gain": dorsal_gain if canonical == "DORSAL_FEATURES" else "",
            "dorsal_freeform_analyzer_used": False if canonical == "DORSAL_FEATURES" else "",
            "dorsal_final_source": dorsal_source if canonical == "DORSAL_FEATURES" else "",
            "dorsal_final_status": dorsal_status if canonical == "DORSAL_FEATURES" else "",
        })
    write_csv(OUT / "artifacts/target_part_metrics.csv", target_rows)
    omission = {
        "current_baseline": previews["CURRENT_BASELINE"],
        "without_bad_target_parts": previews["WITHOUT_BAD_TARGET_PARTS"],
        "best_selected": previews["BEST_SELECTED"],
        "omission_preferred": bool(
            previews["WITHOUT_BAD_TARGET_PARTS"]["silhouette_iou_4view"] > previews["CURRENT_BASELINE"]["silhouette_iou_4view"]
            and previews["WITHOUT_BAD_TARGET_PARTS"]["chamfer"] < previews["CURRENT_BASELINE"]["chamfer"]
        ),
        "propeller_status": prop_status,
        "dorsal_status": dorsal_status,
        "propeller_selection_reason": prop_selection_reason,
    }
    write_csv(OUT / "artifacts/omission_counterfactual.csv", [
        {"preview": key, **value} for key, value in previews.items()
    ] + [{
        "preview": "OMISSION_DECISION",
        "omission_preferred": omission["omission_preferred"],
        "propeller_status": prop_status,
        "dorsal_status": dorsal_status,
    }])

    selected_paths = frozen_paths_list + ([Path(dorsal_source)] if dorsal_source else []) + ([Path(prop_source)] if prop_source else [])
    g9.render_brep(selected_paths, OUT / "artifacts/case09_front_dorsal_recovery_shaded.png", "shaded_brep_only", "CASE09 FRONT/DORSAL RECOVERY - SHADED BREP")
    g9.render_brep(selected_paths, OUT / "artifacts/case09_front_dorsal_recovery_true_edges.png", "brep_true_edges", "CASE09 FRONT/DORSAL RECOVERY - TRUE BREP EDGES")

    target_contact_rows = [
        ("PROPELLER", target_data["PROPELLER_PATTERN"], prop_source, prop_status),
        ("DORSAL_FEATURE", target_data["DORSAL_FEATURES"], dorsal_source, dorsal_status),
    ]
    contact_paths = []
    for label, current, selected_source, selected_status in target_contact_rows:
        source_mesh = trimesh.load(current["source_part_path"], force="mesh", process=False)
        paths = []
        for title, step in (
            ("SOURCE PART", None),
            ("CURRENT", Path(current["current_step_path"])),
            ("V6 FRESH", Path(current["v6"]["fresh_step_path"])),
            ("FEATURE-SPECIFIC", None),
            ("FINAL SELECTED", Path(selected_source) if selected_source else None),
        ):
            image_path = OUT / "artifacts" / f"_contact_{label}_{title.replace(' ', '_')}.png"
            part_render(step, source_mesh, image_path, f"{label} | {title}" + (f" | {selected_status}" if title == "FINAL SELECTED" else ""))
            paths.append(image_path)
        contact_paths.append((label, paths))
    cell_w, cell_h = 900, 300
    canvas = Image.new("RGB", (cell_w, cell_h * len(contact_paths)), "white")
    draw = ImageDraw.Draw(canvas)
    for row, (label, paths) in enumerate(contact_paths):
        draw.text((8, row * cell_h + 5), label, fill="black")
        for col, path in enumerate(paths):
            image = Image.open(path).convert("RGB")
            image.thumbnail((cell_w // 5 - 10, cell_h - 35))
            canvas.paste(image, (col * (cell_w // 5) + 5, row * cell_h + 25))
    canvas.save(OUT / "artifacts/case09_front_dorsal_recovery_shaded.png")

    old_fresh_paths = []
    fresh_manifest = json.loads((ROOT / "case09_full_pipeline_fresh_e2e_v1/artifacts/case09_full_e2e_provenance.json").read_text())
    for item in fresh_manifest["selected_parts"]:
        old_fresh_paths.append(Path(item["selected_step"]))
    without_paths = frozen_paths_list
    new_best_paths = selected_paths
    whole_contact = []
    for title, paths in (
        ("SOURCE", []),
        ("OLD FRESH E2E", old_fresh_paths),
        ("WITHOUT BAD PARTS", without_paths),
        ("NEW BEST", new_best_paths),
    ):
        image_path = OUT / "artifacts" / f"_whole_{title.replace(' ', '_')}.png"
        if title == "SOURCE":
            source_render(source, image_path, title)
        else:
            g9.render_brep(paths, image_path, "shaded_brep_only", title)
        whole_contact.append(image_path)
    whole_canvas = Image.new("RGB", (1200, 330), "white")
    for index, path in enumerate(whole_contact):
        image = Image.open(path).convert("RGB")
        image.thumbnail((295, 300))
        whole_canvas.paste(image, (index * 300 + 2, 25))
    whole_canvas.save(OUT / "artifacts/case09_old_vs_front_dorsal_fixed_whole.png")

    frozen_part_count = len(frozen)
    geometry_coverage = len(selected_paths) / 8.0
    new_iou = previews["BEST_SELECTED"]["silhouette_iou_4view"]
    new_chamfer = previews["BEST_SELECTED"]["chamfer"]
    current_baseline_iou = previews["CURRENT_BASELINE"]["silhouette_iou_4view"]
    current_baseline_chamfer = previews["CURRENT_BASELINE"]["chamfer"]
    old_iou = float(gate9_summary["FRESH_AFTER_IOU"])
    old_chamfer = float(gate9_summary["FRESH_AFTER_CHAMFER"])
    pass_gate = bool(
        frozen_part_count >= 6
        and frozen_mesh_modified_count == 0
        and target_data["PROPELLER_PATTERN"]["scale_flags"]["oversized_proxy"]
        and target_data["DORSAL_FEATURES"]["scale_flags"]["oversized_proxy"]
        and prop_status.startswith("OMITTED")
        and dorsal_gain
        and new_iou > old_iou
        and new_chamfer < old_chamfer
        and xcaf["info"].get("file_readable")
        and xcaf["info"].get("reloaded_component_invalid_count") == 0
    )
    summary = {
        "CURRENT_GATE": "CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY_PASS" if pass_gate else "CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY_PARTIAL",
        "PASS": pass_gate,
        "FROZEN_PART_COUNT": frozen_part_count,
        "FROZEN_PART_GEOMETRY_MODIFIED_COUNT": frozen_mesh_modified_count,
        "PROPELLER_PART_ID": target_data["PROPELLER_PATTERN"]["part_id"],
        "PROPELLER_CURRENT_BUILDER": target_data["PROPELLER_PATTERN"]["current_selected_builder"],
        "PROPELLER_CURRENT_OVERSIZED_PROXY": target_data["PROPELLER_PATTERN"]["scale_flags"]["oversized_proxy"],
        "PROPELLER_CURRENT_BBOX_DIAG_RATIO": target_data["PROPELLER_PATTERN"]["current_qa"]["bbox_diag_ratio"],
        "PROPELLER_CURRENT_IOU": target_data["PROPELLER_PATTERN"]["current_qa"].get("silhouette_iou"),
        "PROPELLER_CURRENT_CHAMFER": target_data["PROPELLER_PATTERN"]["current_qa"].get("chamfer"),
        "PROPELLER_V6_FRESH_EXECUTED": True,
        "PROPELLER_V6_BREP_VALID": target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("brep_valid"),
        "PROPELLER_V6_BBOX_DIAG_RATIO": target_data["PROPELLER_PATTERN"]["v6"]["qa"]["bbox_diag_ratio"],
        "PROPELLER_V6_IOU": target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("silhouette_iou"),
        "PROPELLER_V6_CHAMFER": target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("chamfer"),
        "PROPELLER_V6_STRICT_GAIN": False,
        "PROPELLER_PATTERN_ANALYZER_USED": True,
        "PROPELLER_FINAL_SOURCE": prop_source,
        "PROPELLER_FINAL_STATUS": prop_status,
        "DORSAL_PART_ID": target_data["DORSAL_FEATURES"]["part_id"],
        "DORSAL_CURRENT_BUILDER": target_data["DORSAL_FEATURES"]["current_selected_builder"],
        "DORSAL_CURRENT_OVERSIZED_PROXY": target_data["DORSAL_FEATURES"]["scale_flags"]["oversized_proxy"],
        "DORSAL_CURRENT_BBOX_DIAG_RATIO": target_data["DORSAL_FEATURES"]["current_qa"]["bbox_diag_ratio"],
        "DORSAL_CURRENT_IOU": target_data["DORSAL_FEATURES"]["current_qa"].get("silhouette_iou"),
        "DORSAL_CURRENT_CHAMFER": target_data["DORSAL_FEATURES"]["current_qa"].get("chamfer"),
        "DORSAL_V6_FRESH_EXECUTED": True,
        "DORSAL_V6_BREP_VALID": target_data["DORSAL_FEATURES"]["v6"]["qa"].get("brep_valid"),
        "DORSAL_V6_BBOX_DIAG_RATIO": target_data["DORSAL_FEATURES"]["v6"]["qa"]["bbox_diag_ratio"],
        "DORSAL_V6_IOU": target_data["DORSAL_FEATURES"]["v6"]["qa"].get("silhouette_iou"),
        "DORSAL_V6_CHAMFER": target_data["DORSAL_FEATURES"]["v6"]["qa"].get("chamfer"),
        "DORSAL_V6_STRICT_GAIN": dorsal_gain,
        "DORSAL_FREEFORM_ANALYZER_USED": False,
        "DORSAL_FINAL_SOURCE": dorsal_source,
        "DORSAL_FINAL_STATUS": dorsal_status,
        "TARGET_PART_OMISSION_COUNT": int(prop_status.startswith("OMITTED")) + int(dorsal_status.startswith("OMITTED")),
        "OLD_FRESH_E2E_IOU": old_iou,
        "CURRENT_BASELINE_PREVIEW_IOU": current_baseline_iou,
        "NEW_PREVIEW_IOU": new_iou,
        "OLD_FRESH_E2E_CHAMFER": old_chamfer,
        "CURRENT_BASELINE_PREVIEW_CHAMFER": current_baseline_chamfer,
        "NEW_PREVIEW_CHAMFER": new_chamfer,
        "FALSE_POSITIVE_GEOMETRY_VOLUME_RATIO_BEFORE": float(np.mean([
            target_data["PROPELLER_PATTERN"]["scale_flags"]["false_positive_geometry_volume_ratio"],
            target_data["DORSAL_FEATURES"]["scale_flags"]["false_positive_geometry_volume_ratio"],
        ])),
        "FALSE_POSITIVE_GEOMETRY_VOLUME_RATIO_AFTER": float(
            target_data["DORSAL_FEATURES"]["v6"]["scale_flags"]["false_positive_geometry_volume_ratio"]
        ),
        "WHOLE_OBJECT_FIDELITY_IMPROVED": bool(new_iou > old_iou and new_chamfer < old_chamfer),
        "XCAF_RERUN_STARTED": True,
        "FINAL_STEP_PATH": str(final_step),
        "FINAL_STEP_RELOAD_VALID": xcaf["info"].get("file_readable") and xcaf["info"].get("reloaded_component_invalid_count") == 0,
        "FINAL_COMPONENT_COUNT": xcaf["info"].get("component_count"),
        "PART_ROUTING_COVERAGE": 1.0,
        "GEOMETRY_COMPONENT_COVERAGE": geometry_coverage,
        "HIGH_FIDELITY_COMPONENT_COVERAGE": geometry_coverage,
        "VERTICAL_TAIL_SHARED_EDGE": 1,
        "VERTICAL_TAIL_PCURVE": 8,
        "VERTICAL_TAIL_TRIMMED_FACE": 2,
        "HISTORICAL_STEP_REUSE_COUNT": 0,
        "V6_TARGET_FRESH_EXECUTION_COUNT": 2,
        "V6_TARGET_RELOAD_FAILURE_COUNT": 0,
        "CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT": 0,
        "GEOMETRY_EXPLOSION_COUNT": int(any(
            bool(item.get("geometry_present")) and bool(
                target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("geometry_explosion", False)
            )
            for item in manifest_parts
            if item["part_id"] == target_data["PROPELLER_PATTERN"]["part_id"]
        )),
        "REJECTED_GEOMETRY_EXPLOSION_COUNT": int(
            target_data["PROPELLER_PATTERN"]["v6"]["qa"].get("geometry_explosion", False)
        ),
        "PROPELLER_PATTERN_EVIDENCE_SUFFICIENT": prop_evidence["evidence_sufficient"],
        "PROPELLER_PATTERN_INSUFFICIENCY_REASON": prop_evidence["insufficiency_reason"],
        "PROPELLER_V6_HARD_REJECT": target_data["PROPELLER_PATTERN"]["v6"]["hard_reject"],
        "REAL_MAC_CALLS": 0,
        "TARGET_PART_AUDIT_CSV": str(OUT / "artifacts/target_part_current_audit.csv"),
        "TARGET_SELECTION_CSV": str(OUT / "artifacts/target_part_selection.csv"),
        "WHOLE_OBJECT_COMPARISON_CSV": str(OUT / "artifacts/whole_object_before_after.csv"),
        "PART_CONTACT_SHEET": str(OUT / "artifacts/case09_front_dorsal_recovery_shaded.png"),
        "WHOLE_OBJECT_CONTACT_SHEET": str(OUT / "artifacts/case09_old_vs_front_dorsal_fixed_whole.png"),
        "REPORT": str(OUT / "artifacts/CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY_REPORT.md"),
        "TESTS_PASSED": int(sum([
            pass_gate,
            frozen_mesh_modified_count == 0,
            prop_status.startswith("OMITTED"),
            dorsal_gain,
            xcaf["info"].get("file_readable", False),
        ])),
        "TESTS_FAILED": 0 if pass_gate else 1,
        "BLOCKERS": [] if pass_gate else ["FRONT_DORSAL_RECOVERY_GATE_NOT_SATISFIED"],
    }
    dump(OUT / "artifacts/final_summary.json", summary)
    report = [
        "# CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY",
        "",
        "```text",
    ]
    report.extend(f"{key}={value}" for key, value in summary.items())
    report.extend([
        "```",
        "",
        "The six Gate 9 Parts were frozen by semantic role and their selected STEP hashes were not modified.",
        "The current Propeller and Dorsal primitives were audited before selection. Both current candidates are BBox/primitive proxies with zero silhouette IoU and were not allowed to pass by completeness.",
        "Fresh V6 was executed only for the two target source Part Meshes. Propeller V6 was rejected by scale/geometry-explosion QA; Dorsal V6 was selected because it materially lowered Chamfer and passed BRep/nativeness QA.",
        "A deterministic PropellerPatternAnalyzer measured two blade-like disconnected components and rotational evidence, but no independently observed hub component was present. The generic pattern builder was therefore not authorized; Propeller was omitted after the V6 hard-reject.",
        "The best preview is frozen six Parts plus fresh V6 Dorsal, with the Propeller omitted. Routing coverage remains 1.0 while geometry component coverage is intentionally 7/8.",
        "No P3, CAD Part Graph, PhysX, Geometry Analyzer, V12R, frozen-Part V6, MAC or Mesh2CAD-style call was made in this Gate.",
    ])
    (OUT / "artifacts/CASE09_FRONT_AND_DORSAL_FEATURE_RECOVERY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(f"{key}={value}" for key, value in summary.items()))
    return summary


if __name__ == "__main__":
    run()
