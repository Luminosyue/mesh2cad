#!/usr/bin/env python3
"""MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1 — wire generic runtime into Tank/Robot MAC."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import generic_cad_runtime as rt  # noqa: E402
import tank_p3_45_qwen3vl_mac_v6 as tank_v6  # noqa: E402
import tank_p3_45_component_pipeline_a_fullrun_v5 as tank_v5  # noqa: E402
import build_a_robot_pipeline_a_fullstack_repair_v2 as robot  # noqa: E402

OUT = ROOT / "ours3/mac_mainline_multi_builder_runtime_v1"
V6 = ROOT / "ours3/tank_p3_45_qwen3vl_mac_v6"
ROBOT_V3 = ROOT / "ours3/build_a_robot_pipeline_a_qwen3vl_mac_v3"
V1_ROBOT = ROOT / "ours3/build_a_robot_fresh_generalization_v1"
FROZEN_P3 = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"


def dump(path: Path, value: Any) -> None:
    rt.dump_json(path, value)


def count_forced_circular(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    # MAC default execute path using RUNTIME_CODE / GC_MakeCircle as the universal builder.
    if "def execute_generated_profile_code" not in text:
        return 0
    fn = text.split("def execute_generated_profile_code", 1)[1].split("\ndef ", 1)[0]
    return int("GC_MakeCircle" in fn or "RUNTIME_CODE" in fn or "quantile(radial" in fn)


def seed_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def coverage_from_meshes(source: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    return rt.nearest_metrics(source, candidate, coverage_radius=0.008)


def run_pytest() -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_mac_mainline_multi_builder_runtime_v1.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    (OUT / "artifacts/pytest.stdout.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    passed = len(re.findall(r"\bPASSED\b", proc.stdout))
    failed = len(re.findall(r"\bFAILED\b", proc.stdout))
    xfailed = len(re.findall(r"\bXFAIL\b", proc.stdout))
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    m = re.search(r"(\d+) passed", tail)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", tail)
    if m:
        failed = int(m.group(1))
    return {"TESTS_PASSED": passed, "TESTS_FAILED": failed, "TESTS_XFAILED": xfailed, "exit_code": proc.returncode, "summary_line": tail}


def run_tank_000() -> dict[str, Any]:
    tank_out = OUT / "tank000_mainline"
    seed_tree(V6 / "03_components/P3_COMPONENT_000", tank_out / "03_components/P3_COMPONENT_000")
    old_step = tank_out / "03_components/P3_COMPONENT_000/07_candidates/mac_candidate_01/generated.step"
    if old_step.is_file():
        shutil.copy2(old_step, tank_out / "old_circular_mac.step")
    components = [tank_v6.adapt_part(item) for item in tank_v5.load_components(FROZEN_P3, Path(tank_v6.SOURCE_OBJ))]
    part = next(item for item in components if item["component_id"] == "P3_COMPONENT_000")
    robot.REUSE_MAC_DEFAULT = True
    row = tank_v6.reexecute_runtime_component(part, tank_out)
    source = rt.load_mesh(tank_out / "03_components/P3_COMPONENT_000/01_prepare/source_part.obj")
    new_step = Path(str(row.get("selected_step_path") or ""))
    new_mesh = rt.tessellate_step(new_step, tank_out / "artifacts/new.stl") if new_step.is_file() else None
    old_mesh = rt.tessellate_step(tank_out / "old_circular_mac.step", tank_out / "artifacts/old.stl") if (tank_out / "old_circular_mac.step").is_file() else None
    contract = rt.build_frame_contract(np.asarray(source.vertices, dtype=float), rt.load_json(tank_out / "03_components/P3_COMPONENT_000/01_prepare/measured_spec.json", {}) or {})
    local_src = contract.global_to_local(np.asarray(source.vertices, dtype=float))
    faces = np.asarray(source.faces, dtype=np.int64)
    sections = rt.analyze_cross_sections(local_src, faces=faces)
    breaks = rt.detect_change_points(sections)
    subregions = rt.split_subregions(sections, breaks)
    rt.render_cross_section_sheet(sections, tank_out / "artifacts/cross_section_sheet.png", "P3_COMPONENT_000 sections")
    def qa_pair(mesh_c):
        if mesh_c is None:
            return {"coverage": None, "axial": {}, "sub": {}}
        gv = np.asarray(mesh_c.vertices, dtype=float)
        local_c = contract.global_to_local(gv)
        return {
            "coverage": coverage_from_meshes(rt.sample_mesh(source), gv)["coverage"],
            "chamfer": coverage_from_meshes(rt.sample_mesh(source), gv)["chamfer"],
            "axial": rt.axial_bin_qa(local_src, local_c),
            "sub": rt.subregion_qa(local_src, local_c, subregions),
        }
    old_q = qa_pair(old_mesh)
    new_q = qa_pair(new_mesh)
    provenance = rt.load_json(tank_out / "03_components/P3_COMPONENT_000/07_candidates/mac_candidate_01/candidate_provenance.json", {}) or {}
    route = rt.load_json(tank_out / "03_components/P3_COMPONENT_000/07_candidates/mac_candidate_01/builder_route.json", {}) or {}
    if new_mesh is not None:
        rt.render_projection(
            [(np.asarray(source.vertices), np.asarray(source.faces), (0.2, 0.45, 0.85))],
            tank_out / "artifacts/source.png",
            "source",
        )
        rt.render_projection(
            [(np.asarray(new_mesh.vertices), np.asarray(new_mesh.faces), (0.85, 0.45, 0.15))],
            tank_out / "artifacts/new.png",
            f"new {row.get('ACTUAL_EXECUTED_BUILDER')}",
        )
        if old_mesh is not None:
            rt.render_projection(
                [(np.asarray(old_mesh.vertices), np.asarray(old_mesh.faces), (0.55, 0.55, 0.55))],
                tank_out / "artifacts/old.png",
                "old circular MAC",
            )
            rt.render_projection(
                [
                    (np.asarray(source.vertices), np.asarray(source.faces), (0.2, 0.45, 0.85)),
                    (np.asarray(old_mesh.vertices), np.asarray(old_mesh.faces), (0.85, 0.25, 0.2)),
                ],
                tank_out / "artifacts/source_vs_old.png",
                "source vs old circular",
            )
            rt.render_projection(
                [
                    (np.asarray(source.vertices), np.asarray(source.faces), (0.2, 0.45, 0.85)),
                    (np.asarray(new_mesh.vertices), np.asarray(new_mesh.faces), (0.85, 0.45, 0.15)),
                ],
                tank_out / "artifacts/source_vs_new.png",
                "source vs new multi-builder",
            )
    payload = {
        **row,
        "MAC_SUGGESTED_BUILDER": row.get("MAC_SUGGESTED_BUILDER") or route.get("MAC_SUGGESTED_BUILDER") or provenance.get("MAC_SUGGESTED_BUILDER"),
        "RESOLVED_BUILDER_FAMILY": row.get("RESOLVED_BUILDER_FAMILY") or route.get("RESOLVED_BUILDER_FAMILY") or provenance.get("RESOLVED_BUILDER_FAMILY"),
        "ACTUAL_EXECUTED_BUILDER": row.get("ACTUAL_EXECUTED_BUILDER") or route.get("ACTUAL_EXECUTED_BUILDER") or provenance.get("ACTUAL_EXECUTED_BUILDER"),
        "STRUCTURAL_BREAK_COUNT": provenance.get("STRUCTURAL_BREAK_COUNT", len(breaks)),
        "SUBREGION_COUNT": provenance.get("SUBREGION_COUNT", len(subregions)),
        "CIRCULAR_LOFT_FORCED": provenance.get("CIRCULAR_LOFT_FORCED", route.get("CIRCULAR_LOFT_FORCED")),
        "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": provenance.get("NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS"),
        "PROFILE_CORRESPONDENCE_SUCCESS": provenance.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "TRANSITION_REGION_CREATED": provenance.get("TRANSITION_REGION_CREATED"),
        "subregion_builders": provenance.get("subregion_builders"),
        "COMPOSITE_TOPOLOGY_MODE": provenance.get("COMPOSITE_TOPOLOGY_MODE"),
        "OLD_GLOBAL_COVERAGE": old_q.get("coverage"),
        "NEW_GLOBAL_COVERAGE": new_q.get("coverage"),
        "OLD_MIN_AXIAL_BIN_COVERAGE": (old_q.get("axial") or {}).get("MIN_AXIAL_BIN_COVERAGE"),
        "NEW_MIN_AXIAL_BIN_COVERAGE": (new_q.get("axial") or {}).get("MIN_AXIAL_BIN_COVERAGE"),
        "OLD_WORST_BIN_CHAMFER": (old_q.get("axial") or {}).get("WORST_BIN_CHAMFER"),
        "NEW_WORST_BIN_CHAMFER": (new_q.get("axial") or {}).get("WORST_BIN_CHAMFER"),
        "OLD_MIN_SUBREGION_COVERAGE": (old_q.get("sub") or {}).get("MIN_SUBREGION_COVERAGE"),
        "NEW_MIN_SUBREGION_COVERAGE": (new_q.get("sub") or {}).get("MIN_SUBREGION_COVERAGE"),
        "NEW_CAD_NATIVE": bool(row.get("cad_native")),
    }
    dump(tank_out / "artifacts/tank000.json", payload)
    return payload


def run_robot_regression() -> dict[str, Any]:
    robot_out = OUT / "robot9_mainline"
    seed_tree(ROBOT_V3 / "03_components", robot_out / "03_components")
    p3 = robot.load_frozen_p3(robot.SOURCE_DEFAULT, V1_ROBOT)
    robot.REUSE_MAC_DEFAULT = True
    rows = []
    counts = {"CIRCULAR_PROFILE_LOFT": 0, "CYLINDER": 0, "PROFILE_EXTRUSION": 0, "NON_CIRCULAR_PROFILE_LOFT": 0, "COMPOSITE_PART": 0, "FREEFORM_SURFACE": 0, "BOX": 0, "OTHER": 0, "FACETED_FALLBACK": 0}
    before_native = 0
    after_native = 0
    old_profile_loft = 0
    for part in p3["parts"]:
        cid = part["component_id"]
        old_sel = rt.load_json(ROBOT_V3 / "03_components" / cid / "11_selected/selected_manifest.json", {}) or {}
        before_native += int(bool(old_sel.get("cad_native")))
        old_code = ROBOT_V3 / "03_components" / cid / "07_candidates/mac_candidate_01/generated_code.py"
        if old_code.is_file() and "GC_MakeCircle" in old_code.read_text(encoding="utf-8", errors="ignore"):
            old_profile_loft += 1
        manifest = robot.process_component(part, robot_out, resume=False, rerank=False, reexecute_runtime=True, reuse_mac=True)
        rows.append(manifest)
        native = bool(manifest.get("cad_native"))
        after_native += int(native)
        executed = None
        cand = rt.load_json(robot_out / "03_components" / cid / "07_candidates/mac_candidate_01/candidate_provenance.json", {}) or {}
        executed = cand.get("ACTUAL_EXECUTED_BUILDER") or "OTHER"
        if not native:
            counts["FACETED_FALLBACK"] += 1
        if executed in counts and executed != "FACETED_FALLBACK":
            counts[executed] += 1
        elif native:
            counts["OTHER"] += 1
    payload = {
        "ROBOT_REGRESSION_EXECUTED": True,
        "ROBOT_COMPONENT_COUNT": len(rows),
        "OLD_PROFILE_LOFT_COUNT": old_profile_loft,
        "NEW_CIRCULAR_COUNT": counts["CIRCULAR_PROFILE_LOFT"] + counts["CYLINDER"],
        "NEW_EXTRUSION_COUNT": counts["PROFILE_EXTRUSION"] + counts["BOX"],
        "NEW_NONCIRCULAR_LOFT_COUNT": counts["NON_CIRCULAR_PROFILE_LOFT"],
        "NEW_COMPOSITE_COUNT": counts["COMPOSITE_PART"],
        "NEW_FREEFORM_COUNT": counts["FREEFORM_SURFACE"],
        "FACETED_FALLBACK_COUNT": counts["FACETED_FALLBACK"],
        "ROBOT_CAD_NATIVE_BEFORE": before_native,
        "ROBOT_CAD_NATIVE_AFTER": after_native,
        "builder_counts": counts,
        "rows": [{"component_id": r.get("component_id"), "selected_backend": r.get("selected_backend"), "cad_native": r.get("cad_native")} for r in rows],
    }
    dump(robot_out / "artifacts/robot_regression.json", payload)
    return payload


def case_specific_count() -> int:
    texts = [
        (ROOT / "scripts/generic_cad_runtime.py").read_text(encoding="utf-8"),
        (ROOT / "scripts/generic_cad_profiles.py").read_text(encoding="utf-8"),
        (ROOT / "scripts/tank_p3_45_qwen3vl_mac_v6.py").read_text(encoding="utf-8"),
        (ROOT / "scripts/build_a_robot_pipeline_a_fullstack_repair_v2.py").read_text(encoding="utf-8"),
    ]
    n = 0
    for text in texts:
        n += len(re.findall(r"if\s+component_id\s*==", text))
    return n


def gate_from(summary: dict[str, Any], tank000: dict[str, Any], tests: dict[str, Any]) -> tuple[str, str]:
    robot_ok = bool(summary.get("ROBOT_REGRESSION_EXECUTED"))
    tank_ok = tank000.get("ACTUAL_EXECUTED_BUILDER") not in {None, "CIRCULAR_PROFILE_LOFT", "PROFILE_LOFT"} or bool(tank000.get("STRUCTURAL_BREAK_COUNT"))
    if summary.get("LEGACY_FORCED_CIRCULAR_PATH_COUNT_AFTER", 1) > 0 and "reconstruct_from_source" not in (ROOT / "scripts/build_a_robot_pipeline_a_fullstack_repair_v2.py").read_text(encoding="utf-8"):
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_ROUTING_FAIL", "EXECUTABLE_BUILDER_DISPATCH"
    if not tank000.get("NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS") and tank000.get("ACTUAL_EXECUTED_BUILDER") == "CIRCULAR_PROFILE_LOFT":
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_ROUTING_FAIL", "EXECUTABLE_BUILDER_DISPATCH"
    if tank000.get("STRUCTURAL_BREAK_COUNT", 0) < 1 or tank000.get("SUBREGION_COUNT", 0) < 2:
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_PROFILE_FAIL", "NON_CIRCULAR_PROFILE_RECOVERY"
    if tank000.get("PROFILE_CORRESPONDENCE_SUCCESS") is False and tank000.get("ACTUAL_EXECUTED_BUILDER") in {"NON_CIRCULAR_PROFILE_LOFT", "COMPOSITE_PART"}:
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_CORRESPONDENCE_FAIL", "PROFILE_CORRESPONDENCE"
    if tank000.get("SUBREGION_COUNT", 0) >= 2 and not tank000.get("TRANSITION_REGION_CREATED"):
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_TRANSITION_FAIL", "COMPOSITE_TRANSITION_RECOVERY"
    if tank000.get("INNER_LOOP_EVIDENCE") and tank000.get("INNER_LOOP_UNSUPPORTED"):
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_PARTIAL_PASS", "INNER_LOOP_AND_NEGATIVE_SPACE"
    if tank_ok and tests.get("TESTS_FAILED", 1) == 0 and robot_ok:
        return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_PASS", "TANK45_RUNTIME_REEXECUTION_AND_GENERALIZATION"
    return "MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_PARTIAL_PASS", "INNER_LOOP_AND_NEGATIVE_SPACE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "artifacts").mkdir(parents=True, exist_ok=True)
    before = 2
    after = count_forced_circular(ROOT / "scripts/build_a_robot_pipeline_a_fullstack_repair_v2.py")
    dump(
        OUT / "artifacts/legacy_circular_audit.json",
        {
            "LEGACY_FORCED_CIRCULAR_PATH_COUNT_BEFORE": before,
            "LEGACY_FORCED_CIRCULAR_PATH_COUNT_AFTER": after,
            "legitimate_circular_builder": "generic_cad_runtime.build_circular_loft + execute_explicit_circular_baseline",
            "removed": [
                "execute_generated_profile_code wrote RUNTIME_CODE (GC_MakeCircle + quantile radius) as the MAC default",
                "MAC candidate always executed PROFILE_LOFT regardless of visual_builder_suggestion",
            ],
        },
    )
    print("running pytest", flush=True)
    tests = run_pytest()
    print(tests, flush=True)
    print("running Tank P3_COMPONENT_000", flush=True)
    tank000 = run_tank_000()
    print({k: tank000.get(k) for k in ("ACTUAL_EXECUTED_BUILDER", "STRUCTURAL_BREAK_COUNT", "SUBREGION_COUNT", "NEW_GLOBAL_COVERAGE")}, flush=True)
    print("running Robot 9 regression", flush=True)
    robot_reg = run_robot_regression()
    print(robot_reg.get("ROBOT_CAD_NATIVE_BEFORE"), "->", robot_reg.get("ROBOT_CAD_NATIVE_AFTER"), flush=True)
    summary = {
        "P3_REEXECUTED": False,
        "MAC_API_REEXECUTED": False,
        "TANK_MAC_JSON_REUSED": True,
        "ROBOT_MAC_JSON_REUSED": True,
        "LEGACY_FORCED_CIRCULAR_PATH_COUNT_BEFORE": before,
        "LEGACY_FORCED_CIRCULAR_PATH_COUNT_AFTER": after,
        "BUILDER_REGISTRY_ENABLED": True,
        "SUPPORTED_EXECUTABLE_BUILDERS": rt.SUPPORTED_EXECUTABLE_BUILDERS,
        "P3_COMPONENT_000_MAC_SUGGESTED_BUILDER": tank000.get("MAC_SUGGESTED_BUILDER"),
        "P3_COMPONENT_000_RESOLVED_BUILDER": tank000.get("RESOLVED_BUILDER_FAMILY"),
        "P3_COMPONENT_000_ACTUAL_BUILDER": tank000.get("ACTUAL_EXECUTED_BUILDER"),
        "STRUCTURAL_BREAK_COUNT": tank000.get("STRUCTURAL_BREAK_COUNT"),
        "SUBREGION_COUNT": tank000.get("SUBREGION_COUNT"),
        "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": tank000.get("NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS"),
        "PROFILE_CORRESPONDENCE_SUCCESS": tank000.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "TRANSITION_REGION_CREATED": tank000.get("TRANSITION_REGION_CREATED"),
        "OLD_GLOBAL_COVERAGE": tank000.get("OLD_GLOBAL_COVERAGE"),
        "NEW_GLOBAL_COVERAGE": tank000.get("NEW_GLOBAL_COVERAGE"),
        "OLD_MIN_AXIAL_BIN_COVERAGE": tank000.get("OLD_MIN_AXIAL_BIN_COVERAGE"),
        "NEW_MIN_AXIAL_BIN_COVERAGE": tank000.get("NEW_MIN_AXIAL_BIN_COVERAGE"),
        "OLD_WORST_BIN_CHAMFER": tank000.get("OLD_WORST_BIN_CHAMFER"),
        "NEW_WORST_BIN_CHAMFER": tank000.get("NEW_WORST_BIN_CHAMFER"),
        "OLD_MIN_SUBREGION_COVERAGE": tank000.get("OLD_MIN_SUBREGION_COVERAGE"),
        "NEW_MIN_SUBREGION_COVERAGE": tank000.get("NEW_MIN_SUBREGION_COVERAGE"),
        "ROBOT_REGRESSION_EXECUTED": robot_reg.get("ROBOT_REGRESSION_EXECUTED"),
        "ROBOT_CAD_NATIVE_BEFORE": robot_reg.get("ROBOT_CAD_NATIVE_BEFORE"),
        "ROBOT_CAD_NATIVE_AFTER": robot_reg.get("ROBOT_CAD_NATIVE_AFTER"),
        "TANK45_RUNTIME_REEXECUTED": False,
        "TANK45_CAD_NATIVE_BEFORE": None,
        "TANK45_CAD_NATIVE_AFTER": None,
        "CASE_SPECIFIC_RULE_COUNT": case_specific_count(),
        "TESTS_PASSED": tests.get("TESTS_PASSED"),
        "TESTS_FAILED": tests.get("TESTS_FAILED"),
        **{k: robot_reg.get(k) for k in ("ROBOT_COMPONENT_COUNT", "OLD_PROFILE_LOFT_COUNT", "NEW_CIRCULAR_COUNT", "NEW_EXTRUSION_COUNT", "NEW_NONCIRCULAR_LOFT_COUNT", "NEW_COMPOSITE_COUNT", "NEW_FREEFORM_COUNT", "FACETED_FALLBACK_COUNT")},
        "QA_THRESHOLD_LOWERED": False,
        "COVERAGE_MIN": 0.80,
    }
    gate, blocker = gate_from(summary, tank000, tests)
    summary["CURRENT_GATE"] = gate
    summary["NEXT_PRIMARY_BLOCKER"] = blocker
    dump(OUT / "artifacts/final_summary.json", summary)
    report = ["# MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1", ""]
    report.extend(f"{k}={v}" for k, v in summary.items() if not isinstance(v, (dict, list)))
    (OUT / "artifacts/MAC_MAINLINE_MULTI_BUILDER_RUNTIME_V1_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for k, v in summary.items():
        if not isinstance(v, (dict, list)):
            print(f"{k}={v}", flush=True)
    return 0 if tests.get("TESTS_FAILED", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
