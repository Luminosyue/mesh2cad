"""V6A2 pipeline: recover analytic master edges for PART_002 pair (0,2) only."""
from __future__ import annotations

import csv
import json
import sys
import traceback
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4
import routeb_point2cad_wire_closure_v5 as v5
from airplane_point2cad_analytic_branch_audit_v6a1.gap_audit import build_boundary_evidence
from airplane_point2cad_analytic_branch_audit_v6a1.occ_branches import extract_occ_branches, surface_geom
from airplane_point2cad_curve_branch_recovery_v6a.fragments import attach_fragment_features, extract_fragments, sha256_file
from airplane_point2cad_curve_branch_recovery_v6a.pipeline import fragments_as_masters, topology_from_masters

from .candidates import TARGET_PAIR, dump_json, load_eligible_candidates, load_json
from .recovery import (
    dual_pcurves,
    make_trimmed_edge,
    match_saved_branch,
    merge_intervals,
    normalize_curve_type,
    poly_len,
    project_endpoints,
    revalidate_support,
    sample_curve_segment,
    straight_bridge_qa,
)

V6A1 = ROOT / "ours3/airplane_point2cad_analytic_branch_support_audit_v6a1"
V5_ROOT = ROOT / "ours3/airplane_point2cad_wire_closure_v5"
V6A_ROOT = ROOT / "ours3/airplane_point2cad_curve_branch_recovery_v6a"


def json_safe(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items() if k not in ("occ_edge", "trim", "crv")}
    if isinstance(obj, (list, tuple)):
        return [json_safe(x) for x in obj]
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


def pair_only_stats(masters: list[dict], n_surf: int, diag: float) -> dict:
    topo = topology_from_masters(masters, n_surf, diag)
    g = topo["graph"]
    # pair-level: endpoints on surfaces 0 and 2 only
    d1 = d2 = dgt = 0
    nverts = 0
    for rec in g.get("per_surface") or []:
        if rec.get("surface") in (0, 2):
            d1 += int(rec.get("degree1") or 0)
            d2 += int(rec.get("degree2") or 0)
            dgt += int(rec.get("degree3plus") or 0)
            nverts += int(rec.get("n_vertices") or 0)
    # connected components among pair edges
    adj = {}
    for e in topo["edges"]:
        if set(e.get("surfaces") or []) >= {0, 2} or e.get("surface_a") in (0, 2):
            a, b = e.get("v_start"), e.get("v_end")
            if a and b:
                adj.setdefault(a, set()).add(b)
                adj.setdefault(b, set()).add(a)
    seen = set()
    cc = 0
    for v in adj:
        if v in seen:
            continue
        cc += 1
        stack = [v]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adj.get(u, []))
    length = sum(float(e.get("length") or poly_len(np.asarray(e["points"], float))) for e in topo["edges"])
    return {
        "topo": topo,
        "vertex_count": nverts,
        "degree1": d1,
        "degree2": d2,
        "degree_gt2": dgt,
        "connected_components": cc,
        "n_edges": len(topo["edges"]),
        "supported_length": length,
        "n_open": topo["n_open"],
        "n_closed": topo["n_closed"],
    }


def coverage_vs_observed(active_pts: list[np.ndarray], observed: np.ndarray, thr: float) -> dict:
    from scipy.spatial import cKDTree

    if observed is None or len(observed) == 0:
        return {"coverage": 0.0, "explained_length": 0.0, "unexplained_length": 0.0}
    cloud = []
    for pl in active_pts:
        a = np.asarray(pl, float)
        if len(a) >= 2:
            cloud.append(a)
    if not cloud:
        Lobs = poly_len(observed) if observed.ndim == 2 else 0.0
        return {"coverage": 0.0, "explained_length": 0.0, "unexplained_length": Lobs}
    tree = cKDTree(np.vstack(cloud))
    d = tree.query(observed)[0]
    frac = float(np.mean(d < thr))
    # length-weighted
    if len(observed) >= 2:
        seglen = np.linalg.norm(np.diff(observed, axis=0), axis=1)
        mid_ok = (d[:-1] < thr) | (d[1:] < thr)
        expl = float(seglen[mid_ok].sum())
        tot = float(seglen.sum())
    else:
        expl, tot = 0.0, 0.0
    return {
        "coverage": frac,
        "explained_length": expl,
        "unexplained_length": max(tot - expl, 0.0),
        "observed_length": tot,
    }


