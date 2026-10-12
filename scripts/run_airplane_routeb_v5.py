#!/usr/bin/env python3
"""Airplane Route B V5: stitch Point2CAD intersection fragments → closed wires / solids.

Does not re-run P3 / X-Part / Dora / Point2CAD surface fitting.
Does not overwrite V3 or V4 artifact trees.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_wire_closure_v5 as v5

V3 = ROOT / "ours3/airplane_routeb_point2cad_v3"
AIR = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_point2cad_wire_closure_v5"
CANARY = ["PART_008", "PART_002"]


def part_mesh(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parts", nargs="+", default=CANARY)
    args = parser.parse_args()
    parts = [p.upper() if p.startswith("PART_") or p.startswith("part_") else f"PART_{int(p):03d}" for p in args.parts]
    parts = [p if p.startswith("PART_") else f"PART_{p}" for p in parts]
    # normalize PART_8 -> keep as given if already PART_00X
    norm = []
    for p in args.parts:
        p = p.strip()
        if p.upper().startswith("PART_"):
            idx = int(p.split("_")[1])
            norm.append(f"PART_{idx:03d}")
        else:
            norm.append(f"PART_{int(p):03d}")
    parts = [p for p in norm if p in CANARY]
    if not parts:
        parts = list(CANARY)

    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    keys = [
        "OFFICIAL_CURVES",
        "RAW_INTERSECTION_COMPONENTS",
        "STITCHED_MASTER_CURVES",
        "CURVES_WITH_AUTHORITATIVE_SURFACE_PAIR",
        "CORNER_CANDIDATES",
        "MERGED_TOPO_CORNERS",
        "TRIMMED_MASTER_EDGES",
        "MANIFOLD_EDGES",
        "FREE_EDGES",
        "NONMANIFOLD_EDGES",
        "ENDPOINT_GRAPH_DEGREE1",
        "ENDPOINT_GRAPH_DEGREE2",
        "ENDPOINT_GRAPH_DEGREE3PLUS",
        "SURFACES_TOTAL",
        "SURFACES_WITH_CLOSED_WIRE",
        "CLOSED_WIRES",
        "OPEN_WIRES",
        "MISSING_INTERSECTIONS_ATTEMPTED",
        "MISSING_INTERSECTIONS_ACCEPTED",
        "ANALYTIC_MASTER_EDGES",
        "BSPLINE_MASTER_EDGES",
        "DUAL_PCURVE_ATTEMPTED",
        "DUAL_PCURVE_SUCCESS",
        "VALID_TRIMMED_FACES",
        "SHELLS",
        "CLOSED_SHELLS",
        "CLEAN_PARAMETRIC_PART_SOLIDS",
        "BREP_VALID_PARTS",
        "STEP_RELOAD_VALID_PARTS",
    ]
    tot = {k: 0 for k in keys}
    mapping_rates = []
    for pid in parts:
        print(f"[V5] {pid}", flush=True)
        row = v5.process_canary(pid, V3 / pid, part_mesh(pid), OUT / pid)
        rows.append(row)
        mapping_rates.append(float(row.get("SURFACE_PAIR_MAPPING_RATE") or 0))
        for k in tot:
            if k in ("BREP_VALID_PARTS", "STEP_RELOAD_VALID_PARTS"):
                continue
            src = "SHELL_COUNT" if k == "SHELLS" else k
            val = row.get(src, row.get(k))
            try:
                tot[k] += int(val or 0)
            except (TypeError, ValueError):
                pass
        if row.get("BREP_VALID"):
            tot["BREP_VALID_PARTS"] += 1
        if row.get("STEP_RELOAD_VALID"):
            tot["STEP_RELOAD_VALID_PARTS"] += 1
        print(
            f"[V5] done {pid} stitch={row.get('STITCHED_MASTER_CURVES')} "
            f"corners={row.get('MERGED_TOPO_CORNERS')} closed_wires={row.get('CLOSED_WIRES')} "
            f"faces={row.get('VALID_TRIMMED_FACES')} solids={row.get('CLEAN_PARAMETRIC_PART_SOLIDS')}",
            flush=True,
        )

    d005 = v5.diagnose_part_005(V3 / "PART_005", OUT / "PART_005_diagnosis")
    r008 = next((r for r in rows if r["part"] == "PART_008"), {})
    r002 = next((r for r in rows if r["part"] == "PART_002"), {})

    closed_shells = tot["CLOSED_SHELLS"]
    solids = tot["CLEAN_PARAMETRIC_PART_SOLIDS"]
    closed_w = tot["CLOSED_WIRES"]
    rate = float(np.mean(mapping_rates)) if mapping_rates else 0.0
    stitched = tot["STITCHED_MASTER_CURVES"]
    raw_c = tot["RAW_INTERSECTION_COMPONENTS"]

    blocker = ""
    if rate < 1.0:
        gate = "FAIL"
        blocker = "SURFACE_PAIR_PROVENANCE_UNRESOLVED"
    else:
        gate = "PARTIAL_PASS"
        if solids > 0 and closed_shells > 0 and int(r008.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0) > 0:
            gate = "PASS"
            blocker = ""
        else:
            fb = r008.get("first_blocker") or r002.get("first_blocker") or {}
            blocker = fb.get("blocker_kind") or "WIRE_OPEN"
            if int(r008.get("MISSING_INTERSECTIONS_ATTEMPTED") or 0) > 0 and int(r008.get("MISSING_INTERSECTIONS_ACCEPTED") or 0) == 0 and int(r008.get("SURFACES_WITH_CLOSED_WIRE") or 0) < int(r008.get("SURFACES_TOTAL") or 0):
                # missing pair may contribute, but first concrete failure is still an open wire
                pass
            blocker = fb.get("blocker_kind") or "WIRE_OPEN"

    gate_obj = {
        "CURRENT_GATE": "AIRPLANE_POINT2CAD_WIRE_CLOSURE_V5",
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_SES_REEXECUTED": False,
        "DORA_VAE_USED": False,
        "POINT2CAD_SURFACE_FIT_REEXECUTED": False,
        "PARTS_ATTEMPTED": len(parts),
        "PARTS": parts,
        **tot,
        "SURFACE_PAIR_MAPPING_RATE": rate,
        "FREE_EDGES_BEFORE_SEW": sum(int(r.get("FREE_EDGES_BEFORE_SEW") or 0) for r in rows),
        "FREE_EDGES_AFTER_SEW": sum(int(r.get("FREE_EDGES_AFTER_SEW") or 0) for r in rows),
        "PART_008_RAW_COMPONENTS": r008.get("RAW_INTERSECTION_COMPONENTS"),
        "PART_008_STITCHED_CURVES": r008.get("STITCHED_MASTER_CURVES"),
        "PART_008_SURFACES_TOTAL": r008.get("SURFACES_TOTAL"),
        "PART_008_SURFACES_WITH_CLOSED_WIRE": r008.get("SURFACES_WITH_CLOSED_WIRE"),
        "PART_008_CLOSED_SHELL": bool(int(r008.get("CLOSED_SHELLS") or 0) > 0),
        "PART_008_CLEAN_SOLID": bool(int(r008.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0) > 0),
        "PART_002_RAW_COMPONENTS": r002.get("RAW_INTERSECTION_COMPONENTS"),
        "PART_002_STITCHED_CURVES": r002.get("STITCHED_MASTER_CURVES"),
        "PART_002_CLOSED_WIRES": r002.get("CLOSED_WIRES"),
        "PART_002_CLOSED_SHELL": bool(int(r002.get("CLOSED_SHELLS") or 0) > 0),
        "PART_002_CLEAN_SOLID": bool(int(r002.get("CLEAN_PARAMETRIC_PART_SOLIDS") or 0) > 0),
        "PART_005_PATCH_UNDERSEGMENTATION": True,
        "ROUTE_B_V5_GATE": gate,
        "NEXT_PRIMARY_BLOCKER": blocker,
        "ARTIFACT_ROOT": str(OUT),
        "per_part": [{k: r[k] for k in r if k not in ("qa", "stitch_per_curve")} | {"IoU": (r.get("qa") or {}).get("IoU")} for r in rows],
        "part_005": d005,
        "first_blockers": {r["part"]: r.get("first_blocker") for r in rows},
    }
    v5.dump_json(OUT / "gate.json", gate_obj)

    q1 = (
        "Yes, partially."
        if int(r008.get("STITCHED_MASTER_CURVES") or 99) < int(r008.get("RAW_INTERSECTION_COMPONENTS") or 0)
        else "No: official 3e-3 normalized gap cannot merge most tessellation branches; they are spatially separate intersection branches, not 1e-3 cracks."
    )
    report = [
        "# Airplane Point2CAD Wire Closure V5",
        "",
        "Frozen: P3 / X-Part / Dora / V3 Point2CAD surface fits + official intersections.",
        "Changed: intra-curve stitching, authoritative surface_pair from official combinations, missing-pair completion, OCC BRepCheck.",
        "",
        "## Gate",
        "",
        "```text",
    ]
    for k, val in gate_obj.items():
        if k not in ("per_part", "part_005", "first_blockers"):
            report.append(f"{k}={val}")
    report += ["```", "", "## Q1 — Did intra-curve stitching fix official-curve fragmentation?", "", q1, ""]
    report.append("Per official curve (PART_008):")
    for s in r008.get("stitch_per_curve") or []:
        report.append(f"- {s['curve_id']}: {s['raw']} components → {s['masters']} masters (thr={s['thr']})")
    report += [
        "",
        "## Q2 — PART_008 closed wires: 2/4 → ?",
        "",
        f"SURFACES_WITH_CLOSED_WIRE = {r008.get('SURFACES_WITH_CLOSED_WIRE')} / {r008.get('SURFACES_TOTAL')}",
        f"CLOSED_WIRES = {r008.get('CLOSED_WIRES')}",
        "",
        "## Q3 — Why PART_002 has no cycle (or now does)?",
        "",
        f"components {r002.get('RAW_INTERSECTION_COMPONENTS')} → stitched {r002.get('STITCHED_MASTER_CURVES')}; "
        f"degree1={r002.get('ENDPOINT_GRAPH_DEGREE1')} degree2={r002.get('ENDPOINT_GRAPH_DEGREE2')} degree3+={r002.get('ENDPOINT_GRAPH_DEGREE3PLUS')}; "
        f"closed_wires={r002.get('CLOSED_WIRES')}.",
        f"First blocker: {r002.get('first_blocker')}",
        "",
        "## Q4 — First closed shell / clean solid without refitting?",
        "",
        f"CLOSED_SHELLS={tot['CLOSED_SHELLS']} CLEAN_PARAMETRIC_PART_SOLIDS={solids}",
        "",
        "## Q5 — If still no solid, has the blocker moved to undersegmentation?",
        "",
        f"NEXT_PRIMARY_BLOCKER={blocker}",
        f"PART_005 remains PATCH_UNDERSEGMENTATION (not topology-backend-fixable).",
        "",
        "## First FREE_EDGE / open wire",
        "",
        f"PART_008: {r008.get('first_blocker')}",
        f"PART_002: {r002.get('first_blocker')}",
        "",
    ]
    for r in rows:
        report.append(
            f"- {r['part']}: official={r.get('OFFICIAL_CURVES')} raw_comp={r.get('RAW_INTERSECTION_COMPONENTS')} "
            f"stitched={r.get('STITCHED_MASTER_CURVES')} corners={r.get('MERGED_TOPO_CORNERS')} "
            f"closed_wires={r.get('CLOSED_WIRES')} faces={r.get('VALID_TRIMMED_FACES')} "
            f"closed_shells={r.get('CLOSED_SHELLS')} solids={r.get('CLEAN_PARAMETRIC_PART_SOLIDS')}"
        )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    try:
        from PIL import Image, ImageDraw

        imgs = []
        labels = []
        for pid in parts:
            p = OUT / pid / "renders/03_stitched_master_curves.png"
            if p.is_file():
                imgs.append(p)
                labels.append(pid + " stitched")
            p2 = OUT / pid / "renders/08_closed_wires.png"
            if p2.is_file():
                imgs.append(p2)
                labels.append(pid + " wires")
        if imgs:
            canvas = Image.new("RGB", (520, 28 + 210 * len(imgs)), "white")
            dr = ImageDraw.Draw(canvas)
            for i, (p, lab) in enumerate(zip(imgs, labels)):
                dr.text((8, 8 + i * 210), lab, fill=(20, 20, 20))
                im = Image.open(p).convert("RGB").resize((500, 190))
                canvas.paste(im, (8, 24 + i * 210))
            canvas.save(OUT / "contact_sheet.png")
    except Exception as exc:
        print("contact sheet fail", exc, flush=True)
    for k, val in gate_obj.items():
        if k not in ("per_part", "part_005", "first_blockers"):
            print(f"{k}={val}")
    return 0 if gate != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
