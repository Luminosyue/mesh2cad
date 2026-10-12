import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_case09_style_fullstack_v6_2"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_canary_passed_three_of_three():
    value = load(OUT / "artifacts/canary_summary.json")
    assert value["MAC_CANARY_PASS"]
    assert value["MAC_CANARIES_COMPLETED"] == 3
    assert all(row["HTTP_STATUS"] == 200 and row["valid_step"] for row in value["CANARY_RESULTS"])


def test_batch_stopped_on_first_403():
    value = load(OUT / "artifacts/resume_progress.json")
    assert value["http_403"] == 1
    assert value["stopped"]


def test_quota_error_recorded():
    path = BASE / "08_multi_candidate_mac/CASE_00/CADPART_003/CANDIDATE_02_SEMANTIC_FREEFORM_SKINS/mac_response.json"
    value = load(path)
    assert value["HTTP_STATUS"] == 403
    assert "AllocationQuota.FreeTierOnly" in value["error"]


def test_no_v6_2_fallback_created():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["FALLBACK_CANDIDATES_CREATED_V6_2"] == 0


def test_real_mac_accounting():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["REAL_MAC_CANDIDATES"] >= 16
    assert value["REAL_MAC_STEP_SUCCESS"] >= 13
    assert value["REAL_MAC_STEP_SUCCESS"] <= value["REAL_MAC_CANDIDATES"]


def test_dual_modal_truthful():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["DUAL_MODAL_CONTEXT_ACTUALLY_USED"]
    assert value["TTS_ACTUALLY_USED"]


def test_no_partial_assembly():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["CASES_WITH_FRESH_ASSEMBLY"] == 0
    assert value["SHADED_CONTACT_SHEET"] is None
    assert value["TRUE_EDGE_CONTACT_SHEET"] is None


def test_no_upstream_rerun():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["P3_RERUN_CASES"] == 0
    assert value["PHYSX_RERUN_CASES"] == 0


def test_old_step_not_reconstruction_input():
    assert not load(OUT / "artifacts/final_summary.json")["OLD_STEP_USED_AS_INPUT"]


def test_case09_unchanged():
    path = ROOT / "case09_fullstack_mesh2cad_mac_v6/10_assembly/CASE09_fullstack_mesh2cad_mac_v6.step"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "c0f3b83a08966d10e54554316e1f2fb826f63563c5edc799489ce063a528ba97"


def test_selected_best_registry_unchanged():
    old = load(BASE / "artifacts/best_result_registry.json")
    new = load(OUT / "artifacts/best_result_registry.json")
    for case_id in old["cases"]:
        assert new["cases"][case_id]["SELECTED_BEST"] == old["cases"][case_id]["SELECTED_BEST"]


def test_safe_key_fingerprint_only():
    fingerprint = load(OUT / "artifacts/final_summary.json")["MAC_KEY_FINGERPRINT"]
    assert fingerprint.startswith("sha256:")
    assert len(fingerprint) == 19
