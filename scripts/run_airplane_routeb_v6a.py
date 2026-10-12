#!/usr/bin/env python3
"""Airplane Route B V6A: intersection branch recovery for PART_002."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from airplane_point2cad_curve_branch_recovery_v6a.pipeline import dump_json, process_part

V3 = ROOT / "ours3/airplane_routeb_point2cad_v3"
AIR = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_point2cad_curve_branch_recovery_v6a"
DEFAULT_PARTS = ["PART_002"]


def part_mesh(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parts", nargs="+", default=DEFAULT_PARTS)
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()

    if args.run_tests:
        import unittest

        from airplane_point2cad_curve_branch_recovery_v6a import tests

        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        if not res.wasSuccessful():
            return 1

    norm = []
    for p in args.parts:
        p = p.strip().upper()
        if p.startswith("PART_"):
            idx = int(p.split("_")[1])
            norm.append(f"PART_{idx:03d}")
        else:
            norm.append(f"PART_{int(p):03d}")
    parts = norm or list(DEFAULT_PARTS)

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for pid in parts:
        print(f"[V6A] {pid}", flush=True)
        row = process_part(pid, V3 / pid, part_mesh(pid), OUT / pid)
        rows.append(row)
        print(
            f"[V6A] done {pid} frags={row['RAW_FRAGMENTS']} branches={row['RECOVERED_BRANCHES']} "
            f"d1 {row['DEGREE1_BEFORE']}->{row['DEGREE1_AFTER']} closed_wires={row['CLOSED_WIRES_AFTER']}",
            flush=True,
        )

    r002 = next((r for r in rows if r["part"] == "PART_002"), rows[0] if rows else {})
    gate_name = "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_PARTIAL_PASS"
    if int(r002.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0) >= 1 and int(r002.get("CLOSED_SHELLS") or 0) >= 1:
        if r002.get("GEOMETRY_PASS"):
            gate_name = "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_PASS"
    elif int(r002.get("ACCEPTED_CONNECTIONS") or 0) == 0:
        gate_name = "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_FAIL"

    gate = {
        "CURRENT_GATE": gate_name,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "PARTS": parts,
        "ARTIFACT_ROOT": str(OUT),
        "PART_002": r002,
        "NEXT_PRIMARY_BLOCKER": r002.get("NEXT_PRIMARY_BLOCKER"),
    }
    dump_json(OUT / "gate.json", gate)

    v5_path = ROOT / "ours3/airplane_point2cad_wire_closure_v5/PART_002/part_gate.json"
    v5 = json.loads(v5_path.read_text()) if v5_path.is_file() else {}

    report = [
        "# Airplane Point2CAD Curve Branch Recovery V6A",
        "",
        "## Before / After vs V5",
        "",
        "| Metric | V5 | V6A |",
        "| --- | ---: | ---: |",
        f"| official surface pairs | {v5.get('CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR')} | {r002.get('OFFICIAL_SURFACE_PAIRS')} |",
        f"| raw fragments | {v5.get('RAW_INTERSECTION_COMPONENTS')} | {r002.get('RAW_FRAGMENTS')} |",
        f"| recovered branches | N/A | {r002.get('RECOVERED_BRANCHES')} |",
        f"| accepted branch connections | N/A | {r002.get('ACCEPTED_CONNECTIONS')} |",
        f"| rejected branch connections | N/A | {r002.get('REJECTED_CONNECTIONS')} |",
        f"| degree1 endpoints | {v5.get('ENDPOINT_GRAPH_DEGREE1')} | {r002.get('DEGREE1_AFTER')} |",
        f"| degree2 endpoints | {v5.get('ENDPOINT_GRAPH_DEGREE2')} | {r002.get('DEGREE2_AFTER')} |",
        f"| open wires | {v5.get('OPEN_WIRES')} | {r002.get('OPEN_WIRES_AFTER')} |",
        f"| closed wires | {v5.get('CLOSED_WIRES')} | {r002.get('CLOSED_WIRES_AFTER')} |",
        f"| valid trimmed faces | {v5.get('VALID_TRIMMED_FACES')} | {r002.get('TRIMMED_FACES_VALID')} |",
        f"| free shell edges | {v5.get('FREE_EDGES_AFTER_SEW')} | {r002.get('FREE_SHELL_EDGES')} |",
        f"| closed shells | {v5.get('CLOSED_SHELLS')} | {r002.get('CLOSED_SHELLS')} |",
        f"| clean solids | {v5.get('CLEAN_PARAMETRIC_PART_SOLIDS')} | {r002.get('CLEAN_PARAMETRIC_PART_SOLIDS')} |",
        f"| STEP reload valid | {v5.get('STEP_RELOAD_VALID')} | {r002.get('STEP_RELOAD_VALID')} |",
        f"| IoU | {(v5.get('qa') or {}).get('IoU', 'N/A')} | {r002.get('IoU')} |",
        f"| Chamfer | N/A | {r002.get('Chamfer')} |",
        f"| Hausdorff | N/A | {r002.get('Hausdorff')} |",
        "",
        f"NEXT_PRIMARY_BLOCKER={r002.get('NEXT_PRIMARY_BLOCKER')}",
        f"first_blocker={r002.get('first_blocker')}",
        "",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n")

    keys = [
        "CURRENT_GATE",
        "P3_REEXECUTED",
        "XPART_REEXECUTED",
        "POINT2CAD_SURFACE_FIT_REEXECUTED",
        "PART_002_RAW_FRAGMENTS",
        "PART_002_RECOVERED_BRANCHES",
        "PART_002_ACCEPTED_CONNECTIONS",
        "PART_002_REJECTED_CONNECTIONS",
        "PART_002_DEGREE1_BEFORE",
        "PART_002_DEGREE1_AFTER",
        "PART_002_DEGREE2_BEFORE",
        "PART_002_DEGREE2_AFTER",
        "OPEN_WIRES_BEFORE",
        "OPEN_WIRES_AFTER",
        "CLOSED_WIRES_BEFORE",
        "CLOSED_WIRES_AFTER",
        "TRIMMED_FACES_VALID",
        "FREE_SHELL_EDGES",
        "CLOSED_SHELLS",
        "CLEAN_PARAMETRIC_PART_SOLIDS",
        "DUAL_PCURVE_SUCCESS",
        "SHARED_OCC_EDGE_COUNT",
        "STEP_EXPORTED",
        "STEP_RELOAD_VALID",
        "Chamfer",
        "Hausdorff",
        "Coverage",
        "FALSE_POSITIVE_OCCUPANCY",
        "IoU",
        "NEXT_PRIMARY_BLOCKER",
    ]
    mapping = {
        "CURRENT_GATE": gate_name,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "PART_002_RAW_FRAGMENTS": r002.get("RAW_FRAGMENTS"),
        "PART_002_RECOVERED_BRANCHES": r002.get("RECOVERED_BRANCHES"),
        "PART_002_ACCEPTED_CONNECTIONS": r002.get("ACCEPTED_CONNECTIONS"),
        "PART_002_REJECTED_CONNECTIONS": r002.get("REJECTED_CONNECTIONS"),
        "PART_002_DEGREE1_BEFORE": r002.get("DEGREE1_BEFORE"),
        "PART_002_DEGREE1_AFTER": r002.get("DEGREE1_AFTER"),
        "PART_002_DEGREE2_BEFORE": r002.get("DEGREE2_BEFORE"),
        "PART_002_DEGREE2_AFTER": r002.get("DEGREE2_AFTER"),
        "OPEN_WIRES_BEFORE": r002.get("OPEN_WIRES_BEFORE"),
        "OPEN_WIRES_AFTER": r002.get("OPEN_WIRES_AFTER"),
        "CLOSED_WIRES_BEFORE": r002.get("CLOSED_WIRES_BEFORE"),
        "CLOSED_WIRES_AFTER": r002.get("CLOSED_WIRES_AFTER"),
        "TRIMMED_FACES_VALID": r002.get("TRIMMED_FACES_VALID"),
        "FREE_SHELL_EDGES": r002.get("FREE_SHELL_EDGES"),
        "CLOSED_SHELLS": r002.get("CLOSED_SHELLS"),
        "CLEAN_PARAMETRIC_PART_SOLIDS": r002.get("CLEAN_PARAMETRIC_PART_SOLIDS"),
        "DUAL_PCURVE_SUCCESS": r002.get("DUAL_PCURVE_SUCCESS"),
        "SHARED_OCC_EDGE_COUNT": r002.get("SHARED_OCC_EDGE_COUNT"),
        "STEP_EXPORTED": r002.get("STEP_EXPORTED"),
        "STEP_RELOAD_VALID": r002.get("STEP_RELOAD_VALID"),
        "Chamfer": r002.get("Chamfer"),
        "Hausdorff": r002.get("Hausdorff"),
        "Coverage": r002.get("Coverage"),
        "FALSE_POSITIVE_OCCUPANCY": r002.get("FALSE_POSITIVE_OCCUPANCY"),
        "IoU": r002.get("IoU"),
        "NEXT_PRIMARY_BLOCKER": r002.get("NEXT_PRIMARY_BLOCKER"),
    }
    for k in keys:
        print(f"{k}={mapping[k]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
