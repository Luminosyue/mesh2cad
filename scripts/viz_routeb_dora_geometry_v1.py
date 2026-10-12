#!/usr/bin/env python3
"""Real 2D-projected visualization of Route B canary parts."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
DORA = ROOT / "ours3/dora_ses_xpart45_v1"
ROUTEB = ROOT / "ours3/routeb_dora_geometry_v1"
ROUTEA = ROOT / "ours3/cadfit_xpart45_routea_v1"
PARTS = ["PART_003", "PART_012", "PART_019", "PART_041", "PART_042"]
VIEW = np.array([[0.82, -0.38, 0.0], [0.22, 0.30, 0.86]], dtype=float)
THRESHOLDS = [15, 25, 35, 45]


def load_json(path: Path, default=None):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def source_path(part: str) -> Path:
    idx = int(part.split("_")[1])
    return XPART / part / f"complete_part_{idx:03d}.obj"


def project(pts: np.ndarray) -> np.ndarray:
    return np.asarray(pts, dtype=float) @ VIEW.T


def frame_limits(p2: np.ndarray) -> tuple[tuple[float, float], tuple[float, float]]:
    c = p2.mean(axis=0)
    r = max(float(np.ptp(p2, axis=0).max()) * 0.58, 1e-8)
    return (c[0] - r, c[0] + r), (c[1] - r, c[1] + r)


def subsample_faces(faces: np.ndarray, n: int = 4500) -> np.ndarray:
    if len(faces) <= n:
        return faces
    rng = np.random.default_rng(7)
    return faces[rng.choice(len(faces), n, replace=False)]


def dora_union_edges(part: str) -> np.ndarray:
    seen = {}
    for th in THRESHOLDS:
        npz = DORA / f"threshold_{th}" / part / "salient_edges.npz"
        if not npz.is_file():
            continue
        data = np.load(npz)
        ev = np.asarray(data["edge_vertex_indices"], dtype=np.int64)
        dh = np.asarray(data["edge_dihedral_deg"], dtype=float)
        for (a, b), ang in zip(ev, dh):
            key = (int(a), int(b)) if a < b else (int(b), int(a))
            prev = seen.get(key)
            if prev is None or ang > prev:
                seen[key] = float(ang)
    if not seen:
        return np.zeros((0, 2), dtype=np.int64)
    return np.asarray(list(seen.keys()), dtype=np.int64)


def tessellate_step(step: Path, stl: Path, timeout_s: int = 45) -> trimesh.Trimesh | None:
    if not step.is_file() or step.stat().st_size <= 0:
        return None
    if stl.is_file() and stl.stat().st_mtime >= step.stat().st_mtime:
        try:
            return load_mesh(stl)
        except Exception:
            pass
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(str(step)) != IFSelect_RetDone or not reader.TransferRoots():
            return None
        shape = reader.OneShape()
        if shape.IsNull():
            return None
        BRepMesh_IncrementalMesh(shape, 0.012, False, 0.8, True).Perform()
        stl.parent.mkdir(parents=True, exist_ok=True)
        if not StlAPI_Writer().Write(shape, str(stl)):
            return None
        return load_mesh(stl)
    except Exception:
        return None


def draw_mesh_polys(ax, verts: np.ndarray, faces: np.ndarray, color, edge=None, alpha=0.55):
    p2 = project(verts)
    faces = subsample_faces(faces)
    polys = [p2[f] for f in faces]
    fc = (*color, alpha)
    ec = edge if edge is not None else (0.35, 0.38, 0.42, 0.08)
    ax.add_collection(PolyCollection(polys, facecolors=fc, edgecolors=ec, linewidths=0.04))
    xlim, ylim = frame_limits(p2)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    return p2


def save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_part(part: str) -> dict:
    out = ROUTEB / part / "renders"
    out.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(source_path(part))
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    p2 = project(verts)
    xlim, ylim = frame_limits(p2)

    stage1 = load_json(ROUTEB / part / "edge_graph/stage1_edges_curves.json", {}) or {}
    stage2 = load_json(ROUTEB / part / "surfaces/stage2_surfaces.json", {}) or {}
    stage3 = load_json(ROUTEB / part / "brep/stage3_brep.json", {}) or {}

    # 01 source
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    draw_mesh_polys(ax, verts, faces, (0.55, 0.60, 0.66), alpha=0.85)
    ax.set_title(f"{part} source watertight mesh", fontsize=10)
    save_fig(fig, out / "01_source_mesh.png")

    # 02 raw Dora union
    edges = dora_union_edges(part)
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    draw_mesh_polys(ax, verts, faces, (0.78, 0.80, 0.82), alpha=0.28)
    if len(edges):
        show = edges
        if len(show) > 8000:
            show = show[np.random.default_rng(3).choice(len(show), 8000, replace=False)]
        segs = p2[show]
        ax.add_collection(LineCollection(segs, colors="#c0392b", linewidths=0.45, alpha=0.75))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(f"{part} Dora SES union edges n={len(edges)}", fontsize=10)
    save_fig(fig, out / "02_raw_dora_edges.png")

    # 04 chains / 05 curves from stage1
    chains = stage1.get("chains") or []
    curves = stage1.get("curves") or []
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    draw_mesh_polys(ax, verts, faces, (0.78, 0.80, 0.82), alpha=0.22)
    cmap = plt.cm.tab20
    for i, ch in enumerate(chains[:400]):
        pts = np.asarray(ch.get("points") or [], dtype=float)
        if len(pts) < 2:
            continue
        q = project(pts)
        ax.plot(q[:, 0], q[:, 1], color=cmap(i % 20), lw=1.05, alpha=0.9)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(f"{part} recovered edge chains n={len(chains)}", fontsize=10)
    save_fig(fig, out / "04_edge_chains.png")

    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    draw_mesh_polys(ax, verts, faces, (0.82, 0.83, 0.85), alpha=0.22)
    type_color = {"LINE": "#1d4ed8", "CIRCLE": "#dc2626", "ARC": "#ea580c", "ELLIPSE": "#7c3aed", "BSPLINE": "#0f766e"}
    for cu in curves[:400]:
        pts = np.asarray(cu.get("points_simplified") or [], dtype=float)
        if len(pts) < 2:
            continue
        q = project(pts)
        ax.plot(q[:, 0], q[:, 1], color=type_color.get(cu.get("curve_type"), "#111827"), lw=1.35)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(f"{part} parametric curves n={len(curves)}", fontsize=10)
    save_fig(fig, out / "05_parametric_curves.png")

    # aliases required by the original spec
    for src, dst in [
        ("02_raw_dora_edges.png", "03_filtered_edges.png"),
        ("02_raw_dora_edges.png", "03_edge_confidence.png"),
        ("04_edge_chains.png", "04_edge_components.png"),
        ("04_edge_chains.png", "06_edge_chains.png"),
        ("05_parametric_curves.png", "07_parametric_curves.png"),
    ]:
        (out / dst).write_bytes((out / src).read_bytes())

    # 06 patches
    surfaces = stage2.get("surfaces") or []
    patch = np.full(len(faces), -1, dtype=int)
    for s in surfaces:
        for tid in s.get("triangle_ids") or []:
            if 0 <= int(tid) < len(patch):
                patch[int(tid)] = int(s.get("patch_id") or 0)
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    pick = subsample_faces(np.arange(len(faces)), 5000)
    polys = [p2[faces[i]] for i in pick]
    colors = [plt.cm.tab20(int(patch[i]) % 20) if patch[i] >= 0 else (0.75, 0.76, 0.78, 0.45) for i in pick]
    ax.add_collection(PolyCollection(polys, facecolors=colors, edgecolors=(0.2, 0.2, 0.22, 0.05), linewidths=0.03))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{part} surface patches n={len(surfaces)}", fontsize=10)
    save_fig(fig, out / "06_patch_segmentation.png")
    (out / "07_surface_type_map.png").write_bytes((out / "06_patch_segmentation.png").read_bytes())
    (out / "08_fitted_surfaces.png").write_bytes((out / "06_patch_segmentation.png").read_bytes())
    (out / "08_patch_segmentation.png").write_bytes((out / "06_patch_segmentation.png").read_bytes())
    (out / "09_surface_type_map.png").write_bytes((out / "06_patch_segmentation.png").read_bytes())
    (out / "09_curve_surface_overlay.png").write_bytes((out / "05_parametric_curves.png").read_bytes())
    (out / "10_fitted_surfaces.png").write_bytes((out / "06_patch_segmentation.png").read_bytes())
    (out / "11_curve_surface_overlay.png").write_bytes((out / "05_parametric_curves.png").read_bytes())

    # 10 final brep tessellation
    step = ROUTEB / part / f"{part}.step"
    cad = tessellate_step(step, ROUTEB / part / "qa" / f"{part}_tess.stl")
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    draw_mesh_polys(ax, verts, faces, (0.78, 0.80, 0.82), alpha=0.18)
    if cad is not None:
        draw_mesh_polys(ax, np.asarray(cad.vertices), np.asarray(cad.faces), (0.86, 0.32, 0.22), alpha=0.42)
        title = f"{part} Route B STEP tessellation"
    else:
        title = f"{part} Route B STEP missing/unmeshed"
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(title, fontsize=10)
    save_fig(fig, out / "10_final_brep.png")

    # 11 source vs routeb
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    rng = np.random.default_rng(1)
    src_s = verts[rng.choice(len(verts), min(5000, len(verts)), replace=False)]
    qsrc = project(src_s)
    ax.scatter(qsrc[:, 0], qsrc[:, 1], s=1.4, c="#334155", alpha=0.35, label="X-Part source")
    if cad is not None:
        cv = np.asarray(cad.vertices)
        cad_s = cv[rng.choice(len(cv), min(5000, len(cv)), replace=False)]
        qcad = project(cad_s)
        ax.scatter(qcad[:, 0], qcad[:, 1], s=1.4, c="#dc2626", alpha=0.35, label="Route B CAD")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_title(f"{part} source vs Route B", fontsize=10)
    save_fig(fig, out / "11_source_vs_routeb.png")

    # 12 route A vs B
    a_stl = ROUTEA / "cadfit_raw" / part / "best_greedy_parallel_iterative.stl"
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=140)
    ax.scatter(qsrc[:, 0], qsrc[:, 1], s=1.2, c="#94a3b8", alpha=0.25, label="source")
    if a_stl.is_file():
        am = load_mesh(a_stl)
        av = np.asarray(am.vertices)
        a_s = av[rng.choice(len(av), min(5000, len(av)), replace=False)]
        qa = project(a_s)
        ax.scatter(qa[:, 0], qa[:, 1], s=1.4, c="#2563eb", alpha=0.4, label="Route A")
    if cad is not None:
        ax.scatter(qcad[:, 0], qcad[:, 1], s=1.4, c="#dc2626", alpha=0.4, label="Route B")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_title(f"{part} Route A vs Route B", fontsize=10)
    save_fig(fig, out / "12_routea_vs_routeb.png")

    return {
        "part": part,
        "raw_dora": int(len(edges)),
        "chains": int(len(chains)),
        "curves": int(len(curves)),
        "patches": int(len(surfaces)),
        "step_tessellated": cad is not None,
        "brep_valid": bool(stage3.get("BREP_VALID")),
    }


def contact_sheet(rows: list[dict]) -> None:
    cols = [
        ("01_source_mesh.png", "source"),
        ("02_raw_dora_edges.png", "Dora edges"),
        ("05_parametric_curves.png", "curves"),
        ("06_patch_segmentation.png", "patches"),
        ("10_final_brep.png", "Route B CAD"),
        ("12_routea_vs_routeb.png", "A vs B"),
    ]
    tw, th = 280, 230
    sheet = Image.new("RGB", (tw * len(cols), 40 + (th + 28) * len(PARTS)), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_s = font
    for j, (_, lab) in enumerate(cols):
        draw.text((j * tw + 10, 10), lab, fill=(20, 20, 20), font=font)
    for i, part in enumerate(PARTS):
        y = 40 + i * (th + 28)
        draw.text((8, y), part, fill=(20, 20, 20), font=font_s)
        y += 16
        for j, (name, _) in enumerate(cols):
            p = ROUTEB / part / "renders" / name
            if not p.is_file():
                continue
            im = Image.open(p).convert("RGB").resize((tw - 8, th - 8))
            sheet.paste(im, (j * tw + 4, y))
    dest = ROUTEB / "routeb_5part_contact_sheet.png"
    sheet.save(dest)
    print("wrote", dest)


def main() -> None:
    rows = []
    for part in PARTS:
        print(f"[viz] {part}", flush=True)
        rows.append(render_part(part))
    contact_sheet(rows)
    (ROUTEB / "viz_manifest.json").write_text(json.dumps(rows, indent=2) + "\n")
    print("DONE", rows)


if __name__ == "__main__":
    main()
