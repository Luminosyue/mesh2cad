import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1")
MAC_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/external/Multi-Agent-CAD")
PART_ID = "CADPART_000"
PART = OUT / "05_backend_recovery" / PART_ID
MAC_OUT = PART / "mac"
FEATURE_PATH = OUT / "04_feature_graph" / PART_ID / "cad_feature_graph.json"
SPEC_PATH = PART / "measured_cad_spec.json"


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("no JSON object in response")
    return json.loads(match.group(0))


def extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.S | re.I)
    code = match.group(1) if match else text
    start = code.find("import ")
    if start < 0:
        start = code.find("from ")
    if start < 0:
        raise ValueError("no Python imports in coder response")
    return code[start:].strip() + "\n"


def call(client, model: str, role: str, system: str, user: str, max_tokens: int):
    started = time.time()
    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    usage = getattr(response, "usage", None)
    record = {
        "role": role,
        "request_sent": True,
        "response_received": True,
        "model": model,
        "elapsed_sec": time.time() - started,
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    return response.choices[0].message.content, record


def main() -> int:
    MAC_OUT.mkdir(parents=True, exist_ok=True)
    env_file = Path("/data/home/cuiyuehan/project/pair_agent/.env")
    if not os.environ.get("DASHSCOPE_API_KEY") and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            if line.strip().startswith("DASHSCOPE_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ["DASHSCOPE_API_KEY"] = value
                break
    sys.path.insert(0, str(MAC_ROOT))
    from multi_agent_cad import config
    import multi_agent_cad.nodes as mac_nodes

    if not os.environ.get("DASHSCOPE_API_KEY") and not config.DS_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY is unavailable")
    # The configured key belongs to the standard mainland-China DashScope
    # compatible endpoint, not the token-plan endpoint shipped as the repo
    # default. Keep this override process-local and preserve global config.py.
    config.DS_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    mac_nodes._DS_BASE_URL = config.DS_BASE_URL

    feature = json.loads(FEATURE_PATH.read_text(encoding="utf-8"))
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    payload = json.dumps({"cad_feature_graph": feature, "measured_cad_spec": spec}, ensure_ascii=False)
    client = mac_nodes._llm_client()
    model = config.ARCHITECT_MODEL
    calls = []

    planner_text, rec = call(
        client,
        model,
        "planner",
        "You are the Spec Planner agent in Multi-Agent-CAD. Return strict JSON only. You may use only the supplied measured feature graph and measured CAD spec. Never infer, rescale, smooth, or invent dimensions and never request a raw mesh or any previous STEP.",
        "Plan a measured-data-preserving CAD program for this structured region. Include part_id, exact input_files, operation_sequence, invariants, prohibited_inputs, and acceptance_checks. Payload:\n" + payload,
        4096,
    )
    calls.append(rec)
    planner = extract_json(planner_text)
    (MAC_OUT / "planner_output.json").write_text(json.dumps(planner, indent=2), encoding="utf-8")

    architect_text, rec = call(
        client,
        model,
        "architect",
        "You are the Geometric Architect agent in Multi-Agent-CAD. Return strict JSON only. Design an executable build123d strategy from the measured spec. Preserve every supplied section coordinate and profile vertex exactly. The program must load the JSON at runtime and must not contain guessed geometry or read raw OBJ/old STEP.",
        "Convert this planner output and measured payload into an architecture with coordinate mapping, build123d APIs, CLI contract (--spec and --output), validity checks, and failure conditions.\nPLANNER:\n"
        + json.dumps(planner)
        + "\nPAYLOAD:\n"
        + payload,
        4096,
    )
    calls.append(rec)
    architect = extract_json(architect_text)
    (MAC_OUT / "architect_output.json").write_text(json.dumps(architect, indent=2), encoding="utf-8")

    coder_text, rec = call(
        client,
        config.CODER_MODEL,
        "coder",
        "You are the Python Coder agent in Multi-Agent-CAD. Output only one complete Python code block. It must use build123d, parse --spec and --output, load operations[0].sections from the supplied JSON at runtime, map each [x,z] profile point to Vector(x, section.coordinate, z), create one closed Wire per section, make one non-ruled Solid loft, validate it, and export STEP. Do not read OBJ, STL, GLB, or an old STEP. Do not hard-code geometry coordinates from the payload.",
        "Write the executable program for this architecture.\nARCHITECTURE:\n" + json.dumps(architect),
        4096,
    )
    calls.append(rec)
    code = extract_code(coder_text)
    forbidden = [".obj", ".stl", "old_step", "trimesh"]
    if any(token.lower() in code.lower() for token in forbidden):
        raise RuntimeError("coder output referenced prohibited reconstruction input")
    if "measured_cad_spec" not in code and "--spec" not in code:
        raise RuntimeError("coder output does not load the measured spec")
    program = MAC_OUT / "mac_generated_program.py"
    program.write_text(code, encoding="utf-8")

    output_step = MAC_OUT / "reconstructed.step"
    run = subprocess.run(
        [sys.executable, str(program), "--spec", str(SPEC_PATH), "--output", str(output_step)],
        cwd=str(MAC_OUT),
        text=True,
        capture_output=True,
        timeout=180,
    )
    (MAC_OUT / "execution.stdout.log").write_text(run.stdout, encoding="utf-8")
    (MAC_OUT / "execution.stderr.log").write_text(run.stderr, encoding="utf-8")
    audit = {
        "MAC_API_AVAILABLE": True,
        "API_PROVIDER": "DASHSCOPE_CN_OPENAI_COMPATIBLE",
        "API_BASE_URL": config.DS_BASE_URL,
        "MODEL": model,
        "MAC_USED": True,
        "MAC_PARTS": [PART_ID],
        "MAC_RUNS": 1,
        "LLM_CALLS": len(calls),
        "TOKEN_USAGE": {
            "prompt_tokens": sum(x["prompt_tokens"] or 0 for x in calls),
            "completion_tokens": sum(x["completion_tokens"] or 0 for x in calls),
            "total_tokens": sum(x["total_tokens"] or 0 for x in calls),
        },
        "calls": calls,
        "inputs": [str(FEATURE_PATH), str(SPEC_PATH)],
        "raw_obj_received": False,
        "old_step_received": False,
        "provider_request_sent": all(x["request_sent"] for x in calls),
        "provider_response_received": all(x["response_received"] for x in calls),
        "planner_executed": True,
        "architect_executed": True,
        "coder_executed": True,
        "program_exit_code": run.returncode,
        "output_step": str(output_step),
        "success": run.returncode == 0 and output_step.is_file() and output_step.stat().st_size > 0,
    }
    (MAC_OUT / "mac_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return 0 if audit["success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
