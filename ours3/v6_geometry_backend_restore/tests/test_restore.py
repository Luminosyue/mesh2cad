import json
import csv
from pathlib import Path

ROOT=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v6_geometry_backend_restore")

def data(): return json.loads((ROOT/"artifacts/final_summary.json").read_text())
def test_generator_found_and_fresh():
    x=data(); assert x["V6_GENERATOR_FOUND"] and x["V6_FRESH_RERUN_WORKING"] and x["V6_FRESH_STEP_COUNT"]==5
def test_historical_independence():
    x=data(); assert x["V6_HISTORICAL_STEP_INDEPENDENCE_PASS"] and x["V6_HISTORICAL_STEP_REUSE_COUNT"]==0
def test_safety_zeroes():
    x=data(); assert x["CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT"]==0 and x["V6_GEOMETRY_EXPLOSION_COUNT"]==0 and x["V6_BREP_INVALID_SELECTED_COUNT"]==0
def test_provenance_and_reload():
    x=data(); assert x["V6_BACKEND_PROVENANCE_COMPLETE"] and x["V6_STEP_RELOAD_SUCCESS_COUNT"]==x["V6_FRESH_STEP_COUNT"]
    for path in (ROOT/"cases/CASE09").glob("CADPART_*/v6_backend_provenance.json"):
        p=json.loads(path.read_text())
        assert p["generated_step_sha256"] != p["v6_selected_step_sha256"]
        assert p["historical_candidate_used"] is False
        assert p["runtime_parameters"]["effective_sections"] > 0
def test_strict_gain_gate():
    assert data()["V6_BACKEND_STRICT_GAIN_PART_COUNT"]>=2
def test_artifacts():
    for name in ("v6_generator_trace.csv","v6_backend_reproduction.csv","v6_backend_nativeness_audit.csv","case09_v6_backend_fresh_reproduction_shaded.png","case09_v6_backend_fresh_reproduction_true_edges.png","V6_GEOMETRY_BACKEND_RESTORE_REPORT.md"):
        assert (ROOT/"artifacts"/name).is_file()

def test_nativeness_audit_is_real():
    rows=list(csv.DictReader((ROOT/"artifacts/v6_backend_nativeness_audit.csv").open()))
    assert len(rows)==5
    assert all(int(r["v6_fresh_bspline_face_count"])==2 for r in rows)
    assert all(int(r["v6_fresh_plane_face_count"])==2 for r in rows)
    assert all(int(r["v6_fresh_bspline_control_point_count"])>0 for r in rows)
    assert all(float(r["v6_fresh_design_edge_ratio"])==1.0 for r in rows)
    assert all(r["v6_fresh_structural_class"]=="V6_FREEFORM_COMPACT_BREP" for r in rows)
    assert all(float(r["v6_fresh_fragmentation_score"])==0.0 for r in rows)

def test_vertical_tail_topology_gate():
    rows=list(csv.DictReader((ROOT/"artifacts/v6_backend_candidate_summary.csv").open()))
    row=next(r for r in rows if r["part_id"]=="CADPART_005")
    topology_ok=int(row["v6_fresh_shared_edge_count"])>=1 and int(row["v6_fresh_pcurve_count"])>=2 and int(row["v6_fresh_trimmed_face_count"])>=2
    assert (row["vertical_tail_topology_ok"]=="True") is topology_ok
    if not topology_ok:
        assert row["selected_best_verified"]=="False"

def test_independence_open_trace():
    logs=list((ROOT/"artifacts").glob("CADPART_*_independence_open_trace.log"))
    assert len(logs)==5
    text="\n".join(path.read_text(errors="replace") for path in logs)
    assert "candidate.step" not in text
    assert "selected/generated.step" not in text
    assert text.count("source_part.obj")>=5
