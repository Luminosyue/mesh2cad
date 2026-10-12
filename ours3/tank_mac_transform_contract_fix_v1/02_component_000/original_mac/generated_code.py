import sys
from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace
from pathlib import Path
import cadquery as cq

class Mode(Enum):
    ADD = 'add'

@dataclass(frozen=True)
class Pos:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class Ellipse:
    def __init__(self, major, minor):
        self.major = float(major)
        self.minor = float(minor)

class _PlaneToken:
    def __init__(self, name):
        self.name = name
    def __mul__(self, other):
        if isinstance(other, Pos):
            return _Placement(self.name, other)
        return NotImplemented

class _Placement:
    def __init__(self, plane_name, pos):
        self.plane_name = plane_name
        self.pos = pos
    def __mul__(self, other):
        if isinstance(other, Ellipse):
            return _EllipseSketch(self.plane_name, self.pos, other)
        return NotImplemented

class _EllipseSketch:
    def __init__(self, plane_name, pos, ellipse):
        self.plane_name = plane_name
        self.pos = pos
        self.ellipse = ellipse

class Plane:
    XY = _PlaneToken('XY')
    YZ = _PlaneToken('YZ')
    XZ = _PlaneToken('XZ')

class _CQWrapper:
    def __init__(self, shape):
        self._shape = shape
    def is_valid(self):
        return bool(self._shape.isValid())
    def bounding_box(self):
        bb = self._shape.BoundingBox()
        return SimpleNamespace(
            min=SimpleNamespace(X=bb.xmin, Y=bb.ymin, Z=bb.zmin),
            max=SimpleNamespace(X=bb.xmax, Y=bb.ymax, Z=bb.zmax),
        )
    @property
    def volume(self):
        return float(self._shape.Volume())
    def __add__(self, other):
        return _wrap(self._shape.fuse(_unwrap(other)))
    def __sub__(self, other):
        return _wrap(self._shape.cut(_unwrap(other)))
    def __getattr__(self, name):
        return getattr(self._shape, name)

class BuildPart:
    def __init__(self, workplanes=Plane.XY, mode=Mode.ADD, **kwargs):
        self.workplanes = workplanes
        self.mode = mode
        self.kwargs = kwargs

class BuildSketch:
    def __init__(self, workplanes=Plane.XY, mode=Mode.ADD, **kwargs):
        self.workplanes = workplanes
        self.mode = mode
        self.kwargs = kwargs

class BuildLine:
    def __init__(self, workplane=Plane.XY, mode=Mode.ADD, **kwargs):
        self.workplane = workplane
        self.mode = mode
        self.kwargs = kwargs

class Hole:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

def _unwrap(obj):
    return obj._shape if isinstance(obj, _CQWrapper) else obj

def _wrap(obj):
    return obj if isinstance(obj, _CQWrapper) else _CQWrapper(obj)

def extrude(spec, amount, dir=(1, 0, 0), **kwargs):
    if isinstance(spec, _EllipseSketch):
        wp = cq.Workplane(spec.plane_name)
        wp = wp.center(spec.pos.x, spec.pos.y).ellipse(spec.ellipse.major, spec.ellipse.minor)
        return _wrap(wp.extrude(amount).val())
    raise TypeError(f'Unsupported extrude input: {type(spec)!r}')

def revolve(spec, angle=360, revolution_arc=None, **kwargs):
    raise NotImplementedError('revolve is not implemented in the cadquery fallback')

def fillet(objects, radius=None, **kwargs):
    return objects

def chamfer(objects, length=None, **kwargs):
    return objects

def mirror(objects, **kwargs):
    return objects

def make_face(*args, **kwargs):
    raise NotImplementedError('make_face is not implemented in the cadquery fallback')

def export_step(shape, path):
    cq.exporters.export(_unwrap(shape), str(Path(path)))

def export_stl(shape, path, tolerance=0.01, angular_tolerance=0.1):
    cq.exporters.export(_unwrap(shape), str(Path(path)), tolerance=tolerance, angularTolerance=angular_tolerance)

# === VALIDATION HELPERS ===
import json

_MEASUREMENTS = {}

