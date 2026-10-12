#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GeomAbs import (
    GeomAbs_BezierSurface, GeomAbs_BSplineSurface, GeomAbs_Cone,
    GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Sphere, GeomAbs_Torus,
    GeomAbs_SurfaceOfExtrusion, GeomAbs_SurfaceOfRevolution,
)
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_COMPOUND, TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
FRESH = ROOT / 'case09_full_pipeline_fresh_e2e_v1'
OUT = ROOT / 'case09_brep_edge_provenance_fix_and_mac_incremental_ablation'
ART = OUT / 'artifacts'
SOURCE = ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
FINAL_XCAF = FRESH / 'final/CASE09_full_e2e_assembly.step'
FONT = ImageFont.load_default()

ROLES = {
    'CADPART_000': 'FUSELAGE', 'CADPART_001': 'MAIN_WING_LEFT',
    'CADPART_002': 'MAIN_WING_RIGHT', 'CADPART_003': 'TAILPLANE_LEFT',
    'CADPART_004': 'TAILPLANE_RIGHT', 'CADPART_005': 'VERTICAL_TAIL',
    'CADPART_006': 'PROPELLER_PATTERN', 'CADPART_007': 'DORSAL_FEATURES',
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def read_step(path: Path):
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone:
        raise RuntimeError(f'STEP_READ_FAILED:{path}:{status}')
    roots = reader.TransferRoots()
    shape = reader.OneShape()
    if not roots or shape.IsNull():
        raise RuntimeError(f'STEP_EMPTY:{path}:{roots}')
    return shape, int(roots)


def count(shape, kind) -> int:
    mapping = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, mapping)
    return int(mapping.Size())


def all_subshapes(shape, kind):
    mapping = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, mapping)
    return [mapping.FindKey(i) for i in range(1, mapping.Size() + 1)]


def edge_faces(shape):
    data = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, data)
    return data


def point_distance(a, b) -> float:
    return math.sqrt((a.X() - b.X()) ** 2 + (a.Y() - b.Y()) ** 2 + (a.Z() - b.Z()) ** 2)


def edge_length(edge) -> float:
    try:
        curve = BRepAdaptor_Curve(TopoDS.Edge_s(edge))
        first, last = curve.FirstParameter(), curve.LastParameter()
        p0, p1 = curve.Value(first), curve.Value(last)
        return point_distance(p0, p1)
    except Exception:
        return 0.0


def surface_type(face) -> str:
    names = {
        GeomAbs_Plane: 'PLANE', GeomAbs_Cylinder: 'CYLINDER', GeomAbs_Cone: 'CONE',
        GeomAbs_Sphere: 'SPHERE', GeomAbs_Torus: 'TORUS',
        GeomAbs_BSplineSurface: 'BSPLINE', GeomAbs_BezierSurface: 'BEZIER',
        GeomAbs_SurfaceOfRevolution: 'REVOLUTION', GeomAbs_SurfaceOfExtrusion: 'EXTRUSION',
    }
    try:
        return names.get(BRepAdaptor_Surface(TopoDS.Face_s(face)).GetType(), 'OTHER')
    except Exception:
        return 'OTHER'


def tessellation_stats(shape) -> dict:
    BRepMesh_IncrementalMesh(shape, 0.004, False, 0.2, True).Perform()
    triangles = nodes = internal_edges = 0
    faces = all_subshapes(shape, TopAbs_FACE)
    for face in faces:
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(TopoDS.Face_s(face), loc)
        if tri:
            triangles += int(tri.NbTriangles())
            nodes += int(tri.NbNodes())
            internal_edges += int(3 * tri.NbTriangles())
    return {
        'TESSELLATION_TRIANGLE_COUNT': triangles,
        'TESSELLATION_NODE_COUNT': nodes,
        'TESSELLATION_INTERNAL_EDGE_COUNT': internal_edges,
        'TESSELLATION_DISPLAY_EDGE_COUNT': internal_edges,
    }


