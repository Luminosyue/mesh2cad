"""DeepCAD-compatible invalid classifier contract."""
from __future__ import annotations


def classify_prediction(*, native_program_valid, cad_exec_success, shape, surface_sampling_success):
    if not native_program_valid:
        return True, "native_program_invalid"
    if not cad_exec_success:
        return True, "cad_execution_failure"
    if shape is None:
        return True, "shape_absent"
    try:
        valid = bool(shape.isValid()) and float(shape.Volume()) > 0
    except Exception:
        valid = False
    if not valid:
        return True, "invalid_or_empty_brep"
    if not surface_sampling_success:
        return True, "surface_sampling_failure"
    return False, ""
