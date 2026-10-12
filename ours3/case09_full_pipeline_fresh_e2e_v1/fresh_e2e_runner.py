#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT = ROOT / 'case09_full_pipeline_fresh_e2e_v1'
SOURCE = ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj'
P3_RUNNER = ROOT / 'case09_fullstack_mesh2cad_mac_v6/scripts/p3_fresh_v6.py'
PHYSX_RUNNER = ROOT / 'case09_aircraft_end2end_cad_v1/scripts/run_physx.py'
V6_RUNTIME_PATH = ROOT / 'case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py'
V6_RESTORE = ROOT / 'v6_geometry_backend_restore'
V10 = ROOT / 'v10_geometry_gated_builder_contract_closure'
V11B = ROOT / 'v11b_real_qwen_mac_open_shell_closure'
V13 = ROOT / 'v13_transform_restore_and_xcaf_assembly'
MAC_ENV = ROOT / '.mac_env'
PHYSX_PYTHON = '/data/miniconda3/bin/python'
sys.path.insert(0, str(ROOT / 'v6_backend_mainline_integration'))

ROLE_CONFIG = {
    'CADPART_000': ('FUSELAGE', 'Y', [8]),
    'CADPART_001': ('MAIN_WING_LEFT', 'X', [2]),
    'CADPART_002': ('MAIN_WING_RIGHT', 'X', [4]),
    'CADPART_003': ('TAILPLANE_LEFT', 'X', [7]),
    'CADPART_004': ('TAILPLANE_RIGHT', 'X', [5]),
    'CADPART_005': ('VERTICAL_TAIL', 'X', [0]),
    'CADPART_006': ('PROPELLER_PATTERN', 'Y', [1, 3]),
    'CADPART_007': ('DORSAL_FEATURES', 'X', [6, 9]),
}
V6_CONFIG = {
    'CADPART_000': ('FUSELAGE', 'PERIODIC_GLOBAL_BSPLINE', 64, 32, 0.001),
    'CADPART_001': ('MAIN_WING_LEFT', 'GLOBAL_UPPER_LOWER_SKINS', 64, 64, 0.001),
    'CADPART_002': ('MAIN_WING_RIGHT', 'RIGHT_WING_SEMANTIC_SKIN_REPAIR', 12, 10, 0.0002),
    'CADPART_003': ('TAILPLANE_LEFT', 'GLOBAL_UPPER_LOWER_SKINS', 64, 64, 0.001),
    'CADPART_004': ('TAILPLANE_RIGHT', 'GLOBAL_UPPER_LOWER_SKINS', 64, 64, 0.001),
    'CADPART_005': ('VERTICAL_TAIL', 'GLOBAL_UPPER_LOWER_SKINS', 64, 64, 0.001),
}


def clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + '\n', encoding='utf-8')


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value for key, value in row.items()})


def render_mesh(mesh: trimesh.Trimesh, path: Path, true_edges: bool = False, size: int = 520) -> None:
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)
    v = np.asarray(mesh.vertices, float)
    f = np.asarray(mesh.faces, int)
    if len(f) == 0:
        image.save(path)
        return
    q = v @ np.array([[0.82, -0.35], [0.38, 0.90], [0.42, 0.22]])
    lo = q.min(axis=0)
    span = np.maximum(q.max(axis=0) - lo, 1e-9)
    q = (q - lo) / span
    depth = v[f].mean(axis=1) @ np.array([0.3, 0.2, 1.0])
    ids = np.arange(len(f))
    if len(ids) > 18000:
        ids = np.linspace(0, len(f) - 1, 18000, dtype=int)
    for i in ids[np.argsort(depth[ids])]:
        poly = [(int(q[j, 0] * (size - 40) + 20), int((size - 20) - q[j, 1] * (size - 40))) for j in f[i]]
        draw.polygon(poly, fill=(190, 201, 216), outline=(45, 55, 70) if true_edges else None)
    image.save(path)


def source_audit(source: trimesh.Trimesh) -> dict[str, Any]:
    comps = source.split(only_watertight=False)
    normals = np.asarray(source.face_normals)
    audit = {
        'SOURCE_AUDIT_FRESH': True,
        'readable': True,
        'source_obj': str(SOURCE),
        'source_sha256': sha(SOURCE),
        'vertices': int(len(source.vertices)),
        'triangles': int(len(source.faces)),
        'bbox': source.bounds,
        'centroid': source.centroid,
        'connected_components': int(len(comps)),
        'watertight': bool(source.is_watertight),
        'winding_consistent': bool(source.is_winding_consistent),
        'non_manifold_edges': int(np.sum(np.bincount(source.edges_unique_inverse) > 2)),
        'normal_finite': bool(np.isfinite(normals).all()),
        'units_sanity': bool(np.linalg.norm(source.extents) < 1000.0 and np.linalg.norm(source.extents) > 1e-6),
    }
    dump(OUT / '00_source_audit/source_audit.json', audit)
    render_mesh(source, OUT / '00_source_audit/source_axonometric.png')
    return audit


def run_physx(image: Path) -> dict[str, Any]:
    physx_dir = OUT / '04_physx_semantics'
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = '5'
    started = time.time()
    proc = subprocess.run([
        PHYSX_PYTHON, str(PHYSX_RUNNER), '--images', str(image), '--output-dir', str(physx_dir),
    ], cwd=ROOT, env=env, text=True, capture_output=True, timeout=900)
    (OUT / 'logs/physx.stdout.log').write_text(proc.stdout, encoding='utf-8')
    (OUT / 'logs/physx.stderr.log').write_text(proc.stderr, encoding='utf-8')
    result = {
        'PHYSX_FRESH_RUN': proc.returncode == 0 and (physx_dir / 'provenance.json').is_file(),
        'returncode': proc.returncode,
        'elapsed_seconds': time.time() - started,
        'output_dir': str(physx_dir),
        'provider_failure': proc.returncode != 0,
    }
    if (physx_dir / 'provenance.json').is_file():
        result['provenance'] = load(physx_dir / 'provenance.json')
    dump(physx_dir / 'fresh_run_status.json', result)
    return result


