from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from .common import load_json, sha256, write_step


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V11B = ROOT / "v11b_real_qwen_mac_open_shell_closure"
V10 = ROOT / "v10_geometry_gated_builder_contract_closure"
V12 = ROOT / "v12_full_cad_part_router"
AUDIT = ROOT / "cross_case_geometry_explosion_audit_v1"


def replay(part_id: str, output_root: Path) -> dict[str, Any]:
    sys.path[:0] = [str(V11B), str(V10), str(AUDIT)]
    from execution import registry

    part_root = V12 / "cases/CASE09/parts" / part_id
    plan = load_json(part_root / "selected/structured_plan.json")
    result_doc = load_json(part_root / "selected/resolved_plan.json")
    eligibility = load_json(part_root / "builder_eligibility.json")
    resolved = result_doc["validation"]["resolved"]
    guard_cfg = yaml.safe_load((V10 / "config/builder_guards.yaml").read_text(encoding="utf-8"))
    counters: dict[str, int] = {}
    result = registry.execute(plan, eligibility, {}, guard_cfg, counters, resolved=resolved)
    if not result.get("FRESH_BREP") or result.get("shape") is None:
        raise RuntimeError(f"CURRENT_REPLAY_FAILED:{part_id}:{result.get('error')}")
    output = output_root / "cases/CASE09" / part_id / "CURRENT_BUILDER_REPLAY" / "fresh.step"
    write_step(result["shape"], output)
    return {
        "part_id": part_id,
        "candidate_source": "CURRENT_GEOMETRY_BACKEND",
        "candidate_kind": "V11_BUILDER_REGISTRY_REPLAY",
        "builder": result.get("builder"),
        "step_path": str(output),
        "step_sha256": sha256(output),
        "fresh_brep": True,
        "historical_step_reused": False,
        "runtime_source_mesh_read_count": 0,
        "invalid_builder_executed_count": counters.get("INVALID_BUILDER_REQUEST", 0),
    }
