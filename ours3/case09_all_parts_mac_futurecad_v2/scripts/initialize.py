import hashlib
import json
import shutil
import socket
import time
from pathlib import Path

import numpy as np


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"
OUT = ROOT / "case09_all_parts_mac_futurecad_v2"
SOURCE = ROOT / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
FUTURECAD = ROOT / "external/FutureCAD"
EXPECTED_SHA = "ec3b6fb83ce405bd4c6cd41bb506ef9e5a8995919fb32ab9c40411f400e823cd"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    if not SOURCE.is_file() or sha256(SOURCE) != EXPECTED_SHA:
        raise RuntimeError("source OBJ missing or SHA mismatch")
    if not (V1 / "metrics/summary.json").is_file():
        raise RuntimeError("V1 is incomplete")
    if OUT.exists() and not (OUT / "00_input/provenance_manifest.json").is_file():
        existing = [p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()]
        if any(path != "scripts/initialize.py" for path in existing):
            raise RuntimeError(f"refusing to reuse unrecognized output root: {OUT}; files={existing}")

    for directory in (
        "00_input", "01_part_specs", "02_mac_runs", "03_grounding",
        "04_program_execution", "05_part_qa", "06_assembly",
        "07_final_qa", "artifacts", "metrics", "scripts", "tests"
    ):
        (OUT / directory).mkdir(parents=True, exist_ok=True)

    v1_manifest = load(V1 / "00_source/provenance_manifest.json")
    v1_summary = load(V1 / "metrics/summary.json")
    graph = load(V1 / "02_cad_part_graph/cad_part_graph.json")
    labels = np.load(V1 / "01_part_discovery/p3/triangle_part_id.npy")
    expected_ids = [f"CADPART_{i:03d}" for i in range(8)]
    actual_ids = [node["part_id"] for node in graph["nodes"]]
    if actual_ids != expected_ids or graph["cad_part_count"] != 8:
        raise RuntimeError(f"unexpected V1 part mapping: {actual_ids}")
    if set(np.unique(labels).tolist()) != set(range(graph["p3_segments"])):
        raise RuntimeError("P3 triangle mapping is inconsistent with graph")
    if v1_manifest["source_sha256"] != EXPECTED_SHA or v1_manifest["source_obj"] != str(SOURCE):
        raise RuntimeError("V1 provenance does not resolve to frozen source")

    copy(V1 / "metrics/summary.json", OUT / "00_input/v1_summary.json")
    copy(V1 / "02_cad_part_graph/cad_part_graph.json", OUT / "00_input/v1_cad_part_graph.json")
    copy(V1 / "01_part_discovery/p3/triangle_part_id.npy", OUT / "00_input/p3_triangle_part_id.npy")
    copy(V1 / "01_part_discovery/p3/part_metadata.json", OUT / "00_input/p3_part_metadata.json")
    copy(V1 / "01_part_discovery/physx/provenance.json", OUT / "00_input/physx_provenance.json")
    copy(V1 / "01_part_discovery/physx/physx_global.json", OUT / "00_input/physx_global.json")

    mapping_differences = []
    expected_labels = [
        "FUSELAGE", "MAIN_WING_LEFT", "MAIN_WING_RIGHT",
        "HORIZONTAL_TAIL_LEFT", "HORIZONTAL_TAIL_RIGHT", "VERTICAL_TAIL",
        "PROPELLER_PATTERN", "DORSAL_FEATURES",
    ]
    for node, expected_label in zip(graph["nodes"], expected_labels):
        part_id = node["part_id"]
        if node["label"] != expected_label:
            mapping_differences.append({"part_id": part_id, "expected": expected_label, "artifact": node["label"]})
        target = OUT / "01_part_specs" / part_id
        target.mkdir(parents=True, exist_ok=True)
        feature = load(V1 / "04_feature_graph" / part_id / "cad_feature_graph.json")
        measured = load(V1 / "05_backend_recovery" / part_id / "measured_cad_spec.json")
        analysis = load(V1 / "03_geometry_analyzer" / part_id / "geometry_analysis.json")
        for key in list(measured):
            if key.startswith("MAC_"):
                measured.pop(key, None)
        dump(target / "cad_feature_graph.json", feature)
        dump(target / "measured_cad_spec.json", measured)
        dump(target / "geometry_analysis.json", analysis)
        operation = measured["operations"][0]
        constraints = {
            "schema": "CASE09_MEASURED_GEOMETRY_CONSTRAINTS_V2",
            "part_id": part_id,
            "semantic_label": node["label"],
            "source_sha256": EXPECTED_SHA,
            "source_segments": node["segments"],
            "bbox": analysis.get("bbox"),
            "axis": operation.get("axis", node.get("axis")),
            "profile_curves": operation.get("sections", operation.get("profiles", [])),
            "plane_parameters": operation.get("plane_parameters", analysis.get("plane_parameters", [])),
            "radius": operation.get("radius"),
            "depth": operation.get("depth", operation.get("span")),
            "span": operation.get("span"),
            "twist": operation.get("twist", analysis.get("twist")),
            "part_local_coordinate_system": {
                "local_to_global_transform": node.get("local_to_global_transform"),
                "global_to_local_transform": node.get("global_to_local_transform"),
            },
            "feature_boundaries": feature.get("nodes", []),
            "hard_constraint_policy": "MAC_MUST_NOT_MODIFY_MEASURED_VALUES_WITHOUT_EXPLICIT_REPAIR",
            "raw_obj_available_to_mac": False,
            "old_step_available_to_mac": False,
        }
        dump(target / "geometry_constraints.json", constraints)
        dump(target / "part_mapping.json", node)

    repo_files = sorted(str(p.relative_to(FUTURECAD)) for p in FUTURECAD.rglob("*") if p.is_file() and ".git" not in p.parts)
    official_code = any(p.endswith((".py", ".cpp", ".cu", ".sh")) for p in repo_files)
    brep_code = any("brepground" in p.lower() or "ground" in p.lower() and p.endswith(".py") for p in repo_files)
    weights = any(p.endswith((".pt", ".pth", ".ckpt", ".safetensors", ".bin")) for p in repo_files)
    inference = any("infer" in p.lower() and p.endswith((".py", ".sh")) for p in repo_files)
    audit = {
        "FUTURECAD_REPO_FOUND": (FUTURECAD / ".git").is_dir(),
        "FUTURECAD_COMMIT": "9a39bc895f1d4194fd5279ac67fef0496aadf32b",
        "FUTURECAD_REPO_FILES": repo_files,
        "FUTURECAD_OFFICIAL_CODE_AVAILABLE": official_code,
        "BREPGROUND_CODE_AVAILABLE": brep_code,
        "BREPGROUND_WEIGHTS_AVAILABLE": weights,
        "BREPGROUND_INFERENCE_AVAILABLE": inference,
        "FUTURECAD_OFFICIAL_USED": False,
        "GROUNDING_MODE": "FUTURECAD_COMPATIBLE_GROUNDING_PROXY",
        "reason": "Official repository contains README.md only and states code/usage release is TODO.",
    }
    dump(OUT / "03_grounding/futurecad_official_audit.json", audit)
    provenance = {
        "experiment": "CASE09_ALL_PARTS_MAC_FUTURECAD_V2",
        "created_unix": time.time(),
        "execution_host": socket.gethostname(),
        "source_obj": str(SOURCE),
        "source_sha256": EXPECTED_SHA,
        "v1_root": str(V1),
        "v1_frozen": True,
        "v1_source_mapping_verified": True,
        "v1_p3_reused": True,
        "v1_physx_reused": True,
        "v1_geometry_analyzer_reused": True,
        "v1_feature_graph_reused": True,
        "p3_rerun": False,
        "physx_rerun": False,
        "mapping_differences": mapping_differences,
        "part_ids": actual_ids,
        "part_labels": [node["label"] for node in graph["nodes"]],
        "frozen_thresholds": v1_manifest["frozen_quality_thresholds"],
        "v1_final_step_sha256": v1_summary["FINAL_STEP_SHA256"],
    }
    dump(OUT / "00_input/provenance_manifest.json", provenance)
    print(json.dumps({"OUT": str(OUT), "SOURCE_SHA256": EXPECTED_SHA, "PARTS": actual_ids, "MAPPING_DIFFERENCES": mapping_differences, **audit}, indent=2))


if __name__ == "__main__":
    main()
