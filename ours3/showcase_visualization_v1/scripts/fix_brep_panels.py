#!/usr/bin/env python3
"""Fix showcase B-rep panels: shaded CAD look, not dense wireframe soup."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

O = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = O / "showcase_visualization_v1"
FONT = ImageFont.load_default()
PAL = [
    (137, 190, 219),
    (244, 181, 123),
    (167, 211, 151),
    (215, 148, 167),
    (188, 170, 218),
    (255, 224, 130),
    (141, 211, 199),
    (190, 186, 218),
    (251, 180, 174),
    (179, 222, 105),
]


def camera():
    a, e = np.radians(38), np.radians(24)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), np.sin(e)], [0, -np.sin(e), np.cos(e)]])
    return rx @ rz


R = camera()


def project(P, bounds, w, h, pad=0.06):
    corners = np.array([[x, y, z] for x in bounds[0] for y in bounds[1] for z in bounds[2]])
    q = corners @ R.T
    lo, hi = q[:, :2].min(0), q[:, :2].max(0)
    mid = (lo + hi) / 2
    span = max(hi - lo) * (1 + 2 * pad)
    p = P @ R.T
    xy = (p[:, :2] - mid) / span
    return np.c_[(xy[:, 0] + 0.5) * w, (0.5 - xy[:, 1]) * h], p[:, 2]


def shaded_color(base, n):
    n = n / max(np.linalg.norm(n), 1e-12)
    L = np.array([0.3, 0.45, 0.84])
    L = L / np.linalg.norm(L)
    v = 0.40 + 0.60 * abs(n @ L)
    return tuple(int(min(255, max(0, c * v))) for c in base)


def sharp_edge_segments(mesh: trimesh.Trimesh, sharp_deg=48.0, max_segs=14000):
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces, int)
    if len(F) == 0:
        return []
    rounded = np.round(V, 6)
    uniq, inv = np.unique(rounded, axis=0, return_inverse=True)
    m = trimesh.Trimesh(vertices=uniq, faces=inv[F], process=False)
    if len(m.face_adjacency) == 0:
        return []
    fn = m.face_normals
    adj = m.face_adjacency
    ae = m.face_adjacency_edges
    dots = np.clip(np.einsum("ij,ij->i", fn[adj[:, 0]], fn[adj[:, 1]]), -1, 1)
    ang = np.degrees(np.arccos(dots))
    view = R[2]
    facing = fn @ view
    sil = (facing[adj[:, 0]] * facing[adj[:, 1]]) < -0.02
    keep = (ang >= sharp_deg) | sil
    segs = uniq[ae[keep]]
    # length filter
    ext = float(np.linalg.norm(m.bounds[1] - m.bounds[0]))
    lens = np.linalg.norm(segs[:, 1] - segs[:, 0], axis=1)
    segs = segs[lens >= max(ext * 0.002, 1e-4)]
    if len(segs) > max_segs:
        w = lens[lens >= max(ext * 0.002, 1e-4)] if False else np.linalg.norm(segs[:, 1] - segs[:, 0], axis=1)
        w = np.maximum(w, 1e-9)
        w = w / w.sum()
        idx = np.random.default_rng(0).choice(len(segs), size=max_segs, replace=False, p=w)
        segs = segs[idx]
    return [segs[i] for i in range(len(segs))]


def render(meshes, bounds, path, colors=None, feature_edges=None, size=(1200, 1050), explode=0.0, edge_width=2):
    w, h = size
    im = Image.new("RGB", size, "white")
    dr = ImageDraw.Draw(im)
    alltris = []
    center = bounds.mean(1)
    diag = np.linalg.norm(bounds[:, 1] - bounds[:, 0])
    offsets = []
    for mi, m in enumerate(meshes):
        V = np.asarray(m.vertices, float).copy()
        F = np.asarray(m.faces, int)
        off = np.zeros(3)
        if explode and len(meshes) > 1:
            d = V.mean(0) - center
            off = d / max(np.linalg.norm(d), 1e-12) * diag * explode
            V += off
        offsets.append(off)
        if len(F) > 120000:
            F = F[np.linspace(0, len(F) - 1, 120000).astype(int)]
        xy, z = project(V, bounds, w, h)
        base = (190, 211, 231) if colors is None else colors[mi % len(colors)]
        for f in F:
            p = V[f]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            alltris.append((float(z[f].mean()), [tuple(x) for x in xy[f]], shaded_color(base, n)))
    alltris.sort(key=lambda x: x[0])
    for _, poly, c in alltris:
        dr.polygon(poly, fill=c)
    # feature edges only (already in same frame as meshes; apply same explode offsets if one mesh)
    if feature_edges:
        # if single mesh + explode list of polylines in world frame
        for e in feature_edges:
            pts = np.asarray(e, float)
            if len(pts) < 2:
                continue
            if explode and len(meshes) == 1:
                # no-op
                pass
            xy, _ = project(pts, bounds, w, h)
            dr.line([tuple(x) for x in xy], fill=(38, 55, 76), width=edge_width)
    im.save(path)
    return len(alltris)


def render_exploded_parts(comps, bounds, path, colors, explode=0.045):
    """Part-colored exploded shaded view; feature edges follow each part."""
    w, h = 1200, 1050
    im = Image.new("RGB", (w, h), "white")
    dr = ImageDraw.Draw(im)
    center = bounds.mean(1)
    diag = np.linalg.norm(bounds[:, 1] - bounds[:, 0])
    alltris = []
    all_edges = []
    for mi, m in enumerate(comps):
        V = np.asarray(m.vertices, float).copy()
        F = np.asarray(m.faces, int)
        if len(V) == 0 or len(F) == 0:
            continue
        d = V.mean(0) - center
        off = d / max(np.linalg.norm(d), 1e-12) * diag * explode
        V2 = V + off
        if len(F) > 50000:
            F = F[np.linspace(0, len(F) - 1, 50000).astype(int)]
        xy, z = project(V2, bounds, w, h)
        base = colors[mi % len(colors)]
        for f in F:
            p = V2[f]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            alltris.append((float(z[f].mean()), [tuple(x) for x in xy[f]], shaded_color(base, n)))
        segs = sharp_edge_segments(trimesh.Trimesh(vertices=V, faces=np.asarray(m.faces, int), process=False), sharp_deg=50, max_segs=4000)
        for s in segs:
            all_edges.append(np.asarray(s) + off)
    alltris.sort(key=lambda x: x[0])
    for _, poly, c in alltris:
        dr.polygon(poly, fill=c)
    for e in all_edges:
        xy, _ = project(e, bounds, w, h)
        dr.line([tuple(x) for x in xy], fill=(38, 55, 76), width=1)
    im.save(path)


def load_summary_specs():
    import csv

    summary = {r["CASE_ID"]: r for r in csv.DictReader(open(O / "batch_real_mesh2cad_v1/artifacts/per_case_summary.csv"))}
    return {
        "case00": {
            "id": "CASE_00",
            "src": Path(summary["CASE_00"]["SOURCE_OBJ_PATH"]),
            "cache": O / "render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_assembly.npz",
            "ccache": O / "render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_components.npz",
        },
        "real03": {
            "id": "REAL_03",
            "src": Path(summary["CASE_00"]["SOURCE_OBJ_PATH"]),
            "cache": O / "render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_assembly.npz",
            "ccache": O / "render_upgrade_v1/real03/cache/dccd0d863bb1f2ee_d0.0075_a0.3_components.npz",
        },
        "case05": {
            "id": "CASE_05",
            "src": Path(summary["CASE_05"]["SOURCE_OBJ_PATH"]),
            "cache": O / "render_upgrade_v1/case05/cache/e626e0a003326391_d0.0075_a0.3_assembly.npz",
            "ccache": O / "render_upgrade_v1/case05/cache/e626e0a003326391_d0.0075_a0.3_components.npz",
        },
    }


def main():
    specs = load_summary_specs()
    only = set(filter(None, os.environ.get("SHOWCASE_ONLY", "case05,case00,real03").split(",")))
    for key, s in specs.items():
        if key not in only:
            continue
        print("FIX", key, flush=True)
        src = trimesh.load(str(s["src"]), force="mesh", process=False)
        bounds = np.asarray(src.bounds).T
        d = np.load(s["cache"])
        cad = trimesh.Trimesh(vertices=d["V"], faces=d["F"], process=False)
        cd = np.load(s["ccache"], allow_pickle=True)
        comps = [trimesh.Trimesh(vertices=cd[f"V_{i}"], faces=cd[f"F_{i}"], process=False) for i in range(int(cd["n"]))]
        feat = sharp_edge_segments(cad, sharp_deg=48.0, max_segs=12000)
        print("  feature_edges", len(feat), "tris", len(cad.faces), "comps", len(comps), flush=True)
        out = OUT / key
        # main shaded B-rep: surfaces dominant, sparse feature edges
        render([cad], bounds, out / "brep_model.png", colors=[(190, 210, 234)], feature_edges=feat, edge_width=2)
        # wireframe panel: feature edges only (no triangle cage)
        render([], bounds, out / "brep_wireframe.png", feature_edges=feat, edge_width=2)
        # part colored
        render(comps, bounds, out / "part_colored_brep.png", colors=PAL, feature_edges=None)
        # exploded: edges follow parts
        render_exploded_parts(comps, bounds, out / "exploded_brep.png", PAL, explode=0.045)
        # refresh comparison boards locally
        from PIL import Image as I

        def compose(images, titles, path, cols):
            ims = [I.open(x).convert("RGB") for x in images]
            pw, ph = 640, 560
            rows = math.ceil(len(ims) / cols)
            canvas = I.new("RGB", (pw * cols, ph * rows + 54), (255, 255, 255))
            dr = ImageDraw.Draw(canvas)
            dr.text((18, 15), "SHOWCASE_VISUALIZATION_V1 (fixed shaded B-rep)", fill=(20, 30, 45), font=FONT)
            for i, (im, t) in enumerate(zip(ims, titles)):
                im = im.copy()
                im.thumbnail((pw - 20, ph - 55))
                x = (i % cols) * pw + 10
                y = (i // cols) * ph + 50
                canvas.paste(im, (x, y))
                dr.text((x + 8, y + im.height + 8), t, fill=(25, 35, 50), font=FONT)
            canvas.save(path)

        meshpng = out / "mesh_model.png"
        splitpng = out / "split_model.png"
        brep = out / "brep_model.png"
        part = out / "part_colored_brep.png"
        if meshpng.is_file() and splitpng.is_file():
            compose([meshpng, splitpng, brep], ["Mesh model", "Part / surface split", "B-rep model"], out / "comparison_figure.png", 3)
            compose(
                [meshpng, splitpng, part, brep],
                ["Mesh model", "P3 / part split", "CAD-part / surface split", "B-rep model"],
                out / "comparison_figure_4panel.png",
                4,
            )
        meta_path = out / "render_metadata.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text())
            meta["EDGE_RENDER_MODE"] = "SHARP_EDGE+SILHOUETTE_FILTERED"
            meta["FEATURE_EDGE_SEGMENTS_RENDERED"] = int(len(feat))
            meta["NOTE"] = "Re-rendered: removed dense all-BRep wireframe overlay that drowned shaded faces."
            meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print("DONE", key, flush=True)
    print("ALL_FIXED", flush=True)


if __name__ == "__main__":
    main()
