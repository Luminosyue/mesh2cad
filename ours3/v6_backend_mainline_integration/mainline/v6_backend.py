from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from .common import sha256


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V6_RUNTIME = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py"
V6_GRAPH = ROOT / "case09_fullstack_mesh2cad_mac_v6/02_cad_part_graph"
RESTORE = ROOT / "v6_geometry_backend_restore"

CONFIG = {
    "CADPART_000": ("FUSELAGE", "PERIODIC_GLOBAL_BSPLINE", 64, 32, 0.001),
    "CADPART_001": ("MAIN_WING_LEFT", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
    "CADPART_002": ("MAIN_WING_RIGHT", "RIGHT_WING_SEMANTIC_SKIN_REPAIR", 12, 10, 0.0002),
    "CADPART_003": ("TAILPLANE_LEFT", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
    "CADPART_004": ("TAILPLANE_RIGHT", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
    "CADPART_005": ("VERTICAL_TAIL", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
}


@dataclass
class MainlineV6Candidate:
    part_id: str
    role: str
    candidate_id: str
    source_mesh: Path
    output_step: Path
    representation: str
    shape: Any
    reloaded_shape: Any
    qa: dict[str, Any]
    provenance: dict[str, Any]


def _runtime():
    spec = importlib.util.spec_from_file_location("v6_mainline_runtime", V6_RUNTIME)
    if spec is None or spec.loader is None:
        raise RuntimeError("V6_RUNTIME_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _safety_functions():
    import sys
    sys.path.insert(0, str(RESTORE))
    from backends.v6_backend_safety_wrapper import reload_shape, signature, verify
    return reload_shape, signature, verify


def generate(part_id: str, output_root: Path, transform_metadata: dict[str, Any]) -> MainlineV6Candidate:
    role, representation, sections, profiles, tolerance = CONFIG[part_id]
    source_mesh = V6_GRAPH / part_id / "source_part.obj"
    output_step = output_root / "cases/CASE09" / part_id / "V6_GEOMETRY_BACKEND" / "fresh.step"
    output_step.parent.mkdir(parents=True, exist_ok=True)
    runtime = _runtime()
    shape = runtime.build_candidate(str(source_mesh), representation, str(output_step), sections, profiles, tolerance)
    reload_shape, signature, verify = _safety_functions()
    reloaded = reload_shape(output_step)
    source = trimesh.load(source_mesh, force="mesh", process=False)
    qa = verify(source, reloaded, {})
    source_center = np.asarray(source.bounds, float).mean(axis=0)
    output_center = (np.asarray(qa["bbox"][:3]) + np.asarray(qa["bbox"][3:])) * 0.5
    centroid_error = float(np.linalg.norm(output_center - source_center) / max(np.linalg.norm(source.extents), 1e-12))
    scale_sane = 0.25 <= qa["bbox_ratio"] <= 4.0
    centroid_sane = centroid_error <= 0.75
    degenerate_sane = qa["tiny_face_ratio"] < 0.5 and qa["short_edge_ratio"] < 0.5
    control_net_sane = qa["bspline_control_point_count"] <= 100000
    safety_pass = bool(qa["brep_valid"] and not qa["geometry_explosion"] and scale_sane and centroid_sane and degenerate_sane and control_net_sane)
    qa.update({
        "reload_valid": qa["brep_valid"],
        "centroid_error_normalized": centroid_error,
        "centroid_sane": centroid_sane,
        "scale_sane": scale_sane,
        "degenerate_geometry_sane": degenerate_sane,
        "control_net_sane": control_net_sane,
        "safety_pass": safety_pass,
    })
    runtime_config = {
        "representation": representation,
        "sections": sections,
        "profile_count": profiles,
        "tolerance": tolerance,
    }
    runtime_input = {
        "source_mesh_sha256": sha256(source_mesh),
        "runtime_config": runtime_config,
        "transform_metadata": transform_metadata,
    }
    provenance = {
        "case_id": "CASE09",
        "part_id": part_id,
        "semantic_role": role,
        "candidate_id": f"{part_id}_V6_MAINLINE_FRESH",
        "candidate_source": "V6_GEOMETRY_BACKEND",
        "candidate_kind": "AUDITED_EXTERNAL_GEOMETRY_BACKEND",
        "source_mesh_path": str(source_mesh),
        "source_mesh_sha256": sha256(source_mesh),
        "source_mesh_read_at_utc": datetime.now(timezone.utc).isoformat(),
        "v6_generator_entrypoint": "v6_runtime.build_candidate",
        "v6_generator_code_hash": sha256(V6_RUNTIME),
        "v6_config_hash": hashlib.sha256(json.dumps(runtime_config, sort_keys=True).encode()).hexdigest(),
        "runtime_input_hash": hashlib.sha256(json.dumps(runtime_input, sort_keys=True).encode()).hexdigest(),
        "fresh_step_path": str(output_step),
        "fresh_step_sha256": sha256(output_step),
        "pre_export_shape_signature": signature(shape),
        "reload_shape_signature": signature(reloaded),
        "brep_valid": qa["brep_valid"],
        "reload_valid": qa["reload_valid"],
        "safety_pass": safety_pass,
        "historical_step_reused": False,
        "audit_step_reused": False,
        "source_mesh_read_count": 1,
    }
    return MainlineV6Candidate(part_id, role, provenance["candidate_id"], source_mesh, output_step, representation, shape, reloaded, qa, provenance)
