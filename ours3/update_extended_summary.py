from pathlib import Path
import json

base = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/exact9998_val1000_a0_a1_a2_a3_extended_cad_metrics_v1")
p = base / "reports/FINAL_REPORT.json"
d = json.loads(p.read_text())
d["ALL_FOUR_VALID"]["N"] = 166
d["CLOSURE"]["BEST_CLOSURE_ARM"] = "TIE_A0_A1_A2_A3"
d["A3"]["A3_CLOSURE_ADVANTAGE"] = "NO"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

lines = [
    "# EXACT9998 Extended CAD Metrics",
    "",
    f"CURRENT_GATE = {d['CURRENT_GATE']}",
    f"TEST_TOUCHED = {d['TEST_TOUCHED']}",
    f"P1_UNAFFECTED = {d['P1_UNAFFECTED']}",
    "",
    "## Best Arms",
    "",
    f"- BEST_CURVE_ARM: {d['CURVE']['BEST_CURVE_ARM']}",
    f"- BEST_CLOSURE_ARM: {d['CLOSURE']['BEST_CLOSURE_ARM']}",
    f"- BEST_SURFACE_ARM: {d['SURFACE']['BEST_SURFACE_ARM']}",
    f"- BEST_TOPOLOGY_ARM: {d['TOPOLOGY']['BEST_TOPOLOGY_ARM']}",
    f"- BEST_GRAPH_ARM: {d['GRAPH']['BEST_GRAPH_ARM']}",
    f"- A3_EXTENDED_ADVANTAGE: {d['A3']['A3_EXTENDED_ADVANTAGE']}",
    "",
    "## Notes",
    "",
    "- Normal consistency is UNRELIABLE_DEFERRED.",
    "- Manifold rate is NOT_IMPLEMENTED_RELIABLY.",
    "- Graph edit distance is DEFERRED.",
    "- All continuous valid-only metrics must be read with coverage and paired/common-valid subsets.",
    "",
    "## Integrity",
    "",
]
for key, value in d["integrity"].items():
    if not key.startswith("report_sha"):
        lines.append(f"- {key}: {value}")
(base / "reports/FINAL_REPORT.md").write_text("\n".join(lines) + "\n")
print("updated")
