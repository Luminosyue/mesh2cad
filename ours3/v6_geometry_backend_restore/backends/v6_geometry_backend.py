from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V6_RUNTIME = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py"


@dataclass
class V6BackendCandidate:
    part_id: str
    semantic_role: str
    source_mesh: Path
    output_step: Path
    representation: str
    sections: int
    profile_count: int
    tolerance: float
    shape: Any
    effective_sections: int
    effective_profile_count: int
    source_mesh_read_count: int = 1


def _runtime():
    spec = importlib.util.spec_from_file_location("v6_geometry_runtime_backend", V6_RUNTIME)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


CONFIG = {
    "CADPART_000": ("FUSELAGE", "PERIODIC_GLOBAL_BSPLINE", 64, 32, 0.001),
    "CADPART_001": ("MAIN_WING_LEFT", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
    "CADPART_002": ("MAIN_WING_RIGHT", "RIGHT_WING_SEMANTIC_SKIN_REPAIR", 12, 10, 0.0002),
    "CADPART_003": ("TAILPLANE_LEFT", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
    "CADPART_005": ("VERTICAL_TAIL", "GLOBAL_UPPER_LOWER_SKINS", 64, 64, 0.001),
}


EFFECTIVE_PROFILE_CONFIG = {
    "CADPART_000": (14, 12),
    "CADPART_001": (24, 20),
    "CADPART_002": (10, 10),
    "CADPART_003": (12, 10),
    "CADPART_005": (12, 10),
}


def generate(part_id: str, source_mesh: Path, output_step: Path) -> V6BackendCandidate:
    role, representation, sections, profile_count, tolerance = CONFIG[part_id]
    output_step.parent.mkdir(parents=True, exist_ok=True)
    runtime = _runtime()
    shape = runtime.build_candidate(str(source_mesh), representation, str(output_step), sections, profile_count, tolerance)
    if not output_step.is_file() or output_step.stat().st_size == 0:
        raise RuntimeError(f"V6_FRESH_STEP_NOT_WRITTEN:{part_id}")
    effective_sections, effective_profile_count = EFFECTIVE_PROFILE_CONFIG[part_id]
    return V6BackendCandidate(
        part_id,
        role,
        source_mesh,
        output_step,
        representation,
        sections,
        profile_count,
        tolerance,
        shape,
        effective_sections,
        effective_profile_count,
    )
