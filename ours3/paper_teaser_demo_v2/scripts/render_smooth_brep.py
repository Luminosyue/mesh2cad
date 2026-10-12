#!/usr/bin/env python3
"""Paper renders: smooth shaded BRep, topological edges only."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from numba import njit
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from OCP.TopTools import TopTools_IndexedMapOfShape
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
FROZEN = ROOT / "airplane3_fullseq_14bit_ir_v1/frozen_success_v1/step"
CANON = ROOT / "airplane3_fullseq_14bit_ir_v1/dataset/DeepCAD/geometry_pack_v1"
MESH_DIR = ROOT / "airplane_p3_xpart_cadfit_routea_v1/p3"
OUT = ROOT / "paper_teaser_demo_v2"
PARTS = ["PART_000", "PART_001", "PART_005"]

W = H = 1600
AZIM = -45.0
ELEV = 25.0
FILL = 0.86
BG = np.array([1.0, 1.0, 1.0], dtype=np.float64)
LIGHT = np.array([0.35, -0.20, 0.92], dtype=np.float64)
LIGHT /= np.linalg.norm(LIGHT)
GENERATED_COLOR = np.array([0.086, 0.506, 0.553], dtype=np.float64)
CANONICAL_COLOR = np.array([0.545, 0.627, 0.667], dtype=np.float64)
MESH_COLOR = np.array([0.620, 0.675, 0.710], dtype=np.float64)
EDGE_COLOR = np.array([0.090, 0.130, 0.160], dtype=np.float64)
MESH_EDGE_COLOR = np.array([0.160, 0.210, 0.250], dtype=np.float64)


def camera_basis():
    az, el = np.deg2rad(AZIM), np.deg2rad(ELEV)
    view = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)], dtype=np.float64)
    right = np.cross(np.array([0.0, 0.0, 1.0]), view)
    right /= np.linalg.norm(right)
    up = np.cross(view, right)
    up /= np.linalg.norm(up)
    return view, right, up


VIEW, RIGHT, UP = camera_basis()


def read_step(path: Path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path}")
    reader.TransferRoots()
    return reader.OneShape()


def mesh_shape(shape, linear: float, angular: float = 0.12):
    BRepTools.Clean_s(shape)
    BRepMesh_IncrementalMesh(shape, linear, False, angular, True)
    vertices = []
    faces = []
    offset = 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face, loc)
        exp.Next()
        if poly is None:
            continue
        trsf = loc.Transformation()
        nodes = [
            poly.Node(i).Transformed(trsf)
            for i in range(1, poly.NbNodes() + 1)
        ]
        reverse = face.Orientation() == TopAbs_REVERSED
        for node in nodes:
            vertices.append((node.X(), node.Y(), node.Z()))
        for i in range(1, poly.NbTriangles() + 1):
            tri = poly.Triangle(i)
            a, b, c = tri.Value(1) - 1, tri.Value(2) - 1, tri.Value(3) - 1
            if reverse:
                b, c = c, b
            faces.append((a + offset, b + offset, c + offset))
        offset += len(nodes)
    return np.asarray(vertices, dtype=np.float64), np.asarray(faces, dtype=np.int64)


def brep_polylines(shape, deflection: float):
    indexed = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, indexed)
    lines = []
    for i in range(1, indexed.Extent() + 1):
        edge = TopoDS.Edge_s(indexed.FindKey(i))
        curve = BRepAdaptor_Curve(edge)
        sampled = GCPnts_QuasiUniformDeflection(curve, deflection)
        if not sampled.IsDone() or sampled.NbPoints() < 2:
            continue
        pts = []
        for k in range(1, sampled.NbPoints() + 1):
            p = sampled.Value(k)
            pts.append((p.X(), p.Y(), p.Z()))
        arr = np.asarray(pts, dtype=np.float64)
        if np.linalg.norm(arr[-1] - arr[0]) < 1e-9 and len(arr) < 3:
            continue
        lines.append(arr)
    return lines


def frame_of(*clouds):
    stacked = np.vstack(clouds)
    lo, hi = stacked.min(axis=0), stacked.max(axis=0)
    center = (lo + hi) / 2.0
    span = max(float(np.max(hi - lo)), 1e-9)
    return center, span


def projected_half(vertices, center, span):
    p = (vertices - center) / span
    x = p @ RIGHT
    y = p @ UP
    return max(float(np.max(np.abs(np.concatenate([x, y])))), 1e-6) / FILL


def project(vertices, center, span, half):
    p = (vertices - center) / span
    x = p @ RIGHT
    y = p @ UP
    z = p @ VIEW
    sx = (x + half) / (2.0 * half) * (W - 1)
    sy = (half - y) / (2.0 * half) * (H - 1)
    return sx.astype(np.float64), sy.astype(np.float64), z.astype(np.float64)


def smooth_corner_normals(vertices, faces, feature_deg=32.0):
    a = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    b = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    fn = np.cross(a, b)
    norm = np.linalg.norm(fn, axis=1, keepdims=True)
    fn = fn / np.clip(norm, 1e-12, None)
    incident = [[] for _ in range(len(vertices))]
    for fi, tri in enumerate(faces):
        for vi in tri:
            incident[int(vi)].append(fi)
    cos_thr = np.cos(np.deg2rad(feature_deg))
    corners = np.zeros((len(faces), 3, 3), dtype=np.float64)
    for fi, tri in enumerate(faces):
        base = fn[fi]
        for k, vi in enumerate(tri):
            acc = base.copy()
            for fj in incident[int(vi)]:
                if fj == fi:
                    continue
                if float(np.dot(fn[fj], base)) >= cos_thr:
                    acc += fn[fj]
            length = np.linalg.norm(acc)
            corners[fi, k] = acc / length if length > 1e-12 else base
    return corners


@njit(cache=True)
def _shade(nx, ny, nz, light, view, base):
    ndv = nx * view[0] + ny * view[1] + nz * view[2]
    if ndv < 0.0:
        nx, ny, nz = -nx, -ny, -nz
    ndl = nx * light[0] + ny * light[1] + nz * light[2]
    if ndl < 0.0:
        ndl = 0.0
    hx = light[0] + view[0]
    hy = light[1] + view[1]
    hz = light[2] + view[2]
    hl = (hx * hx + hy * hy + hz * hz) ** 0.5
    hx /= hl
    hy /= hl
    hz /= hl
    ndh = nx * hx + ny * hy + nz * hz
    if ndh < 0.0:
        ndh = 0.0
    spec = ndh * ndh
    spec = spec * spec
    spec = spec * spec
    spec = spec * spec
    inten = 0.40 + 0.58 * ndl + 0.16 * spec
    return base[0] * inten, base[1] * inten, base[2] * inten


@njit(cache=True)
def raster_triangles(sx, sy, zz, corners, faces, base, light, view, img, zbuf, alpha, z_bias):
    height, width = zbuf.shape
    for fi in range(faces.shape[0]):
        i0 = faces[fi, 0]
        i1 = faces[fi, 1]
        i2 = faces[fi, 2]
        x0 = sx[i0]
        y0 = sy[i0]
        x1 = sx[i1]
        y1 = sy[i1]
        x2 = sx[i2]
        y2 = sy[i2]
        minx = int(np.floor(min(x0, x1, x2)))
        maxx = int(np.ceil(max(x0, x1, x2)))
        miny = int(np.floor(min(y0, y1, y2)))
        maxy = int(np.ceil(max(y0, y1, y2)))
        if maxx < 0 or maxy < 0 or minx >= width or miny >= height:
            continue
        if minx < 0:
            minx = 0
        if miny < 0:
            miny = 0
        if maxx >= width:
            maxx = width - 1
        if maxy >= height:
            maxy = height - 1
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-8:
            continue
        z0 = zz[i0] + z_bias
        z1 = zz[i1] + z_bias
        z2 = zz[i2] + z_bias
        n0 = corners[fi, 0]
        n1 = corners[fi, 1]
        n2 = corners[fi, 2]
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                w0 = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
                if w0 < 0.0:
                    continue
                w1 = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / den
                if w1 < 0.0:
                    continue
                w2 = 1.0 - w0 - w1
                if w2 < 0.0:
                    continue
                z = w0 * z0 + w1 * z1 + w2 * z2
                if z <= zbuf[y, x]:
                    continue
                nx = w0 * n0[0] + w1 * n1[0] + w2 * n2[0]
                ny = w0 * n0[1] + w1 * n1[1] + w2 * n2[1]
                nz = w0 * n0[2] + w1 * n1[2] + w2 * n2[2]
                ln = (nx * nx + ny * ny + nz * nz) ** 0.5
                if ln < 1e-10:
                    continue
                nx /= ln
                ny /= ln
                nz /= ln
                r, g, b = _shade(nx, ny, nz, light, view, base)
                zbuf[y, x] = z
                if alpha >= 0.999:
                    img[y, x, 0] = r
                    img[y, x, 1] = g
                    img[y, x, 2] = b
                else:
                    img[y, x, 0] = img[y, x, 0] * (1.0 - alpha) + r * alpha
                    img[y, x, 1] = img[y, x, 1] * (1.0 - alpha) + g * alpha
                    img[y, x, 2] = img[y, x, 2] * (1.0 - alpha) + b * alpha


@njit(cache=True)
def draw_segments(x0, y0, z0, x1, y1, z1, img, zbuf, color, radius, bias, slack):
    height, width = zbuf.shape
    r2 = radius * radius
    for e in range(x0.shape[0]):
        dx = x1[e] - x0[e]
        dy = y1[e] - y0[e]
        length = (dx * dx + dy * dy) ** 0.5
        steps = max(int(length * 2.0), 1)
        for s in range(steps + 1):
            t = s / steps
            x = x0[e] + t * dx
            y = y0[e] + t * dy
            z = z0[e] + t * (z1[e] - z0[e]) + bias
            ix = int(round(x))
            iy = int(round(y))
            for oy in range(-radius, radius + 1):
                for ox in range(-radius, radius + 1):
                    if ox * ox + oy * oy > r2:
                        continue
                    px = ix + ox
                    py = iy + oy
                    if px < 0 or py < 0 or px >= width or py >= height:
                        continue
                    if z + slack >= zbuf[py, px]:
                        img[py, px, 0] = color[0]
                        img[py, px, 1] = color[1]
                        img[py, px, 2] = color[2]


def segments_from_polylines(lines, center, span, half):
    xs0, ys0, zs0, xs1, ys1, zs1 = [], [], [], [], [], []
    for line in lines:
        sx, sy, z = project(line, center, span, half)
        for i in range(len(line) - 1):
            xs0.append(sx[i])
            ys0.append(sy[i])
            zs0.append(z[i])
            xs1.append(sx[i + 1])
            ys1.append(sy[i + 1])
            zs1.append(z[i + 1])
    return (
        np.asarray(xs0, dtype=np.float64),
        np.asarray(ys0, dtype=np.float64),
        np.asarray(zs0, dtype=np.float64),
        np.asarray(xs1, dtype=np.float64),
        np.asarray(ys1, dtype=np.float64),
        np.asarray(zs1, dtype=np.float64),
    )


def segments_from_indexed_edges(sx, sy, z, edges):
    return (
        sx[edges[:, 0]],
        sy[edges[:, 0]],
        z[edges[:, 0]],
        sx[edges[:, 1]],
        sy[edges[:, 1]],
        z[edges[:, 1]],
    )


def save_image(path: Path, img: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = np.clip(img, 0.0, 1.0)
    Image.fromarray((rgb * 255.0 + 0.5).astype(np.uint8), mode="RGB").save(path)


def blank():
    img = np.empty((H, W, 3), dtype=np.float64)
    img[:] = BG
    zbuf = np.full((H, W), -1e30, dtype=np.float64)
    return img, zbuf


def paint_surface(img, zbuf, vertices, faces, corners, color, center, span, half, alpha=1.0, z_bias=0.0):
    sx, sy, z = project(vertices, center, span, half)
    raster_triangles(
        sx, sy, z, corners, faces.astype(np.int64), color, LIGHT, VIEW, img, zbuf, alpha, z_bias
    )
    return sx, sy, z


def paint_edge_segments(img, zbuf, segs, radius, bias, slack):
    if segs[0].size == 0:
        return
    draw_segments(*segs, img, zbuf, EDGE_COLOR if radius > 0 else MESH_EDGE_COLOR, radius, bias, slack)


def mesh_edge_index(faces: np.ndarray) -> np.ndarray:
    pairs = set()
    for tri in faces:
        a, b, c = int(tri[0]), int(tri[1]), int(tri[2])
        for u, v in ((a, b), (b, c), (c, a)):
            if u > v:
                u, v = v, u
            pairs.add((u, v))
    return np.asarray(sorted(pairs), dtype=np.int64)


def load_cad(path: Path):
    shape = read_step(path)
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    x0, y0, z0, x1, y1, z1 = box.Get()
    diag = max(((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5, 1e-9)
    linear = max(diag * 0.00028, 1e-4)
    vertices, faces = mesh_shape(shape, linear, 0.045)
    corners = smooth_corner_normals(vertices, faces, feature_deg=18.0)
    lines = brep_polylines(shape, max(diag * 0.00015, 1e-4))
    return vertices, faces, corners, lines, int(len(faces))


def render_mesh_panel(path: Path, obj_path: Path):
    mesh = trimesh.load(obj_path, force="mesh", process=False)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    corners = smooth_corner_normals(vertices, faces, feature_deg=20.0)
    center, span = frame_of(vertices)
    half = projected_half(vertices, center, span)
    img, zbuf = blank()
    sx, sy, z = paint_surface(img, zbuf, vertices, faces, corners, MESH_COLOR, center, span, half)
    edges = mesh_edge_index(faces)
    segs = segments_from_indexed_edges(sx, sy, z, edges)
    draw_segments(*segs, img, zbuf, MESH_EDGE_COLOR, 0, 0.004, 0.02)
    save_image(path, img)
    return {"triangle_n": int(len(faces)), "drawn_mesh_edges": int(len(edges))}


def render_cad_panel(path: Path, cad, color):
    vertices, faces, corners, lines, tri_n = cad
    center, span = frame_of(vertices)
    half = projected_half(vertices, center, span)
    img, zbuf = blank()
    paint_surface(img, zbuf, vertices, faces, corners, color, center, span, half)
    save_image(path, img)
    return {"shade_triangle_n": tri_n, "brep_polylines": len(lines), "drawn_segments": 0}


def render_overlay(path: Path, generated, canonical):
    gv, gf, gc, gl, gtri = generated
    cv, cf, cc, cl, ctri = canonical
    center, span = frame_of(gv, cv)
    half = projected_half(np.vstack([gv, cv]), center, span)
    img, zbuf = blank()
    paint_surface(img, zbuf, cv, cf, cc, CANONICAL_COLOR, center, span, half, alpha=1.0, z_bias=0.0)
    paint_surface(img, zbuf, gv, gf, gc, GENERATED_COLOR, center, span, half, alpha=0.46, z_bias=0.0015)
    save_image(path, img)
    return {
        "generated_shade_triangles": gtri,
        "canonical_shade_triangles": ctri,
        "generated_brep_polylines": len(gl),
        "canonical_brep_polylines": len(cl),
    }


def compose_teaser():
    labels = {"PART_000": ("Short", "2,810 / 2,810 exact"), "PART_001": ("Medium", "6,596 / 6,596 exact"), "PART_005": ("Long", "12,850 / 12,850 exact")}
    rows = [
        ("Input mesh", "input_mesh"),
        ("Generated CAD", "generated_brep"),
        ("Canonical CAD", "canonical_brep"),
        ("Overlay", "overlay"),
    ]
    fig, axes = plt.subplots(4, 3, figsize=(12.4, 15.2))
    fig.patch.set_facecolor("white")
    for j, part in enumerate(PARTS):
        title, subtitle = labels[part]
        axes[0, j].set_title(f"{title} | {part}\n{subtitle}", fontsize=13, fontweight="bold", color="#14222b", pad=8)
        tag = part.replace("PART_", "part").lower()
        for i, (lab, kind) in enumerate(rows):
            ax = axes[i, j]
            ax.imshow(Image.open(OUT / f"renders/{tag}_{kind}.png"))
            ax.axis("off")
            ax.set_facecolor("white")
            if j == 0:
                ax.text(-0.06, 0.5, lab, rotation=90, va="center", ha="right", transform=ax.transAxes, fontsize=12, fontweight="bold", color="#14222b")
    fig.suptitle("Full-sequence Mesh-to-CAD", fontsize=20, fontweight="bold", color="#14222b")
    fig.text(0.5, 0.012, "Smooth BRep  |  No tessellation edges  |  No chunk  |  No GT prefix  |  Natural EOS  |  IoU = 1.0  |  CD = 0.0", ha="center", fontsize=11, color="#31434d")
    fig.tight_layout(rect=(0.045, 0.03, 0.995, 0.965))
    teaser = OUT / "teaser"
    teaser.mkdir(parents=True, exist_ok=True)
    fig.savefig(teaser / "airplane3_teaser_overview.png", dpi=200, facecolor="white")
    fig.savefig(teaser / "airplane3_teaser_overview.pdf", facecolor="white")
    plt.close(fig)


def main():
    (OUT / "renders").mkdir(parents=True, exist_ok=True)
    stats = {}
    for part in PARTS:
        print("render", part, flush=True)
        low = part.lower()
        obj = MESH_DIR / f"{low}.obj"
        generated = load_cad(FROZEN / f"{part}.step")
        canonical = load_cad(CANON / f"airplane__{part}" / "target.step")
        tag = part.replace("PART_", "part").lower()
        stats[part] = {
            "input_mesh": render_mesh_panel(OUT / f"renders/{tag}_input_mesh.png", obj),
            "generated": render_cad_panel(OUT / f"renders/{tag}_generated_brep.png", generated, GENERATED_COLOR),
            "canonical": render_cad_panel(OUT / f"renders/{tag}_canonical_brep.png", canonical, CANONICAL_COLOR),
            "overlay": render_overlay(OUT / f"renders/{tag}_overlay.png", generated, canonical),
        }
        print(part, stats[part], flush=True)
    (OUT / "reports/render_stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    compose_teaser()
    print("done")


if __name__ == "__main__":
    main()
