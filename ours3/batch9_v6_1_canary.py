#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_mac_resume_v6_1"
MAC_SCRIPT = BASE / "scripts/batch9_mac.py"

CANARIES = [
    ("CASE_01", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"),
    ("CASE_04", "CADPART_000", "CANDIDATE_01_GLOBAL_LOFT"),
    ("CASE_07", "CADPART_000", "CANDIDATE_01_REVOLUTION"),
]


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def status_code(exc: Exception):
    return getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)


def main():
    spec = importlib.util.spec_from_file_location("batch9_mac", MAC_SCRIPT)
    mac = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mac)
    mac.set_key()
    sys.path.insert(0, str(mac.MAC_ROOT))
    from multi_agent_cad import config
    import multi_agent_cad.nodes as nodes

    # DS_BASE_URL comes from multi_agent_cad.config (xinlicloud)
    nodes._DS_BASE_URL = config.DS_BASE_URL
    client = nodes._llm_client()
    model = config.ARCHITECT_MODEL
    results = []

    for index, (case_id, part_id, candidate_id) in enumerate(CANARIES, 1):
        candidate = BASE / "08_multi_candidate_mac" / case_id / part_id / candidate_id
        old = load(candidate / "candidate_manifest.json")
        hypothesis = old["hypothesis"]
        target = OUT / "01_mac_canary" / f"CANARY_{index:02d}_{case_id}_{part_id}_{candidate_id}"
        record = {
            "canary_index": index,
            "case_id": case_id,
            "part_id": part_id,
            "candidate_id": candidate_id,
            "hypothesis": hypothesis,
            "MAC_ATTEMPTED": True,
            "OBJ_TOKENS_SENT_TO_MAC": False,
            "RENDER_SENT_TO_MAC": False,
            "MEASURED_SPEC_SENT_TO_MAC": False,
            "SEMANTIC_GRAPH_SENT_TO_MAC": False,
            "DUAL_MODAL_CONTEXT_ACTUALLY_USED": False,
            "HTTP_STATUS": None,
            "MAC_CANDIDATE_SUCCESS": False,
        }
        started = time.time()
        try:
            visual, visual_raw, visual_usage = mac.visual_context(client, case_id, part_id)
            dump(target / "visual_context.json", visual)
            (target / "vlm_response.txt").write_text(visual_raw, encoding="utf-8")
            dump(target / "visual_token_usage.json", visual_usage)
            record["OBJ_TOKENS_SENT_TO_MAC"] = True
            record["RENDER_SENT_TO_MAC"] = True

            system, user, context = mac.candidate_prompt(case_id, part_id, hypothesis, visual)
            (target / "mac_prompt.txt").write_text(system + "\n\n" + user, encoding="utf-8")
            record["MEASURED_SPEC_SENT_TO_MAC"] = "measured_cad_spec" in context
            record["SEMANTIC_GRAPH_SENT_TO_MAC"] = "semantic_surface_graph" in context
            raw, usage = mac.call(client, model, [{"role": "system", "content": system}, {"role": "user", "content": user}], 3072)
            parsed = mac.json_from(raw)
            generated_code = parsed.get("generated_code", "")
            record.update({
                "HTTP_STATUS": 200,
                "raw_response_nonempty": bool(raw.strip()),
                "generated_code_from_raw_response": bool(generated_code.strip()),
                "LLM_CALLS": 2,
                "DUAL_MODAL_CONTEXT_ACTUALLY_USED": True,
                "MAC_CANDIDATE_SUCCESS": bool(raw.strip() and generated_code.strip()),
                "elapsed_seconds": time.time() - started,
            })
            dump(target / "mac_response.json", {"raw_response": raw, "parsed": parsed, "error": None})
            dump(target / "token_usage.json", usage)
            (target / "generated_code.py").write_text(generated_code, encoding="utf-8")
        except Exception as exc:
            code = status_code(exc)
            record.update({
                "HTTP_STATUS": code,
                "error": f"{type(exc).__name__}: {exc}",
                "quota_exhausted": code == 403,
                "elapsed_seconds": time.time() - started,
            })
            dump(target / "mac_response.json", {"raw_response": "", "parsed": {}, "error": record["error"]})
            dump(target / "canary_result.json", record)
            results.append(record)
            summary = {
                "CURRENT_GATE": "BATCH9_MAC_RESUME_V6_1_FAIL",
                "MAC_CANARY_COUNT": 3,
                "MAC_CANARIES_COMPLETED": len(results),
                "MAC_CANARY_PASS": False,
                "MAC_HTTP_STATUS": code,
                "MAC_QUOTA_AVAILABLE": False if code == 403 else None,
                "STOP_AFTER_CANARY_FAILURE": True,
                "CASE09_RERUN": False,
                "P3_RERUN_CASES": [],
                "PHYSX_RERUN_CASES": [],
                "results": results,
                "BLOCKERS": ["MAC_HTTP_403_ALLOCATION_QUOTA_FREE_TIER_ONLY"] if code == 403 else ["MAC_CANARY_FAILED"],
            }
            dump(OUT / "artifacts/canary_summary.json", summary)
            print(json.dumps(summary, indent=2))
            return 3

        dump(target / "canary_result.json", record)
        results.append(record)
        print(f"CANARY_{index} {case_id} {part_id} HTTP=200 PASS={record['MAC_CANDIDATE_SUCCESS']}", flush=True)
        if not record["MAC_CANDIDATE_SUCCESS"]:
            break

    passed = len(results) == 3 and all(row["MAC_CANDIDATE_SUCCESS"] for row in results)
    summary = {
        "CURRENT_GATE": "BATCH9_MAC_RESUME_V6_1_CANARY_PASS" if passed else "BATCH9_MAC_RESUME_V6_1_FAIL",
        "MAC_CANARY_COUNT": 3,
        "MAC_CANARIES_COMPLETED": len(results),
        "MAC_CANARY_PASS": passed,
        "MAC_HTTP_STATUS": 200 if passed else results[-1].get("HTTP_STATUS"),
        "MAC_QUOTA_AVAILABLE": passed,
        "CASE09_RERUN": False,
        "P3_RERUN_CASES": [],
        "PHYSX_RERUN_CASES": [],
        "results": results,
        "BLOCKERS": [] if passed else ["MAC_CANARY_FAILED"],
    }
    dump(OUT / "artifacts/canary_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
