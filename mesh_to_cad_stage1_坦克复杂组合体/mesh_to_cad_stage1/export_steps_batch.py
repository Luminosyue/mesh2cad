"""Batch-export every outputs_batch_cases/<case>/primitives.json to STEP.

Uses rigid gp_Trsf + SVD orthonormalization (same fix as mesh_to_cad_stage1
export_step_cadquery.py). Does NOT Fuse parts; does NOT rewrite recognition types.

Run this in the user's working CadQuery/OCP environment:
    python export_steps_batch.py
"""
from __future__ import annotations

import json
import math
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import cadquery as cq
import numpy as np
from OCP.gp import gp_Trsf

ROOT = Path(__file__).resolve().parent
BATCH = ROOT / "outputs_batch_cases"
EPS = 1e-12

# Reuse the hardened exporter from the base project when available.
_BASE_EXPORTER = (
    ROOT.parent.parent / "mesh_to_cad_stage1" / "export_step_cadquery.py"
)
if _BASE_EXPORTER.is_file():
    sys.path.insert(0, str(_BASE_EXPORTER.parent))
    try:
        from export_step_cadquery import (  # type: ignore
            apply_transform,
            expected_volume,
            make_shape as _robust_make_shape,
            validate_step_file,
        )

        _HAS_ROBUST = True
    except Exception:  # noqa: BLE001
        _HAS_ROBUST = False
else:
    _HAS_ROBUST = False


def _orthonormalize_rotation(R: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(R)
    R_ortho = U @ Vt
    if np.linalg.det(R_ortho) < 0:
        U = U.copy()
        U[:, -1] *= -1.0
        R_ortho = U @ Vt
    return R_ortho


def _local_make_shape(p: dict[str, Any]) -> cq.Shape:
    """Fallback shape builder with rigid transform (no GTrsf)."""
    if p["type"] == "box":
        x, y, z = (float(v) for v in p["extents"])
        shape = cq.Workplane("XY").box(x, y, z, centered=(True, True, True)).val()
    elif p["type"] == "cylinder":
        shape = cq.Workplane("XY").cylinder(
            float(p["height"]), float(p["radius"]), centered=(True, True, True)
        ).val()
    else:
        raise ValueError(f"Unsupported primitive: {p['type']}")

    T = np.asarray(p["transform"], dtype=float)
    R = _orthonormalize_rotation(T[:3, :3])
    t = T[:3, 3]
    trsf = gp_Trsf()
    trsf.SetValues(
        float(R[0, 0]), float(R[0, 1]), float(R[0, 2]), float(t[0]),
        float(R[1, 0]), float(R[1, 1]), float(R[1, 2]), float(t[1]),
        float(R[2, 0]), float(R[2, 1]), float(R[2, 2]), float(t[2]),
    )
    return shape.located(cq.Location(trsf))


def make_shape(p: dict[str, Any]) -> cq.Shape:
    if _HAS_ROBUST:
        return _robust_make_shape(p)
    return _local_make_shape(p)


def _part_name(p: dict[str, Any], i: int) -> str:
    src = p.get("source_part_name") or p.get("name")
    cid = p.get("component_id", i)
    if src:
        return f"part_{int(cid):02d}_{src}"
    return f"part_{int(cid):02d}_{p['type']}"


def _known_recognition_errors(primitives: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    for p in primitives:
        name = p.get("source_part_name") or f"component_{p.get('component_id')}"
        expected = p.get("expected_type")
        actual = p.get("type")
        if expected and expected != actual:
            notes.append(f"{name}: recognized as {actual}, expected {expected}")
    return notes


def export_one_case(case_dir: Path) -> dict[str, Any]:
    primitives_path = case_dir / "primitives.json"
    step_path = case_dir / "model.step"
    t0 = time.perf_counter()
    report: dict[str, Any] = {
        "case_id": case_dir.name,
        "step_path": str(step_path),
        "status": "pending",
    }
    try:
        primitives = json.loads(primitives_path.read_text(encoding="utf-8"))
        report["primitive_count"] = len(primitives)
        report["known_recognition_errors"] = _known_recognition_errors(primitives)

        assembly = cq.Assembly(name=case_dir.name)
        for i, p in enumerate(primitives):
            assembly.add(make_shape(p), name=_part_name(p, i))

        assembly.export(str(step_path))
        report["file_size_bytes"] = int(step_path.stat().st_size)
        report["export_seconds"] = time.perf_counter() - t0

        if _HAS_ROBUST:
            vr = validate_step_file(step_path, expected_solid_count=len(primitives))
            report.update(
                {
                    "read_success": vr.import_success and not vr.shape_is_null,
                    "solid_count": vr.solid_count,
                    "total_volume": vr.volume,
                    "bounding_box": vr.bounding_box,
                    "empty_shape": vr.shape_is_null,
                    "validation_error": vr.error_message,
                    "theoretical_volume": expected_volume(primitives),
                }
            )
            if vr.volume is not None and report["theoretical_volume"] > EPS:
                report["volume_relative_error"] = abs(
                    vr.volume - report["theoretical_volume"]
                ) / report["theoretical_volume"]
            report["status"] = "ok" if vr.export_success else "written_but_validation_failed"
            report["assembly_part_count"] = len(primitives)
        else:
            imported = cq.importers.importStep(str(step_path))
            shape = imported.val()
            solids = shape.Solids()
            report.update(
                {
                    "read_success": True,
                    "solid_count": len(solids),
                    "total_volume": float(shape.Volume()),
                    "empty_shape": shape.isNull(),
                    "assembly_part_count": len(primitives),
                    "status": "ok",
                }
            )
        print(
            f"Wrote {step_path} solids={report.get('solid_count')} "
            f"vol={report.get('total_volume')} status={report['status']}"
        )
    except Exception as exc:  # noqa: BLE001
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["export_seconds"] = time.perf_counter() - t0
        report["traceback"] = traceback.format_exc()
        print(f"FAILED {case_dir.name}: {report['error']}", file=sys.stderr)
    return report


def main() -> int:
    reports = []
    for primitives_path in sorted(BATCH.glob("*/primitives.json")):
        reports.append(export_one_case(primitives_path.parent))
    out = BATCH / "step_export_report.json"
    out.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    # Never abort the whole batch on a single failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