def _validate_solid(solid, name="solid"):
    """Validate a solid before boolean operations.

    Returns:
        (is_valid, errors): tuple of (bool, list of error strings)
    """
    errors = []

    # 1. Check if valid (manifold, no self-intersections)
    try:
        if not solid.is_valid():
            errors.append(f"{name}: Solid is invalid (non-manifold or self-intersecting)")
    except Exception as e:
        errors.append(f"{name}: Validation error - {str(e)}")

    # 2. Check bounding box
    try:
        bb = solid.bounding_box()
        size_x = bb.max.X - bb.min.X
        size_y = bb.max.Y - bb.min.Y
        size_z = bb.max.Z - bb.min.Z

        # Check for zero or near-zero dimensions
        if size_x < 0.01 or size_y < 0.01 or size_z < 0.01:
            errors.append(
                f"{name}: Dimensions too small ({size_x:.2f} x {size_y:.2f} x {size_z:.2f} mm)"
            )

        # Check for unusually large dimensions
        max_dim = max(size_x, size_y, size_z)
        if max_dim > 1000:  # Assume features shouldn't exceed 1m
            errors.append(f"{name}: Unusually large dimension ({max_dim:.2f} mm)")

    except Exception as e:
        errors.append(f"{name}: Cannot compute bounding box - {str(e)}")

    # 3. Check volume
    try:
        volume = solid.volume
        if volume < 0.001:  # Less than 0.001 mm³
            errors.append(f"{name}: Volume too small ({volume:.6f} mm³)")
    except Exception as e:
        errors.append(f"{name}: Cannot compute volume - {str(e)}")

    return len(errors) == 0, errors


def _measure_feature(solid, name, feature_type="unknown"):
    """Measure a feature before boolean merge and store in diagnostics.

    This is the "white-box instrumentation" approach - measure features BEFORE
    they are merged, so we have accurate dimensions.

    Args:
        solid: The build123d solid to measure
        name: Feature name (e.g., "base", "lug_right")
        feature_type: Type of feature (e.g., "base", "lug", "rib")
    """
    try:
        bb = solid.bounding_box()
        size_x = bb.max.X - bb.min.X
        size_y = bb.max.Y - bb.min.Y
        size_z = bb.max.Z - bb.min.Z

        measurement = {
            "type": feature_type,
            "size_x": round(size_x, 3),
            "size_y": round(size_y, 3),
            "size_z": round(size_z, 3),
            "min_x": round(bb.min.X, 3),
            "min_y": round(bb.min.Y, 3),
            "min_z": round(bb.min.Z, 3),
            "max_x": round(bb.max.X, 3),
            "max_y": round(bb.max.Y, 3),
            "max_z": round(bb.max.Z, 3),
        }

        try:
            measurement["volume"] = round(solid.volume, 3)
        except:
            measurement["volume"] = None

        _MEASUREMENTS[name] = measurement

    except Exception as e:
        _MEASUREMENTS[name] = {"error": str(e)}


def _save_measurements(filename=None):
    """Save all measurements to JSON file for the repair agent to read.

    If filename is None, uses temp_measurements_{iteration}.json where
    iteration is read from the ITERATION environment variable (default 0).
    """
    if filename is None:
        import os as _os
        iteration = int(_os.environ.get("ITERATION", "0"))
        filename = f"temp_measurements_{iteration}.json"
    try:
        output_data = dict(_MEASUREMENTS)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
        print(f"[DIAGNOSTICS] Saved {len(_MEASUREMENTS)} feature measurements to {filename}")
    except Exception as e:
        print(f"[DIAGNOSTICS] WARNING: Failed to save measurements: {e}")


