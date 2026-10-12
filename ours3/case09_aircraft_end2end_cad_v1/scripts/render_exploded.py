#!/usr/bin/env python3
"""Render exploded + face-colored views for CASE09 end2end CAD."""
from __future__ import annotations

import colorsys
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1")
ART = OUT / "artifacts"
SOURCE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj")
RECOVERY = OUT / "05_backend_recovery"

PARTS = [
    ("CADPART_000", "FUSELAGE"),
    ("CADPART_001", "MAIN_WING_LEFT"),
    ("CADPART_002", "MAIN_WING_RIGHT"),
    ("CADPART_003", "HORIZONTAL_TAIL_LEFT"),
    ("CADPART_004", "HORIZONTAL_TAIL_RIGHT"),
    ("CADPART_005", "VERTICAL_TAIL"),
    ("CADPART_006", "PROPELLER_PATTERN"),
    ("CADPART_007", "DORSAL_FEATURES"),
]

PALETTE = [
    (120, 168, 214),
    (232, 170, 120),
    (130, 190, 140),
    (220, 140, 160),
    (170, 140, 210),
    (230, 210, 110),
    (120, 190, 190),
    (190, 150, 170),
]

EXPLODE = 0.08


def camera_matrix():
    a, e = np.radians(38), np.radians(24)
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), np.sin(e)], [0, -np.sin(e), np.cos(e)]])
    return rx @ rz


CAMERA = camera_matrix()


def project(points, bounds, w, h, pad=0.08):
    corners = np.array([[x, y, z] for x in bounds[0] for y in bounds[1] for z in bounds[2]])
    q = corners @ CAMERA.T
    lo, hi = q[:, :2].min(0), q[:, :2].max(0)
    mid = (lo + hi) / 2
    span = max(hi - lo) * (1 + 2 * pad)
    p = points @ CAMERA.T
    xy = (p[:, :2] - mid) / span
    return np.c_[(xy[:, 0] + 0.5) * w, (0.5 - xy[:, 1]) * h], p[:, 2]


def read_step(path: Path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    roots = reader.TransferRoots() if status == IFSelect_RetDone else 0
    shape = reader.OneShape() if roots else None
    return shape


def tessellate(shape, deflection=0.005, angle=0.22):
    BRepMesh_IncrementalMesh(shape, float(deflection), False, float(angle), True).Perform()
    vertices, faces, face_ids, offset, face_id = [], [], [], 0, 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face_id += 1
        face = TopoDS.Face_s(explorer.Current())
        location = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, location)
        if tri:
            transform = location.Transformation()
            local = np.asarray(
                [
                    [
                        tri.Node(i).Transformed(transform).X(),
                        tri.Node(i).Transformed(transform).Y(),
                        tri.Node(i).Transformed(transform).Z(),
                    ]
                    for i in range(1, tri.NbNodes() + 1)
                ],
                float,
            )
            for i in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(i).Get()
                faces.append([offset + a - 1, offset + b - 1, offset + c - 1])
                face_ids.append(face_id)
            vertices.append(local)
            offset += len(local)
        explorer.Next()
    if not vertices or not faces:
        raise RuntimeError("empty tessellation")
    return np.vstack(vertices), np.asarray(faces, np.int64), np.asarray(face_ids, np.int64)


def face_palette(n: int):
    colors = []
    for i in range(max(n, 1)):
        h = (i * 0.61803398875) % 1.0
        s = 0.55 + 0.25 * ((i % 3) / 2)
        v = 0.78 + 0.15 * ((i % 2))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))
    return colors


def shade(base, normal):
    n = normal / max(np.linalg.norm(normal), 1e-12)
    light = np.array([0.3, 0.45, 0.84])
    light /= np.linalg.norm(light)
    v = 0.38 + 0.62 * abs(float(n @ light))
    return tuple(int(c * v) for c in base)


def explode_offset(vertices, center, diag, factor):
    d = vertices.mean(0) - center
    return d / max(np.linalg.norm(d), 1e-12) * diag * factor


