#!/usr/bin/env python3
"""Tests for CAD_STYLE_RENDER_UPGRADE_V1."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/render_upgrade_v1")
CASE05 = ROOT / "case05"
REAL03 = ROOT / "real03"


def _metrics(case_dir: Path):
    p = case_dir / "metrics" / "render_metrics.json"
    assert p.is_file(), p
    return json.loads(p.read_text())


def _art(case_dir: Path, name: str) -> Path:
    return case_dir / "artifacts" / name


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_source_render_uses_faces(case_dir, prefix):
    m = _metrics(case_dir)
    assert m["SOURCE_TRIANGLES"] > 1000
    p = _art(case_dir, "source_shaded.png")
    assert p.is_file() and p.stat().st_size > 10000


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_cad_render_uses_step_only(case_dir, prefix):
    m = _metrics(case_dir)
    assert m["RIGHT_RENDER_USES_SOURCE_MESH"] is False
    assert m["RIGHT_RENDER_SOURCE"] == "STEP_ONLY"
    assert "ASSORTED_VEGETABLE_SET.obj" not in Path(m["STEP_PATH"]).name
    assert "30_CONSTRUCTION_SET.obj" not in Path(m["STEP_PATH"]).name
    assert Path(m["STEP_PATH"]).suffix.lower() == ".step"


@pytest.mark.parametrize("case_dir", [CASE05, REAL03])
def test_step_reload_success(case_dir):
    m = _metrics(case_dir)
    assert m["STEP_RELOAD_SUCCESS"] is True


@pytest.mark.parametrize("case_dir", [CASE05, REAL03])
def test_tessellation_has_faces(case_dir):
    m = _metrics(case_dir)
    assert m["CAD_TESSELLATED_TRIANGLE_COUNT"] > 1000


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_shaded_output_exists(case_dir, prefix):
    assert _art(case_dir, "source_shaded.png").is_file()
    assert _art(case_dir, "cad_shaded_edges.png").is_file()
    assert _art(case_dir, f"{prefix}_source_vs_cad_shaded_edges.png").is_file()


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_edge_overlay_output_exists(case_dir, prefix):
    m = _metrics(case_dir)
    assert "SHARP" in m["EDGE_RENDER_MODE"] or "SILHOUETTE" in m["EDGE_RENDER_MODE"] or "BREP" in m["EDGE_RENDER_MODE"]
    assert _art(case_dir, "cad_shaded_edges.png").stat().st_size > 10000


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_overlay_output_exists(case_dir, prefix):
    assert _art(case_dir, f"{prefix}_overlay_transparent.png").is_file()


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_exploded_output_exists(case_dir, prefix):
    m = _metrics(case_dir)
    assert m["EXPLODED_VIEW_ENABLED"] is True
    assert _art(case_dir, f"{prefix}_exploded_assembly.png").is_file()


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_section_output_exists(case_dir, prefix):
    m = _metrics(case_dir)
    assert m["SECTION_VIEW_ENABLED"] is True
    assert _art(case_dir, f"{prefix}_section_view.png").is_file()


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_provenance_panel_exists(case_dir, prefix):
    m = _metrics(case_dir)
    assert m["PROVENANCE_PANEL_ENABLED"] is True
    p = _art(case_dir, f"{prefix}_provenance_panel.png")
    assert p.is_file() and p.stat().st_size > 5000


@pytest.mark.parametrize("case_dir", [CASE05, REAL03])
def test_right_render_not_source_mesh(case_dir):
    m = _metrics(case_dir)
    assert m["RIGHT_RENDER_USES_SOURCE_MESH"] is False
    assert m["RIGHT_RENDER_SOURCE"] == "STEP_ONLY"
    # CAD triangle count should differ from source (not a copy)
    assert m["CAD_TESSELLATED_TRIANGLE_COUNT"] != m["SOURCE_TRIANGLES"]


@pytest.mark.parametrize("case_dir,prefix", [(CASE05, "CASE05"), (REAL03, "REAL03")])
def test_same_camera_side_by_side(case_dir, prefix):
    p = _art(case_dir, f"{prefix}_source_vs_cad_shaded_edges.png")
    assert p.is_file() and p.stat().st_size > 20000
    four = _art(case_dir, f"{prefix}_four_view_render_sheet.png")
    assert four.is_file()


def test_real03_feature_closeup_exists():
    p = _art(REAL03, "REAL03_feature_closeups.png")
    assert p.is_file() and p.stat().st_size > 10000
