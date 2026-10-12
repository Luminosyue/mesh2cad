import json
from pathlib import Path

import cadquery as cq
import numpy as np
import open3d as o3d

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_full20_20260926/results')


def render(case_dir, out_path):
    all_vertices = []
    all_triangles = []
    for step_path in sorted(case_dir.glob('PART_*/world.step')):
        try:
            shape = cq.importers.importStep(str(step_path)).val()
            vertices, triangles = shape.tessellate(0.35)
            offset = sum(len(v) for v in all_vertices)
            all_vertices.append([v.toTuple() for v in vertices])
            all_triangles.append(np.asarray(triangles, dtype=np.int32) + offset)
        except Exception:
            continue
    if not all_vertices:
        raise RuntimeError('no readable part STEP')
    vertices = np.concatenate([np.asarray(v, dtype=np.float64) for v in all_vertices], axis=0)
    triangles = np.concatenate(all_triangles, axis=0)
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(vertices),
        o3d.utility.Vector3iVector(triangles),
    )
    mesh.compute_vertex_normals()
    mesh.paint_uniform_color([0.92, 0.48, 0.03])
    renderer = o3d.visualization.rendering.OffscreenRenderer(1400, 1050)
    renderer.scene.set_background([1.0, 1.0, 1.0, 1.0])
    material = o3d.visualization.rendering.MaterialRecord()
    material.shader = 'defaultLit'
    material.base_color = [0.92, 0.48, 0.03, 1.0]
    renderer.scene.add_geometry('cad', mesh, material)
    bounds = mesh.get_axis_aligned_bounding_box()
    center = bounds.get_center()
    extent = np.asarray(bounds.get_extent())
    distance = float(max(extent)) * 2.4
    renderer.setup_camera(45.0, center, center + np.array([distance, distance, distance]), [0, 0, 1])
    image = renderer.render_to_image()
    o3d.io.write_image(str(out_path), image, 9)
    return len(mesh.triangles)


def main():
    rows = []
    for case_dir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        out_path = case_dir / 'assembled_cadrille_orange.png'
        try:
            triangles = render(case_dir, out_path)
            rows.append({'case': case_dir.name, 'status': 'PASS', 'triangles': triangles, 'render': str(out_path)})
        except Exception as exc:
            rows.append({'case': case_dir.name, 'status': 'FAIL', 'error': repr(exc)})
    (ROOT / 'RENDER_SUMMARY.json').write_text(json.dumps(rows, indent=2))
    print(json.dumps({'rendered': sum(x['status'] == 'PASS' for x in rows), 'failed': sum(x['status'] != 'PASS' for x in rows)}, indent=2))


if __name__ == '__main__':
    main()
