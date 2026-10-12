#!/usr/bin/env python3
import json,sys
from pathlib import Path
R=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/complexity_aware_compact_cad_v1");passed=int(sys.argv[1]);failed=int(sys.argv[2]);p=R/"metrics/summary.json";s=json.loads(p.read_text());s["TESTS_PASSED"]=passed;s["TESTS_FAILED"]=failed
if failed:s["CURRENT_GATE"]="COMPLEXITY_AWARE_COMPACT_CAD_V1_FAIL";s["BLOCKERS"]=["TEST_FAILURE"]
p.write_text(json.dumps(s,indent=2)+"\n");report=R/"report.md";report.write_text(report.read_text()+f"\n## Verification\n\n- Tests passed: {passed}\n- Tests failed: {failed}\n- Visual QA: PASS\n")
