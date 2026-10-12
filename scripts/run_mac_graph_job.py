#!/usr/bin/env python3
"""Run original Multi-Agent-CAD graph in the MAC conda env and write artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

MAC_REPO = Path("/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD")
CADPY_SRC = MAC_REPO / "packages" / "cadpy" / "src"
if str(CADPY_SRC) not in sys.path:
    sys.path.insert(0, str(CADPY_SRC))
if str(MAC_REPO) not in sys.path:
    sys.path.insert(0, str(MAC_REPO))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, ensure_ascii=False) + "\n", encoding="utf-8")


def plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "value") and not isinstance(value, (bytes, bytearray)):
        try:
            return str(value.value)
        except Exception:
            pass
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--mac-dir", type=Path, required=True)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    mac_dir = args.mac_dir.resolve()
    cache_dir = mac_dir / "pipeline_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    import multi_agent_cad.nodes as mac_nodes
    from multi_agent_cad.graph import build_graph

    mac_nodes._CACHE_DIR = cache_dir
    result = build_graph().invoke(
        {
            "user_request": request["user_request"],
            "iteration_count": 0,
            "max_iterations": 5,
            "force_refresh": True,
            "workflow_id": "original",
            "node_history": [],
            "execution_log": [],
        }
    )
    payload = plain(result) if isinstance(result, dict) else {"raw": plain(result)}
    slim = {key: payload.get(key) for key in payload if key != "current_python_code"}
    dump_json(mac_dir / "mac_graph_result.json", slim)
    code = payload.get("current_python_code")
    code_path = Path(str(payload.get("current_python_code_path") or ""))
    if code_path.is_file():
        (mac_dir / "generated_code.py").write_text(code_path.read_text(encoding="utf-8"), encoding="utf-8")
    elif code:
        (mac_dir / "generated_code.py").write_text(str(code), encoding="utf-8")
    print(json.dumps({"step": payload.get("current_step_path"), "code": payload.get("current_python_code_path"), "error": payload.get("error_type")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
