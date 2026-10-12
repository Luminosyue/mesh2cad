import copy
import json
from pathlib import Path

import numpy as np
import pytest

from geometry.profile_type_classifier import classify_profile
from geometry.representation_router import route_profile_types
from geometry.open_chain_correspondence import ordered_chain_from_graph, resample_open_chain, fit_open_bspline, build_chain_tracks, descriptor
from builders.open_shell_skin_builder import OpenShellSkinBuilder


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
V7A = ROOT / "v7a_profile_recovery"


def closed_record():
    return {"station_id": "S00", "closed_path_count": 1, "open_path_count": 0, "raw_path_count": 1, "open_endpoint_count": 0, "junction_count": 0, "node_degree_histogram": {2: 8}, "outer_loop": {"points": []}}


def open_record():
    return {"station_id": "S01", "closed_path_count": 0, "open_path_count": 1, "raw_path_count": 1, "open_endpoint_count": 2, "junction_count": 0, "node_degree_histogram": {1: 2, 2: 4}}


def test_profile_type_classifier_closed():
    assert classify_profile(closed_record(), False)["profile_type"] == "CLOSED_SOLID_PROFILE"


def test_profile_type_classifier_open_shell():
    assert classify_profile(open_record(), False)["profile_type"] == "OPEN_SHELL_PROFILE"


def test_router_closed_branch():
    assert route_profile_types(["CLOSED_SOLID_PROFILE"] * 9 + ["OPEN_SHELL_PROFILE"])["decision"] == "CLOSED_PROFILE_BRANCH"


def test_router_open_shell_branch():
    assert route_profile_types(["OPEN_SHELL_PROFILE"] * 6 + ["CLOSED_SOLID_PROFILE"] * 4)["decision"] == "OPEN_SHELL_BRANCH"


def test_router_not_part_id_hardcoded():
    source = (OUT / "geometry/representation_router.py").read_text()
    assert "part_id" not in source and "FUSELAGE" not in source and "CADPART" not in source


def test_open_chain_graph_ordering():
    nodes = np.array([[0, 0, 0], [2, 0, 0], [1, 0, 0]])
    result = ordered_chain_from_graph(nodes, [(0, 2), (2, 1)], {0, 1, 2})
    assert np.allclose(result[:, 0], [0, 1, 2])


def test_open_chain_has_two_endpoints():
    with pytest.raises(ValueError, match="INVALID_OPEN_CHAIN_RUNTIME_REJECTED"):
        ordered_chain_from_graph(np.zeros((3, 3)), [(0, 1), (1, 2), (2, 0)], {0, 1, 2})


def test_open_chain_resampling():
    result = resample_open_chain([[0, 0, 0], [1, 0, 0], [1, 2, 0]], 64)
    assert result.shape == (64, 3) and np.allclose(result[[0, -1]], [[0, 0, 0], [1, 2, 0]])


def test_open_bspline_fitting():
    raw = np.c_[np.linspace(0, 1, 20), np.sin(np.linspace(0, 1, 20)), np.zeros(20)]
    fit = fit_open_bspline(raw, resample_open_chain(raw, 64))
    assert fit["curve_type"] == "OPEN_BSPLINE" and fit["periodic"] is False and fit["valid"]


def test_chain_correspondence_across_stations():
    stations = []
    for index in range(3):
        points = np.c_[np.linspace(0, 1, 16), np.full(16, index * .1), np.zeros(16)]
        desc = descriptor(points, [0, index * .1, 0], [1, 0, 0], [0, 0, 1])
        stations.append({"chains": [{"chain_key": f"S{index}.C0", "raw_points_3d": points, "resampled_points_3d": points.copy(), "descriptor": desc}]})
    tracks, _, _ = build_chain_tracks(stations)
    assert sorted(map(len, tracks.values())) == [3]


def test_chain_orientation_consistency():
    points = np.c_[np.linspace(0, 1, 16), np.zeros(16), np.zeros(16)]
    desc1 = descriptor(points, [0, 0, 0], [1, 0, 0], [0, 0, 1])
    desc2 = descriptor(points[::-1], [0, 0, 0], [1, 0, 0], [0, 0, 1])
    stations = [{"chains": [{"chain_key": "S0.C0", "raw_points_3d": points, "resampled_points_3d": points.copy(), "descriptor": desc1}]}, {"chains": [{"chain_key": "S1.C0", "raw_points_3d": points[::-1].copy(), "resampled_points_3d": points[::-1].copy(), "descriptor": desc2}]}]
    tracks, _, flips = build_chain_tracks(stations)
    assert flips == 1 and len(next(iter(tracks.values()))) == 2


def test_open_shell_builder_consumes_measured_profiles():
    summary = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
    assert summary["OPEN_SHELL_PROFILE_PERTURBATION_EFFECTIVE"] is True


def test_open_shell_builder_does_not_resection_mesh():
    source = (OUT / "builders/open_shell_skin_builder.py").read_text()
    assert ".section(" not in source and "trimesh" not in source and "source_mesh" not in source


def test_invalid_open_chain_rejected():
    spec = json.loads((OUT / "04_measured_spec/CADPART_000/measured_cad_spec.json").read_text())
    plan = json.loads((OUT / "05_construction_plan/CADPART_000/OPEN_SHELL.json").read_text())
    first = next(iter(spec["open_chain_tracks"].values()))[0]
    first["ordering_valid"] = False
    with pytest.raises(ValueError, match="INVALID_OPEN_CHAIN_RUNTIME_REJECTED"):
        OpenShellSkinBuilder().build(spec, plan)


@pytest.mark.parametrize("field", ["FORCED_CLOSURE_COUNT", "BBOX_CLOSURE_COUNT", "CONVEX_HULL_CLOSURE_COUNT", "LARGE_GAP_BRIDGE_COUNT", "FAKE_CAP_COUNT"])
def test_no_fake_closure(field):
    summary = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
    assert summary[field] == 0


def test_profile_samples_not_preserved_as_line_edges():
    summary = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
    assert summary["PROFILE_SAMPLE_DERIVED_EDGE_COUNT"] == 0


def test_main_wing_closed_branch_regression():
    summary = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
    result = summary["RESULTS"]["CADPART_001"]
    assert summary["MAIN_WING_ROUTE"] == "CLOSED_PROFILE_BRANCH" and result["metrics"]["OCC_VALID"]


def test_v7_contract_regression():
    old = json.loads((V7A / "artifacts/final_summary.json").read_text())
    assert old["V7_CONTRACT_REGRESSION_PASS"] is True


def test_v7a_profile_regression():
    old = json.loads((V7A / "artifacts/final_summary.json").read_text())
    assert old["PROFILE_CONTRACT_PERTURBATION_EFFECTIVE"] and old["PROFILE_SWAP_PERTURBATION_EFFECTIVE"] and old["INVALID_PROFILE_RUNTIME_REJECTED"]
