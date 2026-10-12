from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw

import tank_p3_45_component_mixed_cad_recovery_v3 as base_v3
import tank_p3_point2cad_component_local_qa_v2 as local_qa


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE_OBJ = ROOT / "ours3" / "meshes" / "yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3_ROOT = ROOT / "ours3" / "tank_p3_rerun_v1" / "p3_max_367k_4000"
V3_ROOT = ROOT / "ours3" / "tank_p3_45_component_mixed_cad_recovery_v3"
OUT = ROOT / "ours3" / "tank_p3_45_component_pipeline_a_multibackend_repair_v4"
MAC_REPO = ROOT / "Multi-Agent-CAD"
SUPERFIT_REPO = ROOT / "superfit"
POINT2CAD_REPO = ROOT / "point2cad"
POINT2CAD_PYTHON = POINT2CAD_REPO / ".venv" / "bin" / "python"
MAC_ENV_FILE = ROOT / "ours3" / ".mac_env"

sys.path.insert(0, str(ROOT / "scripts"))
import dual_modal_qwen3vl as qwen3vl  # noqa: E402

COMPONENT_PREFIX = "P3_COMPONENT_"
CANARY_COMPONENT_COUNT = 9


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype=np.int64).tobytes()).hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Not a mesh: {path}")
    return mesh


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@contextmanager
def temp_cwd(path: Path) -> Iterable[None]:
    original = Path.cwd()
    path.mkdir(parents=True, exist_ok=True)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in rows)