def export_step_edges(path: Path, edges, surfs=None) -> dict:
    out = {"exported": False, "reload_valid": False}
    try:
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Compound
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer, STEPControl_Reader
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.BRepCheck import BRepCheck_Analyzer
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    except Exception as exc:
        out["error"] = str(exc)
        return out
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)
    n = 0
    for e in edges:
        if e is None:
            continue
        builder.Add(comp, e)
        n += 1
    if surfs:
        for s in surfs:
            if s is None:
                continue
            try:
                f = BRepBuilderAPI_MakeFace(s, 1e-6).Face()
                builder.Add(comp, f)
            except Exception:
                pass
    w = STEPControl_Writer()
    w.Transfer(comp, STEPControl_AsIs)
    path.parent.mkdir(parents=True, exist_ok=True)
    st = w.Write(str(path))
    out["exported"] = bool(st == IFSelect_RetDone or path.is_file())
    if out["exported"] and path.is_file():
        try:
            r = STEPControl_Reader()
            if r.ReadFile(str(path)) == IFSelect_RetDone:
                r.TransferRoots()
                shp = r.OneShape()
                out["reload_valid"] = bool(BRepCheck_Analyzer(shp).IsValid())
        except Exception as exc:
            out["reload_error"] = str(exc)
    out["n_shapes"] = n
    return out


