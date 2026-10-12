#!/usr/bin/env python3
"""Airplane Route B V4: Point2CAD intersections → corners/wires → OCC solids.

Freezes P3/X-Part/Dora/V3 Point2CAD surfaces. Only PART_008, PART_002, PART_005.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4

V3 = ROOT / "ours3/airplane_routeb_point2cad_v3"
AIR = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_point2cad_brep_closure_v4"
PARTS = ["PART_008", "PART_002", "PART_005"]


def part_mesh(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    rows = []
    tot = {
        "RAW_INTERSECTION_CURVES": 0,
        "CORNER_CANDIDATES": 0,
        "MERGED_TOPO_CORNERS": 0,
        "RAW_INTERSECTION_EDGES": 0,
        "TRIMMED_TOPO_EDGES": 0,
        "MANIFOLD_EDGES": 0,
        "FREE_EDGES": 0,
        "NONMANIFOLD_EDGES": 0,
        "WIRE_COUNT": 0,
        "CLOSED_WIRES": 0,
        "OPEN_WIRES": 0,
        "VALID_TRIMMED_FACES": 0,
        "SHELLS": 0,
        "CLOSED_SHELLS": 0,
        "CLEAN_PARAMETRIC_PART_SOLIDS": 0,
        "BREP_VALID_PARTS": 0,
        "STEP_RELOAD_VALID_PARTS": 0,
    }
    for pid in PARTS:
        print(f"[V4] {pid}", flush=True)
        row = v4.process_part(pid, V3 / pid, part_mesh(pid), OUT / pid)
        rows.append(row)
        for k in tot:
            if k in ("BREP_VALID_PARTS", "STEP_RELOAD_VALID_PARTS"):
                continue
            src = "SHELL_COUNT" if k == "SHELLS" else k
            val = row.get(src)
            if val is None:
                val = row.get(k) or 0
            try:
                tot[k] += int(val)
            except (TypeError, ValueError):
                pass
        if row.get("BREP_VALID"):
            tot["BREP_VALID_PARTS"] += 1
        if row.get("STEP_RELOAD_VALID"):
            tot["STEP_RELOAD_VALID_PARTS"] += 1
        print(
            f"[V4] done {pid} corners={row.get('MERGED_TOPO_CORNERS')} "
            f"closed_wires={row.get('CLOSED_WIRES')} faces={row.get('VALID_TRIMMED_FACES')} "
            f"solids={row.get('CLEAN_PARAMETRIC_PART_SOLIDS')}",
            flush=True,
        )

    inc_rates = [float(r.get("FACE_EDGE_INCIDENCE_VALID_RATE") or 0) for r in rows]
    n008 = next((r.get("MERGED_TOPO_CORNERS") for r in rows if r["part"] == "PART_008"), 0)
    solids = tot["CLEAN_PARAMETRIC_PART_SOLIDS"]
    closed_w = tot["CLOSED_WIRES"]
    corners = tot["MERGED_TOPO_CORNERS"]
    if corners > 0 and closed_w > 0 and solids > 0:
        gate = "PASS"
        blocker = ""
    elif corners > 0 and closed_w > 0:
        gate = "PARTIAL_PASS"
        blocker = "NO_CLEAN_PARAMETRIC_SOLID"
    elif corners > 0:
        gate = "PARTIAL_PASS"
        blocker = "NO_CLOSED_WIRE"
    else:
        gate = "FAIL"
        blocker = "TOPO_CORNERS_STILL_ZERO"

    gate_obj = {
        "CURRENT_GATE": "AIRPLANE_POINT2CAD_BREP_CLOSURE_V4",
        "PARTS_ATTEMPTED": len(PARTS),
        "PARTS": PARTS,
        "POINT2CAD_SURFACES_REUSED": True,
        "POINT2CAD_INTERSECTIONS_REUSED": True,
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_SES_REEXECUTED": False,
        "PARSE_NET_USED": False,
        **tot,
        "FACE_EDGE_INCIDENCE_VALID_RATE": float(np.mean(inc_rates)) if inc_rates else 0.0,
        "PART_008_CORNER_COUNT": n008,
        "per_part": [{k: r[k] for k in r if k != "qa"} | {"IoU": (r.get("qa") or {}).get("IoU")} for r in rows],
        "ROUTE_B_V4_GATE": gate,
        "NEXT_PRIMARY_BLOCKER": blocker,
        "ARTIFACT_ROOT": str(OUT),
    }
    v4.dump_json(OUT / "gate.json", gate_obj)
    lines = [
        "# Airplane Point2CAD B-Rep Closure V4",
        "",
        "Frozen: P3 / X-Part / Dora / V3 Point2CAD surfaces + intersection polylines.",
        "Changed: official `distance == 0` corner test → tolerant segment-segment + shared-surface filter.",
        "",
        f"- TOPO_CORNERS: 0 → {corners}",
        f"- CLOSED_WIRES: 0 → {closed_w}",
        f"- CLOSED_SHELLS: {tot['CLOSED_SHELLS']}",
        f"- CLEAN_PARAMETRIC_PART_SOLIDS: {solids}",
        f"- PART_008_CORNER_COUNT: {n008}",
        "",
        "```text",
    ]
    for k, val in gate_obj.items():
        if k != "per_part":
            lines.append(f"{k}={val}")
    lines += ["```", ""]
    for r in rows:
        lines.append(
            f"- {r['part']}: corners={r.get('MERGED_TOPO_CORNERS')} "
            f"trimmed_edges={r.get('TRIMMED_TOPO_EDGES')} manifold={r.get('MANIFOLD_EDGES')} "
            f"closed_wires={r.get('CLOSED_WIRES')} open_wires={r.get('OPEN_WIRES')} "
            f"faces={r.get('VALID_TRIMMED_FACES')} clean_solids={r.get('CLEAN_PARAMETRIC_PART_SOLIDS')} "
            f"eps={r.get('eps_frac')}"
        )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (520, 40 + 220 * len(PARTS)), "white")
        dr = ImageDraw.Draw(img)
        for i, pid in enumerate(PARTS):
            dr.text((8, 12 + i * 220), pid, fill=(20, 20, 20))
            p = OUT / pid / "renders/01_corners_edges.png"
            if p.is_file():
                im = Image.open(p).convert("RGB").resize((500, 200))
                img.paste(im, (8, 28 + i * 220))
        img.save(OUT / "contact_sheet.png")
    except Exception as exc:
        print("contact sheet fail", exc, flush=True)
    for k, val in gate_obj.items():
        if k != "per_part":
            print(f"{k}={val}")
    return 0 if gate != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
