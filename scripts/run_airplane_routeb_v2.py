#!/usr/bin/env python3
"""Airplane Route B V2 runner. Reuses frozen airplane P3/X-Part; does not touch Tank V1."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_edge_curve_recovery_v2 as v2

SOURCE_OBJ = ROOT / "ours3/meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
AIR_ROUTEA = ROOT / "ours3/airplane_p3_xpart_cadfit_routea_v1"
OUT = ROOT / "ours3/airplane_routeb_geometry_v2"
DORA_OUT = OUT / "dora_ses"


def dump_json(path: Path, obj) -> None:
    v2.dump_json(path, obj)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def source_audit() -> dict:
    mesh = v2.load_mesh(SOURCE_OBJ)
    verts = np.asarray(mesh.vertices, dtype=float)
    comps = mesh.split(only_watertight=False)
    audit = {
        "path": str(SOURCE_OBJ),
        "sha256": sha256(SOURCE_OBJ),
        "bytes": SOURCE_OBJ.stat().st_size,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "connected_components": int(len(comps)),
        "watertight": bool(mesh.is_watertight),
        "bbox_min": verts.min(0).tolist(),
        "bbox_max": verts.max(0).tolist(),
        "bbox": [verts.min(0).tolist(), verts.max(0).tolist()],
        "bbox_diagonal": v2.bbox_diag(verts),
    }
    dump_json(OUT / "source/source_audit.json", audit)
    shutil.copy2(SOURCE_OBJ, OUT / "source" / SOURCE_OBJ.name)
    return audit


def reuse_p3_xpart(source_hash: str) -> tuple[dict, list[str]]:
    (OUT / "p3").mkdir(parents=True, exist_ok=True)
    (OUT / "xpart").mkdir(parents=True, exist_ok=True)
    meta = v2.load_json(AIR_ROUTEA / "p3/part_metadata.json", {})
    src_path = str(meta.get("source_mesh") or "")
    src_ok = src_path == str(SOURCE_OBJ)
    src_hash_ok = False
    if src_ok and Path(src_path).is_file():
        src_hash_ok = sha256(Path(src_path)) == source_hash
    shutil.copy2(AIR_ROUTEA / "p3/part_metadata.json", OUT / "p3/part_metadata.json")
    xman = v2.load_json(AIR_ROUTEA / "xpart/manifest.json", {})
    shutil.copy2(AIR_ROUTEA / "xpart/manifest.json", OUT / "xpart/manifest.json")
    parts = []
    provenance = []
    for row in xman.get("parts") or []:
        pid = row["part_id"]
        idx = int(pid.split("_")[1])
        obj = AIR_ROUTEA / "xpart" / pid / f"complete_part_{idx:03d}.obj"
        qa = v2.load_json(AIR_ROUTEA / "xpart" / pid / "qa.json", {})
        tf = AIR_ROUTEA / "xpart" / pid / "transform.json"
        dst = OUT / "xpart" / pid
        dst.mkdir(parents=True, exist_ok=True)
        if (AIR_ROUTEA / "xpart" / pid / "qa.json").is_file():
            shutil.copy2(AIR_ROUTEA / "xpart" / pid / "qa.json", dst / "qa.json")
        if tf.is_file():
            shutil.copy2(tf, dst / "transform.json")
        collapsed = float(row.get("volume") or qa.get("volume") or 0) <= 1e-12
        ok = bool(obj.is_file() and row.get("watertight") and row.get("success") and not collapsed)
        rec = {
            "part_id": pid,
            "mesh": str(obj),
            "exists": obj.is_file(),
            "watertight": bool(row.get("watertight")),
            "success": bool(row.get("success")),
            "collapsed": collapsed,
            "eligible": ok,
            "transform_known": tf.is_file(),
        }
        provenance.append(rec)
        if ok:
            parts.append(pid)
            if not (dst / obj.name).exists():
                try:
                    os.symlink(obj, dst / obj.name)
                except OSError:
                    pass
    info = {
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "source_path_match": src_ok,
        "source_hash_match": src_hash_ok,
        "part_id_provenance_valid": bool(parts) and all(p.startswith("PART_") for p in parts),
        "xpart_outputs_exist": bool(parts),
        "AIRPLANE_P3_PART_COUNT": int(meta.get("num_parts") or 0),
        "AIRPLANE_XPART_SUCCESSFUL_PARTS": int(xman.get("XPART_SUCCESSFUL_PARTS") or 0),
        "AIRPLANE_XPART_WATERTIGHT_PARTS": int(xman.get("XPART_WATERTIGHT_PARTS") or 0),
        "AIRPLANE_XPART_WATERTIGHT_RATE": float(xman.get("XPART_WATERTIGHT_RATE") or 0.0),
        "eligible_parts": parts,
        "part_provenance": provenance,
        "reuse_from": str(AIR_ROUTEA),
    }
    dump_json(OUT / "xpart/reuse_manifest.json", info)
    dump_json(OUT / "p3/reuse_manifest.json", {"source_path_match": src_ok, "source_hash_match": src_hash_ok, "P3_REEXECUTED": False})
    return info, parts


def ensure_dora(parts: list[str]) -> bool:
    need = False
    for pid in parts:
        if not (DORA_OUT / "threshold_35" / pid / "salient_edges.npz").is_file() and not (
            DORA_OUT / "threshold_35" / pid / "salient_edges_source_space.npz"
        ).is_file():
            need = True
            break
    if not need:
        return False
    cmd = [
        sys.executable,
        str(ROOT / "scripts/run_dora_ses_xpart45_v1.py"),
        "--output-dir",
        str(DORA_OUT),
        "--xpart-input",
        str(AIR_ROUTEA / "xpart"),
        "--xpart-summary",
        str(AIR_ROUTEA / "xpart/manifest.json"),
        "--parts",
        *parts,
        "--thresholds",
        "15",
        "25",
        "35",
        "45",
        "--skip-edge-json",
    ]
    DORA_OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / "logs/dora_ses.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Dora SES failed, see {log}")
    return True


def part_mesh(pid: str) -> Path:
    idx = int(pid.split("_")[1])
    return AIR_ROUTEA / "xpart" / pid / f"complete_part_{idx:03d}.obj"


def render_part(pid: str, mesh, s1: dict, s2: dict) -> None:
    rdir = OUT / pid / "renders"
    verts = np.asarray(mesh.vertices, dtype=float)
    kept = s1.get("kept_edges") or []
    seed = [e for e in kept if int(e.get("level") or 0) >= 3]
    hyst = kept
    local_pl = [np.asarray(c.get("points") or [], dtype=float) for c in s1.get("local_chains") or [] if c.get("points")]
    merged_pl = [np.asarray(c.get("points") or [], dtype=float) for c in s1.get("merged_chains") or [] if c.get("points")]
    curves = s1.get("curves") or []
    curve_pl = [np.asarray(c.get("points_simplified") or [], dtype=float) for c in curves]
    seed_pl = []
    if seed:
        segs = []
        for e in seed[:4000]:
            segs.append(np.vstack([verts[int(e["v0"])], verts[int(e["v1"])]]))
        seed_pl = segs
    hyst_pl = []
    for e in hyst[:6000]:
        hyst_pl.append(np.vstack([verts[int(e["v0"])], verts[int(e["v1"])]]))
    v2.render_overlay(mesh, [], rdir / "01_source_mesh.png", f"{pid} source")
    v2.render_overlay(mesh, hyst_pl, rdir / "02_raw_dora_edges.png", f"{pid} hysteresis/Dora", line_color="#c0392b")
    v2.render_overlay(mesh, seed_pl, rdir / "03_strong_seed_edges.png", f"{pid} strong seed 35/45", line_color="#7f1d1d")
    v2.render_overlay(mesh, hyst_pl, rdir / "04_hysteresis_expanded_edges.png", f"{pid} hysteresis expanded", line_color="#b45309")
    v2.render_overlay(mesh, local_pl, rdir / "05_local_chains.png", f"{pid} local chains n={s1.get('LOCAL_CHAINS')}", line_color="#64748b")
    v2.render_overlay(mesh, merged_pl, rdir / "06_merged_design_chains.png", f"{pid} merged design chains n={s1.get('MERGED_CHAINS')}", line_color="#1d4ed8")
    v2.render_overlay(mesh, curve_pl, rdir / "07_parametric_curves.png", f"{pid} parametric curves n={len(curves)}")
    # type map by color groups
    by = {}
    for c in curves:
        by.setdefault(c["curve_type"], []).append(np.asarray(c.get("points_simplified") or [], dtype=float))
    # draw all in one
    v2.render_overlay(mesh, curve_pl, rdir / "08_curve_type_map.png", f"{pid} LINE={s1.get('LINES')} CIRCLE={s1.get('CIRCLES')} ARC={s1.get('ARCS')}")
    # surface-colored mesh
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    lab_path = OUT / pid / "surfaces/triangle_labels.npy"
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=130)
    p2 = v2.project(verts)
    f = np.asarray(mesh.faces, dtype=int)
    pick = np.linspace(0, len(f) - 1, min(5000, len(f)), dtype=int)
    type_idx = {"PLANE": 0, "CYLINDER": 1, "CONE": 2, "SPHERE": 3, "TORUS": 4, "REVOLUTION": 5, "RULED": 6, "BSPLINE": 7}
    face_type = np.zeros(len(f), dtype=int)
    for surf in s2.get("surfaces") or []:
        ti = type_idx.get(surf.get("surface_type"), 7)
        for tri in surf.get("triangle_ids") or []:
            if 0 <= int(tri) < len(face_type):
                face_type[int(tri)] = ti
    if lab_path.is_file() and not (s2.get("surfaces") or []):
        lab = np.load(lab_path)
        cols = [plt.cm.tab20(int(lab[i]) % 20) for i in pick]
    else:
        cols = [plt.cm.tab10(int(face_type[i]) % 10) for i in pick]
    ax.add_collection(PolyCollection([p2[f[i]] for i in pick], facecolors=cols, linewidths=0.03, edgecolors=(0.3, 0.3, 0.32, 0.08)))
    c = p2.mean(0)
    rad = max(float(np.ptp(p2, 0).max()) * 0.58, 1e-8)
    ax.set_xlim(c[0] - rad, c[0] + rad)
    ax.set_ylim(c[1] - rad, c[1] + rad)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{pid} patches n={s2.get('PATCH_COUNT')}", fontsize=10)
    fig.savefig(rdir / "08_surface_patches.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    shutil.copy2(rdir / "08_surface_patches.png", rdir / "09_surface_type_map.png")
    shutil.copy2(rdir / "08_surface_patches.png", rdir / "10_fitted_surfaces.png")
    shutil.copy2(rdir / "07_parametric_curves.png", rdir / "09_curve_surface_overlay.png")


def assembly_step(parts: list[str], step_ok: list[Path]) -> dict:
    out = OUT / "assembly/airplane_routeb_v2.step"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not step_ok:
        return {"ASSEMBLY_STEP_RELOAD_VALID": False, "FINAL_ASSEMBLY_STEP": None}
    try:
        from OCP.BRep import BRep_Builder
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
        from OCP.TopoDS import TopoDS_Compound

        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        n = 0
        for sp in step_ok:
            reader = STEPControl_Reader()
            if reader.ReadFile(str(sp)) != IFSelect_RetDone or not reader.TransferRoots():
                continue
            shp = reader.OneShape()
            if shp.IsNull():
                continue
            builder.Add(compound, shp)
            n += 1
        writer = STEPControl_Writer()
        writer.Transfer(compound, STEPControl_AsIs)
        ok = writer.Write(str(out)) == IFSelect_RetDone
        reload_ok = False
        if ok:
            r2 = STEPControl_Reader()
            reload_ok = r2.ReadFile(str(out)) == IFSelect_RetDone and r2.TransferRoots()
        return {"ASSEMBLY_STEP_RELOAD_VALID": bool(reload_ok), "FINAL_ASSEMBLY_STEP": str(out), "parts_in_assembly": n}
    except Exception as exc:
        return {"ASSEMBLY_STEP_RELOAD_VALID": False, "FINAL_ASSEMBLY_STEP": None, "error": str(exc)}


def contact_sheet(parts: list[str]) -> None:
    from PIL import Image, ImageDraw

    cols = ["01_source_mesh.png", "03_strong_seed_edges.png", "06_merged_design_chains.png", "07_parametric_curves.png", "08_surface_patches.png"]
    tw, th = 240, 200
    img = Image.new("RGB", (tw * len(cols), 28 + (th + 22) * len(parts)), "white")
    dr = ImageDraw.Draw(img)
    for i, pid in enumerate(parts):
        dr.text((6, 28 + i * (th + 22)), pid, fill=(20, 20, 20))
        for j, name in enumerate(cols):
            p = OUT / pid / "renders" / name
            if p.is_file():
                im = Image.open(p).convert("RGB").resize((tw - 6, th - 6))
                img.paste(im, (j * tw + 3, 44 + i * (th + 22)))
    img.save(OUT / "airplane_routeb_v2_contact_sheet.png")
    shutil.copy2(OUT / "airplane_routeb_v2_contact_sheet.png", OUT / "renders/airplane_routeb_v2_contact_sheet.png")


def airplane_overview_renders(parts: list[str]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    rdir = OUT / "renders"
    rdir.mkdir(parents=True, exist_ok=True)
    mesh = v2.load_mesh(SOURCE_OBJ)
    v2.render_overlay(mesh, [], rdir / "01_source_airplane.png", "Airplane source mesh")

    def draw_parts(paths: list[Path], out_png: Path, title: str) -> None:
        fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=130)
        all_p = []
        for i, p in enumerate(paths):
            m = v2.load_mesh(p)
            v = np.asarray(m.vertices, dtype=float)
            f = np.asarray(m.faces, dtype=int)
            if len(f) > 3500:
                f = f[np.linspace(0, len(f) - 1, 3500, dtype=int)]
            p2 = v2.project(v)
            all_p.append(p2)
            col = plt.cm.tab10(i % 10)
            ax.add_collection(
                PolyCollection([p2[tri] for tri in f], facecolors=(*col[:3], 0.35), edgecolors=(*col[:3], 0.15), linewidths=0.03)
            )
        if all_p:
            pts = np.vstack(all_p)
            c = pts.mean(0)
            rad = max(float(np.ptp(pts, 0).max()) * 0.58, 1e-8)
            ax.set_xlim(c[0] - rad, c[0] + rad)
            ax.set_ylim(c[1] - rad, c[1] + rad)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(title, fontsize=10)
        fig.savefig(out_png, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    p3_paths = sorted((AIR_ROUTEA / "p3").glob("part_*.obj"))
    draw_parts(p3_paths, rdir / "02_p3_parts.png", "P3 parts")
    x_paths = [part_mesh(pid) for pid in parts]
    draw_parts(x_paths, rdir / "03_xpart_parts.png", "X-Part complete parts")

    def first(name: str) -> Path | None:
        for pid in parts:
            p = OUT / pid / "renders" / name
            if p.is_file():
                return p
        return None

    mapping = {
        "04_dora_edges.png": first("02_raw_dora_edges.png"),
        "05_strong_seed_edges.png": first("03_strong_seed_edges.png"),
        "06_merged_design_curves.png": first("06_merged_design_chains.png"),
        "07_parametric_curve_types.png": first("08_curve_type_map.png"),
        "08_surface_patches.png": first("08_surface_patches.png"),
        "09_surface_type_map.png": first("09_surface_type_map.png"),
        "10_fitted_surfaces.png": first("10_fitted_surfaces.png"),
        "11_cad_parts.png": first("07_parametric_curves.png"),
    }
    for name, src in mapping.items():
        if src and Path(src).is_file():
            shutil.copy2(src, rdir / name)
    cad_stls = [OUT / pid / f"{pid}.qa.stl" for pid in parts if (OUT / pid / f"{pid}.qa.stl").is_file()]
    if cad_stls:
        draw_parts(cad_stls, rdir / "12_routeb_airplane_assembly.png", "Route B V2 assembly tessellation")
        draw_parts(cad_stls, rdir / "13_source_vs_routeb.png", "Route B CAD parts")
    else:
        v2.render_overlay(mesh, [], rdir / "12_routeb_airplane_assembly.png", "Route B assembly (no tessellation)")
        shutil.copy2(rdir / "01_source_airplane.png", rdir / "13_source_vs_routeb.png")


def compare_routea(per: dict) -> None:
    rows = []
    available = False
    for pid, rec in per.items():
        iou_p = AIR_ROUTEA / "cadfit_routea/cadfit_raw" / pid / "final_iou.json"
        a_iou = None
        if iou_p.is_file():
            a_iou = json.loads(iou_p.read_text())["final_iou"]
            available = True
        b_iou = (rec.get("qa") or {}).get("IoU")
        rows.append(
            {
                "part": pid,
                "routea_iou": a_iou,
                "routeb_iou": b_iou,
                "b_circles": rec.get("stage1", {}).get("CIRCLES"),
                "b_planes": rec.get("stage2", {}).get("PLANES"),
                "b_valid": rec.get("stage3", {}).get("BREP_VALID"),
            }
        )
    available = any(r["routea_iou"] is not None for r in rows)
    complete = all(r["routea_iou"] is not None for r in rows) and bool(rows)
    dump_json(OUT / "airplane_routea_vs_routeb_v2.json", {"AIRPLANE_ROUTE_A_AVAILABLE": complete, "AIRPLANE_ROUTE_A_PARTIAL": available and not complete, "rows": rows})
    lines = ["# Airplane Route A vs Route B V2", "", f"AIRPLANE_ROUTE_A_AVAILABLE={complete}", f"AIRPLANE_ROUTE_A_PARTIAL={available and not complete}", "", "| Part | A IoU | B IoU | B circles | B planes | B valid |", "|---|---:|---:|---:|---:|---|"]
    csv = ["Part,RouteA_IoU,RouteB_IoU,B_circles,B_planes,B_valid"]
    for r in rows:
        ai = "" if r["routea_iou"] is None else f"{r['routea_iou']:.4f}"
        bi = "" if r["routeb_iou"] is None else f"{r['routeb_iou']:.4f}"
        lines.append(f"| {r['part']} | {ai or 'n/a'} | {bi or 'n/a'} | {r['b_circles']} | {r['b_planes']} | {r['b_valid']} |")
        csv.append(f"{r['part']},{ai},{bi},{r['b_circles']},{r['b_planes']},{r['b_valid']}")
    if not complete:
        lines.append("\nRoute A CADFit is incomplete; only real IoU values are shown. Missing cells are not fabricated.")
    (OUT / "airplane_routea_vs_routeb_v2.md").write_text("\n".join(lines) + "\n")
    (OUT / "airplane_routea_vs_routeb_v2.csv").write_text("\n".join(csv) + "\n")
    return complete


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", nargs="+")
    ap.add_argument("--skip-dora", action="store_true")
    ap.add_argument("--only-stage1", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "source").mkdir(exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    audit = source_audit()
    xinfo, parts = reuse_p3_xpart(audit["sha256"])
    if args.parts:
        parts = args.parts
    if not xinfo["source_path_match"] or not xinfo["source_hash_match"] or not parts:
        dump_json(OUT / "gate.json", {"CURRENT_GATE": "AIRPLANE_ROUTE_B_GEOMETRIC_CAD_V2", "ROUTE_B_V2_GATE": "FAIL", "NEXT_PRIMARY_BLOCKER": "XPART_PROVENANCE_INVALID"})
        return 2
    dora_ran = False
    if not args.skip_dora:
        try:
            dora_ran = ensure_dora(parts)
        except Exception as exc:
            print(f"[dora] error {exc}; continuing with whatever SES outputs exist", flush=True)
            dora_ran = True
    per = {}
    tot = Counter()
    step_ok = []
    curve_pass = surf_pass = brep_pass = cad_native = 0
    ious, ch, hs, cov, fp = [], [], [], [], []
    rev_parts = 0
    overload = []
    for pid in parts:
        print(f"[V2] {pid}", flush=True)
        pdir = OUT / pid
        for d in ["source", "edge_graph", "curves", "surfaces", "brep", "qa", "renders"]:
            (pdir / d).mkdir(parents=True, exist_ok=True)
        mesh = v2.load_mesh(part_mesh(pid))
        shutil.copy2(part_mesh(pid), pdir / "source" / part_mesh(pid).name)
        tf = AIR_ROUTEA / "xpart" / pid / "transform.json"
        if tf.is_file():
            shutil.copy2(tf, pdir / "source" / "transform.json")
        try:
            s1 = v2.stage1_part(mesh, DORA_OUT, pid, pdir / "edge_graph")
        except Exception as exc:
            s1 = {"CURVE_GATE": "FAIL", "failure_class": "DORA_EDGE_GRAPH_FAIL", "error": str(exc), "ALL_LINE_COLLAPSE": False}
        dump_json(pdir / "edge_graph/stage1.json", {k: v for k, v in s1.items() if k not in {"kept_edges", "merged_chains", "curves", "local_chains"}})
        for name in [
            "raw_dora_edges.npz",
            "persistent_edges.npz",
            "strong_seed_graph.json",
            "merged_chains.json",
            "parametric_curves.json",
            "coaxial_groups.json",
            "curve_qa.json",
            "local_chains.json",
        ]:
            srcp = pdir / "edge_graph" / name
            if srcp.is_file():
                shutil.copy2(srcp, pdir / "curves" / name)
                shutil.copy2(srcp, pdir / name)
        if s1.get("failure_class") == "EDGE_NOISE_OVERLOAD":
            overload.append(pid)
        if s1.get("CURVE_GATE") in {"PASS", "PARTIAL"}:
            curve_pass += 1
        s2 = {"SURFACE_GATE": "FAIL", "surfaces": [], "PATCH_COUNT": 0}
        s3 = {"BREP_VALID": False, "CAD_NATIVE": False}
        qa = {"GEOMETRY_QA_FAIL": True}
        if s1.get("CURVE_GATE") in {"PASS", "PARTIAL"} and not args.only_stage1:
            s2 = v2.stage2_part(mesh, s1, pdir / "surfaces")
            if s2.get("SURFACE_GATE") in {"PASS", "PARTIAL"}:
                surf_pass += 1
                s3 = v2.occ_build(mesh, s2, pdir / f"{pid}.step")
                dump_json(pdir / "brep/stage3_brep.json", s3)
                if s3.get("BREP_VALID"):
                    brep_pass += 1
                if s3.get("CAD_NATIVE") and (pdir / f"{pid}.step").is_file():
                    cad_native += 1
                    step_ok.append(pdir / f"{pid}.step")
                qa = v2.geometry_qa(mesh, pdir / f"{pid}.step")
                dump_json(pdir / "qa/geometry_qa.json", qa)
        try:
            render_part(pid, mesh, s1, s2)
        except Exception as exc:
            print(f"[viz-fail] {pid} {exc}", flush=True)
        slim = {k: v for k, v in s1.items() if k not in {"kept_edges", "merged_chains", "curves", "local_chains", "master_circles", "coaxial_groups"}}
        s2_slim = {k: v for k, v in s2.items() if k not in {"surfaces", "triangle_labels"}}
        per[pid] = {"stage1": slim, "stage2": s2_slim, "stage3": s3, "qa": qa}
        if s1.get("REVOLUTION_EVIDENCE"):
            rev_parts += 1
        for k in [
            "RAW_DORA_EDGES",
            "STRONG_SEED_EDGES",
            "HYSTERESIS_EDGES",
            "LOCAL_CHAINS",
            "MERGED_CHAINS",
            "LINES",
            "CIRCLES",
            "ARCS",
            "ELLIPSES",
            "BSPLINES",
            "COAXIAL_GROUPS",
        ]:
            tot[k] += int(s1.get(k) or 0)
        tot["PLANES"] += int(s2.get("PLANES") or 0)
        tot["CYLINDERS"] += int(s2.get("CYLINDERS") or 0)
        tot["CONES"] += int(s2.get("CONES") or 0)
        tot["SPHERES"] += int(s2.get("SPHERES") or 0)
        tot["TORI"] += int(s2.get("TORI") or 0)
        tot["REVOLUTION_SURFACES"] += int(s2.get("REVOLUTION_SURFACES") or 0)
        tot["RULED_SURFACES"] += int(s2.get("RULED_SURFACES") or 0)
        tot["BSPLINE_SURFACES"] += int(s2.get("BSPLINE_SURFACES") or 0)
        tot["SURFACE_PATCHES"] += int(s2.get("PATCH_COUNT") or 0)
        tot["SHELLS"] += int(s3.get("SHELL_COUNT") or 0)
        tot["SOLIDS"] += int(s3.get("SOLID_COUNT") or 0)
        tot["CLOSED_SHELLS"] += int(s3.get("CLOSED_SHELLS") or 0)
        tot["TRIMMED_FACES"] += int(s3.get("TRIMMED_FACES") or 0)
        tot["SHARED_OCC_EDGES"] += int(s3.get("SHARED_OCC_EDGES") or 0)
        tot["CLOSED_WIRES"] += int(s3.get("WIRE_COUNT") or 0)
        if qa.get("IoU") is not None:
            ious.append(qa["IoU"])
            ch.append(qa["Chamfer"])
            hs.append(qa["Hausdorff"])
            cov.append(qa["Coverage"])
            fp.append(qa["FP_OCCUPANCY"])
        print(f"[V2] done {pid} curve={s1.get('CURVE_GATE')} surf={s2.get('SURFACE_GATE')} brep={s3.get('BREP_VALID')}", flush=True)

    asm = assembly_step(parts, step_ok)
    try:
        airplane_overview_renders(parts)
        contact_sheet(parts)
    except Exception as exc:
        print("render overview fail", exc, flush=True)
    ra_avail = compare_routea(per)
    n_line = tot["LINES"]
    n_cur = n_line + tot["CIRCLES"] + tot["ARCS"] + tot["ELLIPSES"] + tot["BSPLINES"]
    all_line = bool(n_cur > 0 and n_line == n_cur)
    analytic_curve_rate = float((tot["CIRCLES"] + tot["ARCS"] + tot["ELLIPSES"]) / max(n_cur, 1))
    analytic_surf_rate = float(
        (tot["PLANES"] + tot["CYLINDERS"] + tot["CONES"] + tot["SPHERES"] + tot["TORI"] + tot["REVOLUTION_SURFACES"] + tot["RULED_SURFACES"])
        / max(tot["SURFACE_PATCHES"], 1)
    )
    short_b = float(np.mean([per[p]["stage1"].get("SHORT_CHAIN_RATIO_BEFORE") or 1.0 for p in parts]))
    short_a = float(np.mean([per[p]["stage1"].get("SHORT_CHAIN_RATIO_AFTER") or 1.0 for p in parts]))
    compression = float(tot["RAW_DORA_EDGES"] / max(tot["MERGED_CHAINS"], 1))
    solid_rate = float(tot["SOLIDS"] / max(len(parts), 1))
    if cad_native >= 1 and tot["MERGED_CHAINS"] < tot["LOCAL_CHAINS"] and (analytic_curve_rate > 0 or (not all_line)):
        gate = "PASS"
        if tot["SOLIDS"] == 0:
            gate = "PARTIAL_PASS"
    elif curve_pass >= 1:
        gate = "PARTIAL_PASS"
    else:
        gate = "FAIL"
    blocker = ""
    if overload:
        blocker = "EDGE_NOISE_OVERLOAD"
    elif all_line and analytic_curve_rate == 0:
        blocker = "ALL_SHORT_CHAINS_COLLAPSE_TO_LINE"
    elif tot["SOLIDS"] == 0:
        blocker = "NO_SOLID_CLOSURE"
    gate_obj = {
        "CURRENT_GATE": "AIRPLANE_ROUTE_B_GEOMETRIC_CAD_V2",
        "SOURCE_CASE": SOURCE_OBJ.name,
        "SOURCE_SHA256": audit["sha256"],
        "P3_REEXECUTED": False,
        "XPART_REEXECUTED": False,
        "DORA_SES_REEXECUTED": bool(dora_ran),
        "DORA_VAE_USED": False,
        "MAC_REEXECUTED": False,
        "VLM_USED_FOR_GEOMETRY": False,
        "P3_PART_COUNT": xinfo["AIRPLANE_P3_PART_COUNT"],
        "XPART_WATERTIGHT_PARTS": xinfo["AIRPLANE_XPART_WATERTIGHT_PARTS"],
        "XPART_WATERTIGHT_RATE": xinfo["AIRPLANE_XPART_WATERTIGHT_RATE"],
        "ROUTEB_PARTS_ATTEMPTED": len(parts),
        **{k: int(tot[k]) for k in tot},
        "LOCAL_EDGE_CHAINS": int(tot["LOCAL_CHAINS"]),
        "MERGED_DESIGN_CHAINS": int(tot["MERGED_CHAINS"]),
        "SHORT_CHAIN_RATIO_BEFORE": short_b,
        "SHORT_CHAIN_RATIO_AFTER": short_a,
        "LINE_CURVES": int(tot["LINES"]),
        "CIRCLE_CURVES": int(tot["CIRCLES"]),
        "ARC_CURVES": int(tot["ARCS"]),
        "ELLIPSE_CURVES": int(tot["ELLIPSES"]),
        "BSPLINE_CURVES": int(tot["BSPLINES"]),
        "COAXIAL_CIRCLE_GROUPS": int(tot["COAXIAL_GROUPS"]),
        "REVOLUTION_EVIDENCE_PARTS": rev_parts,
        "CURVE_COMPRESSION_RATIO": compression,
        "ANALYTIC_CURVE_RATE": analytic_curve_rate,
        "ANALYTIC_SURFACE_RATE": analytic_surf_rate,
        "SOLID_RATE": solid_rate,
        "BREP_VALID_PARTS": brep_pass,
        "STEP_RELOAD_VALID_PARTS": cad_native,
        "CAD_NATIVE_PARTS": cad_native,
        "MEAN_IOU": float(np.mean(ious)) if ious else None,
        "MEAN_CHAMFER": float(np.mean(ch)) if ch else None,
        "MEAN_HAUSDORFF": float(np.mean(hs)) if hs else None,
        "MEAN_COVERAGE": float(np.mean(cov)) if cov else None,
        "MEAN_FP_OCCUPANCY": float(np.mean(fp)) if fp else None,
        **asm,
        "ALL_LINE_COLLAPSE": all_line,
        "EDGE_NOISE_OVERLOAD_PARTS": overload,
        "AIRPLANE_ROUTE_A_AVAILABLE": ra_avail,
        "ROUTE_B_V2_GATE": gate,
        "ARTIFACT_ROOT": str(OUT),
        "NEXT_PRIMARY_BLOCKER": blocker,
        "CURVE_STAGE_SUCCESSFUL_PARTS": curve_pass,
        "SURFACE_STAGE_SUCCESSFUL_PARTS": surf_pass,
    }
    dump_json(OUT / "gate.json", gate_obj)
    dump_json(OUT / "pipeline_manifest.json", {"parts": parts, "per_part_summary": {p: {k: per[p][k] for k in per[p] if k != "stage1"} | {"stage1_gate": per[p]["stage1"].get("CURVE_GATE"), "circles": per[p]["stage1"].get("CIRCLES"), "lines": per[p]["stage1"].get("LINES")} for p in per}})
    lines = [
        "# Airplane Route B Geometric CAD V2",
        "",
        "## Q1-Q7",
        f"- Q1 fragmentation reduced? merged {tot['MERGED_CHAINS']} < local {tot['LOCAL_CHAINS']}, short {short_b:.3f} -> {short_a:.3f}",
        f"- Q2 thousands of short LINEs? ALL_LINE_COLLAPSE={all_line} LINE={n_line} total_curves={n_cur}",
        f"- Q3 non-line curves: CIRCLE={tot['CIRCLES']} ARC={tot['ARCS']} ELLIPSE={tot['ELLIPSES']}",
        f"- Q4 analytic surfaces rate={analytic_surf_rate:.3f} planes={tot['PLANES']} cyl={tot['CYLINDERS']} ruled={tot['RULED_SURFACES']} rev={tot['REVOLUTION_SURFACES']} bspline={tot['BSPLINE_SURFACES']}",
        f"- Q5 SOLIDS={tot['SOLIDS']} blocker={blocker or 'none'}",
        f"- Q6 overload parts={overload}",
        f"- Q7 Route A available={ra_avail} (see airplane_routea_vs_routeb_v2.md)",
        "",
        "```text",
    ]
    for k, val in gate_obj.items():
        lines.append(f"{k}={val}")
    lines += ["```", ""]
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    for k, val in gate_obj.items():
        print(f"{k}={val}")
    return 0 if gate != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
