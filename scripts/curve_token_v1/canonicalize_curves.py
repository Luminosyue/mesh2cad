#!/usr/bin/env python3
"""Object-level normalization for Track B curves.

Normalization contract is *read* from Track A and re-implemented here; Track A's
`scripts/deepcad/cad_canonical.py` is never imported or modified.

    p_canonical = s * p_source + t
    s = target_diagonal / source_bbox_diagonal      (target_diagonal = 6.0)
    t = -s * source_bbox_min

Under a uniform-scale + translation map:
  - points (origin, center, control points, endpoints)  ->  s*p + t
  - lengths (radius, curve length)                      ->  s*l
  - unit directions (direction, normal, axes)           ->  unchanged
  - knots / multiplicities / weights / degree           ->  unchanged
  - LINE parameter range                                ->  scaled (arc-length param)
  - CIRCLE/ELLIPSE parameter range (angles)             ->  unchanged
  - BSPLINE parameter range                             ->  unchanged (knots unchanged)

World-space parameters are never overwritten; the normalized block is written
alongside them.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .config import NORMALIZATION_VERSION

DEFAULT_TARGET_DIAGONAL = 6.0


@dataclass
class Normalization:
    source_bbox_min: list[float]
    source_bbox_max: list[float]
    source_diagonal: float
    target_diagonal: float
    scale: float
    translation: list[float]
    source: str
    normalization_version: str = NORMALIZATION_VERSION

    @property
    def s(self) -> float:
        return float(self.scale)

    @property
    def t(self) -> np.ndarray:
        return np.asarray(self.translation, dtype=np.float64)

    def points(self, p) -> np.ndarray:
        p = np.asarray(p, dtype=np.float64)
        return self.s * p + self.t

    def lengths(self, l):  # noqa: E741
        return self.s * np.asarray(l, dtype=np.float64)

    def to_json(self) -> dict:
        return asdict(self)


def from_track_a_transform(path: Path) -> Normalization:
    """Reuse Track A's frozen coordinate_transform.json verbatim (read-only).

    This is what keeps future Curve Tokens in the same coordinate frame as the
    existing Surface/Edge tokens.
    """
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Normalization(
        source_bbox_min=[float(x) for x in d["source_bbox_min"]],
        source_bbox_max=[float(x) for x in d["source_bbox_max"]],
        source_diagonal=float(d["source_diagonal"]),
        target_diagonal=float(d["target_diagonal"]),
        scale=float(d["scale"]),
        translation=[float(x) for x in d["translation"]],
        source=f"track_a:{path}",
    )


def from_bbox(
    bbox_min, bbox_max, target_diagonal: float = DEFAULT_TARGET_DIAGONAL
) -> Normalization:
    """Fallback with the same math, derived from the B-Rep bbox.

    Note this is not bit-identical to Track A, whose bbox comes from the sampled
    surface point cloud rather than the exact solid; `source` records which was used.
    """
    mn = np.asarray(bbox_min, dtype=np.float64)
    mx = np.asarray(bbox_max, dtype=np.float64)
    diag = float(np.linalg.norm(mx - mn))
    scale = float(target_diagonal / diag) if diag > 0 and target_diagonal > 0 else 1.0
    return Normalization(
        source_bbox_min=mn.tolist(),
        source_bbox_max=mx.tolist(),
        source_diagonal=diag,
        target_diagonal=float(target_diagonal),
        scale=scale,
        translation=(-scale * mn).tolist(),
        source="curve_token_v1:brep_bbox",
    )


def resolve_normalization(
    track_a_transform: Path | None,
    bbox_min,
    bbox_max,
    target_diagonal: float = DEFAULT_TARGET_DIAGONAL,
) -> Normalization:
    if track_a_transform is not None and Path(track_a_transform).is_file():
        try:
            return from_track_a_transform(Path(track_a_transform))
        except Exception:  # noqa: BLE001
            pass
    return from_bbox(bbox_min, bbox_max, target_diagonal)


# ------------------------------------------------- parameter-block mapping ---
_POINT_KEYS = frozenset({"origin", "center"})
_POINTS_KEYS = frozenset({"control_points"})
_LENGTH_KEYS = frozenset({"radius", "major_radius", "minor_radius"})
_DIR_KEYS = frozenset(
    {
        "direction",
        "normal",
        "x_axis",
        "y_axis",
        "y_axis_from_cross",
        "major_axis",
        "minor_axis",
        "minor_axis_from_cross",
    }
)
_PASSTHROUGH_KEYS = frozenset(
    {
        "degree",
        "knots",
        "multiplicities",
        "num_knots",
        "num_control_points",
        "knot_multiplicity_sum",
        "weights",
        "is_rational",
        "is_periodic",
        "is_closed_geom",
        "native_form",
    }
)
# BSpline/Bezier knots are unchanged, so the geom param range is too.
_PASSTHROUGH_PARAM_KEYS = frozenset({"geom_u_start", "geom_u_end"})


def normalize_parameters(curve_type: str, params: dict, nz: Normalization) -> dict:
    """Map a world-space parameter block into normalized space."""
    if not params:
        return {}
    out: dict = {}
    for key, val in params.items():
        if key in _POINT_KEYS:
            out[key] = nz.points(val).tolist()
        elif key in _POINTS_KEYS:
            out[key] = nz.points(np.asarray(val, dtype=np.float64)).tolist()
        elif key in _LENGTH_KEYS:
            out[key] = float(nz.s * float(val))
        elif key in _DIR_KEYS or key in _PASSTHROUGH_KEYS or key in _PASSTHROUGH_PARAM_KEYS:
            out[key] = val
        else:
            out[key] = val
    return out


def normalize_param_range(curve_type: str, u0: float, u1: float, nz: Normalization) -> tuple[float, float]:
    """LINE parameters are arc length and therefore scale; angles and knots do not."""
    if curve_type == "LINE":
        return float(nz.s * u0), float(nz.s * u1)
    return float(u0), float(u1)


def canonicalize_curve_record(record: dict, nz: Normalization) -> dict:
    """Attach the normalized view to a curve record, leaving world-space intact."""
    ctype = record["curve_type"]
    record["normalized_parameters"] = normalize_parameters(ctype, record.get("world_parameters", {}), nz)
    nu0, nu1 = normalize_param_range(ctype, record["u_start"], record["u_end"], nz)
    record["normalized"] = {
        "start_point": nz.points(record["start_point"]).tolist(),
        "end_point": nz.points(record["end_point"]).tolist(),
        # unit tangents are invariant under uniform scale + translation
        "start_tangent": record["start_tangent"],
        "end_tangent": record["end_tangent"],
        "u_start": nu0,
        "u_end": nu1,
        "length": float(nz.s * record["length"]),
    }
    return record


def canonicalize_curves(data: dict, nz: Normalization) -> dict:
    for rec in data.get("curves", []):
        canonicalize_curve_record(rec, nz)
    data["normalization"] = nz.to_json()
    return data
