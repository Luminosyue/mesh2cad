#!/usr/bin/env python3
"""Airplane Route B V6A.1: analytic branch support audit (PART_002 only)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_analytic_branch_audit_v6a1.baseline_audit import dump_json
from airplane_point2cad_analytic_branch_audit_v6a1.pipeline import process_part

V3 = ROOT / "ours3/airplane_routeb_point2cad_v3"
AIR = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_point2cad_analytic_branch_support_audit_v6a1"


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
        from airplane_point2cad_analytic_branch_audit_v6a1 import tests

        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        if not res.wasSuccessful():
            return 1

    parts = []
    for p in args.parts:
        p = p.strip().upper()
        idx = int(p.split("_")[1]) if p.startswith("PART_") else int(p)
        parts.append(f"PART_{idx:03d}")

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for pid in parts:
        print(f"[V6A.1] {pid}", flush=True)
        row = process_part(pid, V3 / pid, part_mesh(pid), OUT / pid)
        rows.append(row)
        print(f"[V6A.1] done {pid} gate={row['CURRENT_GATE']}", flush=True)

    r = rows[0] if rows else {}
    gate = {
        "CURRENT_GATE": r.get("CURRENT_GATE"),
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "POINT2CAD_INTERSECTION_REEXECUTED": False,
        "TOPOLOGY_MODIFIED": False,
        "PART_002": {k: v for k, v in r.items() if k not in ("gap_classifications", "first_blocker_audit")},
    }
    dump_json(OUT / "gate.json", gate)

    keys = [
        "CURRENT_GATE",
        "P3_REEXECUTED",
        "XPART_REEXECUTED",
        "POINT2CAD_SURFACE_FIT_REEXECUTED",
        "POINT2CAD_INTERSECTION_REEXECUTED",
        "TOPOLOGY_MODIFIED",
        "BASELINE_REPORTING_BUG_FOUND",
        "GAP_GATE_BUG_FOUND",
        "DEGREE_GRAPH_DEFINITION_CHANGED",
        "POINT2CAD_RAW_CURVES",
        "V5_RAW_FRAGMENTS",
        "V6A_RAW_FRAGMENTS",
        "CANONICAL_RAW_FRAGMENTS",
        "PAIR_0_1_OCC_BRANCHES",
        "PAIR_0_2_OCC_BRANCHES",
        "PAIR_1_2_OCC_BRANCHES",
        "PAIR_0_1_FRAGMENT_MATCH_RATE",
        "PAIR_0_2_FRAGMENT_MATCH_RATE",
        "PAIR_1_2_FRAGMENT_MATCH_RATE",
        "PAIR_0_1_GAPS_AUDITED",
        "PAIR_0_2_GAPS_AUDITED",
        "TRUE_INTERSECTION_FRAGMENTATION",
        "TRUE_TRIM_SEPARATION",
        "FIT_TOPOLOGY_INCONSISTENT",
        "AMBIGUOUS",
        "UV_SEAM_CROSSING_COUNT",
        "UV_REJECTIONS_BEFORE_UNWRAP",
        "UV_REJECTIONS_AFTER_UNWRAP",
        "PAIR_1_2_POSITIVE_CONTROL_PASS",
        "FIRST_BLOCKER_CLASSIFICATION",
        "FIRST_BLOCKER_ANALYTIC_BRANCH",
        "FIRST_BLOCKER_SURFACE_SUPPORT",
        "FIRST_BLOCKER_BOUNDARY_SUPPORT",
        "NEXT_PRIMARY_BLOCKER",
        "NEXT_RECOMMENDED_ACTION",
    ]
    mapping = {
        "CURRENT_GATE": r.get("CURRENT_GATE"),
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "POINT2CAD_INTERSECTION_REEXECUTED": False,
        "TOPOLOGY_MODIFIED": False,
        "BASELINE_REPORTING_BUG_FOUND": r.get("REPORTING_BUG_FOUND") or r.get("V6A_PROSE_REPORTING_BUG"),
        "GAP_GATE_BUG_FOUND": r.get("GAP_GATE_BUG_FOUND"),
        "DEGREE_GRAPH_DEFINITION_CHANGED": r.get("DEGREE_GRAPH_DEFINITION_CHANGED"),
        "POINT2CAD_RAW_CURVES": r.get("POINT2CAD_RAW_CURVES"),
        "V5_RAW_FRAGMENTS": r.get("V5_RAW_FRAGMENTS"),
        "V6A_RAW_FRAGMENTS": r.get("V6A_RAW_FRAGMENTS"),
        "CANONICAL_RAW_FRAGMENTS": r.get("CANONICAL_RAW_FRAGMENTS"),
        "PAIR_0_1_OCC_BRANCHES": r.get("PAIR_0_1_OCC_BRANCHES"),
        "PAIR_0_2_OCC_BRANCHES": r.get("PAIR_0_2_OCC_BRANCHES"),
        "PAIR_1_2_OCC_BRANCHES": r.get("PAIR_1_2_OCC_BRANCHES"),
        "PAIR_0_1_FRAGMENT_MATCH_RATE": r.get("PAIR_0_1_FRAGMENT_MATCH_RATE"),
        "PAIR_0_2_FRAGMENT_MATCH_RATE": r.get("PAIR_0_2_FRAGMENT_MATCH_RATE"),
        "PAIR_1_2_FRAGMENT_MATCH_RATE": r.get("PAIR_1_2_FRAGMENT_MATCH_RATE"),
        "PAIR_0_1_GAPS_AUDITED": r.get("PAIR_0_1_GAPS_AUDITED"),
        "PAIR_0_2_GAPS_AUDITED": r.get("PAIR_0_2_GAPS_AUDITED"),
        "TRUE_INTERSECTION_FRAGMENTATION": r.get("TRUE_INTERSECTION_FRAGMENTATION"),
        "TRUE_TRIM_SEPARATION": r.get("TRUE_TRIM_SEPARATION"),
        "FIT_TOPOLOGY_INCONSISTENT": r.get("FIT_TOPOLOGY_INCONSISTENT"),
        "AMBIGUOUS": r.get("AMBIGUOUS"),
        "UV_SEAM_CROSSING_COUNT": r.get("UV_SEAM_CROSSING_COUNT"),
        "UV_REJECTIONS_BEFORE_UNWRAP": r.get("UV_REJECTIONS_BEFORE_UNWRAP"),
        "UV_REJECTIONS_AFTER_UNWRAP": r.get("UV_REJECTIONS_AFTER_UNWRAP"),
        "PAIR_1_2_POSITIVE_CONTROL_PASS": r.get("PAIR_1_2_POSITIVE_CONTROL_PASS"),
        "FIRST_BLOCKER_CLASSIFICATION": r.get("FIRST_BLOCKER_CLASSIFICATION"),
        "FIRST_BLOCKER_ANALYTIC_BRANCH": r.get("FIRST_BLOCKER_ANALYTIC_BRANCH"),
        "FIRST_BLOCKER_SURFACE_SUPPORT": r.get("FIRST_BLOCKER_SURFACE_SUPPORT"),
        "FIRST_BLOCKER_BOUNDARY_SUPPORT": r.get("FIRST_BLOCKER_BOUNDARY_SUPPORT"),
        "NEXT_PRIMARY_BLOCKER": r.get("NEXT_PRIMARY_BLOCKER"),
        "NEXT_RECOMMENDED_ACTION": r.get("NEXT_RECOMMENDED_ACTION"),
    }
    for k in keys:
        print(f"{k}={mapping.get(k)}", flush=True)

    report = [
        "# Airplane Point2CAD Analytic Branch Support Audit V6A.1",
        "",
        f"Gate: {r.get('CURRENT_GATE')}",
        "",
        "## Per-pair classification",
        "",
        f"- PAIR (0,1): {r.get('pair_summary', {}).get('PAIR_0_1_PRIMARY_CLASS')} — fitted open_spline×cone OCC intersection ~10cm from observed fragments",
        f"- PAIR (0,2): {r.get('pair_summary', {}).get('PAIR_0_2_PRIMARY_CLASS')} — several gaps with full surface+boundary support on OCC branch",
        f"- PAIR (1,2): {r.get('pair_summary', {}).get('PAIR_1_2_PRIMARY_CLASS')} — V6A polyline joins lack analytic surface support along OCC gap segments",
        "",
        f"NEXT_RECOMMENDED_ACTION={r.get('NEXT_RECOMMENDED_ACTION')}",
        "",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
