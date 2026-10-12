#!/usr/bin/env python3
"""Re-run tank CAD recovery with connected Qwen3-VL + MAC, reusing frozen P3.

Uses Qwen3-VL visual JSON plus the original Multi-Agent-CAD graph
(planner → architect → python coder → skill loop) to generate build123d CAD.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE_OBJ = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3_ROOT = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
V5_ROOT = ROOT / "ours3/tank_p3_45_component_pipeline_a_fullrun_v5"
OUT_DEFAULT = ROOT / "ours3/tank_p3_45_qwen3vl_mac_v6"
MAC_ENV_FILE = ROOT / "ours3/.mac_env"
BASELINE_MIXED_STEP = ROOT / "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/14_assembly/tank_p3_45_component_assembly.step"

sys.path.insert(0, str(ROOT / "scripts"))
import dual_modal_qwen3vl as qwen3vl  # noqa: E402
import tank_p3_45_component_pipeline_a_fullrun_v5 as tank_v5  # noqa: E402
import tank_p3_point2cad_component_local_qa_v2 as local_qa  # noqa: E402
import build_a_robot_pipeline_a_fullstack_repair_v2 as robot  # noqa: E402
import build_a_robot_fresh_generalization_v1 as robot_v1  # noqa: E402


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_mac_env() -> None:
    if not MAC_ENV_FILE.is_file():
        raise RuntimeError(f"MAC_ENV_MISSING:{MAC_ENV_FILE}")
    for line in MAC_ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))
    qwen3vl.load_mac_env()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})


def adapt_part(component: dict[str, Any]) -> dict[str, Any]:
    part = dict(component)
    part["source_obj"] = component["source_part_obj"]
    part["source_sha256"] = component["source_part_sha256"]
    part["triangle_ids_sha256"] = component["triangle_ids_hash"]
    return part


def copy_faceted_fallback(component: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    dest = component_dir / "10_fallback/faceted_fallback.step"
    dest.parent.mkdir(parents=True, exist_ok=True)
    candidates = [
        V5_ROOT / "03_components" / component["component_id"] / "selected" / "selected.step",
        V5_ROOT / "03_components" / component["component_id"] / "fallback" / "faceted_fallback.step",
    ]
    copied = None
    for path in candidates:
        if path.is_file():
            shutil.copy2(path, dest)
            copied = path
            break
    return {
        "component_id": component["component_id"],
        "backend": "FACETED_FALLBACK",
        "cad_native": False,
        "qa_pass": False,
        "step_path": str(dest.resolve()) if dest.is_file() else None,
        "status": "SUCCESS" if dest.is_file() else "FAIL",
        "failure_reason": None if dest.is_file() else "FACETED_FALLBACK_MISSING",
        "reused_from": str(copied) if copied else None,
        "representation": "MESH_DERIVED_FACETED_BREP",
    }


def qa_mac_candidate(part: dict[str, Any], candidate: dict[str, Any], qa_dir: Path) -> dict[str, Any]:
    qa_dir.mkdir(parents=True, exist_ok=True)
    step_path = Path(str(candidate.get("step_path") or ""))
    stl_path = qa_dir / f"{candidate.get('candidate_id', 'mac')}.stl"
    mesh = None
    if stl_path.is_file() and stl_path.stat().st_size > 0:
        try:
            loaded = trimesh.load(stl_path, force="mesh", process=False)
            if isinstance(loaded, trimesh.Trimesh) and len(loaded.faces):
                mesh = loaded
        except Exception:
            mesh = None
    if mesh is None and candidate.get("step_success") and step_path.is_file():
        mesh = robot_v1.tessellate_step(str(step_path), stl_path)
    if mesh is None:
        qa = {
            "qa_pass": False,
            "reject_reason": "STEP_RELOAD_OR_TESSELLATION_FAILED",
            "candidate_backend": "MAC_GENERATED_CAD",
        }
        dump_json(qa_dir / "qa.json", qa)
        candidate["qa"] = qa
        candidate["qa_pass"] = False
        return candidate
    qa = local_qa.local_component_qa(
        part,
        mesh,
        {"backend": "MAC_GENERATED_CAD", "shell": True, "solid": False, "cad_native": True},
        qa_dir,
    )
    dump_json(qa_dir / "qa.json", qa)
    candidate["qa"] = qa
    candidate["qa_pass"] = bool(qa.get("qa_pass"))
    candidate["cad_native"] = bool(qa.get("qa_pass"))
    candidate["coverage"] = qa.get("coarse_coverage")
    candidate["chamfer"] = qa.get("coarse_chamfer")
    if qa.get("qa_pass") and qa.get("candidate_to_source_transform") and not local_qa.transform_is_identity(qa["candidate_to_source_transform"]):
        aligned = qa_dir / "generated_aligned.step"
        if tank_v5.transform_step(step_path, aligned, np.asarray(qa["candidate_to_source_transform"], dtype=float)):
            candidate["step_path"] = str(aligned.resolve())
            candidate["alignment_baked"] = True
    return candidate


def select_component(mac_candidates: list[dict[str, Any]], fallback: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    passing = [item for item in mac_candidates if item.get("qa_pass") and item.get("step_path")]
    selected = max(passing, key=lambda item: float(item.get("coverage") or 0.0)) if passing else fallback
    selected_dir = component_dir / "09_ranking"
    selected_dir.mkdir(parents=True, exist_ok=True)
    dest = selected_dir / "selected.step"
    if selected.get("step_path") and Path(str(selected["step_path"])).is_file():
        shutil.copy2(selected["step_path"], dest)
    manifest = {
        "selected_backend": selected.get("backend"),
        "cad_native": bool(selected.get("cad_native") and selected.get("qa_pass")),
        "qa_pass": bool(selected.get("qa_pass")),
        "selected_step_path": str(dest.resolve()) if dest.is_file() else selected.get("step_path"),
        "coverage": selected.get("coverage") or (selected.get("qa") or {}).get("coarse_coverage"),
        "chamfer": selected.get("chamfer") or (selected.get("qa") or {}).get("coarse_chamfer"),
        "failure_reason": None if selected.get("qa_pass") else (selected.get("qa") or {}).get("reject_reason") or selected.get("failure_reason") or "NO_CAD_NATIVE_QA_PASS",
        "mac_candidates": mac_candidates,
        "fallback": fallback,
    }
    dump_json(selected_dir / "selected_manifest.json", manifest)
    return manifest


def rerank_component(part: dict[str, Any], out: Path) -> dict[str, Any]:
    cid = part["component_id"]
    component_dir = out / "03_components" / cid
    checkpoint = load_json(component_dir / "checkpoint.json", {}) or {}
    row = dict((checkpoint.get("row") or {}))
    cand_dir = component_dir / "07_candidates" / "mac_candidate_01"
    manifest_path = cand_dir / "candidate_manifest.json"
    step_path = cand_dir / "generated.step"
    if not manifest_path.is_file() or not step_path.is_file():
        return row
    candidate = load_json(manifest_path, {}) or {}
    candidate.setdefault("candidate_id", "MAC_CANDIDATE_01")
    candidate.setdefault("backend", "MAC_GENERATED_CAD")
    candidate["step_path"] = str(step_path.resolve())
    candidate["step_success"] = True
    qa_candidates = [qa_mac_candidate(part, candidate, component_dir / "08_qa" / candidate["candidate_id"])]
    fallback = copy_faceted_fallback(part, component_dir)
    selected = select_component(qa_candidates, fallback, component_dir)
    visual = load_json(component_dir / "05_dual_modal/visual_context.json", {}) or {}
    visual_parsed = visual.get("parsed") if isinstance(visual.get("parsed"), dict) else visual
    row.update(
        {
            "mac_qa_pass": sum(bool(item.get("qa_pass")) for item in qa_candidates),
            "selected_backend": selected["selected_backend"],
            "cad_native": bool(selected["cad_native"]),
            "qa_pass": bool(selected["qa_pass"]),
            "coverage": selected.get("coverage"),
            "chamfer": selected.get("chamfer"),
            "selected_step_path": selected.get("selected_step_path"),
            "failure_reason": selected.get("failure_reason"),
            "global_shape": (visual_parsed or {}).get("global_shape") or row.get("global_shape"),
            "likely_builder_family": (visual_parsed or {}).get("likely_builder_family") or row.get("likely_builder_family"),
        }
    )
    dump_json(component_dir / "checkpoint.json", {"status": "COMPLETE", "row": row})
    return row


def reexecute_runtime_component(part: dict[str, Any], out: Path) -> dict[str, Any]:
    cid = part["component_id"]
    component_dir = out / "03_components" / cid
    spec = robot.enriched_spec(part)
    if not (component_dir / "01_prepare/source_part.obj").is_file():
        robot.prepare_component(part, spec, component_dir)
    mac_candidates = robot.run_mac_candidates(part, spec, component_dir)
    qa_candidates = []
    for candidate in mac_candidates:
        qa_dir = component_dir / "08_qa" / candidate["candidate_id"]
        if qa_dir.exists():
            shutil.rmtree(qa_dir)
        qa_candidates.append(qa_mac_candidate(part, candidate, qa_dir))
        dump_json(Path(candidate.get("generated_code_path") or (component_dir / "07_candidates/mac_candidate_01/generated_code.py")).parent / "candidate_manifest.json", qa_candidates[-1])
    fallback = copy_faceted_fallback(part, component_dir)
    selected = select_component(qa_candidates, fallback, component_dir)
    visual = qwen3vl.visual_json_for_mac(component_dir)
    visual_manifest = load_json(component_dir / "05_dual_modal/mac_input_manifest.json", {}) or {}
    mac = load_json(component_dir / "06_mac/mac_hypotheses.json", {}) or {}
    row = {
        "component_id": cid,
        "p3_label": part.get("p3_label"),
        "triangle_count": part["triangle_count"],
        "P3_REEXECUTED": False,
        "MAC_API_REEXECUTED": bool(mac.get("MAC_API_REEXECUTED")),
        "MAC_JSON_REUSED": bool(mac.get("MAC_JSON_REUSED") or mac.get("hypotheses")),
        "VISUAL_MODEL": qwen3vl.visual_model(),
        "VISUAL_QWEN3VL_OK": bool(visual_manifest.get("VISUAL_QWEN3VL_OK") and visual is not None),
        "VISUAL_ENTERED_MAC_PROMPT": bool(visual_manifest.get("VISUAL_ENTERED_MAC_PROMPT") or visual_manifest.get("DUAL_MODAL_ACTUALLY_USED_BY_MAC")),
        "mac_hypotheses": len(qa_candidates),
        "mac_generated_code": sum(Path(str(item.get("generated_code_path") or "")).is_file() for item in qa_candidates),
        "mac_step_success": sum(bool(item.get("step_success")) for item in qa_candidates),
        "mac_qa_pass": sum(bool(item.get("qa_pass")) for item in qa_candidates),
        "selected_backend": selected["selected_backend"],
        "cad_native": bool(selected["cad_native"]),
        "qa_pass": bool(selected["qa_pass"]),
        "coverage": selected.get("coverage"),
        "chamfer": selected.get("chamfer"),
        "selected_step_path": selected.get("selected_step_path"),
        "failure_reason": selected.get("failure_reason"),
        "global_shape": (visual or {}).get("global_shape"),
        "likely_builder_family": (visual or {}).get("likely_builder_family"),
        "MAC_SUGGESTED_BUILDER": (qa_candidates[0].get("MAC_SUGGESTED_BUILDER") if qa_candidates else None),
        "RESOLVED_BUILDER_FAMILY": (qa_candidates[0].get("RESOLVED_BUILDER_FAMILY") if qa_candidates else None),
        "ACTUAL_EXECUTED_BUILDER": (qa_candidates[0].get("ACTUAL_EXECUTED_BUILDER") if qa_candidates else None),
        "RUNTIME_REEXECUTED": True,
    }
    dump_json(component_dir / "checkpoint.json", {"status": "COMPLETE", "row": row})
    return row


def process_component(part: dict[str, Any], out: Path, resume: bool, rerank: bool = False, reexecute_runtime: bool = False, reuse_mac: bool = True) -> dict[str, Any]:
    cid = part["component_id"]
    component_dir = out / "03_components" / cid
    checkpoint = component_dir / "checkpoint.json"
    robot.REUSE_MAC_DEFAULT = bool(reuse_mac)
    if reexecute_runtime:
        return reexecute_runtime_component(part, out)
    if rerank:
        if (load_json(checkpoint, {}) or {}).get("status") == "COMPLETE":
            return rerank_component(part, out)
        return (load_json(checkpoint) or {}).get("row") or {
            "component_id": cid,
            "selected_backend": "INCOMPLETE",
            "cad_native": False,
            "qa_pass": False,
        }
    if resume and (load_json(checkpoint, {}) or {}).get("status") == "COMPLETE":
        return (load_json(checkpoint) or {})["row"]
    spec = robot.enriched_spec(part)
    robot.prepare_component(part, spec, component_dir)
    visual = qwen3vl.visual_json_for_mac(component_dir)
    mac_candidates = robot.run_mac_candidates(part, spec, component_dir)
    qa_candidates = []
    for candidate in mac_candidates:
        qa_candidates.append(qa_mac_candidate(part, candidate, component_dir / "08_qa" / candidate["candidate_id"]))
    fallback = copy_faceted_fallback(part, component_dir)
    selected = select_component(qa_candidates, fallback, component_dir)
    visual_manifest = load_json(component_dir / "05_dual_modal/mac_input_manifest.json", {}) or {}
    row = {
        "component_id": cid,
        "p3_label": part["p3_label"],
        "triangle_count": part["triangle_count"],
        "P3_REEXECUTED": False,
        "VISUAL_MODEL": qwen3vl.visual_model(),
        "VISUAL_QWEN3VL_OK": bool(visual_manifest.get("VISUAL_QWEN3VL_OK") and visual is not None),
        "VISUAL_ENTERED_MAC_PROMPT": bool(visual_manifest.get("VISUAL_ENTERED_MAC_PROMPT") or visual_manifest.get("DUAL_MODAL_ACTUALLY_USED_BY_MAC")),
        "mac_hypotheses": len(qa_candidates),
        "mac_generated_code": sum(Path(str(item.get("generated_code_path") or "")).is_file() for item in qa_candidates),
        "mac_step_success": sum(bool(item.get("step_success")) for item in qa_candidates),
        "mac_qa_pass": sum(bool(item.get("qa_pass")) for item in qa_candidates),
        "selected_backend": selected["selected_backend"],
        "cad_native": bool(selected["cad_native"]),
        "qa_pass": bool(selected["qa_pass"]),
        "coverage": selected.get("coverage"),
        "chamfer": selected.get("chamfer"),
        "selected_step_path": selected.get("selected_step_path"),
        "failure_reason": selected.get("failure_reason"),
        "global_shape": (visual or {}).get("global_shape"),
        "likely_builder_family": (visual or {}).get("likely_builder_family"),
    }
    dump_json(checkpoint, {"status": "COMPLETE", "row": row})
    return row


def assemble_cad_native(rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    entries = [
        {
            "part_id": row["component_id"],
            "semantic_role": "MAC_GENERATED_CAD",
            "builder": "MAC_MULTI_BUILDER_RUNTIME",
            "route_status": "CAD_NATIVE_SELECTED",
            "quality_tag": "QWEN3VL_MAC_V6",
            "geometry_present": True,
            "fresh_step_path": row["selected_step_path"],
            "T_part_local_to_source_global": np.eye(4).tolist(),
        }
        for row in rows
        if row.get("cad_native") and row.get("selected_step_path") and Path(str(row["selected_step_path"])).is_file()
    ]
    return tank_v5.build_assembly(entries, output, "TANK_QWEN3VL_MAC_CAD_NATIVE")


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    load_mac_env()
    out = Path(args.output_root)
    for name in ("00_source", "01_frozen_p3", "03_components", "05_mixed_assembly", "06_cad_native_only", "artifacts", "logs"):
        (out / name).mkdir(parents=True, exist_ok=True)
    if getattr(args, "rerank", False) or getattr(args, "reexecute_runtime", False):
        health = load_json(out / "artifacts/qwen3vl_health.json", {"ok": True, "skipped": "reuse_mac_runtime"}) or {"ok": True}
        dump_json(out / "artifacts/qwen3vl_health.json", health)
    else:
        health = qwen3vl.healthcheck()
        dump_json(out / "artifacts/qwen3vl_health.json", health)
        if not health.get("ok"):
            raise RuntimeError(f"QWEN3VL_UNAVAILABLE:{health}")
    components = [adapt_part(item) for item in tank_v5.load_components(Path(args.p3_root), Path(args.source))]
    if args.limit:
        components = components[: int(args.limit)]
    dump_json(
        out / "00_source/source_manifest.json",
        {
            "source": str(Path(args.source).resolve()),
            "source_sha256": tank_v5.sha256_file(Path(args.source)),
            "P3_REEXECUTED": False,
        },
    )
    dump_json(
        out / "01_frozen_p3/frozen_p3_manifest.json",
        {
            "p3_root": str(Path(args.p3_root).resolve()),
            "P3_COMPONENT_COUNT": len(components),
            "P3_REEXECUTED": False,
            "component_ids": [item["component_id"] for item in components],
        },
    )
    rows: list[dict[str, Any]] = []
    for index, part in enumerate(components, start=1):
        print(f"[{index}/{len(components)}] {part['component_id']}", flush=True)
        row = process_component(
            part,
            out,
            args.resume,
            bool(getattr(args, "rerank", False)),
            reexecute_runtime=bool(getattr(args, "reexecute_runtime", False)),
            reuse_mac=bool(getattr(args, "reuse_mac", True)),
        )
        rows.append(row)
        print(
            f"  visual={row['VISUAL_QWEN3VL_OK']} mac_step={row['mac_step_success']} "
            f"qa={row['mac_qa_pass']} selected={row['selected_backend']}",
            flush=True,
        )
    fields = [
        "component_id",
        "triangle_count",
        "VISUAL_QWEN3VL_OK",
        "VISUAL_ENTERED_MAC_PROMPT",
        "mac_hypotheses",
        "mac_generated_code",
        "mac_step_success",
        "mac_qa_pass",
        "selected_backend",
        "cad_native",
        "coverage",
        "chamfer",
        "failure_reason",
        "global_shape",
        "likely_builder_family",
        "selected_step_path",
    ]
    write_csv(out / "artifacts/component_backend_manifest.csv", rows, fields)
    cad_native = [row for row in rows if row["cad_native"]]
    cad_step = out / "06_cad_native_only/tank_qwen3vl_mac_cad_native.step"
    mixed_step = out / "05_mixed_assembly/tank_qwen3vl_mac_mixed.step"
    cad_assembly = assemble_cad_native(cad_native, cad_step)
    if BASELINE_MIXED_STEP.is_file():
        shutil.copy2(BASELINE_MIXED_STEP, mixed_step)
        mixed_assembly = {
            "component_count": 45,
            "reused_baseline": True,
            "baseline_path": str(BASELINE_MIXED_STEP.resolve()),
            "reason": "FACETED_BASELINE_REUSED_CAD_NATIVE_RECORDED_SEPARATELY",
        }
    else:
        mixed_assembly = {"component_count": 0, "reason": "BASELINE_MISSING"}
    dump_json(out / "06_cad_native_only/assembly_result.json", cad_assembly)
    dump_json(out / "05_mixed_assembly/assembly_result.json", mixed_assembly)
    summary = {
        "CURRENT_GATE": "TANK_P3_45_QWEN3VL_MAC_V6_PARTIAL_PASS" if cad_native else "TANK_P3_45_QWEN3VL_MAC_V6_CAD_NATIVE_FAIL",
        "NEXT_PRIMARY_BLOCKER": "CAD_NATIVE_TRIANGLE_SUPPORT" if cad_native else "GENERIC_COMPONENT_CAD_GEOMETRY_FIDELITY",
        "P3_REEXECUTED": False,
        "P3_COMPONENT_COUNT": len(rows),
        "VISUAL_MODEL": qwen3vl.visual_model(),
        "VISUAL_BASE_URL": qwen3vl.visual_base_url(),
        "VISUAL_QWEN3VL_OK_COMPONENTS": sum(bool(row["VISUAL_QWEN3VL_OK"]) for row in rows),
        "VISUAL_ENTERED_MAC_PROMPT": sum(bool(row["VISUAL_ENTERED_MAC_PROMPT"]) for row in rows),
        "MAC_HYPOTHESES": sum(int(row["mac_hypotheses"]) for row in rows),
        "MAC_GENERATED_CODE_CREATED": sum(int(row["mac_generated_code"]) for row in rows),
        "MAC_STEP_SUCCESS": sum(int(row["mac_step_success"]) for row in rows),
        "MAC_QA_PASS": sum(int(row["mac_qa_pass"]) for row in rows),
        "CAD_NATIVE_COMPONENT_COUNT": len(cad_native),
        "CAD_NATIVE_RECOVERY_RATE": float(len(cad_native) / max(len(rows), 1)),
        "FACETED_FALLBACK_SELECTED": sum(not row["cad_native"] for row in rows),
        "CAD_NATIVE_ONLY_STEP": str(cad_step) if cad_step.is_file() else None,
        "MIXED_STEP": str(mixed_step) if mixed_step.is_file() else None,
        "runtime_seconds": time.time() - started,
    }
    dump_json(out / "artifacts/final_summary.json", summary)
    report = ["# TANK_P3_45_QWEN3VL_MAC_V6", ""]
    report.extend(f"{key}={value}" for key, value in summary.items())
    (out / "artifacts/TANK_P3_45_QWEN3VL_MAC_V6_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for key, value in summary.items():
        print(f"{key}={value}", flush=True)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE_OBJ))
    parser.add_argument("--p3-root", default=str(FROZEN_P3_ROOT))
    parser.add_argument("--output-root", default=str(OUT_DEFAULT))
    parser.add_argument("--skip-p3", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--rerank", action="store_true", help="Re-QA existing MAC STEPs with current coverage gate; do not re-run MAC.")
    parser.add_argument("--reuse-mac", action="store_true", default=True, help="Reuse existing MAC JSON; do not call the architect API.")
    parser.add_argument("--no-reuse-mac", action="store_false", dest="reuse_mac")
    parser.add_argument("--reexecute-runtime", action="store_true", help="Reuse MAC JSON and rebuild STEP with generic_cad_runtime, then QA/rank.")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    if not args.skip_p3:
        raise RuntimeError("P3_REEXECUTION_FORBIDDEN_USE_--skip-p3")
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
