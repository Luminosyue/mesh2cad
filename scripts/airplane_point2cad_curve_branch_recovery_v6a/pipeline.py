"""V6A pipeline: branch recovery → wires → BRep for PART_002."""
from __future__ import annotations

import json
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4
import routeb_point2cad_wire_closure_v5 as v5

from .branch_recovery import recover_all_branches
from .fragments import (
    attach_fragment_features,
    extract_fragments,
    histograms,
    score_connection,
    sha256_file,
)

V5_ROOT = ROOT / "ours3/airplane_point2cad_wire_closure_v5"


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def load_v5_baseline(pid: str) -> dict:
    p = V5_ROOT / pid / "part_gate.json"
    return json.loads(p.read_text()) if p.is_file() else {}


def build_input_manifest(
    pid: str,
    v3_part: Path,
    xpart_path: Path,
    v5_part: Path,
    out_dir: Path,
) -> dict:
    sources = {
        "topo_world": v3_part / "point2cad/topo/topo_world.json",
        "surface_fits": v3_part / "point2cad/surface_fits.json",
        "clipped_mesh": v3_part / "point2cad/clipped/mesh_world.ply",
        "xpart_mesh": xpart_path,
        "v5_surface_pairs": v5_part / "official_curves/surface_pairs.json",
        "v5_part_gate": v5_part / "part_gate.json",
        "v5_first_blocker": v5_part / "topology/first_blocker.json",
        "v5_wires": v5_part / "wires/wires.json",
    }
    manifest = {
        "part": pid,
        "p3_reexecuted": False,
        "xpart_reexecuted": False,
        "point2cad_surface_fit_reexecuted": False,
        "source_files": {k: str(v) for k, v in sources.items()},
        "source_hashes": {k: sha256_file(v) for k, v in sources.items() if v.is_file()},
    }
    dump_json(out_dir / "input_manifest.json", manifest)
    return manifest


def fragments_as_masters(frags: list[dict]) -> list[dict]:
    masters = []
    for f in frags:
        masters.append(
            {
                "master_id": f["fragment_id"],
                "parent_curve_id": f["curve_id"],
                "surface_a": f["surface_a"],
                "surface_b": f["surface_b"],
                "points": np.asarray(f["points"], dtype=float),
                "closed": bool(f.get("closed")),
                "source": "RAW_FRAGMENT",
                "fragment_ids": [f["fragment_id"]],
            }
        )
    return masters


def branches_to_masters(
    branches: list[dict],
    surf_models: list[dict],
    xpart,
    diag: float,
) -> tuple[list[dict], dict]:
    masters = []
    stats = {"ANALYTIC": 0, "BSPLINE": 0, "POLYLINE": 0}
    for b in branches:
        pts = np.asarray(b["points"], dtype=float)
        sa, sb = int(b["surface_pair"][0]), int(b["surface_pair"][1])
        src = "POLYLINE"
        edge_kind = "branch_polyline"
        if len(pts) >= 4:
            ae = v4.try_analytic_edge(surf_models[sa], surf_models[sb], pts, diag)
            if ae is not None:
                src = "ANALYTIC"
                edge_kind = "OCC_SURFACE_INTERSECTION"
                stats["ANALYTIC"] += 1
            else:
                src = "BSPLINE"
                edge_kind = "P2C_POLYLINE_BSPLINE"
                stats["BSPLINE"] += 1
        else:
            stats["POLYLINE"] += 1
        masters.append(
            {
                "master_id": f"BR_{b['pair_label']}_B{b['branch_id']:03d}",
                "parent_curve_id": b.get("fragment_ids", ["?"])[0].split("_C")[0] if b.get("fragment_ids") else "BRANCH",
                "surface_a": sa,
                "surface_b": sb,
                "points": pts,
                "closed": bool(b.get("closed")),
                "source": "BRANCH_RECOVERY",
                "edge_kind": edge_kind,
                "fragment_ids": b.get("fragment_ids") or [],
                "branch_id": b.get("branch_id"),
                "n_fragments": len(b.get("fragment_ids") or []),
                "connections": len(b.get("connections") or []),
            }
        )
    return masters, stats


