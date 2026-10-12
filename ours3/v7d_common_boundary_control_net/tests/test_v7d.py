from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_no_part_id_fixed_seam_rules():
    text = "\n".join(path.read_text() for path in (ROOT / "boundary_control_net").glob("*.py"))
    assert "if part_id" not in text
    assert "FUSELAGE → endpoint" not in text


def test_no_mesh_section_or_hidden_boundary_detection():
    text = (ROOT / "scripts/run_v7d.py").read_text()
    assert "mesh.section" not in text
    assert 'extract_boundaries(compound([constrained["face_a"], constrained["face_b"]]), pid)' in text
    assert "extract_boundaries(source" not in text


def test_no_forced_sewing_or_fake_caps():
    production = list((ROOT / "boundary_control_net").glob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    text = "\n".join(path.read_text() for path in production)
    forbidden_sewing_api = "BRepBuilderAPI" + "_Sewing"
    assert forbidden_sewing_api not in text
    assert '"convex_hull_generated": False' in text


def test_one_shared_edge_object_is_replaced_into_both_faces():
    text = (ROOT / "boundary_control_net/topology_preview.py").read_text()
    assert "reshape_a.Replace(old_a, edge.Oriented(old_a.Orientation()))" in text
    assert "reshape_b.Replace(old_b, edge.Oriented(old_b.Orientation()))" in text


def test_common_pole_row_is_written_to_both_surfaces():
    text = (ROOT / "boundary_control_net/common_boundary_control_net.py").read_text()
    assert "surface_a.SetPole(index, va, pole)" in text
    assert "surface_b.SetPole(index, vb, pole)" in text