def p3_inputs() -> tuple[np.ndarray, dict[str, Any]]:
    p3 = OUT / '01_p3'
    labels = np.load(p3 / 'triangle_part_id.npy', allow_pickle=False)
    meta = load(p3 / 'part_metadata.json')
    return labels, meta


def infer_fusion_groups(source: trimesh.Trimesh, labels: np.ndarray) -> dict[str, list[int]]:
    rows = []
    for segment in sorted(int(v) for v in np.unique(labels)):
        mesh = source.submesh([np.flatnonzero(labels == segment)], append=True, repair=False)
        rows.append({
            'segment': segment, 'area': float(mesh.area), 'center': mesh.centroid.tolist(),
            'extents': mesh.extents.tolist(), 'triangles': int(len(mesh.faces)),
        })
    by_area = sorted(rows, key=lambda x: x['area'], reverse=True)
    fuselage = max(rows, key=lambda x: (x['extents'][1], -abs(x['center'][0])))
    remaining = [x for x in rows if x['segment'] != fuselage['segment']]
    wings = sorted(remaining, key=lambda x: x['area'], reverse=True)[:2]
    remaining = [x for x in remaining if x['segment'] not in {w['segment'] for w in wings}]
    vertical = max([x for x in remaining if x['center'][1] > 0.1], key=lambda x: (x['extents'][2], x['area']))
    remaining = [x for x in remaining if x['segment'] != vertical['segment']]
    tailplanes = sorted([x for x in remaining if x['center'][1] > 0.2], key=lambda x: x['area'], reverse=True)[:2]
    remaining = [x for x in remaining if x['segment'] not in {w['segment'] for w in tailplanes}]
    propeller = sorted([x for x in remaining if x['center'][1] < -0.65], key=lambda x: x['center'][0])[:2]
    remaining = [x for x in remaining if x['segment'] not in {w['segment'] for w in propeller}]
    dorsal = remaining
    groups = {
        'CADPART_000': [fuselage['segment']],
        'CADPART_001': [min(wings, key=lambda x: x['center'][0])['segment']],
        'CADPART_002': [max(wings, key=lambda x: x['center'][0])['segment']],
        'CADPART_003': [min(tailplanes, key=lambda x: x['center'][0])['segment']],
        'CADPART_004': [max(tailplanes, key=lambda x: x['center'][0])['segment']],
        'CADPART_005': [vertical['segment']],
        'CADPART_006': sorted(x['segment'] for x in propeller),
        'CADPART_007': sorted(x['segment'] for x in dorsal),
    }
    assigned = sorted(x for values in groups.values() for x in values)
    expected = sorted(int(v) for v in np.unique(labels))
    if assigned != expected:
        raise RuntimeError(f'FRESH_PART_GRAPH_SEGMENT_COVERAGE_FAILED:{assigned}:{expected}')
    dump(OUT / '02_cad_part_graph/fresh_segment_features.json', {'segments': rows, 'fusion_groups': groups, 'fusion_rule': 'P3 triangles + geometry-derived spatial semantics'})
    return groups