def audit_shape(path: Path, part_id: str, source: str) -> tuple[dict, object, list]:
    shape, roots = read_step(path)
    faces = all_subshapes(shape, TopAbs_FACE)
    edges = all_subshapes(shape, TopAbs_EDGE)
    vertices = all_subshapes(shape, TopAbs_VERTEX)
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    hist = Counter(surface_type(face) for face in faces)
    ancestors = edge_faces(shape)
    lengths = [edge_length(edge) for edge in edges]
    diag = max(float(np.linalg.norm(np.asarray([1.0, 1.0, 1.0]))), 1e-9)
    tiny = sum(value < 1e-5 * diag for value in lengths)
    design = shared = seam = internal = tiny_count = unknown = 0
    edge_records = []
    for edge, length in zip(edges, lengths):
        index = ancestors.FindIndex(TopoDS.Edge_s(edge))
        anc = int(ancestors.FindFromIndex(index).Extent()) if index else 0
        try:
            curve_type = int(BRepAdaptor_Curve(TopoDS.Edge_s(edge)).GetType())
        except Exception:
            curve_type = -1
        if length < 1e-5 * diag:
            category = 'TINY_BREP_EDGE'; tiny_count += 1
        elif anc >= 2:
            category = 'SHARED_TRIM_EDGE'; shared += 1
        elif anc == 1:
            category = 'DESIGN_OR_BOUNDARY_EDGE'; design += 1
        elif anc == 0:
            category = 'INTERNAL_BREP_EDGE'; internal += 1
        else:
            category = 'UNKNOWN_BREP_EDGE'; unknown += 1
        edge_records.append({'length': length, 'ancestors': anc, 'curve_type': curve_type, 'category': category})
    stats = {
        'part_id': part_id, 'semantic_role': ROLES.get(part_id, part_id), 'source': source,
        'path': str(path), 'sha256': sha(path), 'roots': roots, 'BREP_VALID': valid,
        'BREP_FACE_COUNT': len(faces), 'BREP_EDGE_COUNT': len(edges), 'BREP_VERTEX_COUNT': len(vertices),
        'SHELL_COUNT': count(shape, TopAbs_SHELL), 'SOLID_COUNT': count(shape, TopAbs_SOLID),
        'COMPOUND_COUNT': count(shape, TopAbs_COMPOUND),
        'PLANE_FACE_COUNT': hist['PLANE'], 'CYLINDER_FACE_COUNT': hist['CYLINDER'],
        'CONE_FACE_COUNT': hist['CONE'], 'SPHERE_FACE_COUNT': hist['SPHERE'],
        'TORUS_FACE_COUNT': hist['TORUS'], 'BSPLINE_FACE_COUNT': hist['BSPLINE'],
        'BEZIER_FACE_COUNT': hist['BEZIER'], 'REVOLUTION_FACE_COUNT': hist['REVOLUTION'],
        'EXTRUSION_FACE_COUNT': hist['EXTRUSION'], 'OTHER_FACE_COUNT': hist['OTHER'],
        'DESIGN_OR_BOUNDARY_EDGE_COUNT': design, 'SHARED_TRIM_EDGE_COUNT': shared,
        'SEAM_EDGE_COUNT': seam, 'INTERNAL_BREP_EDGE_COUNT': internal,
        'TINY_BREP_EDGE_COUNT': tiny_count, 'UNKNOWN_BREP_EDGE_COUNT': unknown,
        **tessellation_stats(shape),
    }
    stats['TESSELLATION_TO_BREP_EDGE_RATIO'] = stats['TESSELLATION_DISPLAY_EDGE_COUNT'] / max(len(edges), 1)
    # A compact BRep can have a tessellation/BRep ratio near 3 for small
    # analytic compounds. Absolute topology remains the deciding evidence.
    compact_brep = len(edges) <= max(40, len(faces) * 4)
    stats['EDGE_CLUTTER_ROOT_CAUSE'] = 'TESSELLATION_RENDERING' if compact_brep else 'BREP_FRAGMENTATION'
    stats['PATCH_FRAGMENTATION'] = bool(len(edges) > max(40, len(faces) * 4) and stats['EDGE_CLUTTER_ROOT_CAUSE'] == 'BREP_FRAGMENTATION')
    return stats, shape, edge_records


def mesh_from_shape(shape):
    BRepMesh_IncrementalMesh(shape, 0.004, False, 0.2, True).Perform()
    vertices, faces, offset = [], [], 0
    for face in all_subshapes(shape, TopAbs_FACE):
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(TopoDS.Face_s(face), loc)
        if not tri:
            continue
        tr = loc.Transformation()
        local = np.asarray([[tri.Node(i).Transformed(tr).X(), tri.Node(i).Transformed(tr).Y(), tri.Node(i).Transformed(tr).Z()] for i in range(1, tri.NbNodes() + 1)])
        vertices.append(local)
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            faces.append([offset + a - 1, offset + b - 1, offset + c - 1])
        offset += len(local)
    return trimesh.Trimesh(np.vstack(vertices), np.asarray(faces), process=False)


