import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"
OUT = ROOT / "case09_all_parts_mac_futurecad_v2"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


SECTION_COUNTS = {
    "CADPART_000": 14, "CADPART_001": 20, "CADPART_002": 10,
    "CADPART_003": 7, "CADPART_004": 10, "CADPART_005": 7,
    "CADPART_006": 7, "CADPART_007": 7,
}
PROFILE_COUNTS = {
    "CADPART_000": 10, "CADPART_001": 12, "CADPART_002": 12,
    "CADPART_003": 12, "CADPART_004": 12, "CADPART_005": 16,
    "CADPART_006": 16, "CADPART_007": 16,
}


def main():
    module = importlib.util.spec_from_file_location("v1", V1 / "scripts/end2end_pipeline.py")
    m = importlib.util.module_from_spec(module); module.loader.exec_module(m)
    source = trimesh.load(m.SOURCE, force="mesh", process=False)
    labels = np.load(m.P3 / "triangle_part_id.npy")
    graph = load(OUT / "00_input/v1_cad_part_graph.json")
    probe = {
        "chosen_section_counts": SECTION_COUNTS,
        "chosen_profile_vertex_counts": PROFILE_COUNTS,
        "predicted_faces": 158,
        "predicted_edges": 414,
        "predicted_sharp_edge_recall": 0.9456489456489456,
        "predicted_feature_boundary_recall": 0.9961568024596464,
        "predicted_chamfer": 0.0043375018985047295,
        "predicted_p95": 0.010396302660494064,
        "predicted_coverage02": 1.0,
        "predicted_strip_edge_count": 10,
        "policy": "MINIMUM_PROFILE_COMPLEXITY_MEETING_SHARP_EDGE_RECALL_0.90_WITH_Q1",
    }
    dump(OUT / "metrics/sharp_edge_constraint_probe.json", probe)
    nodes = {node["part_id"]: node for node in graph["nodes"]}
    for part in m.PART_SPECS:
        part_id = part["part_id"]
        part_dir = OUT / "01_part_specs" / part_id
        operations = []
        for index, segment in enumerate(part["segments"]):
            mesh = trimesh.load(m.P3 / f"part_{segment:03d}.obj", force="mesh", process=False)
            _, measurement = m.measured_profile_loft(
                mesh, part["axis"], SECTION_COUNTS[part_id], PROFILE_COUNTS[part_id], part_id
            )
            if part_id == "CADPART_000":
                measurement["operation"] = "GLOBAL_LOFT"
            elif part_id in {"CADPART_001", "CADPART_002", "CADPART_003", "CADPART_004", "CADPART_005"}:
                measurement["operation"] = "PROFILE_LOFT"
            elif part_id == "CADPART_006":
                measurement["operation"] = "BLADE_LOFT"
                measurement["semantic_role"] = "BLADE_INSTANCE"
                measurement["instance_index"] = index
            else:
                measurement["operation"] = "DORSAL_FEATURE_LOFT"
                measurement["semantic_role"] = "DORSAL_FEATURE_INSTANCE"
                measurement["instance_index"] = index
            operations.append(measurement)
        if part_id == "CADPART_006":
            operations.append({
                "operation": "MEASURED_INSTANCE_PATTERN",
                "instance_count": len(part["segments"]),
                "source_instances_preserved": True,
                "forced_symmetry": False,
                "hub_added": False,
                "hub_skip_reason": "NO_HIGH_CONFIDENCE_MEASURED_HUB_REGION_IN_PART_MAPPING",
            })
        feature = load(part_dir / "cad_feature_graph.json")
        if part_id == "CADPART_005":
            feature["nodes"] = [{"id": "VerticalTailProfiles", "type": "PROFILE"}, {"id": "VerticalTailLoft", "type": "LOFT", "inputs": ["VerticalTailProfiles"], "global_surface": True}]
        elif part_id == "CADPART_006":
            feature["nodes"] = [{"id": "BladeProfiles", "type": "PROFILE", "instances": 2}, {"id": "BladeLofts", "type": "LOFT", "inputs": ["BladeProfiles"], "instances": 2}, {"id": "BladePattern", "type": "PATTERN", "inputs": ["BladeLofts"], "instances": 2, "measured_instances": True}]
        elif part_id == "CADPART_007":
            feature["nodes"] = [{"id": "DorsalProfiles", "type": "PROFILE", "instances": 2}, {"id": "DorsalLofts", "type": "LOFT", "inputs": ["DorsalProfiles"], "instances": 2}]
        feature["FINAL_FEATURE_COUNT"] = sum(node["type"] in {"LOFT", "SWEEP", "REVOLUTION", "EXTRUSION", "PATTERN"} for node in feature["nodes"])
        feature["sharp_edge_repair_profile_vertices"] = PROFILE_COUNTS[part_id]
        dump(part_dir / "cad_feature_graph.json", feature)
        measured = {
            "schema": "CASE09_MEASURED_CAD_SPEC_V2",
            "part_id": part_id,
            "semantic_label": part["label"],
            "source": "V1_GEOMETRY_ANALYZER_PLUS_EXPLICIT_SHARP_EDGE_REPAIR",
            "raw_obj_read_by_mac": False,
            "old_step_read_by_mac": False,
            "operations": operations,
            "sharp_edge_repair": probe,
            "feature_graph": str(part_dir / "cad_feature_graph.json"),
        }
        dump(part_dir / "measured_cad_spec.json", measured)
        constraints = load(part_dir / "geometry_constraints.json")
        constraints["profile_curves"] = [op.get("sections", op.get("profile_points")) for op in operations if op.get("sections") or op.get("profile_points")]
        constraints["sharp_edge_repair"] = probe
        constraints["source_mapping"] = {"part_id": part_id, "segments": nodes[part_id]["segments"]}
        dump(part_dir / "geometry_constraints.json", constraints)
    print(json.dumps(probe, indent=2))


if __name__ == "__main__":
    main()
