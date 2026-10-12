#!/usr/bin/env python3
"""Source vs CAD visual review for the two-mesh fullstack run."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "two_mesh_fullstack_latest"
VIS = OUT / "21_visual_review"
HELPER = ROOT / "case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py"

CASES = [
    {
        "id": "CASE_5IHUMO",
        "source": ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj",
        "best": OUT / "20_xcaf_assembly/CASE_5IHUMO/CASE_5IHUMO_best_available.step",
        "gated": OUT / "20_xcaf_assembly/CASE_5IHUMO/CASE_5IHUMO_fullstack.step",
        "p3": OUT / "01_part_discovery/CASE_5IHUMO/p3/p3_part_segmentation.png",
    },
    {
        "id": "CASE_YC4XCA",
        "source": ROOT / "meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj",
        "best": OUT / "20_xcaf_assembly/CASE_YC4XCA/CASE_YC4XCA_best_available.step",
        "gated": OUT / "20_xcaf_assembly/CASE_YC4XCA/CASE_YC4XCA_fullstack.step",
        "p3": OUT / "01_part_discovery/CASE_YC4XCA/p3/p3_part_segmentation.png",
    },
]


def load_helper():
    spec = importlib.util.spec_from_file_location("case09_end2end_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def font(size=18):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def contact_sheet(paths, titles, out, panel=(720, 560)):
    images = [Image.open(p).convert("RGB") for p in paths]
    pw, ph = panel
    canvas = Image.new("RGB", (pw * len(images), ph + 44), "white")
    draw = ImageDraw.Draw(canvas)
    fnt = font(20)
    for i, (im, title) in enumerate(zip(images, titles)):
        thumb = im.copy()
        thumb.thumbnail((pw - 24, ph - 36))
        x = i * pw + (pw - thumb.size[0]) // 2
        y = 40 + (ph - 36 - thumb.size[1]) // 2
        canvas.paste(thumb, (x, y))
        draw.text((i * pw + 16, 10), title, fill=(20, 30, 45), font=fnt)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(180, 180))


def render_step(V, step, source, bounds, dest_prefix, label):
    ok, roots, shape = V.read_step(step)
    if not (ok and roots and shape is not None and not shape.IsNull()):
        raise RuntimeError(f"cannot read {step}")
    diag = float(np.linalg.norm(source.extents))
    verts, faces, _ = V.tessellate(shape, deflection=0.004, angle=0.2)
    cad = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    edges, _ = V.true_edges(shape, diag)
    shaded = Path(f"{dest_prefix}_shaded.png")
    true_edges = Path(f"{dest_prefix}_true_edges.png")
    V.render([cad], bounds, shaded, colors=[(113, 174, 205)])
    V.render([cad], bounds, true_edges, colors=[(154, 195, 215)], edges=edges)
    return {
        "label": label,
        "shaded": str(shaded),
        "true_edges": str(true_edges),
        "step_roots": int(roots),
        "cad_triangles": int(len(cad.faces)),
        "true_edge_count": int(len(edges)),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--case", help="Only render this case id (e.g. CASE_5IHUMO)")
    args = parser.parse_args()

    V = load_helper()
    VIS.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "TWO_MESH_VISUAL_REVIEW", "cases": []}
    vs_paths, vs_titles, shaded_paths, shaded_titles = [], [], [], []

    cases = CASES
    if args.case:
        cases = [c for c in CASES if c["id"] == args.case]
        if not cases:
            raise SystemExit(f"unknown case: {args.case}")

    for case in cases:
        cid = case["id"]
        dest = VIS / cid
        dest.mkdir(parents=True, exist_ok=True)
        print(cid, "load source", flush=True)
        source = trimesh.load(str(case["source"]), force="mesh", process=False)
        bounds = np.asarray(source.bounds).T
        source_png = dest / f"{cid}_source_shaded.png"
        V.render([source], bounds, source_png, colors=[(205, 207, 210)])

        print(cid, "render best-available CAD", flush=True)
        best_step = case["best"] if case["best"].is_file() else case["gated"]
        best = render_step(V, best_step, source, bounds, dest / f"{cid}_best_available", "best_available")
        print(cid, "render gated CAD", flush=True)
        gated = render_step(V, case["gated"], source, bounds, dest / f"{cid}_hard_gate", "hard_gate")

        summary_path = OUT / "artifacts" / cid / "summary.json"
        summary = {}
        if summary_path.is_file():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        hard_n = summary.get("PARTS_HARD_GATE_PASS")
        best_n = summary.get("PARTS_BEST_AVAILABLE")
        part_n = summary.get("PART_COUNT")
        hard_label = f"{cid} hard-gate ({hard_n}/{part_n})" if hard_n is not None else f"{cid} hard-gate"
        best_label = f"{cid} best-available ({best_n}/{part_n})" if best_n is not None else f"{cid} best-available"
        pipeline = summary.get("PIPELINE", "TWO_MESH_FULLSTACK")
        if summary.get("MAINLINE_V6_BACKEND"):
            pipeline = f"{pipeline} + V6 backend"

        vs_best = dest / f"{cid}_source_vs_best_available.png"
        vs_gated = dest / f"{cid}_source_vs_hard_gate.png"
        vs_mainline = dest / f"{cid}_mainline_source_best_hard_gate_shaded.png"
        vs_mainline_edges = dest / f"{cid}_mainline_source_best_hard_gate_true_edges.png"
        V.compose([source_png, best["shaded"]], [f"{cid} source OBJ", f"{cid} CAD best-available"], vs_best)
        V.compose([source_png, gated["shaded"]], [f"{cid} source OBJ", f"{cid} CAD hard-gate"], vs_gated)
        V.compose(
            [source_png, best["shaded"], gated["shaded"]],
            [f"{cid} source OBJ", best_label, hard_label],
            vs_mainline,
        )
        V.compose(
            [source_png, best["true_edges"], gated["true_edges"]],
            [f"{cid} source OBJ", f"{best_label} true edges", f"{hard_label} true edges"],
            vs_mainline_edges,
        )

        four = dest / f"{cid}_review_sheet.png"
        contact_sheet(
            [source_png, best["shaded"], best["true_edges"], case["p3"]],
            [f"{cid} source", f"{cid} CAD shaded", f"{cid} true edges", f"{cid} P3"],
            four,
            panel=(640, 500),
        )

        row = {
            "case_id": cid,
            "source_png": str(source_png),
            "best_available": best,
            "hard_gate": gated,
            "source_vs_best_available": str(vs_best),
            "source_vs_hard_gate": str(vs_gated),
            "mainline_source_best_hard_gate_shaded": str(vs_mainline),
            "mainline_source_best_hard_gate_true_edges": str(vs_mainline_edges),
            "pipeline": pipeline,
            "review_sheet": str(four),
            "p3_segmentation": str(case["p3"]),
        }
        manifest["cases"].append(row)
        vs_paths.append(vs_best)
        vs_titles.append(f"{cid} source vs CAD")
        shaded_paths.append(best["shaded"])
        shaded_titles.append(f"{cid} CAD shaded")
        print(cid, "done", best["cad_triangles"], "cad tris", flush=True)

    sheet_vs = VIS / "source_vs_cad_contact_sheet.png"
    sheet_shaded = VIS / "cad_shaded_contact_sheet.png"
    contact_sheet(vs_paths, vs_titles, sheet_vs)
    contact_sheet(shaded_paths, shaded_titles, sheet_shaded)
    manifest["outputs"] = {
        "source_vs_cad_contact_sheet": str(sheet_vs),
        "cad_shaded_contact_sheet": str(sheet_shaded),
    }
    (VIS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["outputs"], indent=2))


if __name__ == "__main__":
    main()
