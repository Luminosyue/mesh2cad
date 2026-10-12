#!/usr/bin/env python3
"""Airplane Route B V6A2: analytic master edge recovery for PART_002 pair (0,2)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_analytic_master_edge_v6a2.candidates import dump_json
from airplane_point2cad_analytic_master_edge_v6a2.pipeline import process_part

V3 = ROOT / "ours3/airplane_routeb_point2cad_v3"
AIR = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_point2cad_analytic_master_edge_recovery_v6a2"
V6A1_SRC = ROOT / "ours3/airplane_point2cad_analytic_branch_support_audit_v6a1/PART_002/repair_candidates/repair_candidate.json"


def part_mesh(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parts", nargs="+", default=["PART_002"])
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    if args.run_tests:
        import unittest
        from airplane_point2cad_analytic_master_edge_v6a2 import tests

        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        if not res.wasSuccessful():
            return 1

    # prove V6A.1 source not overwritten before run
    src_before = V6A1_SRC.read_bytes() if V6A1_SRC.is_file() else b""

    parts = []
    for p in args.parts:
        p = p.strip().upper()
        idx = int(p.split("_")[1]) if p.startswith("PART_") else int(p)
        parts.append(f"PART_{idx:03d}")

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for pid in parts:
        print(f"[V6A2] {pid} pair=(0,2)", flush=True)
        row = process_part(pid, V3 / pid, part_mesh(pid), OUT / pid)
        rows.append(row)
        print(
            f"[V6A2] done {pid} parametric={row.get('RECOVERED_PARAMETRIC_EDGES')} "
            f"gate={row.get('CURRENT_GATE')}",
            flush=True,
        )

    src_after = V6A1_SRC.read_bytes() if V6A1_SRC.is_file() else b""
    if src_before != src_after:
        print("ERROR: V6A.1 repair_candidate.json was modified", flush=True)
        return 1

    r = rows[0] if rows else {}
    skip = {"_extracted", "_pair_frags", "_results", "_master_branches", "candidate_results"}
    gate = {k: v for k, v in r.items() if k not in skip}
    dump_json(OUT / "gate.json", gate)

    keys = [
        "CURRENT_GATE",
        "P3_REEXECUTED",
        "XPART_REEXECUTED",
        "POINT2CAD_SURFACE_FIT_REEXECUTED",
        "POINT2CAD_INTERSECTION_REEXECUTED",
        "TARGET_PART",
        "TARGET_SURFACE_PAIR",
        "EXPECTED_ELIGIBLE_REPAIR_CANDIDATES",
        "FOUND_ELIGIBLE_REPAIR_CANDIDATES",
        "RECOVERED_PARAMETRIC_EDGES",
        "RECOVERED_3D_ONLY_EDGES",
        "REVALIDATION_FAILED",
        "BRANCH_MATCH_FAILED",
        "PARAMETER_INTERVAL_FAILED",
        "OCC_EDGE_BUILD_FAILED",
        "DUAL_PCURVE_FAILED",
        "EDGE_ORIENTATION_FAILED",
        "AMBIGUOUS",
        "PAIR_0_2_FRAGMENTS_REPLACED",
        "PAIR_0_2_FRAGMENT_COUNT_BEFORE",
        "PAIR_0_2_FRAGMENT_COUNT_AFTER",
        "PAIR_0_2_BRANCH_COUNT_BEFORE",
        "PAIR_0_2_BRANCH_COUNT_AFTER",
        "PAIR_0_2_DEGREE1_BEFORE",
        "PAIR_0_2_DEGREE1_AFTER",
        "PAIR_0_2_DEGREE2_BEFORE",
        "PAIR_0_2_DEGREE2_AFTER",
        "PAIR_0_2_BOUNDARY_COVERAGE_BEFORE",
        "PAIR_0_2_BOUNDARY_COVERAGE_AFTER",
        "PAIR_0_2_SUPPORTED_EDGE_LENGTH_BEFORE",
        "PAIR_0_2_SUPPORTED_EDGE_LENGTH_AFTER",
        "SHARED_OCC_EDGE_COUNT_BEFORE",
        "SHARED_OCC_EDGE_COUNT_AFTER",
        "NEW_SHARED_OCC_EDGES",
        "DUAL_PCURVE_ATTEMPTS",
        "DUAL_PCURVE_SUCCESS",
        "MEAN_MASTER_EDGE_TO_XPART_P95",
        "MAX_MASTER_EDGE_TO_XPART_P95",
        "MIN_BOUNDARY_SUPPORT_FRACTION",
        "WHOLE_PART_OPEN_WIRES_BEFORE",
        "WHOLE_PART_OPEN_WIRES_AFTER",
        "WHOLE_PART_CLOSED_WIRES_BEFORE",
        "WHOLE_PART_CLOSED_WIRES_AFTER",
        "WHOLE_PART_VALID_TRIMMED_FACES_BEFORE",
        "WHOLE_PART_VALID_TRIMMED_FACES_AFTER",
        "CLOSED_SHELLS",
        "CLEAN_PARAMETRIC_PART_SOLIDS",
        "PAIR_DEBUG_STEP_EXPORTED",
        "PAIR_DEBUG_STEP_RELOAD_VALID",
        "WHOLE_DIAGNOSTIC_STEP_EXPORTED",
        "WHOLE_DIAGNOSTIC_STEP_RELOAD_VALID",
        "FIRST_LOCAL_WIRE_BLOCKER",
        "V6A2_PRIMARY_BLOCKER",
        "PART_LEVEL_PRIMARY_BLOCKER",
        "NEXT_RECOMMENDED_ACTION",
    ]
    for k in keys:
        print(f"{k}={r.get(k)}", flush=True)

    lines = [
        "# Airplane Point2CAD Analytic Master Edge Recovery V6A2",
        "",
        f"Gate: {r.get('CURRENT_GATE')}",
        "",
        "## Candidate table",
        "",
        "| Candidate | Status | OCC branch | Edge type | P95 | Boundary support | Dual pcurve |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for c in r.get("candidate_results") or []:
        lines.append(
            f"| {c.get('candidate_id')} | {c.get('status')} | {c.get('RESOLVED_OCC_BRANCH')} | "
            f"{c.get('MASTER_EDGE_CURVE_TYPE')} | {c.get('surface_distance_p95')} | "
            f"{c.get('boundary_support_fraction')} | {c.get('DUAL_PCURVE_SUCCESS')} |"
        )
    lines += [
        "",
        f"V6A2_PRIMARY_BLOCKER={r.get('V6A2_PRIMARY_BLOCKER')}",
        f"PART_LEVEL_PRIMARY_BLOCKER={r.get('PART_LEVEL_PRIMARY_BLOCKER')}",
        f"NEXT_RECOMMENDED_ACTION={r.get('NEXT_RECOMMENDED_ACTION')}",
        "",
        "Did not enter V6B. Did not refit surfaces. Did not repair (0,1) or (1,2).",
        "",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
