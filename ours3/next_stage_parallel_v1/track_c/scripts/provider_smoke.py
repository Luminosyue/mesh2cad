from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PREPARED_MAC = Path("/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD")
OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/next_stage_parallel_v1/track_c/artifacts/provider_smoke.json")
sys.path.insert(0, str(PREPARED_MAC))

from multi_agent_cad import config  # noqa: E402
from openai import OpenAI  # noqa: E402


def main() -> int:
    key = str(getattr(config, "DS_API_KEY", "") or "")
    audit = {
        "provider": "openai_compatible",
        "base_url": config.DS_BASE_URL,
        "model": config.SPEC_PLANNER_MODEL,
        "api_key_present": bool(key),
        "connectivity_smoke_attempted": False,
        "connectivity_smoke_success": False,
        "llm_calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency_seconds": None,
        "error_class": None,
        "error_message": None,
    }
    if not key:
        audit["error_class"] = "MissingAPIKey"
        audit["error_message"] = "Configured DS_API_KEY is empty"
    else:
        audit["connectivity_smoke_attempted"] = True
        audit["llm_calls"] = 1
        started = time.monotonic()
        try:
            client = OpenAI(api_key=key, base_url=config.DS_BASE_URL, timeout=30.0)
            response = client.chat.completions.create(
                model=config.SPEC_PLANNER_MODEL,
                messages=[{"role": "user", "content": "Reply with exactly OK."}],
                temperature=0,
                max_tokens=8,
            )
            audit["connectivity_smoke_success"] = bool(response.choices)
            usage = getattr(response, "usage", None)
            if usage:
                audit["prompt_tokens"] = int(getattr(usage, "prompt_tokens", 0) or 0)
                audit["completion_tokens"] = int(getattr(usage, "completion_tokens", 0) or 0)
                audit["total_tokens"] = int(getattr(usage, "total_tokens", 0) or 0)
            audit["response_nonempty"] = bool(
                response.choices and (response.choices[0].message.content or "").strip()
            )
        except Exception as exc:  # preserve a sanitized provider failure
            audit["error_class"] = type(exc).__name__
            audit["error_message"] = str(exc)[:1000].replace(key, "<redacted>")
        audit["latency_seconds"] = round(time.monotonic() - started, 3)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False))
    return 0 if audit["connectivity_smoke_success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