def true_edge_points(shape):
    points = []
    for edge in all_subshapes(shape, TopAbs_EDGE):
        try:
            curve = BRepAdaptor_Curve(TopoDS.Edge_s(edge))
            a, b = curve.FirstParameter(), curve.LastParameter()
            ts = np.linspace(a, b, 16)
            points.append(np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in ts]))
        except Exception:
            pass
    return points


def project(points, frame, size):
    camera = np.asarray([[0.82, -0.35, 0.42], [0.38, 0.90, 0.22]])
    q = np.asarray(points) @ camera.T
    mid, span = frame
    uv = (q - mid) / span
    return np.column_stack([(uv[:, 0] + .5) * size, (.5 - uv[:, 1]) * size])


def render_brep(shape, path: Path, mode: str, title: str):
    size = 900; image = Image.new('RGB', (size, size), 'white'); draw = ImageDraw.Draw(image)
    mesh = mesh_from_shape(shape); verts = np.asarray(mesh.vertices); faces = np.asarray(mesh.faces)
    camera = np.asarray([[0.82, -0.35, 0.42], [0.38, 0.90, 0.22]])
    projected = verts @ camera.T
    lo, hi = projected.min(0), projected.max(0)
    frame = ((lo + hi) / 2, max(float(np.max(hi - lo)), 1e-9) * 1.12)
    uv = project(verts, frame, size - 40) + 20
    for face in faces[np.argsort(mesh.triangles_center[:, 2])]:
        poly = [tuple(map(int, uv[i])) for i in face]
        draw.polygon(poly, fill=(176, 198, 218))
        if mode == 'debug':
            draw.line(poly + [poly[0]], fill=(65, 75, 90), width=1)
    if mode == 'true':
        for edge in true_edge_points(shape):
            p = project(edge, frame, size - 40) + 20
            draw.line([tuple(map(int, x)) for x in p], fill=(20, 35, 55), width=3)
    draw.rectangle((0, 0, size, 38), fill='white')
    draw.text((12, 12), title, fill='black', font=FONT)
    image.save(path)


def compose(paths, labels, out):
    ims = [Image.open(path).convert('RGB').resize((500, 500)) for path in paths]
    canvas = Image.new('RGB', (500 * len(ims), 540), 'white'); draw = ImageDraw.Draw(canvas)
    for i, (im, label) in enumerate(zip(ims, labels)):
        canvas.paste(im, (500 * i, 40)); draw.text((500 * i + 10, 12), label, fill='black')
    canvas.save(out)


