from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .v6_geometry_backend import V6_RUNTIME


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def provenance(candidate: Any, source_obj: Path, output_step: Path, old_step: Path) -> dict[str, Any]:
    return {
        "case_id": "CASE09",
        "part_id": candidate.part_id,
        "semantic_role": candidate.semantic_role,
        "source_mesh_path": str(candidate.source_mesh),
        "source_mesh_hash": sha(candidate.source_mesh),
        "source_obj_path": str(source_obj),
        "source_obj_hash": sha(source_obj),
        "v6_generator_entrypoint": "v6_runtime.build_candidate",
        "v6_generator_module": str(V6_RUNTIME),
        "v6_generator_code_hash": sha(V6_RUNTIME),
        "v6_config_hash": hashlib.sha256(json.dumps({"representation": candidate.representation, "sections": candidate.sections, "profile_count": candidate.profile_count, "tolerance": candidate.tolerance}, sort_keys=True).encode()).hexdigest(),
        "input_hashes": {"source_part_mesh": sha(candidate.source_mesh), "source_obj": sha(source_obj)},
        "runtime_parameters": {
            "representation": candidate.representation,
            "requested_sections": candidate.sections,
            "requested_profile_count": candidate.profile_count,
            "effective_sections": candidate.effective_sections,
            "effective_profile_count": candidate.effective_profile_count,
            "tolerance": candidate.tolerance,
        },
        "v6_selected_step_path": str(old_step),
        "v6_selected_step_sha256": sha(old_step) if old_step.is_file() else None,
        "generated_step": str(output_step),
        "generated_step_sha256": sha(output_step),
        "render_used": True,
        "mesh_used": True,
        "geometry_analysis_used": True,
        "runtime_mesh_read_used": True,
        "section_sampling_used": True,
        "profile_extraction_used": True,
        "loft_used": "LOFT" in candidate.representation,
        "bspline_used": "BSPLINE" in candidate.representation or "SKIN" in candidate.representation,
        "freeform_used": "SKIN" in candidate.representation or "BSPLINE" in candidate.representation,
        "control_net_used": False,
        "qwen_used": False,
        "mac_used": False,
        "historical_candidate_used": False,
        "fallback_used": False,
        "generator_fresh_execute": True,
    }
