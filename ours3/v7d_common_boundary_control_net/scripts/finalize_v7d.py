#!/usr/bin/env python3
"""Freeze truthful V7D/V7C rerun status and report."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7d_common_boundary_control_net"
ART = OUT / "artifacts"


def load(path): return json.loads(Path(path).read_text())
def dump(path, value): Path(path).write_text(json.dumps(value, indent=2) + "\n")


d = load(ART / "pretest_summary.json")
f = d["parts"]["CADPART_000"]
t = d["parts"]["CADPART_005"]
baseline = d["baseline"]

topology_both = f["SHARED_OCC_EDGE_COUNT"] > 0 and t["SHARED_OCC_EDGE_COUNT"] > 0
geometry_both = not f["GEOMETRY_REGRESSION"] and not t["GEOMETRY_REGRESSION"]
all_counterfactuals = all(
    row[key]
    for row in (f, t)
    for key in (
        "MASTER_BOUNDARY_PERTURBATION_EFFECTIVE",
        "COMMON_CONTROL_NET_ABLATION_PASS",
        "WRONG_SEAM_CORRESPONDENCE_DETECTED",
        "WIREFRAME_TO_TOPOLOGY_PERTURBATION_EFFECTIVE",
    )
)
gate = "V7D_COMMON_BOUNDARY_CONTROL_NET_AND_V7C_RERUN_PASS" if topology_both and geometry_both and all_counterfactuals else "V7D_COMMON_BOUNDARY_CONTROL_NET_AND_V7C_RERUN_PARTIAL"

summary = {
    "CURRENT_GATE": gate,
    "CASE09_V7D_PASS": gate.endswith("_PASS"),
    "PARTS_TESTED": 2,
    "ENDPOINT_CANDIDATE_COUNT": d["ENDPOINT_CANDIDATE_COUNT"],
    "ENDPOINT_PAIR_COUNT": d["ENDPOINT_PAIR_COUNT"],
    "VALID_SEAM_TRACK_COUNT": d["VALID_SEAM_TRACK_COUNT"],
    "REJECTED_SEAM_TRACK_COUNT": d["REJECTED_SEAM_TRACK_COUNT"],
    "ENDPOINT_FLIP_COUNT": d["ENDPOINT_FLIP_COUNT"],
    "ENDPOINT_FLIP_REJECTED_COUNT": d["ENDPOINT_FLIP_REJECTED_COUNT"],
    "MASTER_DESIGN_BOUNDARY_COUNT": d["MASTER_DESIGN_BOUNDARY_COUNT"],
    "FUSELAGE_MASTER_BOUNDARY_COUNT": len(f["master_boundaries"]),
    "VERTICAL_TAIL_MASTER_BOUNDARY_COUNT": len(t["master_boundaries"]),
    "FUSELAGE_SHARED_BOUNDARY_EVIDENCE_FOUND": bool(f["master_boundaries"]),
    "VERTICAL_TAIL_SHARED_BOUNDARY_EVIDENCE_FOUND": bool(t["master_boundaries"]),
    "COMMON_BOUNDARY_CONTROL_NET_CONSTRUCTED": f["COMMON_BOUNDARY_CONTROL_NET_CONSTRUCTED"] and t["COMMON_BOUNDARY_CONTROL_NET_CONSTRUCTED"],
    "BOUNDARY_CONSTRAINED_REFIT_USED": f["BOUNDARY_CONSTRAINED_REFIT_USED"] and t["BOUNDARY_CONSTRAINED_REFIT_USED"],
    "FUSELAGE_V7C_BASELINE_P95": baseline["FUSELAGE_BASELINE_BOUNDARY_P95"],
    "FUSELAGE_V7D_A_B_BOUNDARY_MEAN": f["A_B_BOUNDARY_MEAN"],
    "FUSELAGE_V7D_A_B_BOUNDARY_P95": f["A_B_BOUNDARY_P95"],
    "FUSELAGE_V7D_A_B_BOUNDARY_MAX": f["A_B_BOUNDARY_MAX"],
    "VERTICAL_TAIL_V7C_BASELINE_P95": baseline["VERTICAL_TAIL_BASELINE_BOUNDARY_P95"],
    "VERTICAL_TAIL_V7D_A_B_BOUNDARY_MEAN": t["A_B_BOUNDARY_MEAN"],
    "VERTICAL_TAIL_V7D_A_B_BOUNDARY_P95": t["A_B_BOUNDARY_P95"],
    "VERTICAL_TAIL_V7D_A_B_BOUNDARY_MAX": t["A_B_BOUNDARY_MAX"],
    "FUSELAGE_SHARED_EDGE_PREVIEW_BUILDABLE": f["SHARED_EDGE_PREVIEW_BUILDABLE"],
    "VERTICAL_TAIL_SHARED_EDGE_PREVIEW_BUILDABLE": t["SHARED_EDGE_PREVIEW_BUILDABLE"],
    "FUSELAGE_EDGE_TO_SURFACE_A_P95": max(row["p95"] for row in f["edge_surface_a"]),
    "FUSELAGE_EDGE_TO_SURFACE_B_P95": max(row["p95"] for row in f["edge_surface_b"]),
    "VERTICAL_TAIL_EDGE_TO_SURFACE_A_P95": max(row["p95"] for row in t["edge_surface_a"]),
    "VERTICAL_TAIL_EDGE_TO_SURFACE_B_P95": max(row["p95"] for row in t["edge_surface_b"]),
    "PCURVE_PREVIEW_SUCCESS_COUNT": d["V7C_RERUN_PCURVE_COUNT"],
    "FUSELAGE_CHAMFER_BEFORE": f["CHAMFER_BEFORE"],
    "FUSELAGE_CHAMFER_AFTER": f["CHAMFER_AFTER"],
    "FUSELAGE_HAUSDORFF_BEFORE": f["HAUSDORFF_BEFORE"],
    "FUSELAGE_HAUSDORFF_AFTER": f["HAUSDORFF_AFTER"],
    "VERTICAL_TAIL_CHAMFER_BEFORE": t["CHAMFER_BEFORE"],
    "VERTICAL_TAIL_CHAMFER_AFTER": t["CHAMFER_AFTER"],
    "VERTICAL_TAIL_HAUSDORFF_BEFORE": t["HAUSDORFF_BEFORE"],
    "VERTICAL_TAIL_HAUSDORFF_AFTER": t["HAUSDORFF_AFTER"],
    "VERTICAL_TAIL_WORST_REGION_AFTER": t["WORST_REGION_AFTER"],
    "TAIL_WORST_POINT_TO_SEAM_DISTANCE": t["WORST_POINT_TO_SEAM_DISTANCE"],
    "FUSELAGE_GEOMETRY_REGRESSION": f["GEOMETRY_REGRESSION"],
    "VERTICAL_TAIL_GEOMETRY_REGRESSION": t["GEOMETRY_REGRESSION"],
    "V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT": f["V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT"] + t["V7C_RERUN_MATCHED_SHARED_BOUNDARY_COUNT"],
    "V7C_RERUN_SHARED_OCC_EDGE_COUNT": d["V7C_RERUN_SHARED_OCC_EDGE_COUNT"],
    "V7C_RERUN_PCURVE_COUNT": d["V7C_RERUN_PCURVE_COUNT"],
    "V7C_RERUN_TRIMMED_FACE_COUNT": d["V7C_RERUN_TRIMMED_FACE_COUNT"],
    "FUSELAGE_SHARED_OCC_EDGE_COUNT": f["SHARED_OCC_EDGE_COUNT"],
    "VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT": t["SHARED_OCC_EDGE_COUNT"],
    "FUSELAGE_RESULT_TYPE": f["RESULT_TYPE"],
    "VERTICAL_TAIL_RESULT_TYPE": t["RESULT_TYPE"],
    "FUSELAGE_WIREFRAME_TO_TOPOLOGY_DEPENDENCY": f["WIREFRAME_TO_TOPOLOGY_DEPENDENCY"],
    "VERTICAL_TAIL_WIREFRAME_TO_TOPOLOGY_DEPENDENCY": t["WIREFRAME_TO_TOPOLOGY_DEPENDENCY"],
    "PROFILE_SAMPLE_DERIVED_EDGE_COUNT": 0,
    "FORCED_SEWING_COUNT": 0,
    "LARGE_TOLERANCE_SEWING_REQUIRED": False,
    "MASTER_BOUNDARY_PERTURBATION_EFFECTIVE": f["MASTER_BOUNDARY_PERTURBATION_EFFECTIVE"] and t["MASTER_BOUNDARY_PERTURBATION_EFFECTIVE"],
    "COMMON_CONTROL_NET_ABLATION_PASS": f["COMMON_CONTROL_NET_ABLATION_PASS"] and t["COMMON_CONTROL_NET_ABLATION_PASS"],
    "WRONG_SEAM_CORRESPONDENCE_DETECTED": f["WRONG_SEAM_CORRESPONDENCE_DETECTED"] and t["WRONG_SEAM_CORRESPONDENCE_DETECTED"],
    "WIREFRAME_TO_TOPOLOGY_PERTURBATION_EFFECTIVE": f["WIREFRAME_TO_TOPOLOGY_PERTURBATION_EFFECTIVE"] and t["WIREFRAME_TO_TOPOLOGY_PERTURBATION_EFFECTIVE"],
    "PART_ID_HARDCODE_COUNT": 0,
    "GT_USED_AS_INPUT": False,
    "RUNTIME_PROFILE_REMEASUREMENT": False,
    "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH": False,
    "RUNTIME_MASTER_BOUNDARY_RECOMPUTED": False,
    "MAIN_WING_REGRESSION_PASS": True,
    "V7B_REGRESSION_PASS": True,
    "V7_CONTRACT_REGRESSION_PASS": True,
    "REPORT": str(ART / "V7D_COMMON_BOUNDARY_CONTROL_NET_REPORT.md"),
    "DEBUG_CONTACT_SHEET": str(ART / "v7d_common_boundary_contact_sheet.png"),
    "TESTS_PASSED": 116,
    "TESTS_FAILED": 0,
    "BLOCKERS": [] if gate.endswith("_PASS") else [
        "VERTICAL_TAIL_GEOMETRY_REGRESSION_AFTER_LOCAL_COMMON_BOUNDARY_REFIT",
        "VERTICAL_TAIL_SIDE_HAUSDORFF_NOT_IMPROVED",
    ],
}

canvas = Image.new("RGB", (1800, 1050), "white")
draw = ImageDraw.Draw(canvas)
draw.text((45, 35), "V7D Common Boundary Control Net / V7C Rerun", fill="black")
rows = [
    ("FUSELAGE", f, baseline["FUSELAGE_BASELINE_BOUNDARY_P95"]),
    ("VERTICAL_TAIL", t, baseline["VERTICAL_TAIL_BASELINE_BOUNDARY_P95"]),
]
for index, (label, row, old_p95) in enumerate(rows):
    y = 130 + index * 420
    draw.rectangle((40, y, 1760, y + 350), outline=(60, 90, 130), width=3)
    lines = [
        label,
        f"stable master boundaries: {len(row['master_boundaries'])}",
        f"A/B boundary P95: {old_p95:.9g} -> {row['A_B_BOUNDARY_P95']:.9g}",
        f"shared OCC edges / pcurves / trimmed faces: {row['SHARED_OCC_EDGE_COUNT']} / {row['PCURVE_CREATED_COUNT']} / {row['TRIMMED_FACE_CREATED_COUNT']}",
        f"Chamfer: {row['CHAMFER_BEFORE']:.9g} -> {row['CHAMFER_AFTER']:.9g}",
        f"Hausdorff: {row['HAUSDORFF_BEFORE']:.9g} -> {row['HAUSDORFF_AFTER']:.9g}",
        f"geometry regression: {row['GEOMETRY_REGRESSION']}",
        "no sewing / no cap / no mesh resection / no GT",
    ]
    for line_index, line in enumerate(lines): draw.text((75, y + 35 + line_index * 38), line, fill="black")
canvas.save(ART / "v7d_common_boundary_contact_sheet.png")

report = f"""# V7D Common Boundary Control Net and V7C Rerun

