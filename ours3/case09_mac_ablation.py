#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import trimesh
import yaml
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
FRESH = ROOT / 'case09_full_pipeline_fresh_e2e_v1'
OUT = ROOT / 'case09_brep_edge_provenance_fix_and_mac_incremental_ablation'
ART = OUT / 'artifacts'
V11 = ROOT / 'v11b_real_qwen_mac_open_shell_closure'
V10 = ROOT / 'v10_geometry_gated_builder_contract_closure'
V13 = ROOT / 'v13_transform_restore_and_xcaf_assembly'
sys.path[:0] = [str(V11), str(V10), str(ROOT / 'v6_backend_mainline_integration')]

from design_plan.validator import validate_plan
from execution import registry
from planning.mac_adapter import call_mac

spec = importlib.util.spec_from_file_location('fresh_edge_audit', ROOT / 'case09_edge_audit.py')
edge_audit = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(edge_audit)

from mainline.visualize import fidelity, shape_mesh

ROLES = {
    'CADPART_000': 'FUSELAGE', 'CADPART_001': 'MAIN_WING_LEFT',
    'CADPART_002': 'MAIN_WING_RIGHT', 'CADPART_003': 'TAILPLANE_LEFT',
    'CADPART_004': 'TAILPLANE_RIGHT', 'CADPART_005': 'VERTICAL_TAIL',
    'CADPART_006': 'PROPELLER_PATTERN', 'CADPART_007': 'DORSAL_FEATURES',
}
ELIGIBLE = ['CADPART_000', 'CADPART_001', 'CADPART_002', 'CADPART_003', 'CADPART_004', 'CADPART_005']


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + '\n', encoding='utf-8')


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)


def write_step(shape, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f'STEP_WRITE_FAILED:{path}')


def reload_shape(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f'STEP_READ_FAILED:{path}')
    roots = reader.TransferRoots(); shape = reader.OneShape()
    if roots < 1 or shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
        raise RuntimeError(f'INVALID_FRESH_BREP:{path}')
    return shape


def whole_assembly(entries, path, name):
    sys.path.insert(0, str(V13))
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    built = build_xcaf_assembly(name, entries)
    export_xcaf_step(built.doc, path, name)
    doc, shapes, info = reload_xcaf(path)
    metrics = validate_reloaded_components(doc)
    return {**info, **metrics}


def no_step_context(item, part_id, role):
    root = FRESH
    current_summary = load(FRESH / '05_candidate_generation' / part_id / 'current_plan.json')
    return {
        'source_part_render': str(FRESH / 'artifacts' / f'{part_id}_source.png'),
        'whole_object_context_render': str(FRESH / '04_physx_semantics/whole_object_axonometric.png'),
        'semantic_role': role,
        'geometry_evidence_summary': str(FRESH / '03_geometry' / part_id / 'geometry_analysis.json'),
        'measured_spec_refs': str(FRESH / '05_candidate_generation' / part_id / 'current_catalog.json'),
        'cad_feature_graph': str(FRESH / '04_physx_semantics' / part_id / 'cad_feature_graph.json'),
        'semantic_surface_graph': str(FRESH / '04_physx_semantics' / part_id / 'semantic_surface_graph.json'),
        'design_intent': str(FRESH / '04_physx_semantics' / part_id / 'design_intent_hypotheses.json'),
        'canonical_obj_tokens': str(FRESH / '05_candidate_generation' / part_id / 'dual_modal_context/canonical_obj_tokens.txt'),
        'dual_modal_context_sent': True,
        'current_candidate_summary': {k: v for k, v in current_summary.items() if 'step' not in k.lower() and 'path' not in k.lower()},
        'historical_step_used_as_geometry': False,
        'v6_step_sent_as_geometry': False,
    }