def _safe_union(a, b, name_a="solid_a", name_b="solid_b", min_overlap=0.1):
    """Safe boolean union with validation.

    Validates both operands before union, checks for overlap, and validates result.

    Returns:
        (success, result, errors): tuple of (bool, result_solid_or_None, list_of_errors)
    """
    all_errors = []

    # Validate both operands
    valid_a, errors_a = _validate_solid(a, name_a)
    valid_b, errors_b = _validate_solid(b, name_b)

    all_errors.extend(errors_a)
    all_errors.extend(errors_b)

    if not valid_a or not valid_b:
        return False, None, all_errors

    # Check for overlap between the two solids
    try:
        bb_a = a.bounding_box()
        bb_b = b.bounding_box()

        # Calculate overlap in each dimension
        overlap_x = min(bb_a.max.X, bb_b.max.X) - max(bb_a.min.X, bb_b.min.X)
        overlap_y = min(bb_a.max.Y, bb_b.max.Y) - max(bb_a.min.Y, bb_b.min.Y)
        overlap_z = min(bb_a.max.Z, bb_b.max.Z) - max(bb_a.min.Z, bb_b.min.Z)

        # Check if there's any overlap
        if overlap_x <= 0 or overlap_y <= 0 or overlap_z <= 0:
            all_errors.append(
                f"{name_a} and {name_b} have no overlap. "
                f"Overlap: X={overlap_x:.2f}, Y={overlap_y:.2f}, Z={overlap_z:.2f} mm. "
                f"Solids must overlap by at least {min_overlap}mm to union successfully."
            )
            return False, None, all_errors

        # Check if overlap is too small
        min_overlap_actual = min(overlap_x, overlap_y, overlap_z)
        if min_overlap_actual < min_overlap:
            all_errors.append(
                f"{name_a} and {name_b} overlap too small ({min_overlap_actual:.3f}mm). "
                f"Minimum recommended: {min_overlap}mm. Consider increasing overlap."
            )
            # Warning only, don't fail

    except Exception as e:
        all_errors.append(f"Cannot check overlap: {str(e)}")

    # Perform the union
    try:
        result = a + b

        # Validate the result
        valid_result, errors_result = _validate_solid(result, f"union({name_a},{name_b})")
        all_errors.extend(errors_result)

        if not valid_result:
            return False, None, all_errors

        return True, result, all_errors

    except Exception as e:
        all_errors.append(f"Boolean union failed: {str(e)}")
        return False, None, all_errors


# === END VALIDATION HELPERS ===
import math, json

# Track cuts that miss the target body (position error detection)
_MISSED_CUTS = []

def _safe_cut(body, tool, label=""):
    """Cut tool from body. Detects missed cuts."""
    try:
        _before = body.volume
        result = body - tool
        _after = result.volume
        if abs(_after - _before) < 0.001:
            _MISSED_CUTS.append(f'MISSED_CUT: {label} — tool had NO effect on body. Position is WRONG.')
        return result
    except Exception:
        _MISSED_CUTS.append(f'CUT_ERROR: {label} — exception during cut')
        return body