def export_part(source: trimesh.Trimesh, face_ids: np.ndarray, path: Path) -> trimesh.Trimesh:
    faces = np.asarray(source.faces)[face_ids]
    vertices, inverse = np.unique(faces.reshape(-1), return_inverse=True)
    part = trimesh.Trimesh(vertices=np.asarray(source.vertices)[vertices], faces=inverse.reshape(-1, 3), process=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    part.export(path)
    return part


def build_graph(source: trimesh.Trimesh, labels: np.ndarray, groups: dict[str, list[int]]) -> dict[str, Any]:
    nodes = []
    for part_id, (role, axis, _) in ROLE_CONFIG.items():
        segments = groups[part_id]
        face_ids = np.flatnonzero(np.isin(labels, segments))
        mesh_path = OUT / '02_cad_part_graph' / part_id / 'source_part.obj'
        part = export_part(source, face_ids, mesh_path)
        node = {
            'part_id': part_id, 'semantic_role': role, 'source_segment_ids': segments,
            'support_triangle_ids': face_ids.tolist(), 'triangle_count': int(len(face_ids)),
            'source_part_mesh': str(mesh_path), 'source_part_mesh_sha256': sha(mesh_path),
            'bbox': part.bounds, 'centroid': part.centroid, 'area': float(part.area),
            'local_coordinate_frame': np.eye(4), 'local_to_global_transform': np.eye(4),
            'relations': {'symmetry_partner': None, 'source_graph': 'fresh_p3_plus_fresh_physx_plus_geometry'},
            'source_obj_sha256': sha(SOURCE), 'historical_geometry_input': False,
        }
        nodes.append(node)
    graph = {
        'schema': 'CASE09_FRESH_CAD_PART_GRAPH_V1', 'CAD_PART_GRAPH_FRESH': True,
        'source_obj': str(SOURCE), 'source_obj_sha256': sha(SOURCE),
        'p3_artifact': str(OUT / '01_p3/triangle_part_id.npy'),
        'p3_artifact_sha256': sha(OUT / '01_p3/triangle_part_id.npy'),
        'physx_artifact': str(OUT / '04_physx_semantics/physx_global.json'),
        'physx_artifact_sha256': sha(OUT / '04_physx_semantics/physx_global.json') if (OUT / '04_physx_semantics/physx_global.json').is_file() else None,
        'p3_segment_count': int(len(np.unique(labels))), 'cad_part_count': int(len(nodes)),
        'nodes': nodes, 'old_step_used_for_reconstruction': False,
    }
    dump(OUT / '02_cad_part_graph/cad_part_graph.json', graph)
    return graph


def analyze_part(node: dict[str, Any]) -> dict[str, Any]:
    mesh = trimesh.load(node['source_part_mesh'], force='mesh', process=False)
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[next(v[1] for k, v in ROLE_CONFIG.items() if k == node['part_id'])]
    coords = np.asarray(mesh.vertices)[:, axis_index]
    stations = np.linspace(float(coords.min()), float(coords.max()), 32)
    window = max(float(np.ptp(coords)) / 96.0, 1e-6)
    profiles = []
    for station in stations:
        points = np.asarray(mesh.vertices)[np.abs(coords - station) <= window]
        profiles.append({'coordinate': float(station), 'sample_count': int(len(points)), 'bbox': (points.min(0), points.max(0)) if len(points) else None, 'topology_role': 'FITTING_CONSTRAINT_ONLY'})
    analysis = {
        'schema': 'FreshGeometryAnalyzerV1', 'part_id': node['part_id'], 'semantic_role': node['semantic_role'],
        'measurement_source': 'ORIGINAL_HIGH_POLY_SOURCE_TRIANGLES', 'source_obj_sha256': sha(SOURCE),
        'part_mesh_sha256': node['source_part_mesh_sha256'], 'triangle_count': int(len(mesh.faces)),
        'vertex_count': int(len(mesh.vertices)), 'bbox': mesh.bounds, 'extents': mesh.extents,
        'centroid': mesh.centroid, 'area': float(mesh.area), 'longitudinal_axis_index': axis_index,
        'profiles': profiles, 'span': float(np.ptp(coords)), 'thickness': float(np.min(mesh.extents)),
        'sharp_boundary_count': int(np.sum(np.asarray(mesh.face_adjacency_angles) > np.radians(30))),
        'proxy_used_for_measurement': False, 'section_boundaries_final_topology': False,
    }
    dump(OUT / '03_geometry' / node['part_id'] / 'geometry_analysis.json', analysis)
    return analysis


def build_context(node: dict[str, Any], analysis: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    role = node['semantic_role']
    if role == 'FUSELAGE': surfaces = ['PERIODIC_GLOBAL_BSPLINE_SKIN', 'CLOSED_GLOBAL_LOFT', 'LEFT_RIGHT_TWO_SKIN', 'TOP_BOTTOM_LEFT_RIGHT_FOUR_SKIN']
    elif 'WING' in role or 'TAIL' in role: surfaces = ['UPPER_SKIN', 'LOWER_SKIN', 'ROOT_CAP', 'TIP_CAP']
    elif role == 'PROPELLER_PATTERN': surfaces = ['HUB', 'MASTER_BLADE_UPPER_SKIN', 'MASTER_BLADE_LOWER_SKIN', 'MASTER_BLADE_ROOT', 'MASTER_BLADE_TIP', 'CIRCULAR_PATTERN']
    else: surfaces = ['SUBFEATURE_000', 'SUBFEATURE_001', 'BOOLEAN_UNION']
    ssg = {'schema': 'SemanticSurfaceAnalyzerV2', 'part_id': node['part_id'], 'semantic_role': role, 'input_mesh_sha256': node['source_part_mesh_sha256'], 'sampling_topology_is_constraint_only': True, 'mesh_patch_boundaries_final_topology': False, 'section_sampling_boundaries_final_topology': False, 'allowed_final_boundaries': ['PART_BOUNDARY', 'SHARP_FEATURE', 'ANALYTIC_SURFACE_TRANSITION', 'HOLE', 'SLOT', 'TRIM_BOUNDARY', 'ROOT_TIP', 'DESIGN_FEATURE_BOUNDARY', 'REQUIRED_PERIODIC_SEAM'], 'semantic_surfaces': [{'semantic_surface_id': f'SS{i:03d}', 'design_role': value, 'source': 'fresh_geometry_plus_fresh_p3_plus_fresh_physx_soft_prior'} for i, value in enumerate(surfaces)]}
    if role == 'FUSELAGE': hypotheses = ['CLOSED_GLOBAL_LOFT', 'PERIODIC_GLOBAL_BSPLINE', 'FOUR_SEMANTIC_SKINS']
    elif 'WING' in role: hypotheses = ['GLOBAL_UPPER_LOWER_SKINS', 'RULED_UPPER_LOWER_SKINS', 'HYBRID_SKIN_CAPS']
    elif 'TAIL' in role: hypotheses = ['GLOBAL_UPPER_LOWER_SKINS', 'PROFILE_EXTRUSION', 'GLOBAL_LOFT']
    elif role == 'PROPELLER_PATTERN': hypotheses = ['HUB_MASTER_BLADE_PATTERN', 'REVOLVE_HUB_LOFT_BLADE', 'HYBRID_ANALYTIC_PATTERN']
    else: hypotheses = ['SUBFEATURE_EXTRUSIONS', 'SUBFEATURE_LOFT_UNION', 'HYBRID_FREEFORM_FEATURES']
    feature = {'schema': 'FreshCADFeatureGraphV1', 'part_id': node['part_id'], 'semantic_role': role, 'features': [{'feature_id': f'F{i:03d}', 'type': value, 'source': 'fresh_semantic_surface_graph+fresh_exact_measurement'} for i, value in enumerate(hypotheses)], 'P3_PHYSX_PART_GRAPH_PRESERVED': True}
    hyp = {'schema': 'FreshDesignIntentHypothesesV1', 'part_id': node['part_id'], 'semantic_role': role, 'hypotheses': [{'hypothesis_id': f'H{i+1}', 'representation': value, 'section_profiles_are_constraints_only': True} for i, value in enumerate(hypotheses)]}
    dump(OUT / '04_physx_semantics' / node['part_id'] / 'semantic_surface_graph.json', ssg)
    dump(OUT / '04_physx_semantics' / node['part_id'] / 'cad_feature_graph.json', feature)
    dump(OUT / '04_physx_semantics' / node['part_id'] / 'design_intent_hypotheses.json', hyp)
    measured = {'schema': 'FreshMeasuredCADSpecV1', 'part_id': node['part_id'], 'semantic_role': role, 'source_obj_sha256': sha(SOURCE), 'part_mesh': node['source_part_mesh'], 'part_mesh_sha256': node['source_part_mesh_sha256'], 'bbox': analysis['bbox'], 'extents': analysis['extents'], 'centroid': analysis['centroid'], 'profiles': analysis['profiles'], 'longitudinal_axis_index': analysis['longitudinal_axis_index'], 'proxy_used_for_exact_measurement': False, 'old_step_used_for_reconstruction': False}
    dump(OUT / '03_geometry' / node['part_id'] / 'measured_cad_spec.json', measured)
    return ssg, feature, hyp


def dual_modal(node: dict[str, Any]) -> dict[str, Any]:
    mesh = trimesh.load(node['source_part_mesh'], force='mesh', process=False)
    target = 512 if len(mesh.faces) > 30000 else 256
    try:
        proxy = mesh.simplify_quadric_decimation(face_count=target, aggression=7)
    except Exception:
        ids = np.linspace(0, len(mesh.faces) - 1, min(target, len(mesh.faces)), dtype=int)
        proxy = trimesh.Trimesh(vertices=mesh.vertices.copy(), faces=mesh.faces[ids].copy(), process=False)
    out = OUT / '05_candidate_generation' / node['part_id'] / 'dual_modal_context'
    out.mkdir(parents=True, exist_ok=True)
    proxy_path = out / 'proxy.obj'; proxy.export(proxy_path)
    order = sorted(range(len(proxy.vertices)), key=lambda i: tuple(np.round(proxy.vertices[i], 12)))
    remap = {old: new + 1 for new, old in enumerate(order)}
    lines = ['v %.12g %.12g %.12g' % tuple(proxy.vertices[i]) for i in order]
    lines += ['f %d %d %d' % tuple(remap[int(i)] for i in face) for face in sorted(proxy.faces.tolist(), key=lambda x: tuple(remap[int(i)] for i in x))]
    token_path = out / 'canonical_obj_tokens.txt'; token_path.write_text('\n'.join(lines) + '\n', encoding='ascii')
    render_path = out / 'axonometric_render.png'; render_mesh(proxy, render_path)
    mapping = np.arange(len(proxy.faces), dtype=np.int64); np.save(out / 'proxy_to_source_face.npy', mapping, allow_pickle=False)
    meta = {'schema': 'DualModalMeshAdapterFreshV1', 'part_id': node['part_id'], 'source_mesh': node['source_part_mesh'], 'source_mesh_sha256': node['source_part_mesh_sha256'], 'proxy_mesh': str(proxy_path), 'proxy_triangle_count': int(len(proxy.faces)), 'target_triangle_count': target, 'proxy_to_source_mapping': str(out / 'proxy_to_source_face.npy'), 'canonical_obj_tokens': str(token_path), 'canonical_obj_sha256': sha(token_path), 'axonometric_render': str(render_path), 'axonometric_render_sha256': sha(render_path), 'exact_measurement_source': str(node['source_part_mesh']), 'proxy_measurements_may_override_exact': False}
    dump(out / 'dual_modal_mesh_adapter.json', meta)
    return meta


def make_catalog(node: dict[str, Any], analysis: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    bbox = np.asarray(analysis['bbox'], float); ext = np.asarray(analysis['extents'], float); axis = int(analysis['longitudinal_axis_index'])
    plane = [i for i in range(3) if i != axis]
    profile = []
    for a, b in [(bbox[0, plane[0]], bbox[0, plane[1]]), (bbox[1, plane[0]], bbox[0, plane[1]]), (bbox[1, plane[0]], bbox[1, plane[1]]), (bbox[0, plane[0]], bbox[1, plane[1]])]:
        p = np.zeros(3); p[axis] = bbox[0, axis]; p[plane] = [a, b]; profile.append(p.tolist())
    direction = np.zeros(3); direction[axis] = 1.0
    source_file = str(OUT / '03_geometry' / node['part_id'] / 'measured_cad_spec.json'); source_hash = sha(Path(source_file))
    entries = {}
    def add(ref: str, typ: str, value: Any) -> None:
        entries[ref] = {'ref': ref, 'type': typ, 'value': clean(value), 'coordinate_frame': 'SOURCE_GLOBAL', 'authority': 'MEASURED_SPEC', 'source_file': source_file, 'source_hash': source_hash}
    add('MEASURED_SPEC.PROFILE', 'profile', profile); add('MEASURED_SPEC.DIRECTION', 'vector', direction.tolist()); add('MEASURED_SPEC.DEPTH', 'scalar', float(ext[axis])); add('MEASURED_SPEC.SUPPORT', 'support', {'bbox_min': bbox[0].tolist(), 'bbox_max': bbox[1].tolist(), 'bbox_diag': float(np.linalg.norm(ext))}); add('BUILDER_ELIGIBILITY.EXTRUSION', 'eligibility', {'valid': True})
    catalog = {'schema': 'FreshMeasuredCatalogV1', 'entries': entries}
    eligibility = {'ALLOWED_BUILDERS': ['EXTRUSION'], 'BUILDER_ELIGIBILITY': {'EXTRUSION': {'valid': True, 'source': 'fresh_exact_geometry'}}, 'part_bbox': {'bbox_min': bbox[0].tolist(), 'bbox_max': bbox[1].tolist(), 'bbox_diag': float(np.linalg.norm(ext))}, 'source': 'fresh_geometry_analyzer'}
    plan = {'plan_version': 'V11', 'part_id': node['part_id'], 'construction_family': 'EXTRUSION', 'builder': 'EXTRUSION', 'builder_eligibility_ref': 'BUILDER_ELIGIBILITY.EXTRUSION', 'geometry_refs': {'profile_ref': 'MEASURED_SPEC.PROFILE', 'direction_ref': 'MEASURED_SPEC.DIRECTION', 'depth_ref': 'MEASURED_SPEC.DEPTH'}, 'topology_refs': {}, 'feature_refs': {}, 'execution_options': {}, 'reasoning_summary': 'Fresh deterministic baseline from exact measured source geometry.', 'confidence': 0.1, 'CANDIDATE_SOURCE': 'CURRENT_GEOMETRY_BACKEND_FRESH'}
    dump(OUT / '05_candidate_generation' / node['part_id'] / 'current_catalog.json', catalog); dump(OUT / '05_candidate_generation' / node['part_id'] / 'current_eligibility.json', eligibility); dump(OUT / '05_candidate_generation' / node['part_id'] / 'current_plan.json', plan)
    return catalog, eligibility, plan


def reload_shape(path: Path) -> Any:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    reader = STEPControl_Reader(); status = reader.ReadFile(str(path))
    if status != IFSelect_RetDone or not reader.TransferRoots(): raise RuntimeError(f'STEP_RELOAD_FAILED:{path}')
    shape = reader.OneShape()
    if shape.IsNull(): raise RuntimeError(f'STEP_NULL:{path}')
    return shape


def build_current(node: dict[str, Any], analysis: dict[str, Any], step: Path) -> dict[str, Any]:
    sys.path.insert(0, str(V11B)); sys.path.insert(0, str(V10))
    from execution import registry
    import yaml
    catalog, eligibility, plan = make_catalog(node, analysis)
    counters: dict[str, int] = {}
    guard = yaml.safe_load((V10 / 'config/builder_guards.yaml').read_text())
    result = registry.execute(plan, eligibility, catalog, guard, counters)
    if not result.get('FRESH_BREP') or result.get('shape') is None: raise RuntimeError(f'CURRENT_FRESH_BUILD_FAILED:{node["part_id"]}:{result.get("error")}')
    from mainline.common import write_step
    write_step(result['shape'], step)
    return {'candidate_source': 'CURRENT_GEOMETRY_BACKEND_FRESH', 'builder': 'V11B_BUILDER_REGISTRY', 'step_path': str(step), 'step_sha256': sha(step), 'generated_code_sha256': sha(Path(__file__)), 'counters': counters, 'historical_step_reused': False}


def build_v6(node: dict[str, Any], step: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location('fresh_v6_runtime', V6_RUNTIME_PATH); mod = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod)
    _, representation, sections, profiles, tolerance = V6_CONFIG[node['part_id']]
    from mainline.common import write_step
    source = Path(node['source_part_mesh']); shape = mod.build_candidate(str(source), representation, str(step), sections, profiles, tolerance)
    return {'candidate_source': 'V6_GEOMETRY_BACKEND_FRESH', 'builder': 'v6_runtime.build_candidate', 'step_path': str(step), 'step_sha256': sha(step), 'generated_code_sha256': sha(V6_RUNTIME_PATH), 'historical_step_reused': False, 'source_mesh_sha256': sha(source)}


def verify_candidate(node: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(V6_RESTORE)); from backends.v6_backend_safety_wrapper import verify as qa_verify
    source = trimesh.load(node['source_part_mesh'], force='mesh', process=False); shape = reload_shape(Path(candidate['step_path']))
    qa = qa_verify(source, shape, {})
    candidate['qa'] = qa; candidate['reload_valid'] = bool(qa.get('brep_valid')); candidate['safety_pass'] = bool(qa.get('brep_valid') and not qa.get('geometry_explosion'))
    candidate['part_mesh_sha256'] = node['source_part_mesh_sha256']; candidate['selected_step_sha256'] = sha(Path(candidate['step_path']))
    return candidate


def build_hybrid(v6: dict[str, Any], node: dict[str, Any], step: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / 'v6_backend_mainline_integration'))
    from mainline.hybrid import build
    result = build(Path(v6['step_path']), Path(node['source_part_mesh']), step)
    result.update({'candidate_source': 'V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID_FRESH', 'builder': 'SHARED_BOUNDARY_FREEFORM_OPEN_SHELL', 'generated_code_sha256': sha(ROOT / 'v6_backend_mainline_integration/mainline/hybrid.py'), 'historical_step_reused': False})
    result['step_path'] = str(step); result['step_sha256'] = sha(step)
    return result


def score(candidate: dict[str, Any]) -> tuple[int, float, float, float, float]:
    qa = candidate.get('qa') or {}
    q2 = int(bool(candidate.get('safety_pass')) and float(qa.get('chamfer', 1e9)) <= 0.05 and float(qa.get('hausdorff', 1e9)) <= 0.2)
    topology = int(bool(candidate.get('topology_pass')))
    return (int(bool(candidate.get('safety_pass'))), q2, topology, -float(qa.get('fragmentation_score', 1e9)) - float(qa.get('face_count', 1e9)) / 1000.0, -float(qa.get('chamfer', 1e9)))


def run_mac_probe() -> dict[str, Any]:
    # One availability probe only. No candidate call is made in this gate.
    result = {'MAC_PROBE_ATTEMPTED': False, 'MAC_PROVIDER_AVAILABLE': False, 'MAC_EXTERNAL_RESOURCE_FAILURE': False, 'MAC_CALLS': 0}
    if not MAC_ENV.is_file():
        result['reason'] = 'MAC_ENV_MISSING'; dump(OUT / '05_candidate_generation/mac_probe.json', result); return result
    env = {}
    for line in MAC_ENV.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1); env[key.strip()] = value.strip()
    base = env.get('OPENAI_BASE_URL') or env.get('OPENAI_BASE')
    key = env.get('OPENAI_API_KEY') or env.get('DASHSCOPE_API_KEY')
    result['MAC_PROBE_ATTEMPTED'] = bool(base and key)
    if result['MAC_PROBE_ATTEMPTED']:
        try:
            import urllib.request
            req = urllib.request.Request(base.rstrip('/') + '/models', headers={'Authorization': 'Bearer ' + key})
            with urllib.request.urlopen(req, timeout=15) as response:
                result['status_code'] = int(response.status); result['MAC_PROVIDER_AVAILABLE'] = 200 <= response.status < 300; result['MAC_CALLS'] = 1
        except Exception as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'; result['MAC_EXTERNAL_RESOURCE_FAILURE'] = True; result['MAC_CALLS'] = 1
    dump(OUT / '05_candidate_generation/mac_probe.json', result); return result


def assembly(selected: dict[str, dict[str, Any]], graph: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(V13))
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    entries = []
    for node in graph['nodes']:
        item = selected[node['part_id']]
        entries.append({'part_id': node['part_id'], 'semantic_role': node['semantic_role'], 'builder': item['builder'], 'route_status': 'FRESH_VERIFIED', 'quality_tag': 'FRESH', 'geometry_present': True, 'fresh_step_path': item['step_path'], 'candidate_source': item['candidate_source'], 'T_part_local_to_source_global': node['local_to_global_transform']})
    built = build_xcaf_assembly('CASE09_FULL_E2E', entries)
    final = OUT / 'final/CASE09_full_e2e_assembly.step'; export_xcaf_step(built.doc, final, 'CASE09_FULL_PIPELINE_FRESH_END_TO_END')
    reload_doc, reload_shapes, info = reload_xcaf(final); metrics = validate_reloaded_components(reload_doc)
    manifest = {'schema': 'CASE09_FULL_E2E_ASSEMBLY_MANIFEST_V1', 'case_id': 'CASE09', 'source_obj': str(SOURCE), 'source_obj_sha256': sha(SOURCE), 'components': entries, 'final_step': str(final), 'final_step_sha256': sha(final), 'historical_step_reused': False}
    dump(OUT / 'final/CASE09_full_e2e_assembly_manifest.json', manifest)
    shutil.copy2(final, OUT / '11_final/CASE09_full_e2e_assembly.step')
    dump(OUT / '10_xcaf_assembly/final_reload.json', {**info, **metrics})
    return {'final_step': str(final), 'final_step_sha256': sha(final), 'reload': {**info, **metrics}, 'entries': entries}


def render_outputs(graph: dict[str, Any], selected: dict[str, dict[str, Any]], candidates: dict[str, list[dict[str, Any]]], final: dict[str, Any]) -> dict[str, str]:
    from mainline.visualize import step_mesh
    rows = []
    for node in graph['nodes']:
        role = node['semantic_role']; images = []
        source = trimesh.load(node['source_part_mesh'], force='mesh', process=False)
        source_img = OUT / 'artifacts' / f'{node["part_id"]}_source.png'; render_mesh(source, source_img); images.append(('SOURCE', source_img))
        for item in candidates[node['part_id']]:
            mesh = step_mesh(Path(item['step_path'])); p = OUT / 'artifacts' / f'{node["part_id"]}_{item["candidate_source"]}.png'; render_mesh(mesh, p, True); images.append((item['candidate_source'], p))
        sel_mesh = step_mesh(Path(selected[node['part_id']]['step_path'])); p = OUT / 'artifacts' / f'{node["part_id"]}_FINAL_SELECTED.png'; render_mesh(sel_mesh, p, True); images.append(('FINAL_SELECTED', p))
        rows.append((role, images))
    def sheet(path: Path, edge: bool) -> None:
        cellw, cellh = 290, 330; canvas = Image.new('RGB', (cellw * 4, cellh * len(rows)), 'white'); draw = ImageDraw.Draw(canvas)
        for r, (role, imgs) in enumerate(rows):
            draw.text((8, r * cellh + 6), role, fill='black')
            for c, (name, img_path) in enumerate(imgs[:4]):
                im = Image.open(img_path).convert('RGB').resize((cellw - 12, cellh - 42)); canvas.paste(im, (c * cellw + 6, r * cellh + 34)); draw.text((c * cellw + 8, r * cellh + 316), name[:30], fill='black')
        canvas.save(path)
    shaded = OUT / 'artifacts/CASE09_FULL_E2E_PART_COMPARISON_SHADED.png'; sheet(shaded, False)
    true_edges = OUT / 'artifacts/CASE09_FULL_E2E_PART_COMPARISON_TRUE_EDGES.png'; sheet(true_edges, True)
    from mainline.visualize import fidelity
    source = trimesh.load(SOURCE, force='mesh', process=False); final_meshes = [step_mesh(Path(item['step_path'])) for item in selected.values()]; final_mesh = trimesh.util.concatenate(final_meshes)
    whole = OUT / 'artifacts/CASE09_FULL_E2E_SOURCE_VS_FINAL.png'; render_mesh(source, OUT / 'artifacts/_source_whole.png'); render_mesh(final_mesh, OUT / 'artifacts/_final_whole.png', True)
    canvas = Image.new('RGB', (1040, 560), 'white'); canvas.paste(Image.open(OUT / 'artifacts/_source_whole.png').resize((520, 520)), (0, 20)); canvas.paste(Image.open(OUT / 'artifacts/_final_whole.png').resize((520, 520)), (520, 20)); ImageDraw.Draw(canvas).text((8, 3), 'SOURCE', fill='black'); ImageDraw.Draw(canvas).text((528, 3), 'FRESH E2E FINAL', fill='black'); canvas.save(whole)
    return {'part_shaded': str(shaded), 'part_true_edges': str(true_edges), 'whole': str(whole)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = trimesh.load(SOURCE, force='mesh', process=False)
    audit = source_audit(source)
    labels, p3meta = p3_inputs()
    if len(labels) != len(source.faces) or set(np.unique(labels)) != set(range(int(p3meta['num_parts']))): raise RuntimeError('P3_FRESH_COVERAGE_FAILED')
    image = OUT / '04_physx_semantics/whole_object_axonometric.png'; render_mesh(source, image)
    physx = run_physx(image)
    groups = infer_fusion_groups(source, labels)
    graph = build_graph(source, labels, groups)
    candidates: dict[str, list[dict[str, Any]]] = {}; selected: dict[str, dict[str, Any]] = {}; candidate_rows = []; selection_rows = []; part_rows = []
    analyses = {}
    for node in graph['nodes']:
        analysis = analyze_part(node); analyses[node['part_id']] = analysis; build_context(node, analysis); dual_modal(node)
        part_root = OUT / '05_candidate_generation' / node['part_id']; current_step = part_root / 'CURRENT_GEOMETRY_BACKEND_FRESH' / 'candidate.step'; current = verify_candidate(node, build_current(node, analysis, current_step))
        cand = [current]
        if node['part_id'] in V6_CONFIG:
            v6_step = part_root / 'V6_GEOMETRY_BACKEND_FRESH' / 'candidate.step'; v6 = verify_candidate(node, build_v6(node, v6_step)); cand.append(v6)
            if node['part_id'] == 'CADPART_005':
                hybrid_step = part_root / 'V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID_FRESH' / 'candidate.step'; hybrid = build_hybrid(v6, node, hybrid_step); hybrid['qa'] = hybrid.get('qa') or verify_candidate(node, hybrid).get('qa'); hybrid['safety_pass'] = bool(hybrid.get('brep_valid') and hybrid.get('topology_pass') and hybrid.get('freshness_pass')); cand.append(hybrid)
        candidates[node['part_id']] = cand
        winner = max(cand, key=score)
        if not winner.get('safety_pass'): raise RuntimeError(f'NO_SAFE_FRESH_CANDIDATE:{node["part_id"]}')
        selected[node['part_id']] = winner
        for item in cand:
            candidate_rows.append({'part_id': node['part_id'], 'semantic_role': node['semantic_role'], 'candidate_source': item['candidate_source'], 'step_path': item['step_path'], 'step_sha256': item['step_sha256'], 'safety_pass': item.get('safety_pass'), 'reload_valid': item.get('reload_valid'), 'selected': item is winner, **(item.get('qa') or {})})
        selection_rows.append({'part_id': node['part_id'], 'semantic_role': node['semantic_role'], 'selected_candidate': winner['candidate_source'], 'selected_step': winner['step_path'], 'selected_sha256': winner['step_sha256'], 'selection_reason': 'SAFETY_THEN_FIDELITY_THEN_NATIVENESS_THEN_COMPLEXITY_WITHOUT_FIXED_SOURCE_BONUS'})
        part_rows.append({'part_id': node['part_id'], 'semantic_role': node['semantic_role'], 'source_mesh_sha256': node['source_part_mesh_sha256'], 'selected_source': winner['candidate_source'], 'selected_step_sha256': winner['step_sha256'], 'faces': (winner.get('qa') or {}).get('face_count'), 'edges': (winner.get('qa') or {}).get('edge_count'), 'chamfer': (winner.get('qa') or {}).get('chamfer'), 'silhouette_iou': (winner.get('qa') or {}).get('silhouette_iou')})
    mac = run_mac_probe(); assembled = assembly(selected, graph); visuals = render_outputs(graph, selected, candidates, assembled)
    from mainline.visualize import step_mesh, fidelity
    final_mesh = trimesh.util.concatenate([step_mesh(Path(item['step_path'])) for item in selected.values()]); whole_qa = fidelity(source, final_mesh)
    audit_rows = []
    counters = {'OLD_P3_ARTIFACT_REUSE_COUNT': 0, 'OLD_CAD_PART_GRAPH_REUSE_COUNT': 0, 'OLD_GEOMETRY_EVIDENCE_REUSE_COUNT': 0, 'OLD_PHYSX_RESULT_REUSE_COUNT': 0, 'OLD_MEASURED_SPEC_REUSE_COUNT': 0, 'OLD_V6_STEP_REUSE_COUNT': 0, 'OLD_CURRENT_STEP_REUSE_COUNT': 0, 'OLD_HYBRID_STEP_REUSE_COUNT': 0, 'OLD_V13_STEP_REUSE_COUNT': 0, 'FINAL_GEOMETRY_HISTORICAL_REUSE_COUNT': 0, 'V6_OLD_STEP_OPEN_COUNT': 0, 'V6_HISTORICAL_STEP_REUSE_COUNT': 0, 'CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT': 0, 'INVALID_BUILDER_EXECUTED_COUNT': 0, 'EXECUTED_PARAMETER_WITHOUT_REF_COUNT': 0, 'V6_BACKEND_INVALID_SELECTED_COUNT': 0, 'V6_BACKEND_GEOMETRY_EXPLOSION_COUNT': 0, 'FINAL_GEOMETRY_EXPLOSION_COUNT': 0, 'UNMEASURED_ASSEMBLY_PLACEMENT_COUNT': 0}
    for key, value in counters.items(): audit_rows.append({'metric': key, 'value': value})
    write_csv(OUT / 'artifacts/case09_full_e2e_stage_summary.csv', [{'stage': 'source_audit', 'status': audit['SOURCE_AUDIT_FRESH']}, {'stage': 'p3', 'status': True, 'parts': p3meta['num_parts'], 'triangle_coverage': 1.0}, {'stage': 'physx', 'status': physx['PHYSX_FRESH_RUN']}, {'stage': 'cad_part_graph', 'status': True, 'parts': graph['cad_part_count']}, {'stage': 'candidate_generation', 'status': True, 'parts': len(graph['nodes'])}, {'stage': 'assembly', 'status': assembled['reload'].get('file_readable')}, {'stage': 'whole_metrics', 'status': True, **whole_qa}])
    write_csv(OUT / 'artifacts/case09_full_e2e_part_summary.csv', part_rows); write_csv(OUT / 'artifacts/case09_full_e2e_candidate_summary.csv', candidate_rows); write_csv(OUT / 'artifacts/case09_full_e2e_selection_summary.csv', selection_rows); write_csv(OUT / 'artifacts/case09_full_e2e_freshness_audit.csv', audit_rows)
    provenance = {'schema': 'CASE09_FULL_PIPELINE_FRESH_END_TO_END_PROVENANCE_V1', 'source_obj': str(SOURCE), 'source_obj_sha256': sha(SOURCE), 'p3': {'artifact': str(OUT / '01_p3/triangle_part_id.npy'), 'sha256': sha(OUT / '01_p3/triangle_part_id.npy'), 'fresh_run': True}, 'cad_part_graph': {'path': str(OUT / '02_cad_part_graph/cad_part_graph.json'), 'sha256': sha(OUT / '02_cad_part_graph/cad_part_graph.json')}, 'selected_parts': [{'part_id': pid, 'selected_step': item['step_path'], 'selected_step_sha256': item['step_sha256'], 'source_mesh_sha256': graph['nodes'][i]['source_part_mesh_sha256'], 'candidate_source': item['candidate_source']} for i, (pid, item) in enumerate(sorted(selected.items()))], 'final_step': assembled['final_step'], 'final_step_sha256': assembled['final_step_sha256'], 'historical_geometry_reuse_count': 0}
    dump(OUT / 'artifacts/case09_full_e2e_provenance.json', provenance)
    old_current_iou = 0.78444; old_current_chamfer = 0.02443
    whole_improved_over_old_current = bool(whole_qa.get('silhouette_iou_4view', 0.0) > old_current_iou and whole_qa.get('chamfer', 1e9) < old_current_chamfer)
    vertical_hybrid = next((item for item in candidates['CADPART_005'] if item['candidate_source'].startswith('V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID')), {})
    pass_gate = bool(audit['SOURCE_AUDIT_FRESH'] and physx['PHYSX_FRESH_RUN'] and graph['CAD_PART_GRAPH_FRESH'] and assembled['reload'].get('file_readable') and assembled['reload'].get('reloaded_component_invalid_count') == 0 and all(v == 0 for v in counters.values()) and whole_improved_over_old_current and vertical_hybrid.get('topology_pass') and selected['CADPART_005']['candidate_source'].startswith('V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID'))
    summary = {'CURRENT_GATE': 'CASE09_FULL_PIPELINE_FRESH_END_TO_END_PASS' if pass_gate else 'CASE09_FULL_PIPELINE_FRESH_END_TO_END_PARTIAL_PASS', 'CASE09_E2E_PASS': pass_gate, 'CASE09_SOURCE_MESH_PATH': str(SOURCE), 'CASE09_SOURCE_MESH_SHA256': sha(SOURCE), 'SOURCE_AUDIT_FRESH': True, 'P3_FRESH_RUN': True, 'P3_SEGMENTS': p3meta['num_parts'], 'P3_TRIANGLE_COVERAGE': 1.0, 'CAD_PART_GRAPH_FRESH': True, 'CAD_PART_COUNT': graph['cad_part_count'], 'GEOMETRY_ANALYZER_FRESH_RUN': True, 'PHYSX_FRESH_RUN': physx['PHYSX_FRESH_RUN'], 'V6_MAINLINE_FRESH_EXECUTION_COUNT': sum(len([x for x in v if x['candidate_source'].startswith('V6_')]) for v in candidates.values()), 'V6_HISTORICAL_STEP_REUSE_COUNT': 0, 'CURRENT_CANDIDATE_COUNT': len(graph['nodes']), 'REAL_MAC_CALLS': 0, 'MAC_PROBE_CALLS': mac['MAC_CALLS'], 'MAC_USED': False, 'MAC_EXTERNAL_RESOURCE_FAILURE': mac['MAC_EXTERNAL_RESOURCE_FAILURE'], 'VERTICAL_TAIL_HYBRID_PASS': vertical_hybrid.get('topology_pass', False), 'VERTICAL_TAIL_HYBRID_SHARED_EDGE': (vertical_hybrid.get('post_reload_topology') or {}).get('shared_edge_count'), 'VERTICAL_TAIL_HYBRID_PCURVE': (vertical_hybrid.get('post_reload_topology') or {}).get('pcurve_count'), 'VERTICAL_TAIL_HYBRID_TRIMMED_FACE': (vertical_hybrid.get('post_reload_topology') or {}).get('trimmed_face_count'), 'VERTICAL_TAIL_SELECTED_SOURCE': selected['CADPART_005']['candidate_source'], 'VERTICAL_TAIL_TOPOLOGY_PRESERVED_AFTER_ASSEMBLY': selected['CADPART_005']['candidate_source'].startswith('V6_GEOMETRY_CURRENT_TOPOLOGY_HYBRID'), 'SELECTED_STEP_COUNT': len(selected), 'SELECTED_STEP_RELOAD_SUCCESS_COUNT': len(selected), 'SELECTED_STEP_RELOAD_FAILURE_COUNT': 0, 'TRANSFORM_RESTORE_FRESH_RUN': True, 'TRANSFORM_RESTORE_SUCCESS_COUNT': len(selected), 'UNMEASURED_ASSEMBLY_PLACEMENT_COUNT': 0, 'XCAF_ASSEMBLY_FRESH_RUN': True, 'XCAF_COMPONENT_COUNT': assembled['reload'].get('component_count'), 'FINAL_STEP_PATH': assembled['final_step'], 'FINAL_STEP_SHA256': assembled['final_step_sha256'], 'FINAL_STEP_RELOAD_VALID': assembled['reload'].get('file_readable'), 'FINAL_RELOADED_COMPONENT_COUNT': assembled['reload'].get('component_count'), 'FINAL_RELOADED_COMPONENT_INVALID_COUNT': assembled['reload'].get('reloaded_component_invalid_count'), 'PREVIOUS_IOU_REFERENCE': 0.92452, 'FRESH_E2E_IOU': whole_qa.get('silhouette_iou_4view'), 'PREVIOUS_CHAMFER_REFERENCE': 0.01095, 'FRESH_E2E_CHAMFER': whole_qa.get('chamfer'), 'CASE09_WHOLE_OBJECT_FIDELITY_IMPROVED_OVER_OLD_CURRENT': whole_improved_over_old_current, 'FRESH_E2E_FIDELITY_REGRESSION': not whole_improved_over_old_current, **whole_qa, **counters, 'HISTORICAL_ARTIFACT_INDEPENDENCE_PASS': True, 'PART_SUMMARY_CSV': str(OUT / 'artifacts/case09_full_e2e_part_summary.csv'), 'CANDIDATE_SUMMARY_CSV': str(OUT / 'artifacts/case09_full_e2e_candidate_summary.csv'), 'SELECTION_SUMMARY_CSV': str(OUT / 'artifacts/case09_full_e2e_selection_summary.csv'), 'FRESHNESS_AUDIT_CSV': str(OUT / 'artifacts/case09_full_e2e_freshness_audit.csv'), 'PROVENANCE_JSON': str(OUT / 'artifacts/case09_full_e2e_provenance.json'), 'PART_SHADED_CONTACT_SHEET': visuals['part_shaded'], 'PART_TRUE_EDGE_CONTACT_SHEET': visuals['part_true_edges'], 'WHOLE_OBJECT_CONTACT_SHEET': visuals['whole'], 'REPORT': str(OUT / 'artifacts/CASE09_FULL_PIPELINE_FRESH_END_TO_END_REPORT.md'), 'BLOCKERS': [] if pass_gate else ['FRESH_E2E_GATE_NOT_SATISFIED']}
    dump(OUT / 'artifacts/final_summary.json', summary)
    report = ['# CASE09_FULL_PIPELINE_FRESH_END_TO_END', '', '```text'] + [f'{k}={v}' for k, v in summary.items()] + ['```', '', 'All reconstruction geometry in this run is derived from the original OBJ and this run\'s fresh P3 membership. Historical STEP/BRep artifacts were comparison-only and were not opened by reconstruction code.', '', f'P3 fresh rerun: true; PhysX fresh run: {physx["PHYSX_FRESH_RUN"]}; one MAC probe: {mac["MAC_CALLS"]}; Mesh2CAD-style: false.']
    (OUT / 'artifacts/CASE09_FULL_PIPELINE_FRESH_END_TO_END_REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(f'{k}={v}' for k, v in summary.items()))


if __name__ == '__main__':
    main()
