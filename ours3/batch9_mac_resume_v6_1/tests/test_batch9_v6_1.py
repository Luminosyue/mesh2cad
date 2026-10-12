import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
BASE = ROOT / "batch9_fullstack_mesh2cad_mac_v6"
OUT = ROOT / "batch9_mac_resume_v6_1"
load = lambda p: json.loads(Path(p).read_text())

def test_canary_stopped_on_403():
    x=load(OUT/"artifacts/canary_summary.json");assert x["MAC_HTTP_STATUS"]==403;assert not x["MAC_CANARY_PASS"];assert x["MAC_CANARIES_COMPLETED"]==1;assert x["STOP_AFTER_CANARY_FAILURE"]
def test_case09_not_run():
    x=load(OUT/"artifacts/canary_summary.json");assert not x["CASE09_RERUN"];assert not (OUT/"CASE_09").exists()
def test_no_upstream_rerun():
    x=load(OUT/"artifacts/final_summary.json");assert x["P3_RERUN_CASES"]==[];assert x["PHYSX_RERUN_CASES"]==[];assert x["SEMANTIC_ARTIFACTS_REUSED"]==132;assert x["DUAL_MODAL_ARTIFACTS_REUSED"]==132
def test_canary_input_evidence():
    x=load(OUT/"artifacts/canary_summary.json")["results"][0];assert x["OBJ_TOKENS_SENT_TO_MAC"];assert x["RENDER_SENT_TO_MAC"];assert x["MEASURED_SPEC_SENT_TO_MAC"];assert x["SEMANTIC_GRAPH_SENT_TO_MAC"]
def test_truthful_mac_accounting():
    x=load(OUT/"artifacts/final_summary.json");assert x["REAL_MAC_CANDIDATES_BEFORE"]==3;assert x["REAL_MAC_CANDIDATES_AFTER"]==3;assert x["QUOTA_FALLBACK_CANDIDATES_REPLACED"]==0;assert not x["ALL_PARTS_MAC"]
def test_no_tts_claim():
    x=load(OUT/"artifacts/final_summary.json");assert not x["TTS_ACTUALLY_USED"];assert not x["DUAL_MODAL_CONTEXT_ACTUALLY_USED"]
def test_old_step_not_input():
    assert not load(OUT/"artifacts/final_summary.json")["OLD_STEP_USED_AS_RECONSTRUCTION_INPUT"]
def test_no_regression_registry():
    old=load(BASE/"artifacts/best_result_registry.json");new=load(OUT/"artifacts/best_result_registry.json");assert all(new["cases"][c]["SELECTED_BEST"]==old["cases"][c]["SELECTED_BEST"] for c in old["cases"])
def test_no_resume_assembly_or_visual_fabrication():
    x=load(OUT/"artifacts/final_summary.json");assert x["CASES_WITH_NEW_RESUME_ASSEMBLY"]==0;assert x["SHADED_CONTACT_SHEET"] is None;assert x["VISUALIZATION_STATUS"]=="NOT_GENERATED_CANARY_STOP"
