#!/usr/bin/env python3
"""Per-sample QA gate for cad_spatial_dataset (DeepCAD + Fusion360).

Compares reference mesh (source geometry) vs DSL re-execution mesh.
Writes qa.json with training gate fields.
"""

from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

V1_OPS = {
    "Sketch",
    "Circle",
    "Rectangle",
    "Box",
    "Extrude",
    "ExtrudePolygon",
    "Cut",
    "Union",
    "Cylinder",
    "Revolve",
}

DEFAULT_MAX_CHAMFER_NORM = 0.05
DEFAULT_MAX_HAUSSDORFF95_NORM = 0.10
DEFAULT_MAX_VOLUME_ERROR = 0.05


def _parse_dsl_ops(dsl_text: str) -> tuple[dict[str, int], dict[str, int], int]:
    ops: dict[str, int] = {}
    profiles: dict[str, int] = {}
    try:
        tree = ast.parse(dsl_text, mode="exec")
    except SyntaxError:
        return ops, profiles, 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in V1_OPS:
                ops[name] = ops.get(name, 0) + 1
            if name == "Extrude" and node.args:
                arg0 = node.args[0]
                if isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Name):
                    profiles[arg0.func.id] = profiles.get(arg0.func.id, 0) + 1
            if name == "Box":
                profiles["Rectangle"] = profiles.get("Rectangle", 0) + 1
            if name == "ExtrudePolygon":
                profiles["Polygon"] = profiles.get("Polygon", 0) + 1
    op_count = ops.get("Extrude", 0) + ops.get("ExtrudePolygon", 0) + ops.get("Box", 0)
    return ops, profiles, op_count


def _sample_surface(mesh, n: int, seed: int) -> np.ndarray:
    import trimesh

    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    rng = np.random.default_rng(seed)
    pts, _ = trimesh.sample.sample_surface(mesh, n, seed=int(rng.integers(1 << 30)))
    return np.asarray(pts, dtype=np.float64)


def compare_meshes(ref_path: Path, pred_path: Path, n: int = 10_000, seed: int = 0) -> dict[str, Any]:
    import trimesh
    from scipy.spatial import cKDTree

    ref = trimesh.load(str(ref_path), force="mesh")
    pred = trimesh.load(str(pred_path), force="mesh")
    if isinstance(ref, trimesh.Scene):
        ref = ref.dump(concatenate=True)
    if isinstance(pred, trimesh.Scene):
        pred = pred.dump(concatenate=True)

    diag = float(np.linalg.norm(ref.bounds[1] - ref.bounds[0]))
    if diag < 1e-12:
        return {"error": "zero bbox diagonal"}

    a = _sample_surface(ref, n, seed)
    b = _sample_surface(pred, n, seed + 1)
    d_ab = cKDTree(b).query(a, k=1)[0]
    d_ba = cKDTree(a).query(b, k=1)[0]

    ref_vol = float(abs(ref.volume))
    pred_vol = float(abs(pred.volume))
    volume_ratio = pred_vol / ref_vol if ref_vol > 0 else None
    volume_error = abs(1.0 - volume_ratio) if volume_ratio is not None else None

    return {
        "chamfer_norm": float((d_ab.mean() + d_ba.mean()) / 2 / diag),
        "hausdorff95": float(np.percentile(np.concatenate([d_ab, d_ba]), 95) / diag),
        "volume_ratio": volume_ratio,
        "volume_error": volume_error,
        "ref_vertices": int(len(ref.vertices)),
        "pred_vertices": int(len(pred.vertices)),
    }


def _reexecute_dsl_mesh(dsl_path: Path, out_stl: Path) -> tuple[bool, str | None]:
    from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, parse_dsl

    try:
        code = dsl_path.read_text(encoding="utf-8")
        parse_dsl(code)
        step = out_stl.with_suffix(".step")
        execute_dsl(code, step, out_stl)
        if not out_stl.exists():
            return False, "DSL execution produced no mesh"
        return True, None
    except Exception as exc:
        return False, str(exc)


