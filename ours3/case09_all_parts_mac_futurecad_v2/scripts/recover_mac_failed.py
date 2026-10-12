import json
import shutil
import sys
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "case09_all_parts_mac_futurecad_v2"
sys.path.insert(0, str(OUT / "scripts"))
from run_all_mac import EXPECTED_BUILDERS, PART_IDS, audit_step, code_contract, dump, execute_program, load


def main():
    recovered = []
    for part_id in PART_IDS[:4]:
        run_dir = OUT / "02_mac_runs" / part_id
        summary = load(run_dir / "mac_run_summary.json")
        spec = OUT / "01_part_specs" / part_id / "measured_cad_spec.json"
        for row in summary["candidates"]:
            candidate = run_dir / f"candidate_{row['candidate']:02d}"
            program = candidate / "generated_code.py"; step = candidate / "candidate.step"
            code = program.read_text(encoding="utf-8")
            errors = code_contract(code, EXPECTED_BUILDERS[part_id])
            if errors:
                result_code, stdout, stderr = 2, "", "\n".join(errors)
            else:
                result = execute_program(program, spec, step)
                result_code, stdout, stderr = result.returncode, result.stdout, result.stderr
            audit = audit_step(step) if result_code == 0 and step.is_file() else {"STEP_RELOAD": False, "BREP_VALID": False, "TRANSFER_ROOTS": 0, "FACES": 0, "EDGES": 0}
            row.update({"execution_success": result_code == 0, "semantic_program_pass": not errors, **audit, "adapter_contract_rerun": True})
            log_path = candidate / "execution_log.txt"
            logs = load(log_path) if log_path.is_file() else []
            logs.append({"round": "ADAPTER_CONTRACT_RERUN", "exit_code": result_code, "stdout": stdout, "stderr": stderr})
            dump(log_path, logs); dump(candidate / "candidate_qa.json", row)
        accepted = [row for row in summary["candidates"] if row["execution_success"] and row["BREP_VALID"] and row["semantic_program_pass"]]
        selected = min(accepted, key=lambda row: (row["FACES"], row["EDGES"], row["code_bytes"])) if accepted else None
        if selected:
            selected_dir = run_dir / f"candidate_{selected['candidate']:02d}"
            shutil.copy2(selected_dir / "generated_code.py", run_dir / "generated_code.py")
            shutil.copy2(selected_dir / "candidate.step", run_dir / "selected.step")
            summary["selected_candidate"] = selected["candidate"]
            summary["MAC_RESULT"] = "SUCCESS"
            summary["adapter_contract_recovery"] = True
            recovered.append(part_id)
        dump(run_dir / "mac_run_summary.json", summary)

    rows = [load(OUT / "02_mac_runs" / part_id / "mac_run_summary.json") for part_id in PART_IDS]
    token = [load(OUT / "02_mac_runs" / part_id / "token_usage.json") for part_id in PART_IDS]
    aggregate = {
        "MAC_API_AVAILABLE": True, "API_PROVIDER": "DASHSCOPE_CN_OPENAI_COMPATIBLE",
        "MODEL": "qwen3.7-max", "MAC_PARTS_ATTEMPTED": 8,
        "MAC_PARTS_SUCCESS": sum(row.get("MAC_RESULT") == "SUCCESS" for row in rows),
        "MAC_PART_RATIO": sum(row.get("MAC_RESULT") == "SUCCESS" for row in rows) / 8,
        "ALL_PARTS_MAC": all(row.get("LLM_CALLS", 0) > 0 for row in rows),
        "MAC_RUNS": sum(row.get("MAC_RUNS", 0) for row in rows),
        "LLM_CALLS": sum(row.get("LLM_CALLS", 0) for row in rows),
        "TOTAL_INPUT_TOKENS": sum(x["TOTAL_INPUT_TOKENS"] for x in token),
        "TOTAL_OUTPUT_TOKENS": sum(x["TOTAL_OUTPUT_TOKENS"] for x in token),
        "recovered_after_adapter_contract_fix": recovered,
        "parts": rows,
    }
    dump(OUT / "metrics/mac_aggregate.json", aggregate)
    print(json.dumps(aggregate, indent=2))
    return 0 if aggregate["MAC_PARTS_SUCCESS"] == 8 else 2


if __name__ == "__main__":
    raise SystemExit(main())