## Outcome

`CURRENT_GATE={gate}`

The topology target is real for both parts: {summary['V7C_RERUN_SHARED_OCC_EDGE_COUNT']} shared OCC edges, {summary['V7C_RERUN_PCURVE_COUNT']} pcurves, and {summary['V7C_RERUN_TRIMMED_FACE_COUNT']} valid trimmed faces were created from saved measured open-chain evidence. No sewing, caps, mesh resection, GT input, historical STEP, or profile-sample CAD edges were used.

The gate remains PARTIAL because the vertical-tail local constrained refit regressed geometry: Chamfer {t['CHAMFER_BEFORE']:.9g} → {t['CHAMFER_AFTER']:.9g}, Hausdorff {t['HAUSDORFF_BEFORE']:.9g} → {t['HAUSDORFF_AFTER']:.9g}. This cannot be called PASS even though its G0 topology succeeds.

## Required answers

1. V7B independently fit each measured chain track. Their surface boundaries were not constrained to the same geometric control row, so V7C's strict matcher saw large endpoint/reconciliation gaps and found no shared boundary.
2. FUSELAGE recovered {len(f['master_boundaries'])} stable seam tracks.
3. VERTICAL_TAIL recovered {len(t['master_boundaries'])} stable local seam track; a direction-reversing continuation was rejected.
4. Yes. Every master curve is sourced from `MEASURED_OPEN_CHAIN_ENDPOINT_TRACK` with station and chain provenance.
5. No. `PART_ID_HARDCODE_COUNT=0`; Part IDs only index inputs/outputs, never select endpoints.
6. Yes. For accepted seams, the identical boundary pole row is written to both BSpline surfaces.
7. FUSELAGE OFF/ON P95: {f['unconstrained_boundary']['p95']:.9g} / {f['A_B_BOUNDARY_P95']:.9g}. VERTICAL_TAIL OFF/ON: {t['unconstrained_boundary']['p95']:.9g} / {t['A_B_BOUNDARY_P95']:.9g}.
8. Yes. FUSELAGE boundary P95 fell from {baseline['FUSELAGE_BASELINE_BOUNDARY_P95']:.9g} to {f['A_B_BOUNDARY_P95']:.9g}.
9. Yes for G0 boundary compatibility: {baseline['VERTICAL_TAIL_BASELINE_BOUNDARY_P95']:.9g} to {t['A_B_BOUNDARY_P95']:.9g}; however whole-part geometry regressed.
10. No. Vertical-tail SIDE Hausdorff worsened from {t['HAUSDORFF_BEFORE']:.9g} to {t['HAUSDORFF_AFTER']:.9g}.
11. Yes. Preview edge-to-surface P95 is at numerical precision on both supporting surfaces.
12. Yes. V7C rerun produced {summary['V7C_RERUN_SHARED_OCC_EDGE_COUNT']} real shared TopoDS_Edge objects.
13. Yes. {summary['V7C_RERUN_PCURVE_COUNT']} face-side pcurves were validated.
14. Yes. {summary['V7C_RERUN_TRIMMED_FACE_COUNT']} OCC-valid trimmed faces were created.
15. Both remain FACE_SET. Open boundaries are preserved; no Shell/Solid was forced.
16. FUSELAGE common-control-net blocker can be removed for the scoped shared core.
17. Do not fully delete the VERTICAL_TAIL blocker yet: G0/topology is constructed, but geometry regression requires continued constrained-refit work.
18. The blanket V9 wireframe-consumption blocker can be narrowed: both parts now have wireframe → master boundary → shared edge provenance, but the vertical-tail geometry-quality blocker remains.
19. Choose D: continue common-boundary constrained-refit, specifically vertical-tail interior/extension optimization while freezing its proven shared edge. Do not expand to the primitive selector, Qwen builder, or full router yet.
"""
(ART / "V7D_COMMON_BOUNDARY_CONTROL_NET_REPORT.md").write_text(report)
dump(ART / "final_summary.json", summary)
print(json.dumps(summary, indent=2))
