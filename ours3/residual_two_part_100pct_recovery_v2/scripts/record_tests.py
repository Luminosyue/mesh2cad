#!/usr/bin/env python3
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/residual_two_part_100pct_recovery_v2")
xml = ET.parse(ROOT / "artifacts/pytest.xml").getroot()
suite = xml if xml.tag == "testsuite" else xml.find("testsuite")
tests = int(suite.attrib.get("tests", 0))
failures = int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
path = ROOT / "artifacts/summary.json"
summary = json.loads(path.read_text(encoding="utf-8"))
summary["TESTS_PASSED"] = tests - failures
summary["TESTS_FAILED"] = failures
path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
report = ROOT / "artifacts/residual_two_part_100pct_recovery_v2_report.md"
with report.open("a", encoding="utf-8") as stream:
    stream.write(f"\n## Tests\n\n- Passed: {tests - failures}\n- Failed: {failures}\n")
print(json.dumps({"passed": tests - failures, "failed": failures}))