def _dora_edge_count(sample_dir: Path) -> int | None:
    dora_npz = sample_dir / "dora" / "salient_edges.npz"
    if dora_npz.exists():
        data = np.load(dora_npz)
        if "edge_idx" in data:
            return int(len(data["edge_idx"]))
    sharp_json = sample_dir / "dora" / "sharp_edges.json"
    if sharp_json.exists():
        payload = json.loads(sharp_json.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return len(payload)
        if isinstance(payload, dict) and "chains" in payload:
            return len(payload["chains"])
    return None


def _build_deepcad_reference(source_json: Path, out_stl: Path) -> bool:
    from deepcad_occ_builder import export_deepcad_json

    try:
        export_deepcad_json(source_json, out_stl.with_suffix(".step"), out_stl)
        return out_stl.exists()
    except Exception:
        return False


def run_sample_qa(
    sample_dir: Path,
    *,
    reference_mesh: Path | None = None,
    source_json: Path | None = None,
    dsl_path: Path | None = None,
    step_path: Path | None = None,
    max_chamfer_norm: float = DEFAULT_MAX_CHAMFER_NORM,
    max_hausdorff95: float = DEFAULT_MAX_HAUSSDORFF95_NORM,
    max_volume_error: float = DEFAULT_MAX_VOLUME_ERROR,
    seed: int = 0,
    write: bool = True,
) -> dict[str, Any]:
    """Run QA for one sample directory. Returns qa dict and optionally writes qa.json."""
    sample_dir = Path(sample_dir)
    dsl_path = dsl_path or (sample_dir / "program.dsl")
    step_path = step_path or (sample_dir / "model.step")
    source_json = source_json or (sample_dir / "source.json")

    qa: dict[str, Any] = {
        "sample_id": sample_dir.name,
        "dsl_parse_ok": False,
        "dsl_execute_ok": False,
        "step_valid": step_path.exists() and step_path.stat().st_size > 0,
        "chamfer": None,
        "hausdorff95": None,
        "volume_error": None,
        "op_count": 0,
        "has_cut": False,
        "has_union": False,
        "dora_edge_count": _dora_edge_count(sample_dir),
        "passed": False,
        "reject_reason": None,
    }

    if not dsl_path.exists():
        qa["reject_reason"] = "missing program.dsl"
        if write:
            _write_qa(sample_dir, qa)
        return qa

    dsl_text = dsl_path.read_text(encoding="utf-8")
    try:
        ast.parse(dsl_text, mode="exec")
        qa["dsl_parse_ok"] = True
    except SyntaxError as exc:
        qa["reject_reason"] = f"dsl_parse_error: {exc}"
        if write:
            _write_qa(sample_dir, qa)
        return qa

    ops, _profiles, op_count = _parse_dsl_ops(dsl_text)
    qa["op_count"] = op_count
    qa["has_cut"] = ops.get("Cut", 0) > 0
    qa["has_union"] = ops.get("Union", 0) > 0
    qa["ops"] = ops

    with tempfile.TemporaryDirectory(prefix="cad_qa_") as tmp:
        tmp_path = Path(tmp)
        ref_mesh = reference_mesh
        if ref_mesh is None and source_json.exists():
            ref_stl = tmp_path / "reference.stl"
            if _build_deepcad_reference(source_json, ref_stl):
                ref_mesh = ref_stl
        if ref_mesh is None:
            fallback = sample_dir / "model.obj"
            if fallback.exists():
                ref_mesh = fallback
        if ref_mesh is None or not Path(ref_mesh).exists():
            qa["reject_reason"] = "missing reference mesh"
            if write:
                _write_qa(sample_dir, qa)
            return qa

        dsl_mesh = tmp_path / "dsl_mesh.stl"
        ok, err = _reexecute_dsl_mesh(dsl_path, dsl_mesh)
        qa["dsl_execute_ok"] = ok
        if not ok:
            qa["reject_reason"] = f"dsl_execute_error: {err}"
            if write:
                _write_qa(sample_dir, qa)
            return qa

        metrics = compare_meshes(Path(ref_mesh), dsl_mesh, seed=seed)
        if "error" in metrics:
            qa["reject_reason"] = metrics["error"]
            if write:
                _write_qa(sample_dir, qa)
            return qa

        qa["chamfer"] = metrics["chamfer_norm"]
        qa["hausdorff95"] = metrics["hausdorff95"]
        qa["volume_error"] = metrics["volume_error"]
        qa["geometry"] = metrics

        reasons: list[str] = []
        if qa["chamfer"] > max_chamfer_norm:
            reasons.append(f"chamfer>{max_chamfer_norm}")
        if qa["hausdorff95"] > max_hausdorff95:
            reasons.append(f"hausdorff95>{max_hausdorff95}")
        if qa["volume_error"] is not None and qa["volume_error"] > max_volume_error:
            reasons.append(f"volume_error>{max_volume_error}")

        if reasons:
            qa["reject_reason"] = "; ".join(reasons)
        else:
            qa["passed"] = True

    if write:
        _write_qa(sample_dir, qa)
    return qa


def _write_qa(sample_dir: Path, qa: dict[str, Any]) -> None:
    path = sample_dir / "qa.json"
    path.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run per-sample QA gate")
    parser.add_argument("sample_dir", type=Path, nargs="+")
    parser.add_argument("--max-chamfer", type=float, default=DEFAULT_MAX_CHAMFER_NORM)
    parser.add_argument("--max-hausdorff95", type=float, default=DEFAULT_MAX_HAUSSDORFF95_NORM)
    parser.add_argument("--max-volume-error", type=float, default=DEFAULT_MAX_VOLUME_ERROR)
    args = parser.parse_args()

    passed = 0
    for d in args.sample_dir:
        qa = run_sample_qa(
            d,
            max_chamfer_norm=args.max_chamfer,
            max_hausdorff95=args.max_hausdorff95,
            max_volume_error=args.max_volume_error,
        )
        status = "PASS" if qa["passed"] else "FAIL"
        print(f"{d.name}: {status}  chamfer={qa.get('chamfer')}  reason={qa.get('reject_reason')}")
        passed += int(qa["passed"])
    print(f"\n{passed}/{len(args.sample_dir)} passed")
    return 0 if passed == len(args.sample_dir) else 1


if __name__ == "__main__":
    raise SystemExit(main())
