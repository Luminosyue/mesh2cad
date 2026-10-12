from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _canonical_obj(mesh: trimesh.Trimesh) -> str:
    vertices = np.asarray(mesh.vertices, float)
    faces = np.asarray(mesh.faces, int)
    order = np.lexsort((vertices[:, 2], vertices[:, 1], vertices[:, 0]))
    inverse = np.empty(len(order), dtype=int)
    inverse[order] = np.arange(len(order))
    vertices = vertices[order]
    faces = inverse[faces]
    face_order = np.lexsort((faces[:, 2], faces[:, 1], faces[:, 0]))
    lines = [f"v {p[0]:.9g} {p[1]:.9g} {p[2]:.9g}" for p in vertices]
    lines.extend(f"f {f[0] + 1} {f[1] + 1} {f[2] + 1}" for f in faces[face_order])
    return "\n".join(lines) + "\n"


def _simplify(mesh: trimesh.Trimesh, target: int) -> trimesh.Trimesh:
    if len(mesh.faces) <= target:
        return mesh.copy()
    try:
        return mesh.simplify_quadric_decimation(face_count=target)
    except TypeError:
        return mesh.simplify_quadric_decimation(target)


def _sample(mesh: trimesh.Trimesh, count: int = 6000) -> np.ndarray:
    points, _ = trimesh.sample.sample_surface(mesh, min(count, max(1000, len(mesh.faces) * 4)), seed=31)
    return np.asarray(points, float)


