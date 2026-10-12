from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "generalization/geometry_decomposition/decomposition_router.py"


def load_router():
    from generalization.geometry_decomposition.decomposition_router import decompose_coarse_part
    return decompose_coarse_part


def box(extents, center=(0.0, 0.0, 0.0)):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def test_significant_connected_component_split():
    router = load_router()
    mesh = trimesh.util.concatenate([box((2, 0.2, 0.2), (-2, 0, 0)), box((2, 0.2, 0.2), (2, 0, 0))])
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert len(result["refined_parts"]) == 2
    assert result["split_reason"] == "SIGNIFICANT_CONNECTED_COMPONENTS"


def test_tiny_component_not_split():
    router = load_router()
    big = box((2, 2, 0.2))
    tiny = box((0.01, 0.01, 0.01), (4, 4, 4))
    mesh = trimesh.util.concatenate([big, tiny])
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert len(result["refined_parts"]) == 1


def test_planar_patch_and_thin_plate_detection():
    router = load_router()
    mesh = box((5, 2, 0.08))
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert result["refined_parts"][0].geometry_regime in {"THIN_PLATE", "PLANAR_PATCH"}


def test_cylindrical_rod_detection():
    router = load_router()
    mesh = trimesh.creation.cylinder(radius=0.2, height=5.0, sections=32)
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert result["refined_parts"][0].geometry_regime in {"CYLINDRICAL_ROD", "LINEAR_ROD"}


def test_mixed_plate_rod_is_not_direct_v6():
    router = load_router()
    mesh = trimesh.util.concatenate([box((3, 2, 0.1)), trimesh.creation.cylinder(radius=0.2, height=3.0)])
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert all(not part.backend_eligibility["mixed_direct_v6"] for part in result["refined_parts"])


def test_repetition_group_detection():
    router = load_router()
    parts = [box((0.2, 0.2, 1.0), (index * 0.7, 0, 0)) for index in range(5)]
    mesh = trimesh.util.concatenate(parts)
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert result["repetition_groups"] or len(result["refined_parts"]) >= 5


def test_refined_ids_are_deterministic():
    router = load_router()
    mesh = box((2, 1, 0.2))
    ids = list(range(len(mesh.faces)))
    first = [part.refined_part_id for part in router("COARSE", mesh, [0], ids)["refined_parts"]]
    second = [part.refined_part_id for part in router("COARSE", mesh, [0], ids)["refined_parts"]]
    assert first == second


def test_single_freeform_is_kept_single():
    router = load_router()
    mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    result = router("COARSE", mesh, [0], list(range(len(mesh.faces))))
    assert len(result["refined_parts"]) == 1
