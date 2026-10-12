#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_case09_style_fullstack_v6_2/artifacts/remaining_audit.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def valid_step(path: Path):
    if not path.is_file():
        return False
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        return False
    if reader.TransferRoots() <= 0:
        return False
    shape = reader.OneShape()
    return not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid()


expected = []
for graph_path in sorted((BASE / "02_cad_part_graph").glob("CASE_*/cad_part_graph.json")):
    graph = load(graph_path)
    case_id = graph["case_id"]
    for node in graph["nodes"]:
        part_id = node["part_id"]
        hypotheses = load(BASE / "07_design_intent" / case_id / part_id / "design_intent_hypotheses.json")["hypotheses"]
        for index, hypothesis in enumerate(hypotheses, 1):
            expected.append((case_id, part_id, f"CANDIDATE_{index:02d}_{hypothesis['representation']}"))

records = []
for case_id, part_id, candidate_id in expected:
    directory = BASE / "08_multi_candidate_mac" / case_id / part_id / candidate_id
    response_path = directory / "mac_response.json"
    manifest_path = directory / "candidate_manifest.json"
    response = load(response_path) if response_path.is_file() else {}
    manifest = load(manifest_path) if manifest_path.is_file() else {}
    parsed = response.get("parsed", {})
    generated = parsed.get("generated_code", "") if isinstance(parsed, dict) else ""
    real = bool(response.get("raw_response", "").strip() and generated.strip() and not response.get("error"))
    step_valid = valid_step(directory / "candidate.step") if real else False
    if real and step_valid:
        status = "REAL_VALID_COMPLETE"
    elif real:
        status = "REAL_RESPONSE_NEEDS_EXECUTION_OR_REPAIR"
    elif response.get("HTTP_STATUS") == 403 or "AllocationQuota.FreeTierOnly" in str(response.get("error", "")):
        status = "QUOTA_BLOCKED_RETRY"
    elif manifest.get("DETERMINISTIC_FALLBACK_QUOTA_BLOCKED"):
        status = "OLD_FALLBACK_REPLACE_WITH_REAL_MAC"
    elif response.get("error"):
        status = "FAILED_RETRY"
    else:
        status = "NOT_RUN"
    records.append({
        "case_id": case_id,
        "part_id": part_id,
        "candidate_id": candidate_id,
        "status": status,
        "real_response": real,
        "step_valid": step_valid,
    })

counts = defaultdict(int)
per_case = {}
for record in records:
    counts[record["status"]] += 1
for case_id in sorted({record["case_id"] for record in records}):
    case_records = [record for record in records if record["case_id"] == case_id]
    parts = {record["part_id"] for record in case_records}
    complete_parts = {
        part_id for part_id in parts
        if sum(record["status"] == "REAL_VALID_COMPLETE" for record in case_records if record["part_id"] == part_id) >= 3
    }
    per_case[case_id] = {
        "parts": len(parts),
        "complete_tts_parts": len(complete_parts),
        "real_valid_candidates": sum(record["status"] == "REAL_VALID_COMPLETE" for record in case_records),
        "candidates_remaining": sum(record["status"] != "REAL_VALID_COMPLETE" for record in case_records),
    }

summary = {
    "EXPECTED_PARTS": len({(record["case_id"], record["part_id"]) for record in records}),
    "EXPECTED_CANDIDATES": len(records),
    "REAL_VALID_COMPLETE": counts["REAL_VALID_COMPLETE"],
    "CANDIDATES_REMAINING": len(records) - counts["REAL_VALID_COMPLETE"],
    "REAL_RESPONSE_NEEDS_EXECUTION_OR_REPAIR": counts["REAL_RESPONSE_NEEDS_EXECUTION_OR_REPAIR"],
    "QUOTA_BLOCKED_RETRY": counts["QUOTA_BLOCKED_RETRY"],
    "OLD_FALLBACK_REPLACE_WITH_REAL_MAC": counts["OLD_FALLBACK_REPLACE_WITH_REAL_MAC"],
    "FAILED_RETRY": counts["FAILED_RETRY"],
    "NOT_RUN": counts["NOT_RUN"],
    "COMPLETE_TTS_PARTS": sum(value["complete_tts_parts"] for value in per_case.values()),
    "PARTS_REMAINING": 132 - sum(value["complete_tts_parts"] for value in per_case.values()),
    "PER_CASE": per_case,
    "RECORDS": records,
}
OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({key: value for key, value in summary.items() if key != "RECORDS"}, indent=2, sort_keys=True))
