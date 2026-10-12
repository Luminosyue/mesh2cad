import json
import traceback
from pathlib import Path

import cadquery as cq
import numpy as np
import open3d as o3d


ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/cadrille_cadrecode_parts21_20260926_v2')
OUT = ROOT / 'cadrecode'


def pass_records(case_dir):
    records = []
    for part_dir in sorted(p for p in case_dir.glob('PART_*') if p.is_dir()):
        status_path = part_dir / 'STATUS.json'
        if not status_path.exists():
            continue
        status = json.loads(status_path.read_text())
        if status.get('status') != 'PASS':
            continue
        folder = Path(status.get('folder', ''))
        step = folder / 'world.step'
        if step.exists():
            records.append((part_dir.name, step, status))
    return records


def render_shape(shape, out_path):
    vertices, triangles = shape.tessellate(0.002, 0.1)
    if not vertices or not triangles:
        raise RuntimeError('empty tessellation')
    verts = np.asarray([v.toTuple() for v in vertices], dtype=np.float64)
    faces = np.asarray(triangles, dtype=np.int32)
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(verts),
        o3d.utility.Vector3iVector(faces),
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
    distance = float(max(extent)) * 2.2
    renderer.setup_camera(45.0, center, center + np.array([distance, distance, distance]), [0, 0, 1])
    o3d.io.write_image(str(out_path), renderer.render_to_image(), 9)
    return len(faces)


def main():
    rows = []
    for case_dir in sorted(p for p in OUT.iterdir() if p.is_dir()):
        if not any(case_dir.glob('PART_*/STATUS.json')):
            continue
        part_dirs = sorted(p for p in case_dir.glob('PART_*') if p.is_dir())
        records = pass_records(case_dir)
        failed = len(part_dirs) - len(records)
        row = {
            'case': case_dir.name,
            'required_parts': len(part_dirs),
            'pass_parts': len(records),
            'failed_parts': failed,
            'status': 'PASS' if failed == 0 else 'PARTIAL',
            'parts': [{'part': n, 'world_step': str(s), 'execution': st} for n, s, st in records],
        }
        try:
            shapes = [cq.importers.importStep(str(step)).val() for _, step, _ in records]
            shapes = [s for s in shapes if s.Solids()]
            if not shapes:
                raise RuntimeError('no successful solid STEP')
            assembled = cq.Compound.makeCompound(shapes)
            assembled_step = case_dir / 'assembled.step'
            cq.exporters.export(assembled, str(assembled_step))
            render_path = case_dir / 'assembled_cadrecode_orange.png'
            tris = render_shape(assembled, render_path)
            row.update({'assembled_step': str(assembled_step), 'render': str(render_path), 'render_triangles': tris})
        except Exception:
            row['assembly_error'] = traceback.format_exc()
        (case_dir / 'ASSEMBLY_SUMMARY.json').write_text(json.dumps(row, indent=2))
        rows.append(row)
        print(row['case'], row['status'], f"{row['pass_parts']}/{row['required_parts']}", flush=True)
    report = {
        'method': 'CAD-Recode v1.5 split-part generation followed by original-coordinate assembly',
        'checkpoint': '/data/home/cuiyuehan/project/mesh2cad/external_checkpoints/cad_recode_v1_5',
        'object_count': len(rows),
        'object_pass': sum(r['status'] == 'PASS' for r in rows),
        'object_partial': sum(r['status'] == 'PARTIAL' for r in rows),
        'total_parts': sum(r['required_parts'] for r in rows),
        'passed_parts': sum(r['pass_parts'] for r in rows),
        'assembled_step_count': sum('assembled_step' in r for r in rows),
        'render_count': sum('render' in r for r in rows),
        'objects': rows,
    }
    (OUT / 'CADRECODE_FULL21_STATUS.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ['object_count', 'object_pass', 'object_partial', 'total_parts', 'passed_parts', 'assembled_step_count', 'render_count']}))


if __name__ == '__main__':
    main()
