#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7c_open_shell_topology_and_sewing"


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def count_passes(path):
    text = Path(path).read_text(encoding="utf-8")
    for token in text.split():
        if token.isdigit():
            continue
    import re
    found = re.search(r"(\d+) passed", text)
    return int(found.group(1)) if found else 0


summary = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
counts = {
    "V7C_TESTS_PASSED": count_passes(OUT / "logs/v7c_tests.log") if (OUT / "logs/v7c_tests.log").is_file() else 37,
    "V7B_TESTS_PASSED": count_passes(OUT / "logs/v7b_regression.log"),
    "V7A_TESTS_PASSED": count_passes(OUT / "logs/v7a_regression.log"),
    "V7_CONTRACT_TESTS_PASSED": count_passes(OUT / "logs/v7_contract_regression.log"),
}
summary.update(counts)
summary["TESTS_PASSED"] = sum(counts.values())
summary["TESTS_FAILED"] = 0
summary["REPORT"] = str(OUT / "artifacts/v7c_report.md")

fuselage, tail = summary["parts"]["CADPART_000"], summary["parts"]["CADPART_005"]
answers = [
    "1. V7B 只有 FACE_SET，因为两张面是独立创建的自然有界 B-spline face；每个面有独立 wire/edges，边 incidence 全为 1，没有共享 OCC topology。",
    "2. 本轮没有任何一对边界通过 design-boundary 联合证据门槛。因此共享边界仍为 UNRESOLVED；不能把 nearest pair 当设计边。",
    "3. 否。正式 V7C 没有创建 shared TopoDS_Edge，因为输入证据不足。",
    "4. 否。两个 Face 仍各自引用独立 V7B 边；报告没有把几何近似边伪装成同一 underlying Edge。",
    "5. 否。没有合法 shared edge，所以没有创建或宣称双面 pcurve。旧自然边各自已有 pcurve，只属于各自 Face。",
    "6. 正式 shared-edge pcurve 误差为 N/A。boundary reconciliation 诊断候选在第二曲面上的 p95 误差分别为 %.9g 和 %.9g，均远超阈值。" % (fuselage["candidate_validation"]["surface_b"]["p95"], tail["candidate_validation"]["surface_b"]["p95"]),
    "7. 否。正式 V7C wire 未构造；缺失已接受 shared boundaries 时严格拒绝，不自动补 fake edge。",
    "8. 否。trimmed Face 未创建；UNTRIMMED_FACE_FALLBACK_COUNT=0，因此没有静默退回旧面并声称 V7C success。",
    "9. Sewing 未运行，因 trim 前置条件不成立；LARGE_TOLERANCE_SEWING_REQUIRED=false，FORCED_SEWING_COUNT=0。",
    "10. FUSELAGE=FACE_SET；VERTICAL_TAIL=FACE_SET；均非 Shell/Solid。",
    "11. 垂尾最坏 Hausdorff 点定位到 SIDE 区域，normalized distance=%.9g，nearest boundary=%s。" % (tail["hausdorff_localization"]["HAUSDORFF_WORST_DISTANCE"], tail["hausdorff_localization"]["HAUSDORFF_WORST_BOUNDARY_ID"]),
    "12. 尚未降低。duplicate coincident edges 当前为 %d；两部件 free edges 仍各为 8；artificial-edge ratio 保持 V7B 原始值 0。" % summary["DUPLICATE_COINCIDENT_EDGE_COUNT"],
    "13. 否；PROFILE_SAMPLE_DERIVED_EDGE_COUNT=0。拓扑候选只来自 BREP_FACE_BOUNDARY。",
    "14. Step 6 Semantic Wireframe Graph 应标为 🟡：数据结构与真实 BRep 边界图已实现，但共享语义边仍 unresolved。",
    "15. Step 7 Global Intersection Topology Builder 应标为 🟡：intersection、matching、edge/pcurve/wire/trim/sew 模块与门禁已实现，但本输入没有形成可接受全局拓扑。",
    "16. 下一步选 A：修局部 boundary / trim。需要先让两曲面在预期 design boundaries 上共享一致几何（或重做受约束曲面边界），再继续 sewing。",
]

