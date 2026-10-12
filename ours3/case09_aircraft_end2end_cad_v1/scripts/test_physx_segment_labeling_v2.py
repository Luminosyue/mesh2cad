import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).with_name("physx_segment_labeling_v2.py")
SPEC = importlib.util.spec_from_file_location("segment_v2", SCRIPT)
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_rejects_whole_object_parts_table():
    assert M.contract_check("Parts:\nl_0: wing", None, "P3_SEG_000") == (
        False,
        "WHOLE_OBJECT_PARTS_TABLE",
    )


def test_rejects_multiple_parts_json():
    value = {"parts": [{"name": "a"}, {"name": "b"}]}
    assert M.contract_check(json.dumps(value), value, "P3_SEG_000") == (
        False,
        "MULTI_PART_JSON",
    )


def test_rejects_single_parts_wrapper_too():
    value = {"parts": [{"name": "a"}]}
    assert M.contract_check(json.dumps(value), value, "P3_SEG_000")[0] is False


def test_rejects_l_index_json():
    value = {"l_0": "wing", "p3_segment_id": "P3_SEG_000"}
    assert M.contract_check(json.dumps(value), value, "P3_SEG_000")[0] is False


def test_accepts_exactly_one_bound_object():
    value = {"p3_segment_id": "P3_SEG_000", "generic_part_label": "main_wing"}
    assert M.contract_check(json.dumps(value), value, "P3_SEG_000") == (True, "OK")


def test_strong_view_disagreement_is_unknown():
    label, _, status = M.vote(
        ["main_wing", "propeller", "fuselage", "dorsal_feature"],
        [0.8, 0.8, 0.8, 0.8],
    )
    assert label == "unknown"
    assert status == "UNKNOWN"


def test_geometry_constraints_are_generic_not_gt_lookup():
    source = SCRIPT.read_text(encoding="utf-8")
    body = source.split("def geometry_role_constraint", 1)[1].split("def infer", 1)[0]
    assert "EVAL_GT" not in body


def test_no_parts_table_binding_in_infer():
    source = SCRIPT.read_text(encoding="utf-8")
    body = source.split("def infer", 1)[1].split("def main", 1)[0]
    assert "l_0" not in body
    assert "parsed.get(\"parts\")" not in body

