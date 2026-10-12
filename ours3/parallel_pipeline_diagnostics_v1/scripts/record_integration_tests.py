#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1")
log = (ROOT / "logs/integration_tests.log").read_text(errors="ignore")
passed = int(re.findall(r"(\d+) passed", log)[-1]) if re.findall(r"(\d+) passed", log) else 0
failed = int(re.findall(r"(\d+) failed", log)[-1]) if re.findall(r"(\d+) failed", log) else 0
p = ROOT / "artifacts/summary.json"; s = json.loads(p.read_text())
s["INTEGRATION_TESTS_PASSED"] = passed; s["TESTS_PASSED"] = s["SUBTASK_TESTS_PASSED"] + passed; s["TESTS_FAILED"] = failed
if failed:
    s["CURRENT_GATE"] = "PARALLEL_PIPELINE_DIAGNOSTICS_V1_FAIL"; s["BLOCKERS"].append("INTEGRATION_TEST_FAILURE")
p.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n")
with (ROOT / "report.md").open("a") as f: f.write(f"\n## Verification\n\n{s['SUBTASK_TESTS_PASSED']} subtask tests plus {passed} integration tests passed; {failed} failed.\n")
print(json.dumps({"integration_passed": passed, "failed": failed, "total_passed": s["TESTS_PASSED"]}))