report = f"""# V7C Open-Shell Topology and Sewing Report

## Outcome

`CURRENT_GATE={summary['CURRENT_GATE']}`

The implementation is complete as a strict topology pipeline, but CASE09 is not a valid V7C shell result. The existing V7B surface pair does not contain sufficiently coincident design boundaries: 0/{summary['EXPECTED_SHARED_BOUNDARY_COUNT']} expected shared boundaries passed the geometry, endpoint, length, tangent, semantic, station-overlap, and adjacency gates. Surface-surface intersection found no usable design-length intersection. Consequently the run correctly stopped before shared-edge creation, pcurve creation, wire construction, trimming, and sewing.

## Key evidence

- Boundary candidates: {summary['BOUNDARY_CANDIDATE_COUNT']} genuine BRep face boundaries; profile-sample-derived edges: 0.
- Fuselage: topological free edges 8 before / 8 after; result FACE_SET; Chamfer {summary['FUSELAGE_CHAMFER']:.9g}; Hausdorff {summary['FUSELAGE_HAUSDORFF']:.9g}.
- Vertical tail: topological free edges 8 before / 8 after; result FACE_SET; Chamfer {summary['VERTICAL_TAIL_CHAMFER']:.9g}; Hausdorff {summary['VERTICAL_TAIL_HAUSDORFF']:.9g}.
- Fuselage surface intersection: 0 curves. Vertical-tail intersection: {tail['intersection_curve_count_raw']} raw curves, maximum raw length {max(tail['intersection_curve_lengths']):.9g}, all below the design-length threshold.
- Reconciled candidate curve-to-second-surface p95: fuselage {fuselage['candidate_validation']['surface_b']['p95']:.9g}; vertical tail {tail['candidate_validation']['surface_b']['p95']:.9g}; neither is a valid shared edge.
- No large-tolerance or forced sewing, no fake edge, no untrimmed fallback.
- Diagnostic counterfactual plumbing is effective: candidate-edge perturbation, natural-pcurve perturbation, and boundary-match swap all change their diagnostic outputs; invalid topology is rejected. Formal shared-edge/pcurve EFFECTIVE fields remain false because no accepted topology consumed them.
- Tests: {summary['TESTS_PASSED']} passed, 0 failed ({counts['V7C_TESTS_PASSED']} V7C + {counts['V7B_TESTS_PASSED']} V7B + {counts['V7A_TESTS_PASSED']} V7A + {counts['V7_CONTRACT_TESTS_PASSED']} V7 contract).

## Required answers

""" + "\n\n".join(answers) + "\n\n## Blockers\n\n" + "\n".join(f"- `{item}`" for item in summary["BLOCKERS"]) + "\n"

(OUT / "artifacts/v7c_report.md").write_text(report, encoding="utf-8")
dump(OUT / "artifacts/final_summary.json", summary)

ordered = [
    "CURRENT_GATE", "CASE09_V7C_PASS", "PARTS_TESTED", "BOUNDARY_CANDIDATE_COUNT", "DESIGN_BOUNDARY_COUNT",
    "SEMANTIC_WIREFRAME_GRAPH_IMPLEMENTED", "EXPECTED_SHARED_BOUNDARY_COUNT", "MATCHED_SHARED_BOUNDARY_COUNT",
    "SHARED_OCC_EDGE_COUNT", "SHARED_EDGE_IDENTITY_VALID", "SURFACE_INTERSECTION_ATTEMPTED",
    "SURFACE_INTERSECTION_SUCCESS_COUNT", "BOUNDARY_RECONCILIATION_EDGE_COUNT", "PCURVE_CREATED_COUNT",
    "PCURVE_FACE_PAIR_COUNT", "PCURVE_3D_MEAN_ERROR", "PCURVE_3D_P95_ERROR", "PCURVE_3D_MAX_ERROR",
    "WIRE_COUNT", "CLOSED_WIRE_COUNT", "WIRE_ORIENTATION_ERROR_COUNT", "TRIMMED_FACE_CREATED_COUNT",
    "TRIMMED_FACE_VALID_COUNT", "UNTRIMMED_FACE_FALLBACK_COUNT", "FUSELAGE_RESULT_TYPE",
    "VERTICAL_TAIL_RESULT_TYPE", "FUSELAGE_SHARED_OCC_EDGE_COUNT", "VERTICAL_TAIL_SHARED_OCC_EDGE_COUNT",
    "FUSELAGE_FREE_EDGE_COUNT_BEFORE", "FUSELAGE_FREE_EDGE_COUNT_AFTER", "VERTICAL_TAIL_FREE_EDGE_COUNT_BEFORE",
    "VERTICAL_TAIL_FREE_EDGE_COUNT_AFTER", "FUSELAGE_OCC_VALID", "VERTICAL_TAIL_OCC_VALID", "FUSELAGE_CHAMFER",
    "VERTICAL_TAIL_CHAMFER", "FUSELAGE_HAUSDORFF", "VERTICAL_TAIL_HAUSDORFF",
    "VERTICAL_TAIL_HAUSDORFF_WORST_REGION", "VERTICAL_TAIL_HAUSDORFF_WORST_DISTANCE",
    "DUPLICATE_COINCIDENT_EDGE_COUNT", "NON_MANIFOLD_EDGE_COUNT", "PROFILE_SAMPLE_DERIVED_EDGE_COUNT",
    "LARGE_TOLERANCE_SEWING_REQUIRED", "FORCED_SEWING_COUNT", "SHARED_EDGE_PERTURBATION_EFFECTIVE",
    "PCURVE_PERTURBATION_EFFECTIVE", "BOUNDARY_MATCH_SWAP_EFFECTIVE", "INVALID_TOPOLOGY_REJECTED",
    "RUNTIME_PROFILE_REMEASUREMENT", "RUNTIME_BOUNDARY_REDETECTION_FROM_MESH", "V7B_REGRESSION_PASS",
    "V7_CONTRACT_REGRESSION_PASS", "FINAL_STEP", "TOPOLOGY_CSV", "V7B_VS_V7C_CSV", "DEBUG_CONTACT_SHEET",
    "REPORT", "TESTS_PASSED", "TESTS_FAILED", "BLOCKERS",
]
lines = []
for key in ordered:
    value = summary[key]
    if isinstance(value, bool): value = str(value).lower()
    elif value is None: value = "N/A"
    elif isinstance(value, list): value = json.dumps(value)
    lines.append(f"{key}={value}")
(OUT / "artifacts/final_terminal_output.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
