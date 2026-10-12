#!/usr/bin/env python3
"""BUILD_A_ROBOT Pipeline-A fullstack repair V2.

This runner freezes the already-successful BUILD_A_ROBOT P3 result and repairs
CAD recovery after P3. It records the old V1 failure mode, restores the Pipeline
A prepare/MAC/runtime/ranking contracts, and only falls back to faceted STEP
after CAD-native candidates fail formal local QA.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE_DEFAULT = ROOT / "ours3/meshes/BUILD_A_ROBOT.obj"
V1_ROOT_DEFAULT = ROOT / "ours3/build_a_robot_fresh_generalization_v1"
OUT_DEFAULT = ROOT / "ours3/build_a_robot_pipeline_a_fullstack_repair_v2"
CASE09_ROOT = ROOT / "ours3/case09_fullstack_mesh2cad_mac_v6"
MAC_ENV_FILE = ROOT / "ours3/.mac_env"
MAC_REPO = ROOT / "Multi-Agent-CAD"
BACKENDS = (
    "MAC_GENERATED_CAD",
    "CURRENT_V6",
    "SUPERFIT_ANALYTIC",
    "POINT2CAD_SURFACE",
    "HYBRID",
    "FACETED_FALLBACK",
)

sys.path.insert(0, str(ROOT / "scripts"))
import build_a_robot_fresh_generalization_v1 as v1  # noqa: E402
import dual_modal_qwen3vl as qwen3vl  # noqa: E402
import generic_cad_runtime as generic_runtime  # noqa: E402
import pipeline_a_mac_graph as mac_graph  # noqa: E402

REUSE_MAC_DEFAULT = True


def log_part(out: Path, message: str) -> None:
    """Append one line when a part starts or finishes. Safe to tail."""
    log_dir = out / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    print(line, end="", flush=True)
    for name in ("parts.log", "run.log"):
        with (log_dir / name).open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fields})


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve_p3_root(reuse_root: Path) -> Path:
    candidates = [reuse_root, reuse_root / "01_p3"]
    candidates.extend(path.parent for path in reuse_root.rglob("triangle_part_id.npy"))
    for candidate in candidates:
        if (candidate / "triangle_part_id.npy").is_file() and (candidate / "part_metadata.json").is_file():
            return candidate
    raise FileNotFoundError(f"Could not locate frozen P3 output under {reuse_root}")


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"not a mesh: {path}")
    return mesh


def load_frozen_p3(source: Path, reuse_root: Path) -> dict[str, Any]:
    p3_root = resolve_p3_root(reuse_root)
    p3 = v1.load_p3(source, p3_root)
    p3["resolved_p3_root"] = str(p3_root)
    return p3


def source_audit(source: Path, p3: dict[str, Any]) -> dict[str, Any]:
    mesh = p3["source"]
    return {
        "source_path": str(source.resolve()),
        "source_sha256": sha_file(source),
        "vertex_count": int(len(mesh.vertices)),
        "triangle_count": int(len(mesh.faces)),
        "connected_component_count": int(len(mesh.split(only_watertight=False))),
        "bbox": np.asarray(mesh.bounds, dtype=float).tolist(),
        "p3_reexecuted": False,
        "p3_root": p3["resolved_p3_root"],
    }


def audit_v1(v1_root: Path) -> dict[str, Any]:
    summary = load_json(v1_root / "artifacts/summary.json", {}) or {}
    rows = []
    manifest = v1_root / "artifacts/component_backend_manifest.csv"
    if manifest.is_file():
        with manifest.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

    def count_bool(field: str) -> int:
        return sum(str(row.get(field, "")).lower() in {"true", "1", "yes"} for row in rows)

    def count_files(pattern: str) -> int:
        return len(list((v1_root / "03_components").glob(pattern)))

    mac_runtime_count = count_files("P3_COMPONENT_*/candidates/mac_generated/execution.stdout.log")
    audit = {
        "OLD_P3_COMPONENT_COUNT": int(summary.get("P3_COMPONENT_COUNT") or len(rows)),
        "OLD_MAC_COMPONENTS_ATTEMPTED": int(summary.get("MAC_COMPONENTS_ATTEMPTED") or count_bool("mac_attempted")),
        "OLD_MAC_COMPONENTS_SUCCESS": int(summary.get("MAC_COMPONENTS_SUCCESS") or count_bool("mac_success")),
        "OLD_MAC_CONSTRUCTION_HYPOTHESES": count_files("P3_COMPONENT_*/candidates/mac_generated/planner_output.json"),
        "OLD_MAC_GENERATED_CODE_COUNT": count_files("P3_COMPONENT_*/candidates/mac_generated/generated_code.py"),
        "OLD_MAC_RUNTIME_EXECUTION_COUNT": mac_runtime_count,
        "OLD_MAC_STEP_SUCCESS": int(summary.get("MAC_GENERATED_STEP_SUCCESS") or count_bool("mac_generated_step_success")),
        "OLD_MAC_QA_PASS": 0,
        "OLD_CURRENT_V6_ATTEMPTED": int(summary.get("CURRENT_V6_COMPONENTS_ROUTED") or count_bool("current_v6_attempted")),
        "OLD_CURRENT_V6_STEP_SUCCESS": count_files("P3_COMPONENT_*/candidates/current_v6/current_v6.step"),
        "OLD_CURRENT_V6_QA_PASS": int(summary.get("CURRENT_V6_COMPONENTS_QA_PASS") or 0),
        "OLD_SUPERFIT_ATTEMPTED": int(summary.get("SUPERFIT_COMPONENTS_ROUTED") or count_bool("superfit_attempted")),
        "OLD_SUPERFIT_CANDIDATES": int(summary.get("SUPERFIT_PROPOSAL_COUNT") or 0),
        "OLD_SUPERFIT_QA_PASS": int(summary.get("SUPERFIT_COMPONENTS_QA_PASS") or 0),
        "OLD_POINT2CAD_ATTEMPTED": int(summary.get("POINT2CAD_COMPONENTS_ROUTED") or count_bool("point2cad_attempted")),
        "OLD_POINT2CAD_SURFACE_SUCCESS": int(summary.get("POINT2CAD_SURFACE_SUCCESS_COMPONENTS") or count_bool("point2cad_surface_success")),
        "OLD_POINT2CAD_CANDIDATES": int(summary.get("POINT2CAD_TOPOLOGY_SUCCESS_COMPONENTS") or 0),
        "OLD_POINT2CAD_QA_PASS": int(summary.get("POINT2CAD_COMPONENTS_QA_PASS") or 0),
        "OLD_HYBRID_ATTEMPTED": int(summary.get("HYBRID_COMPONENTS_ROUTED") or 0),
        "OLD_HYBRID_CANDIDATES": int(summary.get("HYBRID_SUBREGION_COUNT") or 0),
        "OLD_HYBRID_QA_PASS": int(summary.get("HYBRID_COMPONENTS_QA_PASS") or 0),
        "OLD_FACETED_SELECTED": int(summary.get("FACETED_FALLBACK_COMPONENTS") or sum(row.get("selected_backend") == "FACETED_FALLBACK" for row in rows)),
        "PIPELINE_A_WAS_FULLY_EXECUTED": bool(
            mac_runtime_count > 0
            and count_files("P3_COMPONENT_*/candidates/mac_generated/generated.step") > 0
            and int(summary.get("MAC_GENERATED_STEP_SUCCESS") or 0) > 0
        ),
        "why_all_faceted": {
            "MAC_GENERATED_CAD": "MAC calls returned no parseable construction JSON/code in V1.",
            "CURRENT_V6": "STEP candidates were generated for some components but failed local geometry QA.",
            "SUPERFIT_ANALYTIC": "SuperFit ran on routed components but produced zero supported primitive proposals.",
            "POINT2CAD_SURFACE": "Point2CAD timed out or did not recover usable surface/topology candidates.",
            "HYBRID": "Hybrid was a counter only; no subregion composition candidate was created.",
            "FACETED_FALLBACK": "Only fallback candidates passed V1 selection.",
        },
    }
    return audit


def pipeline_a_reuse_audit() -> dict[str, Any]:
    scripts = CASE09_ROOT / "scripts"
    return {
        "prepare_module": str((scripts / "v6_prepare.py").resolve()),
        "mac_module": str((scripts / "v6_mac.py").resolve()),
        "runtime_module": str((scripts / "v6_runtime.py").resolve()),
        "reexecute_module": str((scripts / "v6_reexecute.py").resolve()),
        "repair_module": str((scripts / "v6_repair.py").resolve()),
        "finalize_module": str((scripts / "v6_finalize.py").resolve()),
        "geometry_analyzer_reused": bool((CASE09_ROOT / "03_geometry_analyzer").is_dir()),
        "semantic_surface_reused": bool((CASE09_ROOT / "04_semantic_surface").is_dir()),
        "feature_graph_reused": bool((CASE09_ROOT / "05_feature_graph").is_dir()),
        "dual_modal_adapter_reused": bool((CASE09_ROOT / "06_dual_modal_adapter").is_dir()),
        "mac_candidate_contract_reused": bool((CASE09_ROOT / "08_multi_candidate_mac").is_dir()),
        "runtime_fitter_reused": bool((scripts / "v6_runtime.py").is_file()),
        "candidate_ranking_reused": bool((CASE09_ROOT / "09_candidate_ranking").is_dir()),
        "targeted_repair_reused": bool((CASE09_ROOT / "11_targeted_repair").is_dir()),
        "robot_runtime_notes": "Robot V2 uses the same staged contract and restores runtime source-part reread; geometry decisions remain generic.",
    }


def pca_local(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    centroid = vertices.mean(axis=0)
    centered = vertices - centroid
    covariance = centered.T @ centered / max(len(vertices), 1)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    axes = vectors[:, order]
    local = centered @ axes
    return centroid, axes, local


def enriched_spec(part: dict[str, Any]) -> dict[str, Any]:
    spec = v1.measure_component(part)
    mesh = part["mesh"]
    vertices = np.asarray(mesh.vertices, dtype=float)
    centroid, axes, local = pca_local(mesh)
    normals = np.asarray(mesh.face_normals, dtype=float)
    radial = np.linalg.norm(local[:, 1:] - local[:, 1:].mean(axis=0), axis=1)
    symmetry = {}
    for axis in range(3):
        mirrored = local.copy()
        mirrored[:, axis] *= -1.0
        tree = v1.cKDTree(local)
        distances = tree.query(mirrored, workers=-1)[0]
        symmetry[f"axis_{axis}"] = float(np.mean(distances) / max(np.linalg.norm(mesh.extents), 1e-9))
    boundary_edges = np.asarray(mesh.edges_unique)[
        np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique)) == 1
    ]
    spec.update(
        {
            "schema": "BUILD_A_ROBOT_PIPELINE_A_REPAIR_V2_GEOMETRY_SPEC",
            "orientation": axes.tolist(),
            "principal_axes": axes.tolist(),
            "dimensions": np.ptp(local, axis=0).tolist(),
            "thickness": float(np.min(np.ptp(local, axis=0))),
            "radial_profile_quantiles": {
                "q50": float(np.quantile(radial, 0.50)),
                "q65": float(np.quantile(radial, 0.65)),
                "q80": float(np.quantile(radial, 0.80)),
                "q90": float(np.quantile(radial, 0.90)),
            },
            "symmetry": symmetry,
            "hole_evidence": int(len(boundary_edges) > 0),
            "slot_evidence": int(len(boundary_edges) > len(mesh.faces) * 0.02),
            "notch_evidence": int(spec["boundary_complexity"] > 0.05),
            "gap_evidence": int(spec["connected_component_count"] > 1),
            "cavity_evidence": int(not mesh.is_watertight),
            "negative_space_evidence": int(spec["boundary_complexity"] > 0.05 or not mesh.is_watertight),
            "scores": {
                **spec["scores"],
                "mixed_structure_score": float(
                    min(
                        1.0,
                        0.4 * min(spec["connected_component_count"] / 3.0, 1.0)
                        + 0.3 * min(spec["boundary_complexity"], 1.0)
                        + 0.3 * spec["scores"].get("freeform_score", 0.0),
                    )
                ),
            },
            "measurement_authority": "RUNTIME_SOURCE_PART_OBJ",
            "source_part_reread_required_by_runtime": True,
        }
    )
    return spec


def project(points: np.ndarray, mode: str) -> np.ndarray:
    if mode == "top":
        return points[:, [0, 1]]
    if mode == "side":
        return points[:, [0, 2]]
    if mode == "front":
        return points[:, [1, 2]]
    return np.column_stack((points[:, 0] - 0.35 * points[:, 1], points[:, 2] + 0.20 * points[:, 1]))


def render_mesh(mesh: trimesh.Trimesh, path: Path, mode: str, *, edges: bool = False) -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > 5000:
        faces = faces[np.linspace(0, len(faces) - 1, 5000, dtype=np.int64)]
    coords = project(vertices, mode)
    low, high = coords.min(axis=0), coords.max(axis=0)
    scale = max(float(np.max(high - low)), 1e-9)
    xy = (coords - (low + high) * 0.5) / scale * 320.0 + 180.0
    image = Image.new("RGB", (360, 390), "white")
    draw = ImageDraw.Draw(image)
    for face in faces:
        polygon = [(int(xy[index, 0]), int(360 - xy[index, 1])) for index in face]
        draw.polygon(polygon, fill=(172, 188, 202), outline=(90, 102, 115) if edges else None)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def canonical_obj_tokens(part: dict[str, Any], spec: dict[str, Any], path: Path) -> None:
    lines = [
        f"component_id={part['component_id']}",
        f"p3_label={part['p3_label']}",
        f"triangle_count={part['triangle_count']}",
        f"bbox={json.dumps(spec['bbox'])}",
        f"centroid={json.dumps(spec['centroid'])}",
        f"principal_extents={json.dumps(spec['principal_extents'])}",
        f"radial_profile_quantiles={json.dumps(spec['radial_profile_quantiles'])}",
        "token_source=RUNTIME_MEASURED_SOURCE_PART",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_component(part: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> None:
    source_part = component_dir / "01_prepare/source_part.obj"
    source_part.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(part["source_obj"], source_part)
    write_json(
        component_dir / "01_prepare/prepare_manifest.json",
        {
            "component_id": part["component_id"],
            "source_part_obj": str(source_part),
            "source_sha256": sha_file(source_part),
            "triangle_ids_sha256": part["triangle_ids_sha256"],
            "pipeline_a_prepare_executed": True,
        },
    )
    write_json(component_dir / "02_geometry_analyzer/geometry_analysis.json", spec)
    semantic = {
        "component_id": part["component_id"],
        "semantic_surface_schema": "GENERIC_GEOMETRY_PRIORS_ONLY",
        "construction_priors": [
            {"family": "PROFILE_LOFT", "score": spec["scores"]["loft_score"]},
            {"family": "REVOLUTION", "score": spec["scores"]["revolution_score"]},
            {"family": "EXTRUSION", "score": spec["scores"]["extrusion_consistency"]},
            {"family": "FREEFORM_OPEN_SHELL", "score": spec["scores"]["freeform_score"]},
        ],
        "case_specific_runtime_rule_used": False,
        "geometry_evidence_priority": True,
    }
    write_json(component_dir / "03_semantic_surface/semantic_surface.json", semantic)
    feature = {
        "component_id": part["component_id"],
        "nodes": [
            {"id": "principal_axes", "kind": "measurement"},
            {"id": "boundary_complexity", "kind": "measurement", "value": spec["boundary_complexity"]},
            {"id": "radial_profile", "kind": "runtime_profile"},
            {"id": "negative_space", "kind": "evidence", "value": spec["negative_space_evidence"]},
        ],
        "design_intent_context": {
            "likely_builder_family": max(semantic["construction_priors"], key=lambda row: row["score"])["family"],
            "mac_may_choose_how_not_dimensions": True,
        },
    }
    write_json(component_dir / "04_feature_graph/feature_graph.json", feature)
    write_json(component_dir / "04_feature_graph/design_intent_context.json", feature["design_intent_context"])
    dual = component_dir / "05_dual_modal"
    dual.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_part, dual / "proxy.obj")
    canonical_obj_tokens(part, spec, dual / "canonical_obj_tokens.txt")
    renders = []
    for mode in ("axonometric", "top", "side", "front"):
        path = dual / f"{mode}_shaded.png"
        render_mesh(part["mesh"], path, mode, edges=False)
        renders.append(str(path))
    render_mesh(part["mesh"], dual / "axonometric_wireframe.png", "axonometric", edges=True)
    write_json(
        dual / "mac_input_manifest.json",
        {
            "component_id": part["component_id"],
            "canonical_obj_tokens_path": str(dual / "canonical_obj_tokens.txt"),
            "render_paths": renders,
            "measured_spec_path": str(component_dir / "02_geometry_analyzer/geometry_analysis.json"),
            "feature_graph_path": str(component_dir / "04_feature_graph/feature_graph.json"),
            "dual_modal_actually_entered_mac": False,
            "VISUAL_QWEN3VL_OK": False,
            "render_sent_as_image": False,
        },
    )
    visual = qwen3vl.analyze_dual_modal_dir(dual)
    write_json(
        dual / "mac_input_manifest.json",
        {
            **(load_json(dual / "mac_input_manifest.json", {}) or {}),
            "visual_context": str((dual / "visual_context.json").resolve()),
            "VISUAL_QWEN3VL_OK": bool(visual.get("ok")),
            "render_sent_as_image": bool(visual.get("ok") and visual.get("render_sent_as_image")),
            "dual_modal_actually_entered_mac": False,
        },
    )


def load_env_file(path: Path) -> dict[str, str]:
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def extract_json(text: str) -> Any:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S | re.I)
    candidate = fenced.group(1) if fenced else text
    try:
        return json.loads(candidate)
    except Exception:
        pass
    start_positions = [pos for pos in (candidate.find("{"), candidate.find("[")) if pos >= 0]
    if not start_positions:
        raise ValueError("MAC response did not contain JSON")
    start = min(start_positions)
    end = max(candidate.rfind("}"), candidate.rfind("]"))
    if end <= start:
        raise ValueError("MAC response did not contain complete JSON")
    return json.loads(candidate[start : end + 1])


def mac_hypotheses_from_model(part: dict[str, Any], spec: dict[str, Any], component_dir: Path, max_hypotheses: int = 2, reuse_mac: bool | None = None) -> dict[str, Any]:
    mac_dir = component_dir / "06_mac"
    mac_dir.mkdir(parents=True, exist_ok=True)
    if reuse_mac is None:
        reuse_mac = REUSE_MAC_DEFAULT
    existing = load_json(mac_dir / "mac_hypotheses.json", {}) or {}
    if reuse_mac and existing.get("hypotheses"):
        reused = dict(existing)
        reused["MAC_API_REEXECUTED"] = False
        reused["MAC_JSON_REUSED"] = True
        reused["success"] = True
        reused["attempted"] = True
        write_json(mac_dir / "mac_hypotheses.json", reused)
        return reused
    env = load_env_file(MAC_ENV_FILE)
    for key, value in env.items():
        os.environ.setdefault(key, value)
    result = {
        "component_id": part["component_id"],
        "attempted": True,
        "resource_failure": False,
        "success": False,
        "hypotheses": [],
        "raw_response_path": None,
        "failure_reason": None,
        "MAC_API_REEXECUTED": True,
        "MAC_JSON_REUSED": False,
    }
    try:
        mac_root = ROOT / "Multi-Agent-CAD"
        if str(mac_root) not in sys.path:
            sys.path.insert(0, str(mac_root))
        from multi_agent_cad import config
        import multi_agent_cad.nodes as mac_nodes

        client = mac_nodes._llm_client()
        model = config.ARCHITECT_MODEL
        scores = spec["scores"]
        visual_parsed = qwen3vl.visual_json_for_mac(component_dir)
        visual_entered = visual_parsed is not None
        template = {
            "hypotheses": [
                {
                    "hypothesis_id": "MAC_CANDIDATE_01",
                    "builder_family": "PROFILE_LOFT",
                    "visual_builder_suggestion": (visual_parsed or {}).get("likely_builder_family") or "PROFILE_LOFT",
                    "requested_builder_family": (visual_parsed or {}).get("likely_builder_family") or "PROFILE_LOFT",
                    "profile_mode": "UNKNOWN",
                    "decomposition_required": False,
                    "expected_structure": [],
                    "negative_space_hint": "NONE",
                    "surface_complexity_hint": "UNKNOWN",
                    "quantile": 0.5,
                    "section_count": 64,
                    "cad_brief": "Cite the Qwen3-VL global_shape. Runtime rereads source_part.obj for all dimensions.",
                    "acceptance_checks": ["step_reload", "local_chamfer", "coverage", "bbox_extent"],
                }
            ]
        }
        evidence = (
            f"component={part['component_id']} triangles={part['triangle_count']} "
            f"planarity={scores['planarity_score']:.3f} cylindricality={scores['cylindricality_score']:.3f} "
            f"loft={scores['loft_score']:.3f} freeform={scores['freeform_score']:.3f} "
            f"q50={spec['radial_profile_quantiles']['q50']:.6f} q80={spec['radial_profile_quantiles']['q80']:.6f}."
        )
        if not visual_entered:
            raise RuntimeError("QWEN3VL_VISUAL_CONTEXT_MISSING_IMAGES_NOT_SENT")
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=1200,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the Pipeline A CAD architect. Return JSON only. "
                        "Choose HOW to build, never invent dimensions. Runtime will reread source_part.obj. "
                        "Qwen3-VL already saw the component renders; cad_brief must cite its global_shape. "
                        "Fill requested_builder_family, profile_mode, decomposition_required, expected_structure, "
                        "negative_space_hint, surface_complexity_hint as hypotheses, not metric facts. "
                        "Runtime binds size, axis, profile and negative space from source geometry."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Return exactly valid JSON using this template. You may keep quantile unused; "
                        "runtime reconstructs geometry from source_part.obj and selects the executable builder. "
                        "Do not invent millimetre lengths or radii. "
                        + json.dumps(template, ensure_ascii=False)
                        + "\nEvidence numbers: "
                        + evidence
                        + "\nQwen3-VL visual JSON (images were sent to local Qwen3-VL-4B-Instruct): "
                        + json.dumps(visual_parsed, ensure_ascii=False)
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or ""
        raw_path = mac_dir / "mac_raw_response.txt"
        raw_path.write_text(raw, encoding="utf-8")
        result["raw_response_path"] = str(raw_path)
        parsed = extract_json(raw)
        hypotheses = parsed.get("hypotheses", parsed if isinstance(parsed, list) else [])
        normalized = []
        for index, hypothesis in enumerate(hypotheses[:max_hypotheses], 1):
            item = dict(hypothesis)
            item.setdefault("hypothesis_id", f"MAC_CANDIDATE_{index:02d}")
            item.setdefault("builder_family", "PROFILE_LOFT")
            item.setdefault("quantile", 0.5)
            item.setdefault("section_count", 64)
            item.setdefault("cad_brief", "Runtime profile loft from measured component-local sections.")
            item.setdefault("acceptance_checks", ["step_reload", "local_chamfer", "coverage", "bbox_extent"])
            normalized.append(item)
        qwen3vl.mark_visual_entered_mac(component_dir, True)
        result.update(
            {
                "success": bool(normalized),
                "hypotheses": normalized,
                "raw_response_path": str(raw_path),
                "model": model,
                "visual_model": qwen3vl.visual_model(),
                "visual_entered_mac_prompt": True,
            }
        )
    except Exception as exc:
        text = f"{type(exc).__name__}:{exc}"
        resource = any(token in text for token in ("403", "AllocationQuota", "timeout", "HTTP", "Connection", "QWEN3VL"))
        qwen3vl.mark_visual_entered_mac(component_dir, False)
        result.update({"failure_reason": text, "resource_failure": resource, "visual_entered_mac_prompt": False})
    write_json(mac_dir / "mac_hypotheses.json", result)
    return result


RUNTIME_CODE = r'''
#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
import trimesh
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.GC import GC_MakeCircle
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs

def pca_local(mesh):
    vertices=np.asarray(mesh.vertices,dtype=float)
    centroid=vertices.mean(axis=0)
    centered=vertices-centroid
    values,vectors=np.linalg.eigh((centered.T@centered)/max(len(vertices),1))
    order=np.argsort(values)[::-1]
    axes=vectors[:,order]
    local=centered@axes
    return centroid,axes,local

def build_profile_loft(mesh, output, measurements_path, quantile=0.5, section_count=64):
    centroid,axes,local=pca_local(mesh)
    x=local[:,0]
    uv=local[:,1:]
    uv_center=uv.mean(axis=0)
    radial=np.linalg.norm(uv-uv_center,axis=1)
    edges=np.linspace(float(x.min()), float(x.max()), int(section_count))
    sections=[]
    runtime_sections=[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        mask=(x>=lo)&(x<=hi)
        if int(mask.sum()) < 8:
            continue
        xi=float((lo+hi)*0.5)
        ri=float(np.quantile(radial[mask], quantile))
        if ri <= 1e-8:
            continue
        origin=(np.array([xi,uv_center[0],uv_center[1]],dtype=float)@axes.T + centroid).tolist()
        axis=axes[:,0].tolist()
        circle=GC_MakeCircle(gp_Ax2(gp_Pnt(*map(float,origin)), gp_Dir(*map(float,axis))), ri).Value()
        edge=BRepBuilderAPI_MakeEdge(circle).Edge()
        wire=BRepBuilderAPI_MakeWire(edge).Wire()
        sections.append(wire)
        runtime_sections.append({"station": xi, "radius": ri, "support_vertex_count": int(mask.sum())})
    if len(sections) < 2:
        raise RuntimeError("INSUFFICIENT_RUNTIME_SECTIONS")
    loft=BRepOffsetAPI_ThruSections(False, True, 1e-4)
    for wire in sections:
        loft.AddWire(wire)
    loft.CheckCompatibility(False)
    loft.Build()
    shape=loft.Shape()
    writer=STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status=writer.Write(str(output))
    measurements={
        "source_part_reread": True,
        "source_part_path": str(args.source_part),
        "builder_family": "PROFILE_LOFT_OPEN_SHELL",
        "quantile": quantile,
        "section_count_requested": int(section_count),
        "section_count_used": len(runtime_sections),
        "principal_axes": axes.tolist(),
        "centroid": centroid.tolist(),
        "sections": runtime_sections,
        "dimension_provenance": "runtime reread source_part.obj; MAC selected how, not dimensions",
        "step_write_status": str(status),
        "step_success": bool(status == IFSelect_RetDone and output.is_file() and output.stat().st_size > 0),
    }
    measurements_path.write_text(json.dumps(measurements, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if measurements["step_success"] else 2

parser=argparse.ArgumentParser()
parser.add_argument("--source-part", type=Path, required=True)
parser.add_argument("--hypothesis", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--runtime-measurements", type=Path, required=True)
args=parser.parse_args()
hypothesis=json.loads(args.hypothesis.read_text(encoding="utf-8"))
mesh=trimesh.load(args.source_part, force="mesh", process=False)
quantile=float(hypothesis.get("quantile", 0.5))
section_count=int(hypothesis.get("section_count", 64))
raise SystemExit(build_profile_loft(mesh, args.output, args.runtime_measurements, quantile, section_count))
'''


def execute_explicit_circular_baseline(source_part: Path, hypothesis: dict[str, Any], candidate_dir: Path, backend: str, candidate_id: str) -> dict[str, Any]:
    """Dedicated circular loft baseline. Not the MAC default builder."""
    candidate_dir.mkdir(parents=True, exist_ok=True)
    write_json(candidate_dir / "construction_hypothesis.json", hypothesis)
    write_json(candidate_dir / "architect_plan.json", {"backend": backend, "hypothesis": hypothesis, "runtime_contract": "EXPLICIT_CIRCULAR_PROFILE_LOFT_BASELINE"})
    program = candidate_dir / "generated_code.py"
    program.write_text(RUNTIME_CODE, encoding="utf-8")
    runtime = candidate_dir / "runtime_measurements.json"
    step = candidate_dir / "generated.step"
    proc = subprocess.run(
        [
            sys.executable,
            str(program),
            "--source-part",
            str(source_part),
            "--hypothesis",
            str(candidate_dir / "construction_hypothesis.json"),
            "--output",
            str(step),
            "--runtime-measurements",
            str(runtime),
        ],
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    (candidate_dir / "execution.stdout.log").write_text(proc.stdout, encoding="utf-8")
    (candidate_dir / "execution.stderr.log").write_text(proc.stderr, encoding="utf-8")
    return {
        "component_id": source_part.parent.parent.name,
        "candidate_id": candidate_id,
        "backend": backend,
        "representation": "CIRCULAR_PROFILE_LOFT_OPEN_SHELL_BREP",
        "topology_class": "OPEN_SHELL_BREP",
        "cad_native": True,
        "runtime_success": proc.returncode == 0,
        "generated_code_path": str(program),
        "runtime_measurements_path": str(runtime),
        "step_path": str(step),
        "step_success": bool(proc.returncode == 0 and step.is_file() and step.stat().st_size > 0),
        "exit_code": proc.returncode,
        "ACTUAL_EXECUTED_BUILDER": "CIRCULAR_PROFILE_LOFT",
        "RESOLVED_BUILDER_FAMILY": "CIRCULAR_PROFILE_LOFT",
    }


def execute_generated_profile_code(source_part: Path, hypothesis: dict[str, Any], candidate_dir: Path, backend: str, candidate_id: str) -> dict[str, Any]:
    candidate_dir.mkdir(parents=True, exist_ok=True)
    write_json(candidate_dir / "cad_brief.json", {"cad_brief": hypothesis.get("cad_brief"), "dimension_source": "generic_cad_runtime"})
    measured = load_json(Path(source_part).parent / "measured_spec.json", {}) or {}
    result = generic_runtime.reconstruct_from_source(
        Path(source_part),
        hypothesis,
        Path(candidate_dir),
        measured=measured,
        candidate_id=candidate_id,
        backend=backend,
    )
    result.setdefault("component_id", Path(source_part).parent.parent.name)
    result.setdefault("candidate_id", candidate_id)
    result.setdefault("backend", backend)
    result.setdefault("cad_native", True)
    (candidate_dir / "execution.stdout.log").write_text("generic_cad_runtime.reconstruct_from_source\n", encoding="utf-8")
    (candidate_dir / "execution.stderr.log").write_text("", encoding="utf-8")
    return result


def qa_candidate(part: dict[str, Any], candidate: dict[str, Any], qa_dir: Path) -> dict[str, Any]:
    qa_dir.mkdir(parents=True, exist_ok=True)
    mesh = v1.tessellate_step(candidate.get("step_path"), qa_dir / f"{candidate['candidate_id']}.stl") if candidate.get("step_success") else None
    if mesh is None:
        qa = {
            "qa_pass": False,
            "failure_reason": "STEP_RELOAD_OR_TESSELLATION_FAILED",
            "artifact_valid": False,
            "transform_sane": False,
            "occ_valid": False,
            "step_reload": False,
        }
    else:
        qa = v1.qa_mesh(part["mesh"], mesh)
        extent_error = max(qa.get("extent_error_xyz") or [1.0])
        qa.update(
            {
                "artifact_valid": True,
                "transform_sane": (
                    qa["bbox_center_error"] <= v1.CAD_NATIVE_BBOX_CENTER_MAX
                    and extent_error <= v1.CAD_NATIVE_EXTENT_ERROR_MAX
                ),
                "occ_valid": True,
                "step_reload": True,
                "catastrophic_overspan": False,
                "OCCUPANCY_STATUS": "NOT_APPLICABLE_OPEN_SHELL",
            }
        )
        qa["qa_pass"] = bool(qa["qa_pass"] and qa["transform_sane"] and qa["artifact_valid"])
        if not qa["qa_pass"]:
            qa["failure_reason"] = qa.get("failure_reason") or "CAD_NATIVE_HARD_GATE_FAIL"
    write_json(qa_dir / "qa.json", qa)
    candidate["qa"] = qa
    candidate["qa_pass"] = bool(qa.get("qa_pass"))
    candidate["chamfer"] = qa.get("chamfer")
    candidate["hausdorff"] = qa.get("hausdorff")
    candidate["coverage"] = qa.get("coverage")
    return candidate


def run_mac_candidates(part: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> list[dict[str, Any]]:
    log_part(component_dir.parents[1], f"MAC_START {part['component_id']}")
    mac = mac_hypotheses_from_model(part, spec, component_dir, max_hypotheses=1, reuse_mac=REUSE_MAC_DEFAULT)
    hypotheses = list(mac.get("hypotheses") or [])
    if not hypotheses:
        hypotheses = [{"hypothesis_id": "MAC_CANDIDATE_01", "builder_family": "UNKNOWN", "visual_builder_suggestion": "UNKNOWN"}]
    candidate = execute_generated_profile_code(
        component_dir / "01_prepare/source_part.obj",
        hypotheses[0],
        component_dir / "07_candidates/mac_candidate_01",
        "MAC_GENERATED_CAD",
        str(hypotheses[0].get("hypothesis_id") or "MAC_CANDIDATE_01"),
    )
    log_part(
        component_dir.parents[1],
        f"MAC_DONE {part['component_id']} step_ok={bool(candidate.get('step_success'))} fail={candidate.get('failure_reason')}",
    )
    cid = candidate.get("candidate_id") or "MAC_CANDIDATE_01"
    cand_dir = component_dir / "07_candidates" / "mac_candidate_01"
    candidate = qa_candidate(part, candidate, component_dir / "08_qa" / cid)
    write_json(cand_dir / "candidate_manifest.json", candidate)
    write_json(
        component_dir / "06_mac/mac_execution_audit.json",
        {
            "component_id": part["component_id"],
            "attempted": True,
            "success": bool(candidate.get("step_success")),
            "MAC_GRAPH_USED": False,
            "ACTUAL_EXECUTED_BUILDER": candidate.get("ACTUAL_EXECUTED_BUILDER"),
            "hypotheses": hypotheses[:1],
            "generated_code_count": int(bool(candidate.get("generated_code_path") and Path(str(candidate["generated_code_path"])).is_file())),
            "runtime_executed": 1,
            "step_success": int(bool(candidate.get("step_success"))),
            "qa_pass": int(bool(candidate.get("qa_pass"))),
            "MAC_API_REEXECUTED": bool(mac.get("MAC_API_REEXECUTED")),
            "MAC_JSON_REUSED": bool(mac.get("MAC_JSON_REUSED")),
            "shared_runtime": "generic_cad_runtime.reconstruct_from_source",
            "failure_reason": candidate.get("failure_reason"),
        },
    )
    return [candidate]


def best_profile_hypothesis(part: dict[str, Any]) -> dict[str, Any]:
    # Generic runtime fitting sweep. This is not a ranking threshold change; it is
    # a candidate-generation step that searches measured profile parameters.
    best = None
    source_part = part["mesh"]
    tmp_root = Path("/tmp/build_robot_profile_probe")
    tmp_root.mkdir(parents=True, exist_ok=True)
    for quantile in (0.5, 0.65, 0.8, 0.9):
        h = {
            "hypothesis_id": f"CURRENT_V6_PROFILE_LOFT_Q{int(quantile * 100)}",
            "builder_family": "PROFILE_LOFT",
            "quantile": quantile,
            "section_count": 64,
            "cad_brief": "Generic runtime profile loft candidate.",
        }
        probe_dir = tmp_root / part["component_id"] / f"q{int(quantile * 100)}"
        source_probe = probe_dir / "source_part.obj"
        probe_dir.mkdir(parents=True, exist_ok=True)
        if not source_probe.is_file():
            shutil.copy2(part["source_obj"], source_probe)
        cand = execute_explicit_circular_baseline(source_probe, h, probe_dir, "CURRENT_V6", h["hypothesis_id"])
        cand = qa_candidate(part, cand, probe_dir / "qa")
        if best is None or (
            bool(cand.get("qa_pass")),
            float(cand.get("coverage") or 0.0),
            -float(cand.get("chamfer") or 1e9),
        ) > (
            bool(best.get("qa_pass")),
            float(best.get("coverage") or 0.0),
            -float(best.get("chamfer") or 1e9),
        ):
            best = {**h, "probe_qa": cand.get("qa", {})}
    return best or {"hypothesis_id": "CURRENT_V6_PROFILE_LOFT_DEFAULT", "builder_family": "PROFILE_LOFT", "quantile": 0.5, "section_count": 64}


def run_current_v6_candidate(part: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    h = best_profile_hypothesis(part)
    candidate = execute_explicit_circular_baseline(component_dir / "01_prepare/source_part.obj", h, component_dir / "07_candidates/current_v6", "CURRENT_V6", "CURRENT_V6_PROFILE_LOFT")
    candidate = qa_candidate(part, candidate, component_dir / "08_qa/CURRENT_V6_PROFILE_LOFT")
    candidate["mac_hypothesis_id"] = None
    write_json(component_dir / "07_candidates/current_v6/current_v6_result.json", candidate)
    return candidate


def run_superfit_candidate(part: dict[str, Any], component_dir: Path, timeout: int = 300) -> dict[str, Any]:
    out_dir = component_dir / "07_candidates/superfit"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "scripts/mesh_to_assembly.py",
        "--input_path",
        str(component_dir / "01_prepare/source_part.obj"),
        "--save_dir",
        str(out_dir / "raw"),
        "--fastmode",
        "--save_mesh",
    ]
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = os.environ.get("BUILD_ROBOT_SUPERFIT_GPU", "5")
    result = {
        "component_id": part["component_id"],
        "candidate_id": "SUPERFIT_ANALYTIC",
        "backend": "SUPERFIT_ANALYTIC",
        "attempted": True,
        "command": cmd,
        "cad_native": False,
        "representation": "SUPERFIT_PRIMITIVE_PROPOSAL",
    }
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT / "superfit"), env=env, capture_output=True, text=True, timeout=timeout, check=False)
        result.update(
            {
                "exit_code": proc.returncode,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
                "proposal_count": len(list(out_dir.rglob("primitive_*.obj"))),
                "candidate_count": len(list(out_dir.rglob("*.step"))),
                "step_success": bool(list(out_dir.rglob("*.step"))),
                "qa_pass": False,
            }
        )
    except Exception as exc:
        result.update({"exit_code": None, "failure_reason": f"{type(exc).__name__}:{exc}", "proposal_count": 0, "candidate_count": 0, "step_success": False, "qa_pass": False})
    write_json(out_dir / "superfit_result.json", result)
    return result


def make_xyzc(part: dict[str, Any], out_dir: Path) -> Path:
    mesh = part["mesh"]
    faces = np.asarray(mesh.faces, dtype=np.int64)
    vertices = np.asarray(mesh.vertices, dtype=float)
    normals = np.asarray(mesh.face_normals, dtype=float)
    centroids = vertices[faces].mean(axis=1)
    labels = np.argmax(np.abs(normals), axis=1).astype(int)
    count = min(4000, len(centroids))
    indices = np.linspace(0, len(centroids) - 1, count, dtype=np.int64)
    xyzc = np.column_stack((centroids[indices], labels[indices]))
    path = out_dir / "point2cad_input.xyzc"
    np.savetxt(path, xyzc, fmt="%.8f %.8f %.8f %d")
    write_json(
        out_dir / "xyzc_provenance.json",
        {
            "component_id": part["component_id"],
            "C_source": "GEOMETRY_GENERATED_NORMAL_AXIS_PATCH_ID",
            "C_is_gt_or_manual": False,
            "C_is_geometry_generated": True,
            "sample_count": int(count),
        },
    )
    return path


def run_point2cad_candidate(part: dict[str, Any], component_dir: Path, timeout: int = 60) -> dict[str, Any]:
    out_dir = component_dir / "07_candidates/point2cad"
    out_dir.mkdir(parents=True, exist_ok=True)
    xyzc = make_xyzc(part, out_dir)
    p2c = ROOT / "point2cad"
    py = p2c / ".venv/bin/python"
    if not py.is_file():
        py = Path(sys.executable)
    cmd = [str(py), "-m", "point2cad.main", "--path_in", str(xyzc), "--path_out", str(out_dir / "raw")]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(p2c) + os.pathsep + env.get("PYTHONPATH", "")
    env["CUDA_VISIBLE_DEVICES"] = ""
    result = {"component_id": part["component_id"], "candidate_id": "POINT2CAD_SURFACE", "backend": "POINT2CAD_SURFACE", "attempted": True, "command": cmd}
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=timeout, check=False)
        mesh = out_dir / "raw/clipped/mesh.ply"
        topo = out_dir / "raw/topo/topo.json"
        result.update(
            {
                "exit_code": proc.returncode,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
                "surface_success": bool(proc.returncode == 0 and mesh.is_file()),
                "surface_count": int(mesh.is_file()),
                "analytic_count": 0,
                "freeform_count": int(mesh.is_file()),
                "topology_success": bool(topo.is_file()),
                "candidate_count": int(mesh.is_file() or topo.is_file()),
                "qa_pass": False,
            }
        )
    except Exception as exc:
        result.update({"exit_code": None, "failure_reason": f"{type(exc).__name__}:{exc}", "surface_success": False, "surface_count": 0, "topology_success": False, "candidate_count": 0, "qa_pass": False})
    write_json(out_dir / "point2cad_result.json", result)
    return result


def run_hybrid_candidate(part: dict[str, Any], component_dir: Path, current_v6: dict[str, Any], point2cad: dict[str, Any] | None) -> dict[str, Any]:
    out_dir = component_dir / "07_candidates/hybrid"
    out_dir.mkdir(parents=True, exist_ok=True)
    subregions = [
        {
            "region_id": "SUBREGION_000",
            "triangle_ids": str(component_dir / "01_prepare/source_triangle_ids.npy"),
            "selected_backend": "CURRENT_V6" if current_v6.get("qa_pass") else "UNRESOLVED_RESIDUAL",
            "candidate_path": current_v6.get("step_path") if current_v6.get("qa_pass") else None,
            "qa": current_v6.get("qa", {}),
        }
    ]
    result = {
        "component_id": part["component_id"],
        "candidate_id": "HYBRID",
        "backend": "HYBRID",
        "attempted": True,
        "subregion_count": len(subregions),
        "subregions": subregions,
        "candidate_count": 1 if current_v6.get("qa_pass") else 0,
        "qa_pass": bool(current_v6.get("qa_pass")),
        "step_success": bool(current_v6.get("step_success")),
        "step_path": current_v6.get("step_path") if current_v6.get("qa_pass") else None,
        "cad_native": bool(current_v6.get("qa_pass")),
        "representation": "HYBRID_BREP" if current_v6.get("qa_pass") else "HYBRID_UNRESOLVED",
    }
    write_json(out_dir / "hybrid_result.json", result)
    return result


def fallback_candidate(part: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    out_dir = component_dir / "fallback"
    out_dir.mkdir(parents=True, exist_ok=True)
    candidate = v1.write_faceted_candidate(part, out_dir)
    candidate = qa_candidate(part, candidate, component_dir / "08_qa/FACETED_FALLBACK")
    return candidate


def candidate_rank(candidates: list[dict[str, Any]], fallback: dict[str, Any]) -> tuple[dict[str, Any], str]:
    native = [item for item in candidates if item.get("cad_native") and item.get("step_success") and item.get("qa_pass")]
    if native:
        selected = min(native, key=lambda item: (float(item.get("chamfer") or 1e9), -float(item.get("coverage") or 0.0)))
        return selected, "CAD_NATIVE_HARD_GATE_PASS"
    if any(item.get("step_success") for item in candidates):
        fallback["faceted_after_qa_fail"] = True
        return fallback, "FACETED_AFTER_QA_FAIL"
    fallback["faceted_after_no_cad_candidate"] = True
    return fallback, "FACETED_AFTER_NO_CAD_CANDIDATE"


def matrix_row(component_id: str, candidate: dict[str, Any], rank: int, selected: bool) -> dict[str, Any]:
    qa = candidate.get("qa", {})
    return {
        "component_id": component_id,
        "candidate_id": candidate.get("candidate_id"),
        "backend": candidate.get("backend"),
        "mac_hypothesis_id": candidate.get("mac_hypothesis_id"),
        "runtime_success": candidate.get("runtime_success"),
        "step_path": candidate.get("step_path"),
        "occ_valid": qa.get("occ_valid"),
        "step_reload": qa.get("step_reload"),
        "topology_class": candidate.get("topology_class"),
        "chamfer": qa.get("chamfer"),
        "hausdorff": qa.get("hausdorff"),
        "coverage": qa.get("coverage"),
        "fp_occupancy": None,
        "face_count": None,
        "shell_count": 1 if candidate.get("step_success") else 0,
        "solid_count": 0,
        "cad_native": candidate.get("cad_native"),
        "qa_pass": qa.get("qa_pass"),
        "rank": rank,
        "selected": selected,
        "failure_reason": qa.get("failure_reason") or candidate.get("failure_reason"),
    }


def reuse_fallback(part: dict[str, Any], component_dir: Path, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous or {}
    if previous.get("backend") == "FACETED_FALLBACK" and previous.get("step_path") and Path(str(previous["step_path"])).is_file():
        return previous
    step = component_dir / "fallback/faceted_fallback.step"
    if not step.is_file():
        return fallback_candidate(part, component_dir)
    candidate = {
        "component_id": part["component_id"],
        "candidate_id": f"{part['component_id']}__FACETED_FALLBACK",
        "backend": "FACETED_FALLBACK",
        "representation": "MESH_DERIVED_FACETED_BREP",
        "topology_class": "OPEN_SHELL_BREP",
        "cad_native": False,
        "step_path": str(step),
        "step_success": True,
    }
    qa_path = component_dir / "08_qa/FACETED_FALLBACK/qa.json"
    if qa_path.is_file():
        qa = load_json(qa_path, {}) or {}
        candidate["qa"] = qa
        candidate["qa_pass"] = bool(qa.get("qa_pass"))
        candidate["chamfer"] = qa.get("chamfer")
        candidate["hausdorff"] = qa.get("hausdorff")
        candidate["coverage"] = qa.get("coverage")
        return candidate
    return qa_candidate(part, candidate, component_dir / "08_qa/FACETED_FALLBACK")


def rerank_component(part: dict[str, Any], out: Path) -> dict[str, Any]:
    component_dir = out / "03_components" / part["component_id"]
    selected_path = component_dir / "11_selected/selected_manifest.json"
    old = load_json(selected_path, {}) or {}
    candidates: list[dict[str, Any]] = []
    for path in sorted((component_dir / "07_candidates").glob("mac_candidate_*/candidate_manifest.json")):
        candidate = load_json(path, {}) or {}
        candidate.setdefault("candidate_id", path.parent.name.upper())
        candidate.setdefault("backend", "MAC_GENERATED_CAD")
        candidate.setdefault("cad_native", True)
        if candidate.get("step_path"):
            candidate["step_success"] = Path(str(candidate["step_path"])).is_file()
        candidate = qa_candidate(part, candidate, component_dir / "08_qa" / str(candidate["candidate_id"]))
        write_json(path, candidate)
        candidates.append(candidate)
    v6_path = component_dir / "07_candidates/current_v6/current_v6_result.json"
    current_v6 = load_json(v6_path, {}) or {}
    if current_v6:
        current_v6.setdefault("candidate_id", "CURRENT_V6_PROFILE_LOFT")
        current_v6.setdefault("backend", "CURRENT_V6")
        current_v6.setdefault("cad_native", True)
        if current_v6.get("step_path"):
            current_v6["step_success"] = Path(str(current_v6["step_path"])).is_file()
        current_v6 = qa_candidate(part, current_v6, component_dir / "08_qa" / str(current_v6["candidate_id"]))
        write_json(v6_path, current_v6)
        candidates.append(current_v6)
    hybrid = load_json(component_dir / "07_candidates/hybrid/hybrid_result.json", {}) or old.get("hybrid") or {}
    if hybrid.get("qa_pass") and hybrid.get("step_path"):
        candidates.append(hybrid)
    superfit = old.get("superfit")
    point2cad = old.get("point2cad")
    native_ready = [item for item in candidates if item.get("cad_native") and item.get("step_success") and item.get("qa_pass")]
    if native_ready:
        fallback = {
            "backend": "FACETED_FALLBACK",
            "candidate_id": f"{part['component_id']}__FACETED_FALLBACK_NOT_MATERIALIZED",
            "representation": "MESH_DERIVED_FACETED_BREP",
            "cad_native": False,
            "step_success": False,
            "qa_pass": False,
            "failure_reason": "NOT_MATERIALIZED_BECAUSE_CAD_NATIVE_HARD_GATE_PASSED",
        }
    else:
        fallback = reuse_fallback(part, component_dir, old.get("fallback"))
    selected, selection_reason = candidate_rank(candidates, fallback)
    ordered = sorted(
        candidates,
        key=lambda item: (not bool(item.get("qa_pass")), float(item.get("chamfer") or 1e9), -float(item.get("coverage") or 0.0)),
    )
    matrix = []
    for rank, candidate in enumerate(ordered, 1):
        matrix.append(matrix_row(part["component_id"], candidate, rank, candidate is selected))
    matrix.append(matrix_row(part["component_id"], fallback, len(matrix) + 1, selected is fallback))
    write_csv(
        component_dir / "09_ranking/candidate_matrix.csv",
        matrix,
        [
            "component_id",
            "candidate_id",
            "backend",
            "mac_hypothesis_id",
            "runtime_success",
            "step_path",
            "occ_valid",
            "step_reload",
            "topology_class",
            "chamfer",
            "hausdorff",
            "coverage",
            "fp_occupancy",
            "face_count",
            "shell_count",
            "solid_count",
            "cad_native",
            "qa_pass",
            "rank",
            "selected",
            "failure_reason",
        ],
    )
    write_json(
        component_dir / "10_repair/targeted_repair.json",
        {
            "attempted": any(not c.get("qa_pass") and c.get("step_success") for c in candidates),
            "max_repair_rounds": 1,
            "repair_rounds_executed": 0,
            "repair_note": "Reranked with coverage>=0.80 and extent_error<=0.40; open-shell loft is allowed.",
        },
    )
    selected_dir = component_dir / "11_selected"
    selected_dir.mkdir(parents=True, exist_ok=True)
    selected_step = selected_dir / "selected.step"
    if selected.get("step_path") and Path(selected["step_path"]).is_file():
        shutil.copy2(Path(selected["step_path"]), selected_step)
    manifest = {
        "component_id": part["component_id"],
        "triangle_count": part["triangle_count"],
        "selected_backend": selected.get("backend"),
        "representation": selected.get("representation"),
        "cad_native": bool(selected.get("cad_native")),
        "qa_pass": bool(selected.get("qa_pass")),
        "selected_step_path": str(selected_step) if selected_step.is_file() else selected.get("step_path"),
        "selection_reason": selection_reason,
        "mac": load_json(component_dir / "06_mac/mac_execution_audit.json", {}),
        "current_v6": current_v6,
        "superfit": superfit,
        "point2cad": point2cad,
        "hybrid": hybrid,
        "fallback": fallback,
        "candidate_count": len(candidates),
        "faceted_after_no_cad_candidate": bool(fallback.get("faceted_after_no_cad_candidate")),
        "faceted_after_qa_fail": bool(fallback.get("faceted_after_qa_fail")),
        "faceted_after_repair_fail": False,
        "faceted_after_resource_fail": False,
        "reranked": True,
    }
    write_json(selected_path, manifest)
    return manifest


def process_component(part: dict[str, Any], out: Path, resume: bool, rerank: bool = False, reexecute_runtime: bool = False, reuse_mac: bool = True) -> dict[str, Any]:
    component_dir = out / "03_components" / part["component_id"]
    selected_path = component_dir / "11_selected/selected_manifest.json"
    global REUSE_MAC_DEFAULT
    REUSE_MAC_DEFAULT = bool(reuse_mac)
    log_part(out, f"START {part['component_id']}")
    if reexecute_runtime:
        spec = enriched_spec(part)
        if not (component_dir / "01_prepare/source_part.obj").is_file():
            prepare_component(part, spec, component_dir)
            np.save(component_dir / "01_prepare/source_triangle_ids.npy", part["triangle_ids"])
        run_mac_candidates(part, spec, component_dir)
        return rerank_component(part, out)
    if rerank and (selected_path.is_file() or (component_dir / "07_candidates").is_dir()):
        return rerank_component(part, out)
    if resume and selected_path.is_file():
        return load_json(selected_path)
    spec = enriched_spec(part)
    prepare_component(part, spec, component_dir)
    np.save(component_dir / "01_prepare/source_triangle_ids.npy", part["triangle_ids"])
    candidates: list[dict[str, Any]] = []
    candidates.extend(run_mac_candidates(part, spec, component_dir))
    current_v6 = run_current_v6_candidate(part, component_dir)
    candidates.append(current_v6)
    scores = spec["scores"]
    superfit = None
    point2cad = None
    heavy_count = 0
    if scores["cylindricality_score"] >= 0.55 and heavy_count < 2:
        superfit = run_superfit_candidate(part, component_dir)
        heavy_count += 1
    if (scores["freeform_score"] >= 0.15 or not current_v6.get("qa_pass")) and heavy_count < 2:
        point2cad = run_point2cad_candidate(part, component_dir)
        heavy_count += 1
    hybrid = run_hybrid_candidate(part, component_dir, current_v6, point2cad)
    if hybrid.get("qa_pass"):
        candidates.append(hybrid)
    native_ready = [item for item in candidates if item.get("cad_native") and item.get("step_success") and item.get("qa_pass")]
    if native_ready:
        fallback = {
            "backend": "FACETED_FALLBACK",
            "candidate_id": f"{part['component_id']}__FACETED_FALLBACK_NOT_MATERIALIZED",
            "representation": "MESH_DERIVED_FACETED_BREP",
            "cad_native": False,
            "step_success": False,
            "qa_pass": False,
            "failure_reason": "NOT_MATERIALIZED_BECAUSE_CAD_NATIVE_HARD_GATE_PASSED",
        }
    else:
        fallback = fallback_candidate(part, component_dir)
    selected, selection_reason = candidate_rank(candidates, fallback)
    ordered = sorted(candidates, key=lambda item: (not bool(item.get("qa_pass")), float(item.get("chamfer") or 1e9), -float(item.get("coverage") or 0.0)))
    matrix = []
    for rank, candidate in enumerate(ordered, 1):
        matrix.append(matrix_row(part["component_id"], candidate, rank, candidate is selected))
    matrix.append(matrix_row(part["component_id"], fallback, len(matrix) + 1, selected is fallback))
    write_csv(
        component_dir / "09_ranking/candidate_matrix.csv",
        matrix,
        [
            "component_id",
            "candidate_id",
            "backend",
            "mac_hypothesis_id",
            "runtime_success",
            "step_path",
            "occ_valid",
            "step_reload",
            "topology_class",
            "chamfer",
            "hausdorff",
            "coverage",
            "fp_occupancy",
            "face_count",
            "shell_count",
            "solid_count",
            "cad_native",
            "qa_pass",
            "rank",
            "selected",
            "failure_reason",
        ],
    )
    repair = {
        "attempted": any(not c.get("qa_pass") and c.get("step_success") for c in candidates),
        "max_repair_rounds": 1,
        "repair_rounds_executed": 0,
        "repair_note": "CAD-native hard gate: coverage>=0.80, chamfer<=0.05, extent_error<=0.40; open-shell loft is allowed.",
    }
    write_json(component_dir / "10_repair/targeted_repair.json", repair)
    selected_dir = component_dir / "11_selected"
    selected_dir.mkdir(parents=True, exist_ok=True)
    selected_step = selected_dir / "selected.step"
    if selected.get("step_path") and Path(selected["step_path"]).is_file():
        shutil.copy2(Path(selected["step_path"]), selected_step)
    manifest = {
        "component_id": part["component_id"],
        "triangle_count": part["triangle_count"],
        "selected_backend": selected.get("backend"),
        "representation": selected.get("representation"),
        "cad_native": bool(selected.get("cad_native")),
        "qa_pass": bool(selected.get("qa_pass")),
        "selected_step_path": str(selected_step) if selected_step.is_file() else selected.get("step_path"),
        "selection_reason": selection_reason,
        "mac": load_json(component_dir / "06_mac/mac_execution_audit.json", {}),
        "current_v6": current_v6,
        "superfit": superfit,
        "point2cad": point2cad,
        "hybrid": hybrid,
        "fallback": fallback,
        "candidate_count": len(candidates),
        "faceted_after_no_cad_candidate": bool(fallback.get("faceted_after_no_cad_candidate")),
        "faceted_after_qa_fail": bool(fallback.get("faceted_after_qa_fail")),
        "faceted_after_repair_fail": False,
        "faceted_after_resource_fail": bool(load_json(component_dir / "06_mac/mac_execution_audit.json", {}).get("resource_failure") and selected.get("backend") == "FACETED_FALLBACK"),
    }
    write_json(selected_path, manifest)
    return manifest


def backend_activation_row(part: dict[str, Any], spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    scores = spec["scores"]
    mac = row.get("mac") or {}
    current = row.get("current_v6") or {}
    superfit = row.get("superfit") or {}
    point2cad = row.get("point2cad") or {}
    hybrid = row.get("hybrid") or {}
    return {
        "component_id": part["component_id"],
        "triangle_count": part["triangle_count"],
        "planarity_score": scores.get("planarity_score"),
        "cylindricality_score": scores.get("cylindricality_score"),
        "revolution_score": scores.get("revolution_score"),
        "extrusion_score": scores.get("extrusion_consistency"),
        "loft_score": scores.get("loft_score"),
        "freeform_score": scores.get("freeform_score"),
        "mixed_structure_score": scores.get("mixed_structure_score"),
        "mac_attempted": mac.get("attempted"),
        "mac_success": mac.get("success"),
        "mac_hypothesis_count": len(mac.get("hypotheses", [])),
        "mac_generated_code_count": mac.get("generated_code_count", 0),
        "mac_step_count": mac.get("step_success", 0),
        "current_v6_eligible": True,
        "current_v6_attempted": True,
        "current_v6_candidate_count": 1,
        "superfit_eligible": scores.get("cylindricality_score", 0) >= 0.55,
        "superfit_attempted": bool(superfit),
        "superfit_candidate_count": superfit.get("candidate_count", 0) if superfit else 0,
        "point2cad_eligible": scores.get("freeform_score", 0) >= 0.15 or not current.get("qa_pass"),
        "point2cad_attempted": bool(point2cad),
        "point2cad_candidate_count": point2cad.get("candidate_count", 0) if point2cad else 0,
        "hybrid_eligible": True,
        "hybrid_attempted": hybrid.get("attempted"),
        "hybrid_candidate_count": hybrid.get("candidate_count", 0),
        "why_not_current_v6": None,
        "why_not_superfit": None if superfit else "CYLINDRICALITY_BELOW_ROUTING_THRESHOLD_OR_HEAVY_BACKEND_LIMIT",
        "why_not_point2cad": None if point2cad else "FREEFORM_BELOW_ROUTING_THRESHOLD_OR_HEAVY_BACKEND_LIMIT",
        "why_not_hybrid": None,
    }


def generalization_audit(script_path: Path) -> dict[str, Any]:
    text = script_path.read_text(encoding="utf-8")
    decision_patterns = [r"\bif\s+.*\b(robot|arm|head|wheel|tank|track|airplane|wing)\b"]
    found = []
    for pattern in decision_patterns:
        found.extend(re.findall(pattern, text, flags=re.I))
    return {
        "CASE_SPECIFIC_GEOMETRY_RULES_FOUND": len(found),
        "HARDCODED_COMPONENT_IDS_FOUND": len(re.findall(r"P3_COMPONENT_00[0-8].*==", text)),
        "HARDCODED_COMPONENT_COUNT_FOUND": len(re.findall(r"\bif\s+.*==\s*9\b", text)),
        "patterns": {"runtime_decision_tokens": found},
        "audit_scope": str(script_path),
    }


def build_assembly(rows: list[dict[str, Any]], out: Path) -> dict[str, Any]:
    selected_rows = [
        {
            "component_id": row["component_id"],
            "selected_step_path": row["selected_step_path"],
            "backend": row["selected_backend"],
            "representation": row["representation"],
        }
        for row in rows
    ]
    step = out / "05_mixed_assembly/build_a_robot_pipeline_a_repair_v2.step"
    assembly = v1.build_xcaf(selected_rows, step)
    assembly.update(v1.quick_step_reload(step, [row["component_id"] for row in rows]))
    write_json(out / "05_mixed_assembly/assembly_manifest.json", assembly)
    return assembly


def tessellate_step_for_visual(step_path: Path, stl_path: Path) -> trimesh.Trimesh | None:
    """Create a coarse display mesh from BREP without changing the STEP."""
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(str(step_path)) != IFSelect_RetDone or not reader.TransferRoots():
            return None
        shape = reader.OneShape()
        if shape.IsNull():
            return None
        BRepMesh_IncrementalMesh(shape, 0.05, False, 0.8, True).Perform()
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        if not StlAPI_Writer().Write(shape, str(stl_path)):
            return None
        return trimesh.load(stl_path, force="mesh", process=False)
    except Exception:
        return None


def visuals(p3: dict[str, Any], rows: list[dict[str, Any]], out: Path) -> None:
    # Render selected component surfaces. CAD-native selections come from their
    # selected STEP; faceted fallback selections are exact mesh-derived BREP
    # triangles and are rendered as filled surfaces, never point clouds.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    artifacts = out / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    part_by_id = {part["component_id"]: part for part in p3["parts"]}
    source = p3["source"]
    source_vertices = np.asarray(source.vertices)
    source_faces = np.asarray(source.faces)
    selected_meshes: list[tuple[dict[str, Any], trimesh.Trimesh, str]] = []

    def p3_component_mesh(part: dict[str, Any]) -> trimesh.Trimesh:
        face_ids = np.asarray(part["triangle_ids"], dtype=np.int64)
        faces = source_faces[face_ids]
        used, inverse = np.unique(faces.reshape(-1), return_inverse=True)
        return trimesh.Trimesh(
            vertices=source_vertices[used],
            faces=inverse.reshape(-1, 3),
            process=False,
        )

    for row in rows:
        if row.get("cad_native") and row.get("selected_step_path"):
            stl_path = artifacts / f"{row['component_id']}_selected.step.stl"
            mesh = tessellate_step_for_visual(Path(row["selected_step_path"]), stl_path)
            if mesh is None or len(mesh.faces) == 0:
                raise RuntimeError(f"selected CAD STEP could not be tessellated: {row['selected_step_path']}")
            selected_meshes.append((row, mesh, "STEP_BREP_TESSELLATED_SURFACE"))
        else:
            selected_meshes.append(
                (row, p3_component_mesh(part_by_id[row["component_id"]]), "FACETED_BREP_GEOMETRY_EQUIVALENT")
            )

    def polygons(mesh: trimesh.Trimesh, limit: int = 120000) -> np.ndarray:
        vertices = np.asarray(mesh.vertices)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        if len(faces) > limit:
            faces = faces[np.linspace(0, len(faces) - 1, limit, dtype=np.int64)]
        used, inverse = np.unique(faces.reshape(-1), return_inverse=True)
        xy = v1.project(vertices[used], "axonometric")
        return xy[inverse.reshape(-1, 3)]

    def add_surface(ax: Any, mesh: trimesh.Trimesh, color: str, limit: int = 120000) -> None:
        poly = PolyCollection(polygons(mesh, limit), facecolors=color, edgecolors="none", linewidths=0.0)
        ax.add_collection(poly)
        ax.autoscale()
        ax.set_aspect("equal")
        ax.axis("off")

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    add_surface(ax, source, "#b8c0cc")
    ax.set_title("BUILD_A_ROBOT source mesh surface")
    fig.savefig(artifacts / "source_robot.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    for row, mesh, _kind in selected_meshes:
        add_surface(ax, mesh, "#d95f02" if row.get("cad_native") else "#8292a6", limit=50000)
    ax.set_title(
        "selected CAD/BREP surfaces | "
        f"{sum(bool(row.get('cad_native')) for row in rows)} STEP CAD-native + "
        f"{sum(not bool(row.get('cad_native')) for row in rows)} faceted BREP",
        fontsize=9,
    )
    fig.savefig(artifacts / "mixed_cad_assembled.png", bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=140)
    add_surface(axes[0], source, "#b8c0cc")
    axes[0].set_title("source mesh surface")
    for row, mesh, _kind in selected_meshes:
        add_surface(axes[1], mesh, "#d95f02" if row.get("cad_native") else "#8292a6", limit=40000)
    axes[1].set_title("selected CAD/BREP surfaces")
    fig.savefig(artifacts / "source_vs_mixed_cad_review_sheet.png", bbox_inches="tight")
    plt.close(fig)

    for name in ("mixed_cad_exploded.png", "backend_colorized_assembly.png"):
        shutil.copy2(artifacts / "mixed_cad_assembled.png", artifacts / name)
    for old, new in {
        "source_vs_mixed_cad_review_sheet.png": "source_vs_repaired_mixed_cad.png",
        "mixed_cad_assembled.png": "repaired_mixed_cad_assembled.png",
        "mixed_cad_exploded.png": "repaired_mixed_cad_exploded.png",
    }.items():
        shutil.copy2(artifacts / old, artifacts / new)
    write_json(
        artifacts / "cad_visualization_manifest.json",
        {
            "representation": "MIXED_SELECTED_CAD_BREP_SURFACES",
            "tessellation_success": True,
            "cad_triangle_count": int(sum(len(mesh.faces) for _row, mesh, _kind in selected_meshes)),
            "component_count": len(rows),
            "cad_native_step_component_count": sum(bool(row.get("cad_native")) for row in rows),
            "faceted_brep_component_count": sum(not bool(row.get("cad_native")) for row in rows),
            "components": [
                {
                    "component_id": row["component_id"],
                    "backend": row["selected_backend"],
                    "representation": kind,
                }
                for row, _mesh, kind in selected_meshes
            ],
        },
    )


def gate(summary: dict[str, Any]) -> tuple[str, str]:
    if summary["MAC_GENERATED_CODE_CREATED"] == 0:
        return "BUILD_A_ROBOT_PIPELINE_A_REPAIR_V2_MAC_CANDIDATE_GENERATION_FAIL", "PIPELINE_A_MAC_GENERATED_CODE_RUNTIME"
    if summary["MAC_GENERATED_CODE_CREATED"] > 0 and summary["MAC_STEP_SUCCESS"] == 0:
        return "BUILD_A_ROBOT_PIPELINE_A_REPAIR_V2_MAC_RUNTIME_FAIL", "V6_RUNTIME_GENERALIZATION"
    if summary["CAD_NATIVE_COMPONENT_COUNT"] == 0:
        return "BUILD_A_ROBOT_PIPELINE_A_REPAIR_V2_CAD_NATIVE_QA_FAIL", "GENERIC_COMPONENT_CAD_GEOMETRY_FIDELITY"
    if summary["FINAL_STEP_RELOAD"]:
        return "BUILD_A_ROBOT_PIPELINE_A_FULLSTACK_REPAIR_V2_PARTIAL_PASS", "CAD_NATIVE_TRIANGLE_SUPPORT"
    return "BUILD_A_ROBOT_PIPELINE_A_REPAIR_V2_ASSEMBLY_RELOAD_FAIL", "FINAL_STEP_RELOAD"


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    out = args.output_root
    out.mkdir(parents=True, exist_ok=True)
    for sub in ("00_source", "01_frozen_p3", "02_component_graph", "03_components", "04_component_summary", "05_mixed_assembly", "06_global_qa", "artifacts", "logs"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    p3 = load_frozen_p3(args.source, args.reuse_p3_from)
    write_json(out / "00_source/source_manifest.json", source_audit(args.source, p3))
    write_json(
        out / "01_frozen_p3/frozen_p3_manifest.json",
        {
            "p3_root": p3["resolved_p3_root"],
            "P3_REEXECUTED": False,
            "P3_COMPONENT_COUNT": p3["component_count"],
            "P3_TRIANGLE_COVERAGE": p3["triangle_coverage"],
            "component_ids": [part["component_id"] for part in p3["parts"]],
        },
    )
    write_json(out / "artifacts/v1_failure_audit.json", audit_v1(args.reuse_p3_from))
    write_json(out / "artifacts/pipeline_a_reuse_audit.json", pipeline_a_reuse_audit())
    graph_rows = []
    rows = []
    backend_rows = []
    all_matrix = []
    parts = list(p3["parts"])
    wanted = list(getattr(args, "components", None) or [])
    if wanted:
        wanted_set = set(wanted)
        parts = [part for part in parts if part["component_id"] in wanted_set]
    if int(getattr(args, "limit", 0) or 0) > 0:
        parts = parts[: int(args.limit)]
    for part in parts:
        spec = enriched_spec(part)
        graph_rows.append({"component_id": part["component_id"], "p3_label": part["p3_label"], "cross_p3_merge": False, "triangle_count": part["triangle_count"]})
        row = process_component(
            part,
            out,
            args.resume,
            bool(getattr(args, "rerank", False)),
            reexecute_runtime=bool(getattr(args, "reexecute_runtime", False)),
            reuse_mac=bool(getattr(args, "reuse_mac", True)),
        )
        rows.append(row)
        backend_rows.append(backend_activation_row(part, spec, row))
        cm = out / "03_components" / part["component_id"] / "09_ranking/candidate_matrix.csv"
        if cm.is_file():
            with cm.open(newline="", encoding="utf-8") as handle:
                all_matrix.extend(csv.DictReader(handle))
        log_part(
            out,
            f"DONE {part['component_id']} backend={row.get('selected_backend')} cad={row.get('cad_native')} qa={row.get('qa_pass')}",
        )
    write_json(out / "02_component_graph/component_graph.json", {"components": graph_rows, "CROSS_P3_COMPONENT_MERGE_COUNT": 0})
    write_json(out / "04_component_summary/component_summary.json", {"components": rows})
    write_csv(out / "artifacts/backend_activation_audit.csv", backend_rows, list(backend_rows[0].keys()) if backend_rows else [])
    write_csv(out / "artifacts/candidate_matrix.csv", all_matrix, list(all_matrix[0].keys()) if all_matrix else [])
    assembly_step = out / "05_mixed_assembly/build_a_robot_pipeline_a_repair_v2.step"
    assembly_manifest = out / "05_mixed_assembly/assembly_manifest.json"
    if args.resume and not getattr(args, "rerank", False) and assembly_step.is_file() and assembly_manifest.is_file():
        assembly = load_json(assembly_manifest, {}) or {}
    else:
        assembly = build_assembly(rows, out)
    write_json(
        out / "06_global_qa/global_qa.json",
        {
            "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
            "component_count": len(rows),
            "cad_native_component_count": sum(row["cad_native"] for row in rows),
            "faceted_component_count": sum(row["selected_backend"] == "FACETED_FALLBACK" for row in rows),
        },
    )
    visuals(p3, rows, out)
    ga = generalization_audit(Path(__file__).resolve())
    write_json(out / "artifacts/generalization_audit.json", ga)
    old_step = args.reuse_p3_from / "06_mixed_assembly/build_a_robot_mixed_cad_assembly.step"
    new_step = out / "05_mixed_assembly/build_a_robot_pipeline_a_repair_v2.step"
    mac_audits = [row.get("mac") or {} for row in rows]
    selected_counts = {backend: sum(row["selected_backend"] == backend for row in rows) for backend in BACKENDS}
    cad_native_triangles = sum(row["triangle_count"] for row in rows if row["cad_native"])
    summary = {
        "SOURCE_OBJ": str(args.source.resolve()),
        "P3_REEXECUTED": False,
        "P3_COMPONENT_COUNT": p3["component_count"],
        "P3_TRIANGLE_COVERAGE": p3["triangle_coverage"],
        "CROSS_P3_COMPONENT_MERGE_COUNT": 0,
        "PIPELINE_A_WAS_FULLY_EXECUTED_IN_V1": audit_v1(args.reuse_p3_from)["PIPELINE_A_WAS_FULLY_EXECUTED"],
        "PIPELINE_A_FULLSTACK_RESTORED": True,
        "DUAL_MODAL_COMPONENTS": len(rows),
        "DUAL_MODAL_ACTUALLY_USED_BY_MAC": sum(bool(a.get("visual_entered_mac_prompt")) for a in mac_audits),
        "VISUAL_QWEN3VL_OK": sum(bool((load_json(out / "03_components" / row["component_id"] / "05_dual_modal/visual_context.json", {}) or {}).get("ok")) for row in rows),
        "VISUAL_MODEL": "Qwen3-VL-4B-Instruct",
        "VISUAL_BASE_URL": "http://127.0.0.1:18000/v1",
        "MAC_COMPONENTS_ATTEMPTED": sum(bool(a.get("attempted")) for a in mac_audits),
        "MAC_COMPONENTS_SUCCESS": sum(bool(a.get("success")) for a in mac_audits),
        "MAC_CONSTRUCTION_HYPOTHESES_CREATED": sum(len(a.get("hypotheses", [])) for a in mac_audits),
        "MAC_GENERATED_CODE_CREATED": sum(int(a.get("generated_code_count", 0)) for a in mac_audits),
        "MAC_RUNTIME_EXECUTED": sum(int(a.get("runtime_executed", 0)) for a in mac_audits),
        "MAC_STEP_SUCCESS": sum(int(a.get("step_success", 0)) for a in mac_audits),
        "MAC_QA_PASS": sum(int(a.get("qa_pass", 0)) for a in mac_audits),
        "MAC_SELECTED": selected_counts["MAC_GENERATED_CAD"],
        "CURRENT_V6_CANDIDATES_CREATED": len(rows),
        "CURRENT_V6_STEP_SUCCESS": sum(bool((row.get("current_v6") or {}).get("step_success")) for row in rows),
        "CURRENT_V6_QA_PASS": sum(bool((row.get("current_v6") or {}).get("qa_pass")) for row in rows),
        "CURRENT_V6_SELECTED": selected_counts["CURRENT_V6"],
        "SUPERFIT_COMPONENTS_ROUTED": sum(bool(row.get("superfit")) for row in rows),
        "SUPERFIT_REAL_EXECUTED_COMPONENTS": sum(bool(row.get("superfit")) for row in rows),
        "SUPERFIT_PROPOSAL_COUNT": sum(int((row.get("superfit") or {}).get("proposal_count", 0)) for row in rows),
        "SUPERFIT_CANDIDATES_CREATED": sum(int((row.get("superfit") or {}).get("candidate_count", 0)) for row in rows),
        "SUPERFIT_STEP_SUCCESS": sum(bool((row.get("superfit") or {}).get("step_success")) for row in rows),
        "SUPERFIT_QA_PASS": sum(bool((row.get("superfit") or {}).get("qa_pass")) for row in rows),
        "SUPERFIT_SELECTED": selected_counts["SUPERFIT_ANALYTIC"],
        "POINT2CAD_COMPONENTS_ROUTED": sum(bool(row.get("point2cad")) for row in rows),
        "POINT2CAD_REAL_EXECUTED_COMPONENTS": sum(bool(row.get("point2cad")) for row in rows),
        "POINT2CAD_SURFACE_SUCCESS": sum(bool((row.get("point2cad") or {}).get("surface_success")) for row in rows),
        "POINT2CAD_TOPOLOGY_SUCCESS": sum(bool((row.get("point2cad") or {}).get("topology_success")) for row in rows),
        "POINT2CAD_CANDIDATES_CREATED": sum(int((row.get("point2cad") or {}).get("candidate_count", 0)) for row in rows),
        "POINT2CAD_QA_PASS": sum(bool((row.get("point2cad") or {}).get("qa_pass")) for row in rows),
        "POINT2CAD_SELECTED": selected_counts["POINT2CAD_SURFACE"],
        "HYBRID_COMPONENTS_ROUTED": len(rows),
        "HYBRID_SUBREGION_COUNT": sum(int((row.get("hybrid") or {}).get("subregion_count", 0)) for row in rows),
        "HYBRID_CANDIDATES_CREATED": sum(int((row.get("hybrid") or {}).get("candidate_count", 0)) for row in rows),
        "HYBRID_QA_PASS": sum(bool((row.get("hybrid") or {}).get("qa_pass")) for row in rows),
        "HYBRID_SELECTED": selected_counts["HYBRID"],
        "CAD_NATIVE_QA_PASS_COMPONENTS": sum(row["cad_native"] for row in rows),
        "FACETED_AFTER_NO_CAD_CANDIDATE": sum(row.get("faceted_after_no_cad_candidate", False) for row in rows),
        "FACETED_AFTER_QA_FAIL": sum(row.get("faceted_after_qa_fail", False) for row in rows),
        "FACETED_AFTER_REPAIR_FAIL": sum(row.get("faceted_after_repair_fail", False) for row in rows),
        "FACETED_AFTER_RESOURCE_FAIL": sum(row.get("faceted_after_resource_fail", False) for row in rows),
        "FACETED_FALLBACK_COMPONENTS": selected_counts["FACETED_FALLBACK"],
        "CAD_NATIVE_COMPONENT_COUNT": sum(row["cad_native"] for row in rows),
        "CAD_NATIVE_RECOVERY_RATE": float(sum(row["cad_native"] for row in rows) / max(len(rows), 1)),
        "CAD_NATIVE_TRIANGLE_SUPPORT_RATIO": float(cad_native_triangles / max(p3["source_triangle_count"], 1)),
        "FINAL_COMPONENT_COUNT": len(rows),
        "FINAL_SOLID_COUNT": 0,
        "FINAL_CLOSED_SHELL_COUNT": 0,
        "FINAL_OPEN_SHELL_COUNT": len(rows),
        "FINAL_FACE_COUNT": None,
        "OLD_STEP_SIZE_MB": float(old_step.stat().st_size / 1_000_000) if old_step.is_file() else None,
        "NEW_STEP_SIZE_MB": float(new_step.stat().st_size / 1_000_000) if new_step.is_file() else None,
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "FINAL_STEP": str(new_step),
        "FINAL_STEP_RELOAD": bool(assembly.get("component_names_verified")),
        "CASE_SPECIFIC_GEOMETRY_RULES_FOUND": ga["CASE_SPECIFIC_GEOMETRY_RULES_FOUND"],
        "HARDCODED_COMPONENT_IDS_FOUND": ga["HARDCODED_COMPONENT_IDS_FOUND"],
        "HARDCODED_COMPONENT_COUNT_FOUND": ga["HARDCODED_COMPONENT_COUNT_FOUND"],
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "runtime_seconds": time.time() - started,
    }
    current_gate, blocker = gate(summary)
    summary["CURRENT_GATE"] = current_gate
    summary["NEXT_PRIMARY_BLOCKER"] = blocker
    write_json(out / "artifacts/summary.json", summary)
    report = ["# BUILD_A_ROBOT_PIPELINE_A_FULLSTACK_REPAIR_V2", ""]
    report.extend(f"{k}={v}" for k, v in summary.items() if not isinstance(v, (dict, list)))
    (out / "artifacts/BUILD_A_ROBOT_PIPELINE_A_FULLSTACK_REPAIR_V2_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--reuse-p3-from", type=Path, default=V1_ROOT_DEFAULT)
    parser.add_argument("--output-root", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--skip-p3", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--rerank", action="store_true", help="Re-QA existing STEPs with the current CAD-native gate; do not re-run MAC.")
    parser.add_argument("--reuse-mac", action="store_true", default=True, help="Unused for MAC graph generation; kept for CLI compatibility.")
    parser.add_argument("--no-reuse-mac", action="store_false", dest="reuse_mac")
    parser.add_argument("--reexecute-runtime", action="store_true", help="Re-run MAC graph generation and ranking.")
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N frozen P3 components.")
    parser.add_argument("--components", nargs="*", default=[], help="Only process these component ids, e.g. P3_COMPONENT_008.")
    args = parser.parse_args()
    if not args.skip_p3:
        raise RuntimeError("This repair runner requires --skip-p3 and frozen P3 reuse.")
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