def topology_from_masters(
    masters: list[dict],
    n_surf: int,
    diag: float,
) -> dict:
    frac, corners, n_cand, _ = v5.pick_corners(masters, diag)
    eps = frac * diag
    corners = v4.merge_close_corners(
        [
            {
                "vertex_id": c["vertex_id"],
                "xyz": c["xyz"],
                "curve_ids": c.get("incident_curve_ids") or [],
                "n_candidates": c.get("n_candidates", 1),
                "mean_pair_dist": c.get("mean_pair_dist", 0),
                "shared_surface": True,
            }
            for c in corners
        ],
        eps,
    )
    for i, c in enumerate(corners):
        c["vertex_id"] = f"V_{i:03d}"
    edges, verts = v5.trim_masters(masters, corners, diag, eps)
    graph = v5.surface_boundary_graph(n_surf, edges, verts)
    wires, missing = v5.recover_surface_wires(n_surf, edges, graph)
    deg = v5.classify_edge_degree(edges, wires)
    n_closed = sum(1 for w in wires if w.get("closed") and w.get("WIRE_VALID"))
    n_open = sum(1 for w in wires if not w.get("closed"))
    return {
        "frac": frac,
        "eps": eps,
        "corners": corners,
        "n_cand": n_cand,
        "edges": edges,
        "verts": verts,
        "graph": graph,
        "wires": wires,
        "missing": missing,
        "deg": deg,
        "n_closed": n_closed,
        "n_open": n_open,
    }


def find_best_rejected_candidate(
    frags: list[dict],
    fid_to_frag: dict,
    endpoint_xyz: np.ndarray,
    pair: tuple[int, int],
    surfaces: list,
    xpart,
    diag: float,
) -> dict | None:
    best = None
    for f in frags:
        if f["surface_pair"] != pair:
            continue
        for ea, eb, p in (("s", "s", f["start_xyz"]), ("s", "e", f["end_xyz"]), ("e", "s", f["start_xyz"]), ("e", "e", f["end_xyz"])):
            rec = score_connection(
                {"fragment_id": "_QUERY", "surface_pair": pair, **{k: fid_to_frag.get(f["fragment_id"], f)[k] for k in fid_to_frag.get(f["fragment_id"], f) if k != "fragment_id"}},
                f,
                "s" if ea == "s" else "e",
                eb,
                surfaces,
                xpart,
                diag,
            )
            # fix query endpoint to match target
            pa = np.asarray(p, float)
            gap = float(np.linalg.norm(pa - endpoint_xyz))
            if best is None or gap < best["endpoint_gap"]:
                best = {
                    "fragment_id": f["fragment_id"],
                    "endpoint_gap": gap,
                    "normalized_gap": gap / max(diag, 1e-12),
                    "tangent_angle_deg": rec["tangent_angle_deg"],
                    "uv_gap_A": rec["uv_gap_A"],
                    "uv_gap_B": rec["uv_gap_B"],
                    "support_fraction": rec["support_fraction"],
                    "reason_rejected": rec["reason_rejected"],
                    "accepted": rec["accepted"],
                }
    return best


