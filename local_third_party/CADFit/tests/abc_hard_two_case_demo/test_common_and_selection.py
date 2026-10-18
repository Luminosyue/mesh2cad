import csv
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMON_PATH = ROOT / "scripts" / "abc_hard_two_case_demo" / "common.py"
SELECT_PATH = ROOT / "scripts" / "abc_hard_two_case_demo" / "select_two_cases.py"


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


common = load(COMMON_PATH)
sys.path.insert(0, str(COMMON_PATH.parent))
select = load(SELECT_PATH)


def test_abc_id_parse():
    assert common.parse_abc_id("00012345_hash.step") == "00012345"
    assert common.parse_abc_id("abc_0000_stl2_v00/00054321.stl") == "00054321"
    assert common.parse_abc_id("no-id.stl") is None


def test_hard_boundaries():
    assert not common.is_hard_face_count(150)
    assert common.is_hard_face_count(151)
    assert common.is_hard_face_count(1500)
    assert not common.is_hard_face_count(1501)


def test_pairing_and_no_triangle_hard(tmp_path):
    step = tmp_path / "step" / "0000"
    stl = tmp_path / "stl2" / "0000"
    step.mkdir(parents=True)
    stl.mkdir(parents=True)
    (step / "00000001_hash.step").write_text("x")
    (stl / "00000001_hash.stl").write_text("y")
    idx = tmp_path / "m"
    matched, total = load(ROOT / "scripts" / "abc_hard_two_case_demo" / "index_abc_files.py").build_index(step.parent, stl.parent, idx)
    assert matched == 1
    rows = common.read_csv_dicts(idx / "abc_file_index.csv")
    assert rows[0]["abc_id"] == "00000001"
    assert not common.is_hard_face_count(10_000)  # triangle count is irrelevant to Hard status


def test_case_a_and_b_do_not_repeat():
    rows = [
        {"abc_id": "00000001", "step_face_count": "250", "triangle_count": "50000", "is_watertight": "True", "connected_component_count": "1", "step_path": "a", "stl_path": "a"},
        {"abc_id": "00000002", "step_face_count": "1000", "triangle_count": "40000", "is_watertight": "True", "connected_component_count": "1", "step_path": "b", "stl_path": "b"},
    ]
    a, b = select.choose(rows)
    assert a["abc_id"] != b["abc_id"]


def test_successful_outputs(tmp_path):
    for name in ["best_greedy_parallel_iterative.py", "best_greedy_parallel_iterative.stl", "final_iou.json"]:
        (tmp_path / name).write_text("x")
    assert common.successful_outputs(tmp_path)


def test_skip_existing_logic(tmp_path):
    assert not common.successful_outputs(tmp_path)
    (tmp_path / "best_greedy_parallel_iterative.py").write_text("x")
    (tmp_path / "best_greedy_parallel_iterative.stl").write_text("x")
    (tmp_path / "final_iou.json").write_text("x")
    assert common.successful_outputs(tmp_path)


def test_summary_handles_failure(tmp_path, monkeypatch):
    # A failed run can still be represented in summary fields without raising
    # through the CSV writer helper.
    rows = [{"case_name": "case_a", "abc_id": "1", "status": "process_error", "error": "failed"}]
    out = tmp_path / "summary.csv"
    common.write_csv_dicts(out, rows, ["case_name", "abc_id", "status", "error"])
    with out.open() as f:
        assert list(csv.DictReader(f))[0]["status"] == "process_error"


def test_step_export_script_exists():
    assert (ROOT / "scripts" / "abc_hard_two_case_demo" / "export_generated_step.py").exists()
