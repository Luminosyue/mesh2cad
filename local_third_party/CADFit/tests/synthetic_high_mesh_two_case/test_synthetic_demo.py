import csv
import json
import subprocess
import sys
from pathlib import Path

import cadquery as cq
import trimesh


ROOT = Path(__file__).resolve().parents[2]
CASES = ["case_a_flange", "case_b_bracket"]


def case_dir(case):
    return ROOT / "datasets" / "synthetic_high_mesh_two_case_v1" / case


def art_dir(case):
    return ROOT / "artifacts" / "synthetic_high_mesh_two_case_v1" / case


def test_ground_truth_py_executes():
    for case in CASES:
        p = case_dir(case) / "ground_truth.py"
        assert p.exists()
        r = subprocess.run([sys.executable, str(p)], cwd=p.parent, capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr


def test_steps_reopen():
    for case in CASES:
        wp = cq.importers.importStep(str(case_dir(case) / "ground_truth.step"))
        assert len(wp.val().Solids()) == 1
        assert len(wp.val().Faces()) > 0


def test_stls_load_watertight_single_volume():
    for case in CASES:
        mesh = trimesh.load(case_dir(case) / "input_high_mesh.stl", force="mesh")
        assert len(mesh.faces) > 0
        assert mesh.is_watertight
        assert len(mesh.split(only_watertight=False)) == 1
        assert abs(mesh.volume) > 0


def test_input_dir_is_isolated_stl_only():
    for case in CASES:
        p = ROOT / "outputs" / "synthetic_high_mesh_two_case_v1" / case / "cadfit_input"
        if p.exists():
            names = {x.name for x in p.iterdir()}
            assert "input_high_mesh.stl" in names
            assert "ground_truth.py" not in names
            assert "ground_truth.step" not in names


def test_cadfit_command_uses_stl_directory():
    audit = ROOT / "artifacts" / "synthetic_high_mesh_two_case_v1" / "cadfit_command_audit.md"
    assert audit.exists()
    text = audit.read_text()
    assert "run_pipeline.py <isolated_input_dir>" in text
    assert "PRIOR_MODE=no_prior" in text


def test_summary_fields_complete():
    p = ROOT / "artifacts" / "synthetic_high_mesh_two_case_v1" / "demo_summary.csv"
    assert p.exists()
    rows = list(csv.DictReader(p.open()))
    expected = {
        "case_name", "ground_truth_step_faces", "input_vertices", "input_triangles",
        "input_watertight", "cadfit_status", "prior_mode", "iou", "runtime_seconds",
        "generated_program_lines", "extrude_count", "revolve_count", "union_count",
        "cut_count", "fillet_count", "chamfer_count", "reconstructed_step_success", "error",
    }
    assert rows
    assert expected.issubset(rows[0].keys())


def test_comparison_images_exist_for_successes():
    for case in CASES:
        status = json.loads((art_dir(case) / "run_status.json").read_text()) if (art_dir(case) / "run_status.json").exists() else {}
        if status.get("status") == "success":
            assert (art_dir(case) / "comparison.png").exists()


def test_success_generated_code_executes_and_iou_parses():
    for case in CASES:
        status_p = art_dir(case) / "run_status.json"
        if not status_p.exists() or json.loads(status_p.read_text()).get("status") != "success":
            continue
        script = art_dir(case) / "generated_cad.py"
        assert script.exists()
        r = subprocess.run([sys.executable, str(script)], cwd=script.parent, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr
        iou = json.loads((art_dir(case) / "final_iou.json").read_text())
        assert "final_iou" in iou