def diagnose_first_blocker(
    pid: str,
    topo: dict,
    frags: list[dict],
    branch_doc: dict,
    after: dict,
    surfaces: list,
    xpart,
    diag: float,
) -> dict:
    open_w = [w for w in after["wires"] if not w.get("closed")]
    vxyz = {v["vertex_id"]: v.get("xyz") for v in after["verts"]}
    blocker_cat = "NONE"
    first = None
    if open_w:
        w = open_w[0]
        vids = w.get("vertex_ids") or []
        xyz_s = vxyz.get(vids[0]) if vids else None
        xyz_e = vxyz.get(vids[-1]) if vids else None
        pair_guess = None
        cand_frags = []
        for e in after["edges"]:
            if e["edge_id"] in (w.get("edge_ids") or []):
                pair_guess = (e.get("surface_a"), e.get("surface_b"))
                cand_frags = [f["fragment_id"] for f in frags if f["surface_pair"] == (e.get("surface_a"), e.get("surface_b"))]
        best_gap = None
        best_tan = None
        best_uv = None
        best_sup = None
        reason = ""
        if xyz_e is not None and pair_guess:
            fid_map = {f["fragment_id"]: f for f in frags}
            bc = find_best_rejected_candidate(frags, fid_map, np.asarray(xyz_e, float), pair_guess, surfaces, xpart, diag)
            if bc:
                best_gap = bc["endpoint_gap"]
                best_tan = bc["tangent_angle_deg"]
                best_uv = max(bc["uv_gap_A"], bc["uv_gap_B"])
                best_sup = bc["support_fraction"]
                reason = ",".join(bc["reason_rejected"]) or ("ACCEPTED_BUT_NOT_STITCHED" if bc["accepted"] else "AMBIGUOUS")
        if reason.startswith("GAP") or (best_gap and best_gap > 0.003 * diag):
            blocker_cat = "INTERSECTION_BRANCH_FRAGMENTATION"
        elif "TANGENT" in reason:
            blocker_cat = "MISSING_SUPPORTED_CONTINUATION"
        elif "UV" in reason:
            blocker_cat = "AMBIGUOUS_BRANCH_CORRESPONDENCE"
        elif "XPART" in reason or (best_sup is not None and best_sup < 0.35):
            blocker_cat = "MISSING_SUPPORTED_CONTINUATION"
        elif after["n_closed"] < len(surfaces):
            blocker_cat = "WIRE_ORDERING_FAILURE"
        else:
            blocker_cat = "SHELL_CLOSURE_FAILURE"
        first = {
            "part": pid,
            "surface": w.get("surface"),
            "wire": w.get("wire_id"),
            "start": xyz_s or [],
            "end": xyz_e or [],
            "expected_surface_pair": list(pair_guess) if pair_guess else [],
            "candidate_fragments": cand_frags[:8],
            "best_candidate_gap": best_gap,
            "best_candidate_tangent_angle": best_tan,
            "best_candidate_uv_gap": best_uv,
            "best_candidate_support_fraction": best_sup,
            "reason_rejected": reason,
            "blocker_category": blocker_cat,
        }
    elif int(after.get("n_closed") or 0) == 0:
        blocker_cat = "INTERSECTION_BRANCH_FRAGMENTATION"
    return {"first_blocker": first, "blocker_category": blocker_cat, "n_open_wires": len(open_w)}


def classify_gate(
    v5: dict,
    before_d1: int,
    after_d1: int,
    branch_doc: dict,
    occ: dict,
    qa: dict,
) -> tuple[str, str]:
    solids = int(occ.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0)
    closed_shells = int(occ.get("CLOSED_SHELLS") or 0)
    geo_ok = bool(qa.get("IoU") is not None and float(qa.get("IoU") or 0) >= 0.05)
    if (
        closed_shells >= 1
        and solids >= 1
        and occ.get("BREP_VALID")
        and occ.get("STEP_RELOAD_VALID")
        and geo_ok
    ):
        return "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_PASS", "NONE"
    accepted = len(branch_doc.get("accepted_connections") or [])
    rejected = len(branch_doc.get("rejected_connections") or [])
    improved = after_d1 < before_d1 - 2 or after_d1 < int(v5.get("ENDPOINT_GRAPH_DEGREE1") or before_d1) - 2
    if improved and accepted > 0:
        fb = "INTERSECTION_BRANCH_FRAGMENTATION"
        if after_d1 > 0:
            fb = "MISSING_SUPPORTED_CONTINUATION"
        return "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_PARTIAL_PASS", fb
    if accepted == 0 and rejected > 0:
        return "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_FAIL", "INTERSECTION_BRANCH_FRAGMENTATION"
    return "AIRPLANE_POINT2CAD_CURVE_BRANCH_RECOVERY_V6A_PARTIAL_PASS", "INTERSECTION_BRANCH_FRAGMENTATION"


