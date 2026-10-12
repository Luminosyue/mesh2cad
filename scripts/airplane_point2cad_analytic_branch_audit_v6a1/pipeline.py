"""Main V6A.1 audit pipeline (read-only)."""
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
from airplane_point2cad_curve_branch_recovery_v6a.fragments import extract_fragments
from airplane_point2cad_curve_branch_recovery_v6a.branch_recovery import recover_all_branches

from .baseline_audit import dump_json, run_baseline_audit
from .gap_audit import (
    build_boundary_evidence,
    enumerate_gaps,
    match_fragment_to_branch,
)
from .occ_branches import extract_occ_branches
from .uv_audit import audit_uv_rejections


V6A_ROOT = ROOT / "ours3/airplane_point2cad_curve_branch_recovery_v6a"
V5_ROOT = ROOT / "ours3/airplane_point2cad_wire_closure_v5"


def load_branch_doc(v6a_part: Path, topo, pair_map, surfaces, xpart, diag) -> dict:
    frags = extract_fragments(topo, pair_map, diag)
    from airplane_point2cad_curve_branch_recovery_v6a.fragments import attach_fragment_features

    attach_fragment_features(frags, surfaces, xpart, diag)
    return recover_all_branches(frags, surfaces, xpart, diag)


def first_blocker_analytic_audit(
    first_blocker: dict,
    frags: list[dict],
    matches: dict,
    gaps: list[dict],
    branches: list[dict],
    evidence: dict,
    diag: float,
) -> dict:
    pair = tuple(first_blocker.get("expected_surface_pair") or (0, 1))
    pair_frags = [f for f in frags if f["surface_pair"] == pair]
    ws = np.asarray(first_blocker.get("start") or [], float)
    we = np.asarray(first_blocker.get("end") or [], float)
    left = right = None
    for f in pair_frags:
        for tag, p in (("s", f["start_xyz"]), ("e", f["end_xyz"])):
            d0 = float(np.linalg.norm(np.asarray(p, float) - ws))
            d1 = float(np.linalg.norm(np.asarray(p, float) - we))
            if left is None or d0 < left["gap"]:
                left = {"fragment_id": f["fragment_id"], "endpoint": tag, "gap": d0}
            if right is None or d1 < right["gap"]:
                right = {"fragment_id": f["fragment_id"], "endpoint": tag, "gap": d1}
    ml = matches.get(left["fragment_id"]) if left else {}
    mr = matches.get(right["fragment_id"]) if right else {}
    same = bool(ml.get("matched_occ_branch") and ml.get("matched_occ_branch") == mr.get("matched_occ_branch"))
    # find gap between left/right fragments if different
    gap_rec = next(
        (
            g
            for g in gaps
            if {g["fragment_i"], g["fragment_j"]} == {left["fragment_id"], right["fragment_id"]}
        ),
        None,
    )
    if left and right and left["fragment_id"] == right["fragment_id"]:
        classification = "TRUE_TRIM_SEPARATION"
        action = "DO_NOT_STITCH"
        note = "WIRE_001 is a single open fragment edge; endpoints are fragment termini, not a missing stitch between two fragments."
    elif gap_rec:
        classification = gap_rec["classification"]
        action = {
            "TRUE_INTERSECTION_FRAGMENTATION": "V6A2_ANALYTIC_MASTER_EDGE_RECOVERY",
            "TRUE_TRIM_SEPARATION": "DO_NOT_STITCH",
            "FIT_TOPOLOGY_INCONSISTENT": "PATCH_OR_SURFACE_REFIT",
            "AMBIGUOUS": "MORE_BOUNDARY_EVIDENCE",
        }.get(classification, "MORE_BOUNDARY_EVIDENCE")
    else:
        classification = "FIT_TOPOLOGY_INCONSISTENT" if not same else "AMBIGUOUS"
        action = "PATCH_OR_SURFACE_REFIT" if classification == "FIT_TOPOLOGY_INCONSISTENT" else "MORE_BOUNDARY_EVIDENCE"
    return {
        "part": first_blocker.get("part", "PART_002"),
        "surface": first_blocker.get("surface"),
        "wire": first_blocker.get("wire") or first_blocker.get("wire_id"),
        "wire_start": ws.tolist(),
        "wire_end": we.tolist(),
        "expected_surface_pair": list(pair),
        "nearest_fragment_left": left["fragment_id"] if left else "",
        "nearest_fragment_right": right["fragment_id"] if right else "",
        "xyz_endpoint_gap": float(np.linalg.norm(we - ws)) if len(ws) == 3 and len(we) == 3 else None,
        "normalized_xyz_gap": float(np.linalg.norm(we - ws) / max(diag, 1e-12)) if len(ws) == 3 else None,
        "left_occ_branch": ml.get("matched_occ_branch"),
        "right_occ_branch": mr.get("matched_occ_branch"),
        "same_occ_branch": same,
        "analytic_gap_segment_length": gap_rec.get("analytic_gap_segment_length") if gap_rec else None,
        "surface_support_fraction": gap_rec.get("support_frac_surface") if gap_rec else None,
        "boundary_support_fraction": gap_rec.get("support_frac_boundary") if gap_rec else None,
        "surface_distance_p95": gap_rec.get("surface_distance_p95") if gap_rec else None,
        "boundary_distance_p95": gap_rec.get("boundary_distance_p95") if gap_rec else None,
        "uv_seam_crossing": False,
        "classification": classification,
        "recommended_next_action": action,
        "wire_is_single_fragment": bool(left and right and left["fragment_id"] == right["fragment_id"]),
        "fragment_id": left["fragment_id"] if left and right and left["fragment_id"] == right["fragment_id"] else None,
    }


