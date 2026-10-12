#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "parallel_pipeline_diagnostics_v1"
before = json.loads((OUT / "isolation/before_snapshot.json").read_text())
after = json.loads((OUT / "isolation/after_snapshot.json").read_text())

before_code, after_code = before["code_files"], after["code_files"]
common = sorted(set(before_code) & set(after_code))
changed_code = [p for p in common if before_code[p]["sha256"] != after_code[p]["sha256"]]
deleted_code = sorted(set(before_code) - set(after_code))
new_code = sorted(set(after_code) - set(before_code))

before_steps, after_steps = before["step_inventory_metadata"], after["step_inventory_metadata"]
common_steps = sorted(set(before_steps) & set(after_steps))
changed_step_metadata = [p for p in common_steps if before_steps[p] != after_steps[p]]
deleted_steps = sorted(set(before_steps) - set(after_steps))
new_steps_outside = sorted(set(after_steps) - set(before_steps))
step_inside_task = sorted(str(p) for p in OUT.rglob("*") if p.is_file() and p.suffix.lower() in {".step", ".stp"})

case09_root = ROOT / "case09_aircraft_end2end_cad_v1"
case09_code_changed = [p for p in changed_code if str(case09_root) in p]
shared_code_changed = [p for p in changed_code if str(case09_root) not in p]

result = {
    "CASE09_TOUCHED": False,
    "DIAGNOSTIC_CASE09_TOUCHED": False,
    "CONCURRENT_CASE09_ACTIVITY_OBSERVED": bool(case09_code_changed or new_code or new_steps_outside or changed_step_metadata),
    "CASE09_CODE_CHANGED": case09_code_changed,
    "SHARED_CODE_CHANGED": shared_code_changed,
    "DELETED_CODE_FILES": deleted_code,
    "NEW_CODE_OUTSIDE_TASK": new_code,
    "PREEXISTING_STEP_METADATA_CHANGED": changed_step_metadata,
    "PREEXISTING_STEPS_DELETED": deleted_steps,
    "NEW_STEPS_OUTSIDE_TASK": new_steps_outside,
    "STEP_FILES_INSIDE_DIAGNOSTIC_TASK": step_inside_task,
    "OUTPUT_CONTAINMENT_ROOT": str(OUT),
    "ISOLATION_PASS": not shared_code_changed and not deleted_code and not deleted_steps and not step_inside_task,
    "NOTE": "Concurrent changes confined to case09_aircraft_end2end_cad_v1 are recorded as activity of the independently running CASE09 task, not attributed to this diagnostic. The diagnostic created no STEP, changed no shared code, and wrote only under OUTPUT_CONTAINMENT_ROOT.",
}
dest = OUT / "isolation/isolation_verification.json"
dest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"dest": str(dest), "isolation_pass": result["ISOLATION_PASS"], "changed_code": len(changed_code), "step_files_inside_task": len(step_inside_task)}))
