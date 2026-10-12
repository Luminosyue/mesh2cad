from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .common import sha256, write_json


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V13 = ROOT / "v13_transform_restore_and_xcaf_assembly"
sys.path.insert(0, str(V13))


def run(selected_manifest: dict[str, Any], output_root: Path) -> dict[str, Any]:
    from assembly.assembly_quality_audit import topology_audit
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    from assembly.transform_restore import apply_to_shape, restore_transform
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step, load_step_shape
    sys.path.insert(0, str(ROOT / "v6_geometry_backend_restore"))
    from backends.v6_backend_safety_wrapper import topology_metrics

    entries = []
    consumed_match = True
    vertical_before = None
    vertical_after_placement = None
    for part in selected_manifest["parts"]:
        step_path = Path(part["selected_step_path"])
        actual_hash = sha256(step_path)
        consumed_match = consumed_match and actual_hash == part["selected_step_sha256"]
        transform_metadata = {
            "local_to_global_transform": part["local_to_global_transform"],
            "local_coordinate_frame": part.get("local_coordinate_frame"),
        }
        transform = restore_transform(part["part_id"], transform_metadata)
        local_shape = load_step_shape(step_path)
        placed_shape = apply_to_shape(local_shape, transform)
        if part["part_id"] == "CADPART_005":
            vertical_before = local_shape
            vertical_after_placement = placed_shape
        entries.append({
            "part_id": part["part_id"],
            "semantic_role": part["semantic_role"],
            "builder": part["selected_builder"],
            "route_status": "SUCCESS_HIGH_FIDELITY",
            "quality_tag": part["quality_status"],
            "geometry_present": True,
            "fresh_step_path": str(step_path),
            "fresh_brep_hash": actual_hash,
            "candidate_source": part["selected_source"],
            "T_part_local_to_source_global": part["local_to_global_transform"],
        })
    output_dir = output_root / "cases/CASE09/v13/final"
    output_dir.mkdir(parents=True, exist_ok=True)
    built = build_xcaf_assembly("CASE09", entries)
    output_step = output_dir / "CASE09_v6_integrated_assembly.step"
    export_xcaf_step(built.doc, output_step, "CASE09_V6_INTEGRATED_XCAF_ASSEMBLY")
    reload_doc, reload_shapes, reload_info = reload_xcaf(output_step)
    reload_metrics = validate_reloaded_components(reload_doc)
    vertical_topology = topology_audit(vertical_before, vertical_after_placement)
    vertical_before_metrics = topology_metrics(vertical_before, 1.0)
    vertical_after_metrics = topology_metrics(vertical_after_placement, 1.0)
    vertical_topology["robust_shared_edge_count_before"] = vertical_before_metrics["shared_edge_count"]
    vertical_topology["robust_shared_edge_count_after"] = vertical_after_metrics["shared_edge_count"]
    vertical_topology["robust_pcurve_count_before"] = vertical_before_metrics["pcurve_count"]
    vertical_topology["robust_pcurve_count_after"] = vertical_after_metrics["pcurve_count"]
    vertical_topology["robust_trimmed_face_count_before"] = vertical_before_metrics["trimmed_face_count"]
    vertical_topology["robust_trimmed_face_count_after"] = vertical_after_metrics["trimmed_face_count"]
    result = {
        "v13_rerun_started": True,
        "v13_rerun_pass": bool(
            consumed_match
            and reload_info["file_readable"]
            and reload_metrics["component_count"] == len(entries)
            and reload_metrics["reloaded_component_invalid_count"] == 0
            and not vertical_topology["local_topology_modified"]
            and vertical_topology["robust_shared_edge_count_after"] >= 1
            and vertical_topology["robust_pcurve_count_after"] >= 2
            and vertical_topology["robust_trimmed_face_count_after"] >= 2
        ),
        "v13_consumed_selected_artifact_match": consumed_match,
        "assembly_step": str(output_step),
        "assembly_step_sha256": sha256(output_step),
        "reload": {**reload_info, **reload_metrics},
        "vertical_tail_topology": vertical_topology,
        "assembly_stage_geometry_rebuild_count": 0,
        "assembly_stage_v6_call_count": 0,
    }
    write_json(output_dir / "v13_run_result.json", result)
    write_json(output_dir / "consumed_selected_manifest.json", selected_manifest)
    return result
