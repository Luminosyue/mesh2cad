#!/usr/bin/env python3
"""Airplane Hybrid Geometry Router V1 — geometry-driven CAD backend selection."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from hybrid_geometry_router.assembly import (  # noqa: E402
    cadfit_world_mesh,
    cadfit_world_shape,
    load_step_shape,
    write_compound_step,
)
from hybrid_geometry_router.decomposition import decompose_mesh  # noqa: E402
from hybrid_geometry_router.geometry_features import extract_geometry_features  # noqa: E402
from hybrid_geometry_router.io_utils import dump_json, load_json, load_mesh, sha256  # noqa: E402
from hybrid_geometry_router.qa import (  # noqa: E402
    cadfit_qa_fail,
    geometry_qa,
    geometry_score,
    region_masked_qa,
    selection_score,
)
from hybrid_geometry_router.render import (  # noqa: E402
    render_assembly,
    render_mesh,
    render_overlay,
    render_router_chart,
)
from hybrid_geometry_router.router import compute_router_scores  # noqa: E402

SOURCE_OBJ = ROOT / "ours3/meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
AIR_ROUTEA = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
AIR_ROUTEB = ROOT / "ours3/airplane_routeb_point2cad_v3"
OUT = ROOT / "ours3/airplane_hybrid_geometry_router_v1"

SELECTION_WEIGHTS = {"geometry": 0.60, "validity": 0.20, "compactness": 0.10, "analyticity": 0.10}
MAX_DECOMPOSITION_DEPTH = 2
PALETTE = ["#E45756", "#4C78A8", "#54A24B", "#F58518", "#B279A2", "#72B7B2", "#EECA3B", "#FF9DA6", "#9D755D"]


def part_mesh_path(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR_ROUTEA / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def routea_step(pid: str) -> Path:
    return AIR_ROUTEA / "cadfit_routea/step" / pid / f"{pid}.step"


def routea_recon_stl(pid: str) -> Path:
    p = AIR_ROUTEA / "cadfit_routea/step" / pid / f"{pid}_reconstructed.stl"
    if p.is_file():
        return p
    raw = AIR_ROUTEA / "cadfit_routea/cadfit_raw" / pid / "best_greedy_parallel_iterative.stl"
    return raw


def routea_qa_json(pid: str) -> dict:
    p = AIR_ROUTEA / "cadfit_routea/qa" / pid / "qa.json"
    if p.is_file():
        return load_json(p, {})
    summary = load_json(AIR_ROUTEA / "cadfit_routea/qa/summary.json", [])
    for row in summary:
        if row.get("PART_ID") == pid:
            return row
    return {}


def routeb_step(pid: str) -> Path:
    return AIR_ROUTEB / pid / f"{pid}.step"


def routeb_mesh(pid: str) -> Path | None:
    for rel in ["point2cad/clipped/mesh_world.ply", "point2cad/unclipped/mesh_world.ply"]:
        p = AIR_ROUTEB / pid / rel
        if p.is_file():
            return p
    return None


def routeb_qa_json(pid: str) -> dict:
    return load_json(AIR_ROUTEB / pid / "qa/geometry_qa.json", {})


def validate_provenance() -> dict:
    meta = load_json(AIR_ROUTEA / "p3/part_metadata.json", {})
    src = str(meta.get("source_mesh") or "")
    ok_path = Path(src) == SOURCE_OBJ
    ok_hash = sha256(SOURCE_OBJ) if SOURCE_OBJ.is_file() else ""
    audit = {
        "source_path": str(SOURCE_OBJ),
        "source_sha256": ok_hash,
        "routea_source_mesh": src,
        "source_path_match": ok_path,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "routea_root": str(AIR_ROUTEA),
        "routeb_root": str(AIR_ROUTEB),
        "part_count": int(meta.get("num_parts") or 0),
    }
    if not ok_path:
        raise RuntimeError(f"SOURCE_MISMATCH expected {SOURCE_OBJ} got {src}")
    return audit


def cadfit_ops(pid: str) -> dict:
    qa = routea_qa_json(pid)
    ops = int(qa.get("OP_COUNT") or 0)
    extr = int(qa.get("EXTRUDE_COUNT") or 0)
    rev = int(qa.get("REVOLVE_COUNT") or 0)
    return {"op_count": ops, "extrude": extr, "revolve": rev, "cut": int(qa.get("CUT_COUNT") or 0)}


def load_candidate_meshes(pid: str, src: trimesh.Trimesh) -> dict[str, trimesh.Trimesh | None]:
    out = {"cadfit": None, "routeb": None}
    recon = routea_recon_stl(pid)
    if routea_step(pid).is_file() and recon.is_file():
        _, matrix = cadfit_world_shape(routea_step(pid), part_mesh_path(pid), recon)
        out["cadfit"] = cadfit_world_mesh(recon, matrix)
    rb = routeb_mesh(pid)
    if rb is not None:
        out["routeb"] = load_mesh(rb)
    return out


def evaluate_candidate(pid: str, backend: str, src: trimesh.Trimesh, mesh: trimesh.Trimesh | None, step_path: Path | None) -> dict:
    if mesh is None or step_path is None or not step_path.is_file():
        return {"backend": backend, "available": False}
    qa = geometry_qa(src, mesh, qa_source=f"HYBRID_{backend.upper()}")
    ra = routea_qa_json(pid)
    if backend == "cadfit" and ra.get("CADFIT_IOU") is not None:
        qa["IoU"] = float(ra["CADFIT_IOU"])
        qa["Chamfer"] = float(ra.get("CHAMFER") or qa["Chamfer"])
        qa["Hausdorff"] = float(ra.get("HAUSDORFF") or qa["Hausdorff"])
        qa["Coverage"] = float(ra.get("COVERAGE") or qa["Coverage"])
        qa["QA_SOURCE"] = "ROUTEA_QA_JSON+HYBRID_MESH"
    rb = routeb_qa_json(pid)
    if backend == "routeb" and rb:
        for k in ("IoU", "Chamfer", "Hausdorff", "Coverage", "FP_OCCUPANCY"):
            if rb.get(k) is not None:
                qa[k] = rb[k]
        qa["QA_SOURCE"] = "ROUTEB_QA_JSON"
    ops = cadfit_ops(pid) if backend == "cadfit" else {"op_count": 0, "extrude": 0, "revolve": 0, "cut": 0}
    validity = 1.0
    try:
        load_step_shape(step_path)
    except Exception:
        validity = 0.0
    compactness = 1.0 / (1.0 + ops["op_count"] / 20.0) if backend == "cadfit" else 0.7
    analyticity = (ops["extrude"] + ops["revolve"]) / max(ops["op_count"], 1) if backend == "cadfit" else 0.2
    sel = selection_score(qa, validity, compactness, analyticity, SELECTION_WEIGHTS)
    return {
        "backend": backend,
        "available": True,
        "step_path": str(step_path),
        "qa": qa,
        "geometry_score": geometry_score(qa),
        "selection_score": sel,
        "validity": validity,
        "compactness": compactness,
        "analyticity": analyticity,
        "ops": ops,
        "CADFIT_ROUTE_REJECTED": backend == "cadfit" and cadfit_qa_fail(qa),
    }


def stage_geometry_features(parts: list[str]) -> dict[str, dict]:
    rows = {}
    for pid in parts:
        mesh = load_mesh(part_mesh_path(pid))
        feats = extract_geometry_features(mesh, pid)
        route = compute_router_scores(feats, mesh)
        dump_json(OUT / "geometry_features" / f"{pid}.json", route)
        rows[pid] = route
    dump_json(OUT / "router_summary.json", {"parts": rows, "generated_at": datetime.now(timezone.utc).isoformat()})
    return rows


def stage_routing(parts: list[str], feature_rows: dict[str, dict]) -> dict[str, dict]:
    routing = {}
    for pid in parts:
        row = feature_rows[pid].copy()
        mesh = load_mesh(part_mesh_path(pid))
        if row["selected_route"] == "MIXED_STRUCTURE":
            regions = decompose_mesh(mesh, features=row)
            if regions:
                reg_dump = []
                for r in regions:
                    reg_dir = OUT / "decomposition" / pid
                    reg_dir.mkdir(parents=True, exist_ok=True)
                    obj_out = reg_dir / f"{r['region_id']}.obj"
                    r["mesh"].export(str(obj_out))
                    reg_dump.append(
                        {
                            "region_id": r["region_id"],
                            "area_ratio": r["area_ratio"],
                            "selected_route": r["routing"]["selected_route"],
                            "selected_backend": r["routing"]["selected_backend"],
                            "reason_codes": r["routing"]["reason_codes"],
                            "HOMOGENEITY_BEFORE": r.get("HOMOGENEITY_BEFORE"),
                            "HOMOGENEITY_AFTER": r.get("HOMOGENEITY_AFTER"),
                            "mesh_path": str(obj_out),
                        }
                    )
                dump_json(OUT / "decomposition" / f"{pid}_regions.json", reg_dump)
                row["regions"] = reg_dump
                row["region_count"] = len(regions)
                backends = {r["routing"]["selected_backend"] for r in regions}
                if len(backends) > 1:
                    row["mixed_backend_part"] = True
            else:
                row["DECOMPOSITION_REJECTED"] = True
                # Mixed geometry is incompatible with a single CADFit program.
                row["selected_route"] = "THIN_FREEFORM"
                row["selected_backend"] = "DORA_POINT2CAD"
                row["reason_codes"] = list(row.get("reason_codes", [])) + ["DECOMPOSITION_REJECTED", "FALLBACK_ROUTEB_AFTER_MIXED"]
        dump_json(OUT / "routing" / f"{pid}.json", row)
        routing[pid] = row
        if row.get("selected_route") != "MIXED_STRUCTURE":
            stale = OUT / "decomposition" / f"{pid}_regions.json"
            if stale.is_file():
                stale.unlink()
    return routing


def stage_candidates(parts: list[str], routing: dict[str, dict]) -> dict[str, dict]:
    selected = {}
    for pid in parts:
        src = load_mesh(part_mesh_path(pid))
        meshes = load_candidate_meshes(pid, src)
        cands = {
            "cadfit": evaluate_candidate(pid, "cadfit", src, meshes["cadfit"], routea_step(pid)),
            "routeb": evaluate_candidate(pid, "routeb", src, meshes["routeb"], routeb_step(pid)),
        }
        best_name = None
        best = None
        for name, cand in cands.items():
            if not cand.get("available"):
                continue
            if best is None or cand["selection_score"] > best["selection_score"]:
                best, best_name = cand, name

        fallback_used = False
        cad = cands.get("cadfit") or {}
        rb = cands.get("routeb") or {}
        if cad.get("CADFIT_ROUTE_REJECTED") and rb.get("available"):
            if best_name == "cadfit" or not cad.get("available"):
                best, best_name = rb, "routeb"
                fallback_used = True
        elif best_name == "routeb" and cad.get("available") and not cad.get("CADFIT_ROUTE_REJECTED"):
            cad_iou = float((cad.get("qa") or {}).get("IoU") or 0)
            rb_iou = float((rb.get("qa") or {}).get("IoU") or 0)
            if cad_iou >= rb_iou + 0.05:
                best, best_name = cad, "cadfit"

        rec = {
            "part_id": pid,
            "router_backend": routing[pid]["selected_backend"],
            "router_route": routing[pid]["selected_route"],
            "candidates": cands,
            "selected_backend": best_name,
            "selected_step": best.get("step_path") if best else None,
            "selected_qa": best.get("qa") if best else None,
            "selection_score": best.get("selection_score") if best else None,
            "CADFIT_ROUTE_REJECTED": cands.get("cadfit", {}).get("CADFIT_ROUTE_REJECTED", False),
            "fallback_to_routeb": fallback_used,
            "is_mixed_part": bool(routing[pid].get("mixed_backend_part")),
            "region_count": routing[pid].get("region_count", 0),
        }
        dump_json(OUT / "selected_parts" / f"{pid}.json", rec)
        if best and best.get("step_path"):
            dst = OUT / "selected_parts" / pid / f"{pid}.step"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(best["step_path"], dst)
        selected[pid] = rec
    return selected


def stage_assembly(parts: list[str], selected: dict[str, dict]) -> dict:
    shapes = []
    placed_meshes = []
    for i, pid in enumerate(parts):
        rec = selected[pid]
        step = rec.get("selected_step")
        if not step or not Path(step).is_file():
            continue
        shp = load_step_shape(Path(step))
        if rec["selected_backend"] == "cadfit":
            src = load_mesh(part_mesh_path(pid))
            recon = routea_recon_stl(pid)
            shp, _ = cadfit_world_shape(Path(step), part_mesh_path(pid), recon)
        shapes.append(shp)
        mesh = load_candidate_meshes(pid, load_mesh(part_mesh_path(pid)))
        m = mesh.get(rec["selected_backend"])
        if m is not None:
            placed_meshes.append((m, PALETTE[i % len(PALETTE)]))
    out_step = OUT / "assembly/airplane_hybrid_router_v1.step"
    reload_ok = write_compound_step(shapes, out_step) if shapes else False
    if placed_meshes:
        render_assembly(placed_meshes, OUT / "renders/airplane_hybrid_router.png", "Hybrid Router CAD Assembly")
    return {"FINAL_ASSEMBLY_STEP": str(out_step), "ASSEMBLY_STEP_RELOAD_VALID": reload_ok, "parts_in_assembly": len(shapes)}


def stage_renders(parts: list[str], routing: dict, selected: dict) -> None:
    pure_meshes = []
    hybrid_meshes = []
    source_meshes = []
    for i, pid in enumerate(parts):
        src = load_mesh(part_mesh_path(pid))
        source_meshes.append(src)
        rdir = OUT / "renders" / pid
        rdir.mkdir(parents=True, exist_ok=True)
        render_mesh(src, rdir / "01_xpart.png", "#4C78A8", f"{pid} X-Part")
        render_router_chart(routing[pid], rdir / "03_router_decision.png")
        meshes = load_candidate_meshes(pid, src)
        if meshes["cadfit"] is not None:
            render_mesh(meshes["cadfit"], rdir / "06_cadfit_candidate.png", "#E45756", f"{pid} CADFit")
            pure_meshes.append(meshes["cadfit"])
        if meshes["routeb"] is not None:
            render_mesh(meshes["routeb"], rdir / "07_routeb_candidate.png", "#F58518", f"{pid} Route B")
        sel = selected[pid]
        if sel.get("selected_backend") and meshes.get(sel["selected_backend"]) is not None:
            render_mesh(meshes[sel["selected_backend"]], rdir / "08_selected_final.png", "#54A24B", f"{pid} Selected")
            hybrid_meshes.append(meshes[sel["selected_backend"]])
        decomp_path = OUT / "decomposition" / f"{pid}_regions.json"
        if decomp_path.is_file():
            reg_info = load_json(decomp_path, [])
            fig_parts = []
            colors = ["#4C78A8", "#E45756", "#54A24B", "#F58518"]
            for j, reg in enumerate(reg_info):
                mobj = OUT / "decomposition" / pid / f"{reg['region_id']}.obj"
                if mobj.is_file():
                    fig_parts.append((load_mesh(mobj), colors[j % len(colors)]))
            if fig_parts:
                render_assembly(fig_parts, rdir / "04_structural_regions.png", f"{pid} structural regions")

    if source_meshes:
        src_scene = trimesh.util.concatenate(source_meshes)
        render_mesh(src_scene, OUT / "renders/airplane_source.png", "#4C78A8", "Source X-Part Assembly")
    if pure_meshes:
        pure_scene = trimesh.util.concatenate(pure_meshes)
        render_mesh(pure_scene, OUT / "renders/airplane_pure_cadfit.png", "#E45756", "Pure Route A CADFit")
    if hybrid_meshes:
        hy_scene = trimesh.util.concatenate(hybrid_meshes)
        render_mesh(hy_scene, OUT / "renders/airplane_hybrid_router.png", "#54A24B", "Hybrid Router Assembly")
        if source_meshes:
            render_overlay(src_scene, hy_scene, OUT / "renders/airplane_source_vs_hybrid.png", "Source vs Hybrid")


def build_comparison_csv(parts: list[str], selected: dict) -> None:
    rows = []
    for pid in parts:
        ra = routea_qa_json(pid)
        rb = routeb_qa_json(pid)
        sel = selected[pid]
        hy = sel.get("selected_qa") or {}
        rows.append(
            {
                "PART_ID": pid,
                "ROUTER_CLASS": sel.get("router_route"),
                "SELECTED_BACKEND": sel.get("selected_backend"),
                "ROUTE_A_IOU": ra.get("CADFIT_IOU"),
                "ROUTE_A_FP": None,
                "ROUTE_A_OPS": ra.get("OP_COUNT"),
                "ROUTEB_IOU": rb.get("IoU"),
                "ROUTEB_FP": rb.get("FP_OCCUPANCY"),
                "HYBRID_IOU": hy.get("IoU"),
                "HYBRID_FP": hy.get("FP_OCCUPANCY"),
                "IOU_DELTA": (hy.get("IoU") or 0) - (ra.get("CADFIT_IOU") or 0),
                "FP_DELTA": (hy.get("FP_OCCUPANCY") or 0) - (0 if ra.get("CADFIT_IOU") is None else 0),
            }
        )
    csv_path = OUT / "pure_routea_vs_hybrid.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    dump_json(OUT / "hybrid_selection.csv", rows)


def build_routing_table(parts: list[str], routing: dict) -> None:
    rows = []
    for pid in parts:
        r = routing[pid]
        rows.append(
            {
                "Part": pid,
                "Geometry class": r.get("GEOMETRY_REGIME"),
                "CADFit score": round(r["CADFIT_SCORE"], 4),
                "RouteB score": round(r["ROUTEB_SCORE"], 4),
                "Decompose score": round(r["DECOMPOSE_SCORE"], 4),
                "Selected": r["selected_route"],
                "Confidence": round(r["confidence"], 4),
                "Reason codes": ";".join(r.get("reason_codes", [])),
            }
        )
    with (OUT / "router_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def build_gate(parts: list[str], routing: dict, selected: dict, assembly: dict, audit: dict) -> dict:
    route_counts = Counter(r["selected_route"] for r in routing.values())
    backend_counts = Counter(s.get("selected_backend") for s in selected.values())
    ra_ious = [float(routea_qa_json(p).get("CADFIT_IOU") or 0) for p in parts]
    hy_ious = [float((selected[p].get("selected_qa") or {}).get("IoU") or 0) for p in parts if selected[p].get("selected_qa")]
    rb_fp = [float(routeb_qa_json(p).get("FP_OCCUPANCY") or 0) for p in parts]
    hy_fp = [float((selected[p].get("selected_qa") or {}).get("FP_OCCUPANCY") or 0) for p in parts if selected[p].get("selected_qa")]

    p003 = selected.get("PART_003", {})
    p003_ra = routea_qa_json("PART_003").get("CADFIT_IOU")
    p003_hy = (p003.get("selected_qa") or {}).get("IoU")

    diverse_routes = (
        route_counts.get("REGULAR_CADFIT", 0) > 0
        and (route_counts.get("THIN_FREEFORM", 0) + route_counts.get("MIXED_STRUCTURE", 0)) > 0
    ) or (backend_counts.get("cadfit", 0) > 0 and backend_counts.get("routeb", 0) > 0)
    not_all_cadfit = backend_counts.get("cadfit", 0) < len(parts)
    not_all_routeb = backend_counts.get("routeb", 0) < len(parts)
    iou_improved = bool(hy_ious) and float(np.mean(hy_ious)) > float(np.mean(ra_ious))
    decompose_used = route_counts.get("MIXED_STRUCTURE", 0) > 0

    p003_route = routing.get("PART_003", {}).get("selected_route", "")
    p003_fail = (
        routing.get("PART_003", {}).get("selected_route") == "REGULAR_CADFIT"
        and routing.get("PART_003", {}).get("confidence", 0) > 0.65
        and selected.get("PART_003", {}).get("selected_backend") == "cadfit"
        and (p003_hy or 0) <= (p003_ra or 0) * 1.02
    )

    router_gate = "PASS" if (
        diverse_routes
        and not_all_cadfit
        and not_all_routeb
        and iou_improved
        and decompose_used
        and assembly.get("ASSEMBLY_STEP_RELOAD_VALID")
        and not p003_fail
    ) else "FAIL"

    blocker = ""
    if not diverse_routes:
        blocker = "Router did not produce diverse backend assignments"
    elif not decompose_used:
        blocker = "Mixed-structure decomposition was not triggered"
    elif not iou_improved:
        blocker = "Hybrid mean IoU did not improve over pure Route A"
    elif p003_fail:
        blocker = "PART_003 still high-confidence CADFit without geometry improvement"
    elif not assembly.get("ASSEMBLY_STEP_RELOAD_VALID"):
        blocker = "Hybrid assembly STEP reload failed"

    gate = {
        "CURRENT_GATE": "AIRPLANE_HYBRID_GEOMETRY_ROUTER_V1",
        "SOURCE_CASE": SOURCE_OBJ.name,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "PARTS_TOTAL": len(parts),
        "CADFIT_ROUTED_PARTS": sum(1 for r in routing.values() if r["selected_backend"] == "CADFIT"),
        "ROUTEB_ROUTED_PARTS": sum(1 for r in routing.values() if r["selected_backend"] == "DORA_POINT2CAD"),
        "DECOMPOSE_ROUTED_PARTS": route_counts.get("MIXED_STRUCTURE", 0),
        "UNSUPPORTED_PARTS": route_counts.get("UNSUPPORTED", 0),
        "DECOMPOSED_REGIONS": sum(r.get("region_count", 0) for r in routing.values()),
        "REGIONS_TO_CADFIT": sum(
            1 for r in routing.values() for g in r.get("regions") or [] if g.get("selected_backend") == "CADFIT"
        ),
        "REGIONS_TO_ROUTEB": sum(
            1 for r in routing.values() for g in r.get("regions") or [] if g.get("selected_backend") == "DORA_POINT2CAD"
        ),
        "CADFIT_ROUTE_ACCEPTED": sum(1 for s in selected.values() if s.get("selected_backend") == "cadfit"),
        "CADFIT_ROUTE_REJECTED_BY_QA": sum(1 for s in selected.values() if s.get("CADFIT_ROUTE_REJECTED")),
        "ROUTEB_ROUTE_ACCEPTED": sum(1 for s in selected.values() if s.get("selected_backend") == "routeb"),
        "FINAL_SELECTED_CADFIT_PARTS": backend_counts.get("cadfit", 0),
        "FINAL_SELECTED_ROUTEB_PARTS": backend_counts.get("routeb", 0),
        "FINAL_SELECTED_MIXED_PARTS": sum(1 for s in selected.values() if s.get("is_mixed_part")),
        "PURE_ROUTE_A_MEAN_IOU": float(np.mean(ra_ious)),
        "HYBRID_MEAN_IOU": float(np.mean(hy_ious)) if hy_ious else None,
        "PURE_ROUTE_A_MEAN_FP_OCCUPANCY": None,
        "HYBRID_MEAN_FP_OCCUPANCY": float(np.mean(hy_fp)) if hy_fp else None,
        "PART_003_SELECTED_ROUTE": routing.get("PART_003", {}).get("selected_route"),
        "PART_003_ROUTER_REASON": ";".join(routing.get("PART_003", {}).get("reason_codes", [])),
        "PART_003_REGION_COUNT": routing.get("PART_003", {}).get("region_count", 0),
        "PART_003_IOU_BEFORE": p003_ra,
        "PART_003_IOU_AFTER": p003_hy,
        **assembly,
        "ARTIFACT_ROOT": str(OUT),
        "ROUTER_GATE": router_gate,
        "NEXT_PRIMARY_BLOCKER": blocker or "Mixed parts were decomposed for routing, but region-level CADFit/Point2CAD was not re-run; whole-part selected STEP is used in assembly.",
        "decompose_evidence": decompose_used,
        "selection_weights": SELECTION_WEIGHTS,
        **audit,
    }
    dump_json(OUT / "gate.json", gate)
    return gate


def build_report(gate: dict, routing: dict, selected: dict) -> None:
    lines = [
        "# Airplane Hybrid Geometry Router V1",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Gate",
        "",
        "```text",
    ]
    for k in [
        "CURRENT_GATE", "ROUTER_GATE", "P3_REEXECUTED", "XPART_REEXECUTED",
        "CADFIT_ROUTED_PARTS", "ROUTEB_ROUTED_PARTS", "DECOMPOSE_ROUTED_PARTS",
        "PURE_ROUTE_A_MEAN_IOU", "HYBRID_MEAN_IOU", "PART_003_SELECTED_ROUTE",
        "PART_003_IOU_BEFORE", "PART_003_IOU_AFTER", "FINAL_ASSEMBLY_STEP", "NEXT_PRIMARY_BLOCKER",
    ]:
        lines.append(f"{k}={gate.get(k)}")
    lines.extend(["```", "", "## Q1 — Why pure CADFit blocky?", ""])
    thin = [p for p, r in routing.items() if r["THICKNESS_RATIO"] < 0.15]
    lines.append(f"- Thin parts (THICKNESS_RATIO<0.15): {', '.join(thin) or 'none'}")
    lines.append(f"- Mean FREEFORM_SCORE: {np.mean([r['FREEFORM_SCORE'] for r in routing.values()]):.3f}")
    lines.append(f"- Zero revolve in Route A baseline (all extrude+union)")
    lines.extend(["", "## Q2 — Router assignments", ""])
    for pid, r in routing.items():
        lines.append(f"- {pid}: {r['selected_route']} ({r['selected_backend']}) conf={r['confidence']:.2f} reasons={r.get('reason_codes')}")
    lines.extend(["", "## Q3 — Mixed structure", ""])
    mixed = [p for p, r in routing.items() if r.get("region_count")]
    lines.append(f"- Parts decomposed: {mixed or 'none'}")
    lines.extend(["", "## Q5 — Hybrid vs Route A", ""])
    lines.append(f"- Mean IoU: {gate.get('PURE_ROUTE_A_MEAN_IOU'):.4f} → {gate.get('HYBRID_MEAN_IOU'):.4f}")
    lines.extend(["", "## Q6 — PART_003", ""])
    lines.append(f"- Route: {gate.get('PART_003_SELECTED_ROUTE')}, IoU {gate.get('PART_003_IOU_BEFORE')} → {gate.get('PART_003_IOU_AFTER')}")
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-renders", action="store_true")
    args = ap.parse_args()

    for d in [
        "geometry_features", "routing", "decomposition", "cadfit", "routeb",
        "selected_parts", "assembly", "qa", "renders", "logs",
    ]:
        (OUT / d).mkdir(parents=True, exist_ok=True)

    audit = validate_provenance()
    xman = load_json(AIR_ROUTEA / "xpart/manifest.json", {})
    parts = sorted(r["part_id"] for r in xman.get("parts", []) if r.get("watertight") and r.get("success"))

    print("[1/6] geometry features", flush=True)
    features = stage_geometry_features(parts)
    print("[2/6] routing", flush=True)
    routing = stage_routing(parts, features)
    build_routing_table(parts, routing)
    print("[3/6] candidate selection", flush=True)
    selected = stage_candidates(parts, routing)
    build_comparison_csv(parts, selected)
    print("[4/6] assembly", flush=True)
    assembly = stage_assembly(parts, selected)
    if not args.skip_renders:
        print("[5/6] renders", flush=True)
        stage_renders(parts, routing, selected)
    print("[6/6] gate + report", flush=True)
    gate = build_gate(parts, routing, selected, assembly, audit)
    dump_json(
        OUT / "pipeline_manifest.json",
        {
            "case": OUT.name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "stages": ["geometry_features", "routing", "decomposition", "selection", "assembly", "qa", "renders"],
            "reuse": {"routea": str(AIR_ROUTEA), "routeb": str(AIR_ROUTEB)},
            "selection_weights": SELECTION_WEIGHTS,
        },
    )
    build_report(gate, routing, selected)
    print(json.dumps({k: gate[k] for k in gate if k not in {"source_sha256"}}, indent=2))
    return 0 if gate.get("ROUTER_GATE") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
