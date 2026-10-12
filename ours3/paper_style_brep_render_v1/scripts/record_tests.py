import json
import xml.etree.ElementTree as ET
from pathlib import Path

root=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/paper_style_brep_render_v1")
xml=ET.parse(root/"artifacts/pytest.xml").getroot()
suites=[xml] if xml.tag=="testsuite" else list(xml.findall("testsuite"))
tests=sum(int(s.attrib.get("tests",0)) for s in suites)
failures=sum(int(s.attrib.get("failures",0)) for s in suites)
errors=sum(int(s.attrib.get("errors",0)) for s in suites)
skipped=sum(int(s.attrib.get("skipped",0)) for s in suites)
passed=tests-failures-errors-skipped
failed=failures+errors
path=root/"artifacts/summary.json"; summary=json.loads(path.read_text())
summary["TESTS_PASSED"]=passed; summary["TESTS_FAILED"]=failed
if failed:
    summary["CURRENT_GATE"]="PAPER_STYLE_BREP_RENDERER_V1_FAIL"
    summary["BLOCKERS"]=sorted(set(summary.get("BLOCKERS",[])+["TEST_FAILURES"]))
path.write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"passed":passed,"failed":failed}))