def render_parts(comps, bounds, path, colors, explode=0.0, size=(1400, 1050), edges=True):
    w, h = size
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    center = bounds.mean(1)
    diag = float(np.linalg.norm(bounds[:, 1] - bounds[:, 0]))
    triangles = []
    edge_polylines = []
    for mi, mesh in enumerate(comps):
        V = np.asarray(mesh.vertices, float).copy()
        F = np.asarray(mesh.faces, int)
        if len(V) == 0 or len(F) == 0:
            continue
        if explode and len(comps) > 1:
            V = V + explode_offset(V, center, diag, explode)
        xy, z = project(V, bounds, w, h)
        base = colors[mi % len(colors)]
        stride = max(1, len(F) // 90000)
        for face in F[::stride]:
            p = V[face]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            triangles.append((float(z[face].mean()), [tuple(x) for x in xy[face]], shade(base, n)))
        if edges:
            try:
                adj = mesh.face_adjacency
                angles = mesh.face_adjacency_angles
                for (a, b), ang in zip(adj, angles):
                    if ang < np.radians(35):
                        continue
                    shared = np.intersect1d(F[a], F[b])
                    if len(shared) < 2:
                        continue
                    pts = V[shared[:2]]
                    edge_polylines.append(pts)
            except Exception:
                pass
    triangles.sort(key=lambda x: x[0])
    for _, poly, color in triangles:
        draw.polygon(poly, fill=color)
    for pts in edge_polylines:
        xy, _ = project(pts, bounds, w, h)
        draw.line([tuple(xy[0]), tuple(xy[1])], fill=(35, 50, 70), width=1)
    image.save(path, dpi=(180, 180))


def render_face_colored(parts, bounds, path, explode=0.0, size=(1400, 1050)):
    """Each TopoDS face gets a unique color; parts are optionally exploded."""
    w, h = size
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    center = bounds.mean(1)
    diag = float(np.linalg.norm(bounds[:, 1] - bounds[:, 0]))
    total_faces = sum(int(np.max(fids)) if len(fids) else 0 for _, _, fids in parts)
    colors = face_palette(total_faces + 2)
    triangles = []
    face_counter = 0
    for vertices, faces, face_ids in parts:
        V = np.asarray(vertices, float).copy()
        F = np.asarray(faces, int)
        if len(V) == 0 or len(F) == 0:
            continue
        if explode and len(parts) > 1:
            V = V + explode_offset(V, center, diag, explode)
        xy, z = project(V, bounds, w, h)
        local_max = int(np.max(face_ids)) if len(face_ids) else 0
        for tri, fid in zip(F, face_ids):
            base = colors[(face_counter + int(fid) - 1) % len(colors)]
            p = V[tri]
            n = np.cross(p[1] - p[0], p[2] - p[0])
            triangles.append((float(z[tri].mean()), [tuple(x) for x in xy[tri]], shade(base, n)))
        face_counter += local_max
    triangles.sort(key=lambda x: x[0])
    for _, poly, color in triangles:
        draw.polygon(poly, fill=color)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    draw.text((18, 14), f"TopoDS faces colored  |  n={face_counter}  |  explode={explode}", fill=(25, 35, 50), font=font)
    image.save(path, dpi=(180, 180))
    return face_counter


def compose(paths, titles, out):
    images = [Image.open(p).convert("RGB") for p in paths]
    pw, ph = 700, 560
    canvas = Image.new("RGB", (pw * len(images), ph + 40), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    for i, (im, title) in enumerate(zip(images, titles)):
        im = im.copy()
        im.thumbnail((pw - 20, ph - 40))
        canvas.paste(im, (i * pw + 10, 36))
        draw.text((i * pw + 16, 10), title, fill=(20, 30, 45), font=font)
    canvas.save(out, dpi=(180, 180))


def main():
    ART.mkdir(parents=True, exist_ok=True)
    source = trimesh.load(str(SOURCE), force="mesh", process=False)
    bounds = np.asarray(source.bounds).T

    comps = []
    face_parts = []
    meta_parts = []
    for i, (pid, label) in enumerate(PARTS):
        step = RECOVERY / pid / "reconstructed.step"
        shape = read_step(step)
        if shape is None or shape.IsNull():
            raise RuntimeError(f"failed to load {step}")
        V, F, face_ids = tessellate(shape)
        mesh = trimesh.Trimesh(vertices=V, faces=F, process=False)
        comps.append(mesh)
        face_parts.append((V, F, face_ids))
        meta_parts.append(
            {
                "part_id": pid,
                "label": label,
                "face_count": int(np.max(face_ids)) if len(face_ids) else 0,
                "triangles": int(len(F)),
                "vertices": int(len(V)),
            }
        )
        print(f"loaded {pid} {label}: faces={meta_parts[-1]['face_count']} tris={len(F)}", flush=True)

    assembled = ART / "part_colored_assembled.png"
    exploded = ART / "exploded_parts.png"
    face_assem = ART / "face_colored_assembled.png"
    face_expl = ART / "exploded_face_colored.png"
    board = ART / "exploded_board.png"

    render_parts(comps, bounds, assembled, PALETTE, explode=0.0)
    render_parts(comps, bounds, exploded, PALETTE, explode=EXPLODE)
    n1 = render_face_colored(face_parts, bounds, face_assem, explode=0.0)
    n2 = render_face_colored(face_parts, bounds, face_expl, explode=EXPLODE)
    compose(
        [assembled, exploded, face_expl],
        ["Assembled parts", f"Exploded parts (×{EXPLODE})", "Exploded face-colored"],
        board,
    )

    meta = {
        "EXPLODE_FACTOR": EXPLODE,
        "SOURCE_BOUNDS": bounds.tolist(),
        "PARTS": meta_parts,
        "TOTAL_FACES": int(sum(p["face_count"] for p in meta_parts)),
        "FACE_COUNT_RENDERED_ASSEMBLED": n1,
        "FACE_COUNT_RENDERED_EXPLODED": n2,
        "OUTPUTS": {
            "part_colored_assembled": str(assembled),
            "exploded_parts": str(exploded),
            "face_colored_assembled": str(face_assem),
            "exploded_face_colored": str(face_expl),
            "exploded_board": str(board),
        },
    }
    (ART / "exploded_render_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta["OUTPUTS"], indent=2))
    print("TOTAL_FACES", meta["TOTAL_FACES"])


if __name__ == "__main__":
    main()