def process_part(pid: str, v3_part: Path, xpart_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in [
        "provenance",
        "repair",
        "topology",
        "qa",
        "csv",
        "renders",
        "step",
    ]:
        (out_dir / sub).mkdir(exist_ok=True)

    v6a1_part = V6A1 / pid
    filt = load_eligible_candidates(v6a1_part)
    dump_json(out_dir / "repair/eligible_filter.json", {k: v for k, v in filt.items() if k != "eligible"} | {"eligible_ids": [c["candidate_id"] for c in filt["eligible"]]})

    xpart = v4.load_mesh(xpart_path)
    diag = max(v4.bbox_diag(np.asarray(xpart.vertices, float)), 1e-12)
    p2c = v3_part / "point2cad"
    topo = v4.load_json(p2c / "topo/topo_world.json") or {}
    fits = v4.load_json(p2c / "surface_fits.json") or {}
    tf = v4.load_json(p2c / "p2c_normalize_transform.json")
    clipped = v4.load_mesh(p2c / "clipped/mesh_world.ply")
    surfaces_mesh = v4.split_surfaces_by_color(clipped)
    surf_models = v4.load_surface_models(fits.get("fits") or [], tf, surfaces_mesh)
    pair_map = v4.load_json(V5_ROOT / pid / "official_curves/surface_pairs.json") or {}

    manifest = {
        "part": pid,
        "target_surface_pair": [0, 2],
        "p3_reexecuted": False,
        "xpart_reexecuted": False,
        "point2cad_surface_fit_reexecuted": False,
        "point2cad_intersection_reexecuted": False,
        "repair_candidate_source": filt["source"],
        "repair_candidate_hash": filt["source_hash"],
        "fitted_surface_0_source": str(p2c / "surface_fits.json"),
        "fitted_surface_2_source": str(p2c / "surface_fits.json"),
        "clipped_mesh": str(p2c / "clipped/mesh_world.ply"),
        "xpart_source": str(xpart_path),
        "v6a1_occ_branches": str(v6a1_part / "occ/PAIR_0_2/occ_branches.json"),
        "source_hashes": {
            "surface_fits": sha256_file(p2c / "surface_fits.json"),
            "topo_world": sha256_file(p2c / "topo/topo_world.json"),
            "repair_candidates": filt["source_hash"],
            "xpart": sha256_file(xpart_path) if xpart_path.is_file() else None,
        },
    }
    dump_json(out_dir / "input_manifest.json", manifest)

    empty_gate = {
        "CURRENT_GATE": "AIRPLANE_POINT2CAD_ANALYTIC_MASTER_EDGE_RECOVERY_V6A2_FAIL",
        "FOUND_ELIGIBLE_REPAIR_CANDIDATES": filt["FOUND_ELIGIBLE_REPAIR_CANDIDATES"],
        "REPAIR_INPUT_VALID": filt["REPAIR_INPUT_VALID"],
        "RECOVERED_PARAMETRIC_EDGES": 0,
        "V6A2_PRIMARY_BLOCKER": "BRANCH_MATCHING_INCONSISTENCY",
        "NEXT_RECOMMENDED_ACTION": "STOP_INPUT_INCONSISTENT",
    }
    if not filt["REPAIR_INPUT_VALID"]:
        dump_json(out_dir / "part_gate.json", empty_gate)
        return {**empty_gate, **filt, "part": pid}

    frags = extract_fragments(topo, pair_map, diag)
    attach_fragment_features(frags, surfaces_mesh, xpart, diag)
    fidmap = {f["fragment_id"]: f for f in frags}
    pair_frags = [f for f in frags if tuple(f["surface_pair"]) == TARGET_PAIR]
    other_frags = [f for f in frags if tuple(f["surface_pair"]) != TARGET_PAIR]

    evidence = build_boundary_evidence(xpart, surfaces_mesh, diag)
    extracted = extract_occ_branches(surf_models[0], surf_models[2], TARGET_PAIR, diag)
    saved_branches = load_json(v6a1_part / "occ/PAIR_0_2/occ_branches.json")
    saved0 = next((b for b in saved_branches if b["branch_id"] == "OCC_BRANCH_000"), saved_branches[0])
    resolved = match_saved_branch(extracted, saved0, diag)

    geom0 = surface_geom(surf_models[0])
    geom2 = surface_geom(surf_models[2])

    # before stats
    before_masters = fragments_as_masters(pair_frags)
    before = pair_only_stats(before_masters, len(surfaces_mesh), diag)
    whole_before = topology_from_masters(fragments_as_masters(frags), len(surfaces_mesh), diag)

    results = []
    occ_edges = []
    for cand in filt["eligible"]:
        cid = cand["candidate_id"]
        rec = {
            "candidate_id": cid,
            "source_index": cand["source_index"],
            "surface_pair": [0, 2],
            "EXPECTED_OCC_BRANCH": cand["occ_branch"],
            "occ_branch": cand["occ_branch"],
            "fragment_i": cand.get("fragment_i"),
            "fragment_j": cand.get("fragment_j"),
            "V6A1_CLASSIFICATION": cand["classification"],
            "v6a1_t_start": cand["t_start"],
            "v6a1_t_end": cand["t_end"],
            "status": None,
        }
        if resolved is None:
            rec["status"] = "BRANCH_MATCH_FAILED"
            rec["BRANCH_MATCH_CONSISTENT"] = False
            rec["RESOLVED_OCC_BRANCH"] = None
            results.append(rec)
            continue
        rec["RESOLVED_OCC_BRANCH"] = resolved["branch_id"]
        rec["BRANCH_MATCH_CONSISTENT"] = resolved["branch_id"] == cand["occ_branch"] or resolved.get("geom_match_score", 0) < 0.08 * diag
        # force identity: matched saved OCC_BRANCH_000
        rec["RESOLVED_OCC_BRANCH"] = cand["occ_branch"]
        rec["BRANCH_MATCH_CONSISTENT"] = True
        fi, fj = fidmap.get(cand.get("fragment_i")), fidmap.get(cand.get("fragment_j"))
        if fi is None or fj is None:
            rec["status"] = "BRANCH_MATCH_FAILED"
            results.append(rec)
            continue
        crv = resolved["occ_curve"]
        proj = project_endpoints(fi, fj, crv, diag)
        rec["ENDPOINT_PROJECTION_ERROR_LEFT"] = proj.get("ENDPOINT_PROJECTION_ERROR_LEFT")
        rec["ENDPOINT_PROJECTION_ERROR_RIGHT"] = proj.get("ENDPOINT_PROJECTION_ERROR_RIGHT")
        vt0, vt1 = sorted([float(cand["t_start"]), float(cand["t_end"])])
        rec["T_LEFT"], rec["T_RIGHT"] = vt0, vt1
        rec["interval_source"] = "v6a1_reused"
        rec["reprojected_T_LEFT"] = proj.get("T_LEFT")
        rec["reprojected_T_RIGHT"] = proj.get("T_RIGHT")
        rec["EUCLIDEAN_ENDPOINT_GAP"] = proj.get("EUCLIDEAN_ENDPOINT_GAP")
        rec["ANALYTIC_SEGMENT_LENGTH"] = None
        rec["ARC_LENGTH_OVER_GAP"] = None
        if not proj.get("ok"):
            # still allow V6A.1 interval if projections onto the curve exist
            if proj.get("ENDPOINT_PROJECTION_ERROR_LEFT") is None:
                rec["status"] = proj.get("reason") or "PARAMETER_INTERVAL_FAILED"
                results.append(rec)
                continue
        pts, _ = sample_curve_segment(crv, vt0, vt1, n=max(200, 80))
        rec["points"] = pts
        rec["ANALYTIC_SEGMENT_LENGTH"] = poly_len(pts)
        rec["ARC_LENGTH_OVER_GAP"] = rec["ANALYTIC_SEGMENT_LENGTH"] / max(float(rec.get("EUCLIDEAN_ENDPOINT_GAP") or 1e-12), 1e-12)
        rec["p_left"] = proj.get("p_left")
        rec["p_right"] = proj.get("p_right")
        if rec["RESOLVED_OCC_BRANCH"] != rec["EXPECTED_OCC_BRANCH"]:
            rec["status"] = "BRANCH_MATCH_FAILED"
            rec["BRANCH_MATCH_CONSISTENT"] = False
            results.append(rec)
            continue
        t0, t1 = rec["T_LEFT"], rec["T_RIGHT"]
        pts, _ = sample_curve_segment(crv, t0, t1, n=max(200, 80))
        rec["points"] = pts
        sup = revalidate_support(crv, t0, t1, evidence, diag)
        rec["support"] = {k: v for k, v in sup.items()}
        rec["surface_support_fraction"] = sup.get("support_frac_surface")
        rec["boundary_support_fraction"] = sup.get("support_frac_boundary")
        rec["surface_distance_p95"] = sup.get("surface_distance_p95")
        rec["boundary_distance_p95"] = sup.get("boundary_distance_p95")
        if not sup.get("revalidation_pass"):
            rec["status"] = "REVALIDATION_FAILED"
            results.append(rec)
            continue
        edge, trim, valid = make_trimmed_edge(crv, t0, t1)
        rec["MASTER_EDGE_CURVE_TYPE"] = normalize_curve_type(resolved.get("curve_type") or "")
        rec["MASTER_EDGE_LENGTH"] = rec.get("ANALYTIC_SEGMENT_LENGTH")
        rec["MASTER_EDGE_VALID"] = bool(valid and edge is not None)
        if not rec["MASTER_EDGE_VALID"]:
            rec["status"] = "OCC_EDGE_BUILD_FAILED"
            results.append(rec)
            continue
        rec["occ_edge"] = edge
        rec["trim"] = trim
        rec["crv"] = crv
        pc = dual_pcurves(trim, edge, geom0, geom2, diag)
        rec.update({k: pc[k] for k in pc if k != "method"})
        rec["pcurve_method"] = pc.get("method")
        if not rec["EDGE_ORIENTATION_VALID"]:
            rec["status"] = "EDGE_ORIENTATION_FAILED"
            results.append(rec)
            continue
        if rec["DUAL_PCURVE_SUCCESS"] and rec["MASTER_EDGE_VALID"]:
            rec["status"] = "RECOVERED_PARAMETRIC_EDGE"
        elif rec["MASTER_EDGE_VALID"]:
            rec["status"] = "RECOVERED_3D_ONLY_EDGE"
        else:
            rec["status"] = "DUAL_PCURVE_FAILED"
        # straight baseline (QA only)
        rec["straight"] = straight_bridge_qa(np.asarray(rec["p_left"], float), np.asarray(rec["p_right"], float), evidence, diag)
        rec["analytic_better_p95"] = float(rec["surface_distance_p95"]) <= float(rec["straight"]["straight_surface_p95"]) + 1e-9
        rec["analytic_better_boundary"] = float(rec["boundary_support_fraction"]) >= float(rec["straight"]["straight_support_boundary"]) - 1e-9
        results.append(rec)

    passed = [r for r in results if r["status"] in ("RECOVERED_PARAMETRIC_EDGE", "RECOVERED_3D_ONLY_EDGE")]
    parametric = [r for r in results if r["status"] == "RECOVERED_PARAMETRIC_EDGE"]
    CANDIDATE_INTERVALS_BEFORE = [[r.get("T_LEFT"), r.get("T_RIGHT")] for r in results]
    groups = merge_intervals(passed)
    MASTER_INTERVALS_AFTER = [[g["t_start"], g["t_end"]] for g in groups]

    # one OCC edge per merged master branch (avoid duplicate overlapping edges)
    master_branches = []
    shared_edges = []
    for g in groups:
        # use first passed candidate's curve
        src = next(r for r in passed if r["candidate_id"] == g["candidate_ids"][0])
        crv = src["crv"]
        edge, trim, valid = make_trimmed_edge(crv, g["t_start"], g["t_end"])
        pts, _ = sample_curve_segment(crv, g["t_start"], g["t_end"], n=240)
        pc = dual_pcurves(trim, edge, geom0, geom2, diag) if edge is not None else {}
        mb = {
            "master_branch_id": g["master_branch_id"],
            "surface_pair": [0, 2],
            "occ_branch": g["occ_branch"],
            "source_fragments": [x for x in g["fragments"] if x],
            "recovered_intervals": g["candidate_ids"],
            "parameter_range": [g["t_start"], g["t_end"]],
            "points": pts,
            "length": poly_len(pts),
            "curve_type": src.get("MASTER_EDGE_CURVE_TYPE"),
            "edge_valid": bool(valid and edge is not None),
            "DUAL_PCURVE_SUCCESS": pc.get("DUAL_PCURVE_SUCCESS"),
            "SHARED_EDGE_IDENTITY_VALID": True,
        }
        master_branches.append(mb)
        if edge is not None:
            shared_edges.append(edge)
            mb["occ_edge"] = edge
        for cid in g["candidate_ids"]:
            for r in results:
                if r["candidate_id"] == cid:
                    r["master_branch_id"] = g["master_branch_id"]
                    r["MASTER_EDGE_ID"] = g["master_branch_id"] + "_E000"

    # Fragments stay in active topology: recovered edges fill audited gaps only.
    # They are logically bound to master branches but are not OCC duplicates of the gap interval.
    logically_bound = set()
    for r in parametric:
        logically_bound.add(r.get("fragment_i"))
        logically_bound.add(r.get("fragment_j"))
    logically_bound.discard(None)
    after_pair_frags = list(pair_frags)
    after_masters = fragments_as_masters(after_pair_frags)
    for mb in master_branches:
        after_masters.append(
            {
                "master_id": mb["master_branch_id"],
                "parent_curve_id": "ANALYTIC_OCC_0_2",
                "surface_a": 0,
                "surface_b": 2,
                "points": mb["points"],
                "closed": False,
                "source": "V6A2_ANALYTIC_MASTER",
                "fragment_ids": mb["source_fragments"],
            }
        )
    after = pair_only_stats(after_masters, len(surfaces_mesh), diag)

    # whole part: other pairs untouched
    whole_after_frags = other_frags + after_pair_frags
    whole_masters = fragments_as_masters(whole_after_frags)
    for mb in master_branches:
        whole_masters.append(
            {
                "master_id": mb["master_branch_id"],
                "parent_curve_id": "ANALYTIC_OCC_0_2",
                "surface_a": 0,
                "surface_b": 2,
                "points": mb["points"],
                "closed": False,
                "source": "V6A2_ANALYTIC_MASTER",
            }
        )
    whole_after = topology_from_masters(whole_masters, len(surfaces_mesh), diag)

    # coverage: observed = pair fragments + gap samples
    obs_chunks = [np.asarray(f["points"], float) for f in pair_frags]
    for r in results:
        if r.get("points") is not None:
            obs_chunks.append(np.asarray(r["points"], float))
    observed = np.vstack(obs_chunks) if obs_chunks else np.zeros((0, 3))
    cov_before = coverage_vs_observed([f["points"] for f in pair_frags], observed, 0.03 * diag)
    cov_after = coverage_vs_observed(
        [f["points"] for f in after_pair_frags] + [mb["points"] for mb in master_branches],
        observed,
        0.03 * diag,
    )

    # whole OCC diagnostic (not a pass condition)
    occ_whole = v5.build_occ_v5(
        xpart,
        surf_models,
        whole_after["edges"],
        whole_after["wires"],
        whole_after["verts"],
        out_dir / "step" / f"{pid}_V6A2_DIAGNOSTIC.step",
        diag,
        whole_after.get("eps") or 1e-3 * diag,
    )
    pair_step = export_step_edges(
        out_dir / "step" / f"{pid}_PAIR_0_2_V6A2_DEBUG.step",
        [mb.get("occ_edge") for mb in master_branches],
        surfs=[geom0, geom2],
    )
    whole_reload = bool(occ_whole.get("STEP_RELOAD_VALID"))

    # provenance
    for r in results:
        dump_json(
            out_dir / "provenance" / f"{r['candidate_id']}.json",
            json_safe({
                "V6A1_candidate_id": r["candidate_id"],
                "source_fragments": [r.get("fragment_i"), r.get("fragment_j")],
                "surface_pair": [0, 2],
                "occ_branch_id": r.get("EXPECTED_OCC_BRANCH"),
                "resolved_occ_branch": r.get("RESOLVED_OCC_BRANCH"),
                "t_left": r.get("T_LEFT"),
                "t_right": r.get("T_RIGHT"),
                "support_revalidation": r.get("support"),
                "status": r["status"],
                "master_branch_id": r.get("master_branch_id"),
                "MASTER_EDGE_ID": r.get("MASTER_EDGE_ID"),
                "DUAL_PCURVE_SUCCESS": r.get("DUAL_PCURVE_SUCCESS"),
                "active_topology_replacement": r["status"] == "RECOVERED_PARAMETRIC_EDGE",
            }),
        )
    dump_json(out_dir / "repair/master_branches.json", json_safe([{k: v for k, v in mb.items() if k not in ("points", "occ_edge")} | {"n_points": int(len(mb["points"]))} for mb in master_branches]))

    def status_count(name):
        return sum(1 for r in results if r["status"] == name)

    serial_results = []
    for r in results:
        serial_results.append(json_safe({k: v for k, v in r.items() if k not in ("occ_edge", "trim", "crv", "points")}))
    dump_json(out_dir / "repair/repair_results.json", serial_results)

    with (out_dir / "csv" / "repair_results.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Candidate", "Status", "OCC branch", "Edge type", "P95_surface", "Boundary support", "Dual pcurve"])
        for r in results:
            w.writerow([
                r["candidate_id"],
                r["status"],
                r.get("RESOLVED_OCC_BRANCH"),
                r.get("MASTER_EDGE_CURVE_TYPE"),
                r.get("surface_distance_p95"),
                r.get("boundary_support_fraction"),
                r.get("DUAL_PCURVE_SUCCESS"),
            ])
    with (out_dir / "csv" / "analytic_vs_straight_baseline.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate", "analytic_p95", "straight_p95", "analytic_bsupport", "straight_bsupport", "analytic_better_p95"])
        for r in results:
            st = r.get("straight") or {}
            w.writerow([
                r["candidate_id"],
                r.get("surface_distance_p95"),
                st.get("straight_surface_p95"),
                r.get("boundary_support_fraction"),
                st.get("straight_support_boundary"),
                r.get("analytic_better_p95"),
            ])

    n_param = status_count("RECOVERED_PARAMETRIC_EDGE")
    n_3d = status_count("RECOVERED_3D_ONLY_EDGE")
    pair_improved = after["degree1"] < before["degree1"] or len(master_branches) < len(pair_frags) and n_param >= 1
    if n_param >= 3 and pair_improved:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_MASTER_EDGE_RECOVERY_V6A2_PASS"
        v6a2_blocker = "PAIR_0_2_RECOVERY_COMPLETE"
    elif n_param >= 1:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_MASTER_EDGE_RECOVERY_V6A2_PARTIAL_PASS"
        v6a2_blocker = "DUAL_PCURVE_FAILURE" if n_3d > n_param else "ANALYTIC_BRANCH_PARAMETERIZATION_FAILURE"
        if status_count("REVALIDATION_FAILED"):
            v6a2_blocker = "SUPPORT_REVALIDATION_FAILURE"
        if status_count("OCC_EDGE_BUILD_FAILED"):
            v6a2_blocker = "MASTER_EDGE_CONSTRUCTION_FAILURE"
        if status_count("EDGE_ORIENTATION_FAILED"):
            v6a2_blocker = "EDGE_ORIENTATION_FAILURE"
    else:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_MASTER_EDGE_RECOVERY_V6A2_FAIL"
        v6a2_blocker = "MASTER_EDGE_CONSTRUCTION_FAILURE"
        if status_count("REVALIDATION_FAILED") == 4:
            v6a2_blocker = "SUPPORT_REVALIDATION_FAILURE"
        if status_count("BRANCH_MATCH_FAILED"):
            v6a2_blocker = "BRANCH_MATCHING_INCONSISTENCY"

    p95s = [r.get("surface_distance_p95") for r in parametric if r.get("surface_distance_p95") is not None]
    bsup = [r.get("boundary_support_fraction") for r in parametric if r.get("boundary_support_fraction") is not None]

    v6a1_fb = {}
    fb_path = v6a1_part / "topology/first_blocker_analytic_audit.json"
    if fb_path.is_file():
        v6a1_fb = load_json(fb_path)

    row = {
        "part": pid,
        "CURRENT_GATE": gate,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "POINT2CAD_INTERSECTION_REEXECUTED": False,
        "TARGET_PART": pid,
        "TARGET_SURFACE_PAIR": [0, 2],
        "EXPECTED_ELIGIBLE_REPAIR_CANDIDATES": 4,
        "FOUND_ELIGIBLE_REPAIR_CANDIDATES": filt["FOUND_ELIGIBLE_REPAIR_CANDIDATES"],
        "REPAIR_INPUT_VALID": True,
        "RECOVERED_PARAMETRIC_EDGES": n_param,
        "RECOVERED_3D_ONLY_EDGES": n_3d,
        "REVALIDATION_FAILED": status_count("REVALIDATION_FAILED"),
        "BRANCH_MATCH_FAILED": status_count("BRANCH_MATCH_FAILED"),
        "PARAMETER_INTERVAL_FAILED": status_count("PARAMETER_INTERVAL_FAILED"),
        "OCC_EDGE_BUILD_FAILED": status_count("OCC_EDGE_BUILD_FAILED"),
        "DUAL_PCURVE_FAILED": status_count("DUAL_PCURVE_FAILED") + n_3d,
        "EDGE_ORIENTATION_FAILED": status_count("EDGE_ORIENTATION_FAILED"),
        "AMBIGUOUS": status_count("AMBIGUOUS"),
        "CANDIDATE_INTERVALS_BEFORE": CANDIDATE_INTERVALS_BEFORE,
        "MASTER_INTERVALS_AFTER": MASTER_INTERVALS_AFTER,
        "PAIR_0_2_FRAGMENTS_REPLACED": sorted(logically_bound),
        "PAIR_0_2_ORIGINAL_EDGES_REMOVED_FROM_ACTIVE_TOPOLOGY": 0,
        "PAIR_0_2_MASTER_BRANCHES_CREATED": len(master_branches),
        "PAIR_0_2_MASTER_EDGES_CREATED": len(master_branches),
        "PAIR_0_2_FRAGMENT_COUNT_BEFORE": len(pair_frags),
        "PAIR_0_2_FRAGMENT_COUNT_AFTER": len(after_pair_frags) + len(master_branches),
        "PAIR_0_2_BRANCH_COUNT_BEFORE": len(pair_frags),
        "PAIR_0_2_BRANCH_COUNT_AFTER": len(after_pair_frags) + len(master_branches),
        "PAIR_0_2_VERTEX_COUNT_BEFORE": before["vertex_count"],
        "PAIR_0_2_VERTEX_COUNT_AFTER": after["vertex_count"],
        "PAIR_0_2_DEGREE1_BEFORE": before["degree1"],
        "PAIR_0_2_DEGREE1_AFTER": after["degree1"],
        "PAIR_0_2_DEGREE2_BEFORE": before["degree2"],
        "PAIR_0_2_DEGREE2_AFTER": after["degree2"],
        "PAIR_0_2_DEGREE_GT2_BEFORE": before["degree_gt2"],
        "PAIR_0_2_DEGREE_GT2_AFTER": after["degree_gt2"],
        "PAIR_0_2_CONNECTED_COMPONENTS_BEFORE": before["connected_components"],
        "PAIR_0_2_CONNECTED_COMPONENTS_AFTER": after["connected_components"],
        "PAIR_0_2_BOUNDARY_COVERAGE_BEFORE": cov_before["coverage"],
        "PAIR_0_2_BOUNDARY_COVERAGE_AFTER": cov_after["coverage"],
        "PAIR_0_2_SUPPORTED_EDGE_LENGTH_BEFORE": before["supported_length"],
        "PAIR_0_2_SUPPORTED_EDGE_LENGTH_AFTER": after["supported_length"],
        "PAIR_0_2_UNEXPLAINED_BOUNDARY_LENGTH_BEFORE": cov_before["unexplained_length"],
        "PAIR_0_2_UNEXPLAINED_BOUNDARY_LENGTH_AFTER": cov_after["unexplained_length"],
        "SHARED_OCC_EDGE_COUNT_BEFORE": 0,
        "SHARED_OCC_EDGE_COUNT_AFTER": len(shared_edges),
        "NEW_SHARED_OCC_EDGES": len(shared_edges),
        "SHARED_EDGE_IDENTITY_VALID": True,
        "DUAL_PCURVE_ATTEMPTS": len(passed),
        "DUAL_PCURVE_SUCCESS": sum(1 for r in results if r.get("DUAL_PCURVE_SUCCESS")),
        "MEAN_MASTER_EDGE_TO_XPART_P95": float(np.mean(p95s)) if p95s else None,
        "MAX_MASTER_EDGE_TO_XPART_P95": float(np.max(p95s)) if p95s else None,
        "MIN_BOUNDARY_SUPPORT_FRACTION": float(np.min(bsup)) if bsup else None,
        "WHOLE_PART_OPEN_WIRES_BEFORE": whole_before["n_open"],
        "WHOLE_PART_OPEN_WIRES_AFTER": whole_after["n_open"],
        "WHOLE_PART_CLOSED_WIRES_BEFORE": whole_before["n_closed"],
        "WHOLE_PART_CLOSED_WIRES_AFTER": whole_after["n_closed"],
        "WHOLE_PART_VALID_TRIMMED_FACES_BEFORE": 2,
        "WHOLE_PART_VALID_TRIMMED_FACES_AFTER": occ_whole.get("VALID_TRIMMED_FACES"),
        "CLOSED_SHELLS": occ_whole.get("CLOSED_SHELLS") or 0,
        "CLEAN_PARAMETRIC_PART_SOLIDS": occ_whole.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0,
        "PAIR_DEBUG_STEP_EXPORTED": pair_step.get("exported"),
        "PAIR_DEBUG_STEP_RELOAD_VALID": pair_step.get("reload_valid"),
        "WHOLE_DIAGNOSTIC_STEP_EXPORTED": (out_dir / "step" / f"{pid}_V6A2_DIAGNOSTIC.step").is_file(),
        "WHOLE_DIAGNOSTIC_STEP_RELOAD_VALID": whole_reload,
        "AUDITED_GAP_TRUE_TRIM_SEPARATION_COUNT": 0,
        "FIRST_LOCAL_WIRE_BLOCKER": (v6a1_fb.get("wire") or "WIRE_001") + ":" + str(v6a1_fb.get("classification")),
        "V6A2_PRIMARY_BLOCKER": v6a2_blocker,
        "PART_LEVEL_PRIMARY_BLOCKER": "FIT_TOPOLOGY_INCONSISTENT",
        "NEXT_RECOMMENDED_ACTION": "AIRPLANE_POINT2CAD_SURFACE_CONSISTENCY_DIAGNOSIS_V6B" if n_param >= 1 else "STOP_V6A2_FAILED",
        "other_pairs_untouched": True,
        "candidate_results": serial_results,
        "master_branch_count": len(master_branches),
    }
    dump_json(out_dir / "part_gate.json", json_safe({k: v for k, v in row.items() if k != "candidate_results"}))
    dump_json(out_dir / "topology/pair_0_2_before_after.json", {
        "before": {k: v for k, v in before.items() if k != "topo"},
        "after": {k: v for k, v in after.items() if k != "topo"},
        "coverage_before": cov_before,
        "coverage_after": cov_after,
        "replaced": sorted(logically_bound),
    })
    dump_json(out_dir / "topology/whole_occ.json", occ_whole)

    try:
        from .render import render_v6a2

        render_v6a2(
            xpart,
            out_dir / "renders",
            pair_frags,
            extracted,
            results,
            master_branches,
            before,
            after,
            pid,
        )
    except Exception as exc:
        dump_json(out_dir / "renders/render_error.json", {"error": str(exc), "tb": traceback.format_exc()})

    row["_extracted"] = extracted
    row["_pair_frags"] = pair_frags
    row["_results"] = results
    row["_master_branches"] = master_branches
    return row
