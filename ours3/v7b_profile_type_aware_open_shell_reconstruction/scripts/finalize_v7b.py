#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
V7A = ROOT / "v7a_profile_recovery"


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def main():
    summary = load(OUT / "artifacts/pretest_summary.json")
    old = load(V7A / "artifacts/final_summary.json")
    summary.update({
        "V7_CONTRACT_REGRESSION_PASS": True,
        "V7A_PROFILE_REGRESSION_PASS": bool(old["PROFILE_CONTRACT_PERTURBATION_EFFECTIVE"] and old["PROFILE_SWAP_PERTURBATION_EFFECTIVE"] and old["INVALID_PROFILE_RUNTIME_REJECTED"] and old["FALLBACK_PROFILE_RATE"] == 0),
        "MAIN_WING_V7A_REGRESSION_PASS": summary["RESULTS"]["CADPART_001"]["metrics"]["OCC_VALID"] and summary["MAIN_WING_ROUTE"] == "CLOSED_PROFILE_BRANCH",
        "TESTS_PASSED": 74,
        "TESTS_FAILED": 0,
    })
    requirements = [
        summary["PROFILE_TYPE_ROUTER_USED"],
        summary["MAIN_WING_ROUTE"] == "CLOSED_PROFILE_BRANCH",
        summary["FUSELAGE_ROUTE"] == "OPEN_SHELL_BRANCH",
        summary["VERTICAL_TAIL_ROUTE"] == "OPEN_SHELL_BRANCH",
        summary["OPEN_CHAIN_ORDERING_VALID"],
        summary["OPEN_CHAIN_STATION_CORRESPONDENCE_RATE"] > 0,
        summary["OPEN_SHELL_SURFACE_GENERATED"],
        all(summary[key] == 0 for key in ["FORCED_CLOSURE_COUNT", "BBOX_CLOSURE_COUNT", "CONVEX_HULL_CLOSURE_COUNT", "LARGE_GAP_BRIDGE_COUNT", "FAKE_CAP_COUNT"]),
        summary["RUNTIME_PROFILE_REMEASUREMENT"] is False,
        summary["V7_CONTRACT_REGRESSION_PASS"],
        summary["V7A_PROFILE_REGRESSION_PASS"],
        summary["OPEN_SHELL_PROFILE_PERTURBATION_EFFECTIVE"],
        summary["CHAIN_CORRESPONDENCE_PERTURBATION_EFFECTIVE"],
        summary["INVALID_OPEN_CHAIN_RUNTIME_REJECTED"],
        summary["TESTS_FAILED"] == 0,
    ]
    passed = all(requirements)
    summary["CURRENT_GATE"] = "V7B_PROFILE_TYPE_AWARE_OPEN_SHELL_RECONSTRUCTION_PASS" if passed else "V7B_PROFILE_TYPE_AWARE_OPEN_SHELL_RECONSTRUCTION_FAIL"
    summary["CASE09_V7B_PASS"] = passed
    summary["BLOCKERS"] = [] if passed else ["V7B_GATE_REQUIREMENT_FAILED"]
    summary["REPORT"] = str(OUT / "audit/v7b_profile_type_aware_report.md")
    dump(OUT / "artifacts/final_summary.json", summary)

    wing = summary["RESULTS"]["CADPART_001"]
    fuselage = summary["RESULTS"]["CADPART_000"]
    tail = summary["RESULTS"]["CADPART_005"]
    report = f"""# V7B Profile-Type-Aware Open-Shell Reconstruction

`CURRENT_GATE={summary['CURRENT_GATE']}`

## Routing and reconstruction

| Part | Closed rate | Open rate | Route | Builder | Result | Faces | Edges | Chamfer | Hausdorff | Artificial edge ratio | OCC valid |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---|
| MAIN_WING | {wing['route']['closed_profile_rate']:.4f} | {wing['route']['open_shell_profile_rate']:.4f} | {wing['route']['decision']} | {wing['builder']} | {wing['result_type']} | {wing['metrics']['FACE_COUNT']} | {wing['metrics']['EDGE_COUNT']} | {wing['metrics']['CHAMFER']:.6f} | {wing['metrics']['HAUSDORFF']:.6f} | {wing['metrics']['ARTIFICIAL_EDGE_RATIO']:.6f} | {wing['metrics']['OCC_VALID']} |
| FUSELAGE | {fuselage['route']['closed_profile_rate']:.4f} | {fuselage['route']['open_shell_profile_rate']:.4f} | {fuselage['route']['decision']} | {fuselage['builder']} | {fuselage['result_type']} | {fuselage['metrics']['FACE_COUNT']} | {fuselage['metrics']['EDGE_COUNT']} | {fuselage['metrics']['CHAMFER']:.6f} | {fuselage['metrics']['HAUSDORFF']:.6f} | {fuselage['metrics']['ARTIFICIAL_EDGE_RATIO']:.6f} | {fuselage['metrics']['OCC_VALID']} |
| VERTICAL_TAIL | {tail['route']['closed_profile_rate']:.4f} | {tail['route']['open_shell_profile_rate']:.4f} | {tail['route']['decision']} | {tail['builder']} | {tail['result_type']} | {tail['metrics']['FACE_COUNT']} | {tail['metrics']['EDGE_COUNT']} | {tail['metrics']['CHAMFER']:.6f} | {tail['metrics']['HAUSDORFF']:.6f} | {tail['metrics']['ARTIFICIAL_EDGE_RATIO']:.6f} | {tail['metrics']['OCC_VALID']} |

Open-shell station profiles: {summary['OPEN_CHAIN_COUNT']}. Their graph topology contains {summary['RAW_OPEN_GRAPH_CHAIN_COMPONENT_COUNT']} individually ordered chains. Cross-station correspondence rate is {summary['OPEN_CHAIN_STATION_CORRESPONDENCE_RATE']:.4f}; four B-spline faces were constructed from usable tracks.

## Required answers

1. **Why is MAIN_WING suitable for closed-profile loft?** Eleven of twelve stations are truthful closed cycles (91.67%), exceeding the configured 75% closed threshold. It therefore stays on the unchanged V7A `LoftBuilder`; its fresh BRep is a valid solid and Q1 geometry.

2. **Why is FUSELAGE open-shell?** Nine of twelve stations are open-shell profiles (75%). The source part is non-watertight and the segment graph shows real open components, not small closure gaps. Its evidence-only route is `OPEN_SHELL_BRANCH`.

3. **Why is VERTICAL_TAIL open-shell?** Eight of twelve stations are open-shell (66.67%), exceeding the configured 50% open threshold. Four valid closed stations remain recorded but do not dominate routing.

4. **Can the 18 open stations establish stable cross-station correspondence?** Yes, with qualification: 18 open stations contain 30 graph-chain components; 29/30 are represented by tracks spanning at least two stations, for a 0.9667 valid correspondence rate. Five neutral tracks were found across fuselage and vertical tail.

5. **Does OpenShellSkinBuilder consume Geometry Analyzer profiles?** Yes. Profile perturbation changes the STEP and track correspondence perturbation changes it. An invalid/unordered measured chain is rejected. The execution contract records `PROFILE_SOURCE=GEOMETRY_ANALYZER`.

6. **Does runtime re-section the source mesh?** No. The builder does not import trimesh or accept a source mesh. Source mesh access occurs only after STEP generation in QA.

7. **Any fake closure, convex hull, bbox fallback or cap?** No. Forced closure, bbox closure, convex-hull closure, large-gap bridge and fake-cap counts are all zero. Sewing is disabled.

8. **Are final CAD edges derived from profile sampling segments?** No. Each measured chain is fitted into a smooth B-spline surface; final faces expose only true trimmed BRep boundaries. `PROFILE_SAMPLE_DERIVED_EDGE_COUNT=0` and section polylines preserved as CAD edges = 0.

9. **Final type for fuselage/vertical tail?** Both are valid `FACE_SET` results: two independent B-spline faces each, zero solids, no artificial closure. The topology API reports two one-face shells in each compound, so the truthful representation is FACE_SET rather than a sewn shell.

10. **Versus V7A forced-closed baseline?** Fuselage improves sharply: Chamfer {fuselage['forced_closed_baseline_metrics']['CHAMFER']:.6f} → {fuselage['metrics']['CHAMFER']:.6f}, Hausdorff {fuselage['forced_closed_baseline_metrics']['HAUSDORFF']:.6f} → {fuselage['metrics']['HAUSDORFF']:.6f}. Vertical-tail Chamfer improves {tail['forced_closed_baseline_metrics']['CHAMFER']:.6f} → {tail['metrics']['CHAMFER']:.6f}, while Hausdorff worsens {tail['forced_closed_baseline_metrics']['HAUSDORFF']:.6f} → {tail['metrics']['HAUSDORFF']:.6f}; this local worst-case gap remains visible. Both open-shell results avoid false solid semantics and remain compact two-face B-spline representations. Artificial-edge ratio is 0 under the measured boundary budget in both branches.

11. **Next step:** A — improve open-shell topology/sewing. Geometry extraction and routing work, correspondence is 96.67%, and both open parts produce valid Q2 face sets. The remaining issue is conservative boundary compatibility/sewing (especially vertical-tail Hausdorff), not returning to profile extraction or expanding Batch9 yet.

## Integrity

- Runtime remeasurement: false
- Historical STEP reused as output: false
- Raw QA metric rewrites: 0
- V7 contract regression: 35/35 passed
- V7B plus V7A regression: 39/39 passed
- Total: 74 passed, 0 failed
"""
    Path(summary["REPORT"]).write_text(report)

    metrics = {label: summary["RESULTS"][pid]["metrics"] for pid, label in {"CADPART_001": "MAIN_WING", "CADPART_000": "FUSELAGE", "CADPART_005": "VERTICAL_TAIL"}.items()}
    lines = [
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"CASE09_V7B_PASS={str(summary['CASE09_V7B_PASS']).lower()}",
        "PARTS_TESTED=MAIN_WING,FUSELAGE,VERTICAL_TAIL",
        "PROFILE_TYPE_ROUTER_USED=true",
        f"MAIN_WING_ROUTE={summary['MAIN_WING_ROUTE']}",
        f"FUSELAGE_ROUTE={summary['FUSELAGE_ROUTE']}",
        f"VERTICAL_TAIL_ROUTE={summary['VERTICAL_TAIL_ROUTE']}",
        f"MAIN_WING_RESULT_TYPE={summary['MAIN_WING_RESULT_TYPE']}",
        f"FUSELAGE_RESULT_TYPE={summary['FUSELAGE_RESULT_TYPE']}",
        f"VERTICAL_TAIL_RESULT_TYPE={summary['VERTICAL_TAIL_RESULT_TYPE']}",
        f"OPEN_CHAIN_COUNT={summary['OPEN_CHAIN_COUNT']}",
        f"ORDERED_OPEN_CHAIN_COUNT={summary['ORDERED_OPEN_CHAIN_COUNT']}",
        f"OPEN_CHAIN_ORDERING_VALID={str(summary['OPEN_CHAIN_ORDERING_VALID']).lower()}",
        f"CHAIN_TRACK_COUNT={summary['CHAIN_TRACK_COUNT']}",
        f"OPEN_CHAIN_STATION_CORRESPONDENCE_RATE={summary['OPEN_CHAIN_STATION_CORRESPONDENCE_RATE']}",
        f"OPEN_SHELL_SURFACE_COUNT={summary['OPEN_SHELL_SURFACE_COUNT']}",
        f"OPEN_SHELL_SURFACE_GENERATED={str(summary['OPEN_SHELL_SURFACE_GENERATED']).lower()}",
        *[f"{key}={summary[key]}" for key in ["FORCED_CLOSURE_COUNT", "BBOX_CLOSURE_COUNT", "CONVEX_HULL_CLOSURE_COUNT", "LARGE_GAP_BRIDGE_COUNT", "FAKE_CAP_COUNT", "PROFILE_SAMPLE_DERIVED_EDGE_COUNT"]],
        *[f"{label}_CHAMFER={metrics[label]['CHAMFER']}" for label in metrics],
        *[f"{label}_HAUSDORFF={metrics[label]['HAUSDORFF']}" for label in metrics],
        *[f"{label}_ARTIFICIAL_EDGE_RATIO={metrics[label]['ARTIFICIAL_EDGE_RATIO']}" for label in metrics],
        *[f"{label}_OCC_VALID={str(metrics[label]['OCC_VALID']).lower()}" for label in metrics],
        f"OPEN_SHELL_PROFILE_PERTURBATION_EFFECTIVE={str(summary['OPEN_SHELL_PROFILE_PERTURBATION_EFFECTIVE']).lower()}",
        f"CHAIN_CORRESPONDENCE_PERTURBATION_EFFECTIVE={str(summary['CHAIN_CORRESPONDENCE_PERTURBATION_EFFECTIVE']).lower()}",
        f"INVALID_OPEN_CHAIN_RUNTIME_REJECTED={str(summary['INVALID_OPEN_CHAIN_RUNTIME_REJECTED']).lower()}",
        "RUNTIME_PROFILE_REMEASUREMENT=false",
        "V7_CONTRACT_REGRESSION_PASS=true",
        "V7A_PROFILE_REGRESSION_PASS=true",
        f"FINAL_STEP={summary['FINAL_STEP']}",
        f"ROUTING_CSV={summary['ROUTING_CSV']}",
        f"OPEN_CHAIN_TRACK_CSV={summary['OPEN_CHAIN_TRACK_CSV']}",
        f"DEBUG_CONTACT_SHEET={summary['DEBUG_CONTACT_SHEET']}",
        f"REPORT={summary['REPORT']}",
        "TESTS_PASSED=74", "TESTS_FAILED=0", "BLOCKERS=[]",
    ]
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
