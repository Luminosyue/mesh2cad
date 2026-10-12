#!/usr/bin/env python3
"""CAD-style headless rendering: STEP→BRep→tessellation + edges/explode/section."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Softer CAD look (not saturated blue mesh blocks)
SOURCE_RGB = np.array([0.72, 0.73, 0.75])
CAD_RGB = np.array([0.78, 0.84, 0.90])  # industrial light blue-gray / ivory-blue
CAD_EDGE_RGB = np.array([0.18, 0.28, 0.38])
OVERLAY_SRC_RGB = np.array([0.70, 0.70, 0.72])
OVERLAY_CAD_RGB = np.array([0.25, 0.45, 0.75])

PART_PALETTE = [
    [0.55, 0.75, 0.86],
    [0.92, 0.78, 0.55],
    [0.72, 0.82, 0.62],
    [0.88, 0.68, 0.72],
    [0.70, 0.70, 0.84],
    [0.85, 0.85, 0.62],
    [0.78, 0.68, 0.58],
    [0.62, 0.80, 0.78],
    [0.90, 0.70, 0.55],
    [0.68, 0.74, 0.82],
    [0.80, 0.62, 0.70],
    [0.62, 0.72, 0.62],
]

LIN_DEFL = 0.0075
ANG_DEFL = 0.30


def dump(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            obj,
            indent=2,
            default=lambda o: float(o)
            if isinstance(o, (np.floating,))
            else int(o)
            if isinstance(o, (np.integer,))
            else str(o),
        )
        + "\n"
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def orbit_matrix(elev_deg=24.0, azim_deg=38.0):
    elev = math.radians(elev_deg)
    azim = math.radians(azim_deg)
    ca, sa = math.cos(azim), math.sin(azim)
    ce, se = math.cos(elev), math.sin(elev)
    Rz = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]], float)
    Rx = np.array([[1, 0, 0], [0, ce, se], [0, -se, ce]], float)
    return Rx @ Rz


def camera_limits_2d(bbox_min, bbox_max, R, pad=0.08):
    corners = np.array(
        [[x, y, z] for x in (bbox_min[0], bbox_max[0]) for y in (bbox_min[1], bbox_max[1]) for z in (bbox_min[2], bbox_max[2])],
        float,
    )
    proj = corners @ R.T
    lo, hi = proj[:, :2].min(0), proj[:, :2].max(0)
    mid = 0.5 * (lo + hi)
    half = 0.5 * max(hi - lo) * (1.0 + pad)
    return mid[0] - half, mid[0] + half, mid[1] - half, mid[1] + half


def prepare_mesh(mesh: trimesh.Trimesh, max_faces=160000, seed=0) -> trimesh.Trimesh:
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces, int)
    if len(F) == 0:
        return mesh
    if len(V) > 1.5 * max(len(F), 1):
        rounded = np.round(V, 6)
        uniq, inv = np.unique(rounded, axis=0, return_inverse=True)
        V, F = uniq, inv[F]
    if len(F) > max_faces:
        rng = np.random.default_rng(seed)
        F = F[np.sort(rng.choice(len(F), size=max_faces, replace=False))]
    return trimesh.Trimesh(vertices=V, faces=F, process=False)


def face_shade(tris3: np.ndarray, lights=None) -> np.ndarray:
    if lights is None:
        lights = [
            (np.array([0.35, 0.55, 0.85]), 0.72),
            (np.array([-0.55, 0.25, 0.55]), 0.22),
            (np.array([0.10, -0.70, 0.35]), 0.16),
        ]
    n = np.cross(tris3[:, 1] - tris3[:, 0], tris3[:, 2] - tris3[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.maximum(nn, 1e-12)
    inten = np.full(len(tris3), 0.18, float)
    for L, w in lights:
        L = L / np.linalg.norm(L)
        inten += w * np.clip(np.abs(n @ L), 0, 1)
    return np.clip(inten, 0, 1)


def _filter_min_length(segs: np.ndarray, min_len: float) -> np.ndarray:
    if len(segs) == 0:
        return segs
    lens = np.linalg.norm(segs[:, 1] - segs[:, 0], axis=1)
    return segs[lens >= min_len]


def extract_sharp_and_silhouette_edges(mesh: trimesh.Trimesh, sharp_deg=42.0, R=None, min_edge_len=None):
    """Approximate CAD edges from tessellation: sharp dihedral + silhouette."""
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces, int)
    if len(F) == 0:
        return np.zeros((0, 2, 3)), np.zeros((0, 2, 3))
    # weld for adjacency
    rounded = np.round(V, 6)
    uniq, inv = np.unique(rounded, axis=0, return_inverse=True)
    Fw = inv[F]
    m = trimesh.Trimesh(vertices=uniq, faces=Fw, process=False)
    if not hasattr(m, "face_adjacency") or len(m.face_adjacency) == 0:
        return np.zeros((0, 2, 3)), np.zeros((0, 2, 3))
    if min_edge_len is None:
        ext = float(np.linalg.norm(m.bounds[1] - m.bounds[0])) if len(m.vertices) else 1.0
        min_edge_len = max(ext * 0.0025, 1e-4)
    fn = m.face_normals
    adj = m.face_adjacency
    adj_edges = m.face_adjacency_edges
    # dihedral via normal angle
    dots = np.einsum("ij,ij->i", fn[adj[:, 0]], fn[adj[:, 1]])
    dots = np.clip(dots, -1, 1)
    ang = np.degrees(np.arccos(dots))
    sharp_mask = ang >= sharp_deg
    sharp_e = adj_edges[sharp_mask]
    sharp_segs = _filter_min_length(uniq[sharp_e], min_edge_len)

    silhouette = np.zeros((0, 2, 3))
    if R is not None:
        view = R[2]
        facing = fn @ view
        # only strong silhouette crossings (not grazing)
        s_mask = (facing[adj[:, 0]] * facing[adj[:, 1]]) < -0.02
        try:
            eu = m.edges_unique
            counts = np.bincount(m.edges_unique_inverse, minlength=len(eu))
            boundary = eu[counts == 1]
        except Exception:
            boundary = np.zeros((0, 2), int)
        sil_e = adj_edges[s_mask]
        if len(boundary):
            sil_e = np.vstack([sil_e, boundary]) if len(sil_e) else boundary
        if len(sil_e):
            key = np.sort(sil_e, axis=1)
            _, idx = np.unique(key, axis=0, return_index=True)
            silhouette = _filter_min_length(uniq[sil_e[idx]], min_edge_len)
    return sharp_segs, silhouette


def subsample_segments(segs: np.ndarray, max_segs: int, seed=0) -> np.ndarray:
    if len(segs) <= max_segs:
        return segs
    rng = np.random.default_rng(seed)
    # prefer longer edges
    lens = np.linalg.norm(segs[:, 1] - segs[:, 0], axis=1)
    w = np.maximum(lens, 1e-9)
    w = w / w.sum()
    idx = rng.choice(len(segs), size=max_segs, replace=False, p=w)
    return segs[idx]


def render_shaded(
    ax,
    mesh: trimesh.Trimesh,
    rgb,
    bbox_min,
    bbox_max,
    *,
    max_faces=140000,
    elev=24,
    azim=38,
    alpha=1.0,
    seed=0,
    edges=None,
    edge_rgb=CAD_EDGE_RGB,
    edge_lw=0.55,
    edge_alpha=0.92,
    weak_wire=False,
):
    mesh2 = prepare_mesh(mesh, max_faces=max_faces, seed=seed)
    V = np.asarray(mesh2.vertices, float)
    F = np.asarray(mesh2.faces, int)
    R = orbit_matrix(elev, azim)
    if len(F):
        tris = V[F]
        inten = face_shade(tris)
        base = np.asarray(rgb, float)
        colors = np.clip(base[None, :] * (0.35 + 0.65 * inten)[:, None], 0, 1)
        if alpha < 1.0:
            colors = np.concatenate([colors, np.full((len(colors), 1), alpha)], axis=1)
        depth = tris.mean(1) @ R[2]
        order = np.argsort(depth)
        tris2 = (tris @ R.T)[:, :, :2]
        ax.add_collection(
            PolyCollection(tris2[order], facecolors=colors[order], edgecolors="none", closed=True, zorder=1)
        )
        if weak_wire:
            # very light triangle hints (source only, subtle)
            rng = np.random.default_rng(seed + 9)
            pick = rng.choice(len(order), size=min(8000, len(order)), replace=False)
            ax.add_collection(
                PolyCollection(
                    tris2[order][pick],
                    facecolors="none",
                    edgecolors=(0.45, 0.45, 0.48, 0.08),
                    linewidths=0.15,
                    closed=True,
                    zorder=2,
                )
            )
    if edges is not None and len(edges):
        e2 = edges @ R.T
        segs2 = e2[:, :, :2]
        # depth sort approx by mid depth
        midz = edges.mean(1) @ R[2]
        order = np.argsort(midz)
        ergb = np.asarray(edge_rgb, float)
        ax.add_collection(
            LineCollection(
                segs2[order],
                colors=[(*ergb, edge_alpha)],
                linewidths=edge_lw,
                zorder=3,
            )
        )
    xmin, xmax, ymin, ymax = camera_limits_2d(bbox_min, bbox_max, R)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")
    return {"rendered_faces": int(len(F)), "rendered_edge_segments": int(0 if edges is None else len(edges)), "used_scatter": False}


def build_cad_edges(
    mesh: trimesh.Trimesh,
    elev=24,
    azim=38,
    sharp_deg=45.0,
    max_sharp=18000,
    max_sil=12000,
    include_silhouette=True,
):
    R = orbit_matrix(elev, azim)
    sharp, sil = extract_sharp_and_silhouette_edges(
        mesh, sharp_deg=sharp_deg, R=R if include_silhouette else None
    )
    sharp = subsample_segments(sharp, max_sharp, seed=1) if len(sharp) else sharp
    if include_silhouette:
        sil = subsample_segments(sil, max_sil, seed=2) if len(sil) else sil
    else:
        sil = np.zeros((0, 2, 3))
    if len(sharp) and len(sil):
        edges = np.vstack([sharp, sil])
    elif len(sharp):
        edges = sharp
    else:
        edges = sil
    mode = "SHARP_EDGE+SILHOUETTE" if include_silhouette else "SHARP_EDGE"
    return edges, {
        "EDGE_RENDER_MODE": mode,
        "SHARP_EDGE_COUNT": int(len(sharp)),
        "SILHOUETTE_EDGE_COUNT": int(len(sil)),
        "TOTAL_EDGE_SEGMENTS": int(len(edges)),
        "SHARP_DIHEDRAL_DEG": float(sharp_deg),
    }


def read_step(path: Path):
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone

    rd = STEPControl_Reader()
    st = rd.ReadFile(str(path))
    if st != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {path} status={st}")
    n = rd.TransferRoots()
    if n < 1:
        raise RuntimeError(f"STEP TransferRoots=0: {path}")
    return rd.OneShape(), int(n)


def tessellate_shape(shape, lin_defl=LIN_DEFL, ang_defl=ANG_DEFL):
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    BRepMesh_IncrementalMesh(shape, float(lin_defl), False, float(ang_defl), True).Perform()
    verts, faces, offset = [], [], 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            nodes = []
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                nodes.append([p.X(), p.Y(), p.Z()])
            nodes = np.asarray(nodes, float)
            for i in range(1, tri.NbTriangles() + 1):
                n1, n2, n3 = tri.Triangle(i).Get()
                faces.append([offset + n1 - 1, offset + n2 - 1, offset + n3 - 1])
            verts.append(nodes)
            offset += len(nodes)
        exp.Next()
    V = np.vstack(verts) if verts else np.zeros((0, 3))
    F = np.asarray(faces, int) if faces else np.zeros((0, 3), int)
    return V, F


def extract_solid_shapes(shape):
    from OCP.TopAbs import TopAbs_SOLID, TopAbs_SHELL
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopExp import TopExp

    mmap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_SOLID, mmap)
    solids = [mmap.FindKey(i) for i in range(1, mmap.Size() + 1)]
    if solids:
        return solids, "SOLID"
    mmap = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_SHELL, mmap)
    shells = [mmap.FindKey(i) for i in range(1, mmap.Size() + 1)]
    return shells, "SHELL"


def shape_bbox(shape):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, True)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return np.array([xmin, ymin, zmin], float), np.array([xmax, ymax, zmax], float)


def load_components_from_manifest(manifest_path: Path, lin_defl=LIN_DEFL, ang_defl=ANG_DEFL):
    """Load per-part STEP + transform for exploded/part-colored views."""
    man = json.loads(manifest_path.read_text())
    comps = []
    for row in man.get("components", []):
        step = Path(row["step_path"])
        tf = Path(row["transform_path"])
        if not step.is_file() or not tf.is_file():
            continue
        shape, _ = read_step(step)
        V, F = tessellate_shape(shape, lin_defl=lin_defl * 1.4, ang_defl=ang_defl)
        m = trimesh.Trimesh(vertices=V, faces=F, process=False)
        td = json.loads(tf.read_text())
        M = None
        for k in (
            "CANONICAL_TO_SOURCE",
            "CANONICAL_TO_SOURCE_MATRIX",
            "PART_TO_OBJECT_GLOBAL_MATRIX",
            "NORMALIZED_TO_SOURCE_MATRIX",
        ):
            if k in td:
                M = np.asarray(td[k], float)
                break
        if M is None:
            continue
        if M.shape == (3, 4):
            M4 = np.eye(4)
            M4[:3, :] = M
            M = M4
        m.apply_transform(M)
        comps.append({"id": row["component_id"], "mesh": m})
    return comps


def load_or_build_cad_cache(step_path: Path, cache_dir: Path, lin_defl=LIN_DEFL, ang_defl=ANG_DEFL):
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = f"{sha256(step_path)[:16]}_d{lin_defl}_a{ang_defl}"
    mesh_npz = cache_dir / f"{key}_assembly.npz"
    comps_npz = cache_dir / f"{key}_components.npz"
    meta_json = cache_dir / f"{key}_meta.json"

    if mesh_npz.is_file() and comps_npz.is_file() and meta_json.is_file():
        data = np.load(mesh_npz)
        cad = trimesh.Trimesh(vertices=data["V"], faces=data["F"], process=False)
        cdata = np.load(comps_npz, allow_pickle=True)
        components = []
        n = int(cdata["n"])
        for i in range(n):
            components.append(
                {
                    "id": str(cdata[f"id_{i}"]),
                    "mesh": trimesh.Trimesh(vertices=cdata[f"V_{i}"], faces=cdata[f"F_{i}"], process=False),
                }
            )
        meta = json.loads(meta_json.read_text())
        meta["CACHE_HIT"] = True
        return cad, components, meta

    shape, nroots = read_step(step_path)
    bb_min, bb_max = shape_bbox(shape)
    V, F = tessellate_shape(shape, lin_defl=lin_defl, ang_defl=ang_defl)
    cad = trimesh.Trimesh(vertices=V, faces=F, process=False)
    solids, kind = extract_solid_shapes(shape)
    components = []
    for i, sh in enumerate(solids):
        Vi, Fi = tessellate_shape(sh, lin_defl=lin_defl, ang_defl=ang_defl)
        components.append({"id": f"{kind}_{i:03d}", "mesh": trimesh.Trimesh(vertices=Vi, faces=Fi, process=False)})

    np.savez_compressed(mesh_npz, V=V, F=F)
    payload = {"n": len(components)}
    for i, c in enumerate(components):
        payload[f"id_{i}"] = c["id"]
        payload[f"V_{i}"] = np.asarray(c["mesh"].vertices)
        payload[f"F_{i}"] = np.asarray(c["mesh"].faces)
    np.savez_compressed(comps_npz, **payload)

    meta = {
        "STEP_PATH": str(step_path),
        "STEP_SHA256": sha256(step_path),
        "STEP_RELOAD_SUCCESS": True,
        "STEP_ROOTS": int(nroots),
        "STEP_COMPONENT_COUNT": int(len(components)),
        "COMPONENT_KIND": kind,
        "CAD_TESSELLATED_TRIANGLE_COUNT": int(len(F)),
        "CAD_TESSELLATION_DEFLECTION": float(lin_defl),
        "CAD_TESSELLATION_ANGULAR_DEFLECTION": float(ang_defl),
        "STEP_BBOX_MIN": bb_min.tolist(),
        "STEP_BBOX_MAX": bb_max.tolist(),
        "CACHE_HIT": False,
        "RIGHT_RENDER_USES_SOURCE_MESH": False,
        "RIGHT_RENDER_SOURCE": "STEP_ONLY",
    }
    dump(meta_json, meta)
    return cad, components, meta


def explode_components(components, factor=0.35):
    if not components:
        return []
    cents = []
    for c in components:
        m = c["mesh"]
        if len(m.vertices) == 0:
            cents.append(np.zeros(3))
        else:
            cents.append(np.asarray(m.vertices).mean(0))
    cents = np.asarray(cents, float)
    center = cents.mean(0)
    out = []
    for c, cen in zip(components, cents):
        direction = cen - center
        nrm = np.linalg.norm(direction)
        if nrm < 1e-9:
            offset = np.zeros(3)
        else:
            # explode proportional to distance from assembly center
            offset = direction * factor
        m = c["mesh"].copy()
        m.apply_translation(offset)
        out.append({"id": c["id"], "mesh": m, "offset": offset.tolist()})
    return out


def section_cut_mesh(mesh: trimesh.Trimesh, plane_point, plane_normal):
    """Keep triangles with centroid on positive side; add cut outline segments."""
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces, int)
    n = np.asarray(plane_normal, float)
    n = n / max(np.linalg.norm(n), 1e-12)
    p0 = np.asarray(plane_point, float)
    if len(F) == 0:
        return mesh, np.zeros((0, 2, 3))
    cents = V[F].mean(1)
    side = (cents - p0) @ n
    keep = side >= 0
    kept = trimesh.Trimesh(vertices=V, faces=F[keep], process=False)

    # edge intersections for cut outline
    segs = []
    # unique edges
    edges = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)
    d = (V - p0) @ n
    for a, b in edges:
        da, db = d[a], d[b]
        if da == 0 and db == 0:
            segs.append([V[a], V[b]])
        elif da * db < 0:
            t = da / (da - db + 1e-18)
            q = V[a] + t * (V[b] - V[a])
            # store as degenerate-ish pair with neighbor? single points later connected poorly;
            # keep segment stub using projected endpoints along edge crossing
            segs.append([q, q + 1e-6 * n])  # placeholder; better collect crossings per face
    # Better cut outline: per kept/culled face crossings
    segs = []
    for f in F:
        ds = d[f]
        if np.all(ds >= 0) or np.all(ds <= 0):
            continue
        pts = []
        for i in range(3):
            a, b = f[i], f[(i + 1) % 3]
            da, db = d[a], d[b]
            if da * db < 0:
                t = da / (da - db)
                pts.append(V[a] + t * (V[b] - V[a]))
            elif abs(da) < 1e-10:
                pts.append(V[a])
        if len(pts) >= 2:
            segs.append([pts[0], pts[1]])
    outline = np.asarray(segs, float) if segs else np.zeros((0, 2, 3))
    return kept, outline


def save_fig(path: Path, fig, dpi=170):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def make_provenance_panel(path: Path, case_name: str, meta: dict, source_path: Path, step_path: Path, thumb_src=None, thumb_cad=None):
    fig = plt.figure(figsize=(12, 7.2), dpi=160, facecolor="white")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.88])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(f"{case_name} CAD render provenance", fontsize=14, pad=10)

    boxes = [
        (0.04, 0.62, "1. Source mesh\n(OBJ)", "#e8e8ea"),
        (0.28, 0.62, "2. STEP file\n(assembly)", "#dceaf5"),
        (0.52, 0.62, "3. STEP reload\n→ BRep", "#d7f0e2"),
        (0.76, 0.62, "4. Tessellation\n+ edge overlay", "#f5ecd7"),
    ]
    for x, y, txt, col in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 0.18, 0.22, boxstyle="round,pad=0.02", facecolor=col, edgecolor="#444", linewidth=1.2))
        ax.text(x + 0.09, y + 0.11, txt, ha="center", va="center", fontsize=9)
    for x0, x1 in [(0.22, 0.28), (0.46, 0.52), (0.70, 0.76)]:
        ax.annotate("", xy=(x1, 0.73), xytext=(x0, 0.73), arrowprops=dict(arrowstyle="->", color="#333", lw=1.5))

    ax.text(
        0.5,
        0.50,
        "RIGHT PANEL USES STEP→BREP→TESSELLATION ONLY\nSOURCE OBJ NOT USED IN CAD RENDER",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#0b3d5c",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#eef6ff", edgecolor="#2a6f97"),
    )

    lines = [
        f"Source OBJ: {source_path}",
        f"STEP path:  {step_path}",
        f"STEP reload success: {meta.get('STEP_RELOAD_SUCCESS')}",
        f"Component count: {meta.get('STEP_COMPONENT_COUNT')}",
        f"CAD tessellated triangles: {meta.get('CAD_TESSELLATED_TRIANGLE_COUNT')}",
        f"Deflection: lin={meta.get('CAD_TESSELLATION_DEFLECTION')}  ang={meta.get('CAD_TESSELLATION_ANGULAR_DEFLECTION')}",
        f"Edge mode: {meta.get('EDGE_RENDER_MODE', 'SHARP_EDGE+SILHOUETTE')}",
        f"RIGHT_RENDER_USES_SOURCE_MESH: false",
        f"RIGHT_RENDER_SOURCE: STEP_ONLY",
    ]
    ax.text(0.05, 0.34, "\n".join(lines), ha="left", va="top", fontsize=8.5, family="monospace")

    if thumb_src is not None and Path(thumb_src).is_file():
        img = plt.imread(str(thumb_src))
        axins = fig.add_axes([0.55, 0.08, 0.18, 0.28])
        axins.imshow(img)
        axins.set_title("source", fontsize=8)
        axins.axis("off")
    if thumb_cad is not None and Path(thumb_cad).is_file():
        img = plt.imread(str(thumb_cad))
        axins = fig.add_axes([0.76, 0.08, 0.18, 0.28])
        axins.imshow(img)
        axins.set_title("CAD STEP", fontsize=8)
        axins.axis("off")

    save_fig(path, fig, dpi=160)


def crop_around(mesh: trimesh.Trimesh, center, radius) -> trimesh.Trimesh:
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces, int)
    if len(F) == 0:
        return mesh
    c = np.asarray(center, float)
    d = np.linalg.norm(V - c, axis=1)
    keep_v = d <= radius
    # keep faces with any vertex in ball, then also centroid filter
    keep_f = keep_v[F].any(axis=1)
    cents = V[F].mean(1)
    keep_f &= np.linalg.norm(cents - c, axis=1) <= radius * 1.05
    return trimesh.Trimesh(vertices=V, faces=F[keep_f], process=False)
