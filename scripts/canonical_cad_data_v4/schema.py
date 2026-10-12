"""Canonical CAD record schema. All V4 modules update this schema only."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

CANONICAL_RECORD_TEMPLATE: dict[str, Any] = {
    "cad_id": "",
    "source": "",
    "source_id": "",
    "source_path": "",
    "program_available": False,
    "step_available": False,
    "canonical_program_path": None,
    "canonical_step_path": None,
    "canonical_mesh_path": None,
    "operations": [],
    "num_operations": 0,
    "has_sketch": False,
    "has_extrude": False,
    "has_cut": False,
    "has_join": False,
    "has_revolve": False,
    "has_loft": False,
    "has_sweep": False,
    "has_fillet": False,
    "has_chamfer": False,
    "has_shell": False,
    "has_mirror": False,
    "has_pattern": False,
    "num_line": 0,
    "num_circle": 0,
    "num_arc": 0,
    "num_ellipse": 0,
    "num_bspline": 0,
    "bbox_extent": None,
    "volume": None,
    "surface_area": None,
    "dsl_execute": None,
    "step_reload": None,
    "geometry_gate": None,
    "complexity": None,
    "source_sha256": None,
    "canonical_dsl_sha256": None,
    "geometry_fingerprint": None,
    "duplicate_group": None,
    "split": None,
    "status": "candidate",
    "failure_reason": None,
    # V4 extensions (still one schema)
    "aircraft_relevance": 0,
    "edge_source": None,
    "c2_frozen": None,
    "converter_hash": None,
    "pipeline_version": "canonical_cad_data_v4",
}

VALID_SOURCES = ("DEEPCAD", "FUSION360", "CADFS")

STATUS_VALUES = (
    "candidate",
    "converted",
    "unsupported_operation",
    "dsl_execute_fail",
    "step_reload_fail",
    "geometry_fail",
    "surface_fail",
    "edge_fail",
    "curve_fail",
    "c2_fail",
    "clean",
    "duplicate",
    "missing_source",
)


def make_cad_id(source: str, source_id: str) -> str:
    src = source.upper()
    if src not in VALID_SOURCES:
        raise ValueError(f"unknown source: {source}")
    sid = str(source_id).replace("/", "_").replace(" ", "_")
    return f"{src}_{sid}"


def new_record(**kwargs: Any) -> dict[str, Any]:
    rec = deepcopy(CANONICAL_RECORD_TEMPLATE)
    rec.update(kwargs)
    if rec.get("cad_id") and rec.get("source"):
        prefix = rec["source"].upper() + "_"
        if not rec["cad_id"].startswith(prefix):
            raise ValueError(f"cad_id {rec['cad_id']!r} does not match source {rec['source']}")
    return rec
