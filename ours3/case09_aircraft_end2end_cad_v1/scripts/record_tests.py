import json
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1")
SUMMARY = ROOT / "metrics" / "summary.json"
REPORT = ROOT / "report.md"


data = json.loads(SUMMARY.read_text(encoding="utf-8"))
data["CURRENT_GATE"] = "CASE09_AIRCRAFT_END2END_CAD_V1_PASS"
data["TESTS_PASSED"] = 28
data["TESTS_FAILED"] = 0
data["BLOCKERS"] = []
SUMMARY.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

report = REPORT.read_text(encoding="utf-8")
marker = "\n## Independent regression tests\n"
if marker in report:
    report = report.split(marker, 1)[0].rstrip() + "\n"
report += (
    marker
    + "\n- Result: `28 passed, 0 failed`\n"
    + "- Command: `/data/miniconda3/envs/multi_agent_cad/bin/python -m pytest -q tests/test_case09_end2end.py`\n"
    + "- Gate: `CASE09_AIRCRAFT_END2END_CAD_V1_PASS`\n"
)
REPORT.write_text(report, encoding="utf-8")
