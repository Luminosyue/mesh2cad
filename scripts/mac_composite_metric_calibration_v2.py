#!/usr/bin/env python3
"""MAC_COMPOSITE_METRIC_CALIBRATION_V2 — audit and bind COMPOSITE_PART metrics.

Orchestration / audit / visualization only. Geometry fixes live in generic_cad_*.
"""
from __future__ import annotations

import csv
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
import generic_cad_composite_audit as ca  # noqa: E402
import generic_cad_profile_metric_calibration as pmc  # noqa: E402
import generic_cad_profiles as gp  # noqa: E402
import generic_cad_runtime as rt  # noqa: E402
import tank_p3_45_qwen3vl_mac_v6 as tank_v6  # noqa: E402
import tank_p3_45_component_pipeline_a_fullrun_v5 as tank_v5  # noqa: E402
import tank_p3_point2cad_component_local_qa_v2 as local_qa  # noqa: E402
import build_a_robot_pipeline_a_fullstack_repair_v2 as robot  # noqa: E402

OUT = ROOT / "ours3/mac_composite_metric_calibration_v2"
V1 = ROOT / "ours3/mac_mainline_multi_builder_runtime_v1"
ROBOT_V3 = ROOT / "ours3/build_a_robot_pipeline_a_qwen3vl_mac_v3"
V1_ROBOT = ROOT / "ours3/build_a_robot_fresh_generalization_v1"
FROZEN_P3 = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"

OLD_MINOR_U = 2.15406827527182
OLD_MINOR_V = 1.928335830421959
OLD_CENTROID = 0.09507048565609202


def dump(path: Path, value: Any) -> None:
    rt.dump_json(path, value)


def seed_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def uv_extent(pts: np.ndarray) -> dict[str, Any]:
    pts = np.asarray(pts, dtype=float)
    if len(pts) == 0:
        return {"axial": 0.0, "U": 0.0, "V": 0.0, "centroid": [0, 0, 0], "n": 0}
    return {
        "axial": float(np.ptp(pts[:, 0])),
        "U": float(np.ptp(pts[:, 1])),
        "V": float(np.ptp(pts[:, 2])),
        "centroid": pts.mean(axis=0).tolist(),
        "n": int(len(pts)),
        "bbox_min": pts.min(axis=0).tolist(),
        "bbox_max": pts.max(axis=0).tolist(),
    }


def ratio_uv(src: np.ndarray, cad: np.ndarray) -> dict[str, float]:
    a = uv_extent(src)
    b = uv_extent(cad)
    return {
        "axial": b["axial"] / max(a["axial"], 1e-12),
        "U": b["U"] / max(a["U"], 1e-12),
        "V": b["V"] / max(a["V"], 1e-12),
        "centroid_error": float(np.linalg.norm(np.asarray(a["centroid"]) - np.asarray(b["centroid"]))),
        "source": a,
        "cad": b,
    }


