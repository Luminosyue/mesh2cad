#!/usr/bin/env python3
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/batch_10_step_audit_sanity_fix_v2")
summary_path = ROOT / "artifacts/summary.json"
summary = json.load(summary_path.open(encoding="utf-8"))
xml_root = ET.parse(ROOT / "artifacts/pytest.xml").getroot()
suites = [xml_root] if xml_root.tag == "testsuite" else list(xml_root.findall("testsuite"))
tests = sum(int(s.attrib.get("tests", 0)) for s in suites)
failed = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
summary["TESTS_PASSED"] = tests - failed
summary["TESTS_FAILED"] = failed
if failed:
    summary["CURRENT_GATE"] = "BATCH_10_STEP_AUDIT_SANITY_FIX_V2_FAIL"
    summary["BLOCKERS"] = sorted(set(summary.get("BLOCKERS", []) + ["TEST_FAILURES"]))
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

mapping_lines = []
for row in summary["CASES"]:
    mapping_lines += [
        f"CASE_ID={row['CASE_ID']}",
        f"SOURCE_OBJ_PATH={row['SOURCE_OBJ_PATH']}",
        f"SOURCE_OBJ_SHA256={row['SOURCE_OBJ_SHA256']}",
        f"STEP_PATH={row['STEP_PATH'] or 'NO_STEP'}",
        f"STEP_SHA256={row['STEP_SHA256'] or 'NOT_APPLICABLE'}",
        f"STEP_PROVENANCE_FILE={row['STEP_PROVENANCE_FILE']}",
        f"RECOVERY_BACKEND={row['RECOVERY_BACKEND']}",
        f"QUALITY_METRICS_SOURCE={row['QUALITY_METRICS_SOURCE']}",
        f"OLD_GEOM_Q={row['V1_AUDIT_GEOM_Q']}",
        f"OLD_CHAMFER={row['V1_AUDIT_CHAMFER']}",
        f"OLD_P95={row['V1_AUDIT_P95']}",
        f"OLD_COVERAGE02={row['V1_AUDIT_COVERAGE02']}",
        f"NEW_GEOM_Q={row['V2_CORRECTED_GEOM_Q']}",
        f"NEW_CHAMFER={row['V2_CORRECTED_CHAMFER']}",
        f"NEW_P95={row['V2_CORRECTED_P95']}",
        f"NEW_COVERAGE02={row['V2_CORRECTED_COVERAGE02']}",
        f"QA_SCOPE_OLD={row['QA_SCOPE_OLD']}",
        f"QA_SCOPE_NEW={row['QA_SCOPE_NEW']}",
        f"TRANSFORM_OLD={row['TRANSFORM_OLD']}",
        f"TRANSFORM_NEW={row['TRANSFORM_NEW']}",
        "",
    ]
(ROOT / "artifacts/exact_mapping_and_qa.txt").write_text("\n".join(mapping_lines), encoding="utf-8")

j = lambda value: json.dumps(value, separators=(",", ":"))
lines = [
    f"CURRENT_GATE={summary['CURRENT_GATE']}",
    f"CASE00_PROVENANCE_BUG_CONFIRMED={str(summary['CASE00_PROVENANCE_BUG_CONFIRMED']).lower()}",
    f"CASE00_CORRECT_STEP={summary['CASE00_CORRECT_STEP']}",
    f"DUPLICATE_STEP_CASE_GROUPS={j(summary['DUPLICATE_STEP_CASE_GROUPS'])}",
    f"GEOMETRY_QA_TRANSFORM_BUG={str(summary['GEOMETRY_QA_TRANSFORM_BUG']).lower()}",
    f"CASES_WITH_PROVENANCE_CHANGE={j(summary['CASES_WITH_PROVENANCE_CHANGE'])}",
    f"CASES_WITH_GEOM_Q_CHANGE={j(summary['CASES_WITH_GEOM_Q_CHANGE'])}",
]
for row in summary["CASES"]:
    lines.append(f"{row['CASE_ID']} | SOURCE={row['SOURCE_OBJ_PATH']} | STEP={row['STEP_PATH'] or 'NO_STEP'} | SHA={row['STEP_SHA256'] or 'NOT_APPLICABLE'} | OLD_Q={row['V1_AUDIT_GEOM_Q']} | NEW_Q={row['V2_CORRECTED_GEOM_Q']}")
text = "\n".join(lines) + "\n"
(ROOT / "artifacts/final_output.txt").write_text(text, encoding="utf-8")
print(text, end="")