def _safe_fillet(solid, edge_selector_fn, radius, label):
    """Apply fillet with radius auto-degradation + GeomType grouping fallback.
    Stage 1: try fillet on all edges with progressive radius reduction.
    Stage 2: if Stage 1 fails (e.g. mixed Circle+Line edges), group edges
    by GeomType and fillet each group independently.  Each group has its
    own try/except, so one group's failure doesn't block others.  This
    handles mixed-type edge selections that ChFi3d can't process in a
    single call.
    """
    try:
        edges = edge_selector_fn(solid)
        if not edges:
            _MISSED_CUTS.append(f'FILLET_FAILED: {label} — no edges matched filter')
            return solid
        _before = solid.volume
        _radii = [radius, radius * 0.5, radius * 0.25, radius * 0.125]
        _last_err = ''
        # Stage 1: try fillet on all edges with progressive radius
        for _r in _radii:
            try:
                result = fillet(edges, radius=_r)
                _after = result.volume
                if abs(_after - _before) < 0.001:
                    _last_err = f'no volume change at radius {_r}'
                    continue
                if _r < radius:
                    _MISSED_CUTS.append(f'FILLET_DEGRADED: {label} — original radius {radius} failed, succeeded at {_r}. Architect should reduce radius_mm to {_r}.')
                return result
            except Exception as _e:
                _last_err = str(_e)
                continue
        # Stage 2: Stage 1 failed → group edges by GeomType and fillet each group
        # Mixed edge types (Circle + Line) often cause ChFi3d to fail in a
        # single call.  Grouping by GeomType lets each homogeneous group
        # fillet independently with its own try/except.
        try:
            from build123d import GeomType
        except ImportError:
            GeomType = None
        _type_groups = {}
        for _edge in edges:
            _gt = None
            try:
                _gt = _edge.geom_type
            except Exception:
                _gt = 'unknown'
            if _gt not in _type_groups:
                _type_groups[_gt] = []
            _type_groups[_gt].append(_edge)
        _result = solid
        _success_groups = 0
        _fail_groups = 0
        _group_fail_reasons = []
        for _gt, _group_edges in _type_groups.items():
            _group_success = False
            _group_err = ''
            for _r in _radii:
                try:
                    _new_result = fillet(_group_edges, radius=_r)
                    if _new_result is not None and abs(_new_result.volume - _result.volume) > 0.001:
                        _result = _new_result
                        _group_success = True
                        if _r < radius:
                            _MISSED_CUTS.append(f'FILLET_DEGRADED: {label} — group {_gt} radius {radius} → {_r}')
                        break
                    else:
                        _group_err = f'no volume change at radius {_r}'
                except Exception as _e:
                    _group_err = str(_e)
                    continue
            if _group_success:
                _success_groups += 1
            else:
                _fail_groups += 1
                _group_fail_reasons.append(str(_gt) + ': ' + _group_err)
        if _success_groups > 0:
            if _fail_groups > 0:
                _reasons_str = '; '.join(_group_fail_reasons[:3])
                _MISSED_CUTS.append(f'FILLET_PARTIAL: {label} — {_success_groups}/{len(_type_groups)} groups OK, {_fail_groups} failed ({_reasons_str})')
            return _result
        # All stages failed — collect diagnostics so Aider knows what to fix
        _diag = [f'FILLET_FAILED: {label} — all radii {_radii} failed (Stage 1 + Stage 2). Last: {_last_err}']
        _diag.append(f'  Selected {len(edges)} edges in {len(_type_groups)} GeomType groups.')
        try:
            for _i, _e in enumerate(list(edges)[:3]):
                _bb = _e.bounding_box()
                _diag.append(f'  edge[{_i}]: X=[{_bb.min.X:.1f}..{_bb.max.X:.1f}] Y=[{_bb.min.Y:.1f}..{_bb.max.Y:.1f}] Z=[{_bb.min.Z:.1f}..{_bb.max.Z:.1f}]')
            _diag.append('  Likely cause: edges at degenerate junctions (cutout/lug boundaries) where only 2 faces meet.')
            _diag.append('  Root cause: a complete Circle edge may have been split into multiple arc segments')
            _diag.append('  by prior boolean operations (e.g. backplate outer circle split into 12 arcs by')
            _diag.append('  12 blade unions). ChFi3d cannot fillet arc segments at degenerate junctions.')
            _diag.append('  Suggestion 1: use SEMANTIC selectors (.filter_by(Axis.Z), length > N), not hardcoded bbox coords.')
            _diag.append('  Suggestion 2: if the fillet region (these edges bounding box) does NOT overlap with')
            _diag.append('  the region of prior boolean operations, consider MOVING this fillet step BEFORE')
            _diag.append('  the boolean unions/cuts — fillet the complete Circle first, then union internal')
            _diag.append('  features. See Iron Rule 7 exception in the repair prompt.')
        except Exception:
            pass
        _MISSED_CUTS.append('\n'.join(_diag))
        return solid
    except Exception as _e:
        _MISSED_CUTS.append(f'FILLET_FAILED: {label} — {_e}')
        return solid