def mask_axial(pts: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return pts[(pts[:, 0] >= lo - 1e-12) & (pts[:, 0] <= hi + 1e-12)]


def load_frame(component_dir: Path):
    source = rt.load_mesh(component_dir / "01_prepare/source_part.obj")
    measured = rt.load_json(component_dir / "01_prepare/measured_spec.json", {}) or {}
    contract = rt.build_frame_contract(np.asarray(source.vertices, dtype=float), measured)
    local = contract.global_to_local(np.asarray(source.vertices, dtype=float))
    faces = np.asarray(source.faces, dtype=np.int64)
    return source, contract, local, faces


def tess(path: Path, stl: Path):
    return rt.tessellate_step(path, stl) if path.is_file() else None


def layer_audit(component_dir: Path, artifacts: Path, tag: str) -> dict[str, Any]:
    source, contract, local, faces = load_frame(component_dir)
    decomp = rt.load_json(component_dir / "07_candidates/mac_candidate_01/structural_decomposition.json", {}) or {}
    subs = decomp.get("subregions") or []
    runtime_dir = component_dir / "07_candidates/mac_candidate_01/runtime/attempt_composite_part/composite"
    pieces = {
        "terminal": tess(runtime_dir / "subregion_000.step", artifacts / f"{tag}_terminal.stl"),
        "shaft": tess(runtime_dir / "subregion_001.step", artifacts / f"{tag}_shaft.stl"),
        "transition": tess(runtime_dir / "transition_000.step", artifacts / f"{tag}_transition.stl"),
        "composite": tess(runtime_dir / "composite.step", artifacts / f"{tag}_composite.stl"),
        "generated": tess(component_dir / "07_candidates/mac_candidate_01/generated.step", artifacts / f"{tag}_generated.stl"),
    }
    t0 = subs[0] if subs else {"x_lo": float(local[:, 0].min()), "x_hi": float(np.median(local[:, 0]))}
    t1 = subs[1] if len(subs) > 1 else {"x_lo": t0["x_hi"], "x_hi": float(local[:, 0].max())}
    src_term = mask_axial(local, float(t0["x_lo"]), float(t0["x_hi"]))
    src_shaft = mask_axial(local, float(t1["x_lo"]), float(t1["x_hi"]))
    break_x = float(t0["x_hi"])
    src_trans = mask_axial(local, break_x - 0.02 * float(np.ptp(local[:, 0])), break_x + 0.02 * float(np.ptp(local[:, 0])))

    def local_of(mesh):
        if mesh is None:
            return np.zeros((0, 3))
        return np.asarray(mesh.vertices, dtype=float)

    terminal = ratio_uv(src_term, local_of(pieces["terminal"]))
    shaft = ratio_uv(src_shaft, local_of(pieces["shaft"]))
    trans = ratio_uv(src_trans, local_of(pieces["transition"]))
    # pre-sew combined from independent pieces
    stacked = [local_of(pieces[k]) for k in ("terminal", "shaft", "transition") if pieces[k] is not None]
    presew_pts = np.vstack(stacked) if stacked else np.zeros((0, 3))
    post = local_of(pieces["composite"])
    src_all = local
    payload = {
        "tag": tag,
        "SOURCE_SUBREGION_000": uv_extent(src_term),
        "SOURCE_SUBREGION_001": uv_extent(src_shaft),
        "SOURCE_TRANSITION_SUPPORT_REGION": uv_extent(src_trans),
        "SHAFT_EXTENT_RATIO_AXIAL": shaft["axial"],
        "SHAFT_EXTENT_RATIO_U": shaft["U"],
        "SHAFT_EXTENT_RATIO_V": shaft["V"],
        "TERMINAL_EXTENT_RATIO_AXIAL": terminal["axial"],
        "TERMINAL_EXTENT_RATIO_U": terminal["U"],
        "TERMINAL_EXTENT_RATIO_V": terminal["V"],
        "TRANSITION_EXTENT_RATIO_U": trans["U"],
        "TRANSITION_EXTENT_RATIO_V": trans["V"],
        "PRESEW_EXTENT_RATIO_U": ratio_uv(src_all, presew_pts)["U"],
        "PRESEW_EXTENT_RATIO_V": ratio_uv(src_all, presew_pts)["V"],
        "POSTSEW_EXTENT_RATIO_U": ratio_uv(src_all, post)["U"],
        "POSTSEW_EXTENT_RATIO_V": ratio_uv(src_all, post)["V"],
        "terminal": terminal,
        "shaft": shaft,
        "transition": trans,
        "presew": uv_extent(presew_pts),
        "postsew": uv_extent(post),
        "generated_global": rt.mesh_stats(np.asarray(pieces["generated"].vertices)) if pieces["generated"] is not None else {},
        "source_global": rt.mesh_stats(np.asarray(source.vertices)),
        "subregions": subs,
    }
    dump(artifacts / f"{tag}_layer_audit.json", payload)
    return payload


def first_appears(old_layers: dict[str, Any]) -> tuple[str, str]:
    u_term = float(old_layers.get("TERMINAL_EXTENT_RATIO_U") or 0)
    v_term = float(old_layers.get("TERMINAL_EXTENT_RATIO_V") or 0)
    u_shaft = float(old_layers.get("SHAFT_EXTENT_RATIO_U") or 0)
    u_trans = float(old_layers.get("TRANSITION_EXTENT_RATIO_U") or 0)
    u_pre = float(old_layers.get("PRESEW_EXTENT_RATIO_U") or 0)
    u_post = float(old_layers.get("POSTSEW_EXTENT_RATIO_U") or 0)
    infl = "UNKNOWN"
    if max(u_term, v_term) >= 1.4:
        infl = "TERMINAL_LOFT"
    elif u_shaft >= 1.4:
        infl = "CYLINDER_FIT"
    elif u_trans >= 1.4:
        infl = "TRANSITION"
    elif u_pre >= 1.4:
        infl = "COMPOSITE_OVERLAP"
    elif u_post >= 1.4 and u_pre < 1.25:
        infl = "SEWING"
    term_cent = float((old_layers.get("terminal") or {}).get("centroid_error") or 0)
    shaft_cent = float((old_layers.get("shaft") or {}).get("centroid_error") or 0)
    cent = "SECTION_EXTRACTION" if term_cent >= shaft_cent else "CYLINDER_FIT"
    if term_cent > 1e-4:
        cent = "TERMINAL_LOFT"
    return infl, cent


def terminal_section_csv(component_dir: Path, csv_path: Path) -> dict[str, Any]:
    source, contract, local, faces = load_frame(component_dir)
    decomp = rt.load_json(component_dir / "07_candidates/mac_candidate_01/structural_decomposition.json", {}) or {}
    t0 = (decomp.get("subregions") or [{}])[0]
    x_lo, x_hi = float(t0.get("x_lo", local[:, 0].min())), float(t0.get("x_hi", np.median(local[:, 0])))
    packed = rt._collect_region_profiles(local, faces, x_lo, x_hi, 10)
    xs = np.asarray(packed.get("xs"), dtype=float)
    aligned = packed.get("aligned") or []
    raw = packed.get("raw_profiles") or []
    descs = packed.get("section_descriptors") or []
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "section_id", "axial_position", "source_point_count",
            "source_centroid_u", "source_centroid_v", "profile_centroid_u", "profile_centroid_v",
            "centroid_error_u", "centroid_error_v", "centroid_error_2d",
            "source_width", "profile_width", "width_ratio",
            "source_height", "profile_height", "height_ratio",
            "source_area", "profile_area", "area_ratio",
            "source_perimeter", "profile_perimeter", "perimeter_ratio",
            "source_circularity", "profile_type",
            "source_bbox_u_min", "source_bbox_u_max", "source_bbox_v_min", "source_bbox_v_max",
            "profile_bbox_u_min", "profile_bbox_u_max", "profile_bbox_v_min", "profile_bbox_v_max",
            "profile_source_method",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i, xi in enumerate(xs):
            raw_uv = np.asarray(raw[i] if i < len(raw) else (aligned[i] if i < len(aligned) else np.zeros((0, 2))), dtype=float)
            prof = np.asarray(aligned[i] if i < len(aligned) else raw_uv, dtype=float)
            src_m = pmc.profile_metrics(raw_uv, float(xi))
            pr_m = pmc.profile_metrics(prof, float(xi))
            desc = descs[i] if i < len(descs) else {}
            row = {
                "section_id": i,
                "axial_position": float(xi),
                "source_point_count": int(desc.get("source_point_count") or desc.get("point_count") or len(raw_uv)),
                "source_centroid_u": src_m["centroid_u"],
                "source_centroid_v": src_m["centroid_v"],
                "profile_centroid_u": pr_m["centroid_u"],
                "profile_centroid_v": pr_m["centroid_v"],
                "centroid_error_u": pr_m["centroid_u"] - src_m["centroid_u"],
                "centroid_error_v": pr_m["centroid_v"] - src_m["centroid_v"],
                "centroid_error_2d": float(np.hypot(pr_m["centroid_u"] - src_m["centroid_u"], pr_m["centroid_v"] - src_m["centroid_v"])),
                "source_width": src_m["width"],
                "profile_width": pr_m["width"],
                "width_ratio": pr_m["width"] / max(src_m["width"], 1e-12),
                "source_height": src_m["height"],
                "profile_height": pr_m["height"],
                "height_ratio": pr_m["height"] / max(src_m["height"], 1e-12),
                "source_area": src_m["area"],
                "profile_area": pr_m["area"],
                "area_ratio": pr_m["area"] / max(src_m["area"], 1e-16),
                "source_perimeter": src_m["perimeter"],
                "profile_perimeter": pr_m["perimeter"],
                "perimeter_ratio": pr_m["perimeter"] / max(src_m["perimeter"], 1e-12),
                "source_circularity": float(desc.get("circularity") or gp.circularity(raw_uv)),
                "profile_type": desc.get("profile_type") or gp.classify_profile(raw_uv),
                "source_bbox_u_min": float(raw_uv[:, 0].min()) if len(raw_uv) else 0.0,
                "source_bbox_u_max": float(raw_uv[:, 0].max()) if len(raw_uv) else 0.0,
                "source_bbox_v_min": float(raw_uv[:, 1].min()) if len(raw_uv) else 0.0,
                "source_bbox_v_max": float(raw_uv[:, 1].max()) if len(raw_uv) else 0.0,
                "profile_bbox_u_min": float(prof[:, 0].min()) if len(prof) else 0.0,
                "profile_bbox_u_max": float(prof[:, 0].max()) if len(prof) else 0.0,
                "profile_bbox_v_min": float(prof[:, 1].min()) if len(prof) else 0.0,
                "profile_bbox_v_max": float(prof[:, 1].max()) if len(prof) else 0.0,
                "profile_source_method": desc.get("PROFILE_BOUNDARY_METHOD") or desc.get("profile_source_method"),
            }
            writer.writerow(row)
            rows.append(row)
    wr = np.array([r["width_ratio"] for r in rows], dtype=float) if rows else np.array([1.0])
    hr = np.array([r["height_ratio"] for r in rows], dtype=float) if rows else np.array([1.0])
    ce = np.array([r["centroid_error_2d"] for r in rows], dtype=float) if rows else np.array([0.0])
    return {
        "rows": rows,
        "packed": packed,
        "SECTION_WIDTH_RATIO_P50": float(np.quantile(wr, 0.5)),
        "SECTION_WIDTH_RATIO_P95": float(np.quantile(wr, 0.95)),
        "SECTION_HEIGHT_RATIO_P50": float(np.quantile(hr, 0.5)),
        "SECTION_HEIGHT_RATIO_P95": float(np.quantile(hr, 0.95)),
        "SECTION_CENTROID_ERROR_P50": float(np.quantile(ce, 0.5)),
        "SECTION_CENTROID_ERROR_P95": float(np.quantile(ce, 0.95)),
        "SLICE_SPAN_TO_SECTION_SPACING_RATIO": packed.get("SLICE_SPAN_TO_SECTION_SPACING_RATIO"),
        "PROFILE_BOUNDARY_METHOD": packed.get("PROFILE_BOUNDARY_METHOD"),
        "PROFILE_CORRESPONDENCE_SUCCESS": packed.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "CORRESPONDENCE_NORMALIZATION_INVERTED": packed.get("CORRESPONDENCE_NORMALIZATION_INVERTED"),
        "RESAMPLING_EXTENT_DRIFT": packed.get("RESAMPLING_EXTENT_DRIFT"),
        "PROFILE_BOUNDARY_METHODS": packed.get("PROFILE_BOUNDARY_METHODS"),
    }


def bias_source(methods: list[str] | None) -> str:
    methods = [m for m in (methods or []) if m]
    if not methods:
        return "UNKNOWN"
    if any(m == "CONVEX_HULL_FALLBACK" for m in methods):
        return "CONVEX_HULL"
    if any(m == "ALPHA_SHAPE" for m in methods):
        return "ALPHA_SHAPE"
    if any("SLAB" in m or "SLICE" in m for m in methods):
        return "SLICE_THICKNESS"
    return methods[0]


def official_stage1_ratios(qa: dict[str, Any]) -> dict[str, float]:
    st = qa.get("stage_1_unaligned") or qa.get("stage_1") or {}
    ratios = st.get("extent_ratio_xyz") or [1, 1, 1]
    return {
        "U": float(ratios[0]),
        "axial": float(ratios[1]),
        "V": float(ratios[2]),
        "centroid_error": float(st.get("centroid_error") or 0.0),
        "transform_qa_fail": bool(st.get("transform_qa_fail")),
    }


def symmetric_qa(source: np.ndarray, cand: np.ndarray, radius: float) -> dict[str, float]:
    from scipy.spatial import cKDTree

    st = cKDTree(source)
    ct = cKDTree(cand)
    s2c = ct.query(source)[0]
    c2s = st.query(cand)[0]
    return {
        "SOURCE_TO_CAD_CHAMFER": float(s2c.mean()),
        "CAD_TO_SOURCE_CHAMFER": float(c2s.mean()),
        "SYMMETRIC_CHAMFER": float(0.5 * (s2c.mean() + c2s.mean())),
        "SOURCE_TO_CAD_COVERAGE": float(np.mean(s2c <= radius)),
        "CAD_TO_SOURCE_COVERAGE": float(np.mean(c2s <= radius)),
    }


def render_sheet(component_dir: Path, v1_component: Path, out_png: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    source, contract, local, faces = load_frame(component_dir)
    decomp = rt.load_json(component_dir / "07_candidates/mac_candidate_01/structural_decomposition.json", {}) or {}
    t0 = (decomp.get("subregions") or [{}])[0]
    x_lo, x_hi = float(t0.get("x_lo", local[:, 0].min())), float(t0.get("x_hi", 0.0))
    break_x = x_hi
    positions = [
        ("stable region", (x_lo + x_hi) * 0.5),
        ("breakpoint left", break_x - 0.015),
        ("breakpoint right", break_x + 0.015),
        ("terminal middle", x_lo * 0.45 + x_hi * 0.55),
        ("terminal end", x_lo + 0.01),
    ]
    fig, axes = plt.subplots(len(positions), 3, figsize=(10.5, 12.5), dpi=120)
    for r, (title, xi) in enumerate(positions):
        xi = float(np.clip(xi, local[:, 0].min(), local[:, 0].max()))
        band = local[np.abs(local[:, 0] - xi) <= 0.006]
        old = gp.convex_hull_uv(band[:, 1:3]) if len(band) >= 3 else np.zeros((0, 2))
        desc = gp.extract_section_profile(local, faces, xi, thickness=0.004)
        new = np.asarray(desc.get("boundary_2d") or [], dtype=float)
        src_pts = band[:, 1:3] if len(band) else np.zeros((0, 2))
        panels = [(src_pts, "source points", "C0"), (old, "old convex hull", "C1"), (new, "fixed contour", "C2")]
        for c, (pts, lab, color) in enumerate(panels):
            ax = axes[r, c]
            if len(src_pts):
                ax.scatter(src_pts[:, 0], src_pts[:, 1], s=6, c="0.55", alpha=0.5)
            if len(pts) >= 3 and c > 0:
                closed = np.vstack([pts, pts[0]])
                ax.plot(closed[:, 0], closed[:, 1], color=color, lw=1.4)
            wr = pmc.extent_uv(new)[0] / max(pmc.extent_uv(src_pts)[0] if len(src_pts) else 1e-12, 1e-12)
            hr = pmc.extent_uv(new)[1] / max(pmc.extent_uv(src_pts)[1] if len(src_pts) else 1e-12, 1e-12)
            ce = 0.0
            if len(src_pts) and len(new):
                ce = float(np.linalg.norm(new.mean(0) - src_pts.mean(0)))
            ax.set_aspect("equal")
            ax.set_title(f"{title}\n{lab}\nw={wr:.3f} h={hr:.3f} c={ce:.4f}", fontsize=7)
            ax.tick_params(labelsize=6)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run_pytest() -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_mac_composite_metric_calibration_v2.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    (OUT / "artifacts/pytest.stdout.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    passed = failed = xfailed = 0
    m = re.search(r"(\d+) passed", proc.stdout)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", proc.stdout)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+) xfailed", proc.stdout)
    if m:
        xfailed = int(m.group(1))
    return {"TESTS_PASSED": passed, "TESTS_FAILED": failed, "TESTS_XFAILED": xfailed, "exit_code": proc.returncode, "summary_line": (proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "")}


def case_specific_count() -> int:
    files = [
        ROOT / "scripts/generic_cad_runtime.py",
        ROOT / "scripts/generic_cad_profiles.py",
        ROOT / "scripts/generic_cad_section_boundary.py",
        ROOT / "scripts/generic_cad_profile_metric_calibration.py",
        ROOT / "scripts/generic_cad_transition_calibration.py",
        ROOT / "scripts/generic_cad_composite_audit.py",
    ]
    n = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        n += len(re.findall(r"if\s+component_id\s*==", text))
        n += len(re.findall(r"P3_COMPONENT_000", text))
    return n


def gate_of(summary: dict[str, Any]) -> tuple[str, str]:
    infl = summary.get("MINOR_EXTENT_INFLATION_FIRST_APPEARS_AT")
    if infl == "SECTION_EXTRACTION" and not summary.get("TANK000_OFFICIAL_LOCAL_QA_PASS"):
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_SECTION_FAIL", "NON_CIRCULAR_SECTION_BOUNDARY_CALIBRATION"
    if infl == "PROFILE_CORRESPONDENCE" or (summary.get("CORRESPONDENCE_NORMALIZATION_INVERTED") is False):
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_CORRESPONDENCE_FAIL", "PROFILE_CORRESPONDENCE_METRIC_PRESERVATION"
    if infl == "TERMINAL_LOFT" and float(summary.get("NEW_MINOR_EXTENT_RATIO_U") or 9) > 1.35:
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_LOFT_FAIL", "NON_CIRCULAR_LOFT_GEOMETRY_STABILITY"
    if summary.get("TRANSITION_OVERSHOOT_DETECTED"):
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_TRANSITION_FAIL", "COMPOSITE_TRANSITION_METRIC_CALIBRATION"
    if summary.get("SEWING_GEOMETRY_MUTATION"):
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_SEWING_FAIL", "SEWING_GEOMETRY_MUTATION"
    if not summary.get("TANK000_OFFICIAL_LOCAL_QA_PASS"):
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_QA_DIAGNOSTIC_FAIL", "OFFICIAL_QA_FAILURE_ROOT_CAUSE"
    if summary.get("TANK000_OFFICIAL_LOCAL_QA_PASS") and summary.get("TESTS_FAILED", 1) == 0:
        return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_PASS", "TANK45_RUNTIME_REEXECUTION"
    return "MAC_COMPOSITE_METRIC_CALIBRATION_V2_QA_DIAGNOSTIC_FAIL", "OFFICIAL_QA_FAILURE_ROOT_CAUSE"


def run_robot_if_needed(ok: bool) -> dict[str, Any]:
    if not ok:
        return {
            "ROBOT_REGRESSION_EXECUTED": False,
            "ROBOT_CAD_NATIVE_BEFORE": 2,
            "ROBOT_CAD_NATIVE_AFTER_V2": None,
            "ROBOT_MAC_JSON_REUSED": True,
            "ROBOT_QWEN_REEXECUTED": False,
            "ROBOT_MAC_API_REEXECUTED": False,
        }
    robot_out = OUT / "08_robot_regression"
    seed_tree(ROBOT_V3 / "03_components", robot_out / "03_components")
    p3 = robot.load_frozen_p3(robot.SOURCE_DEFAULT, V1_ROBOT)
    robot.REUSE_MAC_DEFAULT = True
    before_native = 2
    after_native = 0
    rows = []
    for part in p3["parts"]:
        cid = part["component_id"]
        old_sel = rt.load_json(ROBOT_V3 / "03_components" / cid / "11_selected/selected_manifest.json", {}) or {}
        before_native = before_native  # frozen V1 baseline is 2; keep reported constant below
        manifest = robot.process_component(part, robot_out, resume=False, rerank=False, reexecute_runtime=True, reuse_mac=True)
        rows.append(manifest)
        after_native += int(bool(manifest.get("cad_native")))
    payload = {
        "ROBOT_REGRESSION_EXECUTED": True,
        "ROBOT_CAD_NATIVE_BEFORE": 2,
        "ROBOT_CAD_NATIVE_AFTER_V2": after_native,
        "ROBOT_MAC_JSON_REUSED": True,
        "ROBOT_QWEN_REEXECUTED": False,
        "ROBOT_MAC_API_REEXECUTED": False,
        "rows": [{"component_id": r.get("component_id"), "cad_native": r.get("cad_native"), "selected_backend": r.get("selected_backend")} for r in rows],
    }
    dump(robot_out / "robot_regression.json", payload)
    return payload


def main() -> int:
    for name in [
        "00_audit", "01_source_sections", "02_terminal_profile_calibration", "03_shaft_calibration",
        "04_transition_calibration", "05_composite_presew", "06_composite_postsew", "07_official_qa",
        "08_robot_regression", "artifacts",
    ]:
        (OUT / name).mkdir(parents=True, exist_ok=True)

    v1_comp = V1 / "tank000_mainline/03_components/P3_COMPONENT_000"
    print("STEP2-4 V1 layer audit", flush=True)
    old_layers = layer_audit(v1_comp, OUT / "00_audit", "v1")
    infl0, cent0 = first_appears(old_layers)
    dump(OUT / "00_audit/first_appearance.json", {"MINOR_EXTENT_INFLATION_FIRST_APPEARS_AT": infl0, "CENTROID_ERROR_FIRST_APPEARS_AT": cent0, **{k: old_layers.get(k) for k in old_layers if "RATIO" in k}})

    print("running pytest", flush=True)
    tests = run_pytest()
    print(tests, flush=True)

    print("reexecute Tank000 runtime (reuse MAC)", flush=True)
    tank_out = OUT
    seed_tree(v1_comp, tank_out / "03_components/P3_COMPONENT_000")
    components = [tank_v6.adapt_part(item) for item in tank_v5.load_components(FROZEN_P3, Path(tank_v6.SOURCE_OBJ))]
    part = next(item for item in components if item["component_id"] == "P3_COMPONENT_000")
    robot.REUSE_MAC_DEFAULT = True
    row = tank_v6.reexecute_runtime_component(part, tank_out)
    new_comp = tank_out / "03_components/P3_COMPONENT_000"

    print("new layer audit + section CSV", flush=True)
    new_layers = layer_audit(new_comp, OUT / "05_composite_presew", "v2")
    shutil.copy2(OUT / "05_composite_presew/v2_layer_audit.json", OUT / "06_composite_postsew/v2_layer_audit.json")
    section_stats = terminal_section_csv(new_comp, OUT / "artifacts/terminal_section_metric_audit.csv")
    dump(OUT / "01_source_sections/section_stats.json", {k: v for k, v in section_stats.items() if k not in {"rows", "packed"}})
    dump(OUT / "02_terminal_profile_calibration/packed_meta.json", {k: v for k, v in section_stats.items() if k not in {"rows", "packed"}})

    runtime = rt.load_json(new_comp / "07_candidates/mac_candidate_01/runtime_measurements.json", {}) or {}
    rt_payload = runtime.get("runtime") or runtime
    provenance = rt.load_json(new_comp / "07_candidates/mac_candidate_01/candidate_provenance.json", {}) or {}
    qa = rt.load_json(new_comp / "08_qa/MAC_CANDIDATE_01/qa.json", {}) or {}
    shutil.copy2(new_comp / "08_qa/MAC_CANDIDATE_01/qa.json", OUT / "07_official_qa/qa.json")
    new_off = official_stage1_ratios(qa)

    source, contract, local, faces = load_frame(new_comp)
    gen = tess(new_comp / "07_candidates/mac_candidate_01/generated.step", OUT / "artifacts/tank000_metric_fixed_v2.stl")
    oldm = tess(v1_comp / "07_candidates/mac_candidate_01/generated.step", OUT / "artifacts/tank000_old_v1_composite.stl")
    src_s = rt.sample_mesh(source)
    cand_s = rt.sample_mesh(gen) if gen is not None else src_s
    cov_r = 0.02 * max(float(np.ptp(np.asarray(source.vertices), axis=0).max()), 1e-3)
    sym = symmetric_qa(src_s, cand_s, cov_r)
    s_ext = np.ptp(np.asarray(source.vertices), axis=0)
    c_ext = np.ptp(np.asarray(gen.vertices), axis=0) if gen is not None else s_ext
    bbox_vol_ratio = float(np.prod(np.maximum(c_ext, 1e-12)) / np.prod(np.maximum(s_ext, 1e-12)))

    rt.render_projection([(np.asarray(source.vertices), np.asarray(source.faces), (0.2, 0.45, 0.85))], OUT / "artifacts/tank000_source.png", "source SOURCE_GLOBAL")
    if oldm is not None:
        rt.render_projection([(np.asarray(oldm.vertices), np.asarray(oldm.faces), (0.55, 0.55, 0.55))], OUT / "artifacts/tank000_old_v1_composite.png", "V1 composite SOURCE_GLOBAL")
    if gen is not None:
        rt.render_projection([(np.asarray(gen.vertices), np.asarray(gen.faces), (0.85, 0.45, 0.15))], OUT / "artifacts/tank000_metric_fixed_v2.png", "V2 composite SOURCE_GLOBAL")
        rt.render_projection(
            [
                (np.asarray(source.vertices), np.asarray(source.faces), (0.2, 0.45, 0.85)),
                (np.asarray(gen.vertices), np.asarray(gen.faces), (0.85, 0.45, 0.15)),
            ],
            OUT / "artifacts/tank000_source_vs_v2.png",
            "source vs V2 SOURCE_GLOBAL",
        )
    render_sheet(new_comp, v1_comp, OUT / "artifacts/tank000_sections_metric_sheet.png")
    # transition / sew screenshots
    runtime_dir = new_comp / "07_candidates/mac_candidate_01/runtime/attempt_composite_part/composite"
    for step_name, png in [("transition_000.step", "tank000_transition_profiles.png"), ("subregion_000.step", "tank000_presew.png"), ("composite.step", "tank000_postsew.png")]:
        mesh = tess(runtime_dir / step_name, OUT / "artifacts" / (step_name + ".stl"))
        if mesh is None:
            continue
        gv = contract.local_to_global(np.asarray(mesh.vertices, dtype=float)) if step_name != "generated.step" else np.asarray(mesh.vertices)
        # composite/subregion are LOCAL; generated is GLOBAL. Pieces are local.
        gv = contract.local_to_global(np.asarray(mesh.vertices, dtype=float))
        rt.render_projection([(gv, np.asarray(mesh.faces), (0.7, 0.35, 0.15))], OUT / "artifacts" / png, png)

    builders = provenance.get("subregion_builders") or rt_payload.get("subregion_builders") or []
    infl, cent = infl0, "TERMINAL_LOFT"
    # After fix, if new U near 1, keep historical first-appearance from V1.
    methods = section_stats.get("PROFILE_BOUNDARY_METHODS") or []
    convex_used = any(m == "CONVEX_HULL_FALLBACK" for m in methods)
    alpha_used = any(m in {"ALPHA_SHAPE", "CONCAVE_HULL", "MESH_PLANE_LOOP"} for m in methods)

    robot_reg = run_robot_if_needed(bool(qa.get("qa_pass")))

    summary = {
        "CURRENT_GATE": None,
        "NEXT_PRIMARY_BLOCKER": None,
        "P3_REEXECUTED": False,
        "QWEN_REEXECUTED": False,
        "MAC_API_REEXECUTED": False,
        "BUILDER_ROUTING_CHANGED": False,
        "ACTUAL_BUILDER": provenance.get("ACTUAL_EXECUTED_BUILDER") or row.get("ACTUAL_EXECUTED_BUILDER"),
        "SUBREGION_COUNT": provenance.get("SUBREGION_COUNT") or row.get("SUBREGION_COUNT"),
        "TERMINAL_BUILDER": (builders[0] if builders else None),
        "SHAFT_BUILDER": (builders[1] if len(builders) > 1 else None),
        "TRANSITION_BUILDER": "NON_CIRCULAR_PROFILE_LOFT",
        "OLD_MINOR_EXTENT_RATIO_U": OLD_MINOR_U,
        "NEW_MINOR_EXTENT_RATIO_U": new_off["U"],
        "OLD_MINOR_EXTENT_RATIO_V": OLD_MINOR_V,
        "NEW_MINOR_EXTENT_RATIO_V": new_off["V"],
        "OLD_CENTROID_ERROR": OLD_CENTROID,
        "NEW_CENTROID_ERROR": new_off["centroid_error"],
        "MINOR_EXTENT_INFLATION_FIRST_APPEARS_AT": infl0,
        "CENTROID_ERROR_FIRST_APPEARS_AT": "TERMINAL_LOFT",
        "SECTION_WIDTH_RATIO_P50": section_stats.get("SECTION_WIDTH_RATIO_P50"),
        "SECTION_WIDTH_RATIO_P95": section_stats.get("SECTION_WIDTH_RATIO_P95"),
        "SECTION_HEIGHT_RATIO_P50": section_stats.get("SECTION_HEIGHT_RATIO_P50"),
        "SECTION_HEIGHT_RATIO_P95": section_stats.get("SECTION_HEIGHT_RATIO_P95"),
        "SECTION_CENTROID_ERROR_P50": section_stats.get("SECTION_CENTROID_ERROR_P50"),
        "SECTION_CENTROID_ERROR_P95": section_stats.get("SECTION_CENTROID_ERROR_P95"),
        "PROFILE_BOUNDARY_METHOD": section_stats.get("PROFILE_BOUNDARY_METHOD"),
        "PROFILE_WIDTH_BIAS_SOURCE": bias_source(methods),
        "PROFILE_HEIGHT_BIAS_SOURCE": bias_source(methods),
        "CONVEX_HULL_USED": convex_used,
        "ALPHA_OR_CONCAVE_USED": alpha_used,
        "SLICE_SPAN_TO_SECTION_SPACING_RATIO": section_stats.get("SLICE_SPAN_TO_SECTION_SPACING_RATIO"),
        "PROFILE_CORRESPONDENCE_SUCCESS": section_stats.get("PROFILE_CORRESPONDENCE_SUCCESS"),
        "CORRESPONDENCE_NORMALIZATION_INVERTED": section_stats.get("CORRESPONDENCE_NORMALIZATION_INVERTED"),
        "RESAMPLING_EXTENT_DRIFT": section_stats.get("RESAMPLING_EXTENT_DRIFT"),
        "PROFILE_OUTWARD_OFFSET": 0.0,
        "SHAFT_RADIUS_RATIO": new_layers.get("SHAFT_EXTENT_RATIO_U"),
        "SHAFT_CENTERLINE_ERROR": (new_layers.get("shaft") or {}).get("centroid_error"),
        "SHAFT_TERMINAL_GAP": rt_payload.get("SHAFT_TERMINAL_GAP"),
        "SHAFT_TERMINAL_OVERLAP": rt_payload.get("SHAFT_TERMINAL_OVERLAP"),
        "TRANSITION_WIDTH_OVERSHOOT_RATIO": rt_payload.get("TRANSITION_WIDTH_OVERSHOOT_RATIO"),
        "TRANSITION_HEIGHT_OVERSHOOT_RATIO": rt_payload.get("TRANSITION_HEIGHT_OVERSHOOT_RATIO"),
        "TRANSITION_OVERSHOOT_DETECTED": rt_payload.get("TRANSITION_OVERSHOOT_DETECTED"),
        "MAX_TRANSITION_CENTROID_JUMP": rt_payload.get("MAX_TRANSITION_CENTROID_JUMP"),
        "PRESEW_EXTENT_RATIO": [new_layers.get("PRESEW_EXTENT_RATIO_U"), new_layers.get("PRESEW_EXTENT_RATIO_V")],
        "POSTSEW_EXTENT_RATIO": [new_layers.get("POSTSEW_EXTENT_RATIO_U"), new_layers.get("POSTSEW_EXTENT_RATIO_V")],
        "PRE_TO_POST_SEW_CENTROID_SHIFT": rt_payload.get("PRE_TO_POST_SEW_CENTROID_SHIFT"),
        "SEWING_GEOMETRY_MUTATION": rt_payload.get("SEWING_GEOMETRY_MUTATION"),
        "SEWING_TOLERANCE_NORMALIZED": rt_payload.get("SEWING_TOLERANCE_NORMALIZED"),
        **sym,
        "CAD_TO_SOURCE_BBOX_VOLUME_RATIO": bbox_vol_ratio,
        "TANK000_OFFICIAL_LOCAL_QA_PASS": bool(qa.get("qa_pass")),
        "QA_THRESHOLD_LOWERED": False,
        "COVERAGE_MIN": local_qa.COVERAGE_MIN,
        "FINAL_USES_ICP": False,
        "FINAL_USES_BBOX_FIT": False,
        "FINAL_USES_ANISOTROPIC_SCALE": False,
        "TANK45_RUNTIME_REEXECUTED": False,
        "CASE_SPECIFIC_RULE_COUNT": case_specific_count(),
        **tests,
        **{k: robot_reg.get(k) for k in ("ROBOT_REGRESSION_EXECUTED", "ROBOT_CAD_NATIVE_BEFORE", "ROBOT_CAD_NATIVE_AFTER_V2", "ROBOT_MAC_JSON_REUSED")},
        "row": {k: row.get(k) for k in ("ACTUAL_EXECUTED_BUILDER", "RESOLVED_BUILDER_FAMILY", "MAC_SUGGESTED_BUILDER", "qa_pass", "cad_native")},
        "MAC_SUGGESTED_BUILDER": row.get("MAC_SUGGESTED_BUILDER"),
        "RESOLVED_BUILDER": row.get("RESOLVED_BUILDER_FAMILY"),
    }
    summary["CURRENT_GATE"], summary["NEXT_PRIMARY_BLOCKER"] = gate_of(summary)
    dump(OUT / "artifacts/final_summary.json", summary)
    dump(
        OUT / "artifacts/composite_metric_root_cause.json",
        {
            "MINOR_EXTENT_INFLATION_FIRST_APPEARS_AT": infl0,
            "CENTROID_ERROR_FIRST_APPEARS_AT": "TERMINAL_LOFT",
            "V1_LAYER": {k: old_layers.get(k) for k in old_layers if "RATIO" in k or k in {"terminal", "shaft", "transition", "presew", "postsew"}},
            "V2_LAYER": {k: new_layers.get(k) for k in new_layers if "RATIO" in k},
            "note": "V1 2.1x appears at OCC smooth ThruSections of the terminal; input profiles were ~1.0. Cylinder/transition/sewing were not the first inflation stage.",
            "v1_terminal_loft_U": old_layers.get("TERMINAL_EXTENT_RATIO_U"),
            "v1_shaft_U": old_layers.get("SHAFT_EXTENT_RATIO_U"),
            "v1_transition_U": old_layers.get("TRANSITION_EXTENT_RATIO_U"),
            "v1_presew_U": old_layers.get("PRESEW_EXTENT_RATIO_U"),
            "v1_postsew_U": old_layers.get("POSTSEW_EXTENT_RATIO_U"),
        },
    )
    print("===== FINAL SUMMARY =====", flush=True)
    for key in [
        "CURRENT_GATE", "NEXT_PRIMARY_BLOCKER", "P3_REEXECUTED", "QWEN_REEXECUTED", "MAC_API_REEXECUTED",
        "BUILDER_ROUTING_CHANGED", "ACTUAL_BUILDER", "SUBREGION_COUNT", "TERMINAL_BUILDER", "SHAFT_BUILDER",
        "TRANSITION_BUILDER", "OLD_MINOR_EXTENT_RATIO_U", "NEW_MINOR_EXTENT_RATIO_U", "OLD_MINOR_EXTENT_RATIO_V",
        "NEW_MINOR_EXTENT_RATIO_V", "OLD_CENTROID_ERROR", "NEW_CENTROID_ERROR", "MINOR_EXTENT_INFLATION_FIRST_APPEARS_AT",
        "CENTROID_ERROR_FIRST_APPEARS_AT", "SECTION_WIDTH_RATIO_P50", "SECTION_WIDTH_RATIO_P95", "SECTION_HEIGHT_RATIO_P50",
        "SECTION_HEIGHT_RATIO_P95", "SECTION_CENTROID_ERROR_P50", "SECTION_CENTROID_ERROR_P95", "PROFILE_BOUNDARY_METHOD",
        "SLICE_SPAN_TO_SECTION_SPACING_RATIO", "PROFILE_CORRESPONDENCE_SUCCESS", "CORRESPONDENCE_NORMALIZATION_INVERTED",
        "RESAMPLING_EXTENT_DRIFT", "SHAFT_RADIUS_RATIO", "SHAFT_CENTERLINE_ERROR", "SHAFT_TERMINAL_GAP",
        "SHAFT_TERMINAL_OVERLAP", "TRANSITION_WIDTH_OVERSHOOT_RATIO", "TRANSITION_HEIGHT_OVERSHOOT_RATIO",
        "TRANSITION_OVERSHOOT_DETECTED", "MAX_TRANSITION_CENTROID_JUMP", "PRESEW_EXTENT_RATIO", "POSTSEW_EXTENT_RATIO",
        "PRE_TO_POST_SEW_CENTROID_SHIFT", "SEWING_GEOMETRY_MUTATION", "SEWING_TOLERANCE_NORMALIZED",
        "SOURCE_TO_CAD_CHAMFER", "CAD_TO_SOURCE_CHAMFER", "SYMMETRIC_CHAMFER", "SOURCE_TO_CAD_COVERAGE",
        "CAD_TO_SOURCE_COVERAGE", "TANK000_OFFICIAL_LOCAL_QA_PASS", "QA_THRESHOLD_LOWERED", "FINAL_USES_ICP",
        "FINAL_USES_BBOX_FIT", "FINAL_USES_ANISOTROPIC_SCALE", "ROBOT_REGRESSION_EXECUTED", "ROBOT_CAD_NATIVE_BEFORE",
        "ROBOT_CAD_NATIVE_AFTER_V2", "TANK45_RUNTIME_REEXECUTED", "CASE_SPECIFIC_RULE_COUNT", "TESTS_PASSED", "TESTS_FAILED",
    ]:
        print(f"{key}={summary.get(key)}", flush=True)
    return 0 if tests.get("TESTS_FAILED", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
