"""Measured-geometry CAD runtime used by MAC-generated CASE09 V2 programs.

This module never reads meshes or previous STEP files. It exposes bounded,
OpenCascade-compatible operations over the frozen measured_cad_spec.json.
"""
from __future__ import annotations

import json
from pathlib import Path

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Pnt


def load_measured_spec(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("raw_obj_read_by_mac") is not False or data.get("old_step_read_by_mac") is not False:
        raise ValueError("measured-input isolation contract is missing")
    if not data.get("operations"):
        raise ValueError("measured spec has no operations")
    return data


def _polygon_wire(points):
    maker = BRepBuilderAPI_MakePolygon(); first = None
    for xyz in points:
        point = gp_Pnt(*map(float, xyz)); maker.Add(point)
        if first is None:
            first = point
    maker.Add(first); maker.Close()
    if not maker.IsDone():
        raise RuntimeError("closed measured profile construction failed")
    return maker.Wire()


def _loft_from_operation(operation: dict):
    axis = operation["axis"]
    axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
    plane_axes = [i for i in range(3) if i != axis_index]
    sections = operation.get("sections", [])
    if len(sections) < 2:
        raise ValueError("loft requires at least two measured sections")
    loft = BRepOffsetAPI_ThruSections(True, False, 1e-5)
    loft.CheckCompatibility(False); loft.SetMaxDegree(int(operation.get("max_degree", 5)))
    for section in sections:
        coordinate = float(section["coordinate"]); points = []
        for uv in section["profile"]:
            xyz = [0.0, 0.0, 0.0]
            xyz[axis_index] = coordinate
            xyz[plane_axes[0]] = float(uv[0]); xyz[plane_axes[1]] = float(uv[1])
            points.append(xyz)
        loft.AddWire(_polygon_wire(points))
    loft.Build()
    if not loft.IsDone():
        raise RuntimeError("measured global loft construction failed")
    shape = loft.Shape()
    if shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("measured loft produced invalid BRep")
    return shape


def _compound(shapes):
    if len(shapes) == 1:
        return shapes[0]
    result = TopoDS_Compound(); builder = BRep_Builder(); builder.MakeCompound(result)
    for shape in shapes:
        builder.Add(result, shape)
    return result


def _coerce_spec(spec=None, args=(), kwargs=None):
    kwargs = kwargs or {}
    candidate = spec if spec is not None else kwargs.get("spec")
    if candidate is None and args:
        candidate = args[0]
    if not isinstance(candidate, dict) or "operations" not in candidate:
        sections = kwargs.get("sections") or kwargs.get("profiles") or kwargs.get("profile_series")
        axis = kwargs.get("axis") or kwargs.get("loft_axis")
        if sections and axis in {"X", "Y", "Z"}:
            normalized = []
            for section in sections:
                if not isinstance(section, dict) or "coordinate" not in section:
                    raise TypeError("section-only builder call requires measured coordinate dictionaries")
                profile = section.get("profile") or section.get("vertices") or section.get("points") or section.get("profile_points")
                if not profile:
                    raise TypeError("section-only builder call lacks measured profile coordinates")
                normalized.append({"coordinate": section["coordinate"], "profile": profile})
            candidate = {"operations": [{"operation": "PROFILE_LOFT", "axis": axis, "sections": normalized, "max_degree": kwargs.get("max_degree", 5)}]}
        else:
            raise TypeError("runtime builder requires complete measured spec or measured sections plus axis")
    return candidate


def build_global_loft_part(spec: dict = None, *args, **kwargs):
    spec = _coerce_spec(spec, args, kwargs)
    return _loft_from_operation(next(op for op in spec["operations"] if op.get("operation") == "GLOBAL_LOFT"))


def build_profile_loft_part(spec: dict = None, *args, **kwargs):
    spec = _coerce_spec(spec, args, kwargs)
    operations = [op for op in spec["operations"] if op.get("operation") == "PROFILE_LOFT"]
    if not operations:
        raise ValueError("PROFILE_LOFT operation missing")
    return _compound([_loft_from_operation(op) for op in operations])


def build_patterned_blade_part(spec: dict = None, *args, **kwargs):
    spec = _coerce_spec(spec, args, kwargs)
    blades = [op for op in spec["operations"] if op.get("operation") == "BLADE_LOFT"]
    pattern = next((op for op in spec["operations"] if op.get("operation") == "MEASURED_INSTANCE_PATTERN"), None)
    if not blades or not pattern or pattern.get("instance_count") != len(blades):
        raise ValueError("measured blade-pattern semantics are incomplete")
    if pattern.get("forced_symmetry"):
        raise ValueError("forced symmetry is prohibited for measured blade instances")
    return _compound([_loft_from_operation(op) for op in blades])


def build_dorsal_feature_part(spec: dict = None, *args, **kwargs):
    spec = _coerce_spec(spec, args, kwargs)
    operations = [op for op in spec["operations"] if op.get("operation") == "DORSAL_FEATURE_LOFT"]
    if not operations:
        raise ValueError("DORSAL_FEATURE_LOFT operations missing")
    return _compound([_loft_from_operation(op) for op in operations])


class ValidationReport(dict):
    def __bool__(self):
        return bool(self.get("valid", False))

    def __iter__(self):
        yield bool(self.get("valid", False))
        yield dict(self)


def validate_shape(shape, *args, **kwargs):
    if shape is None or shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError("final MAC-generated shape is not a valid BRep")
    # Keep one canonical success flag while supporting the vocabulary used by
    # independently generated MAC programs (``valid`` and ``passed``).
    return ValidationReport(valid=True, passed=True, brep_valid=True)


def export_step(shape, output_path: str | Path) -> None:
    validate_shape(shape)
    output = Path(output_path); output.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(output)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP export failed: {output}")


def write_program_provenance(output_path=None, record=None, **kwargs) -> None:
    if isinstance(output_path, dict) and record is None:
        record = output_path; output = Path("program_provenance.json")
    else:
        output = Path(output_path) if output_path is not None else Path("program_provenance.json")
        if output.suffix.lower() == ".step":
            output = output.with_suffix(".program.json")
    payload = dict(record or {}); payload.update(kwargs)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
