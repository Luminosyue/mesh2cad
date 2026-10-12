#!/usr/bin/env python3
"""Finalize CASE01 diagnosis from already-written fresh QA. Performs no geometry work."""
import hashlib
import json
from pathlib import Path

PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = PROJECT / "parallel_pipeline_diagnostics_v1/task_c"
PIPELINE = PROJECT / "batch_real_mesh2cad_v1/scripts/batch_pipeline.py"

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def dump(p, v):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    names = ["candidate_A_loft", "candidate_B_loft", "candidate_C_primitive"]
    audits = [load(OUT / "candidates" / n / "fresh_qa.json") for n in names]
    by = {x["candidate"]: x for x in audits}
    lines = PIPELINE.read_text(encoding="utf-8").splitlines()
    control = {
        "path": str(PIPELINE), "sha256": sha(PIPELINE), "line_range_1_based": [146, 149],
        "source_lines": [{"line": i, "text": lines[i-1]} for i in range(146, 150)],
        "interpretation": "The existence of any candidate_A_loft/candidate.step is treated as an unconditional terminal failure sentinel. The branch writes FAIL and continues before build_one can fresh-QA and rank existing/generated candidates B and C.",
    }
    dump(OUT / "artifacts/case01_control_flow_evidence.json", control)

    graph = load(OUT / "artifacts/case01_provenance_graph.json")
    graph["nodes"].append({"id": "STALE_A_SENTINEL_BRANCH", "type": "CONTROL_FLOW", **control})
    graph["edges"] += [
        {"from": "candidate_A_loft", "to": "STALE_A_SENTINEL_BRANCH", "relation": "EXISTENCE_TRIGGERS_UNCONDITIONAL_FAIL"},
        {"from": "STALE_A_SENTINEL_BRANCH", "to": "candidate_B_loft", "relation": "SKIPS_FRESH_QA_AND_RANKING"},
        {"from": "STALE_A_SENTINEL_BRANCH", "to": "candidate_C_primitive", "relation": "SKIPS_FRESH_QA_AND_RANKING"},
    ]
    dump(OUT / "artifacts/case01_provenance_graph.json", graph)

    sections = load(OUT / "artifacts/case01_geometry_hypothesis_audit.json")["loft_section_audits"]["candidate_A_loft"]
    rootcause = {
        "schema": "CASE01_RECOVERY_ROOTCAUSE_V1",
        "PRIMARY_ROOT_CAUSE": "OTHER",
        "PRIMARY_ROOT_CAUSE_DETAIL": "STALE_CANDIDATE_A_FAILURE_SENTINEL_SKIPPED_VALID_B_AND_C_QA_SELECTION",
        "SECONDARY_ROOT_CAUSES": ["SURFACE_FIT_FAILURE", "BRep_VALID_BUT_GEOMETRY_Q3"],
        "CAUSES_EXPLICITLY_REJECTED": ["RESOURCE_TIMEOUT_ONLY", "TRANSFORM_FAILURE", "LOFT_SECTION_ORDER_FAILURE", "LOFT_TWIST_FAILURE", "GEOMETRY_HYPOTHESIS_WRONG", "PART_DECOMPOSITION_WRONG"],
        "CASE01_RESOURCE_FAILURE": True,
        "CASE01_GEOMETRY_FAILURE": True,
        "CASE01_GEOMETRY_FAILURE_SCOPE": "CANDIDATE_A_SMOOTH_LOFT_ONLY",
        "RESOURCE_TIMEOUT_ONLY_REJECTED": True,
        "evidence": {
            "control_flow": control,
            "candidate_A": {"brep_valid": by["candidate_A_loft"]["brep_valid"], "geometry_q": by["candidate_A_loft"]["geometry_q"], "metrics": by["candidate_A_loft"]["geometry_metrics"], "bbox_sanity": by["candidate_A_loft"]["bbox_sanity"], "surface_histogram": by["candidate_A_loft"]["surface_histogram"]},
            "candidate_B": {"brep_valid": by["candidate_B_loft"]["brep_valid"], "geometry_q": by["candidate_B_loft"]["geometry_q"], "metrics": by["candidate_B_loft"]["geometry_metrics"], "bbox_sanity": by["candidate_B_loft"]["bbox_sanity"], "surface_histogram": by["candidate_B_loft"]["surface_histogram"]},
            "candidate_C": {"brep_valid": by["candidate_C_primitive"]["brep_valid"], "geometry_q": by["candidate_C_primitive"]["geometry_q"], "metrics": by["candidate_C_primitive"]["geometry_metrics"], "bbox_sanity": by["candidate_C_primitive"]["bbox_sanity"], "surface_histogram": by["candidate_C_primitive"]["surface_histogram"]},
            "section_order": {k: sections[k] for k in ["z_strictly_monotonic", "signed_area_orientation_changes", "self_intersecting_section_count", "adjacent_best_reversal_count", "adjacent_large_shift_count", "max_adjacent_area_ratio"]},
        },
        "reasoning": [
            "The batch continuation branch keys only on candidate A STEP existence and marks CASE01 failed before the ordinary build_one QA/ranking path.",
            "Fresh independent QA proves candidate B ruled loft and candidate C primitive are both BRep-valid Q1 in the saved source frame, so CASE01 was recoverable from artifacts that already existed.",
            "Candidate A smooth loft is BRep-valid but geometrically catastrophic: its mapped bbox diagonal is about 10,046 times source while B/C map to source scale. This is a secondary smooth surface-fit failure, not a transform failure.",
            "Section z order is monotonic, orientations do not flip, profiles do not self-intersect, and no large cyclic shifts/reversals occur. Section-order and twist failure are therefore rejected.",
            "The historical timeout is real but not sufficient: fresh A tessellation now completes, and valid Q1 B/C artifacts were bypassed by control flow.",
            "Because B and C fit the source at Q1, neither the whole-object hypothesis nor missing part decomposition explains the recorded CASE failure.",
        ],
        "RESCUE_ROUTE_A": {
            "name": "COMPLETE_EXISTING_CANDIDATE_RANKING",
            "plan_only": True,
            "steps": ["Replace the candidate-A-exists terminal sentinel with a resumable state that inventories all explicit candidates.", "Run the normal fresh QA/ranking path over A/B/C, retaining the saved transform and direct no-ICP protocol.", "Prefer candidate B over C when both pass because B preserves measured section variation and is marked programmatically simpler in the frozen adapter.", "Copy only the selected existing STEP into a new accepted output; never overwrite candidate inputs."],
            "expected_evidence": "Existing candidate B fresh QA: BRep valid, Q1, normalized Chamfer 0.002764, P95 0.005370, Coverage@2%=1.0."
        },
        "RESCUE_ROUTE_B": {
            "name": "STABILIZE_SMOOTH_LOFT_THEN_FALL_BACK_TO_RULED",
            "plan_only": True,
            "steps": ["Reject near-degenerate terminal profiles and cap them separately; the selected sections span a 378.2x adjacent area ratio.", "Add canonical bbox-growth and pole-magnitude guards immediately after smooth loft build.", "If the smooth loft exceeds source-scale bounds or fresh tessellation budget, mark only A failed and continue automatically to ruled B, not case-terminal failure.", "Require fresh STEP reload plus direct Q1/Q2 geometry QA before acceptance."],
            "expected_evidence": "A's smooth BSpline loft is valid but exploded; B uses identical ordered sections with ruled=True and remains source-scale Q1."
        },
        "REBUILD_EXECUTED": False, "MAC_LLM_CALLS": 0, "UNRESTRICTED_ICP_USED": False,
    }
    dump(OUT / "artifacts/case01_rootcause.json", rootcause)

    summary = {
        "CURRENT_GATE": "CASE01_RECOVERY_ROOTCAUSE_V1_PASS",
        "CASE_ID": "CASE_01", "PRIMARY_ROOT_CAUSE": rootcause["PRIMARY_ROOT_CAUSE"], "PRIMARY_ROOT_CAUSE_DETAIL": rootcause["PRIMARY_ROOT_CAUSE_DETAIL"],
        "SECONDARY_ROOT_CAUSES": rootcause["SECONDARY_ROOT_CAUSES"], "CAUSES_EXPLICITLY_REJECTED": rootcause["CAUSES_EXPLICITLY_REJECTED"],
        "CASE01_RESOURCE_FAILURE": True, "CASE01_GEOMETRY_FAILURE": True, "CASE01_GEOMETRY_FAILURE_SCOPE": rootcause["CASE01_GEOMETRY_FAILURE_SCOPE"], "RESOURCE_TIMEOUT_ONLY_REJECTED": True,
        "CANDIDATE_STEP_COUNT": 3, "CANDIDATE_RELOAD_SUCCESS": sum(x["step_reload_success"] for x in audits), "CANDIDATE_BREP_VALID": sum(x["brep_valid"] for x in audits),
        "CANDIDATE_Q1": sum(x["geometry_q"] == "Q1" for x in audits), "CANDIDATE_Q3": sum(x["geometry_q"] == "Q3" for x in audits),
        "RECOVERABLE_EXISTING_CANDIDATES": [x["candidate"] for x in audits if x["geometry_q"] in ("Q1", "Q2")],
        "CANDIDATES": [{"candidate": x["candidate"], "sha256": x["step_sha256"], "brep_valid": x["brep_valid"], "geometry_q": x["geometry_q"], "faces": x["counts"]["faces"], "triangles": x["tessellation_triangle_count"], "raw_bbox_diagonal": x["raw_bbox_diagonal"], "mapped_bbox_diagonal": x["mapped_bbox_diagonal"], **x["geometry_metrics"]} for x in audits],
        "RESCUE_ROUTE_A": rootcause["RESCUE_ROUTE_A"]["name"], "RESCUE_ROUTE_B": rootcause["RESCUE_ROUTE_B"]["name"],
        "REBUILD_EXECUTED": False, "MAC_LLM_CALLS": 0, "UNRESTRICTED_ICP_USED": False,
        "OUTPUT_ROOT": str(OUT), "PROVENANCE_GRAPH": str(OUT / "artifacts/case01_provenance_graph.json"), "REPORT": str(OUT / "artifacts/case01_recovery_rootcause_report.md"),
        "TESTS_PASSED": 0, "TESTS_FAILED": 0, "BLOCKERS": [],
    }
    dump(OUT / "artifacts/task_c_summary.json", summary)
    report = [
        "# CASE01_RECOVERY_ROOTCAUSE_V1", "", f"Gate: `{summary['CURRENT_GATE']}`", "",
        "## Finding", "", f"Primary enum: `{rootcause['PRIMARY_ROOT_CAUSE']}`", "", f"Detail: `{rootcause['PRIMARY_ROOT_CAUSE_DETAIL']}`", "",
        "CASE01's recorded failure is primarily a control-flow/resume defect, not a geometry-wide failure. `batch_pipeline.py:146-149` treats the mere existence of candidate A STEP as a terminal failure sentinel and executes `continue`, bypassing the normal QA/ranking path. Fresh independent QA shows the already-existing ruled B and primitive C candidates are both valid Q1.", "",
        "## Fresh candidate evidence", "",
    ]
    for x in audits:
        m=x["geometry_metrics"]; report.append(f"- `{x['candidate']}`: valid={x['brep_valid']}; faces={x['counts']['faces']}; Q={x['geometry_q']}; Chamfer={m['normalized_symmetric_chamfer']:.9f}; P95={m['normalized_p95']:.9f}; Coverage@2%={m['source_coverage_020']:.6f}; mapped/source diag ratio={x['bbox_sanity']['mapped_to_source_diagonal_ratio']:.6f}.")
    report += ["", "## Cause separation", "", "- Resource event: true; the historical smooth-loft retessellation timeout is evidenced.", "- Geometry failure: true but limited to A; A's valid BSpline BRep explodes to ~10,046x source diagonal.", "- `RESOURCE_TIMEOUT_ONLY`: rejected because A can now be retessellated and Q1 B/C were already present but skipped.", "- `TRANSFORM_FAILURE`: rejected because the same finite inverse-consistent transform maps B/C to source scale.", "- Section-order/twist failure: rejected; z is monotonic, orientation changes=0, self-intersecting profiles=0, large shifts=0, reversals=0.", "", "## Secondary causes", "", "- `SURFACE_FIT_FAILURE`: smooth A is numerically pathological while ruled B from identical sections is Q1.", "- `BRep_VALID_BUT_GEOMETRY_Q3`: A is topologically valid yet geometrically catastrophic.", "", "## Rescue plans — not executed", "", f"- Route A `{rootcause['RESCUE_ROUTE_A']['name']}`: resume candidate inventory and normal QA/ranking; select existing B when it remains Q1.", f"- Route B `{rootcause['RESCUE_ROUTE_B']['name']}`: guard smooth-loft bounds/poles, remove degenerate end profiles, and fall through to ruled B on A failure.", "", "No reconstruction, MAC/LLM call, unrestricted ICP, CASE09 work, shared-code edit, or input STEP overwrite was performed.", ""]
    (OUT / "artifacts/case01_recovery_rootcause_report.md").write_text("\n".join(report), encoding="utf-8")

if __name__ == "__main__": main()
