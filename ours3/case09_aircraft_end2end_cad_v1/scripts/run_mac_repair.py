import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1")
MAC_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/external/Multi-Agent-CAD")
PART = OUT / "05_backend_recovery" / "CADPART_000"
RUN = PART / "mac"
SPEC = PART / "measured_cad_spec.json"
PROGRAM = RUN / "mac_generated_program.py"
STEP = RUN / "reconstructed.step"
AUDIT = RUN / "mac_audit.json"


def load_key():
    env_file = Path("/data/home/cuiyuehan/project/pair_agent/.env")
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        if line.strip().startswith("DASHSCOPE_API_KEY="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                os.environ["DASHSCOPE_API_KEY"] = value
            return


def extract_code(text):
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.S | re.I)
    code = match.group(1) if match else text
    start = min([x for x in (code.find("import "), code.find("from ")) if x >= 0])
    return code[start:].strip() + "\n"


def execute():
    result = subprocess.run(
        [sys.executable, str(PROGRAM), "--spec", str(SPEC), "--output", str(STEP)],
        cwd=str(RUN), text=True, capture_output=True, timeout=180
    )
    return result


def main():
    load_key()
    sys.path.insert(0, str(MAC_ROOT))
    from multi_agent_cad import config
    import multi_agent_cad.nodes as nodes

    nodes._DS_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    client = nodes._llm_client()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    repair_calls = []
    result = execute()
    for attempt in range(1, 3):
        if result.returncode == 0 and STEP.is_file() and STEP.stat().st_size > 0:
            break
        error = result.stderr[-8000:]
        current = PROGRAM.read_text(encoding="utf-8")
        started = time.time()
        response = client.chat.completions.create(
            model=config.CODER_MODEL,
            temperature=0.0,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": "You are the Python Coder repair agent in Multi-Agent-CAD. Return only one complete Python code block. Preserve the measured-data-only contract and build123d implementation. Make the smallest robust correction. The JSON file itself is the measured_cad_spec object: its top-level keys include part_id, operations, and semantic_label; it is not wrapped. Never read raw OBJ or any old STEP and never hard-code profile coordinates."},
                {"role": "user", "content": "Repair this generated program so it executes with --spec and --output. Runtime error:\n" + error + "\nPROGRAM:\n" + current},
            ],
        )
        usage = response.usage
        text = response.choices[0].message.content
        (RUN / f"coder_repair_{attempt}_response.txt").write_text(text, encoding="utf-8")
        PROGRAM.write_text(extract_code(text), encoding="utf-8")
        rec = {
            "role": "coder_repair",
            "attempt": attempt,
            "request_sent": True,
            "response_received": True,
            "model": config.CODER_MODEL,
            "elapsed_sec": time.time() - started,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        }
        repair_calls.append(rec)
        result = execute()
        (RUN / f"repair_{attempt}.stdout.log").write_text(result.stdout, encoding="utf-8")
        (RUN / f"repair_{attempt}.stderr.log").write_text(result.stderr, encoding="utf-8")

    audit["calls"].extend(repair_calls)
    audit["LLM_CALLS"] = len(audit["calls"])
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        audit["TOKEN_USAGE"][key] = sum((x.get(key) or 0) for x in audit["calls"])
    audit["coder_repair_attempts"] = len(repair_calls)
    audit["program_exit_code"] = result.returncode
    audit["success"] = result.returncode == 0 and STEP.is_file() and STEP.stat().st_size > 0
    audit["provider_request_sent"] = all(x["request_sent"] for x in audit["calls"])
    audit["provider_response_received"] = all(x["response_received"] for x in audit["calls"])
    AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if result.returncode:
        print(result.stderr, file=sys.stderr)
    return 0 if audit["success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