def process_part(pid: str, v3_part: Path, xpart_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    v5_part = V5_ROOT / pid
    for sub in [
        "branch_recovery",
        "topology",
        "corners",
        "wires",
        "faces",
        "shell",
        "solid",
        "qa",
        "renders",
    ]:
        (out_dir / sub).mkdir(exist_ok=True)

    build_input_manifest(pid, v3_part, xpart_path, v5_part, out_dir)
    v5_base = load_v5_baseline(pid)
    pair_map = v4.load_json(v5_part / "official_curves/surface_pairs.json") or {}

    xpart = v4.load_mesh(xpart_path)
    diag = max(v4.bbox_diag(np.asarray(xpart.vertices, float)), 1e-12)
    p2c = v3_part / "point2cad"
    topo = v4.load_json(p2c / "topo/topo_world.json") or {}
    fits = v4.load_json(p2c / "surface_fits.json") or {}
    tf = v4.load_json(p2c / "p2c_normalize_transform.json")
    clipped = v4.load_mesh(p2c / "clipped/mesh_world.ply")
    surfaces = v4.split_surfaces_by_color(clipped)
    surf_models = v4.load_surface_models(fits.get("fits") or [], tf, surfaces)

    frags = extract_fragments(topo, pair_map, diag)
    attach_fragment_features(frags, surfaces, xpart, diag)
    dump_json(out_dir / "branch_recovery/fragments.json", [{k: v for k, v in f.items() if k != "points"} | {"n_points": len(f["points"])} for f in frags])

    before_topo = topology_from_masters(fragments_as_masters(frags), len(surfaces), diag)
    branch_doc = recover_all_branches(frags, surfaces, xpart, diag)
    dump_json(out_dir / "branch_recovery/histograms.json", histograms(branch_doc["candidates"]))
    for label, pdata in branch_doc["per_pair"].items():
        pair_dir = out_dir / "branch_recovery" / label
        pair_dir.mkdir(parents=True, exist_ok=True)
        dump_json(
            pair_dir / "branches.json",
            {
                "surface_pair": pdata["surface_pair"],
                "branches": [{k: v for k, v in b.items() if k != "points"} for b in pdata["branches"]],
                "accepted_connections": pdata["accepted_connections"],
                "rejected_connections": pdata["rejected_connections"][:200],
            },
        )

    masters, mstats = branches_to_masters(branch_doc["branches"], surf_models, xpart, diag)
    dump_json(out_dir / "branch_recovery/masters.json", [{k: v for k, v in m.items() if k != "points"} | {"n_points": len(m["points"])} for m in masters])

    after_topo = topology_from_masters(masters, len(surfaces), diag)
    dump_json(out_dir / "corners/corners.json", after_topo["corners"])
    dump_json(out_dir / "wires/wires.json", after_topo["wires"])
    dump_json(out_dir / "topology/incidence_graph.json", {"graph_summary": {k: after_topo["graph"][k] for k in after_topo["graph"] if k != "adj"}})
    dump_json(out_dir / "topology/trimmed_edges.json", [{k: v for k, v in e.items() if k != "points"} for e in after_topo["edges"]])

    occ = v5.build_occ_v5(
        xpart,
        surf_models,
        after_topo["edges"],
        after_topo["wires"],
        after_topo["verts"],
        out_dir / f"{pid}.step",
        diag,
        after_topo["eps"],
    )
    dump_json(out_dir / "faces/brep.json", occ)
    dump_json(out_dir / "shell/shell.json", {k: occ.get(k) for k in ("SHELL_COUNT", "CLOSED_SHELLS", "FREE_EDGE_COUNT", "FREE_EDGES_BEFORE_SEW", "FREE_EDGES_AFTER_SEW")})
    dump_json(out_dir / "solid/solid.json", {k: occ.get(k) for k in ("SOLID_COUNT", "CLEAN_PARAMETRIC_PART_SOLIDS", "BREP_VALID", "STEP_RELOAD_VALID")})

    qa = {}
    try:
        import routeb_edge_curve_recovery_v2 as v2

        if (out_dir / f"{pid}.step").is_file():
            qa = v2.geometry_qa(xpart, out_dir / f"{pid}.step")
    except Exception as exc:
        qa = {"GEOMETRY_QA_FAIL": True, "error": str(exc)}
    dump_json(out_dir / "qa/qa.json", qa)

    fb_doc = diagnose_first_blocker(pid, topo, frags, branch_doc, after_topo, surfaces, xpart, diag)
    dump_json(out_dir / "topology/first_blocker.json", fb_doc)

    gate_name, next_blocker = classify_gate(
        v5_base,
        before_topo["graph"]["ENDPOINT_GRAPH_DEGREE1"],
        after_topo["graph"]["ENDPOINT_GRAPH_DEGREE1"],
        branch_doc,
        occ,
        qa,
    )
    if fb_doc.get("blocker_category") and fb_doc["blocker_category"] != "NONE":
        next_blocker = fb_doc["blocker_category"]

    row = {
        "part": pid,
        "RAW_FRAGMENTS": len(frags),
        "RECOVERED_BRANCHES": len(branch_doc["branches"]),
        "ACCEPTED_CONNECTIONS": len(branch_doc["accepted_connections"]),
        "REJECTED_CONNECTIONS": len(branch_doc["rejected_connections"]),
        "DEGREE1_BEFORE": before_topo["graph"]["ENDPOINT_GRAPH_DEGREE1"],
        "DEGREE1_AFTER": after_topo["graph"]["ENDPOINT_GRAPH_DEGREE1"],
        "DEGREE2_BEFORE": before_topo["graph"]["ENDPOINT_GRAPH_DEGREE2"],
        "DEGREE2_AFTER": after_topo["graph"]["ENDPOINT_GRAPH_DEGREE2"],
        "DEGREE3PLUS_BEFORE": before_topo["graph"]["ENDPOINT_GRAPH_DEGREE3PLUS"],
        "DEGREE3PLUS_AFTER": after_topo["graph"]["ENDPOINT_GRAPH_DEGREE3PLUS"],
        "OPEN_WIRES_BEFORE": before_topo["n_open"],
        "OPEN_WIRES_AFTER": after_topo["n_open"],
        "CLOSED_WIRES_BEFORE": before_topo["n_closed"],
        "CLOSED_WIRES_AFTER": after_topo["n_closed"],
        "V5_DEGREE1": v5_base.get("ENDPOINT_GRAPH_DEGREE1"),
        "V5_CLOSED_WIRES": v5_base.get("CLOSED_WIRES"),
        "V5_OPEN_WIRES": v5_base.get("OPEN_WIRES"),
        "OFFICIAL_SURFACE_PAIRS": v5_base.get("CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR"),
        "SURFACE_PAIR_MAPPING_RATE": v5_base.get("SURFACE_PAIR_MAPPING_RATE"),
        "TRIMMED_FACES_VALID": occ.get("VALID_TRIMMED_FACES"),
        "FREE_SHELL_EDGES": occ.get("FREE_EDGE_COUNT"),
        "CLOSED_SHELLS": occ.get("CLOSED_SHELLS"),
        "CLEAN_PARAMETRIC_PART_SOLIDS": occ.get("CLEAN_PARAMETRIC_PART_SOLIDS"),
        "DUAL_PCURVE_SUCCESS": occ.get("DUAL_PCURVE_SUCCESS"),
        "SHARED_OCC_EDGE_COUNT": len(after_topo["edges"]),
        "STEP_EXPORTED": (out_dir / f"{pid}.step").is_file(),
        "STEP_RELOAD_VALID": bool(occ.get("STEP_RELOAD_VALID")),
        "TOPOLOGY_PASS": after_topo["n_closed"] >= int(v5_base.get("CLOSED_WIRES") or 0),
        "GEOMETRY_PASS": bool(qa.get("IoU") is not None and float(qa.get("IoU") or 0) >= 0.05),
        "Chamfer": qa.get("Chamfer"),
        "Hausdorff": qa.get("Hausdorff"),
        "Coverage": qa.get("Coverage"),
        "FALSE_POSITIVE_OCCUPANCY": qa.get("FALSE_POSITIVE_OCCUPANCY"),
        "IoU": qa.get("IoU"),
        "NEXT_PRIMARY_BLOCKER": next_blocker,
        "master_stats": mstats,
        "first_blocker": fb_doc.get("first_blocker"),
    }
    dump_json(out_dir / "part_gate.json", row)

    try:
        from .render import render_v6a

        render_v6a(
            xpart,
            out_dir / "renders",
            frags,
            branch_doc,
            before_topo,
            after_topo,
            occ,
            pid,
        )
    except Exception as exc:
        dump_json(out_dir / "renders/render_error.json", {"error": str(exc), "tb": traceback.format_exc()})

    return row
