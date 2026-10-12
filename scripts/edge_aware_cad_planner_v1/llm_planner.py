"""LLM CAD coder: Feature operation plan + geometry brief → executable CAD DSL.

Does NOT invent CAD strategy. Follows the Feature Planner plan.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MAC_ENV = ROOT / "ours3/.mac_env"

SYSTEM_PROMPT = """You are a CAD DSL coder (not a CAD strategist).
Given a CAD operation plan AND geometry evidence (NOT a point cloud), generate executable DSL.

Hard rules:
1. Follow the CAD operation plan step-by-step. Do not invent a different strategy.
2. If the plan requires Cut / inner_bore / multi-radius construction, you MUST implement it.
3. Do NOT collapse a multi-step plan into a single plain Cylinder unless the plan says OUTER_CYLINDER.
4. Only use allowed_operations from the plan.
5. Units are SOURCE_NATIVE — use numeric values from the plan / geometry brief.
6. Cylinder origin MUST be the BOTTOM center when provided (use plan origin / bottom_origin).
7. Output ONLY DSL assignments ending with `result = ...`. No markdown, no prose.

DSL ops:
  Cylinder(radius=..., height=..., axis=(ax,ay,az), origin=(x,y,z))
  Extrude(Circle(radius=...), height=..., axis=..., origin=...)
  Revolve(radius=..., height=..., axis=..., origin=...)
  Cut(a, b)
"""


def load_mac_env(path: Path = MAC_ENV) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values


def text_base_url() -> str:
    load_mac_env()
    return os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or ""


def text_api_key() -> str:
    load_mac_env()
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("DASHSCOPE_API_KEY") or ""


def text_model() -> str:
    load_mac_env()
    return os.environ.get("CAD_PLANNER_MODEL") or "qwen-plus"


def chat_completions(messages: list[dict[str, str]], *, temperature: float = 0.1, timeout: float = 90.0) -> str:
    base = text_base_url().rstrip("/")
    if not base:
        raise RuntimeError("OPENAI_BASE_URL not configured")
    url = base + "/chat/completions"
    payload = {
        "model": text_model(),
        "messages": messages,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {text_api_key()}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def build_llm_user_prompt(
    geometry_brief: str,
    feature_plan: dict[str, Any],
    plan_text: str,
) -> str:
    compact = {
        "component_type": feature_plan.get("component_type"),
        "operation_plan": feature_plan.get("operation_plan"),
        "allowed_operations": feature_plan.get("allowed_operations"),
        "must_follow": feature_plan.get("must_follow"),
        "evidence": feature_plan.get("evidence"),
        "axis": feature_plan.get("axis"),
    }
    return (
        "Geometry evidence:\n"
        f"{geometry_brief.rstrip()}\n\n"
        f"{plan_text.rstrip()}\n\n"
        "Compact operation-plan JSON:\n"
        f"{json.dumps(compact, indent=2)}\n\n"
        "Given CAD operation plan, generate executable DSL.\n"
        "DSL format example:\n"
        "  body_0 = Cylinder(radius=..., height=..., axis=(...), origin=(...))\n"
        "  cut_0 = Cylinder(radius=..., height=..., axis=(...), origin=(...))\n"
        "  result = Cut(body_0, cut_0)\n"
        "Only emit DSL code.\n"
    )


def plan_llm_dsl(
    brief: str,
    summary: dict[str, Any] | None = None,
    feature_plan: dict[str, Any] | None = None,
    plan_text: str | None = None,
) -> dict[str, Any]:
    if feature_plan is None:
        # backward-compatible fallback: still ask for DSL, but without strategy bias
        user = (
            brief
            + "\n\nGiven CAD operation plan, generate executable DSL.\n"
            + "Only emit DSL code.\n"
        )
        if summary is not None:
            compact = {
                "axis_extent": summary.get("axis_extent"),
                "closed_feature_candidates": [
                    {"radius": c.get("radius"), "confidence": c.get("confidence"), "source": c.get("source")}
                    for c in (summary.get("closed_feature_candidates") or [])[:6]
                ],
                "detected_features": summary.get("detected_features"),
            }
            user = brief + "\n\nCompact JSON:\n" + json.dumps(compact, indent=2) + "\n\n" + (
                "Given CAD operation plan, generate executable DSL.\nOnly emit DSL code.\n"
            )
    else:
        from .cad_feature_planner import render_operation_plan

        user = build_llm_user_prompt(
            brief,
            feature_plan,
            plan_text or render_operation_plan(feature_plan),
        )

    try:
        content = chat_completions(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ]
        )
        return {
            "planner": "llm",
            "model": text_model(),
            "dsl_raw": content,
            "ok": True,
            "prompt_mode": "operation_plan_to_dsl",
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, RuntimeError) as exc:
        return {
            "planner": "llm",
            "model": text_model(),
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "prompt_mode": "operation_plan_to_dsl",
        }
