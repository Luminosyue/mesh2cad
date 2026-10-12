#!/usr/bin/env python3
"""Step 2 runner: Geometry → Feature Planner → (rule|LLM) → CAD DSL → STEP.

Pipeline:
  P3 Part → Dora spatial pack → Geometry summary
         → CAD Feature Planner (rules)
         → rule|llm DSL coder → OCC/CadQuery → STEP
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, extract_dsl_code, parse_dsl
from edge_aware_cad_planner_v1.cad_feature_planner import plan_cad_features, render_operation_plan
from edge_aware_cad_planner_v1.geometry_summary import build_geometry_summary, render_cad_brief
from edge_aware_cad_planner_v1.llm_planner import plan_llm_dsl
from edge_aware_cad_planner_v1.rule_planner import plan_rule_dsl

DEFAULT_DATASET = ROOT / "cad_spatial_dataset"
DEFAULT_OUT = ROOT / "ours3/edge_aware_cad_planner_v1"


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _validate_against_plan(dsl_code: str, feature_plan: dict) -> None:
    allow = feature_plan.get("allowed_operations") or []
    if "Cut" in dsl_code and "Cut" not in allow:
        raise ValueError("LLM emitted Cut but Cut is not allowed by feature plan")
    # required Cut must appear
    needs_cut = any(
        s.get("required") and (s.get("op") == "Cut" or s.get("role") in {"inner_bore"})
        for s in (feature_plan.get("operation_plan") or [])
    )
    if needs_cut and "Cut" not in dsl_code:
        raise ValueError(
            f"feature plan {feature_plan.get('component_type')} requires Cut, but DSL has none"
        )


def run_part(part_dir: Path, out_dir: Path, planner: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_geometry_summary(part_dir)
    brief = render_cad_brief(summary)
    feature_plan = plan_cad_features(summary)
    plan_text = render_operation_plan(feature_plan)

    write_json(out_dir / "geometry_summary.json", summary)
    (out_dir / "cad_brief.txt").write_text(brief, encoding="utf-8")
    write_json(out_dir / "feature_plan.json", feature_plan)
    (out_dir / "feature_plan.txt").write_text(plan_text, encoding="utf-8")

    rule = plan_rule_dsl(summary, feature_plan)
    write_json(out_dir / "rule_plan.json", rule)
    (out_dir / "rule.dsl").write_text(rule["dsl"], encoding="utf-8")

    chosen = rule
    llm_info = None
    if planner in {"llm", "auto"}:
        llm_info = plan_llm_dsl(brief, summary, feature_plan=feature_plan, plan_text=plan_text)
        write_json(out_dir / "llm_plan.json", llm_info)
        if llm_info.get("ok"):
            raw = llm_info.get("dsl_raw") or ""
            (out_dir / "llm_raw.txt").write_text(raw, encoding="utf-8")
            try:
                dsl_code = extract_dsl_code(raw)
                _validate_against_plan(dsl_code, feature_plan)
                parse_dsl(dsl_code)
                chosen = {
                    "planner": "llm",
                    "strategy": f"llm_{feature_plan.get('component_type', 'plan').lower()}",
                    "component_type": feature_plan.get("component_type"),
                    "dsl": dsl_code if dsl_code.endswith("\n") else dsl_code + "\n",
                    "model": llm_info.get("model"),
                }
            except Exception as exc:
                llm_info["parse_error"] = f"{type(exc).__name__}: {exc}"
                write_json(out_dir / "llm_plan.json", llm_info)
                if planner == "llm":
                    raise
                chosen = {**rule, "fallback_from_llm_error": llm_info["parse_error"]}
        elif planner == "llm":
            raise RuntimeError(llm_info.get("error") or "LLM planner failed")
        else:
            chosen = {**rule, "fallback_from_llm_error": llm_info.get("error")}

    write_json(out_dir / "chosen_plan.json", chosen)
    (out_dir / "program.dsl").write_text(chosen["dsl"], encoding="utf-8")

    program = parse_dsl(chosen["dsl"])
    export = execute_dsl(
        program,
        step_path=out_dir / f"{summary['part_id']}.step",
        stl_path=out_dir / f"{summary['part_id']}_reconstructed.stl",
    )

    report = {
        "part_id": summary["part_id"],
        "planner_requested": planner,
        "planner_used": chosen.get("planner"),
        "strategy": chosen.get("strategy"),
        "component_type": feature_plan.get("component_type"),
        "feature_plan": feature_plan,
        "allowed_operations": feature_plan.get("allowed_operations"),
        "detected_features": summary.get("detected_features"),
        "closed_feature_candidates": summary.get("closed_feature_candidates"),
        "dsl": chosen["dsl"],
        "export": export,
        "llm": llm_info,
    }
    write_json(out_dir / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Edge-aware CAD Planner Step 2")
    parser.add_argument("--part", required=True, help="PART_019 or path to part dir")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--planner",
        choices=["rule", "llm", "auto"],
        default="rule",
        help="rule=feature-plan→DSL; llm=API coder; auto=LLM then fall back to rule",
    )
    args = parser.parse_args()

    part = Path(args.part)
    if part.is_dir():
        part_dir = part
        part_id = part_dir.name
    else:
        part_id = str(args.part)
        part_dir = Path(args.dataset) / part_id
    if not (part_dir / "meta.json").is_file():
        raise SystemExit(f"missing meta.json under {part_dir}")

    out_dir = Path(args.out) / part_id
    report = run_part(part_dir, out_dir, args.planner)
    print(
        json.dumps(
            {
                "part_id": report["part_id"],
                "component_type": report.get("component_type"),
                "planner_used": report["planner_used"],
                "strategy": report["strategy"],
                "allowed_operations": report["allowed_operations"],
                "step": report["export"].get("step"),
                "stl": report["export"].get("stl"),
                "dsl": report["dsl"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
