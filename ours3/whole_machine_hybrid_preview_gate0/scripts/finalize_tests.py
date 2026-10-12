import json
import re
import sys
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/whole_machine_hybrid_preview_gate0")
ART = ROOT / "artifacts"
log_path = ROOT / "logs/test_gate.log"
summary_path = ART / "summary.json"
report_path = ART / "whole_machine_hybrid_report.md"

text = log_path.read_text(encoding="utf-8")
passed_match = re.search(r"(\d+) passed", text)
failed_match = re.search(r"(\d+) failed", text)
if not passed_match:
    raise SystemExit("unable to parse pytest counts")
passed = int(passed_match.group(1))
failed = int(failed_match.group(1)) if failed_match else 0
summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary["TESTS_PASSED"] = passed
summary["TESTS_FAILED"] = failed
if failed:
    summary["CURRENT_GATE"] = "WHOLE_MACHINE_HYBRID_PREVIEW_GATE_0_FAIL"
    summary["BLOCKERS"] = sorted(set(summary.get("BLOCKERS", []) + ["TEST_FAILURE"]))
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
report = report_path.read_text(encoding="utf-8")
report = re.sub(r"Tests: .*", f"Tests: {passed} passed, {failed} failed", report)
report_path.write_text(report, encoding="utf-8")
(ART / "test_results.json").write_text(json.dumps({"tests_passed": passed, "tests_failed": failed, "gate": summary["CURRENT_GATE"], "pytest_log": str(log_path)}, indent=2) + "\n")
print(f"TESTS_PASSED={passed}")
print(f"TESTS_FAILED={failed}")
sys.exit(1 if failed else 0)
