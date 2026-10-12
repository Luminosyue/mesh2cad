#!/usr/bin/env python3
import json
import xml.etree.ElementTree as ET
from pathlib import Path

root=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v10_geometry_gated_builder_contract_closure")
path=root/"artifacts/v10_summary.json"; summary=json.loads(path.read_text())
suite=ET.parse(root/"artifacts/pytest.xml").getroot(); suite=suite if suite.tag=="testsuite" else suite.find("testsuite")
tests=int(suite.attrib.get("tests",0)); failed=int(suite.attrib.get("failures",0))+int(suite.attrib.get("errors",0))
summary["TESTS_PASSED"]=tests-failed; summary["TESTS_FAILED"]=failed
if failed:
    summary["CURRENT_GATE"]="V10_GEOMETRY_GATED_BUILDER_CONTRACT_CLOSURE_FAIL"; summary["V10_PASS"]=False; summary["BLOCKERS"]=["UNIT_TEST_FAILURE"]
path.write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