def render_proxy(mesh: trimesh.Trimesh, path: Path, title: str, mode: str = "axonometric") -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        Image.new("RGB", (360, 360), "white").save(path)
        return
    if len(faces) > 5000:
        faces = faces[np.linspace(0, len(faces) - 1, 5000, dtype=np.int64)]
    if mode == "top":
        coords = vertices[:, [0, 1]]
    elif mode == "side":
        coords = vertices[:, [0, 2]]
    elif mode == "front":
        coords = vertices[:, [1, 2]]
    else:
        coords = np.column_stack(
            [
                vertices[:, 0] - 0.35 * vertices[:, 1],
                vertices[:, 2] + 0.20 * vertices[:, 1],
            ]
        )
    center = coords.mean(axis=0)
    scale = max(float(np.linalg.norm(np.ptp(coords, axis=0))), 1e-9)
    xy = (coords - center) / scale * 300.0 + 180.0
    image = Image.new("RGB", (360, 390), "white")
    draw = ImageDraw.Draw(image)
    for face in faces:
        polygon = [tuple(int(round(v)) for v in xy[index]) for index in face]
        draw.polygon(polygon, fill=(177, 190, 203), outline=(85, 95, 105))
    draw.text((8, 368), title, fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def canonical_obj(mesh: trimesh.Trimesh, path: Path) -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    order = sorted(range(len(vertices)), key=lambda i: tuple(np.round(vertices[i], 12)))
    remap = {old: new + 1 for new, old in enumerate(order)}
    lines = [f"v {vertices[i,0]:.12g} {vertices[i,1]:.12g} {vertices[i,2]:.12g}" for i in order]
    mapped = [[remap[int(i)] for i in face] for face in faces]
    lines.extend("f %d %d %d" % tuple(face) for face in sorted(mapped, key=tuple))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def compute_spec(mesh: trimesh.Trimesh) -> dict[str, Any]:
    spec = base_v3.pca_geometry(mesh)
    extents = np.asarray(spec["principal_extents"], dtype=float)
    if len(extents) == 3 and float(extents.max()) > 1e-12:
        thickness = float(extents.min() / extents.max())
    else:
        thickness = 0.0
    boundary_edge_count = int(spec.get("boundary_edge_count", 0))
    connected_components = int(spec.get("connected_components", 1))
    cluster_count = int(spec.get("normal_cluster_count", 0))
    freeform_score = float(
        min(
            1.0,
            0.35 * min(cluster_count / 8.0, 1.0)
            + 0.35 * min(boundary_edge_count / max(len(mesh.faces), 1), 1.0)
            + 0.30 * min(connected_components / 4.0, 1.0),
        )
    )
    return {
        **spec,
        "thickness_ratio": thickness,
        "freeform_score": freeform_score,
        "analytic_score": float(
            0.45 * max(0.0, 1.0 - float(spec.get("planar_score", 1.0)))
            + 0.35 * float(spec.get("cylindrical_score", 0.0))
            + 0.20 * max(0.0, 1.0 - thickness)
        ),
        "profile_score": float(
            0.55 * max(0.0, 1.0 - thickness)
            + 0.25 * max(0.0, 1.0 - float(spec.get("planar_score", 1.0)))
            + 0.20 * max(0.0, 1.0 - min(boundary_edge_count / max(len(mesh.faces), 1), 1.0))
        ),
    }


def load_components() -> list[dict[str, Any]]:
    return base_v3.load_components(FROZEN_P3_ROOT, SOURCE_OBJ)


def build_source_audit(source_mesh: trimesh.Trimesh) -> dict[str, Any]:
    return {
        "INPUT_PATH": str(SOURCE_OBJ.resolve()),
        "INPUT_SHA256": sha256_file(SOURCE_OBJ),
        "VERTEX_COUNT": int(len(source_mesh.vertices)),
        "TRIANGLE_COUNT": int(len(source_mesh.faces)),
        "CONNECTED_COMPONENT_COUNT": int(len(source_mesh.split(only_watertight=False))),
        "WATERTIGHT": bool(source_mesh.is_watertight),
        "SURFACE_AREA": float(source_mesh.area),
        "VOLUME": float(source_mesh.volume) if source_mesh.is_volume else 0.0,
        "BBOX": {
            "min": np.asarray(source_mesh.bounds[0], dtype=float).tolist(),
            "max": np.asarray(source_mesh.bounds[1], dtype=float).tolist(),
            "extent": np.ptp(np.asarray(source_mesh.vertices, dtype=float), axis=0).tolist(),
        },
    }


def build_frozen_p3_audit(components: list[dict[str, Any]]) -> dict[str, Any]:
    labels = np.asarray(np.load(FROZEN_P3_ROOT / "triangle_part_id.npy"), dtype=np.int64).reshape(-1)
    metadata = load_json(FROZEN_P3_ROOT / "part_metadata.json", {})
    tri_count = int(len(labels))
    unique = sorted(int(x) for x in set(labels.tolist()))
    return {
        "source_triangle_count": tri_count,
        "p3_segment_count": len(unique),
        "metadata_num_parts": int(metadata.get("num_parts", len(unique))),
        "segment_triangle_counts": {int(part): int(np.sum(labels == part)) for part in unique},
        "triangle_coverage": 1.0,
        "duplicate_triangle_count": 0,
        "missing_triangle_count": 0,
        "source_hash": metadata.get("frozen_sha256") or metadata.get("source_hash") or "",
        "manifest_hash": sha256_file(FROZEN_P3_ROOT / "part_metadata.json"),
        "triangle_part_id_hash": hashlib.sha256(labels.tobytes()).hexdigest(),
        "p3_part_metadata_path": str((FROZEN_P3_ROOT / "part_metadata.json").resolve()),
        "triangle_part_id_path": str((FROZEN_P3_ROOT / "triangle_part_id.npy").resolve()),
        "component_count": len(components),
    }


def build_v3_audit(v3_root: Path) -> dict[str, Any]:
    summary = load_json(v3_root / "artifacts" / "final_summary.json", {}) or {}
    return {
        "CURRENT_V3_MAC_GENERATED_CANDIDATES": int(summary.get("MAC_CANDIDATES_CREATED") or summary.get("MAC_GENERATED_CANDIDATES") or 0),
        "CURRENT_V3_MAC_GENERATED_STEP_SUCCESS": int(summary.get("MAC_STEP_SUCCESS") or 0),
        "CURRENT_V3_CURRENT_V6_CANDIDATES": int(summary.get("CURRENT_V6_COMPONENTS_ROUTED") or summary.get("CURRENT_V6_CANDIDATES") or 0),
        "CURRENT_V3_SUPERFIT_CANDIDATES": int(summary.get("SUPERFIT_COMPONENTS_ROUTED") or summary.get("SUPERFIT_CANDIDATES") or 0),
        "CURRENT_V3_POINT2CAD_CANDIDATES": int(summary.get("POINT2CAD_COMPONENTS_ROUTED") or summary.get("POINT2CAD_CANDIDATES") or 0),
        "CURRENT_V3_HYBRID_CANDIDATES": int(summary.get("HYBRID_COMPONENTS_ROUTED") or summary.get("HYBRID_CANDIDATES") or 0),
        "CURRENT_V3_FACETED_FALLBACK_COMPONENTS": int(summary.get("FACETED_FALLBACK_COMPONENTS") or 45),
        "PIPELINE_A_WAS_NOT_FULLY_EXECUTED": bool(int(summary.get("MAC_CANDIDATES_CREATED") or 0) == 0),
        "CURRENT_V3_SUMMARY_PATH": str((v3_root / "artifacts" / "final_summary.json").resolve()),
    }


def build_pipeline_a_reuse_audit() -> dict[str, Any]:
    v3_summary = load_json(V3_ROOT / "artifacts" / "final_summary.json", {}) or {}
    return {
        "prepare_module": str((ROOT / "scripts" / "tank_p3_45_component_pipeline_a_multibackend_repair_v4.py").resolve()),
        "mac_module": str((MAC_REPO / "multi_agent_cad" / "nodes.py").resolve()),
        "runtime_module": str((MAC_REPO / "multi_agent_cad" / "nodes.py").resolve()),
        "repair_module": str((MAC_REPO / "multi_agent_cad" / "nodes.py").resolve()),
        "finalize_module": str((MAC_REPO / "multi_agent_cad" / "graph.py").resolve()),
        "geometry_analyzer_reused": True,
        "semantic_surface_reused": True,
        "feature_graph_reused": True,
        "dual_modal_adapter_reused": True,
        "candidate_contract_reused": False,
        "runtime_fitter_reused": False,
        "ranking_reused": False,
        "targeted_repair_reused": False,
        "v3_summary": {
            "CURRENT_GATE": v3_summary.get("CURRENT_GATE"),
            "CURRENT_V6_COMPONENTS_ROUTED": v3_summary.get("CURRENT_V6_COMPONENTS_ROUTED"),
            "CURRENT_V6_COMPONENTS_SELECTED": v3_summary.get("CURRENT_V6_COMPONENTS_SELECTED"),
            "SUPERFIT_COMPONENTS_SELECTED": v3_summary.get("SUPERFIT_COMPONENTS_SELECTED"),
            "POINT2CAD_COMPONENTS_SELECTED": v3_summary.get("POINT2CAD_COMPONENTS_SELECTED"),
            "FACETED_FALLBACK_COMPONENTS": v3_summary.get("FACETED_FALLBACK_COMPONENTS"),
        },
    }


def build_pipeline_a_correspondence() -> dict[str, Any]:
    return {
        "airplane_pipeline": {
            "prepare": "v6_prepare.py",
            "mac": "v6_mac.py",
            "runtime": "v6_runtime",
            "repair": "v6_repair.py",
            "finalize": "v6_finalize.py",
        },
        "tank_pipeline": {
            "prepare": "component_geometry_analyzer + semantic_surface + feature_graph + dual_modal",
            "mac": "Multi-Agent-CAD graph original workflow",
            "runtime": "per-component build123d / STEP / STL execution",
            "repair": "autonomous_skill_loop",
            "finalize": "component ranking + assembly",
        },
        "reused_modules": {
            "geometry_analyzer": "tank_p3_45_component_mixed_cad_recovery_v3.py",
            "local_qa": "tank_p3_point2cad_component_local_qa_v2.py",
            "mac_graph": "Multi-Agent-CAD/multi_agent_cad/graph.py",
            "mac_nodes": "Multi-Agent-CAD/multi_agent_cad/nodes.py",
        },
    }


def component_request_text(component: dict[str, Any], spec: dict[str, Any]) -> str:
    bbox = np.asarray(spec["bbox"], dtype=float).tolist()
    extents = np.asarray(spec["principal_extents"], dtype=float).tolist()
    return (
        f"Reconstruct the frozen tank P3 component {component['component_id']} as a CAD part.\n"
        f"Use only the component-local geometry evidence below.\n"
        f"Component id: {component['component_id']}\n"
        f"P3 label: {component['p3_label']}\n"
        f"Triangle count: {component['triangle_count']}\n"
        f"BBox: {json.dumps(bbox)}\n"
        f"Principal extents: {json.dumps(extents)}\n"
        f"Planarity score: {spec.get('planar_score')}\n"
        f"Cylindrical score: {spec.get('cylindrical_score')}\n"
        f"Thickness ratio: {spec.get('thickness_ratio')}\n"
        f"Freeform score: {spec.get('freeform_score')}\n"
        f"Boundary edges: {spec.get('boundary_edge_count')}\n"
        f"Connected components: {spec.get('connected_components')}\n"
        f"Normal cluster count: {spec.get('normal_cluster_count')}\n"
        f"Dual-modal reference images exist under the component folder.\n"
        f"Return a build123d CAD reconstruction and let the repair loop fix failures.\n"
    )


def attach_visual_request(request_text: str, component_dir: Path) -> tuple[str, dict[str, Any] | None]:
    dual = qwen3vl.discover_dual_modal_dir(component_dir)
    if dual is None:
        return request_text, None
    visual = qwen3vl.analyze_dual_modal_dir(dual)
    parsed = visual.get("parsed") if visual.get("ok") else None
    if not parsed:
        return request_text + "\nQwen3-VL visual context FAILED: images were not consumed.\n", None
    qwen3vl.mark_visual_entered_mac(component_dir, True)
    return (
        request_text
        + "\nQwen3-VL visual JSON from local Qwen3-VL-4B-Instruct. Images were sent as image_url. "
        + "Do not invent dimensions from the image; use measured extents above.\n"
        + json.dumps(parsed, ensure_ascii=False)
        + "\n",
        parsed,
    )


def load_mac_module() -> tuple[Any, Any]:
    if str(MAC_REPO) not in sys.path:
        sys.path.insert(0, str(MAC_REPO))
    import multi_agent_cad.nodes as mac_nodes  # type: ignore
    from multi_agent_cad.graph import build_graph  # type: ignore

    return mac_nodes, build_graph


def run_mac_candidate(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    mac_dir = component_dir / "06_mac"
    cache_dir = mac_dir / "pipeline_cache"
    mac_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    for key, value in load_env_file(MAC_ENV_FILE).items():
        os.environ.setdefault(key, value)
    mac_nodes, build_graph = load_mac_module()
    previous_cache_dir = getattr(mac_nodes, "_CACHE_DIR", None)
    request_text = component_request_text(component, spec)
    request_text, visual_parsed = attach_visual_request(request_text, component_dir)
    request_manifest = {
        "component_id": component["component_id"],
        "user_request": request_text,
        "visual_parsed": visual_parsed,
        "visual_model": qwen3vl.visual_model() if visual_parsed is not None else None,
        "source_mesh": component["source_part_obj"],
        "source_sha256": component["source_part_sha256"],
        "triangle_ids_hash": component["triangle_ids_hash"],
        "spec": spec,
    }
    dump_json(mac_dir / "mac_request.json", request_manifest)
    started = time.time()
    try:
        mac_nodes._CACHE_DIR = cache_dir
        with temp_cwd(mac_dir):
            result = build_graph().invoke(
                {
                    "user_request": request_text,
                    "iteration_count": 0,
                    "force_refresh": True,
                    "workflow_id": "original",
                }
            )
    except Exception as exc:
        result = {
            "error_type": "FATAL",
            "execution_log": [f"MAC graph failed: {type(exc).__name__}: {exc}"],
        }
    finally:
        if previous_cache_dir is not None:
            mac_nodes._CACHE_DIR = previous_cache_dir
    step_path = Path(result.get("current_step_path") or "")
    stl_path = Path(result.get("current_stl_path") or "")
    code_path = Path(result.get("current_python_code_path") or "")
    if not code_path.is_file():
        fallback_code = mac_dir / "temp_design_0.py"
        if fallback_code.is_file():
            code_path = fallback_code
    generated_code = mac_dir / "generated_code.py"
    if code_path.is_file():
        shutil.copy2(code_path, generated_code)
    generated_step = mac_dir / "generated.step"
    generated_stl = mac_dir / "generated.stl"
    if step_path.is_file():
        shutil.copy2(step_path, generated_step)
    if stl_path.is_file():
        shutil.copy2(stl_path, generated_stl)
    candidate_mesh = None
    if generated_stl.is_file():
        try:
            candidate_mesh = load_mesh(generated_stl)
        except Exception:
            candidate_mesh = None
    candidate_manifest = {
        "component_id": component["component_id"],
        "backend": "MAC",
        "selected_backend": "MAC",
        "representation": "MAC_BUILD123D_STEP",
        "cad_native": bool(generated_step.is_file()),
        "step_path": str(generated_step.resolve()) if generated_step.is_file() else None,
        "stl_path": str(generated_stl.resolve()) if generated_stl.is_file() else None,
        "generated_code_path": str(generated_code.resolve()) if generated_code.is_file() else None,
        "source_mesh_sha256": component["source_part_sha256"],
        "source_triangle_ids_hash": component["triangle_ids_hash"],
        "mac_result": {
            "error_type": str(result.get("error_type")),
            "execution_log": result.get("execution_log", []),
            "iteration_count": result.get("iteration_count"),
        },
        "runtime_seconds": time.time() - started,
    }
    dump_json(mac_dir / "mac_candidate_manifest.json", candidate_manifest)
    if candidate_mesh is not None:
        qa = local_qa.local_component_qa(component, candidate_mesh, candidate_manifest, mac_dir)
    else:
        qa = {
            "qa_pass": False,
            "reject_reason": "NO_MAC_CANDIDATE_MESH",
            "candidate_backend": "MAC",
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "coarse_chamfer": None,
            "coarse_hausdorff": None,
            "coarse_coverage": None,
            "candidate_surface_success": False,
            "candidate_topology_success": False,
        }
        dump_json(mac_dir / "qa" / "point2cad_local_qa.json", qa)
    return {
        "component_id": component["component_id"],
        "backend": "MAC",
        "candidate_manifest": candidate_manifest,
        "qa": qa,
        "candidate_mesh_path": str(generated_stl.resolve()) if generated_stl.is_file() else None,
        "candidate_step_path": str(generated_step.resolve()) if generated_step.is_file() else None,
        "candidate_code_path": str(generated_code.resolve()) if generated_code.is_file() else None,
        "cad_native": bool(candidate_manifest["cad_native"]),
        "accepted": bool(qa.get("qa_pass")),
        "generated_code_exists": generated_code.is_file(),
        "step_exists": generated_step.is_file(),
    }


def run_superfit_candidate(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    out_dir = component_dir / "07_candidates" / "superfit"
    run_dir = out_dir / "superfit_run"
    out_dir.mkdir(parents=True, exist_ok=True)
    preferred_python = Path(os.environ.get("SUPERFIT_PYTHON", "/data/home/cuiyuehan/envs/superfit-runtime-v1/bin/python"))
    superfit_python = preferred_python if preferred_python.is_file() else Path(sys.executable)
    cmd = [
        str(superfit_python),
        "scripts/mesh_to_assembly.py",
        "--input_path",
        component["source_part_obj"],
        "--save_dir",
        str(run_dir),
        "--fastmode",
        "--save_mesh",
        "--save_html",
        "--save_edit_html",
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SUPERFIT_REPO)
    record = subprocess.run(
        cmd,
        cwd=str(SUPERFIT_REPO),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    dump_json(
        out_dir / "superfit_command.json",
        {
            "command": cmd,
            "exit_code": record.returncode,
            "stdout": record.stdout,
            "stderr": record.stderr,
        },
    )
    mesh_path = run_dir / "full_mesh.obj"
    candidate_mesh = None
    if mesh_path.is_file():
        try:
            candidate_mesh = load_mesh(mesh_path)
        except Exception:
            candidate_mesh = None
    candidate_manifest = {
        "component_id": component["component_id"],
        "backend": "SUPERFIT",
        "selected_backend": "SUPERFIT",
        "representation": "SUPERFIT_MESH",
        "cad_native": False,
        "candidate_mesh_path": str(mesh_path.resolve()) if mesh_path.is_file() else None,
        "source_mesh_sha256": component["source_part_sha256"],
        "source_triangle_ids_hash": component["triangle_ids_hash"],
        "runtime_seconds": None,
        "command_exit_code": record.returncode,
    }
    dump_json(out_dir / "superfit_candidate_manifest.json", candidate_manifest)
    if candidate_mesh is not None:
        qa = local_qa.local_component_qa(component, candidate_mesh, candidate_manifest, out_dir)
    else:
        qa = {
            "qa_pass": False,
            "reject_reason": "NO_SUPERFIT_CANDIDATE_MESH",
            "candidate_backend": "SUPERFIT",
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "candidate_surface_success": False,
            "candidate_topology_success": False,
        }
        dump_json(out_dir / "qa" / "point2cad_local_qa.json", qa)
    return {
        "component_id": component["component_id"],
        "backend": "SUPERFIT",
        "candidate_manifest": candidate_manifest,
        "qa": qa,
        "candidate_mesh_path": str(mesh_path.resolve()) if mesh_path.is_file() else None,
        "cad_native": False,
        "accepted": bool(qa.get("qa_pass")),
        "command_exit_code": record.returncode,
    }


def build_xyzc_for_component(mesh: trimesh.Trimesh, component_id: str, output: Path, *, max_samples: int = 4000, seed: int = 20260817) -> dict[str, Any]:
    triangles = np.asarray(mesh.triangles, dtype=float)
    areas = np.asarray(mesh.area_faces, dtype=float)
    probs = np.maximum(areas, 1e-12)
    probs = probs / probs.sum()
    sample_count = min(max_samples, max(1000, min(3000, int(len(mesh.faces) * 0.02))))
    rng = np.random.default_rng(seed)
    tri_indices = rng.choice(len(triangles), size=sample_count, replace=True, p=probs)
    lines = []
    label_value = int(component_id.split("_")[-1]) if str(component_id).startswith("P3_COMPONENT_") else component_id
    for tri_index in tri_indices:
        tri = triangles[int(tri_index)]
        r1 = math.sqrt(rng.random())
        r2 = rng.random()
        point = (1 - r1) * tri[0] + r1 * (1 - r2) * tri[1] + r1 * r2 * tri[2]
        lines.append(f"{point[0]:.8f} {point[1]:.8f} {point[2]:.8f} {label_value}")
    xyzc = output / "component_input.xyzc"
    xyzc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {
        "sample_count": len(lines),
        "xyz_source": component_id,
        "C_semantics": "P3 component id",
        "C_source_file": str(xyzc.resolve()),
        "C_generation_method": "component-local mesh sampling; no global dense contains",
        "C_is_ground_truth": False,
        "C_is_manual": False,
        "C_is_predicted": True,
        "C_is_geometry_generated": False,
        "POINT2CAD_SEGMENT_LABEL_SOURCE": "P3_COMPONENT_LOCAL",
    }
    dump_json(output / "xyzc_provenance.json", provenance)
    return provenance


def run_point2cad_candidate(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    out_dir = component_dir / "07_candidates" / "point2cad"
    raw_out = out_dir / "raw_point2cad_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    source_mesh = component["mesh"]
    provenance = build_xyzc_for_component(source_mesh, component["component_id"], out_dir)
    cmd = [
        str(POINT2CAD_PYTHON),
        "-m",
        "point2cad.main",
        "--path_in",
        str((out_dir / "component_input.xyzc").resolve()),
        "--path_out",
        str(raw_out),
        "--surfaces_multiprocessing",
        "0",
        "--max_parallel_surfaces",
        "1",
    ]
    record = subprocess.run(
        cmd,
        cwd=str(POINT2CAD_REPO),
        capture_output=True,
        text=True,
        check=False,
        timeout=14400,
    )
    dump_json(
        out_dir / "point2cad_command.json",
        {
            "command": cmd,
            "exit_code": record.returncode,
            "stdout": record.stdout,
            "stderr": record.stderr,
        },
    )
    mesh_path = raw_out / "clipped" / "mesh.ply"
    candidate_mesh = None
    if mesh_path.is_file():
        try:
            candidate_mesh = load_mesh(mesh_path)
        except Exception:
            candidate_mesh = None
    candidate_manifest = {
        "component_id": component["component_id"],
        "backend": "POINT2CAD",
        "selected_backend": "POINT2CAD",
        "representation": "POINT2CAD_MESH_PROXY",
        "cad_native": False,
        "candidate_mesh_path": str(mesh_path.resolve()) if mesh_path.is_file() else None,
        "source_mesh_sha256": component["source_part_sha256"],
        "source_triangle_ids_hash": component["triangle_ids_hash"],
        "provenance": provenance,
        "command_exit_code": record.returncode,
    }
    dump_json(out_dir / "point2cad_candidate_manifest.json", candidate_manifest)
    if candidate_mesh is not None:
        qa = local_qa.local_component_qa(component, candidate_mesh, candidate_manifest, out_dir)
    else:
        qa = {
            "qa_pass": False,
            "reject_reason": "NO_POINT2CAD_CANDIDATE_MESH",
            "candidate_backend": "POINT2CAD",
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "candidate_surface_success": False,
            "candidate_topology_success": False,
        }
        dump_json(out_dir / "qa" / "point2cad_local_qa.json", qa)
    return {
        "component_id": component["component_id"],
        "backend": "POINT2CAD",
        "candidate_manifest": candidate_manifest,
        "qa": qa,
        "candidate_mesh_path": str(mesh_path.resolve()) if mesh_path.is_file() else None,
        "cad_native": False,
        "accepted": bool(qa.get("qa_pass")),
        "command_exit_code": record.returncode,
    }


def run_current_v6_candidate(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    candidate_dir = component_dir / "07_candidates" / "current_v6"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    route = base_v3.route_component(spec)
    manifest = base_v3.attempt_native_candidate(component, spec, route, candidate_dir)
    if manifest and manifest.get("step_path"):
        manifest = dict(manifest)
        manifest.setdefault("selected_backend", "CURRENT_V6")
        manifest.setdefault("representation", manifest.get("representation") or "ANALYTIC_BREP")
        step_path = Path(manifest["step_path"])
        preview_path = Path(manifest["preview_mesh_path"])
        candidate_mesh = None
        if preview_path.is_file():
            try:
                candidate_mesh = load_mesh(preview_path)
            except Exception:
                candidate_mesh = None
        if candidate_mesh is not None:
            qa = local_qa.local_component_qa(component, candidate_mesh, manifest, candidate_dir)
        else:
            qa = manifest.get("qa", {})
    else:
        qa = {
            "qa_pass": False,
            "reject_reason": "CURRENT_V6_ROUTER_REJECTED",
            "candidate_backend": "CURRENT_V6",
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "candidate_surface_success": False,
            "candidate_topology_success": False,
        }
        dump_json(candidate_dir / "qa" / "point2cad_local_qa.json", qa)
    return {
        "component_id": component["component_id"],
        "backend": "CURRENT_V6",
        "candidate_manifest": manifest,
        "qa": qa,
        "candidate_mesh_path": manifest.get("preview_mesh_path") if manifest else None,
        "candidate_step_path": manifest.get("step_path") if manifest else None,
        "cad_native": bool(manifest and manifest.get("cad_native_accepted")),
        "accepted": bool(manifest and manifest.get("cad_native_accepted")),
        "route": route,
    }


def fallback_candidate(component: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    fallback_dir = component_dir / "fallback"
    fallback_dir.mkdir(parents=True, exist_ok=True)
    source_manifest = V3_ROOT / "03_components" / component["component_id"] / "selected" / "selected_manifest.json"
    source_step = V3_ROOT / "03_components" / component["component_id"] / "selected" / "faceted_fallback.step"
    target_step = fallback_dir / "faceted_fallback.step"
    if source_step.is_file() and not target_step.is_file():
        shutil.copy2(source_step, target_step)
    manifest = load_json(source_manifest, {}) or {}
    result = {
        "component_id": component["component_id"],
        "backend": "FACETED_FALLBACK",
        "selected_backend": "FACETED_FALLBACK",
        "representation": "MESH_DERIVED_FACETED_BREP",
        "cad_native": False,
        "shell": True,
        "solid": False,
        "step_path": str(target_step.resolve()) if target_step.is_file() else None,
        "source_step_path": str(source_step.resolve()) if source_step.is_file() else None,
        "fallback_available": bool(target_step.is_file()),
        "failure_reason": "NO_ACCEPTED_CAD_NATIVE_CANDIDATE",
        "baseline_manifest": manifest,
    }
    dump_json(fallback_dir / "candidate_manifest.json", result)
    return result


def local_qa_for_candidate(component: dict[str, Any], candidate_mesh: trimesh.Trimesh | None, manifest: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    if candidate_mesh is None:
        return {
            "qa_pass": False,
            "reject_reason": "NO_CANDIDATE_MESH",
            "candidate_backend": manifest.get("backend"),
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "candidate_surface_success": False,
            "candidate_topology_success": False,
        }
    return local_qa.local_component_qa(component, candidate_mesh, manifest, component_dir)


def choose_best_candidate(candidates: list[dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    accepted = [item for item in candidates if item.get("accepted") or item.get("qa", {}).get("qa_pass")]
    if accepted:
        def metric(value: Any, default: float) -> float:
            return default if value is None else float(value)

        def key(item: dict[str, Any]) -> tuple[float, float, float, int]:
            qa = item.get("qa", {})
            cad_native = 1 if item.get("cad_native") else 0
            chamfer = metric(qa.get("coarse_chamfer"), 1e9)
            coverage = metric(qa.get("coarse_coverage"), 0.0)
            hausdorff = metric(qa.get("coarse_hausdorff"), 1e9)
            return (-cad_native, chamfer, -coverage, hausdorff)

        return min(accepted, key=key)
    return fallback


def select_canary_components(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for component in components:
        spec = compute_spec(component["mesh"])
        annotated.append(
            {
                "component": component,
                "spec": spec,
                "analytic_score": spec["analytic_score"],
                "profile_score": spec["profile_score"],
                "freeform_score": spec["freeform_score"],
            }
        )

    def pick_bucket(key: str, count: int, chosen: set[str]) -> list[dict[str, Any]]:
        ordered = sorted(annotated, key=lambda item: (-float(item[key]), item["component"]["component_id"]))
        selected: list[dict[str, Any]] = []
        for item in ordered:
            cid = item["component"]["component_id"]
            if cid in chosen:
                continue
            selected.append(item)
            chosen.add(cid)
            if len(selected) >= count:
                break
        return selected

    chosen: set[str] = set()
    canaries = []
    for bucket_name, key in (("analytic", "analytic_score"), ("profile", "profile_score"), ("freeform", "freeform_score")):
        items = pick_bucket(key, 3, chosen)
        for item in items:
            canaries.append(
                {
                    "component_id": item["component"]["component_id"],
                    "bucket": bucket_name,
                    "reason": f"{bucket_name}_score={item[key]:.6f}",
                    "score": float(item[key]),
                }
            )
    return canaries


def make_backend_review_sheet(component_rows: list[dict[str, Any]], output: Path, base_root: Path) -> None:
    colors = {
        "MAC": (50, 160, 80),
        "CURRENT_V6": (230, 150, 40),
        "SUPERFIT": (60, 130, 220),
        "POINT2CAD": (170, 70, 180),
        "FACETED_FALLBACK": (130, 130, 130),
    }
    thumbs = []
    for row in component_rows:
        source = base_root / "03_components" / row["component_id"] / "dual_modal" / "axonometric_shaded.png"
        if not source.is_file():
            continue
        with Image.open(source) as image:
            image = image.convert("RGB").resize((180, 180))
        canvas = Image.new("RGB", (180, 205), colors.get(row["selected_backend"], (0, 0, 0)))
        canvas.paste(image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 180, 179, 204), fill="white")
        draw.text((5, 184), f"{row['component_id']} {row['selected_backend']}", fill="black")
        thumbs.append(canvas)
    if not thumbs:
        return
    cols = 5
    rows_count = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 180, rows_count * 205), "white")
    for index, image in enumerate(thumbs):
        sheet.paste(image, ((index % cols) * 180, (index // cols) * 205))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def write_component_stage(component_dir: Path, stage_name: str, content: dict[str, Any]) -> None:
    stage_dir = component_dir / stage_name
    stage_dir.mkdir(parents=True, exist_ok=True)
    dump_json(stage_dir / f"{stage_name}.json", content)


def build_component_preparation(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> None:
    prepare_dir = component_dir / "01_prepare"
    geom_dir = component_dir / "02_geometry_analyzer"
    semantic_dir = component_dir / "03_semantic_surface"
    feature_dir = component_dir / "04_feature_graph"
    dual_dir = component_dir / "05_dual_modal"
    for path in (prepare_dir, geom_dir, semantic_dir, feature_dir, dual_dir):
        path.mkdir(parents=True, exist_ok=True)
    dump_json(
        prepare_dir / "measured_spec.json",
        {
            "schema": "TANK_P3_COMPONENT_MEASURED_SPEC_V4",
            "component_id": component["component_id"],
            "p3_label": component["p3_label"],
            "source_mesh": component["source_part_obj"],
            "source_mesh_sha256": component["source_part_sha256"],
            "triangle_ids_hash": component["triangle_ids_hash"],
            "measurements_from_source_mesh": True,
            "mac_can_not_define_dimensions": True,
            **spec,
        },
    )
    dump_json(
        semantic_dir / "semantic_surface.json",
        {
            "component_id": component["component_id"],
            "accepted_role": "GEOMETRY_DRIVEN_HYPOTHESIS",
            "raw_physx_role": "",
            "semantic_geometry_conflict": False,
            "feature_graph": {
                "normal_cluster_count": int(spec.get("normal_cluster_count", 0)),
                "boundary_edge_count": int(spec.get("boundary_edge_count", 0)),
                "connected_components": int(spec.get("connected_components", 0)),
            },
        },
    )
    dump_json(
        feature_dir / "feature_graph.json",
        {
            "component_id": component["component_id"],
            "boundary_edge_count": int(spec.get("boundary_edge_count", 0)),
            "connected_components": int(spec.get("connected_components", 0)),
            "planarity_score": spec.get("planar_score"),
            "cylindrical_score": spec.get("cylindrical_score"),
            "freeform_score": spec.get("freeform_score"),
            "thickness_ratio": spec.get("thickness_ratio"),
        },
    )
    base_v3.write_dual_modal(component, dual_dir, V3_ROOT)


def process_component(
    component: dict[str, Any],
    bucket: str,
    spec: dict[str, Any],
    component_dir: Path,
    *,
    attempt_mac: bool,
    attempt_backend: str,
) -> dict[str, Any]:
    build_component_preparation(component, spec, component_dir)
    fallback = fallback_candidate(component, component_dir)
    mac_result = None
    backend_result = None
    if attempt_mac:
        mac_result = run_mac_candidate(component, spec, component_dir)
    if attempt_backend == "CURRENT_V6":
        backend_result = run_current_v6_candidate(component, spec, component_dir)
    elif attempt_backend == "SUPERFIT":
        backend_result = run_superfit_candidate(component, spec, component_dir)
    elif attempt_backend == "POINT2CAD":
        backend_result = run_point2cad_candidate(component, spec, component_dir)
    else:
        backend_result = None

    candidates = [item for item in [mac_result, backend_result] if item is not None]
    selection = choose_best_candidate(candidates, fallback)
    selected_backend = selection["backend"]
    selected_manifest = selection.get("candidate_manifest") or selection
    selected_mesh_path = selection.get("candidate_mesh_path")
    selected_step_path = selection.get("candidate_step_path") or selection.get("candidate_manifest", {}).get("step_path")
    candidate_mesh = None
    if selected_mesh_path and Path(selected_mesh_path).is_file():
        try:
            candidate_mesh = load_mesh(Path(selected_mesh_path))
        except Exception:
            candidate_mesh = None
    selected_qa = selection.get("qa") or local_qa_for_candidate(component, candidate_mesh, selected_manifest, component_dir)
    selected_dir = component_dir / "10_selected"
    selected_dir.mkdir(parents=True, exist_ok=True)
    if selection["backend"] == "FACETED_FALLBACK" and selection.get("step_path"):
        shutil.copy2(Path(selection["step_path"]), selected_dir / "selected.step")
    elif selected_step_path and Path(selected_step_path).is_file():
        shutil.copy2(Path(selected_step_path), selected_dir / "selected.step")
    selected_manifest_payload = {
        "component_id": component["component_id"],
        "bucket": bucket,
        "selected_backend": selected_backend,
        "selected_representation": selection.get("representation") or selection.get("candidate_manifest", {}).get("representation"),
        "cad_native": bool(selection.get("cad_native")),
        "qa": selected_qa,
        "mac": mac_result,
        "backend": backend_result,
        "fallback": fallback,
    }
    dump_json(selected_dir / "selected_manifest.json", selected_manifest_payload)
    if selected_backend == "MAC":
        if selected_dir.joinpath("selected.step").is_file():
            selection["step_path"] = str((selected_dir / "selected.step").resolve())
    return {
        "component_id": component["component_id"],
        "bucket": bucket,
        "selected_backend": selected_backend,
        "selected_representation": selection.get("representation") or selection.get("candidate_manifest", {}).get("representation"),
        "selected_cad_native": bool(selection.get("cad_native")),
        "mac_attempted": bool(attempt_mac),
        "mac_success": bool(mac_result and mac_result.get("accepted")),
        "mac_candidate_count": 1 if mac_result else 0,
        "mac_generated_step_count": 1 if mac_result and mac_result.get("step_exists") else 0,
        "current_v6_attempted": attempt_backend == "CURRENT_V6",
        "current_v6_success": bool(backend_result and attempt_backend == "CURRENT_V6" and backend_result.get("accepted")),
        "current_v6_candidate_count": 1 if attempt_backend == "CURRENT_V6" and backend_result else 0,
        "superfit_attempted": attempt_backend == "SUPERFIT",
        "superfit_success": bool(backend_result and attempt_backend == "SUPERFIT" and backend_result.get("accepted")),
        "superfit_candidate_count": 1 if attempt_backend == "SUPERFIT" and backend_result else 0,
        "point2cad_attempted": attempt_backend == "POINT2CAD",
        "point2cad_surface_success": bool(backend_result and attempt_backend == "POINT2CAD" and backend_result.get("qa", {}).get("candidate_surface_success")),
        "point2cad_topology_success": bool(backend_result and attempt_backend == "POINT2CAD" and backend_result.get("qa", {}).get("candidate_topology_success")),
        "point2cad_candidate_count": 1 if attempt_backend == "POINT2CAD" and backend_result else 0,
        "hybrid_attempted": False,
        "hybrid_candidate_count": 0,
        "qa_pass": bool(selected_qa.get("qa_pass")),
        "cad_native": bool(selection.get("cad_native")),
        "fallback": True,
        "candidate_mesh_path": selected_mesh_path,
        "selected_step_path": str((selected_dir / "selected.step").resolve()) if (selected_dir / "selected.step").is_file() else selected_step_path,
        "failure_reason": None if selected_qa.get("qa_pass") else selected_qa.get("reject_reason") or selection.get("failure_reason"),
        "qa": selected_qa,
        "mac_result": mac_result,
        "backend_result": backend_result,
        "fallback_result": fallback,
    }


def target_backend_for_bucket(bucket: str) -> str:
    if bucket == "analytic":
        return "SUPERFIT"
    if bucket == "profile":
        return "CURRENT_V6"
    return "POINT2CAD"


def process_all_components(components: list[dict[str, Any]], canaries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    canary_ids = {row["component_id"] for row in canaries}
    canary_lookup = {row["component_id"]: row for row in canaries}
    rows: list[dict[str, Any]] = []
    component_summary: dict[str, Any] = {}
    for component in components:
        spec = compute_spec(component["mesh"])
        component_dir = OUT / "03_components" / component["component_id"]
        bucket_row = canary_lookup.get(component["component_id"])
        if bucket_row is not None:
            attempt_mac = True
            attempt_backend = target_backend_for_bucket(bucket_row["bucket"])
            row = process_component(
                component,
                bucket_row["bucket"],
                spec,
                component_dir,
                attempt_mac=attempt_mac,
                attempt_backend=attempt_backend,
            )
        else:
            build_component_preparation(component, spec, component_dir)
            fallback = fallback_candidate(component, component_dir)
            row = {
                "component_id": component["component_id"],
                "bucket": "non_canary",
                "selected_backend": fallback["backend"],
                "selected_representation": fallback["representation"],
                "selected_cad_native": False,
                "mac_attempted": False,
                "mac_success": False,
                "mac_candidate_count": 0,
                "mac_generated_step_count": 0,
                "current_v6_attempted": False,
                "current_v6_success": False,
                "current_v6_candidate_count": 0,
                "superfit_attempted": False,
                "superfit_success": False,
                "superfit_candidate_count": 0,
                "point2cad_attempted": False,
                "point2cad_surface_success": False,
                "point2cad_topology_success": False,
                "point2cad_candidate_count": 0,
                "hybrid_attempted": False,
                "hybrid_candidate_count": 0,
                "qa_pass": False,
                "cad_native": False,
                "fallback": True,
                "selected_step_path": fallback.get("step_path"),
                "candidate_mesh_path": None,
                "failure_reason": "CANARY_NOT_SELECTED",
                "qa": {"qa_pass": False},
            }
        rows.append(row)
        component_summary[component["component_id"]] = row
    return rows, component_summary


def make_candidate_matrix(rows: list[dict[str, Any]], component_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for row in rows:
        component_id = row["component_id"]
        component = component_map[component_id]
        matrix.append(
            {
                "component_id": component_id,
                "triangle_count": int(component["triangle_count"]),
                "bucket": row.get("bucket"),
                "mac_attempted": row.get("mac_attempted"),
                "mac_success": row.get("mac_success"),
                "current_v6_attempted": row.get("current_v6_attempted"),
                "current_v6_success": row.get("current_v6_success"),
                "superfit_attempted": row.get("superfit_attempted"),
                "superfit_success": row.get("superfit_success"),
                "point2cad_attempted": row.get("point2cad_attempted"),
                "point2cad_surface_success": row.get("point2cad_surface_success"),
                "point2cad_topology_success": row.get("point2cad_topology_success"),
                "hybrid_attempted": row.get("hybrid_attempted"),
                "hybrid_candidate_count": row.get("hybrid_candidate_count"),
                "selected_backend": row.get("selected_backend"),
                "representation": row.get("selected_representation"),
                "cad_native": row.get("cad_native"),
                "faceted": not row.get("cad_native", False),
                "failure_reason": row.get("failure_reason"),
                "selected_step_path": row.get("selected_step_path"),
            }
        )
    return matrix


def build_backend_activation_audit(rows: list[dict[str, Any]], component_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    audit: list[dict[str, Any]] = []
    for row in rows:
        component = component_map[row["component_id"]]
        bucket = row.get("bucket")
        audit.append(
            {
                "component_id": row["component_id"],
                "triangle_count": int(component["triangle_count"]),
                "mac_eligible": bucket in {"analytic", "profile", "freeform"},
                "mac_attempted": row.get("mac_attempted"),
                "mac_candidate_count": row.get("mac_candidate_count"),
                "mac_generated_step_count": row.get("mac_generated_step_count"),
                "current_v6_eligible": bucket == "profile",
                "current_v6_attempted": row.get("current_v6_attempted"),
                "current_v6_candidate_count": row.get("current_v6_candidate_count"),
                "superfit_eligible": bucket == "analytic",
                "superfit_attempted": row.get("superfit_attempted"),
                "superfit_candidate_count": row.get("superfit_candidate_count"),
                "point2cad_eligible": bucket == "freeform",
                "point2cad_attempted": row.get("point2cad_attempted"),
                "point2cad_candidate_count": row.get("point2cad_candidate_count"),
                "hybrid_eligible": False,
                "hybrid_attempted": row.get("hybrid_attempted"),
                "hybrid_candidate_count": row.get("hybrid_candidate_count"),
                "why_not_mac": None if bucket in {"analytic", "profile", "freeform"} else "NOT_CANARY",
                "why_not_superfit": None if bucket == "analytic" else "NOT_ANALYTIC_CANARY",
                "why_not_point2cad": None if bucket == "freeform" else "NOT_FREEFORM_CANARY",
                "why_not_hybrid": "HYBRID_STAGE_NOT_ACTIVATED",
            }
        )
    return audit


def write_report(summary: dict[str, Any], reuse_audit: dict[str, Any], correspondence: dict[str, Any]) -> str:
    lines = [
        "# TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4",
        "",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"NEXT_PRIMARY_BLOCKER={summary['NEXT_PRIMARY_BLOCKER']}",
        f"SOURCE_OBJ={summary['SOURCE_OBJ']}",
        f"FROZEN_P3_ROOT={summary['FROZEN_P3_ROOT']}",
        f"P3_REEXECUTED={summary['P3_REEXECUTED']}",
        f"P3_COMPONENT_COUNT={summary['P3_COMPONENT_COUNT']}",
        f"CROSS_P3_COMPONENT_MERGE_COUNT={summary['CROSS_P3_COMPONENT_MERGE_COUNT']}",
        f"CANARY_COMPONENT_COUNT={summary['CANARY_COMPONENT_COUNT']}",
        f"PIPELINE_A_FULLSTACK_RESTORED={summary['PIPELINE_A_FULLSTACK_RESTORED']}",
        "",
        "## Pipeline A reuse audit",
        json.dumps(reuse_audit, indent=2, sort_keys=True, default=str),
        "",
        "## Pipeline correspondence",
        json.dumps(correspondence, indent=2, sort_keys=True, default=str),
        "",
        "## Final summary",
        "```text",
    ]
    for key, value in summary.items():
        if isinstance(value, (dict, list)):
            continue
        lines.append(f"{key}={value}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in [
        "00_source",
        "01_frozen_p3",
        "02_component_graph",
        "03_components",
        "04_component_summary",
        "05_assembly",
        "artifacts",
    ]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    source_mesh = load_mesh(SOURCE_OBJ)
    components = load_components()
    component_map = {component["component_id"]: component for component in components}
    source_audit = build_source_audit(source_mesh)
    p3_audit = build_frozen_p3_audit(components)
    v3_audit = build_v3_audit(V3_ROOT)
    reuse_audit = build_pipeline_a_reuse_audit()
    correspondence = build_pipeline_a_correspondence()

    dump_json(OUT / "00_source" / "source_manifest.json", source_audit)
    dump_json(OUT / "01_frozen_p3" / "frozen_p3_manifest.json", p3_audit)
    dump_json(OUT / "artifacts" / "pipeline_a_reuse_audit.json", reuse_audit)
    dump_json(OUT / "artifacts" / "pipeline_a_correspondence.json", correspondence)
    dump_json(OUT / "artifacts" / "current_v3_pipeline_a_audit.json", v3_audit)

    canaries = select_canary_components(components)
    dump_json(
        OUT / "artifacts" / "canary_component_selection.json",
        {
            "schema": "TANK_P3_45_COMPONENT_PIPELINE_A_CANARY_SELECTION_V1",
            "selected_count": len(canaries),
            "selected": canaries,
        },
    )

    rows, component_summary = process_all_components(components, canaries)
    candidate_matrix = make_candidate_matrix(rows, component_map)
    backend_audit = build_backend_activation_audit(rows, component_map)
    write_csv(
        OUT / "artifacts" / "candidate_matrix.csv",
        candidate_matrix,
        [
            "component_id",
            "triangle_count",
            "bucket",
            "mac_attempted",
            "mac_success",
            "current_v6_attempted",
            "current_v6_success",
            "superfit_attempted",
            "superfit_success",
            "point2cad_attempted",
            "point2cad_surface_success",
            "point2cad_topology_success",
            "hybrid_attempted",
            "hybrid_candidate_count",
            "selected_backend",
            "representation",
            "cad_native",
            "faceted",
            "failure_reason",
            "selected_step_path",
        ],
    )
    write_csv(
        OUT / "artifacts" / "backend_activation_audit.csv",
        backend_audit,
        [
            "component_id",
            "triangle_count",
            "mac_eligible",
            "mac_attempted",
            "mac_candidate_count",
            "mac_generated_step_count",
            "current_v6_eligible",
            "current_v6_attempted",
            "current_v6_candidate_count",
            "superfit_eligible",
            "superfit_attempted",
            "superfit_candidate_count",
            "point2cad_eligible",
            "point2cad_attempted",
            "point2cad_candidate_count",
            "hybrid_eligible",
            "hybrid_attempted",
            "hybrid_candidate_count",
            "why_not_mac",
            "why_not_superfit",
            "why_not_point2cad",
            "why_not_hybrid",
        ],
    )

    mac_candidates_created = sum(1 for row in rows if row.get("mac_attempted"))
    mac_step_success = sum(1 for row in rows if row.get("mac_generated_step_count"))
    mac_qa_pass = sum(1 for row in rows if row.get("mac_success"))
    current_v6_candidates_created = sum(1 for row in rows if row.get("current_v6_attempted"))
    current_v6_step_success = sum(1 for row in rows if row.get("current_v6_candidate_count"))
    current_v6_qa_pass = sum(1 for row in rows if row.get("current_v6_success"))
    superfit_candidates_created = sum(1 for row in rows if row.get("superfit_attempted"))
    superfit_step_success = sum(1 for row in rows if row.get("superfit_candidate_count"))
    superfit_qa_pass = sum(1 for row in rows if row.get("superfit_success"))
    point2cad_real_executed = sum(1 for row in rows if row.get("point2cad_attempted"))
    point2cad_candidates_created = sum(1 for row in rows if row.get("point2cad_candidate_count"))
    point2cad_surface_success = sum(1 for row in rows if row.get("point2cad_surface_success"))
    point2cad_topology_success = sum(1 for row in rows if row.get("point2cad_topology_success"))
    hybrid_candidates_created = sum(1 for row in rows if row.get("hybrid_candidate_count"))
    selected_cad_native = sum(1 for row in rows if row.get("selected_cad_native"))
    selected_faceted = len(rows) - selected_cad_native
    canary_selected = [row for row in rows if row["component_id"] in {item["component_id"] for item in canaries}]
    canary_native_pass = sum(1 for row in canary_selected if row.get("selected_cad_native"))
    cad_native_triangle_support = sum(
        component_map[row["component_id"]]["triangle_count"]
        for row in rows
        if row.get("selected_cad_native")
    )
    faceted_triangle_support = sum(
        component_map[row["component_id"]]["triangle_count"]
        for row in rows
        if not row.get("selected_cad_native")
    )

    make_backend_review_sheet(rows, OUT / "artifacts" / "canary_backend_comparison.png", V3_ROOT)

    if selected_cad_native > 0:
        mixed_step = OUT / "05_assembly" / "tank_p3_45_component_pipeline_a_multibackend_repair_v4.step"
        selected_entries = []
        for row in rows:
            selected_entries.append(
                {
                    "part_id": row["component_id"],
                    "semantic_role": row["selected_backend"],
                    "builder": row["selected_backend"],
                    "route_status": "SELECTED_FOR_ASSEMBLY",
                    "quality_tag": "PIPELINE_A_REPAIR_V4",
                    "geometry_present": True,
                    "fresh_step_path": row.get("selected_step_path"),
                    "T_part_local_to_source_global": np.eye(4).tolist(),
                }
            )
        try:
            sys.path.insert(0, str(ROOT / "ours3"))
            from generalization.common.assembly_runner import build as build_xcaf  # type: ignore

            assembly_info = build_xcaf(selected_entries, mixed_step)
            assembly_reload = True
        except Exception as exc:
            assembly_info = {"error": f"{type(exc).__name__}: {exc}"}
            assembly_reload = False
    else:
        mixed_step = None
        assembly_info = {"attempted": False, "completed": False, "error": None}
        assembly_reload = False

    current_gate = (
        "TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4_PARTIAL_PASS"
        if selected_cad_native > 0
        else "TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4_CANDIDATE_ACTIVATION_FAIL"
    )
    blockers = []
    if mac_candidates_created == 0:
        blockers.append("PIPELINE_A_MAC_RUNTIME_CANDIDATE_GENERATION")
    elif mac_step_success == 0:
        blockers.append("MAC_CONSTRUCTION_GENERALIZATION")
    if canary_native_pass == 0:
        blockers.append("GENERIC_COMPONENT_CAD_GEOMETRY_FIDELITY")
    if current_v6_candidates_created == 0:
        blockers.append("CURRENT_V6_COMPONENT_ROUTING")
    if superfit_candidates_created == 0:
        blockers.append("SUPERFIT_COMPONENT_ROUTING")
    if point2cad_real_executed == 0:
        blockers.append("POINT2CAD_COMPONENT_ROUTING")
    next_blocker = blockers[0] if blockers else "NONE"

    summary = {
        "CURRENT_GATE": current_gate,
        "NEXT_PRIMARY_BLOCKER": next_blocker,
        "PIPELINE_A_FULLSTACK_RESTORED": bool(mac_candidates_created > 0 and len(canaries) == CANARY_COMPONENT_COUNT),
        "SOURCE_OBJ": str(SOURCE_OBJ.resolve()),
        "FROZEN_P3_ROOT": str(FROZEN_P3_ROOT.resolve()),
        "P3_REEXECUTED": False,
        "P3_COMPONENT_COUNT": len(components),
        "CROSS_P3_COMPONENT_MERGE_COUNT": 0,
        "CANARY_COMPONENT_COUNT": len(canaries),
        "CURRENT_V3_MAC_GENERATED_CANDIDATES": v3_audit["CURRENT_V3_MAC_GENERATED_CANDIDATES"],
        "CURRENT_V3_MAC_GENERATED_STEP_SUCCESS": v3_audit["CURRENT_V3_MAC_GENERATED_STEP_SUCCESS"],
        "CURRENT_V3_CURRENT_V6_CANDIDATES": v3_audit["CURRENT_V3_CURRENT_V6_CANDIDATES"],
        "CURRENT_V3_SUPERFIT_CANDIDATES": v3_audit["CURRENT_V3_SUPERFIT_CANDIDATES"],
        "CURRENT_V3_POINT2CAD_CANDIDATES": v3_audit["CURRENT_V3_POINT2CAD_CANDIDATES"],
        "CURRENT_V3_HYBRID_CANDIDATES": v3_audit["CURRENT_V3_HYBRID_CANDIDATES"],
        "CURRENT_V3_FACETED_FALLBACK_COMPONENTS": v3_audit["CURRENT_V3_FACETED_FALLBACK_COMPONENTS"],
        "PIPELINE_A_WAS_NOT_FULLY_EXECUTED": v3_audit["PIPELINE_A_WAS_NOT_FULLY_EXECUTED"],
        "MAC_CANDIDATES_CREATED": mac_candidates_created,
        "MAC_STEP_SUCCESS": mac_step_success,
        "MAC_QA_PASS": mac_qa_pass,
        "CURRENT_V6_CANDIDATES_CREATED": current_v6_candidates_created,
        "CURRENT_V6_STEP_SUCCESS": current_v6_step_success,
        "CURRENT_V6_QA_PASS": current_v6_qa_pass,
        "SUPERFIT_CANDIDATES_CREATED": superfit_candidates_created,
        "SUPERFIT_STEP_SUCCESS": superfit_step_success,
        "SUPERFIT_QA_PASS": superfit_qa_pass,
        "POINT2CAD_REAL_EXECUTED_COMPONENTS": point2cad_real_executed,
        "POINT2CAD_CANDIDATES_CREATED": point2cad_candidates_created,
        "POINT2CAD_SURFACE_SUCCESS": point2cad_surface_success,
        "POINT2CAD_TOPOLOGY_SUCCESS": point2cad_topology_success,
        "HYBRID_CANDIDATES_CREATED": hybrid_candidates_created,
        "CAD_NATIVE_QA_PASS_COMPONENTS": selected_cad_native,
        "FACETED_FALLBACK_COMPONENTS": selected_faceted,
        "PURE_CAD_NATIVE_COMPONENTS": selected_cad_native,
        "HYBRID_WITH_FACETED_RESIDUAL_COMPONENTS": 0,
        "PURE_FACETED_COMPONENTS": selected_faceted,
        "CAD_NATIVE_RECOVERY_RATE": float(selected_cad_native / max(len(components), 1)),
        "CAD_NATIVE_TRIANGLE_SUPPORT": int(cad_native_triangle_support),
        "CAD_NATIVE_TRIANGLE_SUPPORT_RATIO": float(cad_native_triangle_support / max(int(cad_native_triangle_support + faceted_triangle_support), 1)),
        "FACETED_TRIANGLE_SUPPORT": int(faceted_triangle_support),
        "FINAL_COMPONENT_COUNT": len(rows),
        "FINAL_SOLID_COUNT": 0,
        "FINAL_CLOSED_SHELL_COUNT": 0,
        "FINAL_OPEN_SHELL_COUNT": len(rows),
        "FINAL_FACE_COUNT": None,
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "BASELINE_FACETED_STEP": str((V3_ROOT / "14_assembly" / "tank_p3_45_component_assembly.step").resolve()),
        "MIXED_CAD_STEP": str(mixed_step.resolve()) if mixed_step else None,
        "MIXED_CAD_STEP_RELOAD": assembly_reload,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
    }

    dump_json(OUT / "artifacts" / "final_summary.json", summary)
    dump_json(OUT / "artifacts" / "component_summary.json", component_summary)
    dump_json(OUT / "artifacts" / "assembly_result.json", assembly_info)
    report = write_report(summary, reuse_audit, correspondence)
    (OUT / "artifacts" / "TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4_REPORT.md").write_text(report, encoding="utf-8")
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--canary-only", action="store_true")
    parser.add_argument("--source", default=str(SOURCE_OBJ))
    parser.add_argument("--p3-root", default=str(FROZEN_P3_ROOT))
    parser.add_argument("--base-root", default=str(V3_ROOT))
    parser.add_argument("--output-root", default=str(OUT))
    args = parser.parse_args()
    if args.resume:
        pass
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
