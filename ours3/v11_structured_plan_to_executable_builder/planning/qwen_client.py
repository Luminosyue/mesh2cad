"""Optional real Qwen3-VL call. Timeouts are reported as external blockers, never faked."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from design_plan.schema import PLAN_VERSION


URL = os.environ.get("QWEN_URL", "http://127.0.0.1:18000/v1/chat/completions")
MODEL = os.environ.get("VISUAL_MODEL", "Qwen3-VL-4B-Instruct")


def try_qwen_plan(part_id: str, allowed: list[str], catalog_summary: dict[str, Any], timeout: float = 8.0) -> dict[str, Any]:
    schema_hint = {
        "plan_version": PLAN_VERSION,
        "part_id": part_id,
        "construction_family": "<one of ALLOWED_BUILDERS>",
        "builder": "<same>",
        "builder_eligibility_ref": "BUILDER_ELIGIBILITY.<BUILDER>",
        "geometry_refs": {"*_ref": "MEASURED_SPEC...."},
        "reasoning_summary": "text only, not executed",
        "confidence": 0.0,
    }
    payload = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": 400,
        "messages": [
            {
                "role": "system",
                "content": "Return strict JSON only. Choose builder only from ALLOWED_BUILDERS. All geometry must be MEASURED_SPEC references. Never invent coordinates or numeric dimensions.",
            },
            {
                "role": "user",
                "content": json.dumps({
                    "ALLOWED_BUILDERS": allowed,
                    "catalog_refs": catalog_summary,
                    "schema": schema_hint,
                })[:12000],
            },
        ],
    }
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read())
        text = raw["choices"][0]["message"]["content"]
        start, end = text.find("{"), text.rfind("}")
        parsed = json.loads(text[start : end + 1]) if start >= 0 and end > start else {}
        parsed.setdefault("CANDIDATE_SOURCE", "QWEN_PLAN")
        parsed.setdefault("plan_version", PLAN_VERSION)
        parsed.setdefault("part_id", part_id)
        return {"ok": True, "plan": parsed, "raw": text, "model": MODEL}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "model": MODEL}