def _proxy_metrics(source: trimesh.Trimesh, proxy: trimesh.Trimesh) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    a, b = _sample(source), _sample(proxy)
    da = cKDTree(b).query(a, workers=-1)[0]
    db = cKDTree(a).query(b, workers=-1)[0]
    source_normals = np.asarray(source.face_normals)
    proxy_normals = np.asarray(proxy.face_normals)
    normal_coverage = float(np.mean(np.max(np.abs(source_normals[:: max(1, len(source_normals) // 1000)] @ proxy_normals.T), axis=1))) if len(proxy_normals) else 0.0
    return {
        "surface_chamfer_after_simplification": float((da.mean() + db.mean()) * 0.5),
        "surface_hausdorff_after_simplification": float(max(da.max(), db.max())),
        "feature_preservation_score": normal_coverage,
    }


def _render(part: trimesh.Trimesh, whole: trimesh.Trimesh, part_path: Path, context_path: Path) -> None:
    from PIL import Image, ImageDraw

    width, height = 1220, 1040
    direction = np.asarray([1.35, -1.55, 1.05], float); direction /= np.linalg.norm(direction)
    right = np.cross(direction, np.asarray([0.0, 0.0, 1.0])); right /= np.linalg.norm(right)
    up = np.cross(right, direction); up /= np.linalg.norm(up)

    def projected(mesh: trimesh.Trimesh, bounds: np.ndarray):
        center = bounds.mean(0)
        span = max(float(np.linalg.norm(bounds[1] - bounds[0])), 1e-9)
        points = np.asarray(mesh.vertices, float) - center
        xy = np.column_stack((points @ right, points @ up)) / span
        pixels = np.column_stack((width * (0.5 + xy[:, 0] * 0.82), height * (0.5 - xy[:, 1] * 0.82)))
        depth = points @ direction
        return pixels, depth

    def draw_mesh(draw: ImageDraw.ImageDraw, mesh: trimesh.Trimesh, bounds: np.ndarray, base: tuple[int, int, int]):
        pixels, depth = projected(mesh, bounds)
        faces = np.asarray(mesh.faces, int)
        normals = np.asarray(mesh.face_normals, float)
        order = np.argsort(depth[faces].mean(axis=1))
        light = np.asarray([-0.4, -0.3, 0.85]); light /= np.linalg.norm(light)
        for index in order:
            shade = 0.68 + 0.30 * abs(float(normals[index] @ light))
            color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in base)
            draw.polygon([tuple(pixels[int(vertex)]) for vertex in faces[index]], fill=color)

    for path, context in ((part_path, False), (context_path, True)):
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        bounds = np.asarray(whole.bounds if context else part.bounds)
        if context:
            draw_mesh(draw, whole, bounds, (205, 211, 218))
        draw_mesh(draw, part, bounds, (216, 86, 79))
        path.parent.mkdir(parents=True, exist_ok=True)
        image.resize((820, 700), Image.Resampling.LANCZOS).save(path)


def prepare_dual_modal(part_mesh: Path, whole_mesh: Path, output: Path) -> dict[str, Any]:
    source = trimesh.load(part_mesh, force="mesh", process=False)
    whole = trimesh.load(whole_mesh, force="mesh", process=False)
    audits = []
    proxies: dict[int, trimesh.Trimesh] = {}
    for target in (128, 256, 512):
        proxy = _simplify(source, target)
        proxies[target] = proxy
        metrics = _proxy_metrics(source, proxy)
        audits.append({
            "target_triangle_count": target,
            "original_triangle_count": int(len(source.faces)),
            "simplified_triangle_count": int(len(proxy.faces)),
            "simplification_ratio": float(len(proxy.faces) / max(len(source.faces), 1)),
            **metrics,
        })
    eligible = [row for row in audits if row["feature_preservation_score"] >= 0.90]
    chosen = min(eligible or audits, key=lambda row: (row["surface_chamfer_after_simplification"], row["simplified_triangle_count"]))
    target = int(chosen["target_triangle_count"])
    proxy = proxies[target]
    output.mkdir(parents=True, exist_ok=True)
    proxy.export(output / "vlm_simplified_part.obj")
    tokens = _canonical_obj(proxy)
    (output / "canonical_obj_tokens.txt").write_text(tokens, encoding="ascii")
    _render(source, whole, output / "part_isometric_render.png", output / "source_object_context_render.png")
    result = {
        "original_high_poly_part_mesh": str(part_mesh),
        "original_high_poly_part_mesh_sha256": _sha(part_mesh.read_bytes()),
        "vlm_simplified_part_mesh": str(output / "vlm_simplified_part.obj"),
        "selected_target_triangle_count": target,
        "serialization_sha256": _sha(tokens.encode("ascii")),
        "part_render_sha256": _sha((output / "part_isometric_render.png").read_bytes()),
        "context_render_sha256": _sha((output / "source_object_context_render.png").read_bytes()),
        "simplification_audit": audits,
    }
    (output / "dual_modal_manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _image(path: Path) -> dict[str, Any]:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}}


def call_qwen(part_id: str, semantic_role: str, allowed_builders: list[str], dual_dir: Path, env_path: Path, output: Path, count: int = 4) -> dict[str, Any]:
    from openai import OpenAI

    values = _env(env_path)
    key = values.get("VISUAL_API_KEY") or values.get("DASHSCOPE_API_KEY") or values.get("OPENAI_API_KEY")
    base = values.get("VISUAL_BASE_URL") or values.get("OPENAI_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model = values.get("VISUAL_MODEL") or "qwen3-vl-flash"
    if not key:
        return {"available": False, "status_code": None, "error": "VISUAL_API_KEY_MISSING", "candidates": []}
    tokens = (dual_dir / "canonical_obj_tokens.txt").read_text(encoding="ascii")
    schema = {
        "candidates": [{
            "candidate_id": "MESH2CAD_01",
            "construction_family": "one allowed builder",
            "operation_sequence": ["ordered CAD operations"],
            "topology_hypothesis": {},
            "profile_hypothesis": {},
            "axis_hypothesis": {},
            "boolean_relations": [],
            "raw_cadquery_program": "diagnostic CadQuery Python program",
            "rationale": "why the two mesh modalities support this construction",
        }]
    }
    prompt = {
        "task": f"Propose {count} distinct executable CadQuery construction hypotheses for this CAD part.",
        "part_id": part_id,
        "semantic_role": semantic_role,
        "allowed_builders": allowed_builders,
        "requirements": [
            "Use both canonical OBJ connectivity and the part/context renders.",
            "Use a different construction family for each candidate.",
            "Return diagnostic CadQuery code, but understand raw dimensions will be grounded to measured refs before formal execution.",
            "Do not read STEP/BRep or refer to historical CAD.",
            "Prefer coherent semantic surfaces and compact topology.",
        ],
        "response_schema": schema,
        "canonical_obj_tokens": tokens,
    }
    content = [
        {"type": "text", "text": json.dumps(prompt, separators=(",", ":"))},
        _image(dual_dir / "part_isometric_render.png"),
        _image(dual_dir / "source_object_context_render.png"),
    ]
    client = OpenAI(api_key=key, base_url=base, timeout=240.0)
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.25,
            max_tokens=5000,
            messages=[{"role": "system", "content": "Return one strict JSON object only."}, {"role": "user", "content": content}],
        )
        raw = response.choices[0].message.content or ""
        usage = response.usage
        result = {
            "available": True,
            "status_code": 200,
            "model": model,
            "base_url": base,
            "raw_response": raw,
            "usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            },
            "obj_tokens_used": True,
            "part_render_used": True,
            "whole_context_render_used": True,
        }
    except Exception as exc:
        code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        result = {"available": False, "status_code": code, "model": model, "base_url": base, "error": f"{type(exc).__name__}: {exc}"}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
