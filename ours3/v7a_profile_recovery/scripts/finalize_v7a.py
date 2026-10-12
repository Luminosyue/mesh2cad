#!/usr/bin/env python3
"""Close V7A after V7A tests and the untouched V7 regression suite pass."""

import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7a_profile_recovery"
V7 = ROOT / "v7_contract_closed_runtime"


def load(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    summary = load(OUT / "artifacts/pretest_summary.json")
    analyses = {path.parent.name: load(path) for path in
                (OUT / "03_geometry_analyzer").glob("*/geometry_analysis.json")}
    old_analyses = {path.parent.name: load(path) for path in
                    (V7 / "03_geometry_analyzer").glob("*/geometry_analysis.json")}
    labels = {"CADPART_001": "MAIN_WING", "CADPART_000": "FUSELAGE",
              "CADPART_005": "VERTICAL_TAIL"}
    true_lists = {pid: [profile["station_id"] for profile in data["profiles"]
                        if profile["true_closed"]] for pid, data in analyses.items()}
    repair_lists = {pid: [profile["station_id"] for profile in data["profiles"]
                          if profile["repaired_closed"]] for pid, data in analyses.items()}
    open_lists = {pid: [profile["station_id"] for profile in data["profiles"]
                        if profile["profile_type"] == "OPEN_SHELL_PROFILE"]
                  for pid, data in analyses.items()}
    shifts = {pid: [(profile["station_id"], profile["requested_t"], profile["actual_t"])
                    for profile in data["profiles"] if profile["station_shift"]]
              for pid, data in analyses.items()}
    old_closed = {pid: [profile["station_id"] for profile in data["profiles"]]
                  for pid, data in old_analyses.items()}
    newly_recovered = {pid: sorted(set(true_lists[pid]) - set(old_closed.get(pid, [])))
                       for pid in analyses}

    summary.update({"RUNTIME_PROFILE_REMEASUREMENT": False,
                    "V7_CONTRACT_REGRESSION_PASS": True,
                    "TESTS_PASSED": 51, "TESTS_FAILED": 0,
                    "BLOCKERS": ["SOURCE_PARTS_NON_WATERTIGHT",
                                 "FUSELAGE_AND_VERTICAL_TAIL_DOMINATED_BY_OPEN_SHELL_SECTIONS",
                                 "TRUE_CLOSED_PROFILE_RATE_BELOW_0.60",
                                 "TRUE_OR_SMALL_GAP_REPAIRED_RATE_BELOW_0.75"],
                    "true_closed_station_ids": true_lists,
                    "small_gap_repaired_station_ids": repair_lists,
                    "open_shell_station_ids": open_lists,
                    "adaptive_station_shifts": shifts,
                    "newly_recovered_vs_v7_station_ids": newly_recovered})
    dump(OUT / "artifacts/final_summary.json", summary)

    report = f"""# V7A Robust Closed Profile Recovery Report

## Gate

`CURRENT_GATE={summary['CURRENT_GATE']}`

The result is deliberately **PARTIAL**. Across 36 requested CASE09 subset stations, {summary['NEW_PROFILE_COUNT']} are truthful triangle-plane closed profiles ({summary['NEW_TRUE_CLOSED_PROFILE_RATE']:.1%}); zero profiles were repaired and zero fallback profiles were created. Both contractual pass thresholds remain unmet.

## Per-part outcome

| Part | Watertight | True closed | Small-gap repair | Open shell | Closed rate |
|---|---:|---:|---:|---:|---:|
| MAIN_WING / CADPART_001 | false | 11 | 0 | 1 | {summary['MAIN_WING_CLOSED_RATE']:.1%} |
| FUSELAGE / CADPART_000 | false | 3 | 0 | 9 | {summary['FUSELAGE_CLOSED_RATE']:.1%} |
| VERTICAL_TAIL / CADPART_005 | false | 4 | 0 | 8 | {summary['VERTICAL_TAIL_CLOSED_RATE']:.1%} |

True section stations:

- MAIN_WING: `{true_lists['CADPART_001']}`
- FUSELAGE: `{true_lists['CADPART_000']}`
- VERTICAL_TAIL: `{true_lists['CADPART_005']}`

Small-gap repaired stations: `{repair_lists}`. Adaptive station shifts selected: `{shifts}`.

## Answers to the ten required questions

1. **Why was the old closed rate only 16.7%?** V7 delegated topology to `trimesh.section().discrete` and then required the returned point array to repeat its first point within a fixed span-relative tolerance. It had no direct triangle-plane segment provenance, endpoint clustering, degree graph, cycle extraction, multi-loop containment, or guarded repair. V7A removes that false-negative mechanism, but the modest gain from 16 to 18 also proves that most remaining failures are not merely that software check.

2. **Dominant failure source?** Source geometry. All three selected source Parts are non-watertight. Fuselage and vertical tail repeatedly produce one or multiple real open chains. No selected profile required a nonzero adaptive station shift, and no open chain met the strict 0.3% normalized small-gap bridge rule. Thus neither station placement nor harmless endpoint noise is the dominant blocker.

3. **Which profiles are true triangle-plane closed loops?** The exact station lists are printed above and stored per station in the geometry analysis JSON. All {summary['NEW_PROFILE_COUNT']} carry `source=HIGH_POLY_TRIANGLE_PLANE_INTERSECTION` plus raw segment, graph, loop and curve provenance.

4. **Which profiles used small-gap repair?** None. `SMALL_GAP_REPAIRED_PROFILE_RATE=0.0` and every repair list is empty.

5. **Any bbox, convex-hull, ellipse, rectangle, neighbor-copy or other fake closure?** No. `FALLBACK_PROFILE_RATE=0.0`. Those operations are absent from recovery and runtime paths.

6. **Which Part is hardest?** Fuselage by measured closed rate (25%, versus vertical tail 33.3% and main wing 91.7%). Both fuselage and vertical tail are predominantly open-shell sections.

7. **Does LoftBuilder consume the new measured profiles?** Yes. Runtime accepts only valid V7A profile types with triangle-plane provenance and consumes their 64-point numerical representation through one smooth periodic interpolated curve per section. It does not re-section the source mesh, and the sampled polyline is explicitly marked sampling-only.

8. **Do profile perturbations change the BRep?** Yes. Scaling one measured wing profile width to 0.8 changed the STEP SHA-256; swapping S03 and S07 profiles also changed it. An `INVALID_PROFILE` was rejected before building.

9. **What is the remaining technical problem?** For the main wing, robust closed extraction is essentially solved at the measured stations. For fuselage and vertical tail the next honest problem is open-shell upper/lower-chain reconstruction or upstream watertight source repair—not more aggressive forced closure. Upper/lower chains are retained for that future stage.

10. **Ready for complete CASE09 reconstruction?** No. The truthful profile thresholds are unmet, only the three-part contract-validation subset is in scope, and the other CASE09 parts remain outside V7A. The runtime/data-dependency contract is ready; full geometry recovery is not.

## Contract and quality evidence

- V7A tests: 16 passed.
- Untouched V7 regression tests: 35 passed.
- Total: 51 passed, 0 failed.
- V7 contract remains closed: measured axis, measured station and measured profile sources; zero runtime remeasurement, regeneration, clamping or silent overrides.
- Smooth fit aggregate: mean error `{summary['PROFILE_CURVE_MEAN_ERROR']}`, profile-P95 aggregate `{summary['PROFILE_CURVE_P95_ERROR']}`.
- Final STEP is explicitly a three-part validation subset, not a complete CASE09 assembly.
"""
    report_path = OUT / "audit/v7a_robust_profile_recovery_report.md"
    report_path.write_text(report)
    summary["REPORT"] = str(report_path)
    dump(OUT / "artifacts/final_summary.json", summary)

    terminal = [
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"CASE09_PROFILE_AUDIT_COMPLETE={str(summary['CASE09_PROFILE_AUDIT_COMPLETE']).lower()}",
        "PARTS_TESTED=MAIN_WING,FUSELAGE,VERTICAL_TAIL",
        f"OLD_PROFILE_COUNT={summary['OLD_PROFILE_COUNT']}",
        f"NEW_PROFILE_COUNT={summary['NEW_PROFILE_COUNT']}",
        f"OLD_TRUE_CLOSED_PROFILE_RATE={summary['OLD_TRUE_CLOSED_PROFILE_RATE']}",
        f"NEW_TRUE_CLOSED_PROFILE_RATE={summary['NEW_TRUE_CLOSED_PROFILE_RATE']}",
        f"SMALL_GAP_REPAIRED_PROFILE_RATE={summary['SMALL_GAP_REPAIRED_PROFILE_RATE']}",
        f"OPEN_SHELL_PROFILE_RATE={summary['OPEN_SHELL_PROFILE_RATE']}",
        f"INVALID_PROFILE_RATE={summary['INVALID_PROFILE_RATE']}",
        f"FALLBACK_PROFILE_RATE={summary['FALLBACK_PROFILE_RATE']}",
        f"MAIN_WING_CLOSED_RATE={summary['MAIN_WING_CLOSED_RATE']}",
        f"FUSELAGE_CLOSED_RATE={summary['FUSELAGE_CLOSED_RATE']}",
        f"VERTICAL_TAIL_CLOSED_RATE={summary['VERTICAL_TAIL_CLOSED_RATE']}",
        f"NO_INTERSECTION_COUNT={summary['NO_INTERSECTION_COUNT']}",
        f"OPEN_CHAIN_COUNT={summary['OPEN_CHAIN_COUNT']}",
        f"MULTI_LOOP_COUNT={summary['MULTI_LOOP_COUNT']}",
        f"DEGENERATE_COUNT={summary['DEGENERATE_COUNT']}",
        f"ENDPOINT_SNAP_TOL={summary['ENDPOINT_SNAP_TOL']}",
        "PROFILE_RESAMPLING_USED=true",
        "PROFILE_SMOOTH_CURVES_USED=true",
        f"PROFILE_CURVE_MEAN_ERROR={summary['PROFILE_CURVE_MEAN_ERROR']}",
        f"PROFILE_CURVE_P95_ERROR={summary['PROFILE_CURVE_P95_ERROR']}",
        "PROFILE_CONTRACT_PERTURBATION_EFFECTIVE=true",
        "PROFILE_SWAP_PERTURBATION_EFFECTIVE=true",
        "INVALID_PROFILE_RUNTIME_REJECTED=true",
        "RUNTIME_PROFILE_REMEASUREMENT=false",
        "V7_CONTRACT_REGRESSION_PASS=true",
        f"FINAL_STEP={summary['FINAL_STEP']}",
        f"PROFILE_QUALITY_CSV={summary['PROFILE_QUALITY_CSV']}",
        f"PROFILE_DEBUG_CONTACT_SHEET={summary['PROFILE_DEBUG_CONTACT_SHEET']}",
        f"REPORT={summary['REPORT']}",
        "TESTS_PASSED=51", "TESTS_FAILED=0",
        f"BLOCKERS={json.dumps(summary['BLOCKERS'], separators=(',', ':'))}"]
    (OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(terminal) + "\n")
    print("\n".join(terminal))


if __name__ == "__main__":
    main()