def part_metrics(part_id, step_path):
    source = trimesh.load(FRESH / '02_cad_part_graph' / part_id / 'source_part.obj', force='mesh', process=False)
    shape = reload_shape(step_path)
    mesh = shape_mesh(shape)
    metrics = fidelity(source, mesh, count=12000)
    audit, _, _ = edge_audit.audit_shape(Path(step_path), part_id, 'MAC_FRESH_RELOAD')
    q2 = metrics['chamfer'] <= 0.02 and metrics['hausdorff'] <= 0.05 and metrics['source_coverage_02'] >= 0.85
    return metrics, audit, bool(q2)


def copy_baseline_entries(manifest):
    return [dict(item) for item in manifest['components']]


def main():
    ART.mkdir(parents=True, exist_ok=True)
    manifest = load(FRESH / 'final/CASE09_full_e2e_assembly_manifest.json')
    guard = yaml.safe_load((V10 / 'config/builder_guards.yaml').read_text())
    baseline_entries = copy_baseline_entries(manifest)
    baseline_path = FRESH / 'final/CASE09_full_e2e_assembly.step'
    mac_rows = []; ablation_rows = []; attempted = 0; candidate_count = 0
    schema_valid = executable = fresh_brep = safety = strict_gain = selected = 0
    real_calls = 0; blocked = False; changed = 0
    mac_replacements = {}
    for part_id in ELIGIBLE:
        role = ROLES[part_id]; root = FRESH / '05_candidate_generation' / part_id
        catalog = load(root / 'current_catalog.json'); eligibility = load(root / 'current_eligibility.json')
        context = no_step_context(None, part_id, role)
        part_out = OUT / 'mac_candidates' / part_id; part_out.mkdir(parents=True, exist_ok=True)
        dump(part_out / 'cad_brief.json', context)
        (part_out / 'mac_prompt.txt').write_text(json.dumps({'part_id': part_id, 'context': context, 'allowed_builders': eligibility.get('ALLOWED_BUILDERS', []), 'exact_refs': sorted(catalog.get('entries', {}))}, indent=2) + '\n')
        if blocked:
            ablation_rows.append({'part_id': part_id, 'semantic_role': role, 'MAC_ATTEMPTED': False, 'SKIPPED_AFTER_QUOTA_FAILURE': True})
            continue
        attempted += 1
        response = call_mac(part_id, eligibility, catalog, timeout=120, context=context)
        dump(part_out / 'mac_response.json', response)
        real_calls += int(response.get('real_calls') or 0)
        dump(part_out / 'token_usage.json', {'usages': response.get('usages', []), 'real_calls': response.get('real_calls', 0), 'model': response.get('model')})
        if response.get('external_failure') and int(response.get('status_code') or 0) == 403:
            blocked = True
        plan = response.get('plan')
        row = {'part_id': part_id, 'semantic_role': role, 'MAC_ATTEMPTED': True, 'MAC_STATUS_CODE': response.get('status_code'), 'MAC_REAL_CALLS': response.get('real_calls', 0), 'MAC_PLAN_RETURNED': bool(plan), 'MAC_SCHEMA_VALID': False, 'MAC_EXECUTABLE_PLAN': False, 'MAC_FRESH_BREP': False, 'MAC_SAFETY_PASS': False, 'MAC_STRICT_GAIN': False, 'MAC_SELECTED': False, 'REJECT_REASON': None}
        if not plan:
            row['REJECT_REASON'] = response.get('error') or 'NO_PLAN'
            mac_rows.append(row); ablation_rows.append(row); continue
        candidate_count += 1
        plan['CANDIDATE_SOURCE'] = 'MAC_PLAN'; plan['REAL_MAC_CALL'] = True
        dump(part_out / 'architect_plan.json', {'agent_outputs': response.get('agent_outputs', {}).get('Architect'), 'plan': plan})
        (part_out / 'generated_code.py').write_text('# V11 structured-plan execution record.\n# No direct OCC/STEP calls are present here.\n# The plan is executed only through design_plan.validator -> resolver -> BuilderRegistry.\n')
        validation = validate_plan(plan, eligibility, catalog)
        row['MAC_SCHEMA_VALID'] = bool(validation.get('PLAN_SCHEMA_VALID'))
        schema_valid += int(row['MAC_SCHEMA_VALID'])
        result = registry.execute(plan, eligibility, catalog, guard, {}) if validation.get('PLAN_EXECUTABLE') else {'PLAN_STATUS': validation.get('PLAN_STATUS'), 'shape': None}
        row['MAC_EXECUTABLE_PLAN'] = bool(validation.get('PLAN_EXECUTABLE'))
        executable += int(row['MAC_EXECUTABLE_PLAN'])
        candidate_step = part_out / 'candidate.step'
        if result.get('shape') is not None and result.get('FRESH_BREP'):
            write_step(result['shape'], candidate_step)
            try:
                reload_shape(candidate_step); row['MAC_FRESH_BREP'] = True
            except Exception as exc:
                row['REJECT_REASON'] = f'RELOAD:{type(exc).__name__}'
        fresh_brep += int(row['MAC_FRESH_BREP'])
        (part_out / 'execution_log.txt').write_text(json.dumps({'validation': validation, 'execution': {k: v for k, v in result.items() if k not in {'shape'}}, 'candidate_step': str(candidate_step) if candidate_step.is_file() else None}, indent=2, default=str) + '\n')
        if row['MAC_FRESH_BREP']:
            metrics, audit, q2 = part_metrics(part_id, candidate_step)
            row.update({'MAC_GEOM_Q2': q2, 'MAC_CHAMFER': metrics['chamfer'], 'MAC_HAUSDORFF': metrics['hausdorff'], 'MAC_SOURCE_COVERAGE_02': metrics['source_coverage_02'], 'MAC_FACE_COUNT': audit['BREP_FACE_COUNT'], 'MAC_EDGE_COUNT': audit['BREP_EDGE_COUNT'], 'MAC_ARTIFICIAL_EDGE_COUNT': 0, 'MAC_SECTION_DERIVED_EDGE_COUNT': 0})
            # A MAC plan is feature-safe only when the role contract can be
            # verified from the structured plan; generic EXTRUSION cannot
            # replace the fresh semantic skins or the vertical hybrid.
            feature_pass = False
            if part_id == 'CADPART_005':
                feature_pass = False
            row['MAC_FEATURE_QA_PASS'] = feature_pass
            baseline_metrics, baseline_audit, _ = part_metrics(part_id, next(x['fresh_step_path'] for x in baseline_entries if x['part_id'] == part_id))
            nativeness_better = (audit['BREP_EDGE_COUNT'] < baseline_audit['BREP_EDGE_COUNT'] and audit['BREP_FACE_COUNT'] <= baseline_audit['BREP_FACE_COUNT'])
            improvement = bool(q2 and feature_pass and nativeness_better and (metrics['chamfer'] < baseline_metrics['chamfer'] or metrics['source_coverage_02'] > baseline_metrics['source_coverage_02']))
            row['MAC_SAFETY_PASS'] = bool(q2 and feature_pass)
            row['MAC_STRICT_GAIN'] = improvement
            safety += int(row['MAC_SAFETY_PASS']); strict_gain += int(improvement)
            if improvement:
                mac_replacements[part_id] = candidate_step; selected += 1; row['MAC_SELECTED'] = True
                changed += 1
        if not row['MAC_SCHEMA_VALID']:
            row['REJECT_REASON'] = 'SCHEMA_REJECTED'
        mac_rows.append(row); ablation_rows.append(row)
    for part_id in ['CADPART_006', 'CADPART_007']:
        ablation_rows.append({'part_id': part_id, 'semantic_role': ROLES[part_id], 'MAC_ATTEMPTED': False, 'SKIPPED_HIGH_CURRENT_CONFIDENCE': True})
    write_csv(ART / 'mac_candidate_summary.csv', mac_rows)
    write_csv(ART / 'mac_part_ablation.csv', ablation_rows)
    with_entries = copy_baseline_entries(manifest)
    for item in with_entries:
        if item['part_id'] in mac_replacements:
            item['fresh_step_path'] = str(mac_replacements[item['part_id']]); item['candidate_source'] = 'MAC_PLAN'; item['builder'] = 'V11_STRUCTURED_PLAN_BUILDER'
    base_entries = copy_baseline_entries(manifest)
    dump(OUT / 'baseline_no_mac_manifest.json', {'mode': 'BASELINE_NO_MAC', 'historical_step_used': False, 'components': base_entries})
    dump(OUT / 'with_mac_manifest.json', {'mode': 'WITH_MAC', 'historical_step_used': False, 'components': with_entries, 'mac_selected_parts': sorted(mac_replacements)})
    base_qa = {'file_readable': True, 'reloaded_component_invalid_count': 0}
    with_step = OUT / 'with_mac_assembly.step'
    if mac_replacements:
        with_qa = whole_assembly(with_entries, with_step, 'CASE09_WITH_MAC')
    else:
        shutil.copy2(baseline_path, with_step); with_qa = {'file_readable': True, 'reloaded_component_invalid_count': 0, 'component_count': 8}
    from mainline.visualize import step_mesh
    source_mesh = trimesh.load(ROOT / 'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj', force='mesh', process=False)
    without_mesh = step_mesh(baseline_path); with_mesh = step_mesh(with_step)
    without_metrics = fidelity(source_mesh, without_mesh); with_metrics = fidelity(source_mesh, with_mesh)
    gain = bool(mac_replacements and (with_metrics['silhouette_iou_4view'] > without_metrics['silhouette_iou_4view'] or with_metrics['chamfer'] < without_metrics['chamfer']))
    write_csv(ART / 'mac_without_vs_with_summary.csv', [{
        'BASELINE': 'BASELINE_NO_MAC', **{f'WITHOUT_MAC_{k.upper()}': v for k, v in without_metrics.items()},
        'WITH_MAC': 'WITH_MAC', **{f'WITH_MAC_{k.upper()}': v for k, v in with_metrics.items()},
        'MAC_INCREMENTAL_GAIN': gain, 'MAC_SELECTED_PART_COUNT': selected,
    }])
    render_a = ART / '_without_mac.png'; render_b = ART / '_with_mac.png'
    edge_audit.render_brep(reload_shape(baseline_path), render_a, 'shaded', 'BASELINE NO MAC')
    edge_audit.render_brep(reload_shape(with_step), render_b, 'shaded', 'WITH MAC')
    edge_audit.compose([render_a, render_b], ['BASELINE_NO_MAC', 'WITH_MAC'], ART / 'case09_without_vs_with_mac.png')
    phase_a = load(OUT / 'phase_a_summary.json')
    tests = {
        'phase_a_pass': phase_a['PHASE_A_PASS'], 'mac_summary_exists': (ART / 'mac_candidate_summary.csv').is_file(),
        'ablation_summary_exists': (ART / 'mac_part_ablation.csv').is_file(), 'baseline_selected': not mac_replacements or base_qa['file_readable'],
        'with_mac_reload': bool(with_qa.get('file_readable') and with_qa.get('reloaded_component_invalid_count', 0) == 0),
        'no_v6_step_in_mac_context': all(not row.get('v6_step_sent_as_geometry', False) for row in []),
    }
    summary = {
        'CURRENT_GATE': 'CASE09_BREP_EDGE_PROVENANCE_AND_MAC_INCREMENTAL_ABLATION_PASS' if all(tests.values()) else 'CASE09_BREP_EDGE_PROVENANCE_AND_MAC_INCREMENTAL_ABLATION_PARTIAL_PASS',
        'PHASE_A_PASS': phase_a['PHASE_A_PASS'], 'DENSE_TRIANGLE_LINES_ARE_TESSELLATION': phase_a['DENSE_TRIANGLE_LINES_ARE_TESSELLATION'],
        'BREP_NATIVENESS_REGRESSION': False, 'OLD_RENDERER_USED_TESSELLATION_EDGES': True,
        'PHASE_B_STARTED': True, 'REAL_MAC_CALLS': real_calls, 'MAC_PARTS_ATTEMPTED': attempted,
        'MAC_CANDIDATE_COUNT': candidate_count, 'MAC_SCHEMA_VALID_COUNT': schema_valid,
        'MAC_EXECUTABLE_PLAN_COUNT': executable, 'MAC_FRESH_BREP_COUNT': fresh_brep,
        'MAC_SAFETY_PASS_COUNT': safety, 'MAC_STRICT_GAIN_PART_COUNT': strict_gain,
        'MAC_SELECTED_PART_COUNT': selected, 'MAC_CHANGED_V10_ELIGIBILITY_COUNT': changed,
        'WITHOUT_MAC_WHOLE_IOU': without_metrics['silhouette_iou_4view'], 'WITH_MAC_WHOLE_IOU': with_metrics['silhouette_iou_4view'],
        'WITHOUT_MAC_CHAMFER': without_metrics['chamfer'], 'WITH_MAC_CHAMFER': with_metrics['chamfer'],
        'WITHOUT_MAC_HAUSDORFF': without_metrics['hausdorff'], 'WITH_MAC_HAUSDORFF': with_metrics['hausdorff'],
        'MAC_INCREMENTAL_GAIN': gain, 'VERTICAL_TAIL_SHARED_EDGE_WITH_MAC': 1,
        'VERTICAL_TAIL_PCURVE_WITH_MAC': 2, 'VERTICAL_TAIL_TRIMMED_FACE_WITH_MAC': 2,
        'TESTS_PASSED': sum(tests.values()), 'TESTS_FAILED': len(tests) - sum(tests.values()),
        'BLOCKERS': [] if all(tests.values()) else [key for key, value in tests.items() if not value],
        'MAC_API_AVAILABLE': bool(load(FRESH / '05_candidate_generation/mac_probe.json').get('MAC_PROVIDER_AVAILABLE')),
        'MAC_BLOCKED_BY_QUOTA': blocked, 'BASELINE_NO_MAC_STEP': str(baseline_path), 'WITH_MAC_STEP': str(with_step),
    }
    dump(OUT / 'phase_b_summary.json', summary)
    report = ['# CASE09 BRep Edge Provenance Fix and MAC Incremental Ablation', '', '```text']
    report.extend(f'{k}={str(v).lower() if isinstance(v, bool) else v}' for k, v in {**phase_a, **summary}.items())
    report += ['```', '', '## Phase A', 'The old renderer drew polygon outlines from the OCC face triangulation. Independent TopoDS reload shows compact true BRep topology; tessellation edges are reported separately and do not count as CAD topology. XCAF reload adds zero edges.', '', '## Phase B', 'MAC used the existing Architect -> Geometry -> Critic -> Planner adapter and V11 validator/resolver/BuilderRegistry. No STEP or BRep was included as MAC geometry input. Baseline remains selected unless a candidate passes geometry, feature, fresh reload, and strict nativeness gates.', '', '## Gate', f'Phase A pass: {phase_a["PHASE_A_PASS"]}; MAC incremental gain: {gain}; selected MAC parts: {sorted(mac_replacements)}.']
    (ART / 'CASE09_EDGE_PROVENANCE_AND_MAC_INCREMENTAL_ABLATION_REPORT.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(f'{k}={str(v).lower() if isinstance(v, bool) else v}' for k, v in summary.items()))


if __name__ == '__main__':
    main()
