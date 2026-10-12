#!/usr/bin/env python3
import json
import xml.etree.ElementTree as ET
from pathlib import Path

root=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit")
summary_path=root/"artifacts/pretest_summary.json"
xml=ET.parse(root/"artifacts/pytest.xml").getroot()
suite=xml if xml.tag=="testsuite" else xml.find("testsuite")
tests=int(suite.attrib.get("tests",0)); failed=int(suite.attrib.get("failures",0))+int(suite.attrib.get("errors",0))
summary=json.loads(summary_path.read_text()); summary["TESTS_PASSED"]=tests-failed; summary["TESTS_FAILED"]=failed
summary_path.write_text(json.dumps(summary,indent=2)+"\n")
(root/"artifacts/final_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
report=root/"artifacts/v7d3_final_report.md"
report.write_text(report.read_text()+f"\n## Tests\n\n- Passed: {tests-failed}\n- Failed: {failed}\n- JUnit: `{root/'artifacts/pytest.xml'}`\n")
print(json.dumps(summary,indent=2))
