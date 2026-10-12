import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_case09_style_fullstack_v6_2"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_canary_stopped_after_first_failure():
    value = load(OUT / "artifacts/canary_summary.json")
    assert value["MAC_CANARIES_COMPLETED"] == 1
    assert not value["MAC_CANARY_PASS"]
    directories = list((OUT / "01_mac_canary").glob("CANARY_*"))
    assert len(directories) == 1
    assert "CASE_01" in directories[0].name


def test_http_400_model_not_found_single_attempt():
    value = load(OUT / "artifacts/canary_summary.json")["CANARY_RESULTS"][0]
    assert value["HTTP_STATUS"] == 400
    assert value["HTTP_ATTEMPTS_PER_STAGE"] == 1
    assert value["failure_stage"] == "VISUAL_CONTEXT"
    assert "model_not_found" in value["error"]


def test_no_generated_program_or_step():
    directory = next((OUT / "01_mac_canary").glob("CANARY_*"))
    assert not (directory / "generated_code.py").exists()
    assert not (directory / "candidate.step").exists()


def test_no_batch_or_fallback_started():
    value = load(OUT / "artifacts/final_summary.json")
    assert not value["BATCH_STARTED"]
    assert not value["FALLBACK_STARTED"]
    assert value["REAL_MAC_CANDIDATES"] == 0
    assert value["REAL_MAC_PROGRAMS_EXECUTED"] == 0


def test_no_p3_or_physx_rerun():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["P3_RERUN_CASES"] == 0
    assert value["PHYSX_RERUN_CASES"] == 0
    assert value["UPSTREAM_SOURCE_DERIVED_PARTS_REUSED"] == 132


def test_case09_unchanged():
    path = ROOT / "case09_fullstack_mesh2cad_mac_v6/10_assembly/CASE09_fullstack_mesh2cad_mac_v6.step"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "c0f3b83a08966d10e54554316e1f2fb826f63563c5edc799489ce063a528ba97"
    assert not load(OUT / "artifacts/final_summary.json")["CASE09_RERUN"]


def test_selected_best_registry_unchanged():
    old = load(BASE / "artifacts/best_result_registry.json")
    new = load(OUT / "artifacts/best_result_registry.json")
    for case_id in old["cases"]:
        assert new["cases"][case_id]["SELECTED_BEST"] == old["cases"][case_id]["SELECTED_BEST"]


def test_no_tts_or_dual_modal_success_claim():
    value = load(OUT / "artifacts/final_summary.json")
    assert not value["TTS_ACTUALLY_USED"]
    assert value["TTS_PARTS"] == 0
    assert not value["DUAL_MODAL_CONTEXT_ACTUALLY_USED"]


def test_no_reconstruction_or_visual_claim():
    value = load(OUT / "artifacts/final_summary.json")
    assert value["CASES_WITH_FRESH_ASSEMBLY"] == 0
    assert value["SHADED_CONTACT_SHEET"] is None
    assert value["TRUE_EDGE_CONTACT_SHEET"] is None
    assert not value["OLD_STEP_USED_AS_INPUT"]


def test_safe_key_fingerprint_only():
    value = load(OUT / "artifacts/final_summary.json")
    fingerprint = value["MAC_KEY_FINGERPRINT"]
    assert fingerprint.startswith("sha256:")
    assert len(fingerprint) == 19
