#!/usr/bin/env python3
"""One isolated official Multi-Agent-CAD run with JSON-only geometry input."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "part_to_cad_recovery_fix_v1"
MAC_REPO = Path("/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD")
PART = OUT / "case07/parts/CADPART_001"
RUN = PART / "candidates/route_a_mac"


def plain(value):
    if hasattr(value, "model_dump"):
        return plain(value.model_dump())
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    feature = json.loads((PART / "input/cad_feature_graph.json").read_text())
    measured = json.loads((PART / "input/measured_cad_spec.json").read_text())
    assert not feature.get("raw_mesh_included") and not measured.get("raw_mesh_included")
    request = """Generate one CAD part from the two authoritative JSON objects below.
Do not infer dimensions from an image or raw mesh: neither is supplied and accessing one is prohibited.
Use only explicit measured numbers and the feature hypotheses. Prefer a compact parametric
extrude/revolve/union construction. Save a valid STEP. Treat all dimensions as model units.

CAD_FEATURE_GRAPH_JSON:
{feature}

MEASURED_CAD_SPEC_JSON:
{measured}
""".format(feature=json.dumps(feature, sort_keys=True), measured=json.dumps(measured, sort_keys=True))

    os.chdir(RUN)
    sys.path.insert(0, str(MAC_REPO))
    from multi_agent_cad import nodes
    nodes._CACHE_DIR = RUN / "pipeline_cache"
    from multi_agent_cad.graph import build_graph, get_default_initial_state
    from multi_agent_cad.token_tracker import tracker

    tracker.reset()
    state = get_default_initial_state(workflow_id="part_to_cad_case07_part001")
    state["user_request"] = request
    state["force_refresh"] = True
    started = time.time()
    final_state = dict(state)
    events = []
    error = None
    try:
        app = build_graph()
        for event in app.stream(state, {"recursion_limit": 50}):
            events.append(plain(event))
            for update in event.values():
                if isinstance(update, dict):
                    final_state.update(update)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}

    result = {
        "schema": "STRICT_JSON_ONLY_MAC_RUN_V1",
        "case_id": "CASE_07",
        "part_id": "CADPART_001",
        "official_entry": "multi_agent_cad.graph.build_graph",
        "input_files": [str(PART / "input/cad_feature_graph.json"), str(PART / "input/measured_cad_spec.json")],
        "raw_mesh_supplied": False,
        "elapsed_seconds": time.time() - started,
        "error": error,
        "token_usage": tracker.summary(),
        "final_state": plain(final_state),
        "events": events,
    }
    step = final_state.get("current_step_path")
    if step and Path(step).is_file():
        dst = RUN / "candidate.step"
        shutil.copy2(step, dst)
        result["candidate_step"] = str(dst)
        result["step_exists"] = True
    else:
        result["candidate_step"] = None
        result["step_exists"] = False
    (RUN / "mac_run_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("error", "elapsed_seconds", "token_usage", "candidate_step", "step_exists")}, indent=2))


if __name__ == "__main__":
    main()
