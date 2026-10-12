#!/usr/bin/env python3
"""Render-only V6 visual review pack. No P3/PhysX/MAC."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from OCP.BRepCheck import BRepCheck_Analyzer

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v6_visual_review"
HELPER = ROOT / "case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py"

CASES = [
    {
        "id": "CASE09",
        "step": ROOT / "case09_fullstack_mesh2cad_mac_v6/10_assembly/CASE09_fullstack_mesh2cad_mac_v6.step",
        "source": ROOT / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj",
        "existing": {
            "shaded": ROOT / "case09_fullstack_mesh2cad_mac_v6/artifacts/v6_final_shaded.png",
            "true_edges": ROOT / "case09_fullstack_mesh2cad_mac_v6/artifacts/v6_final_true_edges.png",
            "source_vs": ROOT / "case09_fullstack_mesh2cad_mac_v6/artifacts/source_vs_v6_final_shaded.png",
        },
    },
    {
        "id": "CASE01",
        "step": ROOT / "batch9_fullstack_mesh2cad_mac_v6/11_assembly/CASE_01/CASE_01_fullstack_mesh2cad_mac_v6.step",
        "source": ROOT / "meshes/Asus_M5A99FX_PRO_R20_Motherboard_ATX_Socket_AM3.obj",
        "existing": {},
    },
    {
        "id": "CASE03",
        "step": ROOT / "batch9_fullstack_mesh2cad_mac_v6/11_assembly/CASE_03/CASE_03_fullstack_mesh2cad_mac_v6.step",
        "source": ROOT / "meshes/B003QTD4Y6.obj",
        "existing": {},
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_helper():
    spec = importlib.util.spec_from_file_location("case09_end2end_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_font(size=18):
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
    font = load_font(20)
    for i, (im, title) in enumerate(zip(images, titles)):
        thumb = im.copy()
        thumb.thumbnail((pw - 24, ph - 36))
        x = i * pw + (pw - thumb.size[0]) // 2
        y = 40 + (ph - 36 - thumb.size[1]) // 2
        canvas.paste(thumb, (x, y))
        draw.text((i * pw + 16, 10), title, fill=(20, 30, 45), font=font)
    canvas.save(out, dpi=(180, 180))


def main():
    V = load_helper()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "V6_VISUAL_REVIEW", "outputs": {}, "inputs": [], "policy": "RENDER_ONLY_NO_P3_PHYSX_MAC"}

    shaded_paths, true_paths, source_vs_paths = [], [], []
    shaded_titles, true_titles, source_titles = [], [], []

    for case in CASES:
        cid = case["id"]
        step = case["step"]
        source_path = case["source"]
        assert step.is_file(), f"missing STEP: {step}"
        assert source_path.is_file(), f"missing source: {source_path}"

        print(f"[{cid}] load source/step", flush=True)
        source = trimesh.load(str(source_path), force="mesh", process=False)
        bounds = np.asarray(source.bounds).T
        diag = float(np.linalg.norm(source.extents))

        ok, roots, shape = V.read_step(step)
        assert ok and roots and shape is not None and not shape.IsNull()
        assert BRepCheck_Analyzer(shape).IsValid(), f"{cid} BRep invalid"

        verts, faces, _ = V.tessellate(shape, deflection=0.004, angle=0.2)
        cad = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
        edges, _ = V.true_edges(shape, diag)

        shaded = OUT / f"{cid}_shaded.png"
        true_edges = OUT / f"{cid}_true_edges.png"
        source_png = OUT / f"{cid}_source_shaded.png"
        source_vs = OUT / f"{cid}_source_vs_cad.png"

        print(f"[{cid}] render shaded/true-edges", flush=True)
        V.render([cad], bounds, shaded, colors=[(113, 174, 205)])
        V.render([cad], bounds, true_edges, colors=[(154, 195, 215)], edges=edges)
        V.render([source], bounds, source_png, colors=[(205, 207, 210)])
        V.compose([source_png, shaded], [f"{cid} source OBJ", f"{cid} V6 CAD shaded"], source_vs)

        shaded_paths.append(shaded)
        true_paths.append(true_edges)
        source_vs_paths.append(source_vs)
        shaded_titles.append(f"{cid} shaded")
        true_titles.append(f"{cid} true edges")
        source_titles.append(f"{cid} source vs CAD")

        manifest["inputs"].append(
            {
                "case_id": cid,
                "final_step": str(step),
                "final_step_sha256": sha256(step),
                "source_obj": str(source_path),
                "source_obj_sha256": sha256(source_path),
                "step_roots": int(roots),
                "cad_triangles": int(len(cad.faces)),
                "true_edge_count": int(len(edges)),
                "existing_artifacts": {k: str(v) for k, v in case.get("existing", {}).items() if Path(v).is_file()},
                "outputs": {
                    "shaded": str(shaded),
                    "true_edges": str(true_edges),
                    "source_vs_cad": str(source_vs),
                },
            }
        )
        print(f"[{cid}] done faces~tris={len(cad.faces)} edges={len(edges)}", flush=True)

    sheet_src = OUT / "source_vs_cad_contact_sheet.png"
    sheet_true = OUT / "true_edges_contact_sheet.png"
    contact_sheet(source_vs_paths, source_titles, sheet_src)
    contact_sheet(true_paths, true_titles, sheet_true)

    # also a shaded contact sheet for convenience
    sheet_shaded = OUT / "shaded_contact_sheet.png"
    contact_sheet(shaded_paths, shaded_titles, sheet_shaded)

    manifest["outputs"] = {
        "CASE09_shaded.png": str(OUT / "CASE09_shaded.png"),
        "CASE09_true_edges.png": str(OUT / "CASE09_true_edges.png"),
        "CASE01_shaded.png": str(OUT / "CASE01_shaded.png"),
        "CASE01_true_edges.png": str(OUT / "CASE01_true_edges.png"),
        "CASE03_shaded.png": str(OUT / "CASE03_shaded.png"),
        "CASE03_true_edges.png": str(OUT / "CASE03_true_edges.png"),
        "source_vs_cad_contact_sheet.png": str(sheet_src),
        "true_edges_contact_sheet.png": str(sheet_true),
        "shaded_contact_sheet.png": str(sheet_shaded),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["outputs"], indent=2))


if __name__ == "__main__":
    main()
