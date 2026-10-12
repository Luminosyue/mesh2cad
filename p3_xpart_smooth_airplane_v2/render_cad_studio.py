#!/usr/bin/env python3
"""Studio CAD render: shaded solids + B-rep edges, tight framing."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPEN3D_CPU_RENDERING", "true")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import cadquery as cq
import numpy as np
import open3d as o3d
import plotly.graph_objects as go
from OCP.BRepAdaptor import BRepAdaptor_Surface
from open3d.visualization import rendering
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2")
OUT = ROOT / "visualizations"
TMP = OUT / "_cad_studio_tmp"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)

KEPT = ["PART_000", "PART_002", "PART_003", "PART_005", "PART_008"]
PAL = {
    "PART_000": (0.62, 0.70, 0.80),
    "PART_002": (0.20, 0.48, 0.74),
    "PART_003": (0.18, 0.58, 0.40),
    "PART_005": (0.78, 0.81, 0.85),
    "PART_008": (0.74, 0.28, 0.30),
}
METAL = (0.72, 0.76, 0.80)
BG_RGB = (236, 239, 244)
BG = [BG_RGB[0] / 255, BG_RGB[1] / 255, BG_RGB[2] / 255, 1.0]
W, H = 1600, 1100


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def clone(mesh):
    m = o3d.geometry.TriangleMesh()
    m.vertices = o3d.utility.Vector3dVector(np.asarray(mesh.vertices).copy())
    m.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles).copy())
    m.compute_vertex_normals()
    return m


def aabb(meshes):
    pts = [np.asarray(m.vertices) for m in meshes if len(m.vertices)]
    lo = np.min([p.min(0) for p in pts], axis=0)
    hi = np.max([p.max(0) for p in pts], axis=0)
    return lo, hi


def explode(meshes, factor=0.7):
    cents = np.vstack([np.asarray(m.vertices).mean(0) for m in meshes])
    origin = cents.mean(0)
    out = []
    for mesh, c in zip(meshes, cents):
        mm = clone(mesh)
        mm.translate((c - origin) * factor)
        out.append(mm)
    return out, cents, origin


def explode_points(pts, centroid, origin, factor):
    return np.asarray(pts, float) + (np.asarray(centroid) - origin) * factor


def simplify(mesh, nmax):
    n = len(mesh.triangles)
    if n <= nmax:
        return mesh
    try:
        s = clone(mesh).simplify_quadric_decimation(int(nmax))
        s.compute_vertex_normals()
        if len(s.triangles) >= 32:
            return s
    except Exception:
        pass
    rng = np.random.default_rng(0)
    idx = np.sort(rng.choice(n, nmax, replace=False))
    tris = np.asarray(mesh.triangles)[idx]
    verts = np.asarray(mesh.vertices)
    used = np.unique(tris)
    remap = -np.ones(len(verts), dtype=np.int32)
    remap[used] = np.arange(len(used))
    m = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(verts[used]),
        o3d.utility.Vector3iVector(remap[tris]),
    )
    m.compute_vertex_normals()
    return m


def tessellate_step(path: Path, extent: float) -> o3d.geometry.TriangleMesh:
    tol = max(0.00035, float(extent) * 0.0014)
    print(f"    tessellate {path.parent.name} tol={tol:.5g}", flush=True)
    wp = cq.importers.importStep(str(path))
    shape = wp.val()
    verts, faces = shape.tessellate(tol)
    v = np.array([[float(p.x), float(p.y), float(p.z)] for p in verts], dtype=np.float64)
    f = np.array([[int(a), int(b), int(c)] for a, b, c in faces], dtype=np.int32)
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(v),
        o3d.utility.Vector3iVector(f),
    )
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.compute_vertex_normals()
    return simplify(mesh, 220000)


def _append_polyline(pts, lines, seq):
    if seq is None or len(seq) < 2:
        return
    start = len(pts)
    for p in seq:
        if hasattr(p, "toTuple"):
            pts.append(p.toTuple())
        else:
            pts.append((float(p.X()), float(p.Y()), float(p.Z())) if hasattr(p, "X") else (float(p[0]), float(p[1]), float(p[2])))
    for i in range(len(seq) - 1):
        lines.append((start + i, start + i + 1))


def extract_edges(path: Path, diag: float):
    wp = cq.importers.importStep(str(path))
    pts, lines = [], []
    for e in wp.edges().vals():
        n = max(24, min(160, int(max(e.Length(), 1e-6) / max(diag * 0.004, 1e-5))))
        try:
            seq, _ = e.sample(n)
        except Exception:
            continue
        _append_polyline(pts, lines, seq)
    for face in wp.faces().vals():
        if str(face.geomType()).upper() not in {"BSPLINE", "BEZIER", "SURFACEOFREVOLUTION", "SURFACEOFEXTRUSION"}:
            continue
        try:
            ad = BRepAdaptor_Surface(face.wrapped)
            u1, u2 = float(ad.FirstUParameter()), float(ad.LastUParameter())
            v1, v2 = float(ad.FirstVParameter()), float(ad.LastVParameter())
        except Exception:
            continue
        for u in np.linspace(u1, u2, 9):
            seq = []
            for v in np.linspace(v1, v2, 42):
                p = ad.Value(float(u), float(v))
                seq.append((p.X(), p.Y(), p.Z()))
            _append_polyline(pts, lines, seq)
        for v in np.linspace(v1, v2, 5):
            seq = []
            for u in np.linspace(u1, u2, 42):
                p = ad.Value(float(u), float(v))
                seq.append((p.X(), p.Y(), p.Z()))
            _append_polyline(pts, lines, seq)
    return np.asarray(pts, float) if pts else np.zeros((0, 3)), np.asarray(lines, np.int32) if lines else np.zeros((0, 2), np.int32)


def lit_mat(rgb, metallic=0.28, roughness=0.38):
    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    mat.base_color = [float(rgb[0]), float(rgb[1]), float(rgb[2]), 1.0]
    mat.base_metallic = float(metallic)
    mat.base_roughness = float(roughness)
    mat.base_reflectance = 0.52
    try:
        mat.base_clearcoat = 0.18
        mat.base_clearcoat_roughness = 0.28
    except Exception:
        pass
    return mat


def line_mat(width=1.8):
    mat = rendering.MaterialRecord()
    mat.shader = "unlitLine"
    mat.line_width = float(width)
    mat.base_color = [0.07, 0.08, 0.10, 1.0]
    return mat


def caption(path: Path, text: str):
    im = Image.open(path).convert("RGB")
    f = font(26)
    draw = ImageDraw.Draw(im)
    bbox = draw.textbbox((0, 0), text, font=f)
    bar = (bbox[3] - bbox[1]) + 24
    out = Image.new("RGB", (im.width, im.height + bar), BG_RGB)
    out.paste(im, (0, bar))
    ImageDraw.Draw(out).text((18, 10), text, fill=(28, 32, 40), font=f)
    out.save(path, quality=94)


def crop_object(path: Path, pad=96):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im)
    bg = np.array(BG_RGB, dtype=np.int16)
    mask = np.any(np.abs(arr.astype(np.int16) - bg) > 10, axis=2)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width - 1, x1 + pad)
    y1 = min(im.height - 1, y1 + pad)
    im.crop((x0, y0, x1 + 1, y1 + 1)).save(path, quality=94)


class Renderer:
    def __init__(self, w=W, h=H):
        self.r = rendering.OffscreenRenderer(w, h)
        self.r.scene.set_background(BG)
        try:
            self.r.scene.set_lighting(
                rendering.Open3DScene.LightingProfile.SOFT_SHADOWS,
                np.array([-0.38, -0.58, -0.82]),
            )
        except Exception:
            pass
        self.r.scene.scene.set_sun_light([-0.38, -0.58, -0.82], [1.0, 1.0, 1.0], 110000)
        self.r.scene.scene.enable_sun_light(True)
        try:
            self.r.scene.scene.set_indirect_light_intensity(28000)
        except Exception:
            pass
        self.names = []
        self.lmat = line_mat()

    def clear(self):
        for n in self.names:
            try:
                self.r.scene.remove_geometry(n)
            except Exception:
                pass
        self.names = []

    def add_mesh(self, name, mesh, rgb, metallic=0.28, roughness=0.38):
        m = clone(mesh)
        self.r.scene.add_geometry(name, m, lit_mat(rgb, metallic, roughness))
        self.names.append(name)

    def add_edges(self, name, pts, lines):
        if pts is None or len(pts) < 2 or lines is None or len(lines) == 0:
            return
        ls = o3d.geometry.LineSet()
        ls.points = o3d.utility.Vector3dVector(np.asarray(pts, float))
        ls.lines = o3d.utility.Vector2iVector(np.asarray(lines, np.int32))
        try:
            self.r.scene.add_geometry(name, ls, self.lmat)
            self.names.append(name)
        except Exception as exc:
            print("edge overlay skipped:", exc, flush=True)

    def camera(self, meshes, eye_dir, fill=0.86, fov=38.0):
        lo, hi = aabb(meshes)
        center = 0.5 * (lo + hi)
        d = np.asarray(eye_dir, float)
        d = d / (np.linalg.norm(d) + 1e-12)
        up = np.array([0.0, 0.0, 1.0])
        if abs(float(d @ up)) > 0.96:
            up = np.array([0.0, 1.0, 0.0])
        right = np.cross(up, d)
        right /= np.linalg.norm(right) + 1e-12
        up = np.cross(d, right)
        corners = np.array(
            [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        )
        rel = corners - center
        width = 2.0 * float(np.abs(rel @ right).max())
        height = 2.0 * float(np.abs(rel @ up).max())
        aspect = W / float(H)
        half = np.tan(np.radians(fov) * 0.5)
        dist_h = (height / fill) / (2.0 * half + 1e-9)
        dist_w = (width / fill) / (2.0 * half * aspect + 1e-9)
        dist = max(dist_h, dist_w, 1e-3)
        eye = center + d * dist
        self.r.setup_camera(float(fov), center, eye, up)

    def save(self, path: Path, title: str | None = None, do_crop=True):
        img = self.r.render_to_image()
        o3d.io.write_image(str(path), img, 9)
        if do_crop:
            crop_object(path)
        if title:
            caption(path, title)
        print("WROTE", path, flush=True)


def collect():
    rows = []
    for pid in KEPT:
        i = int(pid.split("_")[1])
        d = ROOT / "parts" / f"{pid}__complete_part_{i:03d}"
        g = json.loads((d / "geometry.json").read_text()) if (d / "geometry.json").exists() else {}
        bbox = g.get("bbox")
        if bbox:
            extent = float(max(bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]))
        else:
            extent = 0.55
        met = json.loads((d / "original_metrics.json").read_text()) if (d / "original_metrics.json").exists() else {}
        rows.append(
            {
                "pid": pid,
                "step": d / "reconstructed.step",
                "extent": extent,
                "faces": g.get("faces") or met.get("cad_brep_face_count"),
                "iou": float(met.get("iou128") or 0.0),
                "color": PAL[pid],
            }
        )
    return rows


def downsample_for_html(mesh, nmax=14000):
    m = simplify(mesh, nmax)
    v = np.asarray(m.vertices)
    f = np.asarray(m.triangles)
    return v, f


def build_html(rows, meshes, edges, out: Path):
    fig = go.Figure()
    pal_hex = {
        "PART_000": "#9EB2CC",
        "PART_002": "#337ABD",
        "PART_003": "#2E9466",
        "PART_005": "#C7CED8",
        "PART_008": "#BD474C",
    }
    lighting = dict(ambient=0.36, diffuse=0.92, specular=0.62, roughness=0.32, fresnel=0.18)
    lightposition = dict(x=0.55, y=-0.85, z=1.15)
    vis_cad = []
    vis_edge = []
    for row, mesh, (pts, lines) in zip(rows, meshes, edges):
        v, f = downsample_for_html(mesh, 16000)
        fig.add_trace(
            go.Mesh3d(
                x=v[:, 0],
                y=v[:, 1],
                z=v[:, 2],
                i=f[:, 0],
                j=f[:, 1],
                k=f[:, 2],
                name=row["pid"],
                color=pal_hex[row["pid"]],
                opacity=1.0,
                flatshading=False,
                lighting=lighting,
                lightposition=lightposition,
                hovertemplate=f"{row['pid']}<extra></extra>",
                showscale=False,
            )
        )
        vis_cad.append(len(fig.data) - 1)
        if len(pts) and len(lines):
            step = max(1, len(lines) // 18000)
            segs = lines[::step]
            xs, ys, zs = [], [], []
            for a, b in segs:
                xs += [pts[a, 0], pts[b, 0], None]
                ys += [pts[a, 1], pts[b, 1], None]
                zs += [pts[a, 2], pts[b, 2], None]
            fig.add_trace(
                go.Scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode="lines",
                    name=f"{row['pid']} edges",
                    line=dict(color="#1a1d22", width=2.4),
                    hoverinfo="skip",
                )
            )
            vis_edge.append(len(fig.data) - 1)
    vis = [True] * len(fig.data)
    cad_only = [i in vis_cad for i in range(len(fig.data))]
    edges_on = vis[:]
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#eef1f6",
        plot_bgcolor="#eef1f6",
        margin=dict(l=8, r=8, t=72, b=16),
        height=860,
        title=dict(
            text="Airplane · reconstructed CAD solids (shaded + B-rep edges)",
            x=0.5,
            font=dict(size=22, color="#1c2230"),
        ),
        scene=dict(
            aspectmode="data",
            bgcolor="#eef1f6",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.35, y=-1.7, z=0.85), up=dict(x=0, y=0, z=1)),
        ),
        showlegend=False,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=1.08,
                buttons=[
                    dict(label="Shaded + edges", method="update", args=[{"visible": vis}]),
                    dict(label="Shaded only", method="update", args=[{"visible": cad_only}]),
                    dict(label="Edges on", method="update", args=[{"visible": edges_on}]),
                ],
            )
        ],
    )
    out.write_text(
        fig.to_html(
            full_html=True,
            include_plotlyjs=True,
            config={
                "responsive": True,
                "displaylogo": False,
                "scrollZoom": True,
                "toImageButtonOptions": {"filename": "airplane_cad_studio", "scale": 2},
            },
        ),
        encoding="utf-8",
    )
    print("WROTE", out, flush=True)


def contact_sheet(paths_labels, title, out, tile=(640, 440)):
    tw, th = tile
    cols = 3
    rows_n = (len(paths_labels) + cols - 1) // cols
    gap, header, footer = 14, 54, 34
    canvas = Image.new(
        "RGB",
        (cols * tw + (cols + 1) * gap, header + rows_n * (th + footer) + (rows_n + 1) * gap),
        (244, 246, 249),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 12), title, fill=(24, 28, 36), font=font(28))
    lf = font(18)
    for i, (p, lab) in enumerate(paths_labels):
        r, c = divmod(i, cols)
        x = gap + c * (tw + gap)
        y = header + gap + r * (th + footer + gap)
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th))
        px = x + (tw - im.width) // 2
        py = y + (th - im.height) // 2
        canvas.paste(im, (px, py))
        draw.rectangle([x, y + th, x + tw, y + th + footer], fill=(255, 255, 255))
        draw.text((x + 10, y + th + 6), lab, fill=(50, 55, 64), font=lf)
    canvas.save(out, quality=93)
    print("WROTE", out, flush=True)


def main():
    rows = collect()
    meshes, edges = [], []
    for row in rows:
        print(f"load {row['pid']} extent={row['extent']:.3g} iou={row['iou']:.3f}", flush=True)
        ply = TMP / f"{row['pid']}.ply"
        npz = TMP / f"{row['pid']}_edges.npz"
        if ply.exists() and npz.exists():
            mesh = o3d.io.read_triangle_mesh(str(ply))
            mesh.compute_vertex_normals()
            z = np.load(npz)
            pts, lines = z["pts"], z["lines"]
            print(f"  cache tris={len(mesh.triangles)} edges={len(lines)}", flush=True)
        else:
            mesh = tessellate_step(row["step"], row["extent"])
            lo = np.asarray(mesh.vertices).min(0)
            hi = np.asarray(mesh.vertices).max(0)
            diag = float(np.linalg.norm(hi - lo) + 1e-9)
            pts, lines = extract_edges(row["step"], diag)
            o3d.io.write_triangle_mesh(str(ply), mesh)
            np.savez_compressed(npz, pts=pts, lines=lines)
            print(
                f"  tris={len(mesh.triangles)} verts={len(mesh.vertices)} edges={len(lines)}",
                flush=True,
            )
        row["mesh"] = mesh
        row["edge_pts"] = pts
        row["edge_lines"] = lines
        meshes.append(mesh)
        edges.append((pts, lines))

    rnd = Renderer()
    views = [
        ("iso", [1.35, -1.85, 0.82], 0.72, 38.0, "isometric"),
        ("iso_b", [-1.45, -1.70, 0.82], 0.72, 38.0, "3/4 rear"),
        ("side", [2.2, 0.06, 0.18], 0.74, 36.0, "side"),
        ("front", [0.06, -1.0, 0.22], 0.48, 36.0, "front"),
        ("top", [0.06, -0.16, 1.0], 0.76, 34.0, "top"),
    ]

    def draw_colored(ms, eds, metallic=0.12, roughness=0.46, colors=None, with_edges=True):
        rnd.clear()
        for j, (m, row, (pts, lines)) in enumerate(zip(ms, rows, eds)):
            rgb = (colors[j] if colors is not None else row["color"])
            rnd.add_mesh(f"p{j}", m, rgb, metallic, roughness)
            if with_edges:
                rnd.add_edges(f"e{j}", pts, lines)

    tiles = []
    for name, eye, fill, fov, label in views:
        draw_colored(meshes, edges)
        rnd.camera(meshes, eye, fill, fov)
        raw = TMP / f"{name}.png"
        rnd.save(raw, do_crop=True)
        out = OUT / f"airplane_cad_studio_{name}.png"
        Image.open(raw).save(out, quality=94)
        caption(out, f"smooth airplane v2 · CAD solids + edges · {label} · kept {len(rows)}/9")
        tiles.append((raw, label))

    draw_colored(
        meshes,
        edges,
        metallic=0.72,
        roughness=0.34,
        colors=[METAL] * len(meshes),
    )
    rnd.camera(meshes, [1.35, -1.85, 0.82], 0.72, 38.0)
    metal = OUT / "airplane_cad_studio_metal.png"
    rnd.save(TMP / "metal.png", do_crop=True)
    Image.open(TMP / "metal.png").save(metal, quality=94)
    caption(metal, "smooth airplane v2 · studio aluminum shader · kept 5/9")

    exp_m, cents, origin = explode(meshes, 0.55)
    exp_e = []
    for (pts, lines), c in zip(edges, cents):
        if len(pts):
            exp_e.append((explode_points(pts, c, origin, 0.75), lines))
        else:
            exp_e.append((pts, lines))
    draw_colored(exp_m, exp_e, with_edges=False)
    rnd.camera(exp_m, [1.35, -1.85, 0.82], 0.68, 38.0)
    exp_out = OUT / "airplane_cad_studio_exploded.png"
    rnd.save(TMP / "exp.png", do_crop=True)
    Image.open(TMP / "exp.png").save(exp_out, quality=94)
    caption(exp_out, "smooth airplane v2 · exploded CAD solids · kept 5/9")
    tiles.append((TMP / "exp.png", "exploded"))
    tiles.append((TMP / "metal.png", "studio metal"))

    hero = OUT / "airplane_cad_studio.png"
    Image.open(TMP / "iso.png").save(hero, quality=94)
    caption(hero, "smooth airplane v2 · reconstructed CAD · shaded with B-rep edges")

    contact_sheet(
        tiles[:6],
        "smooth airplane v2 · CAD studio views · kept 5/9  (drop 001/004/006/007)",
        OUT / "airplane_cad_studio_multiview.png",
    )
    build_html(rows, meshes, edges, OUT / "airplane_cad_studio.html")
    os._exit(0)


if __name__ == "__main__":
    main()
