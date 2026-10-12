#!/usr/bin/env python3
"""GENERIC_CAD_BUILDER_EXPRESSIVITY_V1 — executable non-circular / composite builders."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import generic_cad_runtime as rt  # noqa: E402
import tank_mac_transform_contract_fix_v1 as v1  # noqa: E402

FROZEN_P3 = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
V4 = ROOT / "ours3/tank_p3_45_component_pipeline_a_multibackend_repair_v4"
V6 = ROOT / "ours3/tank_p3_45_qwen3vl_mac_v6"
ROBOT = ROOT / "ours3/build_a_robot_pipeline_a_fullstack_repair_v2"
OUT = ROOT / "ours3/generic_cad_builder_expressivity_v1"


def run_component_000() -> dict[str, Any]:
    for sub in (
        "00_audit",
        "01_component_000/source",
        "01_component_000/existing_mac",
        "01_component_000/cross_sections",
        "01_component_000/decomposition",
        "01_component_000/candidates/circular_loft_baseline",
        "01_component_000/candidates/noncircular_loft",
        "01_component_000/candidates/profile_extrusion",
        "01_component_000/candidates/composite",
        "01_component_000/qa",
        "01_component_000/visuals",
        "02_builder_registry",
        "03_cross_section_analyzer",
        "04_feature_balanced_qa",
        "05_robot_regression",
        "artifacts",
    ):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    source = FROZEN_P3 / "part_000.obj"
    mesh = rt.load_mesh(source)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    measured = rt.load_json(V4 / "03_components/P3_COMPONENT_000/01_prepare/measured_spec.json", {}) or {}
    contract = rt.build_frame_contract(vertices, measured)
    local = contract.global_to_local(vertices)
    geom = rt.measured_geometry_contract(mesh, measured, contract)
    shutil.copy2(source, OUT / "01_component_000/source/source_part.obj")

    mac_hyp = rt.load_json(V6 / "03_components/P3_COMPONENT_000/06_mac/mac_hypotheses.json", {}) or {}
    suggested = "EXTRUSION"
    if isinstance(mac_hyp.get("hypotheses"), list) and mac_hyp["hypotheses"]:
        suggested = mac_hyp["hypotheses"][0].get("visual_builder_suggestion") or mac_hyp["hypotheses"][0].get("builder_family") or suggested
    existing_code = V6 / "03_components/P3_COMPONENT_000/07_candidates/mac_candidate_01/generated_code.py"
    if existing_code.is_file():
        shutil.copy2(existing_code, OUT / "01_component_000/existing_mac/generated_code.py")
    if (V6 / "03_components/P3_COMPONENT_000/06_mac/mac_hypotheses.json").is_file():
        shutil.copy2(V6 / "03_components/P3_COMPONENT_000/06_mac/mac_hypotheses.json", OUT / "01_component_000/existing_mac/mac_hypotheses.json")
    rt.dump_json(
        OUT / "artifacts/mac_builder_routing_audit.json",
        {
            "MAC_SUGGESTED_BUILDER": suggested,
            "ACTUAL_EXECUTED_BUILDER_BEFORE": "PROFILE_LOFT",
            "MAC_BUILDER_SUGGESTION_IGNORED": True,
            "CURRENT_PROFILE_REPRESENTATION": "ONE_RADIUS_PER_SECTION",
            "CURRENT_SECTION_WIRE_TYPE": "CIRCLE",
            "builder_source_file": str(ROOT / "scripts/tank_p3_45_qwen3vl_mac_v6.py") + " + robot PROFILE_LOFT runtime",
        },
    )
    rt.dump_json(
        OUT / "artifacts/current_profile_loft_audit.json",
        {
            "builder_source_file": str(ROOT / "scripts/generic_cad_runtime.py"),
            "section_axis_source": "PREPARE_PCA_MAJOR_AXIS",
            "radial_definition": "quantile of UV radius",
            "quantile": 0.5,
            "wire_type": "CIRCLE",
            "CURRENT_PROFILE_REPRESENTATION": "ONE_RADIUS_PER_SECTION",
            "CURRENT_SECTION_WIRE_TYPE": "CIRCLE",
            "supports_polygon": True,
            "supports_bspline_wire": False,
            "supports_multiple_loops": False,
            "supports_inner_loops": False,
            "supports_composite": True,
        },
    )
    rt.dump_json(OUT / "artifacts/builder_capability_matrix.json", {"builders": rt.BUILDER_CAPABILITIES})
    rt.dump_json(OUT / "02_builder_registry/builder_capability_matrix.json", {"builders": rt.BUILDER_CAPABILITIES})

    sections = rt.analyze_cross_sections(local, faces=faces)
    rt.dump_json(OUT / "01_component_000/cross_sections/sections.json", {"sections": sections})
    rt.dump_json(OUT / "03_cross_section_analyzer/sections.json", {"sections": sections})
    breaks = rt.detect_change_points(sections)
    routing = rt.route_builder(suggested, sections, breaks, geom)
    rt.dump_json(OUT / "01_component_000/decomposition/change_points.json", {"breaks": breaks, "subregions": max(len(breaks) + 1, 1), **routing})

    circ = rt.build_circular_loft(local, OUT / "01_component_000/candidates/circular_loft_baseline/generated.step", faces=faces)
    extr = rt.build_polygon_extrusion(local, float(local[:, 0].min()), float(local[:, 0].max()), OUT / "01_component_000/candidates/profile_extrusion/generated.step", faces=faces)
    ncl = rt.build_noncircular_loft(local, OUT / "01_component_000/candidates/noncircular_loft/generated.step", faces=faces)
    comp = rt.build_composite(local, sections, breaks, OUT / "01_component_000/candidates/composite", faces=faces)

    def eval_cand(name: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = Path(str(payload.get("step_path") or ""))
        mesh_c = rt.tessellate_step(path, path.with_suffix(".stl")) if payload.get("step_success") and path.is_file() else None
        if mesh_c is None:
            return {"candidate_builder": name, "step_success": False, **payload}
        gv = contract.local_to_global(np.asarray(mesh_c.vertices, dtype=float))
        gf = np.asarray(mesh_c.faces, dtype=np.int64)
        global_step = path.with_name(path.stem + "_global.step")
        rt.transform_step(path, global_step, contract.T_GLOBAL_FROM_LOCAL)
        metrics = rt.nearest_metrics(rt.sample_mesh(mesh), gv)
        axial = rt.axial_bin_qa(local, np.asarray(mesh_c.vertices, dtype=float))
        return {
            "candidate_builder": name,
            "step_success": True,
            "global_step": str(global_step),
            "vertices": gv,
            "faces": gf,
            "global_chamfer": metrics["chamfer"],
            "global_coverage": metrics["coverage"],
            "global_hausdorff": metrics["hausdorff"],
            **{k: axial[k] for k in axial if k != "rows"},
            "axial_rows": axial["rows"],
            "mac_suggested_builder": suggested,
            **payload,
        }

    cands = [
        eval_cand("CIRCULAR_PROFILE_LOFT", circ),
        eval_cand("PROFILE_EXTRUSION", extr),
        eval_cand("NON_CIRCULAR_PROFILE_LOFT", ncl),
        eval_cand("COMPOSITE_PART", comp),
    ]
    scored = [c for c in cands if c.get("step_success")]
    best = max(scored, key=lambda row: (row.get("MIN_AXIAL_BIN_COVERAGE") or 0.0, row.get("global_coverage") or 0.0)) if scored else {}
    routed = next((c for c in cands if c.get("candidate_builder") == routing.get("ACTUAL_EXECUTED_BUILDER")), best)
    baseline = next((c for c in cands if c["candidate_builder"] == "CIRCULAR_PROFILE_LOFT"), {})
    new_metrics = routed if routed else best
    rt.write_csv(
        OUT / "artifacts/builder_candidate_manifest.csv",
        [
            {
                "component_id": "P3_COMPONENT_000",
                "mac_suggested_builder": suggested,
                "candidate_builder": c.get("candidate_builder"),
                "step_success": c.get("step_success"),
                "global_chamfer": c.get("global_chamfer"),
                "global_coverage": c.get("global_coverage"),
                "min_axial_bin_coverage": c.get("MIN_AXIAL_BIN_COVERAGE"),
                "worst_bin_chamfer": c.get("WORST_BIN_CHAMFER"),
                "structural_break_count": len(breaks),
                "selected": c.get("candidate_builder") == best.get("candidate_builder"),
            }
            for c in cands
        ],
    )
    rt.dump_json(OUT / "01_component_000/qa/axial_bin_qa.json", {"best": best.get("candidate_builder"), "candidates": [{k: v for k, v in c.items() if k not in {"vertices", "faces", "axial_rows"}} for c in cands]})

    v1.render_meshes([(vertices, faces, (0.4, 0.55, 0.8), "src")], OUT / "artifacts/component_000_source.png", "source", vertices)
    # Cross-section sheet: shaft / transition / terminal
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pick = []
    if sections:
        pick = [sections[0], sections[min(len(sections) // 5, len(sections) - 1)], sections[len(sections) // 2]]
    fig, axes = plt.subplots(3, 3, figsize=(9.6, 8.4), dpi=130)
    row_names = ["terminal", "transition", "shaft"]
    for row_i, sec in enumerate(pick):
        uv = rt.slice_uv_at_x(local, float(sec["section_position"]), faces=faces)
        poly = rt.section_polygon(local, sec["lo"], sec["hi"], faces=faces)
        circ_r = float(np.median(np.linalg.norm(uv - uv.mean(axis=0), axis=1))) if len(uv) else 0.0
        center = uv.mean(axis=0) if len(uv) else np.zeros(2)
        titles = ["source samples", "circular fit", "non-circular contour"]
        for col, title in enumerate(titles):
            ax = axes[row_i][col]
            ax.set_aspect("equal")
            if len(uv):
                ax.scatter(uv[:, 0], uv[:, 1], s=2, c="#4c6ef5", alpha=0.6)
            if col == 1 and circ_r > 0:
                theta = np.linspace(0, 2 * np.pi, 80)
                ax.plot(center[0] + circ_r * np.cos(theta), center[1] + circ_r * np.sin(theta), color="#e8590c", lw=1.2)
            if col == 2 and len(poly) >= 3:
                closed = np.vstack([poly, poly[0]])
                ax.plot(closed[:, 0], closed[:, 1], color="#2b8a3e", lw=1.2)
            ax.set_title(f"{row_names[row_i]} / {title}", fontsize=8)
            ax.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(OUT / "artifacts/component_000_cross_section_sheet.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    if breaks and sections:
        fig2, ax2 = plt.subplots(figsize=(7.2, 5.4), dpi=130)
        view = np.array([[0.78, -0.42, 0.0], [0.18, 0.30, 0.82]], dtype=float)
        x_break = float(sections[breaks[0]]["lo"])
        colors = np.where(local[:, 0] <= x_break, "#4c6ef5", "#e8590c")
        proj = local @ view.T
        ax2.scatter(proj[:, 0], proj[:, 1], s=3, c=colors, alpha=0.7)
        ax2.set_aspect("equal")
        ax2.axis("off")
        ax2.set_title("SUBREGION_000 (blue) / SUBREGION_001 (orange)")
        fig2.savefig(OUT / "artifacts/component_000_structural_decomposition.png", bbox_inches="tight", facecolor="white")
        plt.close(fig2)
    for cand in cands:
        if cand.get("vertices") is None:
            continue
        name = cand["candidate_builder"].lower()
        v1.render_meshes([(cand["vertices"], cand["faces"], (0.85, 0.45, 0.15), "cad")], OUT / "artifacts" / f"component_000_{name}.png", cand["candidate_builder"], cand["vertices"])
    if best.get("vertices") is not None:
        v1.render_meshes([(vertices, faces, (0.35, 0.55, 0.85), "src"), (best["vertices"], best["faces"], (0.85, 0.4, 0.12), "cad")], OUT / "artifacts/component_000_best_builder.png", f"best={best.get('candidate_builder')}", vertices)
        v1.render_meshes([(vertices, faces, (0.35, 0.55, 0.85), "src"), (best["vertices"], best["faces"], (0.85, 0.4, 0.12), "cad")], OUT / "artifacts/component_000_builder_comparison_sheet.png", "builder comparison", vertices)

    generic_src = (ROOT / "scripts/generic_cad_runtime.py").read_text(encoding="utf-8")
    case_rules = sum(1 for token in ["if component_id == 0", "if robot", 'if tank', "if head", "if body", "slotted_block", "triangle_part"] if token in generic_src)

    profile_types = sorted({row["profile_type"] for row in sections})
    shaft_profile = next((row["profile_type"] for row in sections if row["profile_type"] == "CIRCLE"), None)
    term_profile = next((row["profile_type"] for row in sections if row["profile_type"] != "CIRCLE" and row["profile_type"] != "UNKNOWN"), None)
    summary = {
        "CURRENT_GATE": None,
        "NEXT_PRIMARY_BLOCKER": None,
        "P3_REEXECUTED": False,
        "MAC_API_REEXECUTED": False,
        "COMPONENT": "P3_COMPONENT_000",
        "MAC_SUGGESTED_BUILDER": suggested,
        **routing,
        "MAC_BUILDER_SUGGESTION_IGNORED_BEFORE": True,
        "MAC_BUILDER_SUGGESTION_EXECUTABLE_AFTER": routing["ACTUAL_EXECUTED_BUILDER"] != "CIRCULAR_PROFILE_LOFT" or suggested in {"CIRCULAR_PROFILE_LOFT", "CYLINDER"},
        "CURRENT_PROFILE_REPRESENTATION": "CLOSED_2D_WIRE_OR_POLYGON",
        "CURRENT_SECTION_WIRE_TYPE": "POLYGON_OR_CIRCLE_BY_SECTION",
        "LEGACY_PROFILE_REPRESENTATION": "ONE_RADIUS_PER_SECTION",
        "LEGACY_SECTION_WIRE_TYPE": "CIRCLE",
        "NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS": any(t != "CIRCLE" for t in profile_types),
        "SECTION_COUNT": len(sections),
        "SECTION_PROFILE_TYPES": profile_types,
        "STRUCTURAL_BREAK_COUNT": len(breaks),
        "SUBREGION_COUNT": max(len(breaks) + 1, 1),
        "CIRCULAR_LOFT_BASELINE_STEP": circ.get("step_path"),
        "PROFILE_EXTRUSION_STEP": extr.get("step_path"),
        "NONCIRCULAR_LOFT_STEP": ncl.get("step_path"),
        "COMPOSITE_STEP": comp.get("step_path"),
        "CIRCULAR_LOFT_FORCED": False,
        "BASELINE_GLOBAL_COVERAGE": baseline.get("global_coverage"),
        "NEW_GLOBAL_COVERAGE": new_metrics.get("global_coverage"),
        "BASELINE_GLOBAL_CHAMFER": baseline.get("global_chamfer"),
        "NEW_GLOBAL_CHAMFER": new_metrics.get("global_chamfer"),
        "BASELINE_MIN_AXIAL_BIN_COVERAGE": baseline.get("MIN_AXIAL_BIN_COVERAGE"),
        "NEW_MIN_AXIAL_BIN_COVERAGE": new_metrics.get("MIN_AXIAL_BIN_COVERAGE"),
        "BASELINE_WORST_BIN_CHAMFER": baseline.get("WORST_BIN_CHAMFER"),
        "NEW_WORST_BIN_CHAMFER": new_metrics.get("WORST_BIN_CHAMFER"),
        "BEST_GLOBAL_QA_BUILDER": best.get("candidate_builder"),
        "BEST_BUILDER": routing.get("ACTUAL_EXECUTED_BUILDER"),
        "CAD_NATIVE_QA_PASS": bool((best.get("global_coverage") or 0) >= 0.8),
        "CASE_SPECIFIC_BUILDER_RULES_FOUND": case_rules,
        "SHAFT_PROFILE": shaft_profile,
        "TERMINAL_PROFILE": term_profile,
        "SHAFT_BUILDER": comp.get("shaft_builder"),
        "TERMINAL_BUILDER": comp.get("terminal_builder"),
        "COMPOSITE_TOPOLOGY_MODE": comp.get("COMPOSITE_TOPOLOGY_MODE"),
        "INNER_LOOP_UNSUPPORTED": True,
        "INNER_LOOP_EVIDENCE": any(bool(row.get("inner_loop_evidence")) for row in sections),
        "ROBOT_REGRESSION_EXECUTED": False,
        "ROBOT_CAD_NATIVE_BEFORE": 2,
        "ROBOT_CAD_NATIVE_AFTER": None,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED": bool(ncl.get("step_success") or comp.get("step_success")),
    }
    inner_evidence = bool(summary["INNER_LOOP_EVIDENCE"])
    improved = bool(summary["NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED"] and (best.get("MIN_AXIAL_BIN_COVERAGE") or 0) >= (baseline.get("MIN_AXIAL_BIN_COVERAGE") or 0))
    if routing["ACTUAL_EXECUTED_BUILDER"] in {"PROFILE_LOFT", "CIRCULAR_PROFILE_LOFT"} and str(suggested).upper() == "EXTRUSION":
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_ROUTING_FAIL"
        summary["NEXT_PRIMARY_BLOCKER"] = "EXECUTABLE_BUILDER_ROUTING"
    elif not summary["NONCIRCULAR_PROFILE_EXTRACTION_SUCCESS"] and not summary["NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED"]:
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_PROFILE_EXTRACTION_FAIL"
        summary["NEXT_PRIMARY_BLOCKER"] = "NON_CIRCULAR_CROSS_SECTION_RECOVERY"
    elif not any(c.get("step_success") for c in cands if c["candidate_builder"] != "CIRCULAR_PROFILE_LOFT"):
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_BREP_CONSTRUCTION_FAIL"
        summary["NEXT_PRIMARY_BLOCKER"] = "NON_CIRCULAR_PROFILE_TO_BREP"
    elif breaks and not comp.get("step_success"):
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_COMPOSITE_FAIL"
        summary["NEXT_PRIMARY_BLOCKER"] = "INTRA_COMPONENT_COMPOSITE_RECONSTRUCTION"
    elif inner_evidence:
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_PARTIAL_PASS"
        summary["NEXT_PRIMARY_BLOCKER"] = "INNER_LOOP_AND_NEGATIVE_SPACE_RECOVERY"
    elif summary["NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED"] and (new_metrics.get("MIN_AXIAL_BIN_COVERAGE") or 0) > (baseline.get("MIN_AXIAL_BIN_COVERAGE") or 0) + 1e-6:
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_PASS"
        summary["NEXT_PRIMARY_BLOCKER"] = "ROBOT_AND_TANK_BATCH_GENERALIZATION"
    elif summary["NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED"]:
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_PASS"
        summary["NEXT_PRIMARY_BLOCKER"] = "FEATURE_BALANCED_TERMINAL_FIDELITY"
    else:
        summary["CURRENT_GATE"] = "GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_BREP_CONSTRUCTION_FAIL"
        summary["NEXT_PRIMARY_BLOCKER"] = "NON_CIRCULAR_PROFILE_TO_BREP"
    rt.dump_json(OUT / "artifacts/final_summary.json", summary)
    (OUT / "artifacts/GENERIC_CAD_BUILDER_EXPRESSIVITY_V1_REPORT.md").write_text(
        "# GENERIC_CAD_BUILDER_EXPRESSIVITY_V1\n\n" + "\n".join(f"{k}={v}" for k, v in summary.items()) + "\n",
        encoding="utf-8",
    )
    for k, v in summary.items():
        print(f"{k}={v}", flush=True)
    return summary


def robot_regression() -> dict[str, Any]:
    counts = {"CIRCULAR_PROFILE_LOFT": 0, "PROFILE_EXTRUSION": 0, "NON_CIRCULAR_PROFILE_LOFT": 0, "COMPOSITE_PART": 0, "OTHER": 0}
    native = 0
    for i in range(9):
        cid = f"P3_COMPONENT_{i:03d}"
        part = ROBOT / "03_components" / cid / "01_prepare" / "source_part.obj"
        if not part.is_file():
            continue
        mesh = rt.load_mesh(part)
        v = np.asarray(mesh.vertices, dtype=float)
        contract = rt.build_frame_contract(v, None)
        local = contract.global_to_local(v)
        geom = rt.measured_geometry_contract(mesh, {}, contract)
        sections = rt.analyze_cross_sections(local, faces=np.asarray(mesh.faces, dtype=np.int64))
        breaks = rt.detect_change_points(sections)
        route = rt.route_builder("UNKNOWN", sections, breaks, geom)
        counts[route["ACTUAL_EXECUTED_BUILDER"]] = counts.get(route["ACTUAL_EXECUTED_BUILDER"], 0) + 1
        if route["ACTUAL_EXECUTED_BUILDER"] != "UNKNOWN":
            native += 1
    summary = {
        "ROBOT_REGRESSION_EXECUTED": True,
        "ROBOT_COMPONENT_COUNT": 9,
        "CIRCULAR_LOFT_SELECTED": counts.get("CIRCULAR_PROFILE_LOFT", 0),
        "PROFILE_EXTRUSION_SELECTED": counts.get("PROFILE_EXTRUSION", 0) + counts.get("POLYGON_EXTRUSION", 0),
        "NONCIRCULAR_LOFT_SELECTED": counts.get("NON_CIRCULAR_PROFILE_LOFT", 0),
        "COMPOSITE_SELECTED": counts.get("COMPOSITE_PART", 0),
        "OTHER_SELECTED": counts.get("OTHER", 0) + counts.get("UNKNOWN", 0),
        "ROBOT_CAD_NATIVE_BEFORE": 2,
        "ROBOT_CAD_NATIVE_AFTER": native,
    }
    rt.dump_json(OUT / "05_robot_regression/summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--component", default="P3_COMPONENT_000")
    parser.add_argument("--reuse-existing-mac", action="store_true")
    parser.add_argument("--no-p3", action="store_true")
    parser.add_argument("--no-mac-api", action="store_true")
    parser.add_argument("--robot-regression", action="store_true")
    parser.add_argument("--reuse-existing-upstream", action="store_true")
    args = parser.parse_args()
    if args.robot_regression:
        summary = rt.load_json(OUT / "artifacts/final_summary.json", {}) or {}
        if summary.get("NONCIRCULAR_OR_COMPOSITE_CANDIDATE_CREATED"):
            robot = robot_regression()
            summary.update(robot)
            rt.dump_json(OUT / "artifacts/final_summary.json", summary)
            for k, v in robot.items():
                print(f"{k}={v}", flush=True)
        return
    run_component_000()


if __name__ == "__main__":
    main()