def positive_control_pair_12(gaps: list[dict], accepted: list[dict]) -> dict:
    pair_gaps = [g for g in gaps if tuple(g["surface_pair"]) == (1, 2)]
    acc_ids = {(a["fragment_i"], a["fragment_j"]) for a in accepted}
    ok = any(g.get("v6a_accepted") and g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION" for g in pair_gaps)
    if not ok:
        ok = any(g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION" for g in pair_gaps) and len(acc_ids) >= 2
    return {
        "PAIR_1_2_POSITIVE_CONTROL_PASS": bool(ok),
        "accepted_v6a_connections": len(acc_ids),
        "pair_12_gaps": len(pair_gaps),
        "supported_gaps": sum(1 for g in pair_gaps if g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION"),
    }


def write_csvs(out_dir: Path, branches_by_pair, matches, gaps, uv_doc, baseline) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "analytic_branches.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair", "branch_id", "curve_type", "length", "closed", "start_x", "start_y", "start_z"])
        for label, branches in branches_by_pair.items():
            for b in branches:
                w.writerow([label, b["branch_id"], b["curve_type"], b["length"], b["closed"], *b["start"]])
    with (out_dir / "fragment_to_occ_branch.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fragment_id", "surface_pair", "matched_occ_branch", "mean_distance", "p95_distance", "tangent_alignment", "confidence"])
        for m in matches:
            w.writerow([m["fragment_id"], m["surface_pair"], m.get("matched_occ_branch"), m.get("mean_distance"), m.get("p95_distance"), m.get("tangent_alignment"), m.get("confidence")])
    with (out_dir / "gap_support_audit.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "fragment_i",
                "fragment_j",
                "surface_pair",
                "occ_branch",
                "classification",
                "endpoint_xyz_gap",
                "segment_length",
                "support_frac_surface",
                "support_frac_boundary",
                "surface_distance_p95",
                "boundary_distance_p95",
            ]
        )
        for g in gaps:
            w.writerow(
                [
                    g["fragment_i"],
                    g["fragment_j"],
                    g["surface_pair"],
                    g["occ_branch"],
                    g["classification"],
                    g["endpoint_xyz_gap"],
                    g["analytic_gap_segment_length"],
                    g.get("support_frac_surface"),
                    g.get("support_frac_boundary"),
                    g.get("surface_distance_p95"),
                    g.get("boundary_distance_p95"),
                ]
            )
    with (out_dir / "uv_periodicity_audit.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["surface_index", "surface_type", "u_periodic", "v_periodic", "u_period", "v_period"])
        for i, s in enumerate(uv_doc.get("surfaces") or []):
            w.writerow([i, s["surface_type"], s["u_periodic"], s["v_periodic"], s["u_period"], s["v_period"]])
    with (out_dir / "baseline_consistency_audit.csv").open("w", newline="") as f:
        w = csv.writer(f)
        for k, v in baseline.items():
            w.writerow([k, v])


def process_part(pid: str, v3_part: Path, xpart_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["baseline", "occ", "matching", "gaps", "topology", "csv", "renders", "repair_candidates"]:
        (out_dir / sub).mkdir(exist_ok=True)

    v5_part = V5_ROOT / pid
    v6a_part = V6A_ROOT / pid
    xpart = v4.load_mesh(xpart_path)
    diag = max(v4.bbox_diag(np.asarray(xpart.vertices, float)), 1e-12)
    p2c = v3_part / "point2cad"
    topo = v4.load_json(p2c / "topo/topo_world.json") or {}
    fits = v4.load_json(p2c / "surface_fits.json") or {}
    tf = v4.load_json(p2c / "p2c_normalize_transform.json")
    clipped = v4.load_mesh(p2c / "clipped/mesh_world.ply")
    surfaces_mesh = v4.split_surfaces_by_color(clipped)
    surf_models = v4.load_surface_models(fits.get("fits") or [], tf, surfaces_mesh)
    pair_map = v4.load_json(v5_part / "official_curves/surface_pairs.json") or {}

    frags = extract_fragments(topo, pair_map, diag)
    from airplane_point2cad_curve_branch_recovery_v6a.fragments import attach_fragment_features

    attach_fragment_features(frags, surfaces_mesh, xpart, diag)
    branch_doc = load_branch_doc(v6a_part, topo, pair_map, surfaces_mesh, xpart, diag)
    v6a_fb = json.loads((v6a_part / "topology/first_blocker.json").read_text()).get("first_blocker") or {}
    v6a_gate = json.loads((v6a_part / "part_gate.json").read_text()) if (v6a_part / "part_gate.json").is_file() else {}

    baseline = run_baseline_audit(
        topo, pair_map, v5_part, v6a_part, surfaces_mesh, xpart, diag, len(surf_models), branch_doc, v6a_fb
    )
    dump_json(out_dir / "baseline/baseline_consistency_audit.json", baseline)

    pairs = [(0, 1), (0, 2), (1, 2)]
    branches_by_pair = {}
    all_branches_json = {}
    for sa, sb in pairs:
        label = f"PAIR_{sa}_{sb}"
        branches = extract_occ_branches(surf_models[sa], surf_models[sb], (sa, sb), diag)
        branches_by_pair[label] = branches
        all_branches_json[label] = [{k: v for k, v in b.items() if k not in ("points", "parameters", "occ_curve")} for b in branches]
        pair_dir = out_dir / "occ" / label
        pair_dir.mkdir(parents=True, exist_ok=True)
        dump_json(pair_dir / "occ_branches.json", all_branches_json[label])

    pair_frags = {p: [f for f in frags if f["surface_pair"] == p] for p in pairs}
    matches_list = []
    matches_map = {}
    for p in pairs:
        label = f"PAIR_{p[0]}_{p[1]}"
        for f in pair_frags[p]:
            m = match_fragment_to_branch(f, branches_by_pair[label])
            matches_list.append(m)
            matches_map[f["fragment_id"]] = m
    dump_json(out_dir / "matching/fragment_to_occ_branch.json", matches_list)

    evidence = build_boundary_evidence(xpart, surfaces_mesh, diag)
    accepted = branch_doc.get("accepted_connections") or []
    acc_set = {tuple(sorted([a["fragment_i"], a["fragment_j"]])) for a in accepted}
    all_gaps = []
    for p in pairs:
        label = f"PAIR_{p[0]}_{p[1]}"
        gs = enumerate_gaps(pair_frags[p], matches_map, branches_by_pair[label], evidence, diag, acc_set)
        all_gaps.extend(gs)
        dump_json(out_dir / "gaps" / f"{label}_gaps.json", gs)

    uv_doc = audit_uv_rejections(branch_doc.get("candidates") or [], frags, surf_models, surfaces_mesh)
    dump_json(out_dir / "baseline/uv_periodicity_audit.json", uv_doc)

    fb_audit = first_blocker_analytic_audit(v6a_fb, frags, matches_map, all_gaps, [], evidence, diag)
    dump_json(out_dir / "topology/first_blocker_analytic_audit.json", fb_audit)

    pc = positive_control_pair_12(all_gaps, accepted)
    dump_json(out_dir / "gaps/pair_1_2_positive_control.json", pc)

    repair_candidates = [
        {
            "surface_pair": g["surface_pair"],
            "occ_branch": g["occ_branch"],
            "t_start": g["t_start"],
            "t_end": g["t_end"],
            "classification": g["classification"],
            "eligible_for_v6a2": g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION",
        }
        for g in all_gaps
        if g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION"
    ]
    dump_json(out_dir / "repair_candidates/repair_candidate.json", repair_candidates)

    write_csvs(out_dir / "csv", branches_by_pair, matches_list, all_gaps, uv_doc, baseline)

    counts = {
        "TRUE_INTERSECTION_FRAGMENTATION": sum(1 for g in all_gaps if g["classification"] == "TRUE_INTERSECTION_FRAGMENTATION"),
        "TRUE_TRIM_SEPARATION": sum(1 for g in all_gaps if g["classification"] == "TRUE_TRIM_SEPARATION"),
        "FIT_TOPOLOGY_INCONSISTENT": sum(1 for g in all_gaps if g["classification"] == "FIT_TOPOLOGY_INCONSISTENT"),
        "AMBIGUOUS": sum(1 for g in all_gaps if g["classification"] == "AMBIGUOUS"),
    }

    match_rates = {}
    for p in pairs:
        label = f"PAIR_{p[0]}_{p[1]}"
        pf = pair_frags[p]
        hi = sum(1 for f in pf if matches_map[f["fragment_id"]].get("confidence") in ("HIGH", "MEDIUM"))
        match_rates[label] = hi / max(len(pf), 1)

    # gate / next blocker
    main_pairs = [g for g in all_gaps if tuple(g["surface_pair"]) in ((0, 1), (0, 2))]
    classifiable = sum(1 for g in main_pairs if g["classification"] != "AMBIGUOUS")
    occ_ok = all(len(branches_by_pair[f"PAIR_{a}_{b}"]) > 0 for a, b in ((0, 1), (0, 2))) or any(
        len(branches_by_pair[f"PAIR_{a}_{b}"]) > 0 for a, b in ((0, 1), (0, 2))
    )
    if not occ_ok:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_BRANCH_SUPPORT_AUDIT_V6A1_FAIL"
        next_blocker = "OCC_INTERSECTION_FAILURE"
    elif classifiable >= len(main_pairs) * 0.5:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_BRANCH_SUPPORT_AUDIT_V6A1_PASS"
        next_blocker = fb_audit["classification"] if fb_audit["classification"] != "AMBIGUOUS" else "ANALYTIC_BRANCH_MATCHING_AMBIGUITY"
    else:
        gate = "AIRPLANE_POINT2CAD_ANALYTIC_BRANCH_SUPPORT_AUDIT_V6A1_PARTIAL_PASS"
        next_blocker = "ANALYTIC_BRANCH_MATCHING_AMBIGUITY"

    # per-pair primary classification
    pair_summary = {}
    for p in pairs:
        pg = [g for g in all_gaps if tuple(g["surface_pair"]) == p]
        counts_p = {k: sum(1 for g in pg if g["classification"] == k) for k in counts}
        dom = max(counts_p, key=counts_p.get) if pg else "NONE"
        pair_summary[f"PAIR_{p[0]}_{p[1]}_PRIMARY_CLASS"] = dom
        pair_summary[f"PAIR_{p[0]}_{p[1]}_GAP_COUNTS"] = counts_p

    if counts["FIT_TOPOLOGY_INCONSISTENT"] > counts["TRUE_INTERSECTION_FRAGMENTATION"]:
        if pair_summary.get("PAIR_0_2_PRIMARY_CLASS") == "TRUE_INTERSECTION_FRAGMENTATION":
            next_action = "V6A2_ANALYTIC_MASTER_EDGE_RECOVERY_FOR_PAIR_0_2_ONLY"
        else:
            next_action = "PATCH_OR_SURFACE_REFIT"
    elif counts["TRUE_INTERSECTION_FRAGMENTATION"] > 0:
        next_action = "V6A2_ANALYTIC_MASTER_EDGE_RECOVERY"
    elif counts["TRUE_TRIM_SEPARATION"] > 0:
        next_action = "DO_NOT_STITCH"
    else:
        next_action = "PATCH_OR_SURFACE_REFIT"

    if pair_summary.get("PAIR_0_1_PRIMARY_CLASS") == "FIT_TOPOLOGY_INCONSISTENT":
        next_blocker = "FIT_TOPOLOGY_INCONSISTENT"
    row = {
        "part": pid,
        **baseline,
        **counts,
        **uv_doc,
        **pc,
        "PAIR_0_1_OCC_BRANCHES": len(branches_by_pair["PAIR_0_1"]),
        "PAIR_0_2_OCC_BRANCHES": len(branches_by_pair["PAIR_0_2"]),
        "PAIR_1_2_OCC_BRANCHES": len(branches_by_pair["PAIR_1_2"]),
        "PAIR_0_1_FRAGMENT_MATCH_RATE": match_rates["PAIR_0_1"],
        "PAIR_0_2_FRAGMENT_MATCH_RATE": match_rates["PAIR_0_2"],
        "PAIR_1_2_FRAGMENT_MATCH_RATE": match_rates["PAIR_1_2"],
        "PAIR_0_1_GAPS_AUDITED": sum(1 for g in all_gaps if tuple(g["surface_pair"]) == (0, 1)),
        "PAIR_0_2_GAPS_AUDITED": sum(1 for g in all_gaps if tuple(g["surface_pair"]) == (0, 2)),
        "FIRST_BLOCKER_CLASSIFICATION": fb_audit["classification"],
        "FIRST_BLOCKER_ANALYTIC_BRANCH": fb_audit.get("left_occ_branch"),
        "FIRST_BLOCKER_SURFACE_SUPPORT": fb_audit.get("surface_support_fraction"),
        "FIRST_BLOCKER_BOUNDARY_SUPPORT": fb_audit.get("boundary_support_fraction"),
        "NEXT_PRIMARY_BLOCKER": next_blocker,
        "NEXT_RECOMMENDED_ACTION": next_action,
        "pair_summary": pair_summary,
        "TOPOLOGY_MODIFIED": False,
        "POINT2CAD_INTERSECTION_REEXECUTED": False,
        "CURRENT_GATE": gate,
        "first_blocker_audit": fb_audit,
        "gap_classifications": all_gaps,
    }
    dump_json(out_dir / "part_audit.json", {k: v for k, v in row.items() if k != "gap_classifications"})

    try:
        from .render import render_audit

        render_audit(xpart, out_dir / "renders", frags, branches_by_pair, all_gaps, fb_audit, evidence, pid)
    except Exception as exc:
        dump_json(out_dir / "renders/render_error.json", {"error": str(exc), "tb": traceback.format_exc()})

    return row