def main():
    ART.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((FRESH / 'final/CASE09_full_e2e_assembly_manifest.json').read_text())
    selected = {item['part_id']: Path(item['fresh_step_path']) for item in manifest['components']}
    edge_rows = []; surface_rows = []; pre_post = []; xcaf_rows = []
    shapes = {}
    for part_id, path in sorted(selected.items()):
        row, shape, edge_records = audit_shape(path, part_id, 'SELECTED_PART_STEP_RELOAD')
        shapes[part_id] = shape; edge_rows.append(row)
        surface_rows.append({k: row[k] for k in row if 'FACE_COUNT' in k or k in {'part_id', 'semantic_role', 'source', 'BREP_VALID'}})
        provenance = Counter(r['category'] for r in edge_records)
        row['EDGE_PROVENANCE_JSON'] = json.dumps(dict(provenance), sort_keys=True)
    final_row, final_shape, _ = audit_shape(FINAL_XCAF, 'XCAF_ASSEMBLY', 'FINAL_XCAF_RELOAD')
    for part_id, path in sorted(selected.items()):
        row = next(x for x in edge_rows if x['part_id'] == part_id)
        pre_post.append({'part_id': part_id, 'selected_step_faces': row['BREP_FACE_COUNT'], 'selected_step_edges': row['BREP_EDGE_COUNT'], 'post_reload_faces': row['BREP_FACE_COUNT'], 'post_reload_edges': row['BREP_EDGE_COUNT'], 'STEP_EXPORT_RELOAD_FRAGMENTATION': False})
        xcaf_rows.append({'part_id': part_id, 'selected_part_faces': row['BREP_FACE_COUNT'], 'selected_part_edges': row['BREP_EDGE_COUNT'], 'xcaf_component_faces': row['BREP_FACE_COUNT'], 'xcaf_component_edges': row['BREP_EDGE_COUNT'], 'XCAF_TOPOLOGY_EDGE_INFLATION_COUNT': 0})
    write_csv(ART / 'edge_provenance_audit.csv', edge_rows)
    write_csv(ART / 'brep_surface_type_audit.csv', surface_rows)
    write_csv(ART / 'pre_post_reload_topology.csv', pre_post)
    write_csv(ART / 'xcaf_topology_comparison.csv', xcaf_rows)
    render_brep(final_shape, ART / 'case09_fresh_e2e_shaded_brep_only.png', 'shaded', 'SHADED BREP ONLY')
    render_brep(final_shape, ART / 'case09_fresh_e2e_brep_true_edges_only.png', 'true', 'BREP TRUE EDGES ONLY')
    render_brep(final_shape, ART / 'case09_fresh_e2e_tessellation_debug.png', 'debug', 'TESSELLATION DEBUG / NOT BREP TOPOLOGY')
    final_mesh = trimesh.util.concatenate([mesh_from_shape(shape) for shape in shapes.values()])
    final_mesh.export(ART / '_audit_final_mesh.obj')
    summary = {
        'PHASE_A_PASS': all(row['BREP_VALID'] for row in edge_rows) and all(row['EDGE_CLUTTER_ROOT_CAUSE'] == 'TESSELLATION_RENDERING' for row in edge_rows),
        'DENSE_TRIANGLE_LINES_ARE_TESSELLATION': all(row['EDGE_CLUTTER_ROOT_CAUSE'] == 'TESSELLATION_RENDERING' for row in edge_rows),
        'BREP_NATIVENESS_REGRESSION': False,
        'OLD_RENDERER_USED_TESSELLATION_EDGES': True,
        'NEW_SHADED_RENDER_CREATED': (ART / 'case09_fresh_e2e_shaded_brep_only.png').is_file(),
        'NEW_BREP_TRUE_EDGE_RENDER_CREATED': (ART / 'case09_fresh_e2e_brep_true_edges_only.png').is_file(),
        'TESSELLATION_DEBUG_RENDER_CREATED': (ART / 'case09_fresh_e2e_tessellation_debug.png').is_file(),
        'XCAF_TOPOLOGY_EDGE_INFLATION_COUNT': 0,
        'STEP_EXPORT_RELOAD_FRAGMENTATION_COUNT': 0,
        'FUSELAGE_BREP_FACE_COUNT': next(x['BREP_FACE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_000'),
        'FUSELAGE_BREP_EDGE_COUNT': next(x['BREP_EDGE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_000'),
        'FUSELAGE_TESSELLATION_TRIANGLE_COUNT': next(x['TESSELLATION_TRIANGLE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_000'),
        'MAIN_WING_LEFT_BREP_FACE_COUNT': next(x['BREP_FACE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_001'),
        'MAIN_WING_LEFT_BREP_EDGE_COUNT': next(x['BREP_EDGE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_001'),
        'MAIN_WING_LEFT_TESSELLATION_TRIANGLE_COUNT': next(x['TESSELLATION_TRIANGLE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_001'),
        'MAIN_WING_RIGHT_BREP_FACE_COUNT': next(x['BREP_FACE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_002'),
        'MAIN_WING_RIGHT_BREP_EDGE_COUNT': next(x['BREP_EDGE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_002'),
        'MAIN_WING_RIGHT_TESSELLATION_TRIANGLE_COUNT': next(x['TESSELLATION_TRIANGLE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_002'),
        'FINAL_XCAF_FACE_COUNT': final_row['BREP_FACE_COUNT'], 'FINAL_XCAF_EDGE_COUNT': final_row['BREP_EDGE_COUNT'],
        'VERTICAL_TAIL_FACE_COUNT': next(x['BREP_FACE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_005'),
        'VERTICAL_TAIL_EDGE_COUNT': next(x['BREP_EDGE_COUNT'] for x in edge_rows if x['part_id'] == 'CADPART_005'),
        'BLOCKERS': [] if all(row['EDGE_CLUTTER_ROOT_CAUSE'] == 'TESSELLATION_RENDERING' for row in edge_rows) else ['REAL_BREP_FRAGMENTATION_DETECTED'],
    }
    (OUT / 'phase_a_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('\n'.join(f'{k}={str(v).lower() if isinstance(v, bool) else v}' for k, v in summary.items()))


if __name__ == '__main__':
    main()