def _safe_chamfer(solid, edge_selector_fn, length, label):
    """Apply chamfer with length auto-degradation + GeomType grouping fallback.
    Same Stage 1 + Stage 2 pattern as _safe_fillet: try chamfer on all
    edges first, then group by GeomType if Stage 1 fails.
    """
    try:
        edges = edge_selector_fn(solid)
        if not edges:
            _MISSED_CUTS.append(f'CHAMFER_FAILED: {label} — no edges matched filter')
            return solid
        _before = solid.volume
        _lens = [length, length * 0.5, length * 0.25, length * 0.125]
        _last_err = ''
        # Stage 1: try chamfer on all edges with progressive length
        for _l in _lens:
            try:
                result = chamfer(edges, length=_l)
                _after = result.volume
                if abs(_after - _before) < 0.001:
                    _last_err = f'no volume change at length {_l}'
                    continue
                if _l < length:
                    _MISSED_CUTS.append(f'CHAMFER_DEGRADED: {label} — original length {length} failed, succeeded at {_l}. Architect should reduce chamfer_distance_mm to {_l}.')
                return result
            except Exception as _e:
                _last_err = str(_e)
                continue
        # Stage 2: Stage 1 failed → group edges by GeomType and chamfer each group
        try:
            from build123d import GeomType
        except ImportError:
            GeomType = None
        _type_groups = {}
        for _edge in edges:
            _gt = None
            try:
                _gt = _edge.geom_type
            except Exception:
                _gt = 'unknown'
            if _gt not in _type_groups:
                _type_groups[_gt] = []
            _type_groups[_gt].append(_edge)
        _result = solid
        _success_groups = 0
        _fail_groups = 0
        _group_fail_reasons = []
        for _gt, _group_edges in _type_groups.items():
            _group_success = False
            _group_err = ''
            for _l in _lens:
                try:
                    _new_result = chamfer(_group_edges, length=_l)
                    if _new_result is not None and abs(_new_result.volume - _result.volume) > 0.001:
                        _result = _new_result
                        _group_success = True
                        if _l < length:
                            _MISSED_CUTS.append(f'CHAMFER_DEGRADED: {label} — group {_gt} length {length} → {_l}')
                        break
                    else:
                        _group_err = f'no volume change at length {_l}'
                except Exception as _e:
                    _group_err = str(_e)
                    continue
            if _group_success:
                _success_groups += 1
            else:
                _fail_groups += 1
                _group_fail_reasons.append(str(_gt) + ': ' + _group_err)
        if _success_groups > 0:
            if _fail_groups > 0:
                _reasons_str = '; '.join(_group_fail_reasons[:3])
                _MISSED_CUTS.append(f'CHAMFER_PARTIAL: {label} — {_success_groups}/{len(_type_groups)} groups OK, {_fail_groups} failed ({_reasons_str})')
            return _result
        _MISSED_CUTS.append(f'CHAMFER_FAILED: {label} — all lengths {_lens} failed (Stage 1 + Stage 2). Last: {_last_err}. Selected {len(edges)} edges in {len(_type_groups)} groups. Use SEMANTIC selectors, not hardcoded coords. Root cause: a complete Circle edge may have been split into arc segments by prior boolean operations. If the chamfer region does NOT overlap with prior boolean regions, consider moving this chamfer step BEFORE the boolean unions/cuts — see Iron Rule 7 exception.')
        return solid
    except Exception as _e:
        _MISSED_CUTS.append(f'CHAMFER_FAILED: {label} — {_e}')
        return solid

PRINCIPAL_EXTENT_X_MM = 848.5129577095579
PRINCIPAL_EXTENT_Y_MM = 78.34732557851368
PRINCIPAL_EXTENT_Z_MM = 49.1558858676166
ELLIPSE_MAJOR_RADIUS_MM = 39.17366278925684
ELLIPSE_MINOR_RADIUS_MM = 24.5779429338083
ELLIPSE_CENTER_Y_MM = 39.17366278925684
ELLIPSE_CENTER_Z_MM = 24.5779429338083

# --- Derived coordinates (computed, not LLM-provided) ---
_base_half_x = 21.0
_base_half_y = 21.0
_base_thickness = 5.0


def gen_step():
    # --- Generated solids ---

    # Sketch: sk_tank_body_cross_section
    sk_tank_body_cross_section = Ellipse(5, 5)
    solid_0 = extrude(Plane.YZ * Pos(39.17366278925684, 24.5779429338083) * sk_tank_body_cross_section, amount=848.5129577095579, dir=(1, 0, 0))
    _measure_feature(solid_0, 'step-01-extrude-tank-body', 'extrude')

    _measure_feature(solid_0, 'overall', 'final_assembly')
    # --- Write missed-cut warnings (position error detection) ---
    if _MISSED_CUTS:
        import os as _os
        _iteration = int(_os.environ.get('ITERATION', '0'))
        with open(f'temp_missed_{_iteration}.json', 'w') as _f:
            json.dump(_MISSED_CUTS, _f)
    # --- Return result for cadpy.generation ---
    export_step(solid_0, r"temp_output_0.step")
    export_stl(solid_0, r"temp_output_0.stl", tolerance=0.01, angular_tolerance=0.1)
    # --- Save feature measurements (white-box instrumentation) ---
    _save_measurements()  # Uses ITERATION env var
    return {"shape": solid_0}
